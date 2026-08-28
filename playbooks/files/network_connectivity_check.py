#!/usr/bin/env python3
"""Detailed on-prem network / DNS / internet connectivity report."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


def run(cmd: str, timeout: float = 8.0) -> tuple[int, str, str]:
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


def ok_fail(ok: bool) -> str:
    return "OK" if ok else "FAIL"


def read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except Exception as e:
        return f"(unreadable: {e})"


def collect_interfaces() -> list[str]:
    lines = section("Network interfaces / addresses")
    rc, out, err = run("ip -br addr")
    if rc == 0 and out:
        lines.append(out)
    else:
        rc2, out2, _ = run("hostname -I")
        lines.append(out2 or err or "ip/hostname could not be retrieved")
    return lines


def collect_routes() -> list[str]:
    lines = section("Routes / default gateway")
    rc, out, _ = run("ip route")
    if rc == 0 and out:
        lines.append(out)
        default = [l for l in out.splitlines() if l.startswith("default ")]
        if default:
            lines.append(f"Default route: {default[0]}")
        else:
            lines.append("WARNING: no default route — external network/internet is usually impossible.")
    else:
        lines.append("ip route could not be retrieved")
    return lines


def collect_dns_config() -> list[str]:
    lines = section("DNS configuration")
    lines.append("--- /etc/resolv.conf ---")
    resolv = read_file("/etc/resolv.conf")
    lines.append(resolv if resolv else "(empty)")
    nameservers = re.findall(r"^nameserver\s+(\S+)", resolv, flags=re.M)
    search = re.findall(r"^search\s+(.+)$", resolv, flags=re.M)
    lines.append(f"nameserver count: {len(nameservers)} → {', '.join(nameservers) or '-'}")
    if search:
        lines.append(f"search: {search[0].strip()}")

    if Path("/etc/resolv.conf").is_symlink():
        try:
            lines.append(f"resolv.conf symlink → {os.readlink('/etc/resolv.conf')}")
        except Exception:
            pass

    if shutil.which("resolvectl"):
        rc, out, _ = run("resolvectl status", timeout=5)
        if rc == 0 and out:
            # keep it shorter
            keep = []
            for line in out.splitlines():
                if any(
                    k in line
                    for k in (
                        "Current DNS",
                        "DNS Servers",
                        "DNS Domain",
                        "Fallback DNS",
                        "Link ",
                        "Current Scopes",
                    )
                ):
                    keep.append(line.rstrip())
            lines.append("--- resolvectl (summary) ---")
            lines.extend(keep[:40] if keep else out.splitlines()[:25])
    elif shutil.which("systemd-resolve"):
        rc, out, _ = run("systemd-resolve --status", timeout=5)
        if rc == 0 and out:
            lines.append("--- systemd-resolve (first lines) ---")
            lines.extend(out.splitlines()[:30])

    # nsswitch hosts line
    nss = read_file("/etc/nsswitch.conf")
    for line in nss.splitlines():
        if line.strip().startswith("hosts:"):
            lines.append(f"nsswitch hosts: {line.strip()}")
            break

    return lines


def resolve_one(host: str, timeout: float = 3.0) -> dict[str, Any]:
    started = time.monotonic()
    result: dict[str, Any] = {
        "host": host,
        "ok": False,
        "addrs": [],
        "ms": None,
        "error": None,
        "via": None,
    }
    # Prefer getent (uses system resolver / nss)
    if shutil.which("getent"):
        rc, out, err = run(f"getent ahosts {host}", timeout=timeout)
        result["ms"] = round((time.monotonic() - started) * 1000)
        if rc == 0 and out:
            addrs = []
            for line in out.splitlines():
                parts = line.split()
                if parts:
                    addrs.append(parts[0])
            # unique preserve order
            seen = set()
            uniq = []
            for a in addrs:
                if a not in seen:
                    seen.add(a)
                    uniq.append(a)
            result["ok"] = True
            result["addrs"] = uniq[:8]
            result["via"] = "getent"
            return result
        result["error"] = err or "getent failed"

    # Fallback: socket
    try:
        socket.setdefaulttimeout(timeout)
        infos = socket.getaddrinfo(host, None)
        addrs = []
        seen = set()
        for info in infos:
            a = info[4][0]
            if a not in seen:
                seen.add(a)
                addrs.append(a)
        result["ok"] = True
        result["addrs"] = addrs[:8]
        result["via"] = "getaddrinfo"
        result["ms"] = round((time.monotonic() - started) * 1000)
        result["error"] = None
    except Exception as e:
        result["ms"] = round((time.monotonic() - started) * 1000)
        result["error"] = str(e)
    return result


def collect_dns_tests(hosts: list[str]) -> tuple[list[str], dict[str, Any]]:
    lines = section("DNS resolution tests")
    stats = {"ok": 0, "fail": 0, "results": []}
    if not hosts:
        lines.append("(test host list is empty)")
        return lines, stats

    lines.append(f"{'RESULT':<6}  {'ms':>6}  {'HOST':<40}  ADDRESSES / ERROR")
    lines.append("-" * 100)
    with ThreadPoolExecutor(max_workers=min(8, len(hosts))) as ex:
        futs = {ex.submit(resolve_one, h): h for h in hosts}
        ordered = []
        for fut in as_completed(futs):
            ordered.append(fut.result())
    # keep input order
    by_host = {r["host"]: r for r in ordered}
    for h in hosts:
        r = by_host[h]
        stats["results"].append(r)
        if r["ok"]:
            stats["ok"] += 1
            addr = ", ".join(r["addrs"][:4])
            lines.append(
                f"{'OK':<6}  {r['ms'] or 0:>6}  {h:<40}  {addr}  ({r['via']})"
            )
        else:
            stats["fail"] += 1
            lines.append(
                f"{'FAIL':<6}  {r['ms'] or 0:>6}  {h:<40}  {r['error']}"
            )
    lines.append(f"DNS summary: ok={stats['ok']} fail={stats['fail']} total={len(hosts)}")
    return lines, stats


def ping_one(target: str, count: int = 2) -> dict[str, Any]:
    started = time.monotonic()
    # -W1 deadline per probe where supported
    rc, out, err = run(f"ping -c {count} -W 2 {target}", timeout=count * 3 + 2)
    ms = round((time.monotonic() - started) * 1000)
    ok = rc == 0
    loss = None
    m = re.search(r"(\d+(?:\.\d+)?)% packet loss", out)
    if m:
        loss = float(m.group(1))
    rtt = None
    m2 = re.search(r"rtt [^=]*=\s*([0-9.]+)/([0-9.]+)/([0-9.]+)", out)
    if m2:
        rtt = {"min": m2.group(1), "avg": m2.group(2), "max": m2.group(3)}
    return {
        "target": target,
        "ok": ok,
        "ms": ms,
        "loss_pct": loss,
        "rtt": rtt,
        "error": None if ok else (err or out.splitlines()[-1] if out else "ping failed"),
    }


def collect_ping_tests(targets: list[str]) -> tuple[list[str], dict[str, Any]]:
    lines = section("ICMP ping tests")
    lines.append("Note: Many clouds/firewalls drop ICMP; FAIL alone does not mean there is no internet.")
    stats = {"ok": 0, "fail": 0}
    lines.append(f"{'RESULT':<6}  {'ms':>6}  {'LOSS':>6}  TARGET")
    lines.append("-" * 60)
    for t in targets:
        r = ping_one(t)
        if r["ok"]:
            stats["ok"] += 1
            loss = f"{r['loss_pct']}%" if r["loss_pct"] is not None else "-"
            extra = ""
            if r["rtt"]:
                extra = f"  rtt_avg={r['rtt']['avg']}ms"
            lines.append(f"{'OK':<6}  {r['ms']:>6}  {loss:>6}  {t}{extra}")
        else:
            stats["fail"] += 1
            lines.append(f"{'FAIL':<6}  {r['ms']:>6}  {'-':>6}  {t}  → {r['error']}")
    lines.append(f"Ping summary: ok={stats['ok']} fail={stats['fail']}")
    return lines, stats


def tcp_one(host: str, port: int, timeout: float = 3.0) -> dict[str, Any]:
    started = time.monotonic()
    try:
        # Resolve first for clearer errors
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        last_err = None
        for family, _type, _proto, _canon, sockaddr in infos:
            s = socket.socket(family, socket.SOCK_STREAM)
            s.settimeout(timeout)
            try:
                s.connect(sockaddr)
                s.close()
                return {
                    "target": f"{host}:{port}",
                    "ok": True,
                    "ms": round((time.monotonic() - started) * 1000),
                    "peer": f"{sockaddr[0]}:{sockaddr[1]}",
                    "error": None,
                }
            except Exception as e:
                last_err = str(e)
                try:
                    s.close()
                except Exception:
                    pass
        return {
            "target": f"{host}:{port}",
            "ok": False,
            "ms": round((time.monotonic() - started) * 1000),
            "peer": None,
            "error": last_err or "connect failed",
        }
    except Exception as e:
        return {
            "target": f"{host}:{port}",
            "ok": False,
            "ms": round((time.monotonic() - started) * 1000),
            "peer": None,
            "error": str(e),
        }


def collect_tcp_tests(targets: list[str]) -> tuple[list[str], dict[str, Any]]:
    lines = section("TCP connection tests (host:port)")
    stats = {"ok": 0, "fail": 0}
    parsed: list[tuple[str, int]] = []
    for t in targets:
        if ":" not in t:
            continue
        host, port_s = t.rsplit(":", 1)
        try:
            parsed.append((host, int(port_s)))
        except ValueError:
            lines.append(f"Invalid target skipped: {t}")
    lines.append(f"{'RESULT':<6}  {'ms':>6}  {'TARGET':<42}  PEER / ERROR")
    lines.append("-" * 100)

    results = []
    with ThreadPoolExecutor(max_workers=min(10, max(1, len(parsed)))) as ex:
        futs = {ex.submit(tcp_one, h, p): f"{h}:{p}" for h, p in parsed}
        for fut in as_completed(futs):
            results.append(fut.result())
    by_t = {r["target"]: r for r in results}
    for h, p in parsed:
        key = f"{h}:{p}"
        r = by_t[key]
        if r["ok"]:
            stats["ok"] += 1
            lines.append(
                f"{'OK':<6}  {r['ms']:>6}  {key:<42}  {r['peer']}"
            )
        else:
            stats["fail"] += 1
            lines.append(
                f"{'FAIL':<6}  {r['ms']:>6}  {key:<42}  {r['error']}"
            )
    lines.append(f"TCP summary: ok={stats['ok']} fail={stats['fail']}")
    return lines, stats


def http_one(url: str, timeout: float = 5.0, proxy: str | None = None) -> dict[str, Any]:
    started = time.monotonic()
    handlers = []
    if proxy:
        handlers.append(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        )
    else:
        # Respect env proxies automatically; empty ProxyHandler clears if we want direct
        handlers.append(urllib.request.ProxyHandler())
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "ansible-playbooks-netcheck/1.0"},
    )
    try:
        with opener.open(req, timeout=timeout) as resp:
            code = getattr(resp, "status", None) or resp.getcode()
            # read little
            resp.read(256)
            return {
                "url": url,
                "ok": 200 <= int(code) < 500,  # 401/403 still means "reached"
                "reachable": True,
                "code": int(code),
                "ms": round((time.monotonic() - started) * 1000),
                "error": None,
            }
    except urllib.error.HTTPError as e:
        return {
            "url": url,
            "ok": True,  # TCP/TLS + HTTP reached
            "reachable": True,
            "code": int(e.code),
            "ms": round((time.monotonic() - started) * 1000),
            "error": f"HTTP {e.code}",
        }
    except Exception as e:
        return {
            "url": url,
            "ok": False,
            "reachable": False,
            "code": None,
            "ms": round((time.monotonic() - started) * 1000),
            "error": str(e),
        }


def collect_http_tests(urls: list[str]) -> tuple[list[str], dict[str, Any]]:
    lines = section("HTTP/HTTPS access tests")
    lines.append(
        "Note: Even 401/403/404 count as 'reached' (TLS+HTTP works). "
        "Certificate/proxy errors are FAIL."
    )
    stats = {"ok": 0, "fail": 0}
    lines.append(f"{'RESULT':<6}  {'ms':>6}  {'CODE':>5}  URL / ERROR")
    lines.append("-" * 100)
    results = []
    with ThreadPoolExecutor(max_workers=min(8, max(1, len(urls)))) as ex:
        futs = [ex.submit(http_one, u) for u in urls]
        for fut in as_completed(futs):
            results.append(fut.result())
    by_u = {r["url"]: r for r in results}
    for u in urls:
        r = by_u[u]
        if r["ok"]:
            stats["ok"] += 1
            lines.append(
                f"{'OK':<6}  {r['ms']:>6}  {str(r['code'] or '-'):>5}  {u}"
            )
        else:
            stats["fail"] += 1
            lines.append(
                f"{'FAIL':<6}  {r['ms']:>6}  {'-':>5}  {u}  → {r['error']}"
            )
    lines.append(f"HTTP summary: ok={stats['ok']} fail={stats['fail']}")
    return lines, stats


def collect_proxy() -> list[str]:
    lines = section("Proxy / environment variables")
    keys = [
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "no_proxy",
        "NO_PROXY",
        "ALL_PROXY",
        "all_proxy",
    ]
    found = False
    for k in keys:
        v = os.environ.get(k)
        if v:
            found = True
            lines.append(f"{k}={v}")
    if not found:
        lines.append("No proxy variable in the process environment.")

    # apt proxy snippets
    apt_files = [
        "/etc/apt/apt.conf",
        "/etc/apt/apt.conf.d/proxy.conf",
        "/etc/apt/apt.conf.d/95proxies",
        "/etc/apt/apt.conf.d/01proxy",
    ]
    for f in apt_files:
        if Path(f).is_file():
            txt = read_file(f)
            if "proxy" in txt.lower():
                lines.append(f"--- {f} ---")
                for line in txt.splitlines():
                    if "proxy" in line.lower() and not line.strip().startswith("//"):
                        lines.append(line)

    # docker/containerd proxy - optional hints
    for f in (
        "/etc/systemd/system/docker.service.d/http-proxy.conf",
        "/etc/systemd/system/containerd.service.d/http-proxy.conf",
    ):
        if Path(f).is_file():
            lines.append(f"--- {f} ---")
            lines.append(read_file(f)[:800])

    return lines


def collect_gateway_ping() -> list[str]:
    lines = section("Gateway reachability")
    rc, out, _ = run("ip route show default")
    gw = None
    m = re.search(r"default via (\S+)", out)
    if m:
        gw = m.group(1)
        lines.append(f"Gateway: {gw}")
        r = ping_one(gw, count=2)
        if r["ok"]:
            lines.append(f"Gateway ping: OK (avg path ~{r['ms']}ms)")
        else:
            lines.append(f"Gateway ping: FAIL → {r['error']}")
            lines.append(
                "WARNING: Even without ICMP to the gateway, TCP may still work; "
                "but an L2/L3 break is also possible."
            )
    else:
        lines.append("Default gateway not found.")
    return lines


def compute_profile(
    dns_stats: dict[str, Any],
    tcp_stats: dict[str, Any],
    http_stats: dict[str, Any],
) -> tuple[str, str, float, float, float]:
    dns_ok = dns_stats.get("ok", 0)
    dns_fail = dns_stats.get("fail", 0)
    tcp_ok = tcp_stats.get("ok", 0)
    tcp_fail = tcp_stats.get("fail", 0)
    http_ok = http_stats.get("ok", 0)
    http_fail = http_stats.get("fail", 0)

    dns_ratio = dns_ok / max(dns_ok + dns_fail, 1)
    tcp_ratio = tcp_ok / max(tcp_ok + tcp_fail, 1)
    http_ratio = http_ok / max(http_ok + http_fail, 1)

    if http_ratio >= 0.7 and dns_ratio >= 0.7:
        profile = "INTERNET_AVAILABLE"
        detail = (
            "DNS and HTTPS mostly work — online install / image pull is usually possible."
        )
    elif tcp_ratio >= 0.5 and dns_ratio < 0.5:
        profile = "LIMITED_DNS_BROKEN"
        detail = (
            "Some TCP targets are reachable but DNS is weak/broken. "
            "Access by IP or an internal DNS fix is required."
        )
    elif dns_ratio >= 0.7 and http_ratio < 0.3 and tcp_ratio < 0.3:
        profile = "DNS_OK_NO_EGRESS"
        detail = (
            "Names resolve but there is no external TCP/HTTPS — outbound firewall / proxy may be missing."
        )
    elif dns_ratio < 0.3 and tcp_ratio < 0.3 and http_ratio < 0.3:
        profile = "NO_INTERNET_OR_AIRGAP"
        detail = (
            "DNS + external TCP/HTTPS mostly failed — air-gap / isolated on-prem profile. "
            "Plan installation via offline packages/mirrors."
        )
    else:
        profile = "PARTIAL_ACCESS"
        detail = (
            "Mixed results — some registry/apt targets may be open, others closed. "
            "Configure a mirror/proxy based on the FAIL lines below."
        )
    return profile, detail, dns_ratio, tcp_ratio, http_ratio


def download_speed_one(url: str, timeout: float = 60.0) -> dict[str, Any]:
    """Download body and measure throughput (Mbps)."""
    started = time.monotonic()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler())
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "ansible-playbooks-netcheck/1.0"},
    )
    try:
        with opener.open(req, timeout=timeout) as resp:
            total = 0
            chunk = 64 * 1024
            t0 = time.monotonic()
            while True:
                data = resp.read(chunk)
                if not data:
                    break
                total += len(data)
            elapsed = max(time.monotonic() - t0, 0.001)
            mbps = (total * 8) / elapsed / 1_000_000
            return {
                "url": url,
                "ok": total > 0,
                "bytes": total,
                "sec": round(elapsed, 3),
                "mbps": round(mbps, 2),
                "ms_total": round((time.monotonic() - started) * 1000),
                "error": None,
            }
    except Exception as e:
        return {
            "url": url,
            "ok": False,
            "bytes": 0,
            "sec": round(time.monotonic() - started, 3),
            "mbps": None,
            "ms_total": round((time.monotonic() - started) * 1000),
            "error": str(e),
        }


def upload_speed_one(url: str, nbytes: int, timeout: float = 60.0) -> dict[str, Any]:
    """POST random bytes and measure upload throughput (Mbps)."""
    started = time.monotonic()
    # Generate payload without holding huge RAM spikes for very large sizes
    payload = os.urandom(min(nbytes, 256 * 1024))
    if nbytes > len(payload):
        # Repeat block to reach size (memory tradeoff acceptable for <=25MB tests)
        reps = nbytes // len(payload)
        rem = nbytes % len(payload)
        payload = payload * reps + payload[:rem]

    opener = urllib.request.build_opener(urllib.request.ProxyHandler())
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "User-Agent": "ansible-playbooks-netcheck/1.0",
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(payload)),
        },
    )
    try:
        t0 = time.monotonic()
        with opener.open(req, timeout=timeout) as resp:
            resp.read(256)
            code = getattr(resp, "status", None) or resp.getcode()
        elapsed = max(time.monotonic() - t0, 0.001)
        mbps = (len(payload) * 8) / elapsed / 1_000_000
        return {
            "url": url,
            "ok": 200 <= int(code) < 500,
            "bytes": len(payload),
            "sec": round(elapsed, 3),
            "mbps": round(mbps, 2),
            "code": int(code),
            "ms_total": round((time.monotonic() - started) * 1000),
            "error": None,
        }
    except urllib.error.HTTPError as e:
        elapsed = max(time.monotonic() - started, 0.001)
        # Some endpoints accept upload then return non-2xx; still count if body was sent
        mbps = (len(payload) * 8) / elapsed / 1_000_000
        if int(e.code) < 500:
            return {
                "url": url,
                "ok": True,
                "bytes": len(payload),
                "sec": round(elapsed, 3),
                "mbps": round(mbps, 2),
                "code": int(e.code),
                "ms_total": round((time.monotonic() - started) * 1000),
                "error": f"HTTP {e.code}",
            }
        return {
            "url": url,
            "ok": False,
            "bytes": len(payload),
            "sec": round(elapsed, 3),
            "mbps": None,
            "code": int(e.code),
            "ms_total": round((time.monotonic() - started) * 1000),
            "error": f"HTTP {e.code}",
        }
    except Exception as e:
        return {
            "url": url,
            "ok": False,
            "bytes": nbytes,
            "sec": round(time.monotonic() - started, 3),
            "mbps": None,
            "code": None,
            "ms_total": round((time.monotonic() - started) * 1000),
            "error": str(e),
        }


def collect_speed_tests(
    enabled: bool,
    profile: str,
    http_stats: dict[str, Any],
    bytes_list: list[int],
) -> list[str]:
    lines = section("Internet speed test (download + upload)")
    if not enabled:
        lines.append("Skipped: net_speed_test=false")
        return lines

    http_ok = http_stats.get("ok", 0)
    if profile in ("NO_INTERNET_OR_AIRGAP", "DNS_OK_NO_EGRESS") or http_ok == 0:
        lines.append(
            f"Skipped: internet/HTTP is not sufficient (profile={profile}, http_ok={http_ok})."
        )
        return lines

    lines.append(
        "Cloudflare speed endpoint: __down (download) + __up (upload). Approximate measurement."
    )

    # ----- Download -----
    lines.append("--- Download ---")
    lines.append(f"{'RESULT':<6}  {'Mbps':>8}  {'MB':>8}  {'sec':>7}  SIZE")
    lines.append("-" * 70)
    dl_results = []
    for n in bytes_list:
        url = f"https://speed.cloudflare.com/__down?bytes={n}"
        r = download_speed_one(url, timeout=90.0)
        dl_results.append(r)
        if r["ok"]:
            mb = r["bytes"] / 1_000_000
            lines.append(
                f"{'OK':<6}  {r['mbps']:>8.2f}  {mb:>8.2f}  {r['sec']:>7.3f}  {n} bytes"
            )
        else:
            lines.append(
                f"{'FAIL':<6}  {'-':>8}  {'-':>8}  {r['sec']:>7.3f}  {n} bytes → {r['error']}"
            )

    dl_speeds = [r["mbps"] for r in dl_results if r.get("ok") and r.get("mbps")]
    if dl_speeds:
        best_dl = dl_speeds[-1]
        avg_dl = sum(dl_speeds) / len(dl_speeds)
        lines.append(
            f"Download summary: last={best_dl:.2f} Mbps | avg={avg_dl:.2f} Mbps "
            f"({len(dl_speeds)}/{len(dl_results)} successful)"
        )
    else:
        lines.append("Download measurement failed.")
        fb = download_speed_one(
            "http://archive.ubuntu.com/ubuntu/ls-lR.gz", timeout=45.0
        )
        if fb["ok"] and fb["mbps"]:
            lines.append(
                f"Fallback download (archive.ubuntu.com): {fb['mbps']:.2f} Mbps "
                f"({fb['bytes']/1e6:.2f} MB / {fb['sec']:.2f}s)"
            )
            dl_speeds = [fb["mbps"]]

    # ----- Upload -----
    lines.append("")
    lines.append("--- Upload ---")
    lines.append(f"{'RESULT':<6}  {'Mbps':>8}  {'MB':>8}  {'sec':>7}  SIZE")
    lines.append("-" * 70)
    up_results = []
    up_url = "https://speed.cloudflare.com/__up"
    # Slightly smaller defaults are enough for upload; use the given list
    for n in bytes_list:
        r = upload_speed_one(up_url, n, timeout=90.0)
        up_results.append(r)
        if r["ok"] and r.get("mbps") is not None:
            mb = r["bytes"] / 1_000_000
            lines.append(
                f"{'OK':<6}  {r['mbps']:>8.2f}  {mb:>8.2f}  {r['sec']:>7.3f}  {n} bytes"
            )
        else:
            lines.append(
                f"{'FAIL':<6}  {'-':>8}  {'-':>8}  {r['sec']:>7.3f}  {n} bytes → {r['error']}"
            )

    up_speeds = [r["mbps"] for r in up_results if r.get("ok") and r.get("mbps")]
    if up_speeds:
        best_up = up_speeds[-1]
        avg_up = sum(up_speeds) / len(up_speeds)
        lines.append(
            f"Upload summary: last={best_up:.2f} Mbps | avg={avg_up:.2f} Mbps "
            f"({len(up_speeds)}/{len(up_results)} successful)"
        )
    else:
        lines.append(
            "Upload measurement failed (outbound POST blocked / proxy may be cutting uploads)."
        )

    lines.append("")
    if dl_speeds and up_speeds:
        lines.append(
            f"Summary: ↓ download={dl_speeds[-1]:.2f} Mbps | ↑ upload={up_speeds[-1]:.2f} Mbps"
        )
        d, u = dl_speeds[-1], up_speeds[-1]
        if d < 5 or u < 2:
            lines.append(
                "Note: Low speed — large image pull / push and apt may take a long time."
            )
        elif d < 25 or u < 10:
            lines.append("Note: Medium speed — online install is possible; be patient on large transfers.")
        else:
            lines.append("Note: Good speed — suitable for online install / registry pull-push.")
    elif dl_speeds:
        lines.append(f"Summary: ↓ download={dl_speeds[-1]:.2f} Mbps | ↑ upload=could not be measured")
    elif up_speeds:
        lines.append(f"Summary: ↓ download=could not be measured | ↑ upload={up_speeds[-1]:.2f} Mbps")
    else:
        lines.append("Summary: speed measurement could not be performed.")

    return lines


def verdict(
    dns_stats: dict[str, Any],
    tcp_stats: dict[str, Any],
    http_stats: dict[str, Any],
    ping_stats: dict[str, Any],
) -> tuple[list[str], str]:
    lines = section("OVERALL RESULT (internet access profile)")
    profile, detail, _dns_r, _tcp_r, _http_r = compute_profile(
        dns_stats, tcp_stats, http_stats
    )
    dns_ok = dns_stats.get("ok", 0)
    dns_fail = dns_stats.get("fail", 0)
    tcp_ok = tcp_stats.get("ok", 0)
    tcp_fail = tcp_stats.get("fail", 0)
    http_ok = http_stats.get("ok", 0)
    http_fail = http_stats.get("fail", 0)

    lines.append(f"Profile: {profile}")
    lines.append(f"Note: {detail}")
    lines.append(
        f"Scores: DNS {dns_ok}/{dns_ok + dns_fail} | "
        f"TCP {tcp_ok}/{tcp_ok + tcp_fail} | "
        f"HTTP {http_ok}/{http_ok + http_fail} | "
        f"ICMP {ping_stats.get('ok', 0)}/{ping_stats.get('ok', 0) + ping_stats.get('fail', 0)}"
    )
    lines.append("")
    lines.append("Install hint:")
    if profile == "INTERNET_AVAILABLE":
        lines.append("- Standard online install (apt, helm, image pull) can be attempted.")
    elif profile == "NO_INTERNET_OR_AIRGAP":
        lines.append("- Install via offline bundle / internal mirror / bastion.")
        lines.append("- If even DNS is missing, /etc/hosts or internal DNS is required.")
    elif profile == "DNS_OK_NO_EGRESS":
        lines.append("- Request outbound 80/443 or an HTTP proxy; check firewall rules.")
    elif profile == "LIMITED_DNS_BROKEN":
        lines.append("- Fix /etc/resolv.conf and corporate DNS; use an IP allow-list if needed.")
    else:
        lines.append("- Define a dedicated mirror or proxy for FAIL registry/apt URLs.")
    return lines, profile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dns-hosts",
        default=(
            "google.com,cloudflare.com,"
            "registry-1.docker.io,ghcr.io,quay.io,"
            "registry.k8s.io,pkg.k8s.io,"
            "archive.ubuntu.com,security.ubuntu.com,"
            "github.com,raw.githubusercontent.com"
        ),
    )
    parser.add_argument(
        "--ping-targets",
        default="1.1.1.1,8.8.8.8",
    )
    parser.add_argument(
        "--tcp-targets",
        default=(
            "1.1.1.1:443,8.8.8.8:53,"
            "google.com:443,github.com:443,"
            "registry-1.docker.io:443,ghcr.io:443,quay.io:443,"
            "registry.k8s.io:443,"
            "archive.ubuntu.com:80,archive.ubuntu.com:443"
        ),
    )
    parser.add_argument(
        "--http-urls",
        default=(
            "https://www.google.com/generate_204,"
            "https://github.com,"
            "https://registry-1.docker.io/v2/,"
            "https://ghcr.io,"
            "https://quay.io,"
            "https://registry.k8s.io,"
            "http://archive.ubuntu.com/ubuntu/,"
            "https://cloudflare.com"
        ),
    )
    parser.add_argument(
        "--speed-test",
        default="true",
        help="true/false — download speed test when internet is available",
    )
    parser.add_argument(
        "--speed-bytes",
        default="1000000,10000000",
        help="Comma-separated download sizes for Cloudflare __down",
    )
    args = parser.parse_args()

    dns_hosts = [x.strip() for x in args.dns_hosts.split(",") if x.strip()]
    ping_targets = [x.strip() for x in args.ping_targets.split(",") if x.strip()]
    tcp_targets = [x.strip() for x in args.tcp_targets.split(",") if x.strip()]
    http_urls = [x.strip() for x in args.http_urls.split(",") if x.strip()]
    speed_enabled = str(args.speed_test).strip().lower() in ("1", "true", "yes", "on")
    speed_bytes: list[int] = []
    for x in args.speed_bytes.split(","):
        x = x.strip()
        if not x:
            continue
        try:
            speed_bytes.append(int(x))
        except ValueError:
            pass
    if not speed_bytes:
        speed_bytes = [1_000_000, 10_000_000]

    lines: list[str] = []
    lines.append("Network / DNS / internet access report (read-only)")
    lines.extend(collect_interfaces())
    lines.extend(collect_routes())
    lines.extend(collect_gateway_ping())
    lines.extend(collect_dns_config())
    dns_lines, dns_stats = collect_dns_tests(dns_hosts)
    lines.extend(dns_lines)
    ping_lines, ping_stats = collect_ping_tests(ping_targets)
    lines.extend(ping_lines)
    tcp_lines, tcp_stats = collect_tcp_tests(tcp_targets)
    lines.extend(tcp_lines)
    http_lines, http_stats = collect_http_tests(http_urls)
    lines.extend(http_lines)
    lines.extend(collect_proxy())

    profile, _detail, _a, _b, _c = compute_profile(dns_stats, tcp_stats, http_stats)
    lines.extend(
        collect_speed_tests(speed_enabled, profile, http_stats, speed_bytes)
    )

    verdict_lines, _profile = verdict(dns_stats, tcp_stats, http_stats, ping_stats)
    lines.extend(verdict_lines)
    lines.append("")
    lines.append("Details: docs/19_check_network_connectivity.md")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
