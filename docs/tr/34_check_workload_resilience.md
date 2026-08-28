---
lang: tr
title: "34 · check_workload_resilience"
parent: Playbook Kılavuzları
nav_order: 34
---

# 34_check_workload_resilience.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Kubernetes](https://img.shields.io/badge/Kubernetes-Workloads-326CE5?style=flat)

## Amaç

Deployment, StatefulSet ve DaemonSet şablonlarını aşağıdaki konularda denetler:

- CPU/RAM request ve limit eksikleri
- Readiness, liveness ve startup probe eksikleri
- Tek replica workload'lar
- PDB kapsamı
- Anti-affinity / topology spread eksikleri
- `latest` veya etiketsiz container image kullanımı

Rapor öneri niteliğindedir; workload manifestlerini değiştirmez.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `workload_resilience_excluded_namespaces` | `kube-system,kube-public,kube-node-lease` | Denetim dışı namespace'ler |
| `workload_resilience_max_findings` | `300` | Maksimum rapor satırı |

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/34_check_workload_resilience.yml
```

Sistem namespace'lerini de dahil etmek için değişkeni boş string olarak verin.

Resmi referanslar: [Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/), [PodDisruptionBudget](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
