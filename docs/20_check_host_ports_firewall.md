---
lang: en
title: "20 · check_host_ports_firewall"
parent: Playbook Guides
nav_order: 20
---

# 20_check_host_ports_firewall.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

## Purpose

On each host:

1. **Which ports are listening** (`ss -tulnp`)
2. **How they are open** — all interfaces / localhost only / a specific IP
3. **Which application** is listening (process name + pid)
4. **Firewall** — UFW, firewalld (if present), `iptables` + `nft` summary; rules that mention listening ports

Read-only; does not add or delete rules. Each host reports the state on its own disk / own kernel (`HOST` header).

Script: `playbooks/files/host_ports_firewall_check.py`

## What does “how is it open?” mean?

| BIND | Meaning |
|---|---|
| `ALL_INTERFACES` | `0.0.0.0` / `::` — external access **may be possible** (if the firewall allows it) |
| `LOCALHOST_ONLY` | Only local processes can reach it |
| `PRIVATE_IP` / `SPECIFIC_IP` | Listening on a specific interface IP |

Listening ≠ the firewall opening it to the outside. Check INPUT policy / UFW / nft rules in the firewall section of the report.

## Difference from 02

| Playbook | Scope |
|---|---|
| [02](02_check_open_nodeports.md) | Kubernetes **NodePort** services |
| **20** | Host OS listening sockets + iptables/nft/UFW |

## Requirements

- `hosts: all`
- `become: true` (for process names + iptables/nft)
- `python3`, `ss` (iproute2)

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/20_check_host_ports_firewall.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/20_check_host_ports_firewall.yml --limit workers
```

## How to read the output

1. **Listening ports** table → port + bind + application
2. **UFW / firewalld** (if installed)
3. **iptables/nft** → policy, `dpt:` / `dport` lines for listening ports, NAT summary
4. **Risk summary** → services listening on all interfaces

On a K8s node, kube-proxy/CNI rules can be very long; the report filters and shortens relevant lines.

## Notes

- A process field of `-` means missing permission/root (the playbook uses `become`).
- Ports inside containers may show as `*:` or a CNI IP on the host; the application name may be `containerd`/`docker-proxy`.
