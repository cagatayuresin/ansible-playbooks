---
lang: tr
title: "44 · install_helm_aliases"
parent: Playbook Kılavuzları
nav_order: 44
---

# 44_install_helm_aliases.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Amaç

Helm alias paketini `~/.ansible-shell-aliases/helm.sh` olarak kurar veya `shell_aliases_state=absent` ile kaldırır. Ortak model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/44_install_helm_aliases.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/44_install_helm_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Alias ve fonksiyonlar

| Ad | Ne yapar |
|---|---|
| `hl` / `hla` | `helm list` / `-A` |
| `hi` `hu` `hui` `hun` | install / upgrade / upgrade --install / uninstall |
| `hr` `hru` `hrl` | repo / repo update / repo list |
| `hs` `hh` `hg` `hgv` `hgm` | status / history / get / values / manifest |
| `ht` `hse` `hdep` | template / search repo / dependency |
| `hrback` | `helm rollback` (release zorunlu) |
| `hns` | Namespace'teki release'ler |

`hun` ve `hrback` cluster state'ini değiştirir.
