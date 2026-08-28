---
lang: en
title: "33 · check_upgrade_readiness"
parent: Playbook Guides
nav_order: 33
---

# 33_check_upgrade_readiness.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Kubernetes](https://img.shields.io/badge/Kubernetes-Upgrade_Readiness-326CE5?style=flat)

## Purpose

Checks the following blockers in a single report before a Kubernetes upgrade:

- API server and kubelet version alignment
- Node `Ready` / cordon state
- Minor-version skipping and downgrade
- PDBs that can block drain
- Admission webhooks with `failurePolicy=Fail`
- API server deprecated API metrics
- Age of the latest etcd backup
- etcd/root disk fullness

## Variables

| Variable | Default | Description |
|---|---|---|
| `upgrade_readiness_target_version` | empty | Target `X.Y.Z`; if empty, target-specific checks are skipped |
| `upgrade_readiness_backup_directory` | `/var/backups/etcd` | Backup directory |
| `upgrade_readiness_max_backup_age_hours` | `24` | Maximum backup age |
| `upgrade_readiness_max_disk_percent` | `85` | Disk warning threshold |
| `upgrade_readiness_fail_on_blockers` | `true` | Fails the playbook when a blocker is found |

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/33_check_upgrade_readiness.yml \
  --extra-vars 'upgrade_readiness_target_version=1.34.3'
```

Run `06_update_k8s_services.yml` only after this playbook succeeds.

Official references: [kubeadm cluster upgrade](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/), [Kubernetes deprecation policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/)
