---
lang: en
title: "49 · install_virt_aliases"
parent: Playbook Guides
nav_order: 49
---

# 49_install_virt_aliases.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Purpose

Installs or removes libvirt / virt-manager shortcuts. Shared model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md). Intended for GUI hosts (workstations); you do not have to install this on Kubernetes nodes.

`vm-on` uses portable `disown` instead of zsh-specific `&!`.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/49_install_virt_aliases.yml --limit jump
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/49_install_virt_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Aliases and functions

| Name | What it does |
|---|---|
| `vm-on` | Start libvirtd; open virt-manager in the background if present |
| `vm-off` | Stop libvirtd |
| `vm-status` `vm-list` `vm-net` `vm-pool` | Service / VM / network / pool list |
| `vm-start` `vm-stop` `vm-info` | virsh start / shutdown / dominfo |
| `vm-destroy --yes <name>` | `virsh destroy` (does not run without confirmation) |
