---
lang: en
title: "43 · install_kubectl_aliases"
parent: Playbook Guides
nav_order: 43
---

# 43_install_kubectl_aliases.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Purpose

Installs an **Ansible-managed** kubectl alias/function pack into the target user’s home. Pack files are bash-compatible `.sh` snippets. The user’s existing rc file is not rewritten; a marked source block is appended to the **login shell** rc file from `getent passwd` (bash → `~/.bashrc`, zsh → `~/.zshrc`, dash/sh → `~/.profile`).

The same install model is used by playbooks 44–51. To revert a single pack, run this playbook with `shell_aliases_state=absent`; to remove them all, use [53_remove_shell_aliases](53_remove_shell_aliases.md).

## Install model

| Part | Path |
|---|---|
| Pack file | `~/.ansible-shell-aliases/<pack>.sh` |
| Source block | `# BEGIN/END ANSIBLE MANAGED SHELL ALIASES` in the login shell’s rc file |
| Ownership | `shell_aliases_target_user` (default: `ansible_user`) |

Reverting:

1. The matching `.sh` file is deleted.
2. If no other packs remain in the directory, the directory and rc block are removed too.
3. The rest of the user’s rc file is left untouched.

A previous `~/.ansible-zsh-aliases` install is migrated away on the next present/absent-all run.

Open a new SSH session, or source the rc file that the playbook reports (usually `~/.bashrc` on Ubuntu servers).

## Variables

| Variable | Default | Description |
|---|---|---|
| `shell_aliases_state` | `present` | `present` installs, `absent` removes this pack |
| `shell_aliases_target_user` | `ansible_user` | User whose aliases are written |
| `shell_aliases_rc_files` | from login shell | Override rc files (e.g. `['.bashrc']`) |

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/43_install_kubectl_aliases.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/43_install_kubectl_aliases.yml \
  --limit master --extra-vars 'shell_aliases_state=absent'
```

`--check --diff` previews the rc block and the file copy.

## Aliases and functions

| Name | What it does |
|---|---|
| `kgpa` / `kgpaw` | All-namespace pod list (wide) |
| `kgpw` / `kgpwatch` | Pod list / watch |
| `kgn` | Nodes wide |
| `kga` / `kgaa` | `get all` |
| `kgsec(a)` `kgcm(a)` `kging(a)` | Secret, ConfigMap, Ingress |
| `kgpv` `kgpvc(a)` `kgsvc(a)` | PV / PVC / Service |
| `kgd(a)` `kgds(a)` `kgsts(a)` `kgjob` | Deploy, DS, STS, Job/CronJob |
| `kge` / `kgea` | Events by time |
| `ktop` `ktopa` `ktopn` | metrics-server top |
| `klogs` `kex` `kdesc` `kdel` `kapply` `kdiff` `kpf` | Day-to-day work |
| `kctx` / `kns` | kubectx/kubens if present, otherwise kubectl config |
| `ksh` / `kbash` | Pod shell |
| `klog` | `klog pod [lines] [ns]` |
| `knp` / `kfail` | Namespace pods / not Running |
| `kroll` `krollstat` `krollhist` | Rollout |
| `kdrain` | Node drain (name required) |
| `kcordon` / `kuncordon` | Cordon |

`kdrain` and `kdel` change the cluster; the alias is only a shortcut.

## Notes

- `hosts: all` — narrow with `--limit`.
- `kubectl` is not installed by this playbook; it must already be on the target.
- `kubectx` / `kubens` are optional.
