# 08_check_server_time.yml - Kullanım Kılavuzu

## Amaç

Bu playbook, sunucunun saat/saat dilimi bilgisini (`timedatectl`) raporlar ve hangi zaman senkronizasyon servisinin kullanıldığını (chrony, systemd-timesyncd, ntpd — hangisi kuruluysa) **dinamik olarak** tespit eder. Sabit bir servis adı varsayılmaz; `service_facts` ile sistemdeki tüm servisler taranıp `chrony|systemd-timesyncd|ntpd` desenine uyanlar bulunur.

## Gereksinimler

- `hosts: all` — her node'da çalışır.
- Servis keşfi Ansible'ın yerleşik `service_facts` modülüyle yapılır, ek bir collection gerekmez.

## Çalıştırma Komutu

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/08_check_server_time.yml
```

## Örnek Çıktı

```text
TASK [Ping pong] ***************************************************************
ok: [203.0.113.10]

TASK [Zaman senkronizasyon servis durumu (Çalışma Şartı: ilgili servis bulunmalı)] ***
ok: [203.0.113.10] => (item=systemd-timesyncd.service) => {
    "msg": "systemd-timesyncd.service -> durum: running, açılışta aktif: enabled"
}

TASK [Zaman ve saat dilimi raporu] **********************************************
ok: [203.0.113.10] => {
    "msg": "               Local time: Tue 2026-07-28 11:31:07 UTC\n           Universal time: Tue 2026-07-28 11:31:07 UTC\n                 RTC time: Tue 2026-07-28 11:31:07\n                Time zone: Etc/UTC (UTC, +0000)\nSystem clock synchronized: yes\n              NTP service: active\n          RTC in local TZ: no"
}
```
