---
lang: en
title: "14 · check_metrics_server"
parent: Playbook Guides
nav_order: 14
---

# 14_check_metrics_server.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

On the first control-plane node (first host in the `master` / `singlenode` group), checks whether **metrics-server** is installed and its API is Available. Does not install; does not collect stats.

Shared task: [tasks/metrics_server_check.yml](../playbooks/tasks/metrics_server_check.yml)

## What is checked?

| Check | Command / source |
|---|---|
| kubectl access | `kubectl cluster-info` |
| Deployment | `kubectl -n kube-system get deploy metrics-server` |
| API | `v1beta1.metrics.k8s.io` → `Available=True` |
| Pods | `k8s-app=metrics-server` label |

`metrics_server_ready` = deployment exists **and** API is Available.

## Requirements

- `master` and/or `singlenode` in inventory
- Runs only on `first_control_plane`
- `KUBECONFIG` at play level is `~/.kube/config` (k3s compatibility)

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/14_check_metrics_server.yml
```

## Next steps

- If ready, stats: [15_get_metrics_server_stats](15_get_metrics_server_stats.md)
- If not, install + stats: [16_ensure_metrics_server](16_ensure_metrics_server.md)

## Multi-host

Reports start with `HOST` / `hostname`. metrics-server is cluster-scoped, so the query is made from a single control-plane node.
