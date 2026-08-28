#!/usr/bin/env python3
"""Collect a normalized Linux/Kubernetes node baseline as JSON."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys


def run(command: list[str]) -> str:
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
    return result.stdout.strip() if result.returncode == 0 else ""


def file_hash(path: Path) -> str:
    if not path.is_file():
        return "missing"
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return "unreadable"
    return digest.hexdigest()[:16]


def read_value(path: Path) -> str:
    try:
        return path.read_text(errors="replace").strip()
    except OSError:
        return "unreadable"


def os_release() -> dict[str, str]:
    values: dict[str, str] = {}
    text = read_value(Path("/etc/os-release"))
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"')
    return values


def active_time_service() -> str:
    services = ("chronyd", "chrony", "systemd-timesyncd", "ntpd")
    active = [
        service
        for service in services
        if run(["systemctl", "is-active", service]) == "active"
    ]
    return ",".join(active) if active else "none"


def find_containerd_config() -> Path | None:
    candidates = (
        Path("/etc/containerd/config.toml"),
        Path("/var/lib/rancher/k3s/agent/etc/containerd/config.toml"),
        Path("/var/lib/rancher/k3s/agent/etc/containerd/config-v3.toml"),
    )
    return next((path for path in candidates if path.is_file()), None)


def main() -> int:
    release = os_release()
    modules = read_value(Path("/proc/modules"))
    swaps = read_value(Path("/proc/swaps")).splitlines()
    containerd_config = find_containerd_config()
    containerd_text = read_value(containerd_config) if containerd_config else ""
    kubelet_config = Path("/var/lib/kubelet/config.yaml")
    kubelet_text = read_value(kubelet_config)
    cgroup_match = re.search(r"^\s*cgroupDriver:\s*(\S+)", kubelet_text, re.MULTILINE)

    data = {
        "hostname": platform.node(),
        "os_id": release.get("ID", "unknown"),
        "os_version": release.get("VERSION_ID", "unknown"),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "cgroup_version": (
            "v2" if Path("/sys/fs/cgroup/cgroup.controllers").exists() else "v1"
        ),
        "swap_enabled": len(swaps) > 1,
        "ip_forward": read_value(Path("/proc/sys/net/ipv4/ip_forward")),
        "bridge_nf_iptables": read_value(
            Path("/proc/sys/net/bridge/bridge-nf-call-iptables")
        ),
        "br_netfilter_loaded": "br_netfilter " in modules,
        "overlay_loaded": "overlay " in modules,
        "containerd_version": run(["containerd", "--version"]) or "missing",
        "containerd_config_sha256": (
            file_hash(containerd_config) if containerd_config else "missing"
        ),
        "containerd_systemd_cgroup": bool(
            re.search(r"SystemdCgroup\s*=\s*true", containerd_text)
        ),
        "kubelet_version": run(["kubelet", "--version"]) or "missing",
        "kubelet_config_sha256": file_hash(kubelet_config),
        "kubelet_cgroup_driver": (
            cgroup_match.group(1) if cgroup_match else "unknown"
        ),
        "time_sync_service": active_time_service(),
        "reboot_required": Path("/var/run/reboot-required").exists(),
        "root_disk_percent": round(
            shutil.disk_usage("/").used * 100 / shutil.disk_usage("/").total, 1
        ),
    }
    print(json.dumps(data, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
