---
title: "35 · check_service_endpoints"
parent: Playbook Kılavuzları
nav_order: 35
---

# 35_check_service_endpoints.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Kubernetes](https://img.shields.io/badge/Kubernetes-EndpointSlice-326CE5?style=flat)

## Amaç

Service ile `discovery.k8s.io/v1` EndpointSlice kaynaklarını eşleştirir:

- EndpointSlice'ı olmayan Service
- Endpoint'i olduğu hâlde hazır backend'i olmayan Service
- Kısmen hazır endpoint grupları
- External adresi hâlâ `Pending` olan LoadBalancer
- Çoklu port içinde isimsiz port

EndpointSlice içindeki eksik veya `null` `endpoints` alanı boş backend
listesi olarak değerlendirilir ve raporda kritik bulgu olarak gösterilir.

`ExternalName` servisleri bilgi olarak gösterilir.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `service_endpoints_excluded_namespaces` | `kube-system,kube-public,kube-node-lease` | Denetim dışı namespace'ler |
| `service_endpoints_max_findings` | `300` | Maksimum bulgu |

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/35_check_service_endpoints.yml
```

Resmi referans: [Kubernetes EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)
