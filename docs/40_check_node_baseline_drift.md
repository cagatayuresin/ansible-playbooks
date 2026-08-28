---
lang: en
title: "40 · check_node_baseline_drift"
parent: Playbook Guides
nav_order: 40
---

# 40_check_node_baseline_drift.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Linux](https://img.shields.io/badge/Linux-Baseline_Drift-FCC624?style=flat)

## Purpose

Collects a normalized baseline from all hosts and marks differing values as `[DRIFT]`:

- OS, kernel, architecture, and cgroup version
- Swap, IP forwarding, and bridge netfilter
- `overlay` / `br_netfilter` modules
- containerd and kubelet versions
- containerd/kubelet config SHA256 digests
- SystemdCgroup and kubelet cgroup driver
- Time-sync service and reboot required

Config contents are not written to the report; only the first 16 characters of the SHA256 digest are compared.

## Variables

The fields included in the drift comparison can be customized with the `node_baseline_compare_fields` list.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/40_check_node_baseline_drift.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/40_check_node_baseline_drift.yml \
  --limit workers
```
