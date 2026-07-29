#!/usr/bin/env python3
"""Host container image inventory / unused prune: docker and/or crictl."""
import argparse
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone


def run(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def fmt_ts(val):
    if val is None or val == "" or val == "-":
        return "-"
    if isinstance(val, (int, float)):
        ts = float(val)
        if ts > 1e12:
            ts = ts / 1e9
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            )
        except Exception:
            return str(val)
    s = str(val).strip()
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    except Exception:
        return s


def fmt_size(n):
    try:
        n = float(n)
    except Exception:
        return str(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(n)}B"
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return str(n)


def short_id(iid):
    s = (iid or "").replace("sha256:", "")
    return s[:12] if s else "-"


def collect_docker():
    """Return (lines_header_rows_summary, unused_delete_refs)."""
    lines = []
    unused_refs = []  # docker rmi targets (image id)

    lines.append("=== Docker ===")
    rc, out, _err = run("docker images --format '{{json .}}'")
    imgs = []
    if rc == 0 and out.strip():
        for line in out.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                imgs.append(json.loads(line))
            except Exception:
                pass

    used_ids = set()
    used_names = set()
    rc2, ps_out, _ = run(
        "docker ps -a --format '{{.ID}}\\t{{.Image}}\\t{{.ImageID}}'"
    )
    if rc2 == 0 and ps_out.strip():
        for line in ps_out.splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            img = parts[1].strip()
            image_id = parts[2].strip() if len(parts) > 2 else ""
            if img:
                used_names.add(img)
            if image_id:
                used_ids.add(image_id)
                used_ids.add(image_id.replace("sha256:", ""))
                used_ids.add(short_id(image_id))

    for name in list(used_names):
        r4, iid, _ = run(
            "docker image inspect --format '{{.Id}}' " + json.dumps(name)
        )
        if r4 == 0 and iid.strip():
            raw = iid.strip()
            used_ids.add(raw)
            used_ids.add(raw.replace("sha256:", ""))
            used_ids.add(short_id(raw))

    lines.append(f"{'IN_USE':<6}  {'CREATED_AT/AGE':<24}  {'SIZE':<10}  IMAGE")
    lines.append("-" * 100)
    in_use_n = unused_n = 0
    rows = []
    for im in imgs:
        repo = im.get("Repository") or "<none>"
        tag = im.get("Tag") or "<none>"
        name = f"{repo}:{tag}"
        iid_raw = im.get("ID") or ""
        iid = iid_raw.replace("sha256:", "")
        created = im.get("CreatedAt") or im.get("CreatedSince") or "-"
        size = im.get("Size") or "-"
        in_use = False
        if name in used_names or repo in used_names:
            in_use = True
        for u in used_names:
            if u.startswith(repo + ":") or u == repo or (iid and u.startswith(iid)):
                in_use = True
        for u in used_ids:
            us = u.replace("sha256:", "")
            if iid and (iid.startswith(us[:12]) or us.startswith(iid[:12])):
                in_use = True
                break
        if in_use:
            in_use_n += 1
        else:
            unused_n += 1
            # Prefer full id for rmi
            delete_ref = iid_raw if iid_raw else iid
            if not delete_ref.startswith("sha256:") and iid:
                delete_ref = "sha256:" + iid if len(iid) > 12 else iid
            unused_refs.append(
                {"ref": delete_ref or name, "label": name, "size": size}
            )
        rows.append((in_use, created, size, name, short_id(iid)))
    rows.sort(key=lambda r: (not r[0], str(r[1])))
    for in_use, created, size, name, sid in rows:
        flag = "yes" if in_use else "no"
        lines.append(
            f"{flag:<6}  {str(created)[:24]:<24}  {str(size):<10}  {name}  ({sid})"
        )
    lines.append(
        f"Özet: toplam={len(rows)} kullanımda={in_use_n} kullanılmıyor={unused_n}"
    )
    lines.append("")
    return lines, unused_refs


