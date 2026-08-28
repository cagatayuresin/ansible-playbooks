---
lang: en
title: "37 · check_rbac_risks"
parent: Playbook Guides
nav_order: 37
---

# 37_check_rbac_risks.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Security](https://img.shields.io/badge/Security-RBAC-7C3AED?style=flat)

## Purpose

Reports high-risk permissions in RBAC resources:

- `cluster-admin` bindings
- `system:masters`, `system:unauthenticated`, and broad authenticated bindings
- Wildcard verb/resource rules
- `bind`, `escalate`, `impersonate`
- Secret, pod exec/attach, and service account token permissions
- Default ServiceAccount token automount state

Built-in Kubernetes ClusterRole rules that start with `system:` are skipped during role analysis; their bindings are still reported.

## Variables

| Variable | Default | Description |
|---|---|---|
| `rbac_risks_excluded_namespaces` | `kube-system,kube-public,kube-node-lease` | Exceptions for namespace-scoped analysis |
| `rbac_risks_max_findings` | `400` | Maximum findings |

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/37_check_rbac_risks.yml
```

Official reference: [Kubernetes RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
