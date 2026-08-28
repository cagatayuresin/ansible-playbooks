---
lang: en
title: "04 · check_k8s_versions"
parent: Playbook Guides
nav_order: 4
---

# 04_check_k8s_versions.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

This playbook collects and reports version information for the Kubernetes stack running on a node (control-plane or worker): kubectl, kubeadm, kubelet, containerd, runc, and etcd.

Version detection lives in the shared task list [tasks/k8s_versions.yml](../playbooks/tasks/k8s_versions.yml). [06_update_k8s_services.yml](../playbooks/06_update_k8s_services.yml) uses the same file to capture versions before and after an upgrade, so the two playbooks do not implement detection twice.

## Requirements

- `hosts: all` — kubeadm/kubelet/containerd/runc checks run on every node.
- Steps that need `kubectl` (kubectl version, etcd image) run only on hosts where `kubectl cluster-info` succeeds (typically master/singlenode). If access fails, those steps are skipped and the other version data is still collected.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/04_check_k8s_versions.yml

# Limit to a host or group:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/04_check_k8s_versions.yml --limit master
```

## Sample output

```text
TASK [Ping connectivity test] **************************************************
ok: [203.0.113.10]

TASK [Kubeconfig / kubectl access check] ***************************************
ok: [203.0.113.10]

TASK [Version report] **********************************************************
ok: [203.0.113.10] => {
    "msg": [
        "kubectl: clientVersion: ... gitVersion: v1.34.10 ...",
        "kubeadm: v1.34.10",
        "kubelet: Kubernetes v1.34.10",
        "containerd: containerd github.com/containerd/containerd/v2 v2.2.0 ...",
        "runc: runc version 1.3.3 ...",
        "etcd image: registry.k8s.io/etcd:3.6.5-0"
    ]
}
```
