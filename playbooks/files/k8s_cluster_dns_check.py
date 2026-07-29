#!/usr/bin/env python3
"""Salt-okunur: cluster DNS / CoreDNS health + resolution tests."""
from __future__ import annotations

import json
import subprocess


def run(cmd: str, timeout: float = 45.0) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", str(e)


def section(title: str) -> list[str]:
    return ["", f"=== {title} ==="]


def main() -> None:
    lines: list[str] = []
    lines.append("Cluster DNS / CoreDNS raporu (salt-okunur)")

    rc, _, err = run("kubectl cluster-info")
    if rc != 0:
        lines.append(f"kubectl erişimi yok: {err}")
        print("\n".join(lines))
        return

    lines.extend(section("kube-dns / CoreDNS servis"))
    rc, out, err = run("kubectl get svc -n kube-system kube-dns -o wide")
    if rc != 0:
        rc, out, err = run(
            "kubectl get svc -n kube-system -l k8s-app=kube-dns -o wide"
        )
    lines.append(out if rc == 0 else (err or "kube-dns svc yok"))

    lines.extend(section("CoreDNS / kube-dns pod'ları"))
    rc, out, _ = run(
        "kubectl get pods -n kube-system -o wide --no-headers 2>/dev/null | "
        "grep -iE 'coredns|kube-dns' || true"
    )
    lines.append(out if out else "(coredns/kube-dns pod bulunamadı)")

    # endpoints
    lines.extend(section("kube-dns Endpoints"))
    rc, out, err = run("kubectl get endpoints -n kube-system kube-dns -o yaml")
    if rc == 0 and out:
        # compact: subset addresses
        try:
            # use json instead
            rc2, jout, _ = run("kubectl get endpoints -n kube-system kube-dns -o json")
            if rc2 == 0:
                ep = json.loads(jout)
                addrs = []
                for s in ep.get("subsets") or []:
                    for a in s.get("addresses") or []:
                        addrs.append(f"{a.get('ip')} ({a.get('targetRef', {}).get('name', '-')})")
                    for a in s.get("notReadyAddresses") or []:
                        addrs.append(
                            f"NOTREADY {a.get('ip')} ({a.get('targetRef', {}).get('name', '-')})"
                        )
                lines.append("Hazır: " + (", ".join(addrs) if addrs else "(boş!)"))
            else:
                lines.append(out[:1500])
        except Exception:
            lines.append(out[:1500])
    else:
        lines.append(err or "endpoints alınamadı")

    # ConfigMap Corefile snippet
    lines.extend(section("CoreDNS ConfigMap (Corefile özeti)"))
    rc, out, _ = run(
        "kubectl get configmap -n kube-system coredns -o jsonpath='{.data.Corefile}' 2>/dev/null"
    )
    if rc == 0 and out:
        for line in out.splitlines()[:40]:
            lines.append(line)
        if len(out.splitlines()) > 40:
            lines.append("... (kısaltıldı)")
    else:
        lines.append("coredns ConfigMap/Corefile okunamadı")

    # Resolution: CoreDNS image usually has no dig/nslookup; query ClusterIP from the node.
    lines.extend(section("Çözümleme testleri (kube-dns ClusterIP üzerinden)"))
    rc, dns_ip, _ = run(
        "kubectl get svc -n kube-system kube-dns -o jsonpath='{.spec.clusterIP}' 2>/dev/null"
    )
    if not dns_ip:
        rc, dns_ip, _ = run(
            "kubectl get svc -n kube-system -l k8s-app=kube-dns "
            "-o jsonpath='{.items[0].spec.clusterIP}' 2>/dev/null"
        )
    tests = [
        "kubernetes.default.svc.cluster.local",
        "kube-dns.kube-system.svc.cluster.local",
    ]
    if dns_ip:
        lines.append(f"DNS server: {dns_ip}")
        for name in tests:
            out = err = ""
            rc = 1
            for probe in (
                f"dig +short @{dns_ip} {name} A 2>/dev/null",
                f"nslookup {name} {dns_ip} 2>/dev/null",
                f"host {name} {dns_ip} 2>/dev/null",
            ):
                rc, out, err = run(probe, timeout=15.0)
                if rc == 0 and out and "NXDOMAIN" not in out and "not found" not in out.lower():
                    break
            if rc == 0 and out and "NXDOMAIN" not in out and "not found" not in out.lower():
                lines.append(f"OK   {name}")
                for l in out.splitlines()[:6]:
                    lines.append(f"     {l}")
            else:
                lines.append(f"FAIL {name} — {err or out or 'yanıt yok'}")
    else:
        lines.append("kube-dns ClusterIP alınamadı — çözümleme atlandı.")
    # NodeLocal DNS if present
    lines.extend(section("NodeLocal DNS (varsa)"))
    rc, out, _ = run(
        "kubectl get pods -A --no-headers 2>/dev/null | grep -i node-local-dns || true"
    )
    lines.append(out if out else "(node-local-dns yok)")

    lines.append("")
    lines.append(
        "Yorum: Endpoints boş veya kubernetes.default FAIL → cluster DNS kırık; "
        "dış DNS (19) ayrı konudur."
    )
    lines.append("Detay: docs/27_check_cluster_dns.md")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
