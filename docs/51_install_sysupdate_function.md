---
lang: en
title: "51 · install_sysupdate_function"
parent: Playbook Guides
nav_order: 51
---

# 51_install_sysupdate_function.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Purpose

Installs the `sysupdate` function into the target user’s shell. In an interactive session the function runs apt + snap + flatpak maintenance and light cleanup. Shared model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

This playbook **does not run maintenance**; it only places the function. To apply the same maintenance remotely with Ansible, use [52_run_sysupdate](52_run_sysupdate.md). For package updates on Kubernetes nodes with drain/reboot, use [41_patch_and_reboot_nodes](41_patch_and_reboot_nodes.md).

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/51_install_sysupdate_function.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/51_install_sysupdate_function.yml \
  --extra-vars 'shell_aliases_state=absent'
```

After install, on the target host:

```bash
source ~/.bashrc   # bash login shell; use ~/.zshrc or ~/.profile if that is the login shell
sysupdate
```

## What the function does

1. Disk usage (before)
2. `apt update` / `upgrade -y` / `autoremove` / `autoclean`
3. If snap is present: `snap refresh` and cleanup of disabled revisions
4. If Flatpak is present: `flatpak update` and unused removal
5. Thumbnail cache older than 30 days
6. Trash count (does not empty it)
7. Duration, disk (after), `/var/run/reboot-required` warning

The function asks for `sudo`. It does not reboot.
