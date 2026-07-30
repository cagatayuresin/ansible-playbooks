#!/usr/bin/env python3
"""Report high-risk Kubernetes RBAC roles, bindings, and service accounts."""

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


def subject_name(subject: dict) -> str:
    namespace = subject.get("namespace")
    value = f"{subject.get('kind', '?')}:{subject.get('name', '?')}"
    return f"{value}@{namespace}" if namespace else value


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
        cluster_roles = kubectl_json(["get", "clusterroles"])
        roles = kubectl_json(["get", "roles", "--all-namespaces"])
        cluster_bindings = kubectl_json(["get", "clusterrolebindings"])
        role_bindings = kubectl_json(["get", "rolebindings", "--all-namespaces"])
        service_accounts = kubectl_json(
            ["get", "serviceaccounts", "--all-namespaces"]
        )
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"[ERROR] RBAC kaynakları alınamadı: {exc}")
        return 2

    findings: list[tuple[str, str]] = []

    def add(level: str, message: str) -> None:
        if len(findings) < args.max_findings:
            findings.append((level, message))

    for binding in cluster_bindings.get("items", []):
        name = binding.get("metadata", {}).get("name", "bilinmiyor")
        role_name = binding.get("roleRef", {}).get("name", "")
        subjects = binding.get("subjects", []) or []
        subject_text = ", ".join(subject_name(subject) for subject in subjects)
        if role_name == "cluster-admin":
            add(
                "CRITICAL",
                f"ClusterRoleBinding {name}: cluster-admin -> {subject_text or 'subjects yok'}",
            )
        for subject in subjects:
            subject_value = subject.get("name", "")
            if subject_value == "system:masters":
                add("CRITICAL", f"ClusterRoleBinding {name}: system:masters bağlı")
            elif subject_value == "system:unauthenticated":
                add(
                    "CRITICAL",
                    f"ClusterRoleBinding {name}: system:unauthenticated -> {role_name}",
                )
            elif subject_value == "system:authenticated":
                add(
                    "WARN",
                    f"ClusterRoleBinding {name}: tüm authenticated kullanıcılar -> {role_name}",
                )

    for binding in role_bindings.get("items", []):
        metadata = binding.get("metadata", {})
        namespace = metadata.get("namespace", "default")
        if namespace in excluded:
            continue
        name = metadata.get("name", "bilinmiyor")
        role_name = binding.get("roleRef", {}).get("name", "")
        subjects = binding.get("subjects", []) or []
        if role_name == "cluster-admin":
            add(
                "CRITICAL",
                f"RoleBinding {namespace}/{name}: cluster-admin namespace'e bağlanmış",
            )
        for subject in subjects:
            if subject.get("name") == "system:unauthenticated":
                add(
                    "CRITICAL",
                    f"RoleBinding {namespace}/{name}: system:unauthenticated -> {role_name}",
                )

    dangerous_verbs = {"bind", "escalate", "impersonate"}
    sensitive_resources = {
        "secrets",
        "pods/exec",
        "pods/attach",
        "serviceaccounts/token",
    }

    def audit_role(role: dict, cluster_scoped: bool) -> None:
        metadata = role.get("metadata", {})
        namespace = metadata.get("namespace")
        if namespace in excluded:
            return
        name = metadata.get("name", "bilinmiyor")
        prefix = (
            f"ClusterRole {name}"
            if cluster_scoped
            else f"Role {namespace}/{name}"
        )
        if name.startswith("system:"):
            return
        for index, rule in enumerate(role.get("rules", []) or [], start=1):
            verbs = set(rule.get("verbs", []) or [])
            resources = set(rule.get("resources", []) or [])
            api_groups = set(rule.get("apiGroups", []) or [])
            if "*" in verbs and ("*" in resources or "*" in api_groups):
                add(
                    "CRITICAL" if cluster_scoped else "WARN",
                    f"{prefix} kural {index}: wildcard verb/resource yetkisi",
                )
            elif "*" in verbs:
                add("WARN", f"{prefix} kural {index}: wildcard verb")
            if verbs & dangerous_verbs:
                add(
                    "CRITICAL",
                    f"{prefix} kural {index}: tehlikeli verb "
                    f"{','.join(sorted(verbs & dangerous_verbs))}",
                )
            if resources & sensitive_resources and verbs & {
                "*",
                "create",
                "get",
                "list",
                "update",
                "patch",
            }:
                add(
                    "WARN",
                    f"{prefix} kural {index}: hassas kaynak yetkisi "
                    f"{','.join(sorted(resources & sensitive_resources))}",
                )

    for role in cluster_roles.get("items", []):
        audit_role(role, True)
    for role in roles.get("items", []):
        audit_role(role, False)

    for account in service_accounts.get("items", []):
        metadata = account.get("metadata", {})
        namespace = metadata.get("namespace", "default")
        if namespace in excluded or metadata.get("name") != "default":
            continue
        if account.get("automountServiceAccountToken") is not False:
            add(
                "INFO",
                f"ServiceAccount {namespace}/default: automountServiceAccountToken=false değil",
            )

    print("KUBERNETES RBAC RİSK RAPORU")
    print("=" * 92)
    print(
        "İncelenen: "
        f"{len(cluster_roles.get('items', []))} ClusterRole, "
        f"{len(roles.get('items', []))} Role, "
        f"{len(cluster_bindings.get('items', []))} ClusterRoleBinding, "
        f"{len(role_bindings.get('items', []))} RoleBinding"
    )
    print("-" * 92)
    for level, message in findings:
        print(f"[{level}] {message}")
    if not findings:
        print("[OK] Tanımlı politika kapsamında RBAC riski yok")
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
