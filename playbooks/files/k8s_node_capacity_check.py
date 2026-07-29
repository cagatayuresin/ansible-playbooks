#!/usr/bin/env python3
"""Salt-okunur: node conditions + capacity (requests/limits vs allocatable + top)."""
from __future__ import annotations

import json
import subprocess
from typing import Any


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


def parse_cpu(val: str | None) -> float:
    """Return millicores."""
    if not val:
        return 0.0
    s = str(val)
    if s.endswith("m"):
        return float(s[:-1])
    return float(s) * 1000.0


def parse_mem(val: str | None) -> float:
    """Return bytes approx."""
    if not val:
        return 0.0
    s = str(val)
    units = {
        "Ki": 1024,
        "Mi": 1024**2,
        "Gi": 1024**3,
        "Ti": 1024**4,
        "K": 1000,
        "M": 1000**2,
        "G": 1000**3,
        "T": 1000**4,
    }
    for u, mult in units.items():
        if s.endswith(u):
            return float(s[: -len(u)]) * mult
    return float(s)


def fmt_cpu_m(m: float) -> str:
    if m >= 1000:
        return f"{m/1000:.2f}"
    return f"{int(m)}m"


def fmt_bytes(b: float) -> str:
    for u, m in (("Ti", 1024**4), ("Gi", 1024**3), ("Mi", 1024**2)):
        if b >= m:
            return f"{b/m:.1f}{u}"
    return f"{int(b)}B"


def main() -> None:
    lines: list[str] = []
    lines.append("Node conditions + capacity raporu (salt-okunur)")

    rc, _, err = run("kubectl cluster-info")
    if rc != 0:
        lines.append(f"kubectl erişimi yok: {err}")
        print("\n".join(lines))
        return

    rc, out, err = run("kubectl get nodes -o json")
    if rc != 0 or not out:
        lines.append(f"nodes alınamadı: {err}")
        print("\n".join(lines))
        return
    nodes = (json.loads(out).get("items") or [])

    # Pods for request/limit aggregation
    rc, pout, _ = run("kubectl get pods -A -o json")
    pods = []
    if rc == 0 and pout:
        pods = json.loads(pout).get("items") or []

    # metrics (optional)
    top_map: dict[str, dict[str, str]] = {}
    rc, tout, _ = run("kubectl top nodes --no-headers")
    if rc == 0 and tout:
        for line in tout.splitlines():
            parts = line.split()
            if len(parts) >= 5:
                # NAME CPU(cores) CPU% MEMORY(bytes) MEMORY%
                top_map[parts[0]] = {
                    "cpu": parts[1],
                    "cpu_pct": parts[2],
                    "mem": parts[3],
                    "mem_pct": parts[4],
                }

    lines.extend(section("Node conditions"))
    lines.append(
        f"{'NODE':<28} {'READY':<8} {'PRESSURE/OTHER':<40}  AGE/ROLES"
    )
    lines.append("-" * 110)
    not_ready = []
    for n in nodes:
        name = (n.get("metadata") or {}).get("name") or "-"
        status = n.get("status") or {}
        conds = {c.get("type"): c for c in (status.get("conditions") or [])}
        ready = (conds.get("Ready") or {}).get("status") or "?"
        bad = []
        for t in (
            "MemoryPressure",
            "DiskPressure",
            "PIDPressure",
            "NetworkUnavailable",
        ):
            st = (conds.get(t) or {}).get("status")
            if st == "True":
                bad.append(t)
        roles = []
        labels = (n.get("metadata") or {}).get("labels") or {}
        for k, v in labels.items():
            if "node-role.kubernetes.io/" in k:
                roles.append(k.split("/")[-1] or "master")
        role_s = ",".join(roles) if roles else "worker?"
        press = ",".join(bad) if bad else "yok"
        lines.append(f"{name:<28} {ready:<8} {press:<40}  roles={role_s}")
        if ready != "True" or bad:
            not_ready.append(name)

    if not_ready:
        lines.append(f"Dikkat gereken node'lar: {', '.join(not_ready)}")
    else:
        lines.append("Tüm node'lar Ready ve pressure yok.")

    # Capacity per node
    lines.extend(section("Capacity: allocatable vs requests/limits vs usage"))
    lines.append(
        f"{'NODE':<24} {'CPU alloc':>10} {'req%':>7} {'lim%':>7} {'use':>10}  "
        f"{'MEM alloc':>10} {'req%':>7} {'lim%':>7} {'use':>10}"
    )
    lines.append("-" * 120)

    for n in nodes:
        name = (n.get("metadata") or {}).get("name") or "-"
        status = n.get("status") or {}
        alloc = status.get("allocatable") or {}
        cpu_alloc = parse_cpu(alloc.get("cpu"))
        mem_alloc = parse_mem(alloc.get("memory"))

        cpu_req = cpu_lim = mem_req = mem_lim = 0.0
        for p in pods:
            spec = p.get("spec") or {}
            if spec.get("nodeName") != name:
                continue
            phase = (p.get("status") or {}).get("phase")
            if phase in ("Succeeded", "Failed"):
                continue
            for c in (spec.get("containers") or []):
                res = c.get("resources") or {}
                req = res.get("requests") or {}
                lim = res.get("limits") or {}
                cpu_req += parse_cpu(req.get("cpu"))
                cpu_lim += parse_cpu(lim.get("cpu"))
                mem_req += parse_mem(req.get("memory"))
                mem_lim += parse_mem(lim.get("memory"))

        cpu_req_pct = (cpu_req / cpu_alloc * 100) if cpu_alloc else 0
        cpu_lim_pct = (cpu_lim / cpu_alloc * 100) if cpu_alloc else 0
        mem_req_pct = (mem_req / mem_alloc * 100) if mem_alloc else 0
        mem_lim_pct = (mem_lim / mem_alloc * 100) if mem_alloc else 0

        top = top_map.get(name) or {}
        use_cpu = top.get("cpu", "-")
        use_cpu_pct = top.get("cpu_pct", "-")
        use_mem = top.get("mem", "-")
        use_mem_pct = top.get("mem_pct", "-")
        use_cpu_s = f"{use_cpu}({use_cpu_pct})" if top else "n/a"
        use_mem_s = f"{use_mem}({use_mem_pct})" if top else "n/a"

        lines.append(
            f"{name:<24} {fmt_cpu_m(cpu_alloc):>10} {cpu_req_pct:>6.0f}% {cpu_lim_pct:>6.0f}% {use_cpu_s:>10}  "
            f"{fmt_bytes(mem_alloc):>10} {mem_req_pct:>6.0f}% {mem_lim_pct:>6.0f}% {use_mem_s:>10}"
        )
        warn = []
        if cpu_req_pct >= 90:
            warn.append("CPU request yüksek")
        if mem_req_pct >= 90:
            warn.append("MEM request yüksek")
        if top:
            try:
                if float(str(use_cpu_pct).replace("%", "")) >= 85:
                    warn.append("CPU usage yüksek")
                if float(str(use_mem_pct).replace("%", "")) >= 85:
                    warn.append("MEM usage yüksek")
            except Exception:
                pass
        if warn:
            lines.append(f"{'':24}  → {', '.join(warn)}")

    if not top_map:
        lines.append(
            "Not: kubectl top nodes alınamadı (metrics-server?). Usage sütunu n/a — 14/15."
        )

    lines.append("")
    lines.append(
        "Yorum: req% = pod request toplamı / allocatable; lim% = limit toplamı / allocatable; "
        "use = anlık metrics-server."
    )
    lines.append("Detay: docs/24_check_node_capacity.md")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
