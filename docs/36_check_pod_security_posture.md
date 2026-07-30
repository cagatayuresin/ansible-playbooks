---
title: "36 · check_pod_security_posture"
parent: Playbook Kılavuzları
nav_order: 36
---

# 36_check_pod_security_posture.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Security](https://img.shields.io/badge/Security-Pod_Posture-7C3AED?style=flat)

## Amaç

Namespace Pod Security Admission etiketlerini ve çalışan pod'ların güvenlik bağlamlarını inceler:

- `privileged`, root ve privilege escalation
- `hostNetwork`, `hostPID`, `hostIPC`, `hostPath`, `hostPort`
- Ek Linux capability'leri
- Eksik veya `Unconfined` seccomp
- Salt-okunur olmayan root filesystem
- `enforce`, `audit`, `warn` namespace etiketleri

Bu kontrol sezgiseldir; Kubernetes admission controller'ın tam politika evaluator'ı değildir.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `pod_security_excluded_namespaces` | `kube-system,kube-public,kube-node-lease` | Sistem pod'larını varsayılan rapordan çıkarır |
| `pod_security_max_findings` | `400` | Maksimum bulgu |

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/36_check_pod_security_posture.yml
```

Resmi referans: [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
