---
lang: tr
title: "12 · get_argocd_password"
parent: Playbook Kılavuzları
nav_order: 12
---

# 12_get_argocd_password.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

Bu playbook, ArgoCD'nin ilk kurulumda otomatik oluşturduğu admin şifresini (`argocd-initial-admin-secret`) okuyup base64 çözerek raporlar. Salt-okunuştur (secret'a dokunmaz, sadece okur).

## Gereksinimler

- `kubectl` erişimi olan ilk control-plane node (`master`/`singlenode` grubundaki ilk host) üzerinden çalışır.
- ArgoCD'nin `argocd` namespace'inde kurulu olması ve `argocd-initial-admin-secret`'ın henüz silinmemiş olması gerekir. Şifre değiştirilip bu secret silindiyse (ArgoCD'nin önerdiği best practice), playbook bunu tespit edip anlamlı bir uyarı verir — mevcut şifreyi öğrenemez.

## Çalıştırma Komutu

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/12_get_argocd_password.yml
```

## Örnek Çıktı

```text
TASK [ArgoCD admin password report (when: password must be retrievable)] *******
ok: [203.0.113.10] => {
    "msg": "ArgoCD admin password: xK4mQ9vR2wZ7tPa1 (username: admin, service type: NodePort). This is the one-time password created at initial install; Argo CD's official recommendation is to change it after first login and delete this secret with 'kubectl -n argocd delete secret argocd-initial-admin-secret'."
}
```

## Notlar

- Servis tipi `NodePort` ise ArgoCD UI'ye `<node-ip>:<nodeport>` üzerinden erişilir; tam portu görmek için `kubectl -n argocd get svc argocd-server` çalıştırılabilir.
- Servis tipi `ClusterIP` ise ArgoCD'ye doğrudan dışarıdan erişim yoktur, `kubectl port-forward` veya bir Ingress gerekir.
- Bu playbook şifreyi düz metin olarak Ansible çıktısına yazar (terminal/log görünür); hassas bir ortamda çalıştırılıyorsa çıktının nerede tutulduğuna/loglandığına dikkat edin.
