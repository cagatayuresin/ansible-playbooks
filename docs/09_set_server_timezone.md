---
lang: en
title: "09 · set_server_timezone"
parent: Playbook Guides
nav_order: 9
---

# 09_set_server_timezone.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat)

## Purpose

This playbook sets the server timezone to `Europe/Istanbul`, enables the time-sync services found by [08_check_server_time.yml](../playbooks/08_check_server_time.yml) (chrony/systemd-timesyncd/ntpd — whichever is installed) and marks them enabled at boot, then verifies the result with `timedatectl`. When run on its own it first runs `08_check_server_time.yml` (`import_playbook`) to report the pre-change state; the discovered service list (`time_services` fact) is reused in the second play to start those services.

Note: It is normal for `RTC time` to differ from `Local time` — Linux typically keeps the hardware clock (RTC) in UTC, and `Local time` applies the timezone offset. Matching `RTC time` and `Universal time` is the expected/correct behavior.

⚠️ Unlike the others, this playbook is **not a read-only check** — it actually changes the target server's system timezone.

## Requirements

- `hosts: all` — runs on every node.
- The `community.general` collection is required (`community.general.timezone` module).
- Prefer `--limit` to a specific host/group instead of `hosts: all`.
- **The timezone task runs with `become: true` (sudo).** `timedatectl set-timezone` is a D-Bus/polkit operation via `org.freedesktop.timedate1` that requires root; without sudo, polkit never grants approval in a non-interactive SSH session and the request fails with "Connection timed out". Unlike the read-only commands in other playbooks, this is a real system change, so sudo is required.
- The first block of the result/verification reports is machine identity (`HOST` + `hostname`); use it to tell which output belongs to which node.

## How to run

```bash
# See what would change first (no changes on the system):
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/09_set_server_timezone.yml --check --diff

# Apply for real:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/09_set_server_timezone.yml

# Limit to a specific host:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/09_set_server_timezone.yml --limit master
```

## Sample output

```text
PLAY [Server Time and Timezone Report] *****************************************
... (output from 08 — state before the change) ...

PLAY [Set Server Timezone to Europe/Istanbul] **********************************

TASK [Set timezone to Europe/Istanbul] *****************************************
changed: [203.0.113.10]

TASK [Timezone change result] **************************************************
ok: [203.0.113.10] => {
    "msg": "Timezone changed to Europe/Istanbul"
}

TASK [Time sync service enablement report] *************************************
ok: [203.0.113.10] => (item=systemd-timesyncd.service) => {
    "msg": "systemd-timesyncd.service -> already active and enabled"
}

TASK [Verification report] *****************************************************
ok: [203.0.113.10] => {
    "msg": "               Local time: Tue 2026-07-28 14:xx:xx +03\n...\n                Time zone: Europe/Istanbul (+03, +0300)\n..."
}
```
