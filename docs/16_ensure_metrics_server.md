---
lang: en
title: "16 · ensure_metrics_server"
parent: Playbook Guides
nav_order: 16
---

# 16_ensure_metrics_server.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

1. Checks metrics-server status (same check task as 14)
2. If it is not ready, **installs** it from the official manifest
3. Adds `--kubelet-insecure-tls` if needed (on-prem / self-signed kubelet)
4. Waits for rollout + `kubectl top` to become ready
5. Prints the same stats report as 15

⚠️ Changes the cluster (creates Deployment/APIService if missing). If it is already ready, install is skipped and only stats are collected.

## Shared tasks

- [tasks/metrics_server_check.yml](../playbooks/tasks/metrics_server_check.yml)
- [tasks/metrics_server_install.yml](../playbooks/tasks/metrics_server_install.yml)
- [tasks/metrics_server_report.yml](../playbooks/tasks/metrics_server_report.yml)

## Variables

| Variable | Default | Description |
|---|---|---|
| `metrics_server_version` | `v0.8.1` | Pinned release for a reproducible install |
| `metrics_server_manifest_url` | GitHub `v0.8.1/components.yaml` | Manifest to apply; can be replaced with an internal mirror or a local path on the target host |
| `metrics_server_kubelet_insecure_tls` | `true` | Usually required on-prem; can be set to `false` in the cloud |

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/16_ensure_metrics_server.yml \
  --extra-vars 'metrics_server_kubelet_insecure_tls=false'
```

On a fully air-gapped network, copy the manifest to the first control-plane host and pass the local path:

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/16_ensure_metrics_server.yml \
  --extra-vars 'metrics_server_manifest_url=/opt/k8s-manifests/metrics-server-v0.8.1.yaml'
```

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/16_ensure_metrics_server.yml
```

## Notes

- k3s sometimes ships metrics-server itself; if it is already ready, this playbook only reports top stats.
- `--kubelet-insecure-tls` relaxes kubelet certificate verification; common for lab/on-prem, prefer a proper CA in strict production.
- Metrics Server `0.8.x` supports Kubernetes `1.31+`. For Kubernetes `1.27-1.30`, specify the `v0.7.2` manifest explicitly.
- When upgrading, update both `metrics_server_version` and, if needed, a custom `metrics_server_manifest_url` together.
