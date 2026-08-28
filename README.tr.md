# Ansible Playbooks

İngilizce README: [README.md](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
[![CI](https://github.com/cagatayuresin/ansible-playbooks/actions/workflows/ci.yml/badge.svg)](https://github.com/cagatayuresin/ansible-playbooks/actions)
[![Docs](https://img.shields.io/badge/docs-GitHub_Pages-blue.svg)](https://cagatayuresin.github.io/ansible-playbooks/)

![Ansible](https://img.shields.io/badge/Ansible-E3000F?style=flat&logo=ansible&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![On-Premises](https://img.shields.io/badge/Deployment-On--Prem-4B5563?style=flat)
![Air-Gapped](https://img.shields.io/badge/Environment-Air--Gap_Friendly-10B981?style=flat)

Kubernetes cluster'ları ve sunucular için sağlık kontrolü, raporlama ve bakım amaçlı Ansible playbook koleksiyonu.

Tüm playbook kullanım kılavuzları **[GitHub Pages](https://cagatayuresin.github.io/ansible-playbooks/)** üzerindedir. Varsayılan dil İngilizce'dir; Türkçe için sitedeki **Türkçe** düğmesini kullanın veya [`docs/tr/`](docs/tr/) dizinine bakın.

Playbook ve yardımcı betiklerin ekrana yazdığı bildirimler İngilizce'dir. Türkçe kılavuzlardaki örnek çıktılar da bu yüzden İngilizce kaynak çıktısıyla aynıdır.

## Kurulum

İşletim sistemine göre kurulum: **[docs/tr/00_installation.md](docs/tr/00_installation.md)** (İngilizce: [docs/00_installation.md](docs/00_installation.md))

Hızlı başlangıç:

```bash
ansible-playbook -i inventories-example/musteri_a/hosts.ini playbooks/01_check_pod_health.yml
```

## Yapı

```
playbooks/           Playbook dosyaları (01-53, numaralandırılmış)
playbooks/tasks/     Paylaşılan görev listeleri (import_tasks)
playbooks/files/     Hedefe kopyalanan betik ve yapılandırma dosyaları
inventories-example/ Örnek inventory (musteri_a)
inventories/         Gerçek ortam inventory'leri (gitignore'lu)
docs/                İngilizce kılavuzlar (varsayılan GitHub Pages)
docs/tr/             Türkçe kılavuzlar
```

## Playbook'lar

| # | Playbook | Açıklama | Salt-okunur mu? |
|---|---|---|---|
| 00 | — | [Kurulum talimatları](docs/tr/00_installation.md) | — |
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
| 11 | [check_monitoring_tools](playbooks/11_check_monitoring_tools.yml) | İzleme araçlarını kurar/kontrol eder | ⚠️ Eksik araçları kurar |
| 12 | [get_argocd_password](playbooks/12_get_argocd_password.yml) | ArgoCD admin şifresini okur | ✅ |
| 13 | [check_journal_errors](playbooks/13_check_journal_errors.yml) | journalctl kernel + sistem hata/uyarı logları | ✅ |
| 14 | [check_metrics_server](playbooks/14_check_metrics_server.yml) | metrics-server kurulu/Available mı | ✅ |
| 15 | [get_metrics_server_stats](playbooks/15_get_metrics_server_stats.yml) | kubectl top node/pod istatistikleri | ✅ |
| 16 | [ensure_metrics_server](playbooks/16_ensure_metrics_server.yml) | Yoksa kurar, sonra top istatistikleri | ⚠️ Eksikse kurar |
| 17 | [check_container_images](playbooks/17_check_container_images.yml) | Host imaj envanteri | ✅ |
| 18 | [prune_unused_images](playbooks/18_prune_unused_images.yml) | Kullanılmayan imajları listeler / onayla siler | ⚠️ `image_prune_confirm=true` ile siler |
| 19 | [check_network_connectivity](playbooks/19_check_network_connectivity.yml) | DNS/TCP/HTTP/proxy ile internet erişim profili | ✅ |
| 20 | [check_host_ports_firewall](playbooks/20_check_host_ports_firewall.yml) | Dinleyen portlar, bind tipi, süreç + firewall | ✅ |
| 21 | [check_tls_certificates](playbooks/21_check_tls_certificates.yml) | K8s/PKI + Ingress domain/süre + TLS secret’lar | ✅ |
| 22 | [check_k8s_warning_events](playbooks/22_check_k8s_warning_events.yml) | Kubernetes Warning event özeti | ✅ |
| 23 | [check_storage_health](playbooks/23_check_storage_health.yml) | Disk/inode + runtime disk + PV/PVC | ✅ |
| 24 | [check_node_capacity](playbooks/24_check_node_capacity.yml) | Node conditions + capacity/requests/usage | ✅ |
| 25 | [check_etcd_controlplane](playbooks/25_check_etcd_controlplane.yml) | etcd / control-plane sağlık | ✅ |
| 26 | [check_cronjobs_jobs](playbooks/26_check_cronjobs_jobs.yml) | CronJob envanteri + Failed Job’lar | ✅ |
| 27 | [check_cluster_dns](playbooks/27_check_cluster_dns.yml) | CoreDNS / cluster DNS | ✅ |
| 28 | [check_network_policies](playbooks/28_check_network_policies.yml) | NetworkPolicy envanteri | ✅ |
| 29 | [backup_k8s_etcd](playbooks/29_backup_k8s_etcd.yml) | etcd yedeği alır | ⚠️ Hayır — diske snapshot yazar |
| 30 | [check_large_files](playbooks/30_check_large_files.yml) | Sistemdeki 1GB+ büyük dosyaları bulur | ✅ |
| 31 | [check_external_endpoints](playbooks/31_check_external_endpoints.yml) | Dış API/Web servislerine erişimi test eder | ✅ |
| 32 | [verify_etcd_backup](playbooks/32_verify_etcd_backup.yml) | Son etcd snapshot bütünlüğü | ⚠️ Restore testi opsiyonel |
| 33 | [check_upgrade_readiness](playbooks/33_check_upgrade_readiness.yml) | Yükseltme öncesi engel ve deprecated API kontrolü | ✅ |
| 34 | [check_workload_resilience](playbooks/34_check_workload_resilience.yml) | Probe, resource, replica, PDB denetimi | ✅ |
| 35 | [check_service_endpoints](playbooks/35_check_service_endpoints.yml) | Service / EndpointSlice hazır backend sağlığı | ✅ |
| 36 | [check_pod_security_posture](playbooks/36_check_pod_security_posture.yml) | Pod Security Admission ve container güvenlik duruşu | ✅ |
| 37 | [check_rbac_risks](playbooks/37_check_rbac_risks.yml) | cluster-admin, wildcard ve privilege escalation RBAC riskleri | ✅ |
| 38 | [check_control_plane_security](playbooks/38_check_control_plane_security.yml) | API server, audit, encryption-at-rest ve PKI izinleri | ✅ |
| 39 | [diagnose_unschedulable_pods](playbooks/39_diagnose_unschedulable_pods.yml) | Pending ve başlatılamayan pod kök neden analizi | ✅ |
| 40 | [check_node_baseline_drift](playbooks/40_check_node_baseline_drift.yml) | Node OS/kernel/cgroup/containerd/kubelet drift | ✅ |
| 41 | [patch_and_reboot_nodes](playbooks/41_patch_and_reboot_nodes.yml) | Sıralı drain, paket güncelleme, reboot ve uncordon | ⚠️ Açık onayla değiştirir |
| 42 | [generate_support_bundle](playbooks/42_generate_support_bundle.yml) | Redakte edilmiş Kubernetes/sistem tanı arşivi | ⚠️ Controller'a arşiv yazar |
| 43 | [install_kubectl_aliases](playbooks/43_install_kubectl_aliases.yml) | kubectl kabuk alias paketi (login shell rc) | ⚠️ Dotfile yazar; `shell_aliases_state=absent` ile geri alınır |
| 44 | [install_helm_aliases](playbooks/44_install_helm_aliases.yml) | Helm alias paketi | ⚠️ Dotfile yazar; geri alınabilir |
| 45 | [install_docker_aliases](playbooks/45_install_docker_aliases.yml) | Docker/Compose alias paketi | ⚠️ Dotfile yazar; geri alınabilir |
| 46 | [install_git_aliases](playbooks/46_install_git_aliases.yml) | Git alias paketi | ⚠️ Dotfile yazar; geri alınabilir |
| 47 | [install_system_aliases](playbooks/47_install_system_aliases.yml) | Kabuk/sistem alias paketi | ⚠️ Dotfile yazar; geri alınabilir |
| 48 | [install_python_aliases](playbooks/48_install_python_aliases.yml) | Python/venv alias paketi | ⚠️ Dotfile yazar; geri alınabilir |
| 49 | [install_virt_aliases](playbooks/49_install_virt_aliases.yml) | libvirt/virt-manager alias paketi | ⚠️ Dotfile yazar; geri alınabilir |
| 50 | [install_helper_functions](playbooks/50_install_helper_functions.yml) | duh/whoport/bak/extract yardımcıları | ⚠️ Dotfile yazar; geri alınabilir |
| 51 | [install_sysupdate_function](playbooks/51_install_sysupdate_function.yml) | Interaktif `sysupdate` kabuk fonksiyonu | ⚠️ Dotfile yazar; geri alınabilir |
| 52 | [run_sysupdate](playbooks/52_run_sysupdate.yml) | APT/snap/flatpak bakımı (onay kilidi) | ⚠️ `sysupdate_confirm=true` ile değiştirir |
| 53 | [remove_shell_aliases](playbooks/53_remove_shell_aliases.yml) | Tüm Ansible alias paketlerini listeler / siler | ⚠️ Onayla tüm paketleri kaldırır |

Her playbook'un Türkçe kılavuzu `docs/tr/` altında numarayla eşleşir. Playbook'ların kendi bildirim metinleri İngilizce'dir.

## CI

Her push/PR'da [GitHub Actions](.github/workflows/ci.yml) `yamllint`, `ansible-lint`, örnek inventory doğrulaması, yardımcı betik kontrolleri, İngilizce ve Türkçe doküman eşleşmesi, Kubernetes yükseltme politikası testleri ve tüm playbook'lar için `--syntax-check` çalıştırır.

## Inventory'ler

- `inventories-example/` — Repodaki örnek inventory (placeholder host/şifre).
- `inventories/` — Gerçek müşteri/production inventory'leri; klasör gitignore'ludur.

`inventories-example/musteri_a/hosts.ini` şablonunu kopyalayıp `inventories/` altında kendi klasörünüzü oluşturun.

Air-gap ortamlarda dış URL isteyen kurulum playbook'larının manifest adreslerini iç mirror veya hedefteki dosya yollarıyla değiştirin. Gerekli container imajları da ortamın kendi registry'sinde olmalıdır.
