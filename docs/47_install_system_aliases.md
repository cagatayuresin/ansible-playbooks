---
lang: en
title: "47 · install_system_aliases"
parent: Playbook Guides
nav_order: 47
---

# 47_install_system_aliases.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Purpose

Installs or removes shell / system shortcuts (original SYSTEM, FILE/TEXT, and APT sections). Shared model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

The original `alias install='sudo apt install -y'` is **intentionally omitted**. Overriding the generic `install` name is dangerous; `aptin` / `aptsearch` / `aptrm` are provided instead.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/47_install_system_aliases.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/47_install_system_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Aliases and functions

| Name | What it does |
|---|---|
| `ll` `la` `..` `...` `....` | list / directory |
| `mkdir` `df` `du` `free` | `-pv` / human-readable units |
| `ports` `ipa` `path` `myip` | ss / ip -br a / PATH one per line / external IP |
| `grep` `h` `hg` `c` | colored grep / history |
| `sctl` `sctlu` `jctl` `jctlf` | systemctl / journalctl |
| `reload` | sources `~/.bashrc`, `~/.zshrc`, or `~/.profile` for the current shell |
| `zshrc` `bashrc` `als` | edit rc / list installed Ansible packs |
| `aptin` `aptsearch` `aptrm` | apt install -y / search / remove |
