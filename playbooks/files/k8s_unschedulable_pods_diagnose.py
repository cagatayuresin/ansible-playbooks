#!/usr/bin/env python3
"""Explain Pending, unschedulable, image pull, and crash-loop Pod states."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import subprocess
import sys


WAITING_REASONS = {
    "CrashLoopBackOff",
    "CreateContainerConfigError",
    "CreateContainerError",
    "ErrImagePull",
    "ImagePullBackOff",
    "InvalidImageName",
    "RunContainerError",
}


def kubectl_json(args: list[str]) -> dict:
    result = subprocess.run(
        ["kubectl", *args, "-o", "json"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return json.loads(result.stdout)


def parse_time(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def pod_problems(pod: dict) -> list[str]:
    status = pod.get("status", {})
    problems: list[str] = []
    phase = status.get("phase", "Unknown")
    if phase == "Pending":
        problems.append("phase=Pending")
    for condition in status.get("conditions", []):
        if condition.get("type") == "PodScheduled" and condition.get("status") == "False":
            problems.append(
                f"{condition.get('reason', 'Unschedulable')}: "
                f"{condition.get('message', '')}"
            )
    for group in (
        status.get("initContainerStatuses", []),
        status.get("containerStatuses", []),
        status.get("ephemeralContainerStatuses", []),
    ):
        for container in group:
            waiting = container.get("state", {}).get("waiting", {})
            reason = waiting.get("reason")
            if reason in WAITING_REASONS:
                problems.append(
                    f"{container.get('name')}: {reason}: {waiting.get('message', '')}"
                )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exclude-namespaces", default="")
    parser.add_argument("--max-pods", type=int, default=100)
    parser.add_argument("--events-per-pod", type=int, default=5)
    args = parser.parse_args()
    excluded = {
        item.strip()
        for item in args.exclude_namespaces.split(",")
        if item.strip()
    }

    try:
        pods = kubectl_json(["get", "pods", "--all-namespaces"])
        events = kubectl_json(["get", "events", "--all-namespaces"])
        pvcs = kubectl_json(["get", "pvc", "--all-namespaces"])
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Pod tanı kaynakları alınamadı: {exc}")
        return 2

    pvc_status: dict[tuple[str, str], str] = {}
    for pvc in pvcs.get("items", []):
        metadata = pvc.get("metadata", {})
        pvc_status[
            (
                metadata.get("namespace", "default"),
                metadata.get("name", "bilinmiyor"),
            )
        ] = pvc.get("status", {}).get("phase", "Unknown")

    events_by_uid: dict[str, list[dict]] = {}
    for event in events.get("items", []):
        involved = event.get("involvedObject", {})
        uid = involved.get("uid")
        if uid:
            events_by_uid.setdefault(uid, []).append(event)

    affected: list[tuple[dict, list[str]]] = []
    for pod in pods.get("items", []):
        namespace = pod.get("metadata", {}).get("namespace", "default")
        if namespace in excluded:
            continue
        problems = pod_problems(pod)
        if problems:
            affected.append((pod, problems))

    affected.sort(
        key=lambda item: parse_time(
            item[0].get("metadata", {}).get("creationTimestamp")
        )
    )
    affected = affected[: args.max_pods]

    print("KUBERNETES POD ZAMANLAMA / BAŞLATMA TANI RAPORU")
    print("=" * 100)
    print(f"Toplam pod: {len(pods.get('items', []))}")
    print(f"Tanı gerektiren pod: {len(affected)}")

    if not affected:
        print("[OK] Pending veya bilinen başlatma hatasına sahip pod yok")
        return 0

    now = datetime.now(timezone.utc)
    for pod, problems in affected:
        metadata = pod.get("metadata", {})
        spec = pod.get("spec", {})
        namespace = metadata.get("namespace", "default")
        name = metadata.get("name", "bilinmiyor")
        uid = metadata.get("uid", "")
        created = parse_time(metadata.get("creationTimestamp"))
        age = now - created if created.year > 1 else None

        print("\n" + "-" * 100)
        print(
            f"POD: {namespace}/{name} | node={spec.get('nodeName', '<atanmadı>')} "
            f"| yaş={str(age).split('.')[0] if age else 'bilinmiyor'}"
        )
        for problem in problems:
            print(f"  [NEDEN] {problem}")

        claims = [
            volume.get("persistentVolumeClaim", {}).get("claimName")
            for volume in spec.get("volumes", [])
            if volume.get("persistentVolumeClaim")
        ]
        for claim in claims:
            phase = pvc_status.get((namespace, claim), "Bulunamadı")
            marker = "OK" if phase == "Bound" else "PVC"
            print(f"  [{marker}] {claim}: {phase}")

        if spec.get("nodeSelector"):
            print(f"  [BİLGİ] nodeSelector={spec.get('nodeSelector')}")
        if spec.get("affinity"):
            print("  [BİLGİ] affinity kuralları mevcut")
        if spec.get("tolerations"):
            print(f"  [BİLGİ] toleration sayısı={len(spec.get('tolerations', []))}")

        pod_events = sorted(
            events_by_uid.get(uid, []),
            key=lambda event: parse_time(
                event.get("eventTime")
                or event.get("lastTimestamp")
                or event.get("metadata", {}).get("creationTimestamp")
            ),
            reverse=True,
        )
        for event in pod_events[: args.events_per_pod]:
            print(
                f"  [EVENT:{event.get('type', 'Normal')}] "
                f"{event.get('reason', '')}: {event.get('message', '')}"
            )

    if len(affected) >= args.max_pods:
        print(f"\n[WARN] Çıktı {args.max_pods} pod ile sınırlandı")
    return 0


if __name__ == "__main__":
    sys.exit(main())
