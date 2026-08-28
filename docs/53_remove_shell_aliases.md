---
lang: en
title: "53 · remove_shell_aliases"
parent: Playbook Guides
nav_order: 53
---

# 53_remove_shell_aliases.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Cleanup](https://img.shields.io/badge/Cleanup-All_Packs-6366F1?style=flat)

## Purpose

Lists or, with confirmation, fully removes **all** Ansible alias packs installed by 43–51.

- Default: reports packs under `~/.ansible-shell-aliases/`, does not delete.
- `shell_aliases_remove_all_confirm=true`: deletes the directory (and any leftover `~/.ansible-zsh-aliases`) and removes the `# ANSIBLE MANAGED SHELL ALIASES` block from the login shell rc file.

To revert a single pack, run the matching 43–51 playbook with `shell_aliases_state=absent`. 53 is the nuclear option.

Lines outside that block in the user’s rc file are left untouched.

## Variables

| Variable | Default | Description |
|---|---|---|
| `shell_aliases_remove_all_confirm` | `false` | Delete all packs and the rc block |
| `shell_aliases_target_user` | `ansible_user` | User to clean |
| `shell_aliases_rc_files` | from login shell | Extra rc files to search when removing the block |

## How to run

```bash
# What is installed?
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/53_remove_shell_aliases.yml

# Remove everything:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/53_remove_shell_aliases.yml \
  --extra-vars 'shell_aliases_remove_all_confirm=true'
```

After cleanup, open a new session or `source` the rc file again; otherwise the current shell may still keep old functions in memory.
