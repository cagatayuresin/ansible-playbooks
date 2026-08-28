---
lang: tr
title: "19 · check_network_connectivity"
parent: Playbook Kılavuzları
nav_order: 19
---

# 19_check_network_connectivity.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Amaç

On-prem kurulumlarda (internetli / kısıtlı / air-gap) host’un **ağ ve internet erişim profilini** ayrıntılı raporlar. Salt-okunur; yapılandırma değiştirmez.

Kontrol edilenler:

| Bölüm | Ne bakar |
|---|---|
| Arayüzler | `ip -br addr` |
| Rotalar / gateway | `ip route`, default route var mı |
| Gateway ping | Varsayılan gateway ICMP |
| DNS yapılandırması | `/etc/resolv.conf`, nameserver’lar, `resolvectl` özeti, `nsswitch` hosts |
| DNS çözümleme | getent/getaddrinfo ile kritik hostlar (registry, apt, github…) + süre |
| ICMP ping | 1.1.1.1 / 8.8.8.8 (firewall ICMP kesebilir — tek başına karar verme) |
| TCP | 80/443/53 hedeflerine connect (gerçek outbound için daha güvenilir) |
| HTTP/HTTPS | curl benzeri istek; 401/403 bile “ulaşıldı” sayılır |
| **Hız testi** | İnternet/HTTP yeterliyse Cloudflare `__down` (indirme) + `__up` (yükleme) Mbps; yoksa atlanır |
| Proxy | `http(s)_proxy` env, apt/docker/containerd proxy conf ipuçları |
| **GENEL SONUÇ** | `INTERNET_VAR` / `KISMI_ERISIM` / `DNS_VAR_CIKIS_YOK` / `KISITLI_DNS_SORUNLU` / `INTERNET_YOK_VEYA_AIRGAP` |

Her host kendi raporunu üretir (`HOST` / `hostname` başlığı). Çok nodeli ortamda her node ayrı test edilir (NAT/firewall node’a göre değişebilir).

## Profil nasıl yorumlanır?

| Profil | Anlam | Kurulum |
|---|---|---|
| `INTERNET_VAR` | DNS + HTTPS çoğunlukla OK | Online kurulum / image pull |
| `KISMI_ERISIM` | Bazı hedefler açık | FAIL olan registry/apt için mirror veya allow-list |
| `DNS_VAR_CIKIS_YOK` | İsim çözülür, dış TCP/HTTPS yok | Outbound FW / proxy |
| `KISITLI_DNS_SORUNLU` | TCP kısmen var, DNS zayıf | resolv.conf / kurumsal DNS |
| `INTERNET_YOK_VEYA_AIRGAP` | DNS+TCP+HTTPS çoğunlukla FAIL | Offline bundle / iç mirror |

ICMP FAIL tek başına “internet yok” demek değildir; birçok ortamda ICMP kapalı, 443 açıktır. Kararı **DNS + TCP + HTTP** skorlarına göre ver.

## Değişkenler

| Değişken | Varsayılan (özet) |
|---|---|
| `net_dns_hosts` | google, cloudflare, docker/ghcr/quay/k8s registry, ubuntu archive, github |
| `net_ping_targets` | `1.1.1.1,8.8.8.8` |
| `net_tcp_targets` | DNS/HTTPS portları + registry/apt |
| `net_http_urls` | google generate_204, github, registry’ler, ubuntu archive |
| `net_speed_test` | `true` — internet varken hız testi; `false` ile kapat |
| `net_speed_bytes` | `1000000,10000000` (1MB + 10MB Cloudflare indirme) |

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/19_check_network_connectivity.yml \
  --extra-vars 'net_dns_hosts=nexus.local,registry.local,google.com'

# Hız testini kapat:
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/19_check_network_connectivity.yml \
  --extra-vars 'net_speed_test=false'
```

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/19_check_network_connectivity.yml

# Belirli node:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/19_check_network_connectivity.yml --limit workers
```

## Gereksinimler

- `hosts: all`
- Hedefte `python3` (rapor script’i)
- `ping` genelde iputils ile gelir; yoksa ICMP bölümü FAIL olabilir, diğerleri devam eder
- Root gerekmez (proxy dosyaları world-readable ise)

## Notlar

- Testler kısa timeout’ludur; yavaş linkte bazı FAIL’ler timeout olabilir — skorlara ve tekrar koşuya bak.
- Kurumsal SSL inspection varsa HTTPS FAIL (sertifika) görülebilir; TCP 443 OK + HTTPS FAIL kombinasyonu buna işaret eder.
- Hız testi yaklaşık ↓download / ↑upload Mbps verir (Cloudflare). Air-gap / HTTP yoksa bölüm atlanır.
- Script: `playbooks/files/network_connectivity_check.py`
