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
playbooks/       Playbook dosyaları (01-12, numaralandırılmış)
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
| 11 | [check_monitoring_tools](playbooks/11_check_monitoring_tools.yml) | İzleme araçlarını kontrol eder, eksikse kurar | ⚠️ Eksik araçları kurar |
| 12 | [get_argocd_password](playbooks/12_get_argocd_password.yml) | ArgoCD admin şifresini okur | ✅ |

Her playbook'un tam kullanım kılavuzu (gereksinimler, örnek çıktı, notlar) `docs/` klasöründe numarayla eşleşen dosyadadır.

## CI

Her push/PR'da [GitHub Actions](.github/workflows/ci.yml) ile `yamllint` + `ansible-lint` + tüm playbook'lar için `--syntax-check` çalışır.

## Inventory'ler

- `inventories/musteri_a/` — repoda tutulan örnek inventory (placeholder host/şifre değerleriyle).
- Diğer gerçek müşteri/production ortam inventory'leri `.gitignore` ile bu repodan hariç tutulmuştur, sadece yerel olarak bulunur.

Kendi ortamınız için `musteri_a/hosts.ini`'yi örnek alıp `inventories/` altında yeni bir klasör oluşturun.
