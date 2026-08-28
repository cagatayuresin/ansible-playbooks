---
lang: en
title: "01 · check_pod_health"
parent: Playbook Guides
nav_order: 1
---

# 01_check_pod_health.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

This playbook reports the current status and health of pods in all namespaces of your Kubernetes cluster (typically run on `master` or `singlenode`): whether they are healthy, restart counts, the node they run on, and so on.

## Requirements

- `kubectl` must be installed and configured on the target host (master or singlenode).
- Your Ansible inventory must define a `[master]` or `[singlenode]` group.
- The playbook explicitly sets `KUBECONFIG` to `~/.kube/config` because `.bashrc` is not loaded in non-interactive SSH (especially on k3s). Classic kubeadm installs use the same default path.

The playbook now runs a `kubectl cluster-info` access check before collecting pod data. If `kubectl` is unavailable (missing/wrong KUBECONFIG or the cluster is unreachable), a clear warning is printed and the pod query is skipped.

## How to run

```bash
# Run for customer A
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/01_check_pod_health.yml

# Run for customer B
ansible-playbook -i inventories/musteri_b/hosts.ini playbooks/01_check_pod_health.yml
```

## Sample output

When the command runs, a ping connectivity test runs first. If it succeeds, the output of `kubectl get pods -A -o wide` is printed:

```text
TASK [Ping connectivity test] **************************************************
ok: [192.168.1.10]

TASK [Check kubeconfig / kubectl access] ***************************************
ok: [192.168.1.10]

TASK [Get all pods in all namespaces with wide output] *************************
ok: [192.168.1.10]

TASK [Display pod health status] ***********************************************
ok: [192.168.1.10] => {
    "msg": [
        "NAMESPACE     NAME                               READY   STATUS    RESTARTS   AGE   IP            NODE      NOMINATED NODE   READINESS GATES",
        "kube-system   calico-node-abcd1                  1/1     Running   0          12d   192.168.1.10  master    <none>           <none>",
        "argocd        argocd-server-54d68c4847-p9qwx     1/1     Running   0          5d    10.244.1.5    worker1   <none>           <none>"
    ]
}
```
