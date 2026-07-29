#!/usr/bin/env python3
"""Salt-okunur: K8s API/etcd certs + Ingress TLS domain/expiry report."""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def run(cmd: str, timeout: float = 60.0, env: dict | None = None) -> tuple[int, str, str]:
    e = os.environ.copy()
    if env:
        e.update(env)
    try:
        p = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=e,
        )
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as ex:
        return 1, "", str(ex)


def section(title: str) -> list[str]:
    return ["", f"=== {title} ==="]


def parse_openssl_dates(pem_or_path: str, is_path: bool = False) -> dict[str, Any]:
    """Return subject, not_before, not_after, san, days_left."""
    result: dict[str, Any] = {
        "ok": False,
        "subject": None,
        "issuer": None,
        "not_before": None,
        "not_after": None,
        "san": [],
        "days_left": None,
        "error": None,
    }
    if not shutil.which("openssl"):
        result["error"] = "openssl yok"
        return result

    if is_path:
        cmd = (
            f"openssl x509 -in {pem_or_path} -noout -subject -issuer -dates "
            f"-ext subjectAltName 2>/dev/null"
        )
        rc, out, err = run(cmd)
    else:
        with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as f:
            f.write(pem_or_path)
            tmp = f.name
        try:
            cmd = (
                f"openssl x509 -in {tmp} -noout -subject -issuer -dates "
                f"-ext subjectAltName 2>/dev/null"
            )
            rc, out, err = run(cmd)
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    if rc != 0 or not out:
        result["error"] = err or "openssl parse failed"
        return result

    for line in out.splitlines():
        if line.startswith("subject="):
            result["subject"] = line[len("subject=") :].strip()
        elif line.startswith("issuer="):
            result["issuer"] = line[len("issuer=") :].strip()
        elif line.startswith("notBefore="):
            result["not_before"] = line[len("notBefore=") :].strip()
        elif line.startswith("notAfter="):
            result["not_after"] = line[len("notAfter=") :].strip()
        elif "DNS:" in line or "IP Address:" in line:
            sans = re.findall(r"DNS:([^,\s]+)", line)
            sans += re.findall(r"IP Address:([^,\s]+)", line)
            result["san"].extend(sans)

    # Parse notAfter
    if result["not_after"]:
        raw = result["not_after"]
        dt = None
        for fmt in ("%b %d %H:%M:%S %Y %Z", "%b %d %H:%M:%S %Y GMT"):
            try:
                dt = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
                break
            except Exception:
                continue
        if dt is None:
            # try date -d via shell
            rc2, out2, _ = run(f"date -u -d '{raw}' +%s")
            if rc2 == 0 and out2.isdigit():
                dt = datetime.fromtimestamp(int(out2), tz=timezone.utc)
        if dt:
            now = datetime.now(timezone.utc)
            result["days_left"] = int((dt - now).total_seconds() // 86400)
            result["not_after_iso"] = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            result["ok"] = True
    return result


def severity(days: int | None) -> str:
    if days is None:
        return "BILINMIYOR"
    if days < 0:
        return "SURESI_DOLMUS"
    if days <= 7:
        return "KRITIK"
    if days <= 30:
        return "UYARI"
    if days <= 90:
        return "YAKLASIYOR"
    return "OK"


def collect_kubeadm_certs() -> list[str]:
    lines = section("kubeadm certs check-expiration")
    if not shutil.which("kubeadm"):
        lines.append("kubeadm yok — atlandı (muhtemelen k3s veya başka dağıtım).")
        return lines
    rc, out, err = run("kubeadm certs check-expiration")
    if rc == 0 and out:
        lines.append(out)
    else:
        lines.append(err or "kubeadm certs check-expiration başarısız")
    return lines


def collect_pki_files(paths: list[str]) -> list[str]:
    lines = section("Control-plane PEM dosyaları (openssl)")
    found_any = False
    rows = []
    for pattern_root in paths:
        root = Path(pattern_root)
        if not root.is_dir():
            continue
        for crt in sorted(root.rglob("*.crt")):
            # skip huge trees / unwanted
            if "backup" in str(crt).lower():
                continue
            found_any = True
            info = parse_openssl_dates(str(crt), is_path=True)
            rows.append((str(crt), info))
        for pem in sorted(root.glob("*.pem")):
            if pem.suffix == ".pem" and "key" in pem.name.lower():
                continue
            # client certs sometimes .pem
            if "key" in pem.name.lower():
                continue
            found_any = True
            info = parse_openssl_dates(str(pem), is_path=True)
            rows.append((str(pem), info))

    if not found_any:
        lines.append(
            "Bilinen PKI dizinleri bulunamadı "
            "(/etc/kubernetes/pki, /var/lib/rancher/k3s/server/tls)."
        )
        return lines

    lines.append(
        f"{'SEVIYE':<14} {'KALAN_GUN':>10}  {'BITIS':<22}  DOSYA"
    )
    lines.append("-" * 110)
    rows.sort(
        key=lambda x: (
            x[1].get("days_left") is None,
            x[1].get("days_left") if x[1].get("days_left") is not None else 99999,
        )
    )
    for path, info in rows:
        days = info.get("days_left")
        sev = severity(days)
        bitis = info.get("not_after_iso") or info.get("not_after") or "-"
        lines.append(
            f"{sev:<14} {str(days) if days is not None else '-':>10}  {str(bitis)[:22]:<22}  {path}"
        )
        if info.get("subject"):
            lines.append(f"{'':14} {'':10}  {'':22}  subject: {info['subject']}")
    return lines


def kubectl_json(args: str) -> Any | None:
    rc, out, err = run(f"kubectl {args} -o json")
    if rc != 0 or not out:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def collect_ingress_tls() -> list[str]:
    lines = section("Ingress TLS — domainler ve süreler")
    rc, _, err = run("kubectl cluster-info")
    if rc != 0:
        lines.append(f"kubectl erişimi yok: {err or 'cluster-info failed'}")
        return lines

    data = kubectl_json("get ingress -A")
    if data is None:
        lines.append("Ingress listesi alınamadı (CRD yok veya yetki yok).")
        return lines

    items = data.get("items") or []
    if not items:
        lines.append("Cluster'da Ingress kaynağı yok.")
        return lines

    lines.append(
        f"{'SEVIYE':<14} {'KALAN':>7}  {'BITIS':<22}  {'NS/INGRESS':<40}  DOMAINS / SECRET"
    )
    lines.append("-" * 120)

    summaries = []
    for ing in items:
        meta = ing.get("metadata") or {}
        ns = meta.get("namespace") or "-"
        name = meta.get("name") or "-"
        spec = ing.get("spec") or {}
        # hosts from rules
        hosts = []
        for rule in spec.get("rules") or []:
            h = rule.get("host")
            if h:
                hosts.append(h)
        tls_list = spec.get("tls") or []
        if not tls_list:
            summaries.append(
                {
                    "sev": "TLS_YOK",
                    "days": None,
                    "bitis": "-",
                    "ref": f"{ns}/{name}",
                    "hosts": hosts or ["(host yok)"],
                    "secret": "-",
                    "detail": "Ingress TLS bloğu tanımlı değil",
                }
            )
            continue

        for tls in tls_list:
            secret_name = tls.get("secretName") or ""
            tls_hosts = tls.get("hosts") or hosts
            if not secret_name:
                summaries.append(
                    {
                        "sev": "SECRET_YOK",
                        "days": None,
                        "bitis": "-",
                        "ref": f"{ns}/{name}",
                        "hosts": tls_hosts or hosts,
                        "secret": "-",
                        "detail": "tls.secretName boş",
                    }
                )
                continue

            sec = kubectl_json(f"get secret -n {ns} {secret_name}")
            if not sec:
                summaries.append(
                    {
                        "sev": "SECRET_EKSIK",
                        "days": None,
                        "bitis": "-",
                        "ref": f"{ns}/{name}",
                        "hosts": tls_hosts,
                        "secret": secret_name,
                        "detail": "Secret bulunamadı",
                    }
                )
                continue

            sdata = sec.get("data") or {}
            crt_b64 = sdata.get("tls.crt") or sdata.get("cert") or sdata.get("certificate")
            if not crt_b64:
                summaries.append(
                    {
                        "sev": "CERT_YOK",
                        "days": None,
                        "bitis": "-",
                        "ref": f"{ns}/{name}",
                        "hosts": tls_hosts,
                        "secret": secret_name,
                        "detail": "Secret içinde tls.crt yok",
                    }
                )
                continue
            try:
                pem = base64.b64decode(crt_b64).decode("utf-8", errors="replace")
            except Exception as e:
                summaries.append(
                    {
                        "sev": "DECODE_HATA",
                        "days": None,
                        "bitis": "-",
                        "ref": f"{ns}/{name}",
                        "hosts": tls_hosts,
                        "secret": secret_name,
                        "detail": str(e),
                    }
                )
                continue

            info = parse_openssl_dates(pem, is_path=False)
            days = info.get("days_left")
            san = info.get("san") or []
            domain_list = tls_hosts or san or hosts
            summaries.append(
                {
                    "sev": severity(days),
                    "days": days,
                    "bitis": info.get("not_after_iso") or info.get("not_after") or "-",
                    "ref": f"{ns}/{name}",
                    "hosts": domain_list,
                    "secret": f"{ns}/{secret_name}",
                    "subject": info.get("subject"),
                    "issuer": info.get("issuer"),
                    "san": san,
                    "detail": info.get("error"),
                }
            )

    def sort_key(s):
        order = {
            "SURESI_DOLMUS": 0,
            "KRITIK": 1,
            "UYARI": 2,
            "YAKLASIYOR": 3,
            "SECRET_EKSIK": 4,
            "CERT_YOK": 4,
            "SECRET_YOK": 5,
            "TLS_YOK": 6,
            "OK": 7,
        }
        return (
            order.get(s["sev"], 50),
            s["days"] if s["days"] is not None else 99999,
            s["ref"],
        )

    summaries.sort(key=sort_key)
    for s in summaries:
        days_s = str(s["days"]) if s["days"] is not None else "-"
        hosts_s = ", ".join(s["hosts"][:8])
        if len(s["hosts"]) > 8:
            hosts_s += f" (+{len(s['hosts']) - 8})"
        lines.append(
            f"{s['sev']:<14} {days_s:>7}  {str(s['bitis'])[:22]:<22}  {s['ref']:<40}  domains: {hosts_s}"
        )
        lines.append(
            f"{'':14} {'':7}  {'':22}  {'':40}  secret: {s['secret']}"
        )
        if s.get("issuer"):
            lines.append(
                f"{'':14} {'':7}  {'':22}  {'':40}  issuer: {s['issuer']}"
            )
        if s.get("san"):
            lines.append(
                f"{'':14} {'':7}  {'':22}  {'':40}  SAN: {', '.join(s['san'][:12])}"
            )
        if s.get("detail") and s["sev"] not in ("OK", "YAKLASIYOR", "UYARI", "KRITIK", "SURESI_DOLMUS"):
            lines.append(
                f"{'':14} {'':7}  {'':22}  {'':40}  not: {s['detail']}"
            )

    # counts
    from collections import Counter

    c = Counter(s["sev"] for s in summaries)
    lines.append(f"Ingress özet: {dict(c)} | toplam_ingress_tls_kaydı={len(summaries)}")
    return lines


def collect_cert_manager() -> list[str]:
    lines = section("cert-manager Certificate kaynakları (varsa)")
    data = kubectl_json("get certificates.cert-manager.io -A")
    if data is None:
        # try short name
        data = kubectl_json("get certificate -A")
    if data is None:
        lines.append("cert-manager Certificate CRD yok veya listelenemedi.")
        return lines
    items = data.get("items") or []
    if not items:
        lines.append("Certificate kaynağı yok.")
        return lines

    lines.append(
        f"{'READY':<8} {'RENEWAL':<22} {'NS/NAME':<40}  DNS / SECRET"
    )
    lines.append("-" * 110)
    for it in items:
        meta = it.get("metadata") or {}
        ns = meta.get("namespace") or "-"
        name = meta.get("name") or "-"
        spec = it.get("spec") or {}
        status = it.get("status") or {}
        dns = spec.get("dnsNames") or []
        secret = spec.get("secretName") or "-"
        renew = status.get("renewalTime") or status.get("notAfter") or "-"
        ready = "-"
        for cond in status.get("conditions") or []:
            if cond.get("type") == "Ready":
                ready = str(cond.get("status"))
        lines.append(
            f"{ready:<8} {str(renew)[:22]:<22}  {ns + '/' + name:<40}  dns={', '.join(dns[:6])} secret={secret}"
        )
    lines.append(f"Toplam Certificate: {len(items)}")
    return lines


def collect_tls_secrets_scan() -> list[str]:
    """Optional: all kubernetes-type secrets expiry (can be noisy). Summarize worst ones."""
    lines = section("kubernetes.io/tls secret tarama (en kritik 25)")
    data = kubectl_json("get secrets -A --field-selector type=kubernetes.io/tls")
    if data is None:
        lines.append("TLS secret listesi alınamadı.")
        return lines
    items = data.get("items") or []
    parsed = []
    for sec in items:
        meta = sec.get("metadata") or {}
        ns = meta.get("namespace") or "-"
        name = meta.get("name") or "-"
        sdata = sec.get("data") or {}
        crt_b64 = sdata.get("tls.crt")
        if not crt_b64:
            continue
        try:
            pem = base64.b64decode(crt_b64).decode("utf-8", errors="replace")
        except Exception:
            continue
        info = parse_openssl_dates(pem, is_path=False)
        if not info.get("ok") and info.get("days_left") is None:
            continue
        parsed.append(
            {
                "ref": f"{ns}/{name}",
                "days": info.get("days_left"),
                "bitis": info.get("not_after_iso") or info.get("not_after"),
                "san": info.get("san") or [],
                "sev": severity(info.get("days_left")),
            }
        )
    parsed.sort(
        key=lambda x: (
            x["days"] is None,
            x["days"] if x["days"] is not None else 99999,
        )
    )
    lines.append(f"Toplam TLS secret: {len(items)} | parse edilen: {len(parsed)}")
    lines.append(f"{'SEVIYE':<14} {'KALAN':>7}  {'BITIS':<22}  SECRET  SAN")
    lines.append("-" * 110)
    for p in parsed[:25]:
        san = ", ".join(p["san"][:5]) if p["san"] else "-"
        lines.append(
            f"{p['sev']:<14} {str(p['days']) if p['days'] is not None else '-':>7}  "
            f"{str(p['bitis'])[:22]:<22}  {p['ref']}  {san}"
        )
    if len(parsed) > 25:
        lines.append(f"... +{len(parsed) - 25} secret daha (en kritik 25 gösterildi)")
    return lines


def main() -> None:
    lines: list[str] = []
    lines.append("TLS / Ingress / Kubernetes sertifika raporu (salt-okunur)")
    lines.extend(collect_kubeadm_certs())
    lines.extend(
        collect_pki_files(
            [
                "/etc/kubernetes/pki",
                "/var/lib/rancher/k3s/server/tls",
            ]
        )
    )
    lines.extend(collect_ingress_tls())
    lines.extend(collect_cert_manager())
    lines.extend(collect_tls_secrets_scan())
    lines.append("")
    lines.append(
        "Seviyeler: SURESI_DOLMUS (<0) | KRITIK (<=7g) | UYARI (<=30g) | "
        "YAKLASIYOR (<=90g) | OK"
    )
    lines.append("Detay: docs/21_check_tls_certificates.md")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
