---
lang: en
title: "41 · patch_and_reboot_nodes"
parent: Playbook Guides
nav_order: 41
---

# 41_patch_and_reboot_nodes.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Maintenance](https://img.shields.io/badge/Maintenance-Serial_1-F59E0B?style=flat)

## ⚠️ Can update packages and reboot live nodes

A default run only reports pending packages and whether a reboot is needed. Changes require `node_patch_confirm=true`.

Confirmed maintenance flow:

1. If it is a Kubernetes node, drain via the first control-plane
2. `apt dist-upgrade` on Debian, `dnf update` on RedHat
3. Reboot if reboot was also confirmed and is required
4. Uncordon the node
5. On error, attempt uncordon from the rescue block

Hosts are processed one at a time with `serial: 1`.

## Variables

| Variable | Default | Description |
|---|---|---|
| `node_patch_confirm` | `false` | Enables package updates |
| `node_reboot_confirm` | `false` | Allows a reboot when required |
| `node_reboot_always` | `false` | Reboots even if there is no reboot flag |
| `node_allow_single_node_maintenance` | `false` | Extra confirmation for singlenode maintenance |
| `kubernetes_node_name` | `ansible_hostname` | Node name in the Kubernetes API |

## How to run

```bash
# Report only:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/41_patch_and_reboot_nodes.yml

# Patch a worker and reboot if required:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/41_patch_and_reboot_nodes.yml \
  --limit worker1 \
  --extra-vars 'node_patch_confirm=true node_reboot_confirm=true'
```

A singlenode cluster also requires `node_allow_single_node_maintenance=true`. Before maintenance, verify a current etcd backup with `32_verify_etcd_backup.yml`.
