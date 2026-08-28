---
lang: tr
title: "40 · check_node_baseline_drift"
parent: Playbook Kılavuzları
nav_order: 40
---

# 40_check_node_baseline_drift.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Linux](https://img.shields.io/badge/Linux-Baseline_Drift-FCC624?style=flat)

## Amaç

Tüm host'lardan normalize edilmiş baseline verisi toplayıp farklı değerleri `[DRIFT]` olarak işaretler:

- OS, kernel, mimari ve cgroup sürümü
- Swap, IP forwarding ve bridge netfilter
- `overlay` / `br_netfilter` modülleri
- containerd ve kubelet sürümleri
- containerd/kubelet config SHA256 özetleri
- SystemdCgroup ve kubelet cgroup driver
- Zaman senkron servisi ve reboot ihtiyacı

Config içerikleri rapora yazılmaz; yalnızca ilk 16 karakterlik SHA256 özeti karşılaştırılır.

## Değişkenler

`node_baseline_compare_fields` listesiyle drift karşılaştırmasına dahil edilen alanlar özelleştirilebilir.

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/40_check_node_baseline_drift.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/40_check_node_baseline_drift.yml \
  --limit workers
```
