# 16_ensure_metrics_server.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Amaç

1. metrics-server durumunu kontrol eder (14 ile aynı check task’ı)
2. Hazır değilse resmi manifest ile **kurar**
3. Gerekirse `--kubelet-insecure-tls` ekler (on-prem / self-signed kubelet)
4. Rollout + `kubectl top` hazır olana kadar bekler
5. 15 ile aynı istatistik raporunu basar

⚠️ Cluster’ı değiştirir (eksikse Deployment/APIService oluşturur). Zaten hazırsa kurulum atlanır, sadece istatistik alınır.

## Ortak görevler

- [tasks/metrics_server_check.yml](../playbooks/tasks/metrics_server_check.yml)
- [tasks/metrics_server_install.yml](../playbooks/tasks/metrics_server_install.yml)
- [tasks/metrics_server_report.yml](../playbooks/tasks/metrics_server_report.yml)

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `metrics_server_manifest_url` | GitHub `latest` `components.yaml` | Uygulanacak manifest |
| `metrics_server_kubelet_insecure_tls` | `true` | On-prem’de çoğu zaman şart; cloud’da `false` yapılabilir |

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/16_ensure_metrics_server.yml \
  --extra-vars 'metrics_server_kubelet_insecure_tls=false'
```

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/16_ensure_metrics_server.yml
```

## Notlar

- k3s bazen metrics-server’ı kendisi getirir; hazırsa bu playbook sadece top raporlar.
- `--kubelet-insecure-tls` kubelet sertifika doğrulamasını gevşetir; lab/on-prem için yaygın, sıkı prod’da alternatif (doğru CA) tercih edilir.
- Manifest URL’ini sabitlemek istersen spesifik release tag’i ver.
