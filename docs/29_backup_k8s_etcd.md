# 29. K8s etcd Veritabanı Yedeği Alma

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

Kubernetes'in kalbi olan `etcd` veritabanının anlık görüntüsünü (snapshot) alır ve güvenli bir şekilde yedekler.

**Playbook:** `playbooks/29_backup_k8s_etcd.yml`

## Ne Yapar?
* Cluster'da `k3s` veya `kubeadm` (etcdctl) olup olmadığını otomatik algılar.
* Snapshot işlemini gerçekleştirip yedeği `/var/backups/etcd` klasörüne zaman damgasıyla kaydeder.
* Yedek dizinini `0700`, snapshot dosyalarını `0600` izinleriyle korur.
* Başarılı yedeklemeden sonra saklama süresinden eski snapshot'ları temizler.
* İşlemi sadece master node'lar üzerindeki ilk sunucuda çalıştırarak gereksiz tekrarları önler.

## Parametreler (Opsiyonel)

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `etcd_backup_retention_days` | `30` | Başarılı yedeklemeden sonra bu süreden eski snapshot'ları siler. Pozitif tam sayı olmalıdır. |

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/29_backup_k8s_etcd.yml \
  --extra-vars 'etcd_backup_retention_days=14'
```

> etcd snapshot'ı Kubernetes Secret verilerini de içerir. Yedek dizinine erişimi yalnızca yetkili kullanıcılarla sınırlandırın ve yedeği şifreli, ayrı bir ortama kopyalayın.

## Örnek Çıktı

```
################################################################################
# HOST: master1
################################################################################
k3s detected. Running k3s etcd-snapshot...
Retention: snapshots older than 30 days were removed.
SUCCESS: k3s etcd snapshot saved to /var/backups/etcd
```
