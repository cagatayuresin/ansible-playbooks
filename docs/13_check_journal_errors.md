---
title: "13 · check_journal_errors"
parent: Playbook Kılavuzları
nav_order: 13
---

# 13_check_journal_errors.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Amaç

DevOps / SRE teşhisi için her node’da `journalctl` ile:

1. **Kernel** hata logları (`err` ve üzeri)
2. **Kernel** uyarıları (`warning`)
3. **Sistem genel** hata logları (tüm systemd unit’leri, `err` ve üzeri)
4. **Bu boot** içindeki kernel hataları

salt-okunur şekilde toplar ve raporlar. Sistemi değiştirmez.

[10_check_system_health](10_check_system_health.md) genel sağlık özetidir; bu playbook log seviyesinde “ne kırıldı / ne uyarıyor” arar.

## Çoklu makine çıktısı

Her host raporunun **ilk satırı** makine kimliğidir:

```text
################################################################################
# HOST: 192.168.1.21
# hostname: worker1
# aralık: 24 hours ago | satır limiti/bölüm: 80
################################################################################
```

`HOST` = inventory’deki adres/isim (`inventory_hostname`), `hostname` = makinenin kendi hostname’i. Birden fazla node’da çalıştırınca hangi bloğun hangi makineye ait olduğu buradan okunur. Ansible zaten `ok: [host]` yazar; uzun raporlarda kaybolmamak için mesajın içine de gömüldü.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `journal_since` | `24 hours ago` | journalctl `--since` değeri |
| `journal_lines` | `80` | Her bölümde en fazla kaç satır |

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/13_check_journal_errors.yml \
  --extra-vars 'journal_since="6 hours ago" journal_lines=120'

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/13_check_journal_errors.yml --limit workers
```

## Gereksinimler

- `hosts: all`
- `become: true` (sudo) — sistem journal’ını okumak için genelde root gerekir; `ansible_become_pass` inventory’de olmalı.
- `systemd-journald` çalışan bir Linux host (Ubuntu/Debian vb.)

## Çalıştırma Komutu

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/13_check_journal_errors.yml
```

## Bölümler nasıl yorumlanır?

### journalctl öncelik seviyeleri

| Seviye | Anlam |
|---|---|
| emerg / alert / crit | Acil / kritik |
| err | Hata — bakılmalı |
| warning | Uyarı — trend / erken sinyal |
| notice / info / debug | Bu playbook’ta filtrelenmez (gürültü) |

### Kernel ERR+

Donanım, sürücü, bellek, dosya sistemi kernel tarafı. Örnek kırmızı bayraklar:

- `Out of memory` / `oom-killer` → bellek baskısı
- `I/O error`, `Buffer I/O error`, `EXT4-fs error` → disk
- `nvme` / `ata` reset, timeout → depolama yolu
- `BUG:`, `Oops`, `general protection fault` → kernel/sürücü ciddi arıza
- `NETDEV WATCHDOG`, NIC reset → ağ

### Kernel WARNING

Henüz çökme değil; thrashing, deprecated API, retry, thermal throttle vb. Tek seferlik gürültü olabilir; **tekrarlayan** aynı uyarılar önemli.

### Sistem ERR+ (tüm unit’ler)

`sshd`, `kubelet`, `containerd`, `cron`, auth, uygulama unit’leri. Kernel boş ama burası doluysa sorun userspace’tedir. Aynı unit’in tekrarlayan fail satırları → `systemctl status <unit>` / `journalctl -u <unit>`.

### Bu boot kernel ERR+

`--since`’ten bağımsız; son reboot’tan beri. “Dün düzeldi ama bu açılıştan beri yine var mı?” sorusu için.

Boş bölümler `-- Bu aralıkta / bu öncelikte kayıt yok --` yazar; bu genelde iyi haberdir.

## Örnek Çıktı (kısaltılmış)

```text
TASK [Journal hata / kernel log raporu] ***
ok: [192.168.1.21] => {
  "msg": [
    "################################################################################\n# HOST: 192.168.1.21\n# hostname: worker1\n# aralık: 24 hours ago | satır limiti/bölüm: 80\n################################################################################",
    "=== Kernel ERR+ (24 hours ago) ===\nYorum: ...\n-- Bu aralıkta / bu öncelikte kayıt yok --",
    "=== Sistem ERR+ tüm unit'ler (24 hours ago) ===\n...\n2026-07-29T10:01:02+00:00 worker1 kubelet[1234]: E0729 ... failed to ..."
  ]
}
```

## Notlar

- Satır limiti aşılırsa en **yeni** kayıtlar gelir (`-n`); daha geriye gitmek için `journal_lines` artır veya `journal_since` genişlet.
- Çok gürültülü ortamlarda önce `--limit` ile şüpheli node’u hedefle.
- Salt-okunur: log silmez, journal’ı truncate etmez.
