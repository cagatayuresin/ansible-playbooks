---
lang: en
title: "50 · install_helper_functions"
parent: Playbook Guides
nav_order: 50
---

# 50_install_helper_functions.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Purpose

Installs or removes disk, port, backup, and archive helper functions. Shared model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/50_install_helper_functions.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/50_install_helper_functions.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Functions

| Name | What it does |
|---|---|
| `duh [path]` | `du -h --max-depth=1` largest first |
| `whoport <port>` | `lsof -i :port` (sudo) |
| `ipinfo [ip]` | ipinfo.io; own external IP if no argument |
| `bak <file>` | Copy to `file.bak.YYYYMMDD_HHMMSS` |
| `mkcd <dir>` | mkdir -p and cd |
| `waitport <host> <port> [sec]` | Wait until the port opens (default 30s) |
| `extract <archive>` | Extract tar/zip/gz/bz2 |

`ipinfo` reaches the external network. Failure on an air-gapped host is expected.
