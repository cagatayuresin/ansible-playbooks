---
lang: tr
title: "46 · install_git_aliases"
parent: Playbook Kılavuzları
nav_order: 46
---

# 46_install_git_aliases.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Amaç

Git alias paketini kurar veya kaldırır. Ortak model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

`git commit --amend` geçmişi yeniden yazar; `gca` sessiz alias değil, `gca --yes` ister.

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/46_install_git_aliases.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/46_install_git_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Alias ve fonksiyonlar

| Ad | Ne yapar |
|---|---|
| `gs` / `gss` | status / kısa status |
| `gp` `gpu` `gf` | pull / push / fetch --all --prune |
| `gco` `gcb` `gsw` `gswc` | checkout / yeni dal / switch |
| `gba` `gl` `gla` | branch -a / log grafiği |
| `gd` `gds` `gcm` | diff / staged diff / commit -m |
| `gst` `gstp` | stash / stash pop |
| `gca --yes` | `git commit --amend` |
| `gundo` | `git reset --soft HEAD~1` |
| `gcurrent` / `gsync` | aktif dal / fetch+ff-only pull |
