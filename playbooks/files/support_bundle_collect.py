#!/usr/bin/env python3
"""Create a redacted Kubernetes and host support bundle without collecting Secrets."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import time


COMMANDS: list[tuple[str, list[str]]] = [
    ("cluster-info.txt", ["kubectl", "cluster-info"]),
    ("version.txt", ["kubectl", "version", "--output=yaml"]),
    ("nodes.txt", ["kubectl", "get", "nodes", "-o", "wide"]),
    ("pods.txt", ["kubectl", "get", "pods", "--all-namespaces", "-o", "wide"]),
    (
        "workloads.txt",
        [
            "kubectl",
            "get",
            "deployments,statefulsets,daemonsets",
            "--all-namespaces",
            "-o",
            "wide",
        ],
    ),
    ("services.txt", ["kubectl", "get", "services", "--all-namespaces", "-o", "wide"]),
    (
        "endpointslices.txt",
        ["kubectl", "get", "endpointslices", "--all-namespaces"],
    ),
    ("events.txt", ["kubectl", "get", "events", "--all-namespaces", "--sort-by=.lastTimestamp"]),
    ("storage.txt", ["kubectl", "get", "pv,pvc", "--all-namespaces", "-o", "wide"]),
    ("pdb.txt", ["kubectl", "get", "pdb", "--all-namespaces"]),
    (
        "networkpolicies.txt",
        ["kubectl", "get", "networkpolicies", "--all-namespaces"],
    ),
    ("apiservices.txt", ["kubectl", "get", "apiservices"]),
    ("csrs.txt", ["kubectl", "get", "certificatesigningrequests"]),
    ("uname.txt", ["uname", "-a"]),
    ("uptime.txt", ["uptime"]),
    ("disk.txt", ["df", "-hT"]),
    ("memory.txt", ["free", "-h"]),
    ("failed-services.txt", ["systemctl", "--failed", "--no-pager"]),
    (
        "journal-warnings.txt",
        ["journalctl", "-p", "warning", "-n", "500", "--no-pager"],
    ),
]


def bool_arg(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def redact(text: str) -> str:
    text = re.sub(
        r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])",
        "<REDACTED_IP>",
        text,
    )

    def redact_ipv6(match: re.Match[str]) -> str:
        candidate = match.group(0)
        try:
            address = ipaddress.ip_address(candidate)
        except ValueError:
            return candidate
        return "<REDACTED_IP>" if address.version == 6 else candidate

    text = re.sub(
        r"(?<![0-9A-Fa-f:])[0-9A-Fa-f:]*:[0-9A-Fa-f:]+(?![0-9A-Fa-f:])",
        redact_ipv6,
        text,
    )
    text = re.sub(
        r"(?i)(authorization:\s*bearer\s+)[A-Za-z0-9._~+/=-]+",
        r"\1<REDACTED_TOKEN>",
        text,
    )
    text = re.sub(
        r"(?i)((?:password|passwd|token|secret)\s*[=:]\s*)\S+",
        r"\1<REDACTED>",
        text,
    )
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "<REDACTED_EMAIL>",
        text,
    )
    return text


def run_command(command: list[str]) -> tuple[int, str, float]:
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        output = result.stdout
        if result.stderr:
            output += "\n--- STDERR ---\n" + result.stderr
        return result.returncode, output, time.monotonic() - started
    except FileNotFoundError:
        return 127, f"Komut bulunamadı: {command[0]}\n", time.monotonic() - started
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + "\nKomut 120 saniyede zaman aşımına uğradı.\n"
        return 124, output, time.monotonic() - started


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--redact", type=bool_arg, default=True)
    args = parser.parse_args()

    output = Path(args.output).expanduser().resolve()
    allowed_parents = (Path("/tmp").resolve(), Path("/var/tmp").resolve())
    if output.parent not in allowed_parents or output.suffixes[-2:] != [".tar", ".gz"]:
        print("[ERROR] Output /tmp veya /var/tmp altında .tar.gz olmalıdır")
        return 2

    metadata: dict[str, object] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "redacted": args.redact,
        "hostname": os.uname().nodename,
        "commands": [],
        "excluded_resources": ["Secret içerikleri", "ConfigMap içerikleri"],
    }

    with tempfile.TemporaryDirectory(prefix="ansible-support-") as temp_name:
        workspace = Path(temp_name)
        for filename, command in COMMANDS:
            rc, command_output, duration = run_command(command)
            if args.redact:
                command_output = redact(command_output)
            report = (
                f"$ {' '.join(command)}\n"
                f"return_code={rc} duration_seconds={duration:.2f}\n\n"
                f"{command_output}"
            )
            (workspace / filename).write_text(report, errors="replace")
            metadata["commands"].append(
                {
                    "file": filename,
                    "command": command,
                    "return_code": rc,
                    "duration_seconds": round(duration, 2),
                }
            )

        (workspace / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2)
        )
        (workspace / "README.txt").write_text(
            "Bu arşiv Kubernetes Secret/ConfigMap içeriklerini toplamaz.\n"
            "Redaksiyon sezgiseldir; üçüncü tarafla paylaşmadan önce manuel inceleyin.\n"
        )

        output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with tarfile.open(output, "w:gz") as archive:
            for path in sorted(workspace.iterdir()):
                archive.add(path, arcname=path.name, recursive=False)
        output.chmod(0o600)

    print("SUPPORT BUNDLE TAMAMLANDI")
    print(f"Arşiv: {output}")
    print(f"Boyut: {output.stat().st_size} byte")
    print(f"Redaksiyon: {'açık' if args.redact else 'kapalı'}")
    print("Secret ve ConfigMap içerikleri toplanmadı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
