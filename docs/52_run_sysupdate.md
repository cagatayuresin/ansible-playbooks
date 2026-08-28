---
lang: en
title: "52 · run_sysupdate"
parent: Playbook Guides
nav_order: 52
---

# 52_run_sysupdate.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Maintenance](https://img.shields.io/badge/Maintenance-Confirm_Lock-F59E0B?style=flat)

## ⚠️ Does not upgrade packages without confirmation

A default run produces a report only: APT simulation, snap/flatpak inventory, disk, trash count, reboot flag. Changes require `sysupdate_confirm=true`.

This is the Ansible counterpart of the interactive `sysupdate` function installed by [51](51_install_sysupdate_function.md). It is **not** the Kubernetes node drain/reboot flow; use [41_patch_and_reboot_nodes](41_patch_and_reboot_nodes.md) for that. 52 does not reboot.

## Confirmed workflow

1. On Debian family: `apt` update + safe upgrade + autoremove + autoclean
2. If snap is present: `snap refresh` and cleanup of disabled revisions
3. If Flatpak is present: update + unused removal
4. Target user’s thumbnail files older than 30 days (optional)
5. Trash is reported only, not emptied
6. Disk and reboot-required report

On non-Debian hosts the apt step is skipped; the message points to 41.

## Variables

| Variable | Default | Description |
|---|---|---|
| `sysupdate_confirm` | `false` | Enables package updates |
| `sysupdate_clean_thumbnails` | `true` | On a confirmed run, delete 30d+ thumbnails |
| `sysupdate_target_user` | `ansible_user` | Owner of thumbnail/trash paths |

## How to run

```bash
# Report only:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/52_run_sysupdate.yml

# Apply (no reboot):
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/52_run_sysupdate.yml \
  --limit jump --extra-vars 'sysupdate_confirm=true'
```

For single-node cluster or worker maintenance, use the drain confirmations in 41; 52 is intended for workstation / bastion-style hosts.
