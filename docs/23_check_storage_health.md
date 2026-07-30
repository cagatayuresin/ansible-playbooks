---
title: "23 · check_storage_health"
parent: Playbook Kılavuzları
nav_order: 23
---

# 23_check_storage_health.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Amaç

Her host’ta salt-okunur depolama raporu:

1. **df -hT** — gerçek dosya sistemleri
2. **df -i** — inode kullanımı
3. **containerd/crictl / docker** disk kullanımı + imaj toplam boyutu
4. **kubectl** varsa: PVC / PV / StorageClass + Bound olmayan PVC’ler

## Host kapsamı

`hosts: all` — disk/inode her node’da localdir. PV/PVC bilgisi kubectl erişimi olan node’da dolar (genelde control-plane); worker’da kubectl yoksa o bölüm atlanır.

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/23_check_storage_health.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/23_check_storage_health.yml --limit workers
```

## Yorumlama

| Bulgu | Aksiyon |
|---|---|
| Disk Use% yüksek | Log / image birikimi; 17–18 |
| IUse% yüksek | Çok sayıda küçük dosya / layer |
| PVC Pending | StorageClass / provisioner / quota |
| PV Released/Failed | Manuel temizlik / reclaim policy |

## Notlar

- Script: `playbooks/files/storage_health_check.py`
- `become: true` (du / runtime dizinleri)
- Cluster’ı değiştirmez.
