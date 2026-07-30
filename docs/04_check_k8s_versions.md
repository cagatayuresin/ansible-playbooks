# 04_check_k8s_versions.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

Bu playbook, bir Kubernetes node'unda (control-plane veya worker) çalışan k8s stack'inin (kubectl, kubeadm, kubelet, containerd, runc, etcd) sürüm bilgilerini toplar ve raporlar.

Sürüm tespit mantığı [tasks/k8s_versions.yml](../playbooks/tasks/k8s_versions.yml) dosyasında paylaşılan bir görev listesi olarak tanımlıdır; [06_update_k8s_services.yml](../playbooks/06_update_k8s_services.yml) de aynı dosyayı güncelleme öncesi/sonrası sürümleri tespit etmek için kullanır. Böylece iki playbook aynı sürüm bilgisini iki farklı şekilde bulmuyor.

## Gereksinimler

- `hosts: all` — kubeadm/kubelet/containerd/runc sürüm kontrolleri her node'da çalışır.
- `kubectl` gerektiren adımlar (kubectl sürümü, etcd image bilgisi) yalnızca `kubectl cluster-info` başarılı olan host'larda (genelde master/singlenode) çalışır; erişim yoksa atlanır, diğer sürüm bilgileri yine de toplanır.

## Çalıştırma Komutu

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/04_check_k8s_versions.yml

# Belirli bir host/grup ile sınırlamak için:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/04_check_k8s_versions.yml --limit master
```

## Örnek Çıktı

```text
TASK [Ping pong] ***************************************************************
ok: [203.0.113.10]

TASK [Kubeconfig / kubectl erişim kontrolü] ************************************
ok: [203.0.113.10]

TASK [Sürüm raporu] ************************************************************
ok: [203.0.113.10] => {
    "msg": [
        "kubectl: clientVersion: ... gitVersion: v1.34.10 ...",
        "kubeadm: v1.34.10",
        "kubelet: Kubernetes v1.34.10",
        "containerd: containerd github.com/containerd/containerd/v2 v2.2.0 ...",
        "runc: runc version 1.3.3 ...",
        "etcd image: registry.k8s.io/etcd:3.6.5-0"
    ]
}
```
