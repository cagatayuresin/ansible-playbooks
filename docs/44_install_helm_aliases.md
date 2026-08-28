---
lang: en
title: "44 · install_helm_aliases"
parent: Playbook Guides
nav_order: 44
---

# 44_install_helm_aliases.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Purpose

Installs the Helm alias pack as `~/.ansible-shell-aliases/helm.sh`, or removes it with `shell_aliases_state=absent`. Shared model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/44_install_helm_aliases.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/44_install_helm_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Aliases and functions

| Name | What it does |
|---|---|
| `hl` / `hla` | `helm list` / `-A` |
| `hi` `hu` `hui` `hun` | install / upgrade / upgrade --install / uninstall |
| `hr` `hru` `hrl` | repo / repo update / repo list |
| `hs` `hh` `hg` `hgv` `hgm` | status / history / get / values / manifest |
| `ht` `hse` `hdep` | template / search repo / dependency |
| `hrback` | `helm rollback` (release required) |
| `hns` | Releases in the namespace |

`hun` and `hrback` change cluster state.
