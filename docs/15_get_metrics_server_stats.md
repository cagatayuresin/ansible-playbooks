---
lang: en
title: "15 · get_metrics_server_stats"
parent: Playbook Guides
nav_order: 15
---

# 15_get_metrics_server_stats.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

If metrics-server is ready, reports **node** and **pod** CPU/memory usage via `kubectl top` in a readable form. If it is not installed, it does not install; it prints a warning (use 16 to install).

Shared tasks:
- [tasks/metrics_server_check.yml](../playbooks/tasks/metrics_server_check.yml)
- [tasks/metrics_server_report.yml](../playbooks/tasks/metrics_server_report.yml)

## Report sections

| Section | Command | How to read |
|---|---|---|
| Node | `kubectl top nodes` | Instant CPU (cores) and MEMORY per node |
| Pod CPU | `kubectl top pods -A --sort-by=cpu` | Highest CPU pods first |
| Pod memory | `kubectl top pods -A --sort-by=memory` | Highest RAM pods first |

Values are instantaneous (metrics-server scrapes ~15s); this is not a long-term graph. Interpret high usage together with [10](10_check_system_health.md) / [11](11_check_monitoring_tools.md).

## Requirements

- `master` / `singlenode`, first control-plane
- metrics-server must be **READY** (`Available=True`). If not, use 14 or 16.

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/15_get_metrics_server_stats.yml
```

## Notes

- Right after a fresh install you may see “no data”; waiting ~1 minute and re-running 15 is enough.
- Read-only.
