---
title: "07 · check_calico"
parent: Playbook Kılavuzları
nav_order: 7
---

# 07_check_calico.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

Bu playbook, Calico CNI'nin mevcut sürümünü (`calico-node` DaemonSet image tag'i) raporlar ve isteğe bağlı olarak yeni bir manifest uygulayarak günceller.

⚠️ Calico bir apt paketi değil, cluster içinde çalışan bir DaemonSet'tir. `calico_manifest_url` verilirse gerçek bir güncelleme yapılır (salt-okunur değildir). Sürüm atlamadan önce Calico'nun resmi upgrade rehberini kontrol edin — bazı sürüm atlamalarında CRD güncellemesi de gerekir.

## Gereksinimler

- `kubectl` erişimi olan ilk control-plane node (`master`/`singlenode` grubundaki ilk host) üzerinden çalışır.
- Güncelleme yapılacaksa `calico_manifest_url` değişkeni verilmelidir; verilmezse sadece mevcut sürüm raporlanır.

## Çalıştırma Komutu

```bash
# Sadece mevcut sürümü görmek için:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/07_check_calico.yml

# Güncellemek için:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/07_check_calico.yml \
  --extra-vars "calico_manifest_url=https://raw.githubusercontent.com/projectcalico/calico/v3.31.1/manifests/calico.yaml"
```

## Örnek Çıktı

```text
TASK [Ping pong] ***************************************************************
ok: [203.0.113.10]

TASK [Kubeconfig / kubectl erişim kontrolü (Çalışma Şartı: ilk control-plane node olmalı)] ***
ok: [203.0.113.10]

TASK [calico_manifest_url verilmedi uyarısı (Çalışma Şartı: calico_manifest_url verilMEMİŞ olmalı)] ***
ok: [203.0.113.10] => {
    "msg": "calico_manifest_url belirtilmedi, güncelleme yapılmadı. Örnek kullanım: --extra-vars \"calico_manifest_url=<resmi manifest URL'i>\""
}

TASK [Calico sürüm raporu (Çalışma Şartı: ilk control-plane node olmalı ve kubectl erişimi olmalı)] ***
ok: [203.0.113.10] => {
    "msg": "Calico: quay.io/calico/node:v3.31.1 -> quay.io/calico/node:v3.31.1"
}
```
