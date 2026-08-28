---
lang: en
title: "46 · install_git_aliases"
parent: Playbook Guides
nav_order: 46
---

# 46_install_git_aliases.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Purpose

Installs or removes the Git alias pack. Shared model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

`git commit --amend` rewrites history; `gca` is not a silent alias and requires `gca --yes`.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/46_install_git_aliases.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/46_install_git_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Aliases and functions

| Name | What it does |
|---|---|
| `gs` / `gss` | status / short status |
| `gp` `gpu` `gf` | pull / push / fetch --all --prune |
| `gco` `gcb` `gsw` `gswc` | checkout / new branch / switch |
| `gba` `gl` `gla` | branch -a / log graph |
| `gd` `gds` `gcm` | diff / staged diff / commit -m |
| `gst` `gstp` | stash / stash pop |
| `gca --yes` | `git commit --amend` |
| `gundo` | `git reset --soft HEAD~1` |
| `gcurrent` / `gsync` | current branch / fetch+ff-only pull |
