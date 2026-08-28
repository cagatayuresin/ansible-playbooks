---
lang: en
title: "23 · check_storage_health"
parent: Playbook Guides
nav_order: 23
---

# 23_check_storage_health.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Purpose

Read-only storage report on each host:

1. **df -hT** — real filesystems
2. **df -i** — inode usage
3. **containerd/crictl / docker** disk usage + total image size
4. **kubectl** if present: PVC / PV / StorageClass + unbound PVCs

## Host scope

`hosts: all` — disk/inode is local to each node. PV/PVC data is filled on the node with kubectl access (usually the control-plane); if kubectl is missing on a worker, that section is skipped.

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/23_check_storage_health.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/23_check_storage_health.yml --limit workers
```

## Interpretation

| Finding | Action |
|---|---|
| High disk Use% | Log / image accumulation; 17–18 |
| High IUse% | Many small files / layers |
| PVC Pending | StorageClass / provisioner / quota |
| PV Released/Failed | Manual cleanup / reclaim policy |

## Notes

- Script: `playbooks/files/storage_health_check.py`
- `become: true` (du / runtime directories)
- Does not change the cluster.
