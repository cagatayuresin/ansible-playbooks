---
lang: en
title: "32 · verify_etcd_backup"
parent: Playbook Guides
nav_order: 32
---

# 32_verify_etcd_backup.yml - Usage Guide

![Conditional](https://img.shields.io/badge/State-Read--Only_Default-F59E0B?style=flat) ![etcd](https://img.shields.io/badge/Datastore-etcd-419EDA?style=flat)

## Purpose

Finds the newest snapshot under `/var/backups/etcd` and reports its age, size, SHA256, and file permissions. Verifies integrity with `etcdutl` or `etcdctl snapshot status`. An optional restore test writes only to a temporary directory and does not touch live etcd data.

## Requirements

- `etcdutl` or `etcdctl` on the first control-plane
- Root access to the backup directory
- Snapshot names must start with the `etcd_snapshot_*` pattern

## Variables

| Variable | Default | Description |
|---|---|---|
| `etcd_backup_directory` | `/var/backups/etcd` | Snapshot directory |
| `etcd_backup_max_age_hours` | `24` | Backups older than this are treated as critical |
| `etcd_backup_restore_test` | `false` | Runs an isolated restore test |
| `etcd_backup_verify_fail_on_error` | `true` | Fails the playbook on a critical finding |

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/32_verify_etcd_backup.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/32_verify_etcd_backup.yml \
  --extra-vars 'etcd_backup_restore_test=true'
```

The restore test runs in an isolated directory created with `mktemp`; the live member directory and manifests are not changed.

Official reference: [etcd Disaster Recovery](https://etcd.io/docs/v3.7/op-guide/recovery/)
