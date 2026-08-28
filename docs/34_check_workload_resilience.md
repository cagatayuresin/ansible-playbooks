---
lang: en
title: "34 · check_workload_resilience"
parent: Playbook Guides
nav_order: 34
---

# 34_check_workload_resilience.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Kubernetes](https://img.shields.io/badge/Kubernetes-Workloads-326CE5?style=flat)

## Purpose

Audits Deployment, StatefulSet, and DaemonSet templates for:

- Missing CPU/RAM requests and limits
- Missing readiness, liveness, and startup probes
- Single-replica workloads
- PDB coverage
- Missing anti-affinity / topology spread
- Use of `latest` or untagged container images

The report is advisory; it does not change workload manifests.

## Variables

| Variable | Default | Description |
|---|---|---|
| `workload_resilience_excluded_namespaces` | `kube-system,kube-public,kube-node-lease` | Namespaces excluded from the audit |
| `workload_resilience_max_findings` | `300` | Maximum report lines |

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/34_check_workload_resilience.yml
```

To include system namespaces as well, pass the variable as an empty string.

Official references: [Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/), [PodDisruptionBudget](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
