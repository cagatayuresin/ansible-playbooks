# Ansible Playbooks

Kubernetes cluster'ları ve sunucular için sağlık kontrolü, raporlama ve bakım amaçlı Ansible playbook koleksiyonu.

## Kurulum

İşletim sistemine göre ayrı kurulum talimatları için: **[docs/00_installation.md](docs/00_installation.md)**

Hızlı başlangıç:

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/01_check_pod_health.yml
```

## Yapı

```
playbooks/       Playbook dosyaları (01-28, numaralandırılmış)
playbooks/tasks/ Paylaşılan/tekrar kullanılan görev listeleri (import_tasks ile çağrılır)
inventories/     Ortam bazlı inventory'ler (musteri_a örnek olarak repoda, diğerleri gitignore'lu)
docs/            Her playbook için kullanım kılavuzu (numarayla eşleşir)
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

Her playbook'un tam kullanım kılavuzu (gereksinimler, örnek çıktı, notlar) `docs/` klasöründe numarayla eşleşen dosyadadır.

## CI

Her push/PR'da [GitHub Actions](.github/workflows/ci.yml) ile `yamllint` + `ansible-lint` + tüm playbook'lar için `--syntax-check` çalışır.

## Inventory'ler

- `inventories/musteri_a/` — repoda tutulan örnek inventory (placeholder host/şifre değerleriyle).
- Diğer gerçek müşteri/production ortam inventory'leri `.gitignore` ile bu repodan hariç tutulmuştur, sadece yerel olarak bulunur.

Kendi ortamınız için `musteri_a/hosts.ini`'yi örnek alıp `inventories/` altında yeni bir klasör oluşturun.
