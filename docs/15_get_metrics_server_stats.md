# 15_get_metrics_server_stats.yml - Kullanım Kılavuzu

## Amaç

metrics-server hazırsa `kubectl top` ile **node** ve **pod** CPU/bellek kullanımını okunaklı raporlar. Kurulu değilse kurmaz; uyarı basar (kurulum için 16).

Ortak görevler:
- [tasks/metrics_server_check.yml](../playbooks/tasks/metrics_server_check.yml)
- [tasks/metrics_server_report.yml](../playbooks/tasks/metrics_server_report.yml)

## Rapor bölümleri

| Bölüm | Komut | Nasıl okunur |
|---|---|---|
| Node | `kubectl top nodes` | Node başına anlık CPU (cores) ve MEMORY |
| Pod CPU | `kubectl top pods -A --sort-by=cpu` | En çok CPU yiyen pod üstte |
| Pod bellek | `kubectl top pods -A --sort-by=memory` | En çok RAM yiyen pod üstte |

Değerler anlıktır (metrics-server scrapes ~15s); uzun vadeli grafik değildir. Yüksek kullanım + [10](10_check_system_health.md) / [11](11_check_monitoring_tools.md) ile birlikte yorumlanır.

## Gereksinimler

- `master` / `singlenode`, ilk control-plane
- metrics-server **HAZIR** olmalı (`Available=True`). Değilse 14 veya 16.

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/15_get_metrics_server_stats.yml
```

## Notlar

- Yeni kurulumdan hemen sonra “veri yok” görülebilir; ~1 dk bekleyip tekrar 15 yeterli.
- Salt-okunur.
