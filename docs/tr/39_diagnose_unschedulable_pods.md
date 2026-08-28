---
lang: tr
title: "39 · diagnose_unschedulable_pods"
parent: Playbook Kılavuzları
nav_order: 39
---

# 39_diagnose_unschedulable_pods.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Kubernetes](https://img.shields.io/badge/Kubernetes-Pod_Diagnostics-326CE5?style=flat)

## Amaç

Pending veya başlatılamayan pod'lar için scheduler condition, container waiting reason, PVC ve son event verilerini birleştirir. Aşağıdaki durumları açıklar:

- `Unschedulable`
- Yetersiz CPU/RAM, taint, affinity ve node selector sorunları
- Bound olmayan PVC
- `ErrImagePull` / `ImagePullBackOff`
- `CrashLoopBackOff`
- Container config/image adı hataları

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `pod_diagnostics_excluded_namespaces` | boş | Hariç tutulacak namespace listesi |
| `pod_diagnostics_max_pods` | `100` | Raporlanacak maksimum pod |
| `pod_diagnostics_events_per_pod` | `5` | Pod başına son event sayısı |

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/39_diagnose_unschedulable_pods.yml
```
