---
lang: tr
title: "47 · install_system_aliases"
parent: Playbook Kılavuzları
nav_order: 47
---

# 47_install_system_aliases.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Amaç

Kabuk / sistem kısayollarını kurar veya kaldırır (orijinal “SİSTEM”, “DOSYA/METİN” ve APT bölümleri). Ortak model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

Orijinal `alias install='sudo apt install -y'` **bilinçli olarak yok**. Genel `install` adını ezmek tehlikelidir; yerine `aptin` / `aptsearch` / `aptrm` vardır.

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/47_install_system_aliases.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/47_install_system_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Alias ve fonksiyonlar

| Ad | Ne yapar |
|---|---|
| `ll` `la` `..` `...` `....` | liste / dizin |
| `mkdir` `df` `du` `free` | `-pv` / insan okunur birimler |
| `ports` `ipa` `path` `myip` | ss / ip -br a / PATH satır satır / dış IP |
| `grep` `h` `hg` `c` | renkli grep / history |
| `sctl` `sctlu` `jctl` `jctlf` | systemctl / journalctl |
| `reload` | mevcut kabuğa göre `~/.bashrc`, `~/.zshrc` veya `~/.profile` |
| `zshrc` `bashrc` `als` | rc düzenle / kurulu Ansible paketlerini listele |
| `aptin` `aptsearch` `aptrm` | apt install -y / search / remove |
