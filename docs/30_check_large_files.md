---
lang: en
title: "30 · check_large_files"
parent: Playbook Guides
nav_order: 30
---

# 30_check_large_files.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

Finds very large, recently updated files that may be filling disks on servers.

**Playbook:** `playbooks/30_check_large_files.yml`

## What it does

* Scans the whole disk for files larger than a given size (e.g. 1GB).
* Lists only files changed in the last `X` days.
* That makes it easier to catch suddenly growing logs instead of old, static large files (e.g. ISO images).

## Parameters (optional)

Override these variables (vars) to change the filter:

* `min_size`: Minimum size to search for (default: `1G`)
* `max_age_days`: Changed in the last X days (default: `30`)

## How to run

```bash
# Search only for files larger than 500MB:
ansible-playbook ... playbooks/30_check_large_files.yml -e "min_size=500M"
```
