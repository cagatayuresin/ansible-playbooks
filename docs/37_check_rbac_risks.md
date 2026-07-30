---
title: "37 · check_rbac_risks"
parent: Playbook Kılavuzları
nav_order: 37
---

# 37_check_rbac_risks.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Security](https://img.shields.io/badge/Security-RBAC-7C3AED?style=flat)

## Amaç

RBAC kaynaklarında yüksek riskli yetkileri raporlar:

- `cluster-admin` binding'leri
- `system:masters`, `system:unauthenticated` ve geniş authenticated binding'leri
- Wildcard verb/resource kuralları
- `bind`, `escalate`, `impersonate`
- Secret, pod exec/attach ve service account token yetkileri
- Varsayılan ServiceAccount token automount durumu

`system:` ile başlayan Kubernetes yerleşik ClusterRole kuralları rol analizi sırasında atlanır; binding'leri yine raporlanır.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `rbac_risks_excluded_namespaces` | `kube-system,kube-public,kube-node-lease` | Namespace kapsamlı analiz istisnaları |
| `rbac_risks_max_findings` | `400` | Maksimum bulgu |

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/37_check_rbac_risks.yml
```

Resmi referans: [Kubernetes RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
