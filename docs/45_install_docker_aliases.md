---
lang: en
title: "45 · install_docker_aliases"
parent: Playbook Guides
nav_order: 45
---

# 45_install_docker_aliases.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Purpose

Installs or removes the Docker and Compose alias pack. Shared model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

The original `dprune='docker system prune -af --volumes'` was **not added as a silent alias**. Calling `dprune` without `--yes` deletes nothing.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/45_install_docker_aliases.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/45_install_docker_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Aliases and functions

| Name | What it does |
|---|---|
| `d` `dps` `dpsa` `di` | docker / ps / ps -a / images |
| `drm` `drmi` `dex` `dlog` | rm / rmi / exec -it / logs -f |
| `dstats` `dnet` `dvol` | stats / network ls / volume ls |
| `dcu` `dcd` `dcl` `dcr` `dcps` `dcb` `dcpull` | Compose shortcuts |
| `dprune --yes` | `docker system prune -af --volumes` (does not run without confirmation) |
| `dsh` / `dbash` / `dlogn` | Container shell / last N log lines |

For cluster image cleanup, [18_prune_unused_images](18_prune_unused_images.md) offers a safer candidate list.
