---
title: "22 · check_k8s_warning_events"
parent: Playbook Kılavuzları
nav_order: 22
---

# 22_check_k8s_warning_events.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

İlk control-plane üzerinden cluster’daki **Warning** tipindeki Kubernetes event’lerini toplar:

- Son N saat (varsayılan 24)
- Reason frekansı
- Namespace dağılımı
- Son event satırları (zaman, count, kind/name, message)

Salt-okunur.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `events_since_hours` | `24` | Ne kadar geriye bakılsın |
| `events_limit` | `80` | Listelenecek max event |
| `events_namespace` | `""` (boş) | Doluysa sadece o namespace; boşsa tüm namespace’ler |

```bash
# Tüm namespace'ler
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/22_check_k8s_warning_events.yml \
  --extra-vars 'events_since_hours=48 events_limit=120'

# Sadece bir namespace
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/22_check_k8s_warning_events.yml \
  --extra-vars 'events_namespace=n8n'
```

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/22_check_k8s_warning_events.yml
```

## Yorumlama

| Reason (ör.) | Ne bakmalı |
|---|---|
| `FailedScheduling` | Kaynak / taint / affinity |
| `FailedMount` / `FailedAttachVolume` | PV/storage → 23 |
| `ImagePullBackOff` / `ErrImagePull` | Registry / image → 17, 19 |
| `OOMKilled` / `BackOff` | Limit / bellek → 10, 15 |
| `Unhealthy` | Probe / uygulama sağlığı → 01 |

## Notlar

- Script: `playbooks/files/k8s_warning_events_check.py`
- Event’ler etcd’de tutulur ve zamanla silinir; “son 24s boş” her zaman sorun yok demektir.
