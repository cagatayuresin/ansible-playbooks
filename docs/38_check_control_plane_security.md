---
title: "38 · check_control_plane_security"
parent: Playbook Kılavuzları
nav_order: 38
---

# 38_check_control_plane_security.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Security](https://img.shields.io/badge/Security-Control--Plane-7C3AED?style=flat)

## Amaç

İlk control-plane host'unda kubeadm veya k3s yapılandırmasını otomatik algılayarak şunları kontrol eder:

- Anonymous authentication
- `Node,RBAC` authorization ve `AlwaysAllow`
- Insecure port ve profiling
- Audit policy/backend
- Secret encryption-at-rest provider sırası
- NodeRestriction admission plugin
- Minimum TLS sürümü
- `admin.conf`, `k3s.yaml` ve private key dosya izinleri

Encryption provider içindeki anahtar verileri hiçbir zaman çıktıya yazılmaz.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `control_plane_security_fail_on_critical` | `false` | Kritik bulguda playbook'u başarısız yapar |

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/38_check_control_plane_security.yml

ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/38_check_control_plane_security.yml \
  --extra-vars 'control_plane_security_fail_on_critical=true'
```

Dağıtım sağlayıcıları bazı ayarları farklı yöntemlerle uygulayabilir; uyarılar cluster yapılandırmasıyla birlikte değerlendirilmelidir.

Resmi referanslar: [Encrypting Confidential Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/), [Kubernetes Auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
