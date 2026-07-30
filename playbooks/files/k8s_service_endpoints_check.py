#!/usr/bin/env python3
"""Find Kubernetes Services without ready EndpointSlice backends."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def as_dict(value: object) -> dict:
    """Return a dictionary for nullable Kubernetes API fields."""
    return value if isinstance(value, dict) else {}


def as_list(value: object) -> list:
    """Return a list for nullable Kubernetes API fields."""
    return value if isinstance(value, list) else []


def kubectl_json(args: list[str]) -> dict:
    result = subprocess.run(
        ["kubectl", *args, "-o", "json"],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return json.loads(result.stdout)


def endpoint_is_ready(endpoint: dict) -> bool:
    conditions = as_dict(as_dict(endpoint).get("conditions"))
    ready = conditions.get("ready")
    serving = conditions.get("serving")
    terminating = conditions.get("terminating", False)
    if ready is None:
        ready = True
    if serving is None:
        serving = ready
    return bool(ready and serving and not terminating)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exclude-namespaces", default="")
    parser.add_argument("--max-findings", type=int, default=300)
    args = parser.parse_args()
    excluded = {
        item.strip()
        for item in args.exclude_namespaces.split(",")
        if item.strip()
    }

    try:
        services = kubectl_json(["get", "services", "--all-namespaces"])
        slices = kubectl_json(["get", "endpointslices", "--all-namespaces"])
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Service/EndpointSlice kaynakları alınamadı: {exc}")
        return 2

    service_items = as_list(as_dict(services).get("items"))
    slice_items = as_list(as_dict(slices).get("items"))

    slices_by_service: dict[tuple[str, str], list[dict]] = {}
    for endpoint_slice in slice_items:
        endpoint_slice = as_dict(endpoint_slice)
        metadata = as_dict(endpoint_slice.get("metadata"))
        namespace = metadata.get("namespace", "default")
        service_name = as_dict(metadata.get("labels")).get(
            "kubernetes.io/service-name", ""
        )
        if service_name:
            slices_by_service.setdefault((namespace, service_name), []).append(
                endpoint_slice
            )

    findings: list[tuple[str, str]] = []
    checked = 0
    healthy = 0

    def add(level: str, message: str) -> None:
        if len(findings) < args.max_findings:
            findings.append((level, message))

    for service in service_items:
        service = as_dict(service)
        metadata = as_dict(service.get("metadata"))
        namespace = metadata.get("namespace", "default")
        if namespace in excluded:
            continue
        name = metadata.get("name", "bilinmiyor")
        spec = as_dict(service.get("spec"))
        service_type = spec.get("type", "ClusterIP")
        prefix = f"{namespace}/{name}"
        checked += 1

        if service_type == "ExternalName":
            add("INFO", f"{prefix}: ExternalName -> {spec.get('externalName', '')}")
            healthy += 1
            continue

        related = slices_by_service.get((namespace, name), [])
        endpoints = [
            endpoint
            for endpoint_slice in related
            for endpoint in as_list(endpoint_slice.get("endpoints"))
            if isinstance(endpoint, dict)
        ]
        ready_endpoints = [
            endpoint for endpoint in endpoints if endpoint_is_ready(endpoint)
        ]

        if not related:
            level = "CRITICAL" if spec.get("selector") else "WARN"
            add(level, f"{prefix}: EndpointSlice yok")
        elif not ready_endpoints:
            add(
                "CRITICAL",
                f"{prefix}: {len(endpoints)} endpoint var fakat hazır backend yok",
            )
        else:
            healthy += 1

        if service_type == "LoadBalancer" and not (
            as_dict(as_dict(service.get("status")).get("loadBalancer")).get(
                "ingress"
            )
        ):
            add("WARN", f"{prefix}: LoadBalancer external adresi Pending")

        ports = as_list(spec.get("ports"))
        if len(ports) > 1:
            unnamed = [port for port in ports if not as_dict(port).get("name")]
            if unnamed:
                add("WARN", f"{prefix}: çoklu port içinde isimsiz port var")

        not_ready = len(endpoints) - len(ready_endpoints)
        if not_ready and ready_endpoints:
            add(
                "WARN",
                f"{prefix}: {len(ready_endpoints)} hazır, {not_ready} hazır olmayan endpoint",
            )

    print("KUBERNETES SERVICE / ENDPOINTSLICE SAĞLIK RAPORU")
    print("=" * 88)
    print(f"İncelenen Service : {checked}")
    print(f"Sağlıklı Service  : {healthy}")
    print(f"EndpointSlice     : {len(slice_items)}")
    print("-" * 88)
    for level, message in findings:
        print(f"[{level}] {message}")
    if not findings:
        print("[OK] Tüm Service'lerin hazır backend'i var")
    if len(findings) >= args.max_findings:
        print(f"[WARN] Çıktı {args.max_findings} bulgu ile sınırlandı")
    counts = {
        level: sum(1 for finding_level, _ in findings if finding_level == level)
        for level in ("CRITICAL", "WARN", "INFO")
    }
    print("-" * 88)
    print(
        f"Özet: {counts['CRITICAL']} kritik, {counts['WARN']} uyarı, "
        f"{counts['INFO']} bilgi"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
