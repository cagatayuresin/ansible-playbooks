---
title: "10 · check_system_health"
parent: Playbook Kılavuzları
nav_order: 10
---

# 10_check_system_health.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Amaç

Bu playbook, bir sunucunun genel sistem sağlığını raporlar:

- OS (dağıtım/sürüm), kernel sürümü, uptime
- CPU çekirdek sayısı
- Load average (1/5/15 dk) ve çekirdek başına normalize edilmiş 1 dakikalık yük
- Çalışma kuyruğu (o an çalışan/toplam process sayısı, `/proc/loadavg`'tan)
- Zombie (defunct) process sayısı
- Sanallaştırma tespiti: `ansible_facts` (rol/tip) + `systemd-detect-virt` + `dmidecode` (üretici/ürün/BIOS sürümü) — hangi hypervisor üzerinde çalıştığını (Hyper-V, VMware, KVM, vb.) dinamik olarak bulmaya çalışır
- Bellek kullanımı (`free -h`, MB/GB otomatik ayrımlı)
- Disk kullanımı (`df -hT`, gerçek dosya sistemleri; tmpfs/overlay gibi sanal olanlar hariç), MB/GB ve yüzde olarak doluluk
- En çok CPU tüketen 10 işlem
- En çok RAM tüketen 10 işlem
- Reboot gerekip gerekmediği (`/var/run/reboot-required`)
- Başarısız (failed) systemd servisleri
- Kurulabilir paket/güvenlik güncellemesi sayısı

## Gereksinimler

- `hosts: all` — her node'da çalışır.
- Bu playbook `gather_facts: true` kullanır (repodaki diğer playbook'ların aksine) — OS/kernel/CPU/sanallaştırma bilgisi Ansible'ın kendi fact toplama mekanizmasından gelir.
- `dmidecode` çıktısı için `become: true` (sudo) gerekir; kurulu değilse veya erişilemezse o bölüm sessizce "erişilemedi" mesajı gösterir, playbook hata vermez.
- Raporun ilk bloğu makine kimliğidir (`HOST` = inventory adı/IP, `hostname` = sunucunun kendi adı); birden fazla node'da hangi çıktının kime ait olduğu buradan okunur.

## Çalıştırma Komutu

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/10_check_system_health.yml

# Belirli bir host/grup ile sınırlamak için:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/10_check_system_health.yml --limit worker1
```

## Örnek Çıktı

```text
TASK [Sistem sağlığı raporu] ****************************************************
ok: [203.0.113.10] => {
    "msg": [
        "################################################################################\n# HOST: 203.0.113.10\n# hostname: node1\n################################################################################",
        "OS: Ubuntu 22.04 (jammy)",
        "Kernel: 5.15.0-186-generic",
        "Uptime: up 2 days, 6 hours, 20 minutes",
        "CPU çekirdek sayısı: 16",
        "Load average (1/5/15 dk): 0.97 / 0.98 / 1.01 (çekirdek başına 1dk: 0.06)",
        "Çalışma kuyruğu (çalışan/toplam process): 1/2090",
        "Zombie (defunct) process sayısı: 0",
        "Sanallaştırma: rol=guest, tip=VirtualPC, systemd-detect-virt=microsoft",
        "Donanım/Hypervisor bilgisi:\nManufacturer: Microsoft Corporation\nProduct: Virtual Machine\nBIOS Version: 090007",
        "Bellek:\n               total  used  free  shared  buff/cache  available\nMem:  125Gi  5.2Gi  90Gi  121Mi   29Gi        119Gi\nSwap: 0B     0B    0B",
        "Disk kullanımı:\nFilesystem  Type  Size  Used  Avail  Use%  Mounted on\n/dev/mapper/ubuntu--vg-ubuntu--lv  ext4  540G  388G  130G  75%  /",
        "En çok CPU tüketen 10 işlem:\n...",
        "En çok RAM tüketen 10 işlem:\n...",
        "Reboot gerekiyor mu: EVET",
        "Başarısız systemd servisleri: Yok",
        "Kurulabilir paket güncellemesi sayısı: 32"
    ]
}
```

## Notlar

- `systemd-detect-virt` + `dmidecode` kombinasyonu, guest VM'lerde hypervisor'ı (ör. Microsoft Hyper-V, VMware, KVM) ve bazen BIOS sürümünü ortaya çıkarır; hypervisor'ın kendi sürümü genelde guest içinden tam olarak bilinemez, sadece BIOS/ürün bilgisiyle ipucu elde edilir.
- "Reboot gerekiyor mu" ve "kurulabilir paket güncellemesi sayısı" Debian/Ubuntu'ya özgüdür (`/var/run/reboot-required`, `apt list --upgradable`); farklı bir dağıtımda bu adımlar sessizce boş/hatasız döner.
