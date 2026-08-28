# Ansible Playbooks

Turkish README: [README.tr.md](README.tr.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
[![CI](https://github.com/cagatayuresin/ansible-playbooks/actions/workflows/ci.yml/badge.svg)](https://github.com/cagatayuresin/ansible-playbooks/actions)
[![Docs](https://img.shields.io/badge/docs-GitHub_Pages-blue.svg)](https://cagatayuresin.github.io/ansible-playbooks/)

![Ansible](https://img.shields.io/badge/Ansible-E3000F?style=flat&logo=ansible&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![On-Premises](https://img.shields.io/badge/Deployment-On--Prem-4B5563?style=flat)
![Air-Gapped](https://img.shields.io/badge/Environment-Air--Gap_Friendly-10B981?style=flat)

A collection of Ansible playbooks for health checks, reporting, and maintenance of Kubernetes clusters and servers.

Full usage guides for every playbook are on **[GitHub Pages](https://cagatayuresin.github.io/ansible-playbooks/)**. Documentation is English by default; Turkish lives in [`docs/tr/`](docs/tr/) and on GitHub Pages via the **Türkçe** language switch.

## Installation

OS-specific install steps: **[docs/00_installation.md](docs/00_installation.md)**

Quick start:

```bash
ansible-playbook -i inventories-example/musteri_a/hosts.ini playbooks/01_check_pod_health.yml
```

## Structure

```
playbooks/           Playbook files (01-53, numbered)
playbooks/tasks/     Shared/reusable task lists (called via import_tasks)
playbooks/files/     Static scripts and config files copied to target hosts
inventories-example/ Example inventory files (musteri_a is included as a sample)
inventories/         Real environment inventories (all gitignored)
docs/                Per-playbook usage guides (English by default; numbers match playbooks)
docs/tr/             Turkish translations of the same guides
```

## Playbooks

| # | Playbook | Description | Read-only? |
|---|---|---|---|
| 00 | — | [Installation instructions](docs/00_installation.md) | — |
| 01 | [check_pod_health](playbooks/01_check_pod_health.yml) | Kubernetes pod health | ✅ |
| 02 | [check_open_nodeports](playbooks/02_check_open_nodeports.yml) | Finds open NodePorts and produces browser links | ✅ |
| 03 | [check_docker_containers](playbooks/03_check_docker_containers.yml) | Docker container status and port links | ✅ |
| 04 | [check_k8s_versions](playbooks/04_check_k8s_versions.yml) | kubectl/kubeadm/kubelet/containerd/runc/etcd version report | ✅ |
| 05 | [check_k8s_services](playbooks/05_check_k8s_services.yml) | Status of K8s/container services and recent logs | ✅ |
| 06 | [update_k8s_services](playbooks/06_update_k8s_services.yml) | K8s stack update with kubeadm | ⚠️ No — changes the cluster |
| 07 | [check_calico](playbooks/07_check_calico.yml) | Calico version, optional update | ⚠️ Changes only if `calico_manifest_url` is set |
| 08 | [check_server_time](playbooks/08_check_server_time.yml) | Server time/timezone and time-sync service | ✅ |
| 09 | [set_server_timezone](playbooks/09_set_server_timezone.yml) | Sets the timezone to Europe/Istanbul | ⚠️ No — changes a system setting |
| 10 | [check_system_health](playbooks/10_check_system_health.yml) | OS/CPU/RAM/disk/process/virtualization report | ✅ |
| 11 | [check_monitoring_tools](playbooks/11_check_monitoring_tools.yml) | Installs/checks monitoring tools and produces sample output | ⚠️ Installs missing tools |
| 12 | [get_argocd_password](playbooks/12_get_argocd_password.yml) | Reads the ArgoCD admin password | ✅ |
| 13 | [check_journal_errors](playbooks/13_check_journal_errors.yml) | journalctl kernel + system error/warning logs | ✅ |
| 14 | [check_metrics_server](playbooks/14_check_metrics_server.yml) | Whether metrics-server is installed/Available | ✅ |
| 15 | [get_metrics_server_stats](playbooks/15_get_metrics_server_stats.yml) | kubectl top node/pod statistics | ✅ |
| 16 | [ensure_metrics_server](playbooks/16_ensure_metrics_server.yml) | Installs if missing, then top statistics | ⚠️ Installs if missing |
| 17 | [check_container_images](playbooks/17_check_container_images.yml) | Host image inventory (installed/in-use/age) | ✅ |
| 18 | [prune_unused_images](playbooks/18_prune_unused_images.yml) | Lists unused images / deletes with confirmation | ⚠️ Deletes when `image_prune_confirm=true` |
| 19 | [check_network_connectivity](playbooks/19_check_network_connectivity.yml) | Internet access profile via DNS/TCP/HTTP/proxy | ✅ |
| 20 | [check_host_ports_firewall](playbooks/20_check_host_ports_firewall.yml) | Listening ports, bind type, process + iptables/nft/UFW | ✅ |
| 21 | [check_tls_certificates](playbooks/21_check_tls_certificates.yml) | K8s/PKI + Ingress domain/expiry + TLS secrets | ✅ |
| 22 | [check_k8s_warning_events](playbooks/22_check_k8s_warning_events.yml) | Kubernetes Warning event summary | ✅ |
| 23 | [check_storage_health](playbooks/23_check_storage_health.yml) | Disk/inode + runtime disk + PV/PVC | ✅ |
| 24 | [check_node_capacity](playbooks/24_check_node_capacity.yml) | Node conditions + capacity/requests/usage | ✅ |
| 25 | [check_etcd_controlplane](playbooks/25_check_etcd_controlplane.yml) | etcd / control-plane health (k3s+kubeadm) | ✅ |
| 26 | [check_cronjobs_jobs](playbooks/26_check_cronjobs_jobs.yml) | CronJob inventory + Failed Jobs | ✅ |
| 27 | [check_cluster_dns](playbooks/27_check_cluster_dns.yml) | CoreDNS / cluster DNS | ✅ |
| 28 | [check_network_policies](playbooks/28_check_network_policies.yml) | NetworkPolicy inventory | ✅ |
| 29 | [backup_k8s_etcd](playbooks/29_backup_k8s_etcd.yml) | Takes an etcd backup (k3s/kubeadm) | ⚠️ No — writes a snapshot to disk and prunes old backups |
| 30 | [check_large_files](playbooks/30_check_large_files.yml) | Finds files 1GB+ on the system | ✅ |
| 31 | [check_external_endpoints](playbooks/31_check_external_endpoints.yml) | Tests access to external API/web services | ✅ |
| 32 | [verify_etcd_backup](playbooks/32_verify_etcd_backup.yml) | Latest etcd snapshot integrity and optional isolated restore test | ⚠️ Restore test is optional |
| 33 | [check_upgrade_readiness](playbooks/33_check_upgrade_readiness.yml) | Pre-upgrade blocker and deprecated API check | ✅ |
| 34 | [check_workload_resilience](playbooks/34_check_workload_resilience.yml) | Probe, resource, replica, PDB, and image resilience checks | ✅ |
| 35 | [check_service_endpoints](playbooks/35_check_service_endpoints.yml) | Service / EndpointSlice ready-backend health | ✅ |
| 36 | [check_pod_security_posture](playbooks/36_check_pod_security_posture.yml) | Pod Security Admission and container security posture | ✅ |
| 37 | [check_rbac_risks](playbooks/37_check_rbac_risks.yml) | cluster-admin, wildcard, and privilege-escalation RBAC risks | ✅ |
| 38 | [check_control_plane_security](playbooks/38_check_control_plane_security.yml) | API server, audit, encryption-at-rest, and PKI permissions | ✅ |
| 39 | [diagnose_unschedulable_pods](playbooks/39_diagnose_unschedulable_pods.yml) | Root-cause analysis for Pending and unschedulable pods | ✅ |
| 40 | [check_node_baseline_drift](playbooks/40_check_node_baseline_drift.yml) | Node OS/kernel/cgroup/containerd/kubelet drift comparison | ✅ |
| 41 | [patch_and_reboot_nodes](playbooks/41_patch_and_reboot_nodes.yml) | Serial drain, package update, reboot, and uncordon | ⚠️ Changes with explicit confirmation |
| 42 | [generate_support_bundle](playbooks/42_generate_support_bundle.yml) | Redacted Kubernetes/system diagnostic archive | ⚠️ Writes an archive on the controller |
| 43 | [install_kubectl_aliases](playbooks/43_install_kubectl_aliases.yml) | kubectl shell alias pack (login shell rc) | ⚠️ Writes a dotfile; revert with `shell_aliases_state=absent` |
| 44 | [install_helm_aliases](playbooks/44_install_helm_aliases.yml) | Helm alias pack | ⚠️ Writes a dotfile; reversible |
| 45 | [install_docker_aliases](playbooks/45_install_docker_aliases.yml) | Docker/Compose alias pack | ⚠️ Writes a dotfile; reversible |
| 46 | [install_git_aliases](playbooks/46_install_git_aliases.yml) | Git alias pack | ⚠️ Writes a dotfile; reversible |
| 47 | [install_system_aliases](playbooks/47_install_system_aliases.yml) | Shell/system alias pack | ⚠️ Writes a dotfile; reversible |
| 48 | [install_python_aliases](playbooks/48_install_python_aliases.yml) | Python/venv alias pack | ⚠️ Writes a dotfile; reversible |
| 49 | [install_virt_aliases](playbooks/49_install_virt_aliases.yml) | libvirt/virt-manager alias pack | ⚠️ Writes a dotfile; reversible |
| 50 | [install_helper_functions](playbooks/50_install_helper_functions.yml) | duh/whoport/bak/extract helpers | ⚠️ Writes a dotfile; reversible |
| 51 | [install_sysupdate_function](playbooks/51_install_sysupdate_function.yml) | Interactive `sysupdate` shell function | ⚠️ Writes a dotfile; reversible |
| 52 | [run_sysupdate](playbooks/52_run_sysupdate.yml) | APT/snap/flatpak maintenance (confirm lock) | ⚠️ Changes the host when `sysupdate_confirm=true` |
| 53 | [remove_shell_aliases](playbooks/53_remove_shell_aliases.yml) | Lists / deletes all Ansible alias packs | ⚠️ Removes all packs when confirmed |

Each playbook’s full usage guide (requirements, sample output, notes) is the matching numbered file under `docs/`.

## CI

On every push/PR, [GitHub Actions](.github/workflows/ci.yml) runs `yamllint`, `ansible-lint`, example inventory validation, helper script checks, documentation mapping, Kubernetes upgrade policy behavior tests, and `--syntax-check` for every playbook. CI tool versions are pinned in [requirements-ci.txt](requirements-ci.txt).

## Inventories

- `inventories-example/` — Example inventory files kept in the repo (e.g. `musteri_a` with placeholder host/password values).
- `inventories/` — Reserved for real customer/production inventories. The entire directory is gitignored and exists only locally.

Copy `inventories-example/musteri_a/hosts.ini` as a template and create a new folder under `inventories/` for your environment.

In air-gapped environments, replace install-playbook manifest URLs that need an external source with an internal mirror or a file path already copied onto the target host. Required container images must also be available in the environment’s own registry.
