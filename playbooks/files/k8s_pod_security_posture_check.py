#!/usr/bin/env python3
"""Heuristic Pod Security Standards posture report for running Pods."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


DANGEROUS_CAPABILITIES = {
    "ALL",
    "SYS_ADMIN",
    "SYS_MODULE",
    "SYS_PTRACE",
    "NET_ADMIN",
    "DAC_READ_SEARCH",
}


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exclude-namespaces", default="")
    parser.add_argument("--max-findings", type=int, default=400)
    args = parser.parse_args()
    excluded = {
        item.strip()
        for item in args.exclude_namespaces.split(",")
        if item.strip()
    }

    try:
        namespaces = kubectl_json(["get", "namespaces"])
        pods = kubectl_json(["get", "pods", "--all-namespaces"])
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Pod güvenlik kaynakları alınamadı: {exc}")
        return 2

    findings: list[tuple[str, str]] = []

    def add(level: str, message: str) -> None:
        if len(findings) < args.max_findings:
            findings.append((level, message))

    checked_namespaces = 0
    for namespace in namespaces.get("items", []):
        metadata = namespace.get("metadata", {})
        name = metadata.get("name", "bilinmiyor")
        if name in excluded:
            continue
        checked_namespaces += 1
        labels = metadata.get("labels", {})
        enforce = labels.get("pod-security.kubernetes.io/enforce")
        audit = labels.get("pod-security.kubernetes.io/audit")
        warn = labels.get("pod-security.kubernetes.io/warn")
        if not enforce:
            add("WARN", f"Namespace {name}: Pod Security enforce etiketi yok")
        elif enforce == "privileged":
            add("WARN", f"Namespace {name}: enforce=privileged")
        if not audit:
            add("INFO", f"Namespace {name}: Pod Security audit etiketi yok")
        if not warn:
            add("INFO", f"Namespace {name}: Pod Security warn etiketi yok")

    checked_pods = 0
    checked_containers = 0
    for pod in pods.get("items", []):
        metadata = pod.get("metadata", {})
        namespace = metadata.get("namespace", "default")
        if namespace in excluded:
            continue
        pod_name = metadata.get("name", "bilinmiyor")
        prefix = f"{namespace}/{pod_name}"
        spec = pod.get("spec", {})
        pod_security = spec.get("securityContext", {})
        checked_pods += 1

        for field in ("hostNetwork", "hostPID", "hostIPC"):
            if spec.get(field):
                add("CRITICAL", f"{prefix}: {field}=true")

        for volume in spec.get("volumes", []):
            if "hostPath" in volume:
                path = volume.get("hostPath", {}).get("path", "")
                add(
                    "CRITICAL",
                    f"{prefix}: hostPath volume {volume.get('name')} -> {path}",
                )

        pod_seccomp = pod_security.get("seccompProfile", {})
        for container_kind, containers in (
            ("container", spec.get("containers", [])),
            ("initContainer", spec.get("initContainers", [])),
            ("ephemeralContainer", spec.get("ephemeralContainers", [])),
        ):
            for container in containers:
                checked_containers += 1
                name = container.get("name", "bilinmiyor")
                label = f"{prefix}/{container_kind}/{name}"
                security = container.get("securityContext", {})

                if security.get("privileged"):
                    add("CRITICAL", f"{label}: privileged=true")
                if security.get("procMount") == "Unmasked":
                    add("CRITICAL", f"{label}: procMount=Unmasked")
                if security.get("runAsUser") == 0:
                    add("CRITICAL", f"{label}: runAsUser=0")

                run_as_non_root = security.get(
                    "runAsNonRoot", pod_security.get("runAsNonRoot")
                )
                if run_as_non_root is not True:
                    add("WARN", f"{label}: runAsNonRoot=true değil")

                if security.get("allowPrivilegeEscalation") is not False:
                    add("WARN", f"{label}: allowPrivilegeEscalation=false değil")

                added_caps = set(
                    security.get("capabilities", {}).get("add", []) or []
                )
                if added_caps:
                    level = (
                        "CRITICAL"
                        if added_caps & DANGEROUS_CAPABILITIES
                        else "WARN"
                    )
                    add(
                        level,
                        f"{label}: ek Linux capability: {','.join(sorted(added_caps))}",
                    )

                seccomp = security.get("seccompProfile") or pod_seccomp
                if not seccomp:
                    add("WARN", f"{label}: seccompProfile tanımlı değil")
                elif seccomp.get("type") == "Unconfined":
                    add("CRITICAL", f"{label}: seccompProfile=Unconfined")

                if security.get("readOnlyRootFilesystem") is not True:
                    add("INFO", f"{label}: readOnlyRootFilesystem=true değil")

                for port in container.get("ports", []):
                    if int(port.get("hostPort", 0) or 0) > 0:
                        add(
                            "WARN",
                            f"{label}: hostPort={port.get('hostPort')}",
                        )

    print("KUBERNETES POD GÜVENLİK DURUŞU RAPORU")
    print("=" * 92)
    print(f"İncelenen namespace : {checked_namespaces}")
    print(f"İncelenen pod       : {checked_pods}")
    print(f"İncelenen container : {checked_containers}")
    print("Not: Bu rapor resmi admission evaluator yerine sezgisel bir ön kontroldür.")
    print("-" * 92)
    for level, message in findings:
        print(f"[{level}] {message}")
    if not findings:
        print("[OK] Tanımlı politika kapsamında güvenlik bulgusu yok")
    if len(findings) >= args.max_findings:
        print(f"[WARN] Çıktı {args.max_findings} bulgu ile sınırlandı")
    counts = {
        level: sum(1 for finding_level, _ in findings if finding_level == level)
        for level in ("CRITICAL", "WARN", "INFO")
    }
    print("-" * 92)
    print(
        f"Özet: {counts['CRITICAL']} kritik, {counts['WARN']} uyarı, "
        f"{counts['INFO']} bilgi"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
