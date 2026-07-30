# Ansible Playbooks

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
[![CI](https://github.com/cagatayuresin/ansible-playbooks/actions/workflows/ci.yml/badge.svg)](https://github.com/cagatayuresin/ansible-playbooks/actions)
[![Docs](https://img.shields.io/badge/docs-GitHub_Pages-blue.svg)](https://cagatayuresin.github.io/ansible-playbooks/)

![Ansible](https://img.shields.io/badge/Ansible-E3000F?style=flat&logo=ansible&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![On-Premises](https://img.shields.io/badge/Deployment-On--Prem-4B5563?style=flat)
![Air-Gapped](https://img.shields.io/badge/Environment-Air--Gapped_Ready-10B981?style=flat)

Kubernetes cluster'ları ve sunucular için sağlık kontrolü, raporlama ve bakım amaçlı Ansible playbook koleksiyonu. 

Tüm playbook'ların detaylı kullanım kılavuzlarına **[GitHub Pages Dokümantasyonu](https://cagatayuresin.github.io/ansible-playbooks/)** üzerinden erişebilirsiniz.

## Kurulum

İşletim sistemine göre ayrı kurulum talimatları için: **[docs/00_installation.md](docs/00_installation.md)**

Hızlı başlangıç:

```bash
ansible-playbook -i inventories-example/musteri_a/hosts.ini playbooks/01_check_pod_health.yml
```

## Yapı

```
playbooks/           Playbook dosyaları (01-28, numaralandırılmış)
playbooks/tasks/     Paylaşılan/tekrar kullanılan görev listeleri (import_tasks ile çağrılır)
playbooks/files/     Hedef sunuculara kopyalanacak statik betik ve yapılandırma dosyaları
inventories-example/ Örnek inventory dosyaları (musteri_a örnek olarak repoda)
inventories/         Gerçek ortam inventory'leri (tümü gitignore'lu)
docs/                Her playbook için kullanım kılavuzu (numarayla eşleşir)
```

## Playbook'lar

| # | Playbook | Açıklama | Salt-okunur mu? |
|---|---|---|---|
| 00 | — | [Kurulum talimatları](docs/00_installation.md) | — |
| 01 | [check_pod_health](playbooks/01_check_pod_health.yml) | Kubernetes pod sağlık durumu | ✅ |
| 02 | [check_open_nodeports](playbooks/02_check_open_nodeports.yml) | Açık NodePort'ları bulur, browser linki üretir | ✅ |
| 03 | [check_docker_containers](playbooks/03_check_docker_containers.yml) | Docker container durumu ve port linkleri | ✅ |
| 04 | [check_k8s_versions](playbooks/04_check_k8s_versions.yml) | kubectl/kubeadm/kubelet/containerd/runc/etcd sürüm raporu | ✅ |
| 05 | [check_k8s_services](playbooks/05_check_k8s_services.yml) | K8s/container servislerinin durumu ve son logları | ✅ |
| 06 | [update_k8s_services](playbooks/06_update_k8s_services.yml) | kubeadm ile K8s stack güncellemesi | ⚠️ Hayır — cluster'ı değiştirir |
| 07 | [check_calico](playbooks/07_check_calico.yml) | Calico sürümü, opsiyonel güncelleme | ⚠️ Sadece `calico_manifest_url` verilirse değişiklik yapar |
| 08 | [check_server_time](playbooks/08_check_server_time.yml) | Sunucu zamanı/saat dilimi ve zaman senkron servisi | ✅ |
| 09 | [set_server_timezone](playbooks/09_set_server_timezone.yml) | Saat dilimini Europe/Istanbul yapar | ⚠️ Hayır — sistem ayarını değiştirir |
| 10 | [check_system_health](playbooks/10_check_system_health.yml) | OS/CPU/RAM/disk/süreç/sanallaştırma raporu | ✅ |
| 11 | [check_monitoring_tools](playbooks/11_check_monitoring_tools.yml) | İzleme araçlarını kurar/kontrol eder, örnek çıktı ve yorum üretir | ⚠️ Eksik araçları kurar |
| 12 | [get_argocd_password](playbooks/12_get_argocd_password.yml) | ArgoCD admin şifresini okur | ✅ |
| 13 | [check_journal_errors](playbooks/13_check_journal_errors.yml) | journalctl kernel + sistem hata/uyarı logları | ✅ |
| 14 | [check_metrics_server](playbooks/14_check_metrics_server.yml) | metrics-server kurulu/Available mı | ✅ |
| 15 | [get_metrics_server_stats](playbooks/15_get_metrics_server_stats.yml) | kubectl top node/pod istatistikleri | ✅ |
| 16 | [ensure_metrics_server](playbooks/16_ensure_metrics_server.yml) | Yoksa kurar, sonra top istatistikleri | ⚠️ Eksikse kurar |
| 17 | [check_container_images](playbooks/17_check_container_images.yml) | Host imaj envanteri (yüklü/kullanımda/tarih) | ✅ |
| 18 | [prune_unused_images](playbooks/18_prune_unused_images.yml) | Kullanılmayan imajları listeler / onayla siler | ⚠️ `image_prune_confirm=true` ile siler |
| 19 | [check_network_connectivity](playbooks/19_check_network_connectivity.yml) | DNS/TCP/HTTP/proxy ile internet erişim profili | ✅ |
| 20 | [check_host_ports_firewall](playbooks/20_check_host_ports_firewall.yml) | Dinleyen portlar, bind tipi, süreç + iptables/nft/UFW | ✅ |
| 21 | [check_tls_certificates](playbooks/21_check_tls_certificates.yml) | K8s/PKI + Ingress domain/süre + TLS secret’lar | ✅ |
| 22 | [check_k8s_warning_events](playbooks/22_check_k8s_warning_events.yml) | Kubernetes Warning event özeti | ✅ |
| 23 | [check_storage_health](playbooks/23_check_storage_health.yml) | Disk/inode + runtime disk + PV/PVC | ✅ |
| 24 | [check_node_capacity](playbooks/24_check_node_capacity.yml) | Node conditions + capacity/requests/usage | ✅ |
| 25 | [check_etcd_controlplane](playbooks/25_check_etcd_controlplane.yml) | etcd / control-plane sağlık (k3s+kubeadm) | ✅ |
| 26 | [check_cronjobs_jobs](playbooks/26_check_cronjobs_jobs.yml) | CronJob envanteri + Failed Job’lar | ✅ |
| 27 | [check_cluster_dns](playbooks/27_check_cluster_dns.yml) | CoreDNS / cluster DNS | ✅ |
| 28 | [check_network_policies](playbooks/28_check_network_policies.yml) | NetworkPolicy envanteri | ✅ |
| 29 | [backup_k8s_etcd](playbooks/29_backup_k8s_etcd.yml) | etcd yedeği (k3s/kubeadm) alır | ✅ |
| 30 | [check_large_files](playbooks/30_check_large_files.yml) | Sistemdeki 1GB+ büyük dosyaları bulur | ✅ |
| 31 | [check_external_endpoints](playbooks/31_check_external_endpoints.yml) | Dış API/Web servislerine erişimi test eder | ✅ |

Her playbook'un tam kullanım kılavuzu (gereksinimler, örnek çıktı, notlar) `docs/` klasöründe numarayla eşleşen dosyadadır.

## CI

Her push/PR'da [GitHub Actions](.github/workflows/ci.yml) ile `yamllint` + `ansible-lint` + tüm playbook'lar için `--syntax-check` çalışır.

## Inventory'ler

- `inventories-example/` — Repoda tutulan örnek inventory dosyaları (örn: `musteri_a` placeholder host/şifre değerleriyle).
- `inventories/` — Gerçek müşteri/production ortam inventory'leri için ayrılmıştır. Bu klasörün tamamı `.gitignore` ile repodan hariç tutulmuştur ve sadece yerel olarak bulunur.

Kendi ortamınız için `inventories-example/musteri_a/hosts.ini`'yi örnek alıp `inventories/` altında yeni bir klasör oluşturabilirsiniz.
