---
lang: en
title: "22 · check_k8s_warning_events"
parent: Playbook Guides
nav_order: 22
---

# 22_check_k8s_warning_events.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

Collects Kubernetes events of type **Warning** in the cluster from the first control-plane:

- Last N hours (default 24)
- Reason frequency
- Namespace distribution
- Recent event lines (time, count, kind/name, message)

Read-only.

## Variables

| Variable | Default | Description |
|---|---|---|
| `events_since_hours` | `24` | How far back to look |
| `events_limit` | `80` | Max events to list |
| `events_namespace` | `""` (empty) | If set, only that namespace; if empty, all namespaces |

```bash
# All namespaces
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/22_check_k8s_warning_events.yml \
  --extra-vars 'events_since_hours=48 events_limit=120'

# A single namespace
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/22_check_k8s_warning_events.yml \
  --extra-vars 'events_namespace=n8n'
```

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/22_check_k8s_warning_events.yml
```

## Interpretation

| Reason (e.g.) | What to check |
|---|---|
| `FailedScheduling` | Resources / taint / affinity |
| `FailedMount` / `FailedAttachVolume` | PV/storage → 23 |
| `ImagePullBackOff` / `ErrImagePull` | Registry / image → 17, 19 |
| `OOMKilled` / `BackOff` | Limit / memory → 10, 15 |
| `Unhealthy` | Probe / application health → 01 |

## Notes

- Script: `playbooks/files/k8s_warning_events_check.py`
- Events are stored in etcd and expire over time; “empty for the last 24h” does not always mean there is no problem.
