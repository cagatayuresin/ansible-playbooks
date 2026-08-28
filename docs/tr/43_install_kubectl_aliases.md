---
lang: tr
title: "43 · install_kubectl_aliases"
parent: Playbook Kılavuzları
nav_order: 43
---

# 43_install_kubectl_aliases.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Reversible](https://img.shields.io/badge/Cleanup-Reversible-10B981?style=flat)

## Amaç

Hedef kullanıcının ev dizinine **Ansible yönetimli** kubectl alias/fonksiyon paketini kurar. Paketler bash uyumlu `.sh` dosyalarıdır. Kullanıcının mevcut rc dosyası yeniden yazılmaz; `getent passwd` ile bulunan **login kabuğunun** rc dosyasına işaretli bir kaynak bloğu eklenir (bash → `~/.bashrc`, zsh → `~/.zshrc`, dash/sh → `~/.profile`).

Aynı kurulum modeli 44–51 playbook'larında da kullanılır. Tek paketi geri almak için bu playbook `shell_aliases_state=absent` ile çalıştırılır; hepsini silmek için [53_remove_shell_aliases](53_remove_shell_aliases.md) kullanılır.

## Kurulum modeli

| Parça | Yol |
|---|---|
| Paket dosyası | `~/.ansible-shell-aliases/<paket>.sh` |
| Kaynak bloğu | Login kabuğunun rc dosyasında `# BEGIN/END ANSIBLE MANAGED SHELL ALIASES` |
| Sahiplik | `shell_aliases_target_user` (varsayılan: `ansible_user`) |

Geri alma:

1. İlgili `.sh` dosyası silinir.
2. Dizinde başka paket kalmazsa dizin ve rc bloğu da kaldırılır.
3. Kullanıcının rc dosyasının geri kalanına dokunulmaz.

Önceki `~/.ansible-zsh-aliases` kurulumu bir sonraki present / toplu absent çalışmasında temizlenir.

Yeni SSH oturumu açın veya playbook'un bildirdiği rc dosyasını source edin (Ubuntu sunucularda genelde `~/.bashrc`).

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `shell_aliases_state` | `present` | `present` kurar, `absent` bu paketi kaldırır |
| `shell_aliases_target_user` | `ansible_user` | Alias'ların yazılacağı kullanıcı |
| `shell_aliases_rc_files` | login kabuğundan | rc dosyalarını elle seçmek için (ör. `['.bashrc']`) |

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/43_install_kubectl_aliases.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/43_install_kubectl_aliases.yml \
  --limit master --extra-vars 'shell_aliases_state=absent'
```

`--check --diff` ile rc bloğu ve dosya kopyası önizlenir.

## Alias ve fonksiyonlar

| Ad | Ne yapar |
|---|---|
| `kgpa` / `kgpaw` | Tüm namespace pod listesi (wide) |
| `kgpw` / `kgpwatch` | Pod listesi / watch |
| `kgn` | Node'lar wide |
| `kga` / `kgaa` | `get all` |
| `kgsec(a)` `kgcm(a)` `kging(a)` | Secret, ConfigMap, Ingress |
| `kgpv` `kgpvc(a)` `kgsvc(a)` | PV / PVC / Service |
| `kgd(a)` `kgds(a)` `kgsts(a)` `kgjob` | Deploy, DS, STS, Job/CronJob |
| `kge` / `kgea` | Event'ler zamana göre |
| `ktop` `ktopa` `ktopn` | metrics-server top |
| `klogs` `kex` `kdesc` `kdel` `kapply` `kdiff` `kpf` | Günlük iş |
| `kctx` / `kns` | kubectx/kubens varsa onlar, yoksa kubectl config |
| `ksh` / `kbash` | Pod shell |
| `klog` | `klog pod [satır] [ns]` |
| `knp` / `kfail` | Namespace pod'ları / Running olmayanlar |
| `kroll` `krollstat` `krollhist` | Rollout |
| `kdrain` | Node drain (ad zorunlu) |
| `kcordon` / `kuncordon` | Cordon |

`kdrain` ve `kdel` cluster'ı değiştirir; alias yalnızca kısayoldur.

## Notlar

- `hosts: all` — `--limit` ile daraltın.
- `kubectl` bu playbook ile kurulmaz; hedefte zaten olmalıdır.
- `kubectx` / `kubens` opsiyoneldir.
