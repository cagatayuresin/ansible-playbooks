---
lang: en
title: "48 · install_python_aliases"
parent: Playbook Guides
nav_order: 48
---

# 48_install_python_aliases.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Purpose

Installs or removes Python / venv shortcuts. Shared model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/48_install_python_aliases.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/48_install_python_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Aliases and functions

| Name | What it does |
|---|---|
| `py` / `pip` | python3 / pip3 |
| `venv [dir]` | `python3 -m venv` and activate (default `.venv`) |
| `activate [dir]` | Activate an existing venv |
| `pyclean [path]` | Clean `__pycache__` and `.pyc` |
| `pyserve [port]` | `python3 -m http.server` (default 8000) |
| `pipoutdated` | `pip3 list --outdated` |
