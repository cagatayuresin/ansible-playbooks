#!/usr/bin/env python3
"""Audit workload probes, resources, replica resilience, and PDB coverage."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


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


def selector_matches(selector: dict, labels: dict[str, str]) -> bool:
    for key, value in selector.get("matchLabels", {}).items():
        if labels.get(key) != value:
            return False
    for expression in selector.get("matchExpressions", []):
        key = expression.get("key", "")
        operator = expression.get("operator", "")
        values = expression.get("values", [])
        if operator == "In" and labels.get(key) not in values:
            return False
        if operator == "NotIn" and labels.get(key) in values:
            return False
        if operator == "Exists" and key not in labels:
            return False
        if operator == "DoesNotExist" and key in labels:
            return False
    return True


def image_has_mutable_tag(image: str) -> bool:
    last_segment = image.rsplit("/", 1)[-1]
    if "@sha256:" in image:
        return False
    if ":" not in last_segment:
        return True
    return last_segment.rsplit(":", 1)[-1] == "latest"


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
        workloads = kubectl_json(
            [
                "get",
                "deployments,statefulsets,daemonsets",
                "--all-namespaces",
            ]
        )
        pdb_data = kubectl_json(["get", "pdb", "--all-namespaces"])
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Kubernetes kaynakları alınamadı: {exc}")
        return 2

    pdbs_by_namespace: dict[str, list[dict]] = {}
    for pdb in pdb_data.get("items", []):
        namespace = pdb.get("metadata", {}).get("namespace", "default")
        pdbs_by_namespace.setdefault(namespace, []).append(pdb)

    findings: list[tuple[str, str]] = []
    workload_count = 0
    container_count = 0

    def add(level: str, message: str) -> None:
        if len(findings) < args.max_findings:
            findings.append((level, message))

    for workload in workloads.get("items", []):
        metadata = workload.get("metadata", {})
        namespace = metadata.get("namespace", "default")
        if namespace in excluded:
            continue
        name = metadata.get("name", "bilinmiyor")
        kind = workload.get("kind", "Workload")
        prefix = f"{namespace}/{kind}/{name}"
        spec = workload.get("spec", {})
        template_spec = spec.get("template", {}).get("spec", {})
        template_labels = (
            spec.get("template", {}).get("metadata", {}).get("labels", {})
        )
        workload_count += 1

        if kind in {"Deployment", "StatefulSet"}:
            replicas = int(spec.get("replicas", 1) or 0)
            if replicas < 2:
                add("WARN", f"{prefix}: replica sayısı {replicas}; tek hata noktası")
            if replicas >= 2:
                matching_pdb = any(
                    selector_matches(pdb.get("spec", {}).get("selector", {}), template_labels)
                    for pdb in pdbs_by_namespace.get(namespace, [])
                )
                if not matching_pdb:
                    add("WARN", f"{prefix}: eşleşen PodDisruptionBudget yok")
                if not template_spec.get("topologySpreadConstraints") and not (
                    template_spec.get("affinity", {})
                    .get("podAntiAffinity", {})
                    .get("requiredDuringSchedulingIgnoredDuringExecution")
                ):
                    add(
                        "INFO",
                        f"{prefix}: zorunlu anti-affinity/topology spread tanımlı değil",
                    )

        for container_type, containers in (
            ("container", template_spec.get("containers", [])),
            ("initContainer", template_spec.get("initContainers", [])),
        ):
            for container in containers:
                container_count += 1
                container_name = container.get("name", "bilinmiyor")
                label = f"{prefix}/{container_type}/{container_name}"
                resources = container.get("resources", {})
                requests = resources.get("requests", {})
                limits = resources.get("limits", {})

                for resource in ("cpu", "memory"):
                    if not requests.get(resource):
                        add("WARN", f"{label}: {resource} request tanımlı değil")
                    if not limits.get(resource):
                        add("INFO", f"{label}: {resource} limit tanımlı değil")

                if container_type == "container":
                    if not container.get("readinessProbe"):
                        add("WARN", f"{label}: readinessProbe tanımlı değil")
                    if not container.get("livenessProbe"):
                        add("WARN", f"{label}: livenessProbe tanımlı değil")
                    if (
                        container.get("livenessProbe")
                        and not container.get("startupProbe")
                    ):
                        add(
                            "INFO",
                            f"{label}: startupProbe yok; yavaş başlayan servisleri kontrol edin",
                        )

                image = container.get("image", "")
                if image_has_mutable_tag(image):
                    add("WARN", f"{label}: değişken image etiketi kullanıyor ({image})")

    print("KUBERNETES WORKLOAD DAYANIKLILIK RAPORU")
    print("=" * 88)
    print(f"İncelenen workload: {workload_count}")
    print(f"İncelenen container: {container_count}")
    print(f"Hariç namespace'ler: {', '.join(sorted(excluded)) or 'yok'}")
    print("-" * 88)
    for level, message in findings:
        print(f"[{level}] {message}")
    if not findings:
        print("[OK] Tanımlı politika kapsamında bulgu yok")
    if len(findings) >= args.max_findings:
        print(f"[WARN] Çıktı {args.max_findings} bulgu ile sınırlandı")
    counts = {
        level: sum(1 for finding_level, _ in findings if finding_level == level)
        for level in ("WARN", "INFO")
    }
    print("-" * 88)
    print(f"Özet: {counts['WARN']} uyarı, {counts['INFO']} bilgi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
