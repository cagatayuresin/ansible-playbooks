---
lang: tr
title: "53 · remove_shell_aliases"
parent: Playbook Kılavuzları
nav_order: 53
---

# 53_remove_shell_aliases.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Cleanup](https://img.shields.io/badge/Cleanup-All_Packs-6366F1?style=flat)

## Amaç

43–51 ile kurulan **tüm** Ansible alias paketlerini listeler veya onayla tamamen kaldırır.

- Varsayılan: `~/.ansible-shell-aliases/` içindeki paketleri raporlar, silmez.
- `shell_aliases_remove_all_confirm=true`: dizini (ve varsa eski `~/.ansible-zsh-aliases`) siler; login kabuğu rc dosyasındaki `# ANSIBLE MANAGED SHELL ALIASES` bloğunu çıkarır.

Tek paketi geri almak için ilgili 43–51 playbook'unu `shell_aliases_state=absent` ile çalıştırmak yeterlidir. 53 nükleer seçenektir.

Kullanıcının rc dosyasının bloğun dışındaki satırlarına dokunulmaz.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `shell_aliases_remove_all_confirm` | `false` | Tüm paketleri ve rc bloğunu sil |
| `shell_aliases_target_user` | `ansible_user` | Temizlenecek kullanıcı |
| `shell_aliases_rc_files` | login kabuğundan | Bloğun aranacağı ek rc dosyaları |

## Çalıştırma

```bash
# Ne kurulu?
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/53_remove_shell_aliases.yml

# Hepsini kaldır:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/53_remove_shell_aliases.yml \
  --extra-vars 'shell_aliases_remove_all_confirm=true'
```

Temizlikten sonra yeni oturum açın veya rc dosyasını tekrar `source` edin; aksi halde mevcut kabuk hâlâ eski fonksiyonları bellekte tutabilir.
