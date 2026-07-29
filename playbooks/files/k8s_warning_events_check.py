#!/usr/bin/env python3
"""Salt-okunur: Kubernetes Warning events report."""
from __future__ import annotations

import json
import os
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
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


def parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--since-hours", type=int, default=24)
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument(
        "--namespace",
        default="",
        help="Belirli namespace; boşsa tüm namespace'ler (-A)",
    )
    args = parser.parse_args()
    ns_filter = (args.namespace or "").strip()

    scope = f"namespace={ns_filter}" if ns_filter else "namespace=ALL"
    lines: list[str] = []
    lines.append(
        f"Kubernetes Warning event raporu (son ~{args.since_hours}s, {scope}, salt-okunur)"
    )

    rc, _, err = run("kubectl cluster-info")
    if rc != 0:
        lines.append(f"kubectl erişimi yok: {err}")
        print("\n".join(lines))
        return

    if ns_filter:
        rc, out, err = run(f"kubectl get events -n {ns_filter} -o json")
    else:
        rc, out, err = run("kubectl get events -A -o json")
    if rc != 0 or not out:
        lines.append(f"events alınamadı: {err}")
        print("\n".join(lines))
        return

    data = json.loads(out)
    items = data.get("items") or []
    now = datetime.now(timezone.utc)
    cutoff = now.timestamp() - args.since_hours * 3600

    warnings = []
    for ev in items:
        if (ev.get("type") or "") != "Warning":
            continue
        # lastTimestamp / eventTime / deprecatedCount
        ts = (
            parse_ts(ev.get("lastTimestamp"))
            or parse_ts(ev.get("eventTime"))
            or parse_ts((ev.get("metadata") or {}).get("creationTimestamp"))
        )
        if ts and ts.timestamp() < cutoff:
            continue
        obj = ev.get("involvedObject") or {}
        ev_ns = (
            obj.get("namespace")
            or (ev.get("metadata") or {}).get("namespace")
            or "-"
        )
        if ns_filter and ev_ns != ns_filter:
            continue
        warnings.append(
            {
                "ts": ts,
                "ns": ev_ns,
                "kind": obj.get("kind") or "-",
                "name": obj.get("name") or "-",
                "reason": ev.get("reason") or "-",
                "count": ev.get("count") or ev.get("deprecatedCount") or 1,
                "message": (ev.get("message") or "").replace("\n", " "),
                "source": ((ev.get("source") or {}).get("component") or "-"),
            }
        )

    warnings.sort(
        key=lambda w: (w["ts"] or datetime.fromtimestamp(0, tz=timezone.utc)),
        reverse=True,
    )

    lines.extend(section("Özet"))
    lines.append(f"Kapsam: {scope}")
    lines.append(f"Warning event (filtre sonrası): {len(warnings)}")
    by_reason = Counter(w["reason"] for w in warnings)
    by_ns = Counter(w["ns"] for w in warnings)
    lines.append("En sık reason:")
    for reason, cnt in by_reason.most_common(15):
        lines.append(f"  {cnt:>4}  {reason}")
    if not ns_filter:
        lines.append("Namespace dağılımı (top):")
        for ns, cnt in by_ns.most_common(15):
            lines.append(f"  {cnt:>4}  {ns}")

    lines.extend(section(f"Son Warning event'ler (max {args.limit})"))
    lines.append(
        f"{'ZAMAN':<22} {'CNT':>4}  {'NS':<20} {'KIND/NAME':<40}  REASON / MESSAGE"
    )
    lines.append("-" * 120)
    for w in warnings[: args.limit]:
        ts_s = w["ts"].strftime("%Y-%m-%d %H:%M:%S") if w["ts"] else "-"
        kn = f"{w['kind']}/{w['name']}"
        msg = w["message"][:90]
        lines.append(
            f"{ts_s:<22} {str(w['count']):>4}  {w['ns']:<20} {kn:<40}  {w['reason']}"
        )
        lines.append(f"{'':22} {'':4}  {'':20} {'':40}  {msg}")

    if len(warnings) > args.limit:
        lines.append(f"... +{len(warnings) - args.limit} event daha")

    lines.append("")
    lines.append(
        "Yorum: FailedScheduling / FailedMount / ImagePullBackOff / OOMKilled / "
        "Unhealthy sık görülürse 01, 10, 17 playbook'ları ile birleştir."
    )
    lines.append("Detay: docs/22_check_k8s_warning_events.md")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
