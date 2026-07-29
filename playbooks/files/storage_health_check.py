#!/usr/bin/env python3
"""Salt-okunur: disk/inode + container runtime + PV/PVC storage report."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any


def run(cmd: str, timeout: float = 45.0) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", str(e)


def section(title: str) -> list[str]:
    return ["", f"=== {title} ==="]


def collect_df() -> list[str]:
    lines = section("Dosya sistemleri (df -hT)")
    rc, out, err = run(
        "df -hT -x tmpfs -x devtmpfs -x squashfs -x overlay -x efivarfs"
    )
    lines.append(out if rc == 0 else (err or "df başarısız"))
    return lines


def collect_inodes() -> list[str]:
    lines = section("Inode kullanımı (df -i)")
    rc, out, err = run(
        "df -iT -x tmpfs -x devtmpfs -x squashfs -x overlay -x efivarfs"
    )
    lines.append(out if rc == 0 else (err or "df -i başarısız"))
    lines.append(
        "Yorum: IUse% yüksekse (özellikle >80) küçük dosya yağmuru / container layer birikimi şüphesi."
    )
    return lines


def collect_runtime_disk() -> list[str]:
    lines = section("Container runtime disk kullanımı")
    if shutil.which("crictl"):
        rc, out, err = run("crictl info -o json")
        if rc == 0 and out:
            try:
                info = json.loads(out)
                # try common paths
                roots = []
                cfg = info.get("config") or info.get("runtimeConfig") or {}
                for k in ("containerdRootDir", "root", "state", "containerdPath"):
                    if isinstance(cfg, dict) and cfg.get(k):
                        roots.append(str(cfg[k]))
                # fallback paths
                for p in (
                    "/var/lib/containerd",
                    "/var/lib/rancher/k3s/agent/containerd",
                    "/run/k3s/containerd",
                ):
                    if os.path.isdir(p):
                        roots.append(p)
                lines.append("crictl info: OK")
                seen = set()
                for p in roots:
                    if p in seen or not os.path.isdir(p):
                        continue
                    seen.add(p)
                    rc2, du, _ = run(f"du -sh {p} 2>/dev/null")
                    if rc2 == 0 and du:
                        lines.append(f"  {du}")
            except Exception as e:
                lines.append(f"crictl info parse: {e}")
        else:
            lines.append(f"crictl info yok: {err}")
        rc, out, _ = run("crictl images -v 2>/dev/null | tail -5")
        # disk via images summary
        rc2, out2, _ = run(
            "crictl images -o json | python3 -c "
            "\"import sys,json; d=json.load(sys.stdin); "
            "s=sum(int(i.get('size') or 0) for i in d.get('images') or []); "
            "print(f'crictl images toplam boyut: {s/1e9:.2f} GB ({len(d.get(\\\"images\\\") or [])} imaj)')\""
        )
        if rc2 == 0 and out2:
            lines.append(out2)
    else:
        lines.append("crictl yok.")

    if shutil.which("docker"):
        rc, out, _ = run("docker system df")
        if rc == 0 and out:
            lines.append("--- docker system df ---")
            lines.append(out)
    return lines


def collect_pv_pvc() -> list[str]:
    lines = section("Kubernetes PV / PVC")
    rc, _, err = run("kubectl cluster-info")
    if rc != 0:
        lines.append(f"kubectl yok/erişilemez — PV/PVC atlandı ({err or '-'}).")
        return lines

    for kind, title in (
        ("pvc", "PVC"),
        ("pv", "PV"),
        ("sc", "StorageClass"),
    ):
        rc, out, err = run(f"kubectl get {kind} -A -o wide" if kind == "pvc" else f"kubectl get {kind} -o wide")
        lines.append(f"--- {title} ---")
        if rc == 0 and out:
            lines.append(out)
        else:
            lines.append(err or f"{kind} alınamadı")

    # Pending / Lost highlights
    rc, out, _ = run(
        "kubectl get pvc -A --no-headers 2>/dev/null | "
        "awk '$3!=\"Bound\" {print}'"
    )
    lines.append("--- Bound olmayan PVC'ler ---")
    lines.append(out if out else "(yok — hepsi Bound veya PVC yok)")

    rc, out, _ = run(
        "kubectl get pv --no-headers 2>/dev/null | "
        "awk '$5!=\"Bound\" && $5!=\"Available\" {print}'"
    )
    lines.append("--- Sorunlu/Released PV'ler (Bound/Available dışı) ---")
    lines.append(out if out else "(yok veya tümü Bound/Available)")
    return lines


def main() -> None:
    lines: list[str] = []
    lines.append("Depolama / inode / PV raporu (salt-okunur)")
    lines.extend(collect_df())
    lines.extend(collect_inodes())
    lines.extend(collect_runtime_disk())
    lines.extend(collect_pv_pvc())
    lines.append("")
    lines.append(
        "Yorum: Disk doluluğu + yüksek inode + büyük crictl images → 17/18 playbook'ları."
    )
    lines.append("Detay: docs/23_check_storage_health.md")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
