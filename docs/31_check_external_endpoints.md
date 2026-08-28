---
lang: en
title: "31 · check_external_endpoints"
parent: Playbook Guides
nav_order: 31
---

# 31_check_external_endpoints.yml - Usage Guide

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

Checks reachability and latency of external APIs and websites that your project depends on (payment APIs, SMS services, and similar).

**Playbook:** `playbooks/31_check_external_endpoints.yml`

## What it does

* Sends HTTP GET requests to the critical URL list defined in the playbook.
* Reports the HTTP status code (200 OK) and how long the request took in milliseconds.
* This playbook runs on `localhost`; it does not SSH to target servers. It tests the network from the machine where it runs.

## Parameters

Update the `endpoints` list inside the playbook to match your critical services.

## Sample output

```text
[SUCCESS] Google API (https://www.google.com)
Status code: 200
Elapsed time: 0.231 seconds

[ERROR] Example Endpoint (https://api.github.com/error)
Status code: 404
Elapsed time: 0.150 seconds
```