def collect_crictl():
    lines = []
    unused_refs = []

    lines.append("=== containerd / crictl (K8s) ===")
    rc, img_out, _ = run("crictl images -o json")
    rc2, ps_out, _ = run("crictl ps -a -o json")
    images = []
    if rc == 0 and img_out.strip():
        try:
            images = json.loads(img_out).get("images") or []
        except Exception as e:
            lines.append(f"crictl images parse hatası: {e}")

    used_refs = set()
    used_ids = set()
    if rc2 == 0 and ps_out.strip():
        try:
            for c in json.loads(ps_out).get("containers") or []:
                ref = c.get("imageRef") or ""
                img = c.get("image")
                if isinstance(img, dict):
                    val = img.get("image")
                    if val:
                        used_refs.add(val)
                elif isinstance(img, str) and img:
                    used_refs.add(img)
                if ref:
                    used_refs.add(ref)
                    used_ids.add(ref.replace("sha256:", ""))
                    used_ids.add(short_id(ref))
        except Exception as e:
            lines.append(f"crictl ps parse hatası: {e}")

    age_by_digest = {}
    if shutil.which("ctr"):
        for ns in ("k8s.io", "default"):
            r_ctr, ctr_out, _ = run(f"ctr -n {ns} content ls")
            if r_ctr != 0 or not ctr_out.strip():
                continue
            for line in ctr_out.splitlines()[1:]:
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                digest = parts[0].strip()
                age = parts[2].strip()
                if digest.startswith("sha256:"):
                    age_by_digest[digest] = age
                    age_by_digest[digest.replace("sha256:", "")] = age

    lines.append(f"{'IN_USE':<6}  {'CREATED_AT/AGE':<24}  {'SIZE':<10}  IMAGE")
    lines.append("-" * 100)
    in_use_n = unused_n = 0
    rows = []
    for im in images:
        iid = (im.get("id") or "").replace("sha256:", "")
        tags = im.get("repoTags") or []
        digests = im.get("repoDigests") or []
        if tags:
            names = tags
        elif digests:
            names = digests
        else:
            names = [f"<untagged>@{short_id(iid)}"]
        size = fmt_size(im.get("size") or 0)
        created = "-"
        for dig in digests:
            if "@sha256:" in dig:
                d = "sha256:" + dig.split("@sha256:")[-1]
                if d in age_by_digest:
                    created = age_by_digest[d]
                    break
            if dig in age_by_digest:
                created = age_by_digest[dig]
                break
        if created == "-" and iid:
            for key in (f"sha256:{iid}", iid):
                if key in age_by_digest:
                    created = age_by_digest[key]
                    break
        if created == "-" and iid:
            for candidate in (f"sha256:{iid}", iid):
                r5, insp, _ = run(f"crictl inspecti -o json {candidate}")
                if r5 == 0 and insp.strip():
                    try:
                        st = json.loads(insp)
                        status = st.get("status") or st
                        created_raw = status.get("createdAt") or status.get("created")
                        created = fmt_ts(created_raw) if created_raw else "-"
                    except Exception:
                        created = "-"
                    break
        in_use = False
        for n in names:
            if n in used_refs:
                in_use = True
        for u in used_ids:
            us = u.replace("sha256:", "")
            if iid and (iid.startswith(us[:12]) or us.startswith(iid[:12])):
                in_use = True
                break
        if in_use:
            in_use_n += 1
        else:
            unused_n += 1
            delete_ref = f"sha256:{iid}" if iid else (names[0] if names else "")
            unused_refs.append(
                {
                    "ref": delete_ref,
                    "label": ", ".join(names),
                    "size": size,
                }
            )
        rows.append((in_use, created, size, ", ".join(names), short_id(iid)))

    rows.sort(key=lambda r: (not r[0], str(r[1])))
    for in_use, created, size, name, sid in rows:
        flag = "yes" if in_use else "no"
        lines.append(
            f"{flag:<6}  {str(created)[:24]:<24}  {str(size):<10}  {name}  ({sid})"
        )
    lines.append(
        f"Özet: toplam={len(rows)} kullanımda={in_use_n} kullanılmıyor={unused_n}"
    )
    lines.append("")
    lines.append(
        "Yorum: IN_USE=yes → bu host'ta container (çalışan veya durmuş) bu imajı kullanıyor."
    )
    lines.append(
        "       IN_USE=no → prune adayı (başka node sonra pull edebilir; dikkatli silin)."
    )
    lines.append(
        "       CREATED_AT/AGE → Docker'da mutlak tarih; containerd'de genelde content AGE."
    )
    return lines, unused_refs


