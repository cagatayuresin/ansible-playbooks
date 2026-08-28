---
lang: tr
title: "51 · install_sysupdate_function"
parent: Playbook Kılavuzları
nav_order: 51
---

# 51_install_sysupdate_function.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Amaç

Hedef kullanıcının kabuğuna `sysupdate` fonksiyonunu kurar. Fonksiyon interaktif oturumda apt + snap + flatpak bakımı ve hafif temizlik yapar. Ortak model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

Bu playbook **bakımı çalıştırmaz**; yalnızca fonksiyonu yerleştirir. Uzaktan Ansible ile aynı bakımı uygulamak için [52_run_sysupdate](52_run_sysupdate.md) kullanın. Kubernetes node'larında drain/reboot'lu paket güncellemesi için [41_patch_and_reboot_nodes](41_patch_and_reboot_nodes.md) vardır.

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/51_install_sysupdate_function.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/51_install_sysupdate_function.yml \
  --extra-vars 'shell_aliases_state=absent'
```

Kurulumdan sonra hedef host'ta:

```bash
source ~/.bashrc   # bash login kabuğu; zsh/sh ise ~/.zshrc veya ~/.profile
sysupdate
```

## Fonksiyon ne yapar?

1. Disk kullanımı (önce)
2. `apt update` / `upgrade -y` / `autoremove` / `autoclean`
3. Snap varsa `snap refresh` ve disabled revizyon temizliği
4. Flatpak varsa `flatpak update` ve unused kaldırma
5. 30 günden eski thumbnail önbelleği
6. Çöp kutusu sayısı (boşaltmaz)
7. Süre, disk (sonra), `/var/run/reboot-required` uyarısı

Fonksiyon `sudo` ister. Reboot etmez.
