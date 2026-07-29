# 09_set_server_timezone.yml - Kullanım Kılavuzu

## Amaç

Bu playbook, sunucunun saat dilimini `Europe/Istanbul` olarak ayarlar, [08_check_server_time.yml](../playbooks/08_check_server_time.yml) ile bulunan zaman senkronizasyon servislerini (chrony/systemd-timesyncd/ntpd — hangisi kuruluysa) aktif ve açılışta otomatik başlayacak (enabled) hale getirir, ardından `timedatectl` çıktısıyla sonucu doğrular. Tek başına çalıştırıldığında önce `08_check_server_time.yml`'i (`import_playbook` ile) çalıştırarak değişiklik öncesi mevcut durumu raporlar; bulunan servis listesi (`time_services` fact'i) ikinci play'de servisleri aktifleştirmek için tekrar kullanılır.

Not: `RTC time` alanının `Local time`'dan farklı görünmesi normaldir — Linux donanım saatini (RTC) genelde UTC'de tutar, `Local time` ise saat dilimi farkı eklenerek hesaplanır. `RTC time` ile `Universal time` alanlarının eşleşmesi beklenen/doğru davranıştır.

⚠️ Bu playbook diğerlerinin aksine **salt-okunur bir kontrol değildir** — hedef sunucunun sistem saat dilimini gerçekten değiştirir.

## Gereksinimler

- `hosts: all` — her node'da çalışır.
- `community.general` collection'ı gereklidir (`community.general.timezone` modülü).
- `hosts: all` yerine belirli bir host/grup için `--limit` kullanılması önerilir.
- **Saat dilimini ayarlayan görev `become: true` (sudo) ile çalışır.** `timedatectl set-timezone`, `org.freedesktop.timedate1` üzerinden root yetkisi gerektiren bir D-Bus/polkit işlemidir; sudo olmadan interaktif olmayan bir SSH oturumunda polkit onayı hiç gelmediği için istek "Connection timed out" ile başarısız olur. Diğer playbook'lardaki salt-okunur komutların aksine, bu gerçek bir sistem değişikliği olduğu için sudo gerekir.

## Çalıştırma Komutu

```bash
# Önce ne değişeceğini görmek için (sistem üzerinde değişiklik yapmadan):
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/09_set_server_timezone.yml --check --diff

# Gerçekten uygulamak için:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/09_set_server_timezone.yml

# Belirli bir host ile sınırlamak için:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/09_set_server_timezone.yml --limit master
```

## Örnek Çıktı

```text
PLAY [Sunucu Zamanı ve Saat Dilimi Raporu] *************************************
... (08'in çıktısı - değişiklik öncesi durum) ...

PLAY [Set Server Timezone to Europe/Istanbul] **********************************

TASK [Zaman dilimini Europe/Istanbul olarak ayarla] ****************************
changed: [203.0.113.10]

TASK [Zaman dilimi ayarlama sonucu] *********************************************
ok: [203.0.113.10] => {
    "msg": "Timezone Europe/Istanbul olarak değiştirildi"
}

TASK [Zaman senkronizasyon servisi aktifleştirme raporu] ************************
ok: [203.0.113.10] => (item=systemd-timesyncd.service) => {
    "msg": "systemd-timesyncd.service -> zaten aktif ve enabled idi"
}

TASK [Doğrulama raporu] *********************************************************
ok: [203.0.113.10] => {
    "msg": "               Local time: Tue 2026-07-28 14:xx:xx +03\n...\n                Time zone: Europe/Istanbul (+03, +0300)\n..."
}
```
