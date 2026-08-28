---
lang: en
title: "05 · check_k8s_services"
parent: Playbook Guides
nav_order: 5
---

# 05_check_k8s_services.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

This playbook **dynamically** discovers systemd services related to Kubernetes/containers (not a hardcoded list; it matches the `kube|containerd|calico|etcd|runc` pattern) and reports each service's active/enabled state plus the last 10 log lines.

## Requirements

- `hosts: all` — runs on every node.
- Service discovery uses Ansible's built-in `service_facts` module; no extra collection is required.
- The user must be able to read journal logs so `journalctl` output is available.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/05_check_k8s_services.yml

# Limit to a host or group:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/05_check_k8s_services.yml --limit worker1
```

## Sample output

```text
TASK [Ping connectivity test] **************************************************
ok: [203.0.113.10]

TASK [Service status report - active/enabled (when: matching services must exist)] ***
ok: [203.0.113.10] => (item=containerd.service) => {"msg": "containerd.service -> state: running, enabled at boot: enabled"}
ok: [203.0.113.10] => (item=kubelet.service) => {"msg": "kubelet.service -> state: running, enabled at boot: enabled"}

TASK [Service log report (when: logs must be readable)] ************************
ok: [203.0.113.10] => (item=kubelet.service) => {
    "msg": "===== kubelet.service recent logs =====\n... (last 10 lines) ..."
}
```

## Notes

- The service list is fully dynamic: `service_facts` scans all services on the system and only names matching `kube`, `containerd`, `calico`, `etcd`, or `runc` are included. Docker is outside this pattern.
- Log output is capped at 10 lines so the report stays readable when many services/hosts are involved.
- `.get('state', ...)` / `.get('status', ...)` are used because some service entries in `service_facts` can omit those fields.
