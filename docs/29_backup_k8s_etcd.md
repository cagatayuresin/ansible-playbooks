# 29. K8s etcd Veritabanı Yedeği Alma

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

Kubernetes'in kalbi olan `etcd` veritabanının anlık görüntüsünü (snapshot) alır ve güvenli bir şekilde yedekler.

**Playbook:** `playbooks/29_backup_k8s_etcd.yml`

## Ne Yapar?
* Cluster'da `k3s` veya `kubeadm` (etcdctl) olup olmadığını otomatik algılar.
* Snapshot işlemini gerçekleştirip yedeği `/var/backups/etcd` klasörüne zaman damgasıyla kaydeder.
* İşlemi sadece master node'lar üzerindeki ilk sunucuda çalıştırarak gereksiz tekrarları önler.

## Parametreler (Opsiyonel)
Bu playbook standart olarak dışarıdan parametre beklemez.

## Örnek Çıktı

```
################################################################################
# HOST: master1
################################################################################
k3s detected. Running k3s etcd-snapshot...
SUCCESS: k3s etcd snapshot saved to /var/backups/etcd
```
