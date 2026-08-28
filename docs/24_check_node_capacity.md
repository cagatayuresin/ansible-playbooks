---
lang: en
title: "24 · check_node_capacity"
parent: Playbook Guides
nav_order: 24
---

# 24_check_node_capacity.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

Read-only from the first control-plane:

- Node **conditions** (Ready, MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable)
- **Capacity**: allocatable vs total pod **requests/limits** vs (if present) instant `kubectl top` usage

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/24_check_node_capacity.yml
```

## Interpretation

| Finding | Meaning |
|---|---|
| Ready≠True / Pressure=True | Node is under pressure or unhealthy |
| High req% | Scheduling gets harder (new pods may not fit) |
| High use% | Instant load — look together with 15 |
| top n/a | metrics-server missing → 14/15 |

Script: `playbooks/files/k8s_node_capacity_check.py`
