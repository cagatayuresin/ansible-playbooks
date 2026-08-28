---
lang: tr
title: "27 · check_cluster_dns"
parent: Playbook Kılavuzları
nav_order: 27
---

# 27_check_cluster_dns.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

Cluster **içi** DNS (CoreDNS / kube-dns):

- Service + pod + endpoints
- Corefile özeti
- Node üzerinden kube-dns ClusterIP’ye `dig`/`nslookup` ile `kubernetes.default` çözümleme
- NodeLocal DNS varsa listeler

Dış internet DNS’i için [19](19_check_network_connectivity.md).

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/27_check_cluster_dns.yml
```

Script: `playbooks/files/k8s_cluster_dns_check.py`
