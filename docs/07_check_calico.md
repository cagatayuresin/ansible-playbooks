---
lang: en
title: "07 · check_calico"
parent: Playbook Guides
nav_order: 7
---

# 07_check_calico.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

This playbook reports the current Calico CNI version (`calico-node` DaemonSet image tag) and, optionally, applies a new manifest to upgrade it.

⚠️ Calico is not an apt package; it is a DaemonSet running in the cluster. If `calico_manifest_url` is set, a real upgrade is applied (this is not read-only). Check Calico's official upgrade guide before skipping versions — some jumps also require a CRD update.

## Requirements

- Runs on the first control-plane node with `kubectl` access (the first host in the `master`/`singlenode` group).
- To upgrade, set `calico_manifest_url`; if it is omitted, only the current version is reported.

## How to run

```bash
# Report the current version only:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/07_check_calico.yml

# Upgrade:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/07_check_calico.yml \
  --extra-vars "calico_manifest_url=https://raw.githubusercontent.com/projectcalico/calico/v3.31.1/manifests/calico.yaml"
```

## Sample output

```text
TASK [Ping connectivity test] **************************************************
ok: [203.0.113.10]

TASK [Kubeconfig / kubectl access check (when: first control-plane node)] ***
ok: [203.0.113.10]

TASK [calico_manifest_url not provided warning (when: calico_manifest_url must NOT be set)] ***
ok: [203.0.113.10] => {
    "msg": "calico_manifest_url was not set; no update was applied. Example: --extra-vars \"calico_manifest_url=<official manifest URL>\""
}

TASK [Calico version report (when: first control-plane node and kubectl access)] ***
ok: [203.0.113.10] => {
    "msg": "Calico: quay.io/calico/node:v3.31.1 -> quay.io/calico/node:v3.31.1"
}
```
