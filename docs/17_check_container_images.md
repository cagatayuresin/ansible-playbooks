---
lang: en
title: "17 · check_container_images"
parent: Playbook Guides
nav_order: 17
---

# 17_check_container_images.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Docker](https://img.shields.io/badge/Runtime-Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Purpose

Inventories **container images** installed on each host:

| Column | Meaning |
|---|---|
| `IN_USE` | `yes` = at least one container on this host (running or stopped) uses this image; `no` = no current reference |
| `CREATED_AT/AGE` | Docker: absolute create time. containerd/k3s: most versions have no `createdAt` → `ctr content` **AGE** (e.g. `6 months`, `5 weeks`) |
| `SIZE` | Disk size |
| `IMAGE` | Repo:tag (and short image id) |

Runtime is detected automatically:

- **Docker** if present → `docker images` + `docker ps -a`
- **crictl / containerd** (K8s/k3s) if present → `crictl images` + `crictl ps -a`

If both exist, both sections are printed. If neither exists, the host is skipped / a “not found” message is shown.

Read-only; does not delete or prune images.

## Host scope (important)

The inventory is **only for the host(s) the playbook runs on**. Each node has its own image store; seeing images on master does not show worker images. For the whole cluster, include every node in inventory and run with `hosts: all` (or an appropriate `--limit`). The same rule applies for deletion: [18_prune_unused_images](18_prune_unused_images.md).

Shared task: [tasks/container_images_inventory.yml](../playbooks/tasks/container_images_inventory.yml)

## Difference from 03

[03_check_docker_containers](03_check_docker_containers.md) is about container **processes** and port links.  
**17** is the image **layer**: which images are on disk, which are in use, when they arrived — for prune / drift / disk-full diagnosis.

## Requirements

- `hosts: all` (master, worker, singlenode, datanode…)
- `become: true` (sudo) — crictl/containerd usually need root
- `python3` on the target (for report assembly; default on modern Ubuntu)

## How to run

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/17_check_container_images.yml

# Workers only:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/17_check_container_images.yml --limit workers
```

## Multi-host

Each report starts with:

```text
# HOST: <inventory name/IP>
# hostname: <server hostname>
```

## How to read the output

- **IN_USE=yes** is listed first — live / recently stopped workloads.
- **IN_USE=no** → prune candidate; before deleting, check whether another node still uses the same image (separate cluster-wide `kubectl get pods -A -o jsonpath='{..image}'`).
- The same image can have several tags; the id column (`abcdef123456`) helps matching.
- `<none>:<none>` / `<untagged>` → dangling image; usually safe to clean.
- CREATED_AT is a hint for “when it was pulled/built”; it is not always the registry push time.

## Sample (shortened)

```text
################################################################################
# HOST: 188.240.81.253
# hostname: cagatayuresincom
################################################################################
Runtime: crictl/containerd

=== containerd / crictl (K8s) ===
IN_USE  CREATED_AT                SIZE        IMAGE
------  ------------------------  ----------  -----
yes     2026-01-15 10:00:00 UTC   77.0MB      rancher/mirrored-metrics-server:v0.8.0  (7b9c9c4b9c)
no      2025-06-01 08:00:00 UTC   120.0MB     old/unused:1.0  (aabbccddeeff)
Summary: total=40 in_use=18 unused=22
```

## Notes

- Collecting dates with `crictl inspecti` can take a while on hosts with many images.
- The report is host-local; to answer “is this image used anywhere in the cluster?” run 17 on every node and combine the `IN_USE` rows.

## Deleting unused images

Candidate list / delete: [18_prune_unused_images](18_prune_unused_images.md)

```bash
# Candidates only (does not delete)
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/18_prune_unused_images.yml

# Delete
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/18_prune_unused_images.yml \
  --extra-vars 'image_prune_confirm=true'
```
