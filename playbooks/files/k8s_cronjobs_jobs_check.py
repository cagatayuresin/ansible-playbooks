#!/usr/bin/env python3
"""Read-only: CronJob / Job failure report."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone


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


def parse_ts(s: str | None):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="")
    args = parser.parse_args()
    ns = (args.namespace or "").strip()

    lines: list[str] = []
    scope = f"namespace={ns}" if ns else "namespace=ALL"
    lines.append(f"CronJob / Job report ({scope}, read-only)")

    rc, _, err = run("kubectl cluster-info")
    if rc != 0:
        lines.append(f"kubectl access missing: {err}")
        print("\n".join(lines))
        return

    ns_flag = f"-n {ns}" if ns else "-A"

    # CronJobs
    lines.extend(section("CronJobs"))
    rc, out, err = run(f"kubectl get cronjobs {ns_flag} -o json")
    if rc != 0 or not out:
        lines.append(f"cronjobs could not be retrieved: {err}")
    else:
        items = json.loads(out).get("items") or []
        if not items:
            lines.append("(no CronJob)")
        else:
            lines.append(
                f"{'NS/NAME':<45} {'SCH':<20} {'SUSPEND':<8} {'LAST_SCHEDULE':<22} {'ACTIVE':>6}"
            )
            lines.append("-" * 110)
            for cj in items:
                meta = cj.get("metadata") or {}
                cns = meta.get("namespace") or "-"
                name = meta.get("name") or "-"
                spec = cj.get("spec") or {}
                status = cj.get("status") or {}
                sched = spec.get("schedule") or "-"
                susp = str(spec.get("suspend") or False)
                last = status.get("lastScheduleTime") or "-"
                active = len(status.get("active") or [])
                lines.append(
                    f"{cns + '/' + name:<45} {sched:<20} {susp:<8} {str(last)[:22]:<22} {active:>6}"
                )
            lines.append(f"Total CronJob: {len(items)}")

    # Jobs — especially Failed
    lines.extend(section("Jobs (Failed / active problems first)"))
    rc, out, err = run(f"kubectl get jobs {ns_flag} -o json")
    if rc != 0 or not out:
        lines.append(f"jobs could not be retrieved: {err}")
        print("\n".join(lines))
        return

    jobs = json.loads(out).get("items") or []
    parsed = []
    for j in jobs:
        meta = j.get("metadata") or {}
        status = j.get("status") or {}
        spec = j.get("spec") or {}
        cns = meta.get("namespace") or "-"
        name = meta.get("name") or "-"
        succeeded = int(status.get("succeeded") or 0)
        failed = int(status.get("failed") or 0)
        active = int(status.get("active") or 0)
        completions = int((spec.get("completions") or 1))
        start = status.get("startTime")
        completion = status.get("completionTime")
        conds = status.get("conditions") or []
        reason = "-"
        for c in conds:
            if c.get("type") in ("Failed", "Complete") and c.get("status") == "True":
                reason = c.get("reason") or c.get("type") or reason
        state = "Failed" if failed and not succeeded else (
            "Complete" if succeeded >= completions else ("Active" if active else "Unknown")
        )
        parsed.append(
            {
                "ref": f"{cns}/{name}",
                "state": state,
                "succeeded": succeeded,
                "failed": failed,
                "active": active,
                "start": start,
                "completion": completion,
                "reason": reason,
                "backoff": spec.get("backoffLimit"),
            }
        )

    order = {"Failed": 0, "Active": 1, "Unknown": 2, "Complete": 3}
    parsed.sort(key=lambda x: (order.get(x["state"], 9), x["ref"]))

    failed_jobs = [p for p in parsed if p["state"] == "Failed"]
    lines.append(f"Total Job: {len(parsed)} | Failed: {len(failed_jobs)}")
    lines.append(
        f"{'STATE':<10} {'S/F/A':>8}  {'NS/NAME':<45}  START / REASON"
    )
    lines.append("-" * 110)
    # show failed first already sorted; limit complete noise
    shown = 0
    for p in parsed:
        if p["state"] == "Complete" and shown > 40:
            continue
        sfa = f"{p['succeeded']}/{p['failed']}/{p['active']}"
        lines.append(
            f"{p['state']:<10} {sfa:>8}  {p['ref']:<45}  {str(p['start'] or '-')[:22]}  {p['reason']}"
        )
        shown += 1
        if shown >= 60:
            lines.append(f"... truncated (total {len(parsed)} jobs)")
            break

    if failed_jobs:
        lines.append("")
        lines.append("Failed job references:")
        for p in failed_jobs[:30]:
            lines.append(f"  - {p['ref']}")

    lines.append("")
    lines.append(
        "Note: Failed CronJob children are usually ImagePull/OOM/backoff — combine with 01, 17, 22."
    )
    lines.append("Details: docs/26_check_cronjobs_jobs.md")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
