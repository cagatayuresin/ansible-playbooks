---
lang: tr
title: "28 · check_network_policies"
parent: Playbook Kılavuzları
nav_order: 28
---

# 28_check_network_policies.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

Namespace bazında **NetworkPolicy** envanteri:

- Hangi ns’te policy var / yok (yok ≈ default-allow, CNI’ye bağlı)
- Her policy: policyTypes, podSelector, ingress/egress kural sayısı (boş liste = deny-all)

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `netpol_namespace` | `""` | Doluysa sadece o ns |

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/28_check_network_policies.yml
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/28_check_network_policies.yml \
  --extra-vars 'netpol_namespace=n8n'
```

Script: `playbooks/files/k8s_network_policies_check.py`
