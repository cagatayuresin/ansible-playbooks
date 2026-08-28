---
lang: en
title: "38 · check_control_plane_security"
parent: Playbook Guides
nav_order: 38
---

# 38_check_control_plane_security.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Security](https://img.shields.io/badge/Security-Control--Plane-7C3AED?style=flat)

## Purpose

Auto-detects kubeadm or k3s configuration on the first control-plane host and checks:

- Anonymous authentication
- `Node,RBAC` authorization and `AlwaysAllow`
- Insecure port and profiling
- Audit policy/backend
- Secret encryption-at-rest provider order
- NodeRestriction admission plugin
- Minimum TLS version
- File permissions on `admin.conf`, `k3s.yaml`, and private keys

Key material inside encryption providers is never written to output.

## Variables

| Variable | Default | Description |
|---|---|---|
| `control_plane_security_fail_on_critical` | `false` | Fails the playbook on a critical finding |

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/38_check_control_plane_security.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/38_check_control_plane_security.yml \
  --extra-vars 'control_plane_security_fail_on_critical=true'
```

Distribution vendors may apply some settings in different ways; warnings should be evaluated together with the cluster configuration.

Official references: [Encrypting Confidential Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/), [Kubernetes Auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
