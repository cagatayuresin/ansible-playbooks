---
lang: en
title: "18 · prune_unused_images"
parent: Playbook Guides
nav_order: 18
---

# 18_prune_unused_images.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Docker](https://img.shields.io/badge/Runtime-Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Purpose

Using the same logic as [17_check_container_images](17_check_container_images.md), for images with `IN_USE=no`:

1. **Default:** only shows them as a **candidate list** (does not delete)
2. **Confirmed:** deletes them from the host with `docker rmi` / `crictl rmi`

⚠️ Changes the cluster / host disk (if confirmed). An image deleted by mistake will be pulled again on the next pod schedule (registry access + time/cost).

## Host scope (important)

Unused images are listed / deleted **only on the disk of the host(s) the playbook runs on**.

- Each node's containerd/Docker image store is **separate**.
- Running only on `master` / `singlenode` **does not touch worker disks**.
- To clean every node in a multi-node cluster, workers must be in inventory and the playbook must run **on each target host** with `hosts: all` (or `--limit workers` / the relevant groups).
- There is no “one command from master that cleans everyone's disk”; Ansible connects to each host separately and processes `IN_USE=no` images on that host.

Shared script/task: `files/container_images_inventory.py`, `tasks/container_images_inventory.yml`

## Safety lock

| `image_prune_confirm` | Behavior |
|---|---|
| `false` (default) | Lists unused candidates only |
| `true` | Deletes the candidates |

## How to run

```bash
# 1) See candidates first (does not delete):
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/18_prune_unused_images.yml

# 2) Actually delete:
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/18_prune_unused_images.yml \
  --extra-vars 'image_prune_confirm=true'

# Specific host:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/18_prune_unused_images.yml \
  --limit worker1 --extra-vars 'image_prune_confirm=true'
```

## What is deleted / what is not?

- **Deleted:** Images that no container on this host (running or stopped) references — `IN_USE=no` in 17.
- **Not deleted:** `IN_USE=yes` (a running or exited container still holds it).
- Some deletes can end with **ERROR** (shared layer, “image is in use”, another reference at the same time); it shows on the report line and the playbook does not fail.
- `DeadlineExceeded` / `RST_STREAM` / `CANCEL` are usually a transient RPC timeout to containerd (it does not mean the image is still “in use”). The script retries a few times; if it still happens, re-running 18 is enough.

## Relationship to 17

| Playbook | What it does |
|---|---|
| 17 | Full inventory (in use + unused) |
| 18 (confirm=false) | Unused candidates only |
| 18 (confirm=true) | Delete candidates + result |

Recommendation: run 17 or 18 without confirm first, review the list, then confirm=true.

## Notes

- This is host-local cleanup; it does not affect the same image on another node. Unused = `IN_USE=no` images **only on the host the playbook ran on**.
- On k3s/containerd, accumulated digest-only images (old CI tags) are usually cleaned here.
- `become: true` is required.
