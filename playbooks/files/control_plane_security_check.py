#!/usr/bin/env python3
"""Inspect kubeadm and k3s control-plane security settings without exposing keys."""

from __future__ import annotations

import os
from pathlib import Path
import re
import stat
import subprocess
import sys


RELEVANT_FLAGS = {
    "anonymous-auth",
    "authentication-config",
    "authorization-mode",
    "authorization-config",
    "insecure-port",
    "secure-port",
    "audit-policy-file",
    "audit-log-path",
    "audit-webhook-config-file",
    "encryption-provider-config",
    "enable-admission-plugins",
    "disable-admission-plugins",
    "profiling",
    "tls-min-version",
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except OSError:
        return ""


def command_output(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout if result.returncode == 0 else ""


def extract_flags(text: str) -> dict[str, str]:
    flags: dict[str, str] = {}
    pattern = re.compile(r"--([a-z0-9-]+)(?:[=\s]+([^\s\"']+))?")
    for name, value in pattern.findall(text):
        if name in RELEVANT_FLAGS:
            flags[name] = value or "true"

    for name in RELEVANT_FLAGS:
        config_pattern = re.compile(
            rf"(?:^|[\s\"']){re.escape(name)}[=:]\s*[\"']?([^,\s\"']+)",
            re.MULTILINE,
        )
        match = config_pattern.search(text)
        if match and name not in flags:
            flags[name] = match.group(1)
    return flags


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    lowered = value.lower()
    if lowered in {"true", "yes", "1", "on"}:
        return True
    if lowered in {"false", "no", "0", "off"}:
        return False
    return None


def mode(path: Path) -> int | None:
    try:
        return stat.S_IMODE(path.stat().st_mode)
    except OSError:
        return None


def encryption_provider_summary(path: Path) -> tuple[bool, str]:
    text = read_text(path)
    if not text:
        return False, "encryption provider file unreadable"
    providers = re.findall(r"^\s*-\s+(aescbc|aesgcm|secretbox|kms|identity)\s*:", text, re.MULTILINE)
    if not providers:
        return False, "encryption provider list not found"
    if providers[0] == "identity":
        return False, "identity is the first provider; new data may not be encrypted"
    strong = {"aescbc", "aesgcm", "secretbox", "kms"}
    if not any(provider in strong for provider in providers):
        return False, "encryption provider not found"
    return True, "provider order: " + " -> ".join(providers)


def main() -> int:
    critical: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    kubeadm_manifest = Path("/etc/kubernetes/manifests/kube-apiserver.yaml")
    k3s_config = Path("/etc/rancher/k3s/config.yaml")
    sources: list[tuple[str, str]] = []
    if kubeadm_manifest.is_file():
        sources.append(("kubeadm manifest", read_text(kubeadm_manifest)))
    if k3s_config.is_file():
        sources.append(("k3s config", read_text(k3s_config)))

    process_text = command_output(["ps", "-eo", "args"])
    process_lines = "\n".join(
        line
        for line in process_text.splitlines()
        if "kube-apiserver" in line or "k3s server" in line
    )
    if process_lines:
        sources.append(("running process", process_lines))

    combined = "\n".join(text for _, text in sources)
    flags = extract_flags(combined)
    is_k3s = k3s_config.is_file() or "k3s server" in process_lines

    print("KUBERNETES CONTROL-PLANE SECURITY REPORT")
    print("=" * 88)
    print("Detected sources: " + (", ".join(name for name, _ in sources) or "none"))
    print(f"Distribution type: {'k3s' if is_k3s else 'kubeadm/standard'}")

    if not sources:
        critical.append("kube-apiserver or k3s configuration not found")

    anonymous = parse_bool(flags.get("anonymous-auth"))
    if anonymous is True:
        warnings.append("anonymous-auth=true")
    elif anonymous is False:
        info.append("anonymous-auth=false")
    elif "authentication-config" in flags:
        info.append("Anonymous access is managed via structured authentication config")
    else:
        warnings.append("anonymous-auth is not explicitly disabled")

    authorization = flags.get("authorization-mode", "")
    if "AlwaysAllow" in authorization:
        critical.append("AlwaysAllow is present in authorization-mode")
    elif authorization:
        modes = {item.strip() for item in authorization.split(",")}
        if not {"Node", "RBAC"}.issubset(modes):
            warnings.append(f"authorization-mode is not the expected Node,RBAC: {authorization}")
        else:
            info.append(f"authorization-mode={authorization}")
    elif "authorization-config" in flags:
        info.append("Structured authorization config is in use")
    else:
        warnings.append("authorization-mode/config could not be detected explicitly")

    insecure_port = flags.get("insecure-port")
    if insecure_port and insecure_port != "0":
        critical.append(f"insecure-port={insecure_port}")

    if parse_bool(flags.get("profiling")) is not False:
        warnings.append("kube-apiserver profiling is enabled or not explicitly disabled")
    else:
        info.append("profiling=false")

    audit_enabled = any(
        key in flags
        for key in ("audit-policy-file", "audit-log-path", "audit-webhook-config-file")
    )
    if audit_enabled:
        info.append("API audit configuration detected")
    else:
        warnings.append("API audit policy/backend not detected")

    encryption_path_value = flags.get("encryption-provider-config")
    k3s_secrets_encryption = bool(
        re.search(r"^\s*secrets-encryption\s*:\s*true\s*$", combined, re.MULTILINE)
        or "--secrets-encryption" in combined
    )
    if encryption_path_value:
        encryption_path = Path(encryption_path_value)
        ok, summary = encryption_provider_summary(encryption_path)
        if ok:
            info.append(f"Encryption at rest: {summary}")
        else:
            critical.append(summary)
    elif k3s_secrets_encryption:
        info.append("k3s secrets-encryption is enabled")
    else:
        warnings.append("Kubernetes Secret encryption-at-rest not detected")

    enabled_admission = flags.get("enable-admission-plugins", "")
    disabled_admission = flags.get("disable-admission-plugins", "")
    if "NodeRestriction" in disabled_admission:
        critical.append("NodeRestriction admission plugin is disabled")
    elif enabled_admission and "NodeRestriction" not in enabled_admission:
        warnings.append("NodeRestriction is not listed in enable-admission-plugins")
    elif "NodeRestriction" in enabled_admission:
        info.append("NodeRestriction admission plugin is enabled")

    tls_min = flags.get("tls-min-version")
    if tls_min:
        info.append(f"tls-min-version={tls_min}")
    else:
        warnings.append("tls-min-version is not explicitly pinned")

    sensitive_files = [
        Path("/etc/kubernetes/admin.conf"),
        Path("/etc/kubernetes/super-admin.conf"),
        Path("/etc/rancher/k3s/k3s.yaml"),
    ]
    for path in sensitive_files:
        file_mode = mode(path)
        if file_mode is None:
            continue
        if file_mode & 0o077:
            critical.append(f"{path} permissions are too open: {file_mode:04o}")
        else:
            info.append(f"{path} permissions: {file_mode:04o}")

    for pki_root in (
        Path("/etc/kubernetes/pki"),
        Path("/var/lib/rancher/k3s/server/tls"),
    ):
        if not pki_root.is_dir():
            continue
        exposed_keys = []
        for key_path in pki_root.rglob("*.key"):
            key_mode = mode(key_path)
            if key_mode is not None and key_mode & 0o077:
                exposed_keys.append(f"{key_path}:{key_mode:04o}")
        if exposed_keys:
            critical.append(
                f"{pki_root} has overly permissive private key(s): "
                + ", ".join(exposed_keys[:10])
            )
        else:
            info.append(f"{pki_root} private key permissions are appropriate")

    print("-" * 88)
    for line in info:
        print(f"[INFO] {line}")
    for line in warnings:
        print(f"[WARN] {line}")
    for line in critical:
        print(f"[CRITICAL] {line}")
    print("-" * 88)
    print(
        f"Summary: {len(critical)} critical, {len(warnings)} warning(s), "
        f"{len(info)} info"
    )
    return 2 if critical else 0


if __name__ == "__main__":
    sys.exit(main())
