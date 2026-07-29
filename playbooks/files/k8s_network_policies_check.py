#!/usr/bin/env python3
"""Salt-okunur: NetworkPolicy inventory per namespace."""
from __future__ import annotations

import json
import subprocess
from collections import defaultdict


def run(cmd: str, timeout: float = 60.0) -> tuple[int, str, str]:
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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="")
    args = parser.parse_args()
    ns_filter = (args.namespace or "").strip()

    lines: list[str] = []
    scope = f"namespace={ns_filter}" if ns_filter else "namespace=ALL"
    lines.append(f"NetworkPolicy envanteri ({scope}, salt-okunur)")

    rc, _, err = run("kubectl cluster-info")
    if rc != 0:
        lines.append(f"kubectl erişimi yok: {err}")
        print("\n".join(lines))
        return

    # namespaces
    if ns_filter:
        namespaces = [ns_filter]
    else:
        rc, out, err = run("kubectl get ns -o json")
        if rc != 0:
            lines.append(f"namespaces alınamadı: {err}")
            print("\n".join(lines))
            return
        namespaces = [
            (i.get("metadata") or {}).get("name")
            for i in (json.loads(out).get("items") or [])
        ]
        namespaces = [n for n in namespaces if n]

    ns_flag = f"-n {ns_filter}" if ns_filter else "-A"
    rc, out, err = run(f"kubectl get networkpolicies.networking.k8s.io {ns_flag} -o json")
    if rc != 0:
        # older short name
        rc, out, err = run(f"kubectl get netpol {ns_flag} -o json")
    if rc != 0 or not out:
        lines.append(f"NetworkPolicy listesi alınamadı: {err}")
        print("\n".join(lines))
        return

    items = json.loads(out).get("items") or []
    by_ns: dict[str, list] = defaultdict(list)
    for it in items:
        meta = it.get("metadata") or {}
        n = meta.get("namespace") or "-"
        by_ns[n].append(it)

    lines.extend(section("Namespace özeti (policy var mı?)"))
    lines.append(f"{'NAMESPACE':<40} {'NETPOL':>6}  DURUM")
    lines.append("-" * 70)
    open_ns = []
    for n in sorted(namespaces):
        count = len(by_ns.get(n) or [])
        if count == 0:
            # skip system ns noise optionally still show
            status = "POLICY YOK (default allow — CNI'ye bağlı)"
            open_ns.append(n)
        else:
            status = "policy tanımlı"
        lines.append(f"{n:<40} {count:>6}  {status}")

    lines.append(
        f"Özet: ns={len(namespaces)} | policy'siz ns={len(open_ns)} | toplam NetworkPolicy={len(items)}"
    )

    lines.extend(section("NetworkPolicy detayları"))
    if not items:
        lines.append("(hiç NetworkPolicy yok)")
    else:
        for it in sorted(
            items,
            key=lambda x: (
                (x.get("metadata") or {}).get("namespace") or "",
                (x.get("metadata") or {}).get("name") or "",
            ),
        ):
            meta = it.get("metadata") or {}
            spec = it.get("spec") or {}
            n = meta.get("namespace") or "-"
            name = meta.get("name") or "-"
            pod_sel = spec.get("podSelector") or {}
            policy_types = spec.get("policyTypes") or []
            ingress = spec.get("ingress")
            egress = spec.get("egress")
            sel = pod_sel.get("matchLabels") or pod_sel
            if pod_sel == {}:
                sel_s = "TÜM pod'lar (boş podSelector)"
            else:
                sel_s = str(sel)
            lines.append(f"- {n}/{name}")
            lines.append(f"    policyTypes: {policy_types or '-'}")
            lines.append(f"    podSelector: {sel_s}")
            if "Ingress" in (policy_types or ["Ingress"]) or ingress is not None:
                if ingress == []:
                    lines.append("    ingress: DENY-ALL (boş liste)")
                elif ingress is None and "Ingress" in (policy_types or []):
                    lines.append("    ingress: (tanımsız — tipe bak)")
                else:
                    lines.append(f"    ingress kuralları: {len(ingress or [])}")
            if "Egress" in (policy_types or []) or egress is not None:
                if egress == []:
                    lines.append("    egress: DENY-ALL (boş liste)")
                else:
                    lines.append(f"    egress kuralları: {len(egress or [])}")

    lines.append("")
    lines.append(
        "Yorum: Policy'siz namespace + default-allow CNI = pod'lar arası serbest trafik. "
        "Boş ingress [] = o selector için giriş yok."
    )
    lines.append("Detay: docs/28_check_network_policies.md")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
