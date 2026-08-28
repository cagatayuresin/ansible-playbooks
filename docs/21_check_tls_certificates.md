---
lang: en
title: "21 · check_tls_certificates"
parent: Playbook Guides
nav_order: 21
---

# 21_check_tls_certificates.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

Read-only TLS / certificate inventory (on the first control-plane):

1. **kubeadm** `certs check-expiration` (if present)
2. **Control-plane PEM files** — `/etc/kubernetes/pki`, `/var/lib/rancher/k3s/server/tls` (openssl expiry + days remaining)
3. **Ingress TLS** — for each Ingress: domains, secret, issuer, SAN, expiry date, days remaining, level
4. **cert-manager** `Certificate` resources (if the CRD exists)
5. **All `kubernetes.io/tls` secrets** — the most critical 25 (by days remaining)

## Levels

| Level | Days remaining |
|---|---|
| `EXPIRED` | < 0 |
| `CRITICAL` | ≤ 7 |
| `WARNING` | ≤ 30 |
| `APPROACHING` | ≤ 90 |
| `OK` | > 90 |

## Requirements

- `hosts: master:singlenode` — `first_control_plane` only
- `become: true` (PKI directories are usually root)
- `kubectl` + `openssl` + `python3`
- `KUBECONFIG` at play level is `~/.kube/config`

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/21_check_tls_certificates.yml
```

## How to read Ingress output

Each record has:

- **domains** — Ingress rule / TLS hosts
- **secret** — `namespace/secretName`
- **issuer / SAN** — certificate identity
- **REMAINING / EXPIRY / LEVEL** — renewal urgency

`NO_TLS` / `SECRET_MISSING` / `NO_CERT` → missing configuration, not expiry.

## Notes

- Script: `playbooks/files/k8s_tls_certificates_check.py`
- Does not change the cluster.
