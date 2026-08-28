#!/usr/bin/env python3
"""Read-only: NetworkPolicy inventory per namespace."""
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
    lines.append(f"NetworkPolicy inventory ({scope}, read-only)")

    rc, _, err = run("kubectl cluster-info")
    if rc != 0:
        lines.append(f"kubectl access missing: {err}")
        print("\n".join(lines))
        return

    # namespaces
    if ns_filter:
        namespaces = [ns_filter]
    else:
        rc, out, err = run("kubectl get ns -o json")
        if rc != 0:
            lines.append(f"namespaces could not be retrieved: {err}")
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
        lines.append(f"NetworkPolicy list could not be retrieved: {err}")
        print("\n".join(lines))
        return

    items = json.loads(out).get("items") or []
    by_ns: dict[str, list] = defaultdict(list)
    for it in items:
        meta = it.get("metadata") or {}
        n = meta.get("namespace") or "-"
        by_ns[n].append(it)

    lines.extend(section("Namespace summary (is there a policy?)"))
    lines.append(f"{'NAMESPACE':<40} {'NETPOL':>6}  STATUS")
    lines.append("-" * 70)
    open_ns = []
    for n in sorted(namespaces):
        count = len(by_ns.get(n) or [])
        if count == 0:
            # skip system ns noise optionally still show
            status = "NO POLICY (default allow — depends on CNI)"
            open_ns.append(n)
        else:
            status = "policy defined"
        lines.append(f"{n:<40} {count:>6}  {status}")

    lines.append(
        f"Summary: ns={len(namespaces)} | ns without policy={len(open_ns)} | total NetworkPolicy={len(items)}"
    )

    lines.extend(section("NetworkPolicy details"))
    if not items:
        lines.append("(no NetworkPolicy)")
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
                sel_s = "ALL pods (empty podSelector)"
            else:
                sel_s = str(sel)
            lines.append(f"- {n}/{name}")
            lines.append(f"    policyTypes: {policy_types or '-'}")
            lines.append(f"    podSelector: {sel_s}")
            if "Ingress" in (policy_types or ["Ingress"]) or ingress is not None:
                if ingress == []:
                    lines.append("    ingress: DENY-ALL (empty list)")
                elif ingress is None and "Ingress" in (policy_types or []):
                    lines.append("    ingress: (undefined — check type)")
                else:
                    lines.append(f"    ingress rules: {len(ingress or [])}")
            if "Egress" in (policy_types or []) or egress is not None:
                if egress == []:
                    lines.append("    egress: DENY-ALL (empty list)")
                else:
                    lines.append(f"    egress rules: {len(egress or [])}")

    lines.append("")
    lines.append(
        "Note: Namespace without policy + default-allow CNI = unrestricted pod-to-pod traffic. "
        "Empty ingress [] = no ingress for that selector."
    )
    lines.append("Details: docs/28_check_network_policies.md")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
