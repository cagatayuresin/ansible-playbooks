---
lang: en
title: "35 · check_service_endpoints"
parent: Playbook Guides
nav_order: 35
---

# 35_check_service_endpoints.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Kubernetes](https://img.shields.io/badge/Kubernetes-EndpointSlice-326CE5?style=flat)

## Purpose

Matches Services with `discovery.k8s.io/v1` EndpointSlice resources:

- Services with no EndpointSlice
- Services that have endpoints but no ready backends
- Partially ready endpoint groups
- LoadBalancers whose external address is still `Pending`
- Unnamed ports among multiple ports

A missing or `null` `endpoints` field on an EndpointSlice is treated as an empty backend
list and shown as a critical finding in the report.

`ExternalName` services are shown as information only.

## Variables

| Variable | Default | Description |
|---|---|---|
| `service_endpoints_excluded_namespaces` | `kube-system,kube-public,kube-node-lease` | Namespaces excluded from the audit |
| `service_endpoints_max_findings` | `300` | Maximum findings |

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/35_check_service_endpoints.yml
```

Official reference: [Kubernetes EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
