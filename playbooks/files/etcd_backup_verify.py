#!/usr/bin/env python3
"""Validate the newest etcd snapshot and optionally perform an isolated restore."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile


def bool_arg(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def run(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
        check=False,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def human_size(size: int) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def newest_snapshot(directory: Path) -> Path:
    candidates = [
        path
        for path in directory.rglob("etcd_snapshot_*")
        if path.is_file() and not path.name.endswith(".part")
    ]
    if not candidates:
        raise FileNotFoundError(f"no etcd_snapshot_* found under {directory}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def extract_if_needed(snapshot: Path, workspace: Path) -> tuple[Path, str]:
    if zipfile.is_zipfile(snapshot):
        with zipfile.ZipFile(snapshot) as archive:
            members = [
                member
                for member in archive.infolist()
                if not member.is_dir() and member.file_size > 0
            ]
            if not members:
                raise RuntimeError("ZIP snapshot contains no verifiable file")
            member = max(members, key=lambda item: item.file_size)
            extracted = workspace / "snapshot.db"
            with archive.open(member) as source, extracted.open("wb") as target:
                shutil.copyfileobj(source, target)
            return extracted, f"ZIP contents: {member.filename}"

    if tarfile.is_tarfile(snapshot):
        with tarfile.open(snapshot) as archive:
            members = [
                member
                for member in archive.getmembers()
                if member.isfile() and member.size > 0
            ]
            if not members:
                raise RuntimeError("TAR snapshot contains no verifiable file")
            member = max(members, key=lambda item: item.size)
            extracted = workspace / "snapshot.db"
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError("Could not open snapshot archive")
            with source, extracted.open("wb") as target:
                shutil.copyfileobj(source, target)
            return extracted, f"TAR contents: {member.name}"

    return snapshot, "Uncompressed snapshot"


def snapshot_tool() -> str | None:
    return shutil.which("etcdutl") or shutil.which("etcdctl")


def status_snapshot(tool: str, snapshot: Path) -> tuple[bool, str]:
    env = os.environ.copy()
    env["ETCDCTL_API"] = "3"
    result = run([tool, "snapshot", "status", str(snapshot), "--write-out=json"], env)
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()

    raw = result.stdout.strip()
    try:
        data = json.loads(raw)
        if isinstance(data, list) and data:
            data = data[0]
        if isinstance(data, dict):
            details = ", ".join(f"{key}={value}" for key, value in sorted(data.items()))
            return True, details
    except json.JSONDecodeError:
        pass
    return True, raw


def restore_snapshot(tool: str, snapshot: Path, workspace: Path) -> tuple[bool, str]:
    restore_dir = workspace / "restore-data"
    env = os.environ.copy()
    env["ETCDCTL_API"] = "3"
    result = run(
        [tool, "snapshot", "restore", str(snapshot), "--data-dir", str(restore_dir)],
        env,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode != 0:
        return False, output[-1000:]
    if not restore_dir.exists() or not any(restore_dir.rglob("*")):
        return False, "Restore command succeeded but data-dir is empty"
    return True, output[-1000:] or "Isolated restore completed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup-dir", default="/var/backups/etcd")
    parser.add_argument("--max-age-hours", type=int, default=24)
    parser.add_argument("--restore-test", type=bool_arg, default=False)
    args = parser.parse_args()

    problems: list[str] = []
    warnings: list[str] = []
    directory = Path(args.backup_dir).expanduser().resolve()

    if not directory.is_dir():
        print(f"[CRITICAL] Backup directory not found: {directory}")
        return 2

    try:
        snapshot = newest_snapshot(directory)
    except FileNotFoundError as exc:
        print(f"[CRITICAL] {exc}")
        return 2

    snapshot_stat = snapshot.stat()
    age_hours = (time.time() - snapshot_stat.st_mtime) / 3600
    file_mode = stat.S_IMODE(snapshot_stat.st_mode)
    dir_mode = stat.S_IMODE(directory.stat().st_mode)

    print("ETCD BACKUP VERIFICATION REPORT")
    print("=" * 72)
    print(f"Snapshot      : {snapshot}")
    print(f"Size          : {human_size(snapshot_stat.st_size)}")
    print(f"Age           : {age_hours:.1f} hours")
    print(f"SHA256        : {sha256_file(snapshot)}")
    print(f"File mode     : {file_mode:04o}")
    print(f"Dir mode      : {dir_mode:04o}")

    if age_hours > args.max_age_hours:
        problems.append(
            f"Snapshot is {age_hours:.1f} hours old; threshold {args.max_age_hours} hours"
        )
    if file_mode & 0o077:
        problems.append(f"Snapshot is group/other-readable: {file_mode:04o}")
    if dir_mode & 0o077:
        problems.append(f"Backup directory is group/other-accessible: {dir_mode:04o}")

    tool = snapshot_tool()
    if not tool:
        problems.append("etcdutl or etcdctl not found; snapshot integrity was not verified")
    else:
        with tempfile.TemporaryDirectory(prefix="etcd-verify-") as temp_name:
            workspace = Path(temp_name)
            try:
                candidate, archive_note = extract_if_needed(snapshot, workspace)
                print(f"Format         : {archive_note}")
                ok, detail = status_snapshot(tool, candidate)
                print(f"Status tool    : {tool}")
                print(f"Status result  : {'PASSED' if ok else 'FAILED'}")
                if detail:
                    print(f"Status detail  : {detail}")
                if not ok:
                    problems.append("Snapshot status check failed")

                if args.restore_test:
                    restored, restore_detail = restore_snapshot(tool, candidate, workspace)
                    print(f"Restore test   : {'PASSED' if restored else 'FAILED'}")
                    if restore_detail:
                        print(f"Restore detail : {restore_detail}")
                    if not restored:
                        problems.append("Isolated restore test failed")
                else:
                    warnings.append(
                        "Isolated restore test is off; enable with etcd_backup_restore_test=true"
                    )
            except (OSError, RuntimeError, zipfile.BadZipFile, tarfile.TarError) as exc:
                problems.append(f"Snapshot could not be prepared: {exc}")

    print("\nRESULT")
    print("-" * 72)
    for warning in warnings:
        print(f"[WARN] {warning}")
    for problem in problems:
        print(f"[CRITICAL] {problem}")
    if problems:
        print(f"Status: FAILED ({len(problems)} critical finding(s))")
        return 2
    print("Status: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
