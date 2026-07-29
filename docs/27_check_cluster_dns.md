# 27_check_cluster_dns.yml - Kullanım Kılavuzu

## Amaç

Cluster **içi** DNS (CoreDNS / kube-dns):

- Service + pod + endpoints
- Corefile özeti
- Node üzerinden kube-dns ClusterIP’ye `dig`/`nslookup` ile `kubernetes.default` çözümleme
- NodeLocal DNS varsa listeler

Dış internet DNS’i için [19](19_check_network_connectivity.md).

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/27_check_cluster_dns.yml
```

Script: `playbooks/files/k8s_cluster_dns_check.py`
