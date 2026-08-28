---
lang: en
title: "26 · check_cronjobs_jobs"
parent: Playbook Guides
nav_order: 26
---

# 26_check_cronjobs_jobs.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![k3s](https://img.shields.io/badge/Kubernetes-k3s-FFC61C?style=flat&logo=kubernetes&logoColor=black) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## Purpose

CronJob inventory (schedule, suspend, lastSchedule, active) and Job statuses; **Failed** ones are highlighted.

## Variables

| Variable | Default | Description |
|---|---|---|
| `jobs_namespace` | `""` | If set, only that ns; if empty, all |

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/26_check_cronjobs_jobs.yml
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/26_check_cronjobs_jobs.yml \
  --extra-vars 'jobs_namespace=n8n'
```

Script: `playbooks/files/k8s_cronjobs_jobs_check.py`
