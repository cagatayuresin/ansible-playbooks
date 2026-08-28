---
lang: tr
title: "33 · check_upgrade_readiness"
parent: Playbook Kılavuzları
nav_order: 33
---

# 33_check_upgrade_readiness.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Kubernetes](https://img.shields.io/badge/Kubernetes-Upgrade_Readiness-326CE5?style=flat)

## Amaç

Kubernetes yükseltmesinden önce aşağıdaki engelleri tek raporda kontrol eder:

- API server ve kubelet sürüm uyumu
- Node `Ready` / cordon durumu
- Minor atlama ve downgrade
- Drain'i engelleyebilecek PDB'ler
- `failurePolicy=Fail` admission webhook'ları
- API server deprecated API metriği
- Son etcd yedeğinin yaşı
- etcd/root disk doluluğu

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `upgrade_readiness_target_version` | boş | Hedef `X.Y.Z`; boşsa hedefe özel kontroller atlanır |
| `upgrade_readiness_backup_directory` | `/var/backups/etcd` | Yedek dizini |
| `upgrade_readiness_max_backup_age_hours` | `24` | Maksimum yedek yaşı |
| `upgrade_readiness_max_disk_percent` | `85` | Disk uyarı eşiği |
| `upgrade_readiness_fail_on_blockers` | `true` | Engelde playbook'u başarısız yapar |

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/33_check_upgrade_readiness.yml \
  --extra-vars 'upgrade_readiness_target_version=1.34.3'
```

Bu playbook başarılı olduktan sonra `06_update_k8s_services.yml` çalıştırılmalıdır.

Resmi referanslar: [kubeadm cluster upgrade](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/), [Kubernetes deprecation policy](https://kubernetes.io/docs/reference/using-api/deprecation-policy/)
