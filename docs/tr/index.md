---
lang: tr
layout: home
title: Ana Sayfa
nav_order: 1
---

# Ansible Playbooks Dokümantasyonu

Kubernetes cluster'ları ve sunucular için sağlık kontrolü, raporlama ve bakım amaçlı Ansible playbook koleksiyonuna hoş geldiniz.

Dili değiştirmek için üstteki **English** / **Türkçe** bağlantılarını kullanın. Playbook çıktıları İngilizce'dir; bu kılavuzlardaki örnek çıktılar da kaynak kodla aynıdır.

## Başlangıç

- [Kurulum Talimatları](00_installation.md)

## Playbook Kılavuzları

| # | Kılavuz |
|---|---|
| 01 | [check_pod_health](01_check_pod_health.md) |
| 02 | [check_open_nodeports](02_check_open_nodeports.md) |
| 03 | [check_docker_containers](03_check_docker_containers.md) |
| 04 | [check_k8s_versions](04_check_k8s_versions.md) |
| 05 | [check_k8s_services](05_check_k8s_services.md) |
| 06 | [update_k8s_services](06_update_k8s_services.md) |
| 07 | [check_calico](07_check_calico.md) |
| 08 | [check_server_time](08_check_server_time.md) |
| 09 | [set_server_timezone](09_set_server_timezone.md) |
| 10 | [check_system_health](10_check_system_health.md) |
| 11 | [check_monitoring_tools](11_check_monitoring_tools.md) |
| 12 | [get_argocd_password](12_get_argocd_password.md) |
| 13 | [check_journal_errors](13_check_journal_errors.md) |
| 14 | [check_metrics_server](14_check_metrics_server.md) |
| 15 | [get_metrics_server_stats](15_get_metrics_server_stats.md) |
| 16 | [ensure_metrics_server](16_ensure_metrics_server.md) |
| 17 | [check_container_images](17_check_container_images.md) |
| 18 | [prune_unused_images](18_prune_unused_images.md) |
| 19 | [check_network_connectivity](19_check_network_connectivity.md) |
| 20 | [check_host_ports_firewall](20_check_host_ports_firewall.md) |
| 21 | [check_tls_certificates](21_check_tls_certificates.md) |
| 22 | [check_k8s_warning_events](22_check_k8s_warning_events.md) |
| 23 | [check_storage_health](23_check_storage_health.md) |
| 24 | [check_node_capacity](24_check_node_capacity.md) |
| 25 | [check_etcd_controlplane](25_check_etcd_controlplane.md) |
| 26 | [check_cronjobs_jobs](26_check_cronjobs_jobs.md) |
| 27 | [check_cluster_dns](27_check_cluster_dns.md) |
| 28 | [check_network_policies](28_check_network_policies.md) |
| 29 | [backup_k8s_etcd](29_backup_k8s_etcd.md) |
| 30 | [check_large_files](30_check_large_files.md) |
| 31 | [check_external_endpoints](31_check_external_endpoints.md) |
| 32 | [verify_etcd_backup](32_verify_etcd_backup.md) |
| 33 | [check_upgrade_readiness](33_check_upgrade_readiness.md) |
| 34 | [check_workload_resilience](34_check_workload_resilience.md) |
| 35 | [check_service_endpoints](35_check_service_endpoints.md) |
| 36 | [check_pod_security_posture](36_check_pod_security_posture.md) |
| 37 | [check_rbac_risks](37_check_rbac_risks.md) |
| 38 | [check_control_plane_security](38_check_control_plane_security.md) |
| 39 | [diagnose_unschedulable_pods](39_diagnose_unschedulable_pods.md) |
| 40 | [check_node_baseline_drift](40_check_node_baseline_drift.md) |
| 41 | [patch_and_reboot_nodes](41_patch_and_reboot_nodes.md) |
| 42 | [generate_support_bundle](42_generate_support_bundle.md) |
| 43 | [install_kubectl_aliases](43_install_kubectl_aliases.md) |
| 44 | [install_helm_aliases](44_install_helm_aliases.md) |
| 45 | [install_docker_aliases](45_install_docker_aliases.md) |
| 46 | [install_git_aliases](46_install_git_aliases.md) |
| 47 | [install_system_aliases](47_install_system_aliases.md) |
| 48 | [install_python_aliases](48_install_python_aliases.md) |
| 49 | [install_virt_aliases](49_install_virt_aliases.md) |
| 50 | [install_helper_functions](50_install_helper_functions.md) |
| 51 | [install_sysupdate_function](51_install_sysupdate_function.md) |
| 52 | [run_sysupdate](52_run_sysupdate.md) |
| 53 | [remove_shell_aliases](53_remove_shell_aliases.md) |

*(Ana repoya dönmek için [GitHub Deposuna Gidin](https://github.com/cagatayuresin/ansible-playbooks))*
