---
title: "11 · check_monitoring_tools"
parent: Playbook Kılavuzları
nav_order: 11
---

# 11_check_monitoring_tools.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat)

## Amaç

Bu playbook iki iş yapar:

1. **Araç setini hazırlar** — yaygın Linux performans/izleme araçlarının kurulu olup olmadığına bakar; eksikse `apt` ile kurar.
2. **Anlık örnek alır** — kurulu her araçla kısa, salt-okunur bir komut çalıştırıp çıktıyı rapora basar (canlı TUI açmaz).

[10_check_system_health](10_check_system_health.md) “şu anki sağlık özeti”dir (load, RAM, disk, top process…). Bu playbook ise **ileride SSH ile bakacağın izleme araçlarını** node’da hazır tutar ve örnek çıktı verir. İkisini birlikte kullanmak mantıklıdır: 10 ile genel tablo, 11 ile detaylı teşhis araçları.

⚠️ Eksik paketleri **gerçekten kurar** (`apt install`). Örnek komutlar sistemi değiştirmez; kurulum adımı değiştirir.

## Çoklu makine çıktısı

Raporun **ilk bloğu** makine kimliğidir (`HOST` = inventory adı/IP, `hostname` = sunucunun kendi adı). Birden fazla node’da çalıştırınca hangi aracın hangi makineye ait olduğu buradan okunur.

## Araç Bazında Yaklaşım

| Araç | Paket | Playbook ne yapar | Ne zaman işine yarar |
|---|---|---|---|
| vmstat | `procps` | `vmstat 1 3` | CPU, bellek, swap, I/O bekleme genel bakış |
| iostat | `sysstat` | `iostat -xz 1 2` | Disk/device bazlı I/O, util%, await |
| sar | `sysstat` | `sar 1 2` | CPU kırılımı (user/system/iowait/idle) |
| htop | `htop` | Sadece kurulum | İnteraktif süreç izleme (SSH’te elle `htop`) |
| dstat | `dstat` | `dstat -cdngy 1 1` | CPU+disk+net+sys tek satırda özet |
| iotop | `iotop` | `iotop -b -n 1 -o` | Hangi process disk okuyor/yazıyor |
| atop | `atop` | Sistem özeti (PID listesi kesilir) | CPU/mem/disk/ağ paneli; geçmiş için atop log’ları |
| perf | `linux-tools-*` | `perf stat -a -- sleep 1` | Donanım/yazılım sayaçları, CPU verimliliği |
| bpftrace | `bpftrace` | Sadece `--version` | Kernel/eBPF ile derin izleme (betik elle yazılır) |
| glances | `glances` | `--stdout` ile kısa örnek | CPU/mem/load tek bakışta |

## Gereksinimler

- `hosts: all` — her node’da çalışır.
- `become: true` (sudo) apt kurulumları ve `iotop` / `atop` / `perf` için gerekir → inventory’de `ansible_become_pass` olmalı.
- Bir araç kurulamazsa (repo’da yok, kernel paketi uyuşmaz) playbook **fail olmaz**; o satır `kurulamadı` + varsa hata mesajı gösterir.

## Çalıştırma Komutu

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/11_check_monitoring_tools.yml

