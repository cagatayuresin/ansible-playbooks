---
title: "24 · check_node_capacity"
parent: Playbook Kılavuzları
nav_order: 24
---

# 24_check_node_capacity.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

İlk control-plane üzerinden salt-okunur:

- Node **conditions** (Ready, MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable)
- **Capacity**: allocatable vs pod **requests/limits** toplamı vs (varsa) `kubectl top` anlık kullanım

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/24_check_node_capacity.yml
```

## Yorumlama

| Bulgu | Anlam |
|---|---|
| Ready≠True / Pressure=True | Node baskıda veya sorunlu |
| req% yüksek | Scheduling zorlaşır (yeni pod sığmayabilir) |
| use% yüksek | Anlık yük — 15 ile birlikte bak |
| top n/a | metrics-server yok → 14/15 |

Script: `playbooks/files/k8s_node_capacity_check.py`
