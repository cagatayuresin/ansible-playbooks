---
lang: tr
title: "20 · check_host_ports_firewall"
parent: Playbook Kılavuzları
nav_order: 20
---

# 20_check_host_ports_firewall.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Amaç

Her host’ta:

1. **Hangi portlar dinleniyor** (`ss -tulnp`)
2. **Ne şekilde açık** — tüm arayüzler / sadece localhost / belirli IP
3. **Hangi uygulama** dinliyor (process adı + pid)
4. **Firewall** — UFW, firewalld (varsa), `iptables` + `nft` özeti; dinlenen portlara değinen kurallar

Salt-okunur; kural ekleyip silmez. Her host kendi diskindeki / kendi kernel’indeki durumu raporlar (`HOST` başlığı).

Script: `playbooks/files/host_ports_firewall_check.py`

## “Nasıl açık?” ne demek?

| BIND | Anlam |
|---|---|
| `TUM_ARAYUZLER` | `0.0.0.0` / `::` — dışarıdan erişim **mümkün olabilir** (firewall izin verirse) |
| `SADECE_LOCALHOST` | Yalnızca local process’ler erişir |
| `OZEL_IP` / `BELIRLI_IP` | Belirli arayüz IP’sinde dinliyor |

Dinlemek ≠ firewall’ın dışarıya açması. Raporun firewall bölümündeki INPUT policy / UFW / nft kurallarına bak.

## 02 ile farkı

| Playbook | Kapsam |
|---|---|
| [02](02_check_open_nodeports.md) | Kubernetes **NodePort** servisleri |
| **20** | Host OS dinleyen socket’ler + iptables/nft/UFW |

## Gereksinimler

- `hosts: all`
- `become: true` (süreç adları + iptables/nft için)
- `python3`, `ss` (iproute2)

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/20_check_host_ports_firewall.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/20_check_host_ports_firewall.yml --limit workers
```

## Çıktı nasıl okunur?

1. **Dinleyen portlar** tablosu → port + bind + uygulama
2. **UFW / firewalld** (kuruluysa)
3. **iptables/nft** → policy, dinlenen portlara ait `dpt:` / `dport` satırları, NAT özeti
4. **Risk özeti** → tüm arayüzde dinleyen servis listesi

K8s node’unda kube-proxy/CNI kuralları çok uzun olabilir; rapor ilgili satırları süzerek kısaltır.

## Notlar

- Process alanı `-` ise izin/root eksik demektir (playbook `become` kullanır).
- Container içi portlar host’ta `*:` veya CNI IP’sinde görünebilir; uygulama adı `containerd`/`docker-proxy` olabilir.