# Belirli host/grup:
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/11_check_monitoring_tools.yml --limit singlenode
```

---

## Çıktılar nasıl yorumlanır?

Rapor her araç için **durum** (`kurulu` / `kurulamadı`) ve varsa **örnek çıktı** basar. Aşağıdaki anahtarlar “ne bakmalı / ne kırmızı bayrak” içindir. Değerler iş yüküne göre değişir; çekirdek sayısına göre normalize etmeyi unutma.

### vmstat (`vmstat 1 3`)

İlk satır ortalama (boot’tan beri) olabilir; **son 1–2 satıra** bak.

| Sütun | Anlamı | Dikkat |
|---|---|---|
| `r` | Çalışmaya hazır / koşan process | Sürekli çekirdek sayısından belirgin yüksekse CPU kuyruğu |
| `b` | Kesintisiz sleep (genelde I/O) | Sürekli >0 → disk veya kilit bekleme |
| `si` / `so` | Swap in / out | Düzenli `so` > 0 → bellek yetmiyor |
| `us` / `sy` | User / system CPU % | İkisi yüksek + `id` düşük → CPU meşgul |
| `id` | Idle % | Düşük idle = meşgul CPU |
| `wa` | I/O wait % | Yüksek `wa` → disk/network I/O darboğazı şüphesi |
| `st` | Steal (VM) | Yüksek steal → hypervisor komşu gürültüsü |

### iostat (`iostat -xz 1 2`)

`-x` extended, `-z` sıfır aktiviteyi gizler. İlk örnek genelde özet; **ikinci örnek** daha “şu an”a yakındır.

| Alan | Anlamı | Dikkat |
|---|---|---|
| `%util` | Cihazın meşgul olduğu süre % | Sürekli ~100 → disk doymuş |
| `await` / `aqu-sz` | Ortalama bekleme / kuyruk | Yüksek await + dolu kuyruk → yavaş depolama |
| `r/s` `w/s` | Okuma/yazma IOPS | Ani sıçrama → hangi process için `iotop` |
| `rkB/s` `wkB/s` | Throughput | Büyük yedek/compaction ile uyumlu mu bak |

### sar (`sar 1 2`)

CPU yüzdeleri (tüm çekirdekler ortalaması).

| Alan | Anlamı | Dikkat |
|---|---|---|
| `%user` / `%system` | Uygulama / kernel CPU | Sürekli yüksek → profil (`perf`, `htop`) |
| `%iowait` | CPU’nun I/O beklemesi | Yüksek → disk tarafına bak (`iostat`) |
| `%idle` | Boşta | Düşük idle = kapasite dolu |
| `%steal` | VM steal | Hipervizör baskısı |

### htop

Playbook örnek üretmez (TUI). SSH’te `htop`: renkli bar’lar, process ağacı, F6 ile sort. Anlık “kim CPU/RAM yiyor?” için.

### dstat

Tek satırda cpu / disk / net / system. `dstat` bazı yeni Ubuntu sürümlerinde paketten kalkmış olabilir (`kurulamadı` normal); yerine `pcp`/`dstat` alternatifleri veya `vmstat`+`iostat` yeterli.

### iotop (`-b -n 1 -o`)

Sadece disk I/O yapan process’ler (`-o`). `DISK READ` / `DISK WRITE` yüksek satırlar → hangi pod/process disk’i yoruyor. Boş liste = o anda anlamlı disk I/O yok.

### atop (sistem özeti)

CPU/MEM/DSK/NET blokları. Process tablosu bilerek kesilir (gürültü). Çok sayıda ağ arayüzü (ör. Calico veth) NET bölümünü uzatır; bu hata değil. Geçmiş analiz için host’ta `atop` log’ları (paket kurulumuna bağlı) ayrı bakılır.

### perf (`perf stat -a -- sleep 1`)

1 sn’lik sistem geneli sayaç özeti. Çıktı çoğu zaman **stderr**’dedir; playbook onu da rapora alır.

| Gösterge | Kabaca yorum |
|---|---|
| `cycles` / `instructions` | IPC düşükse (az instruction / çok cycle) → stall, cache, I/O bekleme |
| `cache-misses` | Yüksek miss oranı → bellek erişim maliyeti |
| `context-switches` / `cpu-migrations` | Aşırı yüksek → aşırı schedule / thread thrash |
| `<not supported>` | VM/bulutta donanım sayacı yok — **hata değil** |

### bpftrace

Sadece sürüm doğrulanır; otomatik betik yok (yanlış one-liner üretimde riskli). Kuruluysa SSH’te örneğin I/O veya syscall izleme betikleri elle çalıştırılır.

### glances (`--stdout` örnek)

| Alan | Anlamı |
|---|---|
| `cpu.total` | Toplam CPU kullanımı % |
| `mem.percent` / `mem.used` | Bellek doluluk |
| `load.min1` | 1 dk load — çekirdek sayısıyla karşılaştır (örn. 8 çekirdekte load 8 ≈ tam dolu) |

---

## Örnek Rapor (kısaltılmış)

```text
TASK [İzleme araçları raporu] ***
ok: [203.0.113.10] => {
  "msg": [
    "=== vmstat ===\nDurum: kurulu\nYorum: r/b kuyruk; si/so swap; us/sy/id/wa CPU\nprocs -----------memory---------- ...",
    "=== iostat ===\nDurum: kurulu\nYorum: %util ve await'e bak\n...",
    "=== htop ===\nDurum: kurulu (interaktif; SSH'te elle çalıştır)",
    "=== perf ===\nDurum: kurulu\n... <not supported> satırları VM'de normal ...",
    ...
  ]
}
```

## Notlar

- `perf stat` çıktısı stderr’e gider; rapor bunu birleştirir.
- `glances --stdout` döngüde kalmasın diye `timeout` ile sınırlıdır.
- `dstat` / `linux-tools-<kernel>` bazı ortamlarda apt’te olmayabilir → `kurulamadı` + hata satırı; diğer araçlar etkilenmez.
- Tekrar çalıştırınca zaten kurulu paketler için `apt` no-op olur; örnek komutlar her seferinde yenilenir.
