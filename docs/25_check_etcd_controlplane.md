---
lang: en
title: "25 · check_etcd_controlplane"
parent: Playbook Guides
nav_order: 25
---

# 25_check_etcd_controlplane.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

Read-only control-plane / etcd check:

- apiserver/etcd/scheduler/controller (or k3s) pods in kube-system
- `/healthz` `/readyz` `/livez`
- **k3s**: `etcd-snapshot ls`, data dir size
- **kubeadm**: `etcdctl endpoint health/status/alarm`, dbSize vs in-use (defrag **hint** only, does not run it), snapshot file age

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/25_check_etcd_controlplane.yml
```

## Notes

- `become: true` (PKI / k3s directories)
- Defrag, restore, and snapshot **are not performed**
- Script: `playbooks/files/k8s_etcd_controlplane_check.py`
