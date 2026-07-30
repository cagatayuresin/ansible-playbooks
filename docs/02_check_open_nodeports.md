---
title: "02 · check_open_nodeports"
parent: Playbook Kılavuzları
nav_order: 2
---

# 02_check_open_nodeports.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

Bu playbook, Kubernetes cluster'ınızda `NodePort` tipiyle dışarıya açılmış olan tüm servisleri tespit eder. Ardından inventory'nizde tanımlı olan sunucu IP adresini (`inventory_hostname`) kullanarak, browser üzerinden doğrudan tıklayıp/kopyalayarak erişebileceğiniz HTTP linklerini (ör. `http://192.168.1.10:31234`) dinamik olarak oluşturur ve ekrana basar.

## Gereksinimler

- Hedef sunucuda (master veya singlenode) `kubectl` kurulu ve konfigüre edilmiş olmalıdır.
- Ansible inventory'nizde `[master]` veya `[singlenode]` grubu tanımlanmış olmalıdır.

Playbook artık NodePort sorgusundan önce `kubectl cluster-info` ile bir erişim ön kontrolü yapar. `kubectl` erişimi yoksa anlamlı bir uyarı mesajı basılır ve NodePort sorgusu atlanır.

## Çalıştırma Komutu

```bash
# Müşteri A için çalıştırma
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/02_check_open_nodeports.yml

# Müşteri B için çalıştırma
ansible-playbook -i inventories/musteri_b/hosts.ini playbooks/02_check_open_nodeports.yml
```

## Örnek Çıktı

Komut çalıştırıldığında "Ping pong" başarılı olursa, aktif NodePort'lar listelenir ve linkler oluşturulur:

```text
TASK [Ping pong] ***************************************************************
ok: [192.168.1.10]

TASK [Kubeconfig / kubectl erişim kontrolü] *************************************
ok: [192.168.1.10]

TASK [Find all NodePort services and their ports] ******************************
ok: [192.168.1.10]

TASK [Generate browser accessible links] ***************************************
ok: [192.168.1.10] => {
    "msg": "Aşağıdaki servisler NodePort olarak açılmıştır. Browser üzerinden erişmek için linkleri kullanabilirsiniz:\n\n- default/nginx-service -> http://192.168.1.10:32001\n- argocd/argocd-server -> http://192.168.1.10:30080\n"
}
```
