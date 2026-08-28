---
lang: en
title: "12 · get_argocd_password"
parent: Playbook Guides
nav_order: 12
---

# 12_get_argocd_password.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

This playbook reads the admin password that Argo CD creates automatically on first install (`argocd-initial-admin-secret`), base64-decodes it, and reports it. It is read-only (it does not modify the secret; it only reads it).

## Requirements

- Runs on the first control-plane node with `kubectl` access (the first host in the `master`/`singlenode` group).
- Argo CD must be installed in the `argocd` namespace and `argocd-initial-admin-secret` must not have been deleted yet. If the password was changed and this secret was deleted (Argo CD's recommended practice), the playbook detects that and prints a clear warning — it cannot recover the current password.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/12_get_argocd_password.yml
```

## Sample output

```text
TASK [ArgoCD admin password report (when: password must be retrievable)] *******
ok: [203.0.113.10] => {
    "msg": "ArgoCD admin password: xK4mQ9vR2wZ7tPa1 (username: admin, service type: NodePort). This is the one-time password created at initial install; Argo CD's official recommendation is to change it after first login and delete this secret with 'kubectl -n argocd delete secret argocd-initial-admin-secret'."
}
```

## Notes

- If the service type is `NodePort`, the Argo CD UI is reached at `<node-ip>:<nodeport>`; run `kubectl -n argocd get svc argocd-server` for the exact port.
- If the service type is `ClusterIP`, there is no direct external access; use `kubectl port-forward` or an Ingress.
- This playbook writes the password in plaintext to Ansible output (visible in the terminal/logs); in a sensitive environment, watch where the output is stored/logged.
