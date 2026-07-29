#!/usr/bin/env python3
"""Salt-okunur: etcd / control-plane health (kubeadm + k3s)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


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


def main() -> None:
    lines: list[str] = []
    lines.append("etcd / control-plane sağlık raporu (salt-okunur)")

    rc, _, err = run("kubectl cluster-info")
    if rc != 0:
        lines.append(f"kubectl erişimi yok: {err}")
        print("\n".join(lines))
        return

    # Component statuses (deprecated but still useful on some clusters)
    lines.extend(section("Control-plane component'ler"))
    for kind in ("deploy -n kube-system", "pods -n kube-system"):
        pass
    rc, out, _ = run(
        "kubectl get pods -n kube-system --no-headers 2>/dev/null | "
        "grep -E 'etcd|kube-apiserver|kube-controller|kube-scheduler|k3s' || true"
    )
    lines.append(out if out else "(eşleşen kube-system control-plane pod'u yok / k3s embedded)")

    # API healthz
    lines.extend(section("API server health"))
    for path in ("/healthz", "/readyz", "/livez"):
        rc, out, err = run(
            f"kubectl get --raw {path} 2>/dev/null || kubectl get --raw '{path}?verbose'"
        )
        if rc == 0:
            summary = out.splitlines()[0] if out else "ok"
            if len(out.splitlines()) > 1:
                # count ok/fail lines for verbose
                fails = [l for l in out.splitlines() if l.endswith(": error") or "failed" in l.lower()]
                lines.append(
                    f"{path}: OK ({len(out.splitlines())} check) "
                    f"{'— sorunlu: ' + str(len(fails)) if fails else ''}"
                )
                for f in fails[:10]:
                    lines.append(f"  {f}")
            else:
                lines.append(f"{path}: {summary}")
        else:
            lines.append(f"{path}: FAIL — {err or out or '-'}")

    # etcd endpoints / pods
    lines.extend(section("etcd"))
    is_k3s = Path("/var/lib/rancher/k3s").is_dir() or shutil.which("k3s")
    if is_k3s:
        lines.append("Dağıtım ipucu: k3s (embedded etcd veya harici).")
        rc, out, _ = run("k3s etcd-snapshot ls 2>/dev/null || true")
        if out:
            lines.append("--- k3s etcd-snapshot ls ---")
            # show last lines
            snap_lines = out.splitlines()
            lines.extend(snap_lines[:5])
            if len(snap_lines) > 8:
                lines.append("...")
                lines.extend(snap_lines[-5:])
            # try parse newest age from listing if present
        else:
            lines.append(
                "k3s etcd-snapshot ls boş/erişilemez — snapshot schedule veya yetki kontrol et."
            )
        # db size if possible
        for p in (
            "/var/lib/rancher/k3s/server/db/etcd",
            "/var/lib/rancher/k3s/server/db",
        ):
            if Path(p).exists():
                rc, du, _ = run(f"du -sh {p} 2>/dev/null")
                if rc == 0 and du:
                    lines.append(f"etcd data dir: {du}")
                break
    else:
        lines.append("Dağıtım ipucu: kubeadm/klasik (veya k3s değil).")
        rc, out, _ = run(
            "kubectl get pods -n kube-system -l component=etcd -o wide --no-headers"
        )
        lines.append(out if out else "etcd pod label component=etcd bulunamadı")

        # etcdctl if available with kubeadm certs
        etcdctl = shutil.which("etcdctl")
        cacert = "/etc/kubernetes/pki/etcd/ca.crt"
        cert = "/etc/kubernetes/pki/etcd/server.crt"
        key = "/etc/kubernetes/pki/etcd/server.key"
        if etcdctl and Path(cacert).is_file():
            env = (
                f"ETCDCTL_API=3 etcdctl --cacert={cacert} --cert={cert} --key={key} "
                f"--endpoints=https://127.0.0.1:2379"
            )
            for sub in (
                "endpoint health",
                "endpoint status -w table",
                "alarm list",
            ):
                rc, out, err = run(f"{env} {sub}")
                lines.append(f"--- etcdctl {sub} ---")
                lines.append(out or err or "-")
            # defrag hint via db size vs in-use if status shows
            rc, out, _ = run(f"{env} endpoint status -w json")
            if rc == 0 and out:
                try:
                    st = json.loads(out)
                    if isinstance(st, list) and st:
                        s0 = st[0].get("Status") or st[0]
                        db = int(s0.get("dbSize") or 0)
                        db_inuse = int(s0.get("dbSizeInUse") or 0)
                        if db and db_inuse:
                            waste = (db - db_inuse) / db * 100
                            lines.append(
                                f"dbSize={db/1e6:.1f}MB dbSizeInUse={db_inuse/1e6:.1f}MB "
                                f"boşalan≈{waste:.0f}%"
                            )
                            if waste >= 40 and db >= 100_000_000:
                                lines.append(
                                    "UYARI: Defrag adayı olabilir (boşalan yüksek + DB büyük). "
                                    "Salt-okunur rapor — defrag ÇALIŞTIRILMADI."
                                )
                except Exception:
                    pass
        else:
            lines.append(
                "etcdctl veya /etc/kubernetes/pki/etcd cert'leri yok — endpoint health atlandı."
            )

        # snapshot age under /etc/kubernetes/ or /var/lib/etcd
        snap_dirs = [
            "/etc/kubernetes/etcd-snapshots",
            "/var/lib/etcd/snapshots",
            "/var/backups/etcd",
        ]
        snaps = []
        for d in snap_dirs:
            p = Path(d)
            if not p.is_dir():
                continue
            for f in p.glob("*"):
                if f.is_file():
                    snaps.append(f)
        if snaps:
            snaps.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            newest = snaps[0]
            age_h = (datetime.now().timestamp() - newest.stat().st_mtime) / 3600
            lines.append(
                f"Son snapshot dosyası: {newest} (yaş≈{age_h:.1f} saat)"
            )
            if age_h > 48:
                lines.append("UYARI: Snapshot 48 saatten eski görünüyor.")
        else:
            lines.append(
                "Yerel snapshot dizini bulunamadı (backup job ayrı makinede olabilir)."
            )

    # scheduler / controller pods (kubeadm); k3s embeds these in the k3s process
    lines.extend(section("Scheduler / controller (kube-system)"))
    rc, out, _ = run(
        "kubectl get pods -n kube-system -o wide --no-headers 2>/dev/null | "
        "grep -E 'kube-scheduler|kube-controller-manager' || true"
    )
    if out:
        lines.append(out)
    elif is_k3s:
        lines.append("(k3s embedded — ayrı scheduler/controller pod'u yok)")
    else:
        lines.append("(listelenemedi)")
    lines.append("")
    lines.append(
        "Yorum: ready/livez FAIL veya etcd alarm/no snapshot → öncelikli incele. "
        "Defrag/restore bu playbook'ta YAPILMAZ."
    )
    lines.append("Detay: docs/25_check_etcd_controlplane.md")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
