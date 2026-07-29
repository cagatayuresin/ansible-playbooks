# 25_check_etcd_controlplane.yml - Kullanım Kılavuzu

## Amaç

Salt-okunur control-plane / etcd kontrolü:

- kube-system içindeki apiserver/etcd/scheduler/controller (veya k3s) pod’ları
- `/healthz` `/readyz` `/livez`
- **k3s**: `etcd-snapshot ls`, data dir boyutu
- **kubeadm**: `etcdctl endpoint health/status/alarm`, dbSize vs in-use (defrag **ipucu**, çalıştırmaz), snapshot dosya yaşı

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/25_check_etcd_controlplane.yml
```

## Notlar

- `become: true` (PKI / k3s dizinleri)
- Defrag, restore, snapshot alma **yapılmaz**
- Script: `playbooks/files/k8s_etcd_controlplane_check.py`
