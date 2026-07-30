---
title: "05 · check_k8s_services"
parent: Playbook Kılavuzları
nav_order: 5
---

# 05_check_k8s_services.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

Bu playbook, sistemde bulunan Kubernetes/container ile ilgili tüm systemd servislerini **dinamik olarak** keşfedip (sabit bir liste değil, `kube|containerd|calico|etcd|runc` desenine göre arama) her birinin aktif/enabled durumunu ve son 10 satır logunu raporlar.

## Gereksinimler

- `hosts: all` — her node'da çalışır.
- Servis keşfi Ansible'ın yerleşik `service_facts` modülüyle yapılır, ek bir collection gerekmez.
- `journalctl` çıktısı okunabilmesi için ilgili kullanıcının journal loglarına erişimi olmalıdır.

## Çalıştırma Komutu

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/05_check_k8s_services.yml

# Belirli bir host/grup ile sınırlamak için:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/05_check_k8s_services.yml --limit worker1
```

## Örnek Çıktı

```text
TASK [Ping pong] ***************************************************************
ok: [203.0.113.10]

TASK [Servis durum raporu - aktif/enabled (Çalışma Şartı: ilgili servis bulunmalı)] ***
ok: [203.0.113.10] => (item=containerd.service) => {"msg": "containerd.service -> durum: running, açılışta aktif: enabled"}
ok: [203.0.113.10] => (item=kubelet.service) => {"msg": "kubelet.service -> durum: running, açılışta aktif: enabled"}

TASK [Servis log raporu (Çalışma Şartı: log kaydı alınabilmeli)] ***************
ok: [203.0.113.10] => (item=kubelet.service) => {
    "msg": "===== kubelet.service son loglar =====\n... (son 10 satır) ..."
}
```

## Notlar

- Servis listesi tamamen dinamiktir: `service_facts` ile sistemdeki tüm servisler taranır, yalnızca isim deseni eşleşenler (`kube`, `containerd`, `calico`, `etcd`, `runc`) rapora dahil edilir. Docker bu desenin dışındadır.
- Log satır sayısı 10 ile sınırlıdır — çok sayıda servis/host için çalıştırıldığında çıktının okunabilir kalması amaçlanıyor.
- `.get('state', ...)` / `.get('status', ...)` kullanılmıştır çünkü bazı servis girdileri `service_facts` çıktısında eksik alanlarla gelebiliyor.
