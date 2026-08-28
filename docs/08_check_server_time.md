---
lang: en
title: "08 · check_server_time"
parent: Playbook Guides
nav_order: 8
---

# 08_check_server_time.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Purpose

This playbook reports the server's time/timezone (`timedatectl`) and **dynamically** detects which time-sync service is in use (chrony, systemd-timesyncd, or ntpd — whichever is installed). It does not assume a fixed service name; `service_facts` scans all services and matches `chrony|systemd-timesyncd|ntpd`.

## Requirements

- `hosts: all` — runs on every node.
- Service discovery uses Ansible's built-in `service_facts` module; no extra collection is required.
- The first block of the report is machine identity (`HOST` = inventory name/IP, `hostname` = the server's own name); use it to tell which output belongs to which node.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/08_check_server_time.yml
```

## Sample output

```text
TASK [Ping connectivity test] **************************************************
ok: [203.0.113.10]

TASK [Time sync service status (when: matching service must exist)] ***
ok: [203.0.113.10] => (item=systemd-timesyncd.service) => {
    "msg": "systemd-timesyncd.service -> state: running, enabled at boot: enabled"
}

TASK [Time and timezone report] ************************************************
ok: [203.0.113.10] => {
    "msg": "               Local time: Tue 2026-07-28 11:31:07 UTC\n           Universal time: Tue 2026-07-28 11:31:07 UTC\n                 RTC time: Tue 2026-07-28 11:31:07\n                Time zone: Etc/UTC (UTC, +0000)\nSystem clock synchronized: yes\n              NTP service: active\n          RTC in local TZ: no"
}
```
