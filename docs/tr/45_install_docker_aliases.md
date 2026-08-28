---
lang: tr
title: "45 · install_docker_aliases"
parent: Playbook Kılavuzları
nav_order: 45
---

# 45_install_docker_aliases.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Amaç

Docker ve Compose alias paketini kurar veya kaldırır. Ortak model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

Orijinal `dprune='docker system prune -af --volumes'` **sessiz alias olarak eklenmedi**. `dprune --yes` onayı olmayan çağrı hiçbir şey silmez.

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/45_install_docker_aliases.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/45_install_docker_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Alias ve fonksiyonlar

| Ad | Ne yapar |
|---|---|
| `d` `dps` `dpsa` `di` | docker / ps / ps -a / images |
| `drm` `drmi` `dex` `dlog` | rm / rmi / exec -it / logs -f |
| `dstats` `dnet` `dvol` | stats / network ls / volume ls |
| `dcu` `dcd` `dcl` `dcr` `dcps` `dcb` `dcpull` | compose kısayolları |
| `dprune --yes` | `docker system prune -af --volumes` (onaysız çalışmaz) |
| `dsh` / `dbash` / `dlogn` | container shell / son N log |

Cluster imaj temizliği için [18_prune_unused_images](18_prune_unused_images.md) daha güvenli bir aday listesi sunar.
