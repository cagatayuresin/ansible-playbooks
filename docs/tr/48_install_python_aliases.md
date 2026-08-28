---
lang: tr
title: "48 · install_python_aliases"
parent: Playbook Kılavuzları
nav_order: 48
---

# 48_install_python_aliases.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Amaç

Python / venv kısayollarını kurar veya kaldırır. Ortak model: [43_install_kubectl_aliases](43_install_kubectl_aliases.md).

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/48_install_python_aliases.yml
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/48_install_python_aliases.yml \
  --extra-vars 'shell_aliases_state=absent'
```

## Alias ve fonksiyonlar

| Ad | Ne yapar |
|---|---|
| `py` / `pip` | python3 / pip3 |
| `venv [dir]` | `python3 -m venv` ve activate (varsayılan `.venv`) |
| `activate [dir]` | Mevcut venv'i aktive et |
| `pyclean [yol]` | `__pycache__` ve `.pyc` temizliği |
| `pyserve [port]` | `python3 -m http.server` (varsayılan 8000) |
| `pipoutdated` | `pip3 list --outdated` |