def prune_docker(unused_refs):
    lines = ["=== Docker prune ==="]
    if not unused_refs:
        lines.append("Silinecek kullanılmayan Docker imajı yok.")
        return lines
    ok = fail = 0
    # Deduplicate by ref
    seen = set()
    for item in unused_refs:
        ref = item["ref"]
        if not ref or ref in seen:
            continue
        seen.add(ref)
        rc, out, err = run("docker rmi " + json.dumps(ref))
        # also try without quotes via plain if needed
        if rc != 0:
            rc, out, err = run("docker rmi " + ref)
        if rc == 0:
            ok += 1
            lines.append(f"SİLİNDİ: {item['label']} ({ref}) size={item['size']}")
        else:
            fail += 1
            msg = (err or out or "").strip().splitlines()
            msg = msg[-1] if msg else "bilinmeyen hata"
            lines.append(f"HATA: {item['label']} ({ref}) → {msg}")
    lines.append(f"Docker prune özeti: silinen={ok} hata={fail}")
    lines.append("")
    return lines


def prune_crictl(unused_refs, retries=3, delay_sec=2):
    lines = ["=== crictl/containerd prune ==="]
    if not unused_refs:
        lines.append("Silinecek kullanılmayan crictl imajı yok.")
        return lines
    ok = fail = 0
    seen = set()
    for item in unused_refs:
        ref = item["ref"]
        if not ref or ref in seen:
            continue
        seen.add(ref)
        last_msg = ""
        deleted = False
        for attempt in range(1, retries + 1):
            rc, out, err = run("crictl rmi " + ref)
            if rc == 0:
                ok += 1
                deleted = True
                extra = f" (deneme {attempt})" if attempt > 1 else ""
                lines.append(
                    f"SİLİNDİ{extra}: {item['label']} ({ref}) size={item['size']}"
                )
                break
            last_msg = (err or out or "").strip().splitlines()
            last_msg = last_msg[-1] if last_msg else "bilinmeyen hata"
            transient = any(
                x in last_msg
                for x in (
                    "DeadlineExceeded",
                    "context deadline exceeded",
                    "RST_STREAM",
                    "CANCEL",
                    "Unavailable",
                    "connection refused",
                )
            )
            if transient and attempt < retries:
                time.sleep(delay_sec * attempt)
                continue
            break
        if not deleted:
            fail += 1
            lines.append(f"HATA: {item['label']} ({ref}) → {last_msg}")
    lines.append(f"crictl prune özeti: silinen={ok} hata={fail}")
    lines.append("")
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("report", "unused", "prune"),
        default="report",
        help="report=tam envanter, unused=sadece adaylar, prune=sil",
    )
    args = parser.parse_args()

    lines = []
    any_rt = False
    docker_unused = []
    crictl_unused = []

    if shutil.which("docker"):
        any_rt = True
        d_lines, docker_unused = collect_docker()
        if args.mode == "report":
            lines.extend(d_lines)
        elif args.mode in ("unused", "prune"):
            lines.append("=== Docker — kullanılmayan (IN_USE=no) ===")
            if not docker_unused:
                lines.append("(yok)")
            else:
                for u in docker_unused:
                    lines.append(f"- {u['label']}  size={u['size']}  ref={u['ref']}")
            lines.append(f"Aday sayısı: {len(docker_unused)}")
            lines.append("")

    if shutil.which("crictl"):
        any_rt = True
        c_lines, crictl_unused = collect_crictl()
        if args.mode == "report":
            lines.extend(c_lines)
        elif args.mode in ("unused", "prune"):
            lines.append("=== crictl — kullanılmayan (IN_USE=no) ===")
            if not crictl_unused:
                lines.append("(yok)")
            else:
                for u in crictl_unused:
                    lines.append(f"- {u['label']}  size={u['size']}  ref={u['ref']}")
            lines.append(f"Aday sayısı: {len(crictl_unused)}")
            lines.append("")

    if not any_rt:
        lines.append(
            "Bu host'ta docker ve crictl bulunamadı; imaj envanteri alınamadı."
        )

    if args.mode == "prune":
        lines.append("=== SİLME BAŞLIYOR ===")
        if shutil.which("docker"):
            lines.extend(prune_docker(docker_unused))
        if shutil.which("crictl"):
            lines.extend(prune_crictl(crictl_unused))
        lines.append(
            "Not: Bazı imajlar paylaşılan katman / son referans yüzünden silinemeyebilir."
        )
    elif args.mode == "unused":
        lines.append(
            "Silmek için: playbooks/18_prune_unused_images.yml "
            "--extra-vars 'image_prune_confirm=true'"
        )

    print("\n".join(lines))


if __name__ == "__main__":
    main()
