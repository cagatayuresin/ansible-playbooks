---
lang: en
title: "28 · check_network_policies"
parent: Playbook Guides
nav_order: 28
---

# 28_check_network_policies.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

Per-namespace **NetworkPolicy** inventory:

- Which namespaces have / do not have a policy (none ≈ default-allow, depends on the CNI)
- Per policy: policyTypes, podSelector, ingress/egress rule counts (empty list = deny-all)

## Variables

| Variable | Default | Description |
|---|---|---|
| `netpol_namespace` | `""` | If set, only that ns |

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/28_check_network_policies.yml
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/28_check_network_policies.yml \
  --extra-vars 'netpol_namespace=n8n'
```

Script: `playbooks/files/k8s_network_policies_check.py`
