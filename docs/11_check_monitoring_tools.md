# 11_check_monitoring_tools.yml - Kullanım Kılavuzu

## Amaç

Bu playbook, yaygın sistem izleme araçlarının (`vmstat`, `iostat`, `sar`, `htop`, `dstat`, `iotop`, `atop`, `perf`, `bpftrace`, `glances`) kurulu olup olmadığını kontrol eder, **kurulu değilse apt ile kurar**, sonra her biriyle salt-okunur, tek seferlik bir kontrol çalıştırıp sonucu raporlar.

⚠️ "Salt-okunur" ifadesi araçların topladığı veriler için geçerlidir (sistemi değiştirmezler); ancak eksik araçları **gerçekten kurar** (apt install), bu bir sistem değişikliğidir.

## Araç Bazında Yaklaşım

| Araç | Kurulum paketi | Kontrol komutu |
|---|---|---|
| vmstat | `procps` (genelde zaten kurulu) | `vmstat 1 3` |
| iostat | `sysstat` | `iostat -xz 1 2` |
| sar | `sysstat` (iostat ile aynı paket) | `sar 1 2` |
| htop | `htop` | Sadece kurulum kontrolü — interaktif TUI aracı, batch/otomatik rapor modu yok |
| dstat | `dstat` | `dstat -cdngy --nocolor 1 1` |
| iotop | `iotop` | `iotop -b -n 1 -o` (root gerektirir) |
| atop | `atop` | `atop 1 1`, process listesi hariç sadece sistem özeti (CPU/bellek/disk/ağ) |
| perf | `linux-tools-common` + `linux-tools-<kernel>` | `perf stat -a -- sleep 1` (donanım sayaçları VM'de kısıtlı olabilir) |
| bpftrace | `bpftrace` | Sadece kurulum + `--version` — otomatik izleme betiği çalıştırılmaz (kernel'e özgü, riskli olabilir) |
| glances | `glances` | `timeout 3 glances --stdout now,cpu.total,mem.percent,mem.used,mem.total,load.min1` |

## Gereksinimler

- `hosts: all` — her node'da çalışır.
- `become: true` (sudo) apt kurulumları ve `iotop`/`atop`/`perf` gibi root gerektiren komutlar için kullanılır.
- Bir araç kurulamazsa (ör. repoda yoksa, kernel-özel paket eksikse) playbook hata vermez; o aracın rapor satırı "kurulamadı" gösterir, diğer araçlar etkilenmez.

## Çalıştırma Komutu

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/11_check_monitoring_tools.yml

# Belirli bir host/grup ile sınırlamak için:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/11_check_monitoring_tools.yml --limit worker1
```

## Örnek Çıktı

```text
TASK [İzleme araçları raporu] **************************************************
ok: [203.0.113.10] => {
    "msg": [
        "vmstat: kurulu\n...",
        "iostat: kurulu\n...",
        "sar: kurulu\n...",
        "htop: kurulu (interaktif araç, otomatik rapor üretilmez)",
        "dstat: kurulu\n...",
        "iotop: kurulu\n...",
        "atop: kurulu\n... (sistem özeti, process listesi hariç)",
        "perf: kurulu\n... (VM'de cycles/instructions '<not supported>' görünebilir)",
        "bpftrace: kurulu, sürüm: bpftrace v0.14.0",
        "glances: kurulu\nnow: ...\ncpu.total: 10.0\nmem.percent: 5.3\n..."
    ]
}
```

## Notlar

- `perf stat` çıktısı `stderr`'e yazılır (perf'in kendine has davranışı), playbook bunu doğru şekilde yakalayıp rapora ekler.
- VM ortamlarında (ör. Hyper-V, bazı bulut sağlayıcıları) donanım performans sayaçları (cycles/instructions) genelde erişilebilir değildir; `perf stat` bu satırları `<not supported>` olarak gösterir, bu bir hata değildir.
- `glances --stdout` varsayılan olarak sürekli döngüde çalışır; `timeout 3` ile tek seferlik hale getirilmiştir.
- `atop` çıktısı ağ arayüzü sayısına göre uzayabilir (ör. çok sayıda Calico veth arayüzü olan bir k8s node'unda); bu gürültü değil, gerçek per-interface istatistiktir.
