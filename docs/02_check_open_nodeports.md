---
lang: en
title: "02 · check_open_nodeports"
parent: Playbook Guides
nav_order: 2
---

# 02_check_open_nodeports.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

This playbook finds every Kubernetes service of type `NodePort` that is exposed externally. It then uses the server IP from inventory (`inventory_hostname`) to build clickable/copyable HTTP links (for example `http://192.168.1.10:31234`) and prints them.

## Requirements

- `kubectl` must be installed and configured on the target host (master or singlenode).
- Your Ansible inventory must define a `[master]` or `[singlenode]` group.

The playbook now runs a `kubectl cluster-info` access check before querying NodePorts. If `kubectl` is unavailable, a clear warning is printed and the NodePort query is skipped.

## How to run

```bash
# Run for customer A
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/02_check_open_nodeports.yml

# Run for customer B
ansible-playbook -i inventories/musteri_b/hosts.ini playbooks/02_check_open_nodeports.yml
```

## Sample output

When the ping connectivity test succeeds, active NodePorts are listed and links are generated:

```text
TASK [Ping connectivity test] **************************************************
ok: [192.168.1.10]

TASK [Kubeconfig / kubectl access check] ***************************************
ok: [192.168.1.10]

TASK [Find all NodePort services and their ports] ******************************
ok: [192.168.1.10]

TASK [Generate browser accessible links] ***************************************
ok: [192.168.1.10] => {
    "msg": "The following services are exposed as NodePort. Use the links to open them in a browser:\n\n- default/nginx-service -> http://192.168.1.10:32001\n- argocd/argocd-server -> http://192.168.1.10:30080\n"
}
```
