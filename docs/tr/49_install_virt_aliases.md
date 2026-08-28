---
lang: tr
title: "49 · install_virt_aliases"
parent: Playbook Kılavuzları
nav_order: 49
---

# 49_install_virt_aliases.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Amaç

libvirt / virt-manager kısayollarını kurar veya kaldırır. Ortak model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md). GUI host'lar (çalışma istasyonu) içindir; Kubernetes node'lara kurmak zorunda değilsiniz.

`vm-on` içindeki zsh'e özgü `&!` yerine taşınabilir `disown` kullanılır.

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/49_install_virt_aliases.yml --limit jump
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/49_install_virt_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Alias ve fonksiyonlar

| Ad | Ne yapar |
|---|---|
| `vm-on` | libvirtd başlat, virt-manager varsa arka planda aç |
| `vm-off` | libvirtd durdur |
| `vm-status` `vm-list` `vm-net` `vm-pool` | servis / VM / ağ / pool listesi |
| `vm-start` `vm-stop` `vm-info` | virsh start / shutdown / dominfo |
| `vm-destroy --yes <ad>` | `virsh destroy` (onaysız çalışmaz) |
