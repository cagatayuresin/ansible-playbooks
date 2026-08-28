---
lang: en
title: "13 · check_journal_errors"
parent: Playbook Guides
nav_order: 13
---

# 13_check_journal_errors.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Purpose

For DevOps / SRE diagnosis, on each node via `journalctl`:

1. **Kernel** error logs (`err` and above)
2. **Kernel** warnings (`warning`)
3. **System-wide** error logs (all systemd units, `err` and above)
4. **Kernel errors for this boot**

collected and reported read-only. Does not change the system.

[10_check_system_health](10_check_system_health.md) is the overall health summary; this playbook looks at log level for “what broke / what is warning”.

## Multi-host output

The **first line** of each host report is machine identity:

```text
################################################################################
# HOST: 192.168.1.21
# hostname: worker1
# since: 24 hours ago | line limit/section: 80
################################################################################
```

`HOST` = address/name in inventory (`inventory_hostname`), `hostname` = the machine's own hostname. When you run it on several nodes, use that to see which block belongs to which machine. Ansible already writes `ok: [host]`; the identity is also embedded in the message so it is not lost in a long report.

## Variables

| Variable | Default | Description |
|---|---|---|
| `journal_since` | `24 hours ago` | journalctl `--since` value |
| `journal_lines` | `80` | Maximum lines per section |

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/13_check_journal_errors.yml \
  --extra-vars 'journal_since="6 hours ago" journal_lines=120'

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/13_check_journal_errors.yml --limit workers
```

## Requirements

- `hosts: all`
- `become: true` (sudo) — reading the system journal usually needs root; `ansible_become_pass` must be in inventory.
- A Linux host running `systemd-journald` (Ubuntu/Debian and similar)

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/13_check_journal_errors.yml
```

## How to read the sections

### journalctl priority levels

| Level | Meaning |
|---|---|
| emerg / alert / crit | Emergency / critical |
| err | Error — should be investigated |
| warning | Warning — trend / early signal |
| notice / info / debug | Not filtered by this playbook (noise) |

### Kernel ERR+

Hardware, driver, memory, filesystem on the kernel side. Example red flags:

- `Out of memory` / `oom-killer` → memory pressure
- `I/O error`, `Buffer I/O error`, `EXT4-fs error` → disk
- `nvme` / `ata` reset, timeout → storage path
- `BUG:`, `Oops`, `general protection fault` → serious kernel/driver failure
- `NETDEV WATCHDOG`, NIC reset → network

### Kernel WARNING

Not a crash yet; thrashing, deprecated API, retry, thermal throttle, and so on. A one-off can be noise; **repeating** identical warnings matter.

### System ERR+ (all units)

`sshd`, `kubelet`, `containerd`, `cron`, auth, application units. If the kernel section is empty but this one is full, the problem is in userspace. Repeating fail lines from the same unit → `systemctl status <unit>` / `journalctl -u <unit>`.

### This boot kernel ERR+

Independent of `--since`; since the last reboot. Answers “it was fixed yesterday, but is it back since this boot?”.

Empty sections print `-- No records in this window / at this priority --`; that is usually good news.

## Sample output (shortened)

```text
TASK [Journal error / kernel log report] ***
ok: [192.168.1.21] => {
  "msg": [
    "################################################################################\n# HOST: 192.168.1.21\n# hostname: worker1\n# since: 24 hours ago | line limit/section: 80\n################################################################################",
    "=== Kernel ERR+ (24 hours ago) ===\nComment: ...\n-- No records in this window / at this priority --",
    "=== System ERR+ all units (24 hours ago) ===\n...\n2026-07-29T10:01:02+00:00 worker1 kubelet[1234]: E0729 ... failed to ..."
  ]
}
```

## Notes

- If the line limit is hit, the **newest** records are returned (`-n`); to go further back, increase `journal_lines` or widen `journal_since`.
- In noisy environments, target the suspected node first with `--limit`.
- Read-only: does not delete logs or truncate the journal.
