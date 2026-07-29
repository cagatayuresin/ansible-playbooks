#!/usr/bin/env python3
"""Host listening ports + firewall (iptables/nft/ufw) report."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


def run(cmd: str, timeout: float = 30.0) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", str(e)


def section(title: str) -> list[str]:
    return ["", f"=== {title} ==="]


def classify_bind(addr: str) -> str:
    a = addr.strip().lower()
    if a in ("*", "0.0.0.0", "::", "[::]"):
        return "TUM_ARAYUZLER (dışarıdan erişilebilir olabilir)"
    if a in ("127.0.0.1", "::1", "[::1]", "localhost"):
        return "SADECE_LOCALHOST"
    if a.startswith("10.") or a.startswith("192.168.") or a.startswith("172."):
        return f"OZEL_IP ({addr}) — iç ağ arayüzü"
    return f"BELIRLI_IP ({addr})"


def parse_ss_process(proc: str) -> str:
    """users:(("sshd",pid=1,fd=3)) -> sshd (pid=1)"""
    if not proc:
        return "-"
    names = re.findall(r'\("([^"]+)",pid=(\d+)', proc)
    if not names:
        # fallback
        m = re.search(r'users:\(\((.+)\)\)', proc)
        return m.group(1) if m else proc
    parts = [f"{n} (pid={p})" for n, p in names]
    return ", ".join(parts)


def parse_ss_lines(out: str) -> list[dict[str, Any]]:
    rows = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("netid"):
            continue
        # Process field may contain spaces inside users:(...)
        proc = ""
        mproc = re.search(r'(users:\(.*\))\s*$', line)
        if mproc:
            proc = mproc.group(1)
            line = line[: mproc.start()].rstrip()
        parts = line.split()
        if len(parts) < 5:
            continue
        netid = parts[0]  # tcp/udp
        state = parts[1]
        # Local Address:Port is usually parts[4]
        local = parts[4] if len(parts) > 4 else ""
        # Handle IPv6 [addr]:port
        if local.startswith("["):
            m = re.match(r"^\[([^\]]+)\]:(\d+)$", local)
            if m:
                addr, port = m.group(1), m.group(2)
            else:
                addr, port = local, "?"
        else:
            if ":" in local:
                addr, port = local.rsplit(":", 1)
            else:
                addr, port = local, "?"
        if state.upper() not in ("LISTEN", "UNCONN"):
            # UDP often UNCONN for listening
            if netid.startswith("udp") and state.upper() == "UNCONN":
                pass
            elif netid.startswith("tcp") and state.upper() != "LISTEN":
                continue
        rows.append(
            {
                "proto": netid,
                "state": state,
                "addr": addr,
                "port": port,
                "bind": classify_bind(addr),
                "process": parse_ss_process(proc),
                "raw_proc": proc,
            }
        )
    return rows


def collect_listening() -> tuple[list[str], list[dict[str, Any]]]:
    lines = section("Dinleyen portlar (ss)")
    rows: list[dict[str, Any]] = []

    # Prefer JSON if available
    rc, out, err = run("ss -H -tulnp --json 2>/dev/null || true")
    if rc == 0 and out.startswith("{"):
        try:
            data = json.loads(out)
            for s in data.get("sockets") or data.get("Listening") or []:
                # ss json schema varies; fall through to text if weird
                pass
        except Exception:
            pass

    rc, out, err = run("ss -H -tulnp")
    if rc != 0 or not out:
        # without -p if permission denied
        rc2, out2, err2 = run("ss -H -tuln")
        if rc2 != 0:
            lines.append(f"ss alınamadı: {err or err2}")
            return lines, rows
        out = out2
        lines.append(
            "UYARI: süreç adları görünmüyor (ss -p için root/izin gerekebilir)."
        )

    rows = parse_ss_lines(out)
    # sort by proto, port numeric
    def port_key(r):
        try:
            return (r["proto"], int(r["port"]))
        except Exception:
            return (r["proto"], 0, r["port"])

    rows.sort(key=port_key)

    lines.append(
        f"{'PROTO':<6} {'PORT':>6}  {'BIND_ADDR':<22}  NASIL_ACIK / UYGULAMA"
    )
    lines.append("-" * 110)
    for r in rows:
        lines.append(
            f"{r['proto']:<6} {r['port']:>6}  {r['addr']:<22}  {r['bind']}"
        )
        lines.append(f"{'':6} {'':6}  {'':22}  uygulama: {r['process']}")

    # summary by bind type
    by_bind = defaultdict(int)
    by_proto = defaultdict(int)
    for r in rows:
        by_proto[r["proto"]] += 1
        if "TUM_ARAYUZLER" in r["bind"]:
            by_bind["tum_arayuz"] += 1
        elif "LOCALHOST" in r["bind"]:
            by_bind["localhost"] += 1
        else:
            by_bind["belirli_ip"] += 1
    lines.append(
        f"Özet: toplam_dinleme={len(rows)} | "
        f"tcp/udp={dict(by_proto)} | "
        f"tum_arayuz={by_bind['tum_arayuz']} localhost={by_bind['localhost']} "
        f"belirli_ip={by_bind['belirli_ip']}"
    )
    return lines, rows


def collect_ufw() -> list[str]:
    lines = []
    if not shutil.which("ufw"):
        return lines
    lines.extend(section("UFW durumu"))
    rc, out, err = run("ufw status verbose")
    if rc == 0 and out:
        lines.append(out)
    else:
        lines.append(err or "ufw status alınamadı")
    return lines


def collect_firewalld() -> list[str]:
    lines = []
    if not shutil.which("firewall-cmd"):
        return lines
    rc, out, _ = run("systemctl is-active firewalld")
    if out.strip() != "active":
        return lines
    lines.extend(section("firewalld"))
    for cmd in (
        "firewall-cmd --state",
        "firewall-cmd --get-default-zone",
        "firewall-cmd --list-all",
    ):
        rc, out, err = run(cmd)
        lines.append(f"$ {cmd}")
        lines.append(out or err or "-")
    return lines


def collect_iptables(listen_ports: list[dict[str, Any]]) -> list[str]:
    lines = section("iptables / nft özeti")
    ports = sorted(
        {
            r["port"]
            for r in listen_ports
            if str(r.get("port", "")).isdigit()
        },
        key=lambda x: int(x),
    )

    # Prefer nft if ruleset exists
    if shutil.which("nft"):
        rc, out, err = run("nft list ruleset")
        if rc == 0 and out.strip():
            lines.append("--- nftables ruleset (kısaltılmış / ilgili) ---")
            # Full ruleset can be huge on k8s; summarize + filter port mentions
            all_lines = out.splitlines()
            lines.append(f"Toplam nft satır: {len(all_lines)}")
            # Show table/chain headers and first policies
            headers = [
                l
                for l in all_lines
                if l.strip().startswith("table ")
                or l.strip().startswith("chain ")
                or "policy" in l
                or "type filter hook" in l
            ]
            lines.extend(headers[:40])
            if ports:
                lines.append("--- Dinlenen portlara değinen nft satırları ---")
                port_hits = []
                for l in all_lines:
                    for p in ports:
                        if re.search(rf"\b{p}\b", l) and (
                            "dport" in l or "sport" in l or "tcp" in l or "udp" in l
                        ):
                            port_hits.append(l.strip())
                            break
                if port_hits:
                    # unique preserve
                    seen = set()
                    for h in port_hits:
                        if h not in seen:
                            seen.add(h)
                            lines.append(h)
                        if len(seen) >= 80:
                            lines.append("... (daha fazla eşleşme kısaltıldı)")
                            break
                else:
                    lines.append(
                        "(Dinlenen port numarası geçen bariz nft kuralı bulunamadı; "
                        "policy ACCEPT ise genel açık olabilir.)"
                    )
        else:
            lines.append("nft ruleset boş veya alınamadı.")

    if shutil.which("iptables"):
        lines.append("--- iptables filter (iptables -L -n -v) ---")
        rc, out, err = run("iptables -L -n -v")
        if rc == 0 and out:
            # Extract policy lines and keep it manageable
            pol = [
                l
                for l in out.splitlines()
                if l.startswith("Chain ") or "policy" in l.lower()
            ]
            lines.extend(pol[:30] if pol else out.splitlines()[:20])
            # Show ACCEPT/DROP/REJECT with dpt for listening ports
            if ports:
                lines.append("--- Dinlenen portlara ait iptables satırları (filter) ---")
                hits = []
                for l in out.splitlines():
                    for p in ports:
                        if f"dpt:{p}" in l or f"dpt:{p} " in l or f":{p} " in l:
                            hits.append(l.rstrip())
                            break
                if hits:
                    seen = set()
                    for h in hits:
                        if h not in seen:
                            seen.add(h)
                            lines.append(h)
                        if len(seen) >= 60:
                            lines.append("... (kısaltıldı)")
                            break
                else:
                    lines.append(
                        "(dpt:<port> eşleşmesi yok — UFW/nft arkasında veya policy ACCEPT)"
                    )
            # Truncated full dump tip
            lines.append(
                f"(Tam filter çıktı {len(out.splitlines())} satır; özet yukarıda.)"
            )
        else:
            lines.append(f"iptables filter alınamadı: {err or '-'}")

        lines.append("--- iptables nat (özet) ---")
        rc, out, err = run("iptables -t nat -L -n -v")
        if rc == 0 and out:
            pol = [l for l in out.splitlines() if l.startswith("Chain ")]
            lines.extend(pol[:20])
            # DNAT/REDIRECT interesting
            interesting = [
                l
                for l in out.splitlines()
                if any(x in l for x in ("DNAT", "REDIRECT", "MASQUERADE"))
            ]
            for l in interesting[:40]:
                lines.append(l.rstrip())
            if not interesting:
                lines.append("(belirgin DNAT/REDIRECT/MASQUERADE yok veya görülemedi)")
        else:
            lines.append(f"iptables nat alınamadı: {err or '-'}")

        # iptables-save short policy extract
        if shutil.which("iptables-save"):
            rc, out, _ = run("iptables-save -c")
            if rc == 0 and out:
                lines.append("--- iptables-save policy / önemli satırlar ---")
                for l in out.splitlines():
                    if (
                        l.startswith(":")
                        or l.startswith("*")
                        or "INPUT" in l
                        or "FORWARD" in l
                        or "OUTPUT" in l
                    ) and (
                        l.startswith(":")
                        or l.startswith("*")
                        or "-P " in l
                        or l.startswith("-A INPUT")
                        or l.startswith("-A FORWARD")
                    ):
                        # keep policies and first INPUT rules sample
                        pass
                policies = [l for l in out.splitlines() if l.startswith(":")]
                lines.extend(policies[:20])
                input_rules = [
                    l for l in out.splitlines() if l.startswith("-A INPUT")
                ]
                lines.append(f"INPUT kural sayısı: {len(input_rules)}")
                for l in input_rules[:25]:
                    lines.append(l)
                if len(input_rules) > 25:
                    lines.append(f"... +{len(input_rules) - 25} INPUT kuralı daha")

    if not shutil.which("iptables") and not shutil.which("nft"):
        lines.append("iptables/nft bulunamadı.")

    return lines


def collect_correlation(rows: list[dict[str, Any]]) -> list[str]:
    lines = section("Yorum / risk özeti")
    ext = [r for r in rows if "TUM_ARAYUZLER" in r["bind"]]
    local = [r for r in rows if "LOCALHOST" in r["bind"]]
    lines.append(
        f"Tüm arayüzlerde dinleyen: {len(ext)} | Sadece localhost: {len(local)}"
    )
    if ext:
        lines.append("Dışarıya bakıyor olabilecek servisler (TUM_ARAYUZLER):")
        for r in ext:
            lines.append(
                f"  - {r['proto']}/{r['port']} → {r['process']}"
            )
    lines.append(
        "Not: 'Dinliyor' ≠ 'firewall izin veriyor'. nft/iptables/UFW DROP ise "
        "dışarıdan kapalı olabilir. Tersine policy ACCEPT ise dinleyen portlar açık sayılır."
    )
    lines.append(
        "K8s/k3s node'larında kube-proxy/CNI yüzünden iptables/nft çok kalabalık olabilir; "
        "NodePort için ayrıca playbook 02 kullanılabilir."
    )
    return lines


def main() -> None:
    lines: list[str] = []
    lines.append("Host açık portlar + firewall raporu (salt-okunur)")

    listen_lines, rows = collect_listening()
    lines.extend(listen_lines)
    lines.extend(collect_ufw())
    lines.extend(collect_firewalld())
    lines.extend(collect_iptables(rows))
    lines.extend(collect_correlation(rows))
    lines.append("")
    lines.append("Detay: docs/20_check_host_ports_firewall.md")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
