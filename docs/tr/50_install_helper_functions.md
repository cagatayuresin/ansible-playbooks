---
lang: tr
title: "50 · install_helper_functions"
parent: Playbook Kılavuzları
nav_order: 50
---

# 50_install_helper_functions.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Amaç

Disk, port, yedek ve arşiv yardımcı fonksiyonlarını kurar veya kaldırır. Ortak model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/50_install_helper_functions.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/50_install_helper_functions.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Fonksiyonlar

| Ad | Ne yapar |
|---|---|
| `duh [yol]` | `du -h --max-depth=1` büyükten küçüğe |
| `whoport <port>` | `lsof -i :port` (sudo) |
| `ipinfo [ip]` | ipinfo.io; argümansız kendi dış IP |
| `bak <dosya>` | `dosya.bak.YYYYMMDD_HHMMSS` kopyası |
| `mkcd <dir>` | mkdir -p ve cd |
| `waitport <host> <port> [sn]` | Port açılana kadar bekle (varsayılan 30s) |
| `extract <arşiv>` | tar/zip/gz/bz2 aç |

`ipinfo` dış ağa çıkar. Air-gap host'ta başarısız olması beklenen davranıştır.
