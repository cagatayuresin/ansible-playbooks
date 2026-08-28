---
lang: en
title: "42 · generate_support_bundle"
parent: Playbook Guides
nav_order: 42
---

# 42_generate_support_bundle.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Writes_Archive-F59E0B?style=flat) ![Support](https://img.shields.io/badge/Support-Redacted_Bundle-6366F1?style=flat)

## Purpose

Collects Kubernetes and operating-system diagnostics from the first control-plane host and fetches a `.tar.gz` archive into `support-bundles/` on the controller.

Main data collected:

- Cluster/version/node/pod/workload lists
- Service and EndpointSlice
- Events, storage, PDB, NetworkPolicy, APIService, and CSR
- Disk, RAM, uptime, failed services, and recent journal warnings

Kubernetes Secret and ConfigMap contents are never requested. Default redaction masks IPs, email addresses, and known token/password patterns.

## Variables

| Variable | Default | Description |
|---|---|---|
| `support_bundle_redact` | `true` | Heuristic masking of sensitive data |
| `support_bundle_keep_remote` | `false` | Keeps the target archive under `/tmp` |
| `support_bundle_local_dir` | `support-bundles/` | Controller output directory |

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/42_generate_support_bundle.yml
```

Redaction is heuristic. Review the archive contents manually before sharing it with a third party. `support-bundles/` is gitignored; the directory is created with `0700` and archives with `0600`.
