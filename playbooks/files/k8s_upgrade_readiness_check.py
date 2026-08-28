#!/usr/bin/env python3
"""Report blockers and warnings before a Kubernetes minor or patch upgrade."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)")
RELEASE_RE = re.compile(r"^v?(\d+)\.(\d+)(?:\.(\d+))?")


def run(command: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def kubectl_json(args: list[str]) -> tuple[dict, str | None]:
    result = run(["kubectl", *args, "-o", "json"])
    if result.returncode != 0:
        return {}, (result.stderr or result.stdout).strip()
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as exc:
        return {}, f"kubectl JSON output unreadable: {exc}"


def version_tuple(value: str) -> tuple[int, int, int] | None:
    match = VERSION_RE.match(value.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def release_tuple(value: str) -> tuple[int, int, int] | None:
    match = RELEASE_RE.match(value.strip())
    if not match:
        return None
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch or 0)


def ready_condition(node: dict) -> tuple[bool, str]:
    for condition in node.get("status", {}).get("conditions", []):
        if condition.get("type") == "Ready":
            return condition.get("status") == "True", condition.get("reason", "unknown")
    return False, "Ready condition missing"


def newest_backup(directory: Path) -> Path | None:
    if not directory.is_dir():
        return None
    files = [path for path in directory.rglob("etcd_snapshot_*") if path.is_file()]
    return max(files, key=lambda path: path.stat().st_mtime) if files else None


def parse_deprecated_metrics(text: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    pattern = re.compile(
        r'^apiserver_requested_deprecated_apis\{([^}]*)\}\s+([0-9.eE+-]+)$'
    )
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        try:
            active = float(match.group(2)) > 0
        except ValueError:
            continue
        if not active:
            continue
        labels = dict(re.findall(r'(\w+)="([^"]*)"', match.group(1)))
        findings.append(labels)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-version", default="")
    parser.add_argument("--backup-dir", default="/var/backups/etcd")
    parser.add_argument("--max-backup-age-hours", type=int, default=24)
    parser.add_argument("--max-disk-percent", type=int, default=85)
    args = parser.parse_args()

    blockers: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    if not shutil.which("kubectl"):
        print("[BLOCKER] kubectl not found")
        return 2

    version_data, error = kubectl_json(["version"])
    if error:
        blockers.append(f"API server version could not be retrieved: {error}")
        server_version = None
    else:
        server_text = version_data.get("serverVersion", {}).get("gitVersion", "")
        server_version = version_tuple(server_text)
        info.append(f"API server: {server_text or 'unknown'}")

    target_version = None
    if args.target_version:
        target_version = version_tuple(args.target_version)
        if target_version is None or not re.fullmatch(
            r"\d+\.\d+\.\d+", args.target_version
        ):
            blockers.append("Target version must be in X.Y.Z format")
        elif server_version:
            if target_version[0] != server_version[0]:
                blockers.append("Major version upgrades are not supported")
            elif target_version[1] < server_version[1]:
                blockers.append("Minor version downgrades are not supported")
            elif target_version[1] > server_version[1] + 1:
                blockers.append("Skipping more than one minor version is not allowed")
            elif (
                target_version[1] == server_version[1]
                and target_version[2] < server_version[2]
            ):
                blockers.append("Patch version cannot be lowered within the same minor")
            else:
                info.append(f"Target version: v{args.target_version}")
    else:
        warnings.append("Target version not provided; target-specific checks were skipped")

    nodes, error = kubectl_json(["get", "nodes"])
    if error:
        blockers.append(f"Node list could not be retrieved: {error}")
    else:
        for node in nodes.get("items", []):
            name = node.get("metadata", {}).get("name", "unknown")
            ready, reason = ready_condition(node)
            kubelet_text = (
                node.get("status", {}).get("nodeInfo", {}).get("kubeletVersion", "")
            )
            kubelet_version = version_tuple(kubelet_text)
            if not ready:
                blockers.append(f"Node is not Ready: {name} ({reason})")
            if node.get("spec", {}).get("unschedulable"):
                warnings.append(f"Node is already cordoned: {name}")
            if server_version and kubelet_version:
                if kubelet_version[:2] > server_version[:2]:
                    blockers.append(
                        f"Kubelet is newer than API server: {name} {kubelet_text}"
                    )
                elif server_version[1] - kubelet_version[1] > 3:
                    blockers.append(
                        f"Kubelet version skew is too large: {name} {kubelet_text}"
                    )
            info.append(f"Node {name}: Ready={ready}, kubelet={kubelet_text}")

    pdbs, error = kubectl_json(["get", "pdb", "--all-namespaces"])
    if error:
        warnings.append(f"PDB list could not be retrieved: {error}")
    else:
        for pdb in pdbs.get("items", []):
            metadata = pdb.get("metadata", {})
            status = pdb.get("status", {})
            if int(status.get("disruptionsAllowed", 0) or 0) == 0:
                blockers.append(
                    "PDB that may block drain: "
                    f"{metadata.get('namespace')}/{metadata.get('name')} "
                    f"(healthy={status.get('currentHealthy', 0)}, "
                    f"desired={status.get('desiredHealthy', 0)})"
                )

    for resource in (
        "validatingwebhookconfigurations",
        "mutatingwebhookconfigurations",
    ):
        webhooks, error = kubectl_json(["get", resource])
        if error:
            warnings.append(f"{resource} could not be retrieved: {error}")
            continue
        for config in webhooks.get("items", []):
            config_name = config.get("metadata", {}).get("name", "unknown")
            for webhook in config.get("webhooks", []):
                if webhook.get("failurePolicy", "Fail") == "Fail":
                    warnings.append(
                        f"failurePolicy=Fail webhook: {config_name}/"
                        f"{webhook.get('name', 'unknown')}"
                    )

    metrics = run(["kubectl", "get", "--raw=/metrics"])
    if metrics.returncode == 0:
        deprecated = parse_deprecated_metrics(metrics.stdout)
        for item in deprecated:
            removed = item.get("removed_release", "unknown")
            resource = "/".join(
                filter(
                    None,
                    [
                        item.get("group"),
                        item.get("version"),
                        item.get("resource"),
                    ],
                )
            )
            message = f"Deprecated API call: {resource} (removal: {removed})"
            removed_version = release_tuple(removed)
            if target_version and removed_version and removed_version <= target_version:
                blockers.append(message)
            else:
                warnings.append(message)
    else:
        warnings.append("API server /metrics unreadable; deprecated API check is incomplete")

    backup = newest_backup(Path(args.backup_dir))
    if backup is None:
        blockers.append(f"etcd snapshot not found: {args.backup_dir}")
    else:
        age = (time.time() - backup.stat().st_mtime) / 3600
        info.append(f"Latest etcd backup: {backup.name}, {age:.1f} hours")
        if age > args.max_backup_age_hours:
            blockers.append(
                f"Latest etcd backup is stale: {age:.1f} hours "
                f"(threshold {args.max_backup_age_hours})"
            )

    for disk_path in ("/var/lib/etcd", "/var/lib/rancher/k3s", "/"):
        path = Path(disk_path)
        if not path.exists():
            continue
        usage = shutil.disk_usage(path)
        percent = usage.used * 100 / usage.total if usage.total else 0
        info.append(f"Disk {disk_path}: {percent:.1f}% used")
        if percent >= 95:
            blockers.append(f"Disk is critically full: {disk_path} {percent:.1f}%")
        elif percent >= args.max_disk_percent:
            warnings.append(f"Disk usage exceeded threshold: {disk_path} {percent:.1f}%")
        break

    print("KUBERNETES UPGRADE READINESS REPORT")
    print("=" * 80)
    for line in info:
        print(f"[INFO] {line}")
    for line in warnings:
        print(f"[WARN] {line}")
    for line in blockers:
        print(f"[BLOCKER] {line}")
    print("-" * 80)
    print(
        f"Summary: {len(blockers)} blocker(s), {len(warnings)} warning(s), "
        f"{len(info)} info"
    )
    return 2 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
