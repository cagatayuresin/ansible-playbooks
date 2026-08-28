---
lang: tr
title: "52 · run_sysupdate"
parent: Playbook Kılavuzları
nav_order: 52
---

# 52_run_sysupdate.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Maintenance](https://img.shields.io/badge/Maintenance-Confirm_Lock-F59E0B?style=flat)

## ⚠️ Onay olmadan paket yükseltmez

Varsayılan çalıştırma salt rapor üretir: APT simülasyonu, snap/flatpak envanteri, disk, çöp kutusu sayısı, reboot işareti. Değişiklik için `sysupdate_confirm=true` zorunludur.

Bu, [51](51_install_sysupdate_function.md) ile kurulan interaktif `sysupdate` fonksiyonunun Ansible karşılığıdır. Kubernetes node drain/reboot akışı **değildir**; o iş için [41_patch_and_reboot_nodes](41_patch_and_reboot_nodes.md) kullanın. 52 reboot etmez.

## Onaylı akış

1. Debian ailesinde `apt` update + safe upgrade + autoremove + autoclean
2. Snap varsa `snap refresh` ve disabled revizyon temizliği
3. Flatpak varsa update + unused kaldırma
4. Hedef kullanıcının 30 günden eski thumbnail dosyaları (opsiyonel)
5. Çöp kutusu yalnızca raporlanır, boşaltılmaz
6. Disk ve reboot-required raporu

Debian olmayan host'larda apt adımı atlanır; mesaj 41'e yönlendirir.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `sysupdate_confirm` | `false` | Paket güncellemesini açar |
| `sysupdate_clean_thumbnails` | `true` | Onaylı çalışmada 30g+ thumbnail sil |
| `sysupdate_target_user` | `ansible_user` | Thumbnail/çöp kutusu sahibi |

## Çalıştırma

```bash
# Yalnızca rapor:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/52_run_sysupdate.yml

# Uygula (reboot yok):
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/52_run_sysupdate.yml \
  --limit jump --extra-vars 'sysupdate_confirm=true'
```

Tek node cluster veya worker bakımı için 41'deki drain onaylarını kullanın; 52 iş istasyonu / bastion tarzi host'lar içindir.
