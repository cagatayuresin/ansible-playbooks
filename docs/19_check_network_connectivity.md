---
lang: en
title: "19 · check_network_connectivity"
parent: Playbook Guides
nav_order: 19
---

# 19_check_network_connectivity.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Purpose

On on-prem installs (internet / restricted / air-gap), reports the host's **network and internet access profile** in detail. Read-only; does not change configuration.

What is checked:

| Section | What it looks at |
|---|---|
| Interfaces | `ip -br addr` |
| Routes / gateway | `ip route`, whether a default route exists |
| Gateway ping | ICMP to the default gateway |
| DNS configuration | `/etc/resolv.conf`, nameservers, `resolvectl` summary, `nsswitch` hosts |
| DNS resolution | Critical hosts via getent/getaddrinfo (registry, apt, github…) + duration |
| ICMP ping | 1.1.1.1 / 8.8.8.8 (firewall may drop ICMP — do not decide on this alone) |
| TCP | Connect to 80/443/53 targets (more reliable for real outbound) |
| HTTP/HTTPS | curl-like request; even 401/403 counts as “reached” |
| **Speed test** | If internet/HTTP is sufficient, Cloudflare `__down` (download) + `__up` (upload) Mbps; otherwise skipped |
| Proxy | `http(s)_proxy` env, apt/docker/containerd proxy conf hints |
| **OVERALL RESULT** | `INTERNET_AVAILABLE` / `PARTIAL_ACCESS` / `DNS_OK_NO_EGRESS` / `RESTRICTED_DNS_ISSUE` / `NO_INTERNET_OR_AIRGAP` |

Each host produces its own report (`HOST` / `hostname` header). In a multi-node environment each node is tested separately (NAT/firewall can differ per node).

## How to read the profile

| Profile | Meaning | Install |
|---|---|---|
| `INTERNET_AVAILABLE` | DNS + HTTPS mostly OK | Online install / image pull |
| `PARTIAL_ACCESS` | Some targets open | Mirror or allow-list for FAIL registry/apt |
| `DNS_OK_NO_EGRESS` | Names resolve, no external TCP/HTTPS | Outbound FW / proxy |
| `RESTRICTED_DNS_ISSUE` | TCP partly works, DNS is weak | resolv.conf / corporate DNS |
| `NO_INTERNET_OR_AIRGAP` | DNS+TCP+HTTPS mostly FAIL | Offline bundle / internal mirror |

ICMP FAIL alone does not mean “no internet”; many environments block ICMP but allow 443. Decide from the **DNS + TCP + HTTP** scores.

## Variables

| Variable | Default (summary) |
|---|---|
| `net_dns_hosts` | google, cloudflare, docker/ghcr/quay/k8s registry, ubuntu archive, github |
| `net_ping_targets` | `1.1.1.1,8.8.8.8` |
| `net_tcp_targets` | DNS/HTTPS ports + registry/apt |
| `net_http_urls` | google generate_204, github, registries, ubuntu archive |
| `net_speed_test` | `true` — speed test when internet is present; set `false` to disable |
| `net_speed_bytes` | `1000000,10000000` (1MB + 10MB Cloudflare download) |

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/19_check_network_connectivity.yml \
  --extra-vars 'net_dns_hosts=nexus.local,registry.local,google.com'

# Disable the speed test:
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/19_check_network_connectivity.yml \
  --extra-vars 'net_speed_test=false'
```

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/19_check_network_connectivity.yml

# Specific node:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/19_check_network_connectivity.yml --limit workers
```

## Requirements

- `hosts: all`
- `python3` on the target (report script)
- `ping` usually comes with iputils; if missing, the ICMP section may FAIL and the others continue
- Root is not required (if proxy files are world-readable)

## Notes

- Tests use short timeouts; on a slow link some FAILs may be timeouts — look at the scores and a re-run.
- With corporate SSL inspection you may see HTTPS FAIL (certificate); TCP 443 OK + HTTPS FAIL points to that.
- The speed test gives approximate ↓download / ↑upload Mbps (Cloudflare). The section is skipped on air-gap / no HTTP.
- Script: `playbooks/files/network_connectivity_check.py`
