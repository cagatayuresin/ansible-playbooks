---
lang: en
title: "10 · check_system_health"
parent: Playbook Guides
nav_order: 10
---

# 10_check_system_health.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Purpose

This playbook reports overall system health for a server:

- OS (distribution/version), kernel version, uptime
- CPU core count
- Load average (1/5/15 min) and 1-minute load normalized per core
- Run queue (currently running/total process count, from `/proc/loadavg`)
- Zombie (defunct) process count
- Virtualization detection: `ansible_facts` (role/type) + `systemd-detect-virt` + `dmidecode` (manufacturer/product/BIOS version) — tries to identify the hypervisor (Hyper-V, VMware, KVM, and so on)
- Memory usage (`free -h`, with automatic MB/GB units)
- Disk usage (`df -hT`, real filesystems only; virtual ones such as tmpfs/overlay are excluded), size in MB/GB and percent full
- Top 10 CPU-consuming processes
- Top 10 RAM-consuming processes
- Whether a reboot is required (`/var/run/reboot-required`)
- Failed systemd services
- Count of installable package/security updates

## Requirements

- `hosts: all` — runs on every node.
- This playbook uses `gather_facts: true` (unlike the other playbooks in this repo) — OS/kernel/CPU/virtualization data comes from Ansible's own fact gathering.
- `dmidecode` output needs `become: true` (sudo); if it is missing or inaccessible, that section quietly shows "could not be accessed" and the playbook does not fail.
- The first block of the report is machine identity (`HOST` = inventory name/IP, `hostname` = the server's own name); use it to tell which output belongs to which node.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/10_check_system_health.yml

# Limit to a host or group:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/10_check_system_health.yml --limit worker1
```

## Sample output

```text
TASK [System health report] ****************************************************
ok: [203.0.113.10] => {
    "msg": [
        "################################################################################\n# HOST: 203.0.113.10\n# hostname: node1\n################################################################################",
        "OS: Ubuntu 22.04 (jammy)",
        "Kernel: 5.15.0-186-generic",
        "Uptime: up 2 days, 6 hours, 20 minutes",
        "CPU cores: 16",
        "Load average (1/5/15 min): 0.97 / 0.98 / 1.01 (1-min per core: 0.06)",
        "Run queue (running/total processes): 1/2090",
        "Zombie (defunct) process count: 0",
        "Virtualization: role=guest, type=VirtualPC, systemd-detect-virt=microsoft",
        "Hardware/Hypervisor info:\nManufacturer: Microsoft Corporation\nProduct: Virtual Machine\nBIOS Version: 090007",
        "Memory:\n               total  used  free  shared  buff/cache  available\nMem:  125Gi  5.2Gi  90Gi  121Mi   29Gi        119Gi\nSwap: 0B     0B    0B",
        "Disk usage:\nFilesystem  Type  Size  Used  Avail  Use%  Mounted on\n/dev/mapper/ubuntu--vg-ubuntu--lv  ext4  540G  388G  130G  75%  /",
        "Top 10 CPU-consuming processes:\n...",
        "Top 10 RAM-consuming processes:\n...",
        "Reboot required: YES",
        "Failed systemd services: None",
        "Installable package updates: 32"
    ]
}
```

## Notes

- `systemd-detect-virt` + `dmidecode` together reveal the hypervisor on guest VMs (for example Microsoft Hyper-V, VMware, KVM) and sometimes the BIOS version; the hypervisor's own version is usually not fully visible from inside the guest — BIOS/product info is only a hint.
- "Reboot required" and "installable package updates" are Debian/Ubuntu-specific (`/var/run/reboot-required`, `apt list --upgradable`); on other distributions those steps quietly return empty/without error.
