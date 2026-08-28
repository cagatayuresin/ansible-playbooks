---
lang: en
title: "03 · check_docker_containers"
parent: Playbook Guides
nav_order: 3
---

# 03_check_docker_containers.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Docker](https://img.shields.io/badge/Runtime-Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Purpose

This playbook checks whether Docker is installed on the inventory hosts. If Docker is present, it runs a `docker ps -a`-style command and prints a table of container names, health/uptime (Status/Uptime), and published ports. It also generates clickable browser links for ports bound to the public address (`0.0.0.0`).

## Requirements

- Docker should be installed on the target hosts. (If it is not, the playbook does not fail; it only reports that Docker is missing.)
- Your Ansible inventory must define the relevant groups (for example `workers`, `master`).

The container table is collected separately with Docker's own `table` format (for display). Link generation uses structured JSON from `docker ps --format '{% raw %}{{json .}}{% endraw %}'` (replacing the earlier `sed` regex approach). That way every published port on a multi-port container gets its own link; the old approach captured only the first port per line.

## How to run

```bash
# Run on all servers (master + workers + datanode):
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/03_check_docker_containers.yml

# Limit to the workers group (worker1, worker2, worker3):
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/03_check_docker_containers.yml --limit workers
```

## Sample output

A ping connectivity test runs first. If Docker is installed, a formatted container list is printed:

```text
TASK [Ping connectivity test] **************************************************
ok: [192.168.1.21]

TASK [Check if Docker is installed] ********************************************
ok: [192.168.1.21]

TASK [Get Docker containers info as table] *************************************
ok: [192.168.1.21]

TASK [Display Docker containers status] ****************************************
ok: [192.168.1.21] => {
    "msg": "NAMES                  STATUS                  PORTS\nnginx-proxy            Up 4 days (healthy)     0.0.0.0:80->80/tcp, :::80->80/tcp\npayment-api            Up 2 hours              0.0.0.0:8080->8080/tcp\nold-container          Exited (0) 5 days ago   "
}

TASK [Get Docker containers info as JSON] **************************************
ok: [192.168.1.21]

TASK [Parse container JSON output] *********************************************
ok: [192.168.1.21]

TASK [Generate browser accessible links for containers] ************************
ok: [192.168.1.21] => (item=nginx-proxy)
ok: [192.168.1.21] => (item=payment-api)
ok: [192.168.1.21] => (item=old-container)

TASK [Display container links] *************************************************
ok: [192.168.1.21] => {
    "msg": "You can reach the following container ports in a browser:\n\n- nginx-proxy -> http://192.168.1.21:80\n- payment-api -> http://192.168.1.21:8080"
}

TASK [Docker not found message] ************************************************
skipping: [192.168.1.21]
```
