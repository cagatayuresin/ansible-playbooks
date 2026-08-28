---
lang: tr
title: "32 · verify_etcd_backup"
parent: Playbook Kılavuzları
nav_order: 32
---

# 32_verify_etcd_backup.yml - Kullanım Kılavuzu

![Conditional](https://img.shields.io/badge/State-Read--Only_Default-F59E0B?style=flat) ![etcd](https://img.shields.io/badge/Datastore-etcd-419EDA?style=flat)

## Amaç

`/var/backups/etcd` altındaki en yeni snapshot'ı bulup yaş, boyut, SHA256 ve dosya izinlerini raporlar. `etcdutl` veya `etcdctl snapshot status` ile bütünlüğü doğrular. İsteğe bağlı restore testi yalnızca geçici bir dizine yapılır ve canlı etcd verisine dokunmaz.

## Gereksinimler

- İlk control-plane üzerinde `etcdutl` veya `etcdctl`
- Yedek dizinine root erişimi
- Snapshot adı `etcd_snapshot_*` kalıbıyla başlamalıdır

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `etcd_backup_directory` | `/var/backups/etcd` | Snapshot dizini |
| `etcd_backup_max_age_hours` | `24` | Bundan eski yedek kritik kabul edilir |
| `etcd_backup_restore_test` | `false` | İzole restore testi yapar |
| `etcd_backup_verify_fail_on_error` | `true` | Kritik bulguda playbook'u başarısız yapar |

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/32_verify_etcd_backup.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/32_verify_etcd_backup.yml \
  --extra-vars 'etcd_backup_restore_test=true'
```

Restore testi `mktemp` ile oluşturulan izole dizinde çalışır; canlı member dizini veya manifestler değiştirilmez.

Resmi referans: [etcd Disaster Recovery](https://etcd.io/docs/v3.7/op-guide/recovery/)
