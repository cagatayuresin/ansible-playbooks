---
lang: en
title: "36 · check_pod_security_posture"
parent: Playbook Guides
nav_order: 36
---

# 36_check_pod_security_posture.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Security](https://img.shields.io/badge/Security-Pod_Posture-7C3AED?style=flat)

## Purpose

Inspects namespace Pod Security Admission labels and running pods’ security contexts:

- `privileged`, root, and privilege escalation
- `hostNetwork`, `hostPID`, `hostIPC`, `hostPath`, `hostPort`
- Extra Linux capabilities
- Missing or `Unconfined` seccomp
- Root filesystem that is not read-only
- Namespace `enforce`, `audit`, and `warn` labels

This check is heuristic; it is not the full policy evaluator of the Kubernetes admission controller.

## Variables

| Variable | Default | Description |
|---|---|---|
| `pod_security_excluded_namespaces` | `kube-system,kube-public,kube-node-lease` | Excludes system pods from the default report |
| `pod_security_max_findings` | `400` | Maximum findings |

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/36_check_pod_security_posture.yml
```

Official reference: [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
