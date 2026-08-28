---
lang: en
title: "06 · update_k8s_services"
parent: Playbook Guides
nav_order: 6
---

# 06_update_k8s_services.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## ⚠️ This playbook upgrades a live Kubernetes cluster

It is not read-only; it actually upgrades the `kubeadm`, `kubelet`, `kubectl`, and `containerd` packages and drain/uncordon nodes one at a time. Docker is out of scope. Calico is covered separately in [07_check_calico.yml](../playbooks/07_check_calico.yml).

Always dry-run with `--check --diff` first, and try it on a non-critical cluster (for example a single-node lab) before production.

## Purpose and approach

Follows the official Kubernetes `kubeadm` upgrade flow:

1. **Control plane (`master`/`singlenode`, `serial: 1` — nodes are processed one at a time):**
   - First control-plane node: `kubeadm upgrade plan` + `kubeadm upgrade apply v<version>`
   - Additional control-plane nodes (if any): `kubeadm upgrade node`
   - The node is drained (`kubectl drain`, delegated to the first control-plane node via `delegate_to`)
   - `kubeadm`/`kubelet`/`kubectl` apt packages are pinned to the target version (packages on `apt-mark hold` are temporarily unheld, upgraded, then held again)
   - `containerd` is upgraded to the latest version from the current apt repo ("latest" is used because it is not tightly coupled to the Kubernetes version)
   - kubelet is restarted and the node is uncordoned
2. **Worker nodes (`workers`, `serial: 1`):** The same steps, but always `kubeadm upgrade node` (never `apply`).

Pre- and post-upgrade versions are collected with the same shared [tasks/k8s_versions.yml](../playbooks/tasks/k8s_versions.yml) task list used by [04_check_k8s_versions.yml](../playbooks/04_check_k8s_versions.yml) (kubectl/kubeadm/kubelet/containerd/runc/etcd) — version detection is not duplicated.

`etcd` does not need a separate step — in a standard kubeadm (stacked etcd) install, etcd runs as a static pod and is updated automatically during `kubeadm upgrade apply/node`.

## Requirements / prerequisites

- The **`kube_version` variable is required** and must be exactly `X.Y.Z` (for example `1.34.3`); there is no default/"latest".
- The playbook reads the current `kubeadm` version and validates the upgrade window before making changes: major jumps, downgrades, and skipping more than one minor are rejected. Within the same minor, only the same or a newer patch is allowed; for a different minor, only the next minor is allowed.
- **If you are moving to a new minor**, update `/etc/apt/sources.list.d/kubernetes.list` to the official repo for that minor (`https://pkgs.k8s.io/core:/stable:/v1.XX/deb/`) and run `apt-get update` **before** this playbook — it does not touch your apt repo file (automatically rewriting it was considered risky because keyring/file layout differs across installs).
- Uses `become: true` (sudo) — `ansible_become_pass` must be set in inventory.
- Drain/uncordon runs on the first control-plane node via `delegate_to` as `become: true` (root), so `KUBECONFIG=/etc/kubernetes/admin.conf` is set on the task `environment:` (root typically has no `~/.kube/config`).
- Hosts without kubeadm (for example `datanode`) skip the upgrade steps automatically and do not fail.

## How to run

```bash
# See what would change first (REQUIRED first step):
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/06_update_k8s_services.yml \
  --extra-vars "kube_version=1.34.3" --check --diff

# Apply for real:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/06_update_k8s_services.yml \
  --extra-vars "kube_version=1.34.3"

# Limit to a single node (for example try one worker first):
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/06_update_k8s_services.yml \
  --extra-vars "kube_version=1.34.3" --limit worker1
```

## Notes

- `serial: 1` processes nodes one at a time in each play — the whole cluster is not upgraded at once, so disruption to running workloads is kept to a minimum.
- The package version is pinned using the full apt version string from `apt-cache madison` (for example `1.34.3-1.1`); writing only `1.34.3` usually does not match in apt.
- Always do the first run with `--check --diff` on a non-critical node/cluster.
- If `kubeadm upgrade apply` fails with a transient error (for example a connection timeout after etcd restarts), the cluster can be left partially upgraded. kubeadm is idempotent for this case — re-running the playbook with the same `kube_version` skips components that already completed (for example etcd) and continues from where it stopped.
