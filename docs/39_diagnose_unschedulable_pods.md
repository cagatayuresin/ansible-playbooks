---
lang: en
title: "39 · diagnose_unschedulable_pods"
parent: Playbook Guides
nav_order: 39
---

# 39_diagnose_unschedulable_pods.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Kubernetes](https://img.shields.io/badge/Kubernetes-Pod_Diagnostics-326CE5?style=flat)

## Purpose

Combines scheduler conditions, container waiting reasons, PVCs, and recent events for Pending or pods that cannot start. Explains:

- `Unschedulable`
- Insufficient CPU/RAM, taint, affinity, and node selector issues
- Unbound PVCs
- `ErrImagePull` / `ImagePullBackOff`
- `CrashLoopBackOff`
- Container config/image name errors

## Variables

| Variable | Default | Description |
|---|---|---|
| `pod_diagnostics_excluded_namespaces` | empty | Namespace list to exclude |
| `pod_diagnostics_max_pods` | `100` | Maximum pods to report |
| `pod_diagnostics_events_per_pod` | `5` | Recent events per pod |

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/39_diagnose_unschedulable_pods.yml
```
