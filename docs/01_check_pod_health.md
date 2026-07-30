---
title: "01 · check_pod_health"
parent: Playbook Kılavuzları
nav_order: 1
---

# 01_check_pod_health.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

Bu playbook, Kubernetes cluster'ınızdaki (genellikle `master` veya `singlenode` üzerinde çalıştırılarak) tüm namespace'lerde bulunan pod'ların mevcut durumlarını ve sağlıklarını (sağlıklı çalışıp çalışmadığını, yeniden başlama sayısını, çalıştığı node'u vb.) döndürür.

## Gereksinimler

- Hedef sunucuda (master veya singlenode) `kubectl` kurulu ve konfigüre edilmiş olmalıdır.
- Ansible inventory'nizde `[master]` veya `[singlenode]` grubu tanımlanmış olmalıdır.
- Playbook, non-interactive SSH'te `.bashrc` yüklenmediği için (özellikle k3s) `KUBECONFIG` yolunu `~/.kube/config` olarak açıkça set eder. Klasik kubeadm kurulumlarında da aynı varsayılan yol kullanılır.

Playbook artık pod bilgisi almadan önce `kubectl cluster-info` ile bir erişim ön kontrolü yapar. `kubectl` erişimi yoksa (KUBECONFIG eksik/yanlış veya cluster'a ulaşılamıyor) anlamlı bir uyarı mesajı basılır ve pod sorgusu atlanır.

## Çalıştırma Komutu

```bash
# Müşteri A için çalıştırma
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/01_check_pod_health.yml

# Müşteri B için çalıştırma
ansible-playbook -i inventories/musteri_b/hosts.ini playbooks/01_check_pod_health.yml
```

## Örnek Çıktı

Komut çalıştırıldığında, öncelikle "Ping pong" adımıyla bağlantı testi yapılır. Başarılı ise `kubectl get pods -A -o wide` çıktısı ekrana yazdırılır:

```text
TASK [Ping pong] ***************************************************************
ok: [192.168.1.10]

TASK [Kubeconfig / kubectl erişim kontrolü] *************************************
ok: [192.168.1.10]

TASK [Get all pods in all namespaces with wide output] *************************
ok: [192.168.1.10]

TASK [Display pod health status] ***********************************************
ok: [192.168.1.10] => {
    "msg": [
        "NAMESPACE     NAME                               READY   STATUS    RESTARTS   AGE   IP            NODE      NOMINATED NODE   READINESS GATES",
        "kube-system   calico-node-abcd1                  1/1     Running   0          12d   192.168.1.10  master    <none>           <none>",
        "argocd        argocd-server-54d68c4847-p9qwx     1/1     Running   0          5d    10.244.1.5    worker1   <none>           <none>"
    ]
}
```
