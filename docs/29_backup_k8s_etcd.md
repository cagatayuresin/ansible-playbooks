---
lang: en
title: "29 · backup_k8s_etcd"
parent: Playbook Guides
nav_order: 29
---

# 29_backup_k8s_etcd.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

Takes a snapshot of the `etcd` database (the heart of Kubernetes) and stores it safely.

**Playbook:** `playbooks/29_backup_k8s_etcd.yml`

## What it does

* Detects whether the cluster uses `k3s` or `kubeadm` (etcdctl).
* Takes the snapshot and saves it under `/var/backups/etcd` with a timestamp.
* Protects the backup directory with `0700` and snapshot files with `0600`.
* After a successful backup, removes snapshots older than the retention period.
* Runs only on the first server in the master nodes to avoid duplicate work.

## Parameters (optional)

| Variable | Default | Description |
|---|---|---|
| `etcd_backup_retention_days` | `30` | After a successful backup, deletes snapshots older than this many days. Must be a positive integer. |

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/29_backup_k8s_etcd.yml \
  --extra-vars 'etcd_backup_retention_days=14'
```

> An etcd snapshot also contains Kubernetes Secret data. Restrict access to the backup directory to authorized users and copy the backup to a separate, encrypted location.

## Sample output

```text
################################################################################
# HOST: master1
################################################################################
k3s detected. Running k3s etcd-snapshot...
Retention: snapshots older than 30 days were removed.
SUCCESS: k3s etcd snapshot saved to /var/backups/etcd
```
