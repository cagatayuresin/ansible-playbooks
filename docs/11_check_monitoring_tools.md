---
lang: en
title: "11 · check_monitoring_tools"
parent: Playbook Guides
nav_order: 11
---

# 11_check_monitoring_tools.yml - Usage Guide

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat)

## Purpose

This playbook does two jobs:

1. **Prepares the toolset** — checks whether common Linux performance/monitoring tools are installed; installs missing ones with `apt`.
2. **Takes a snapshot** — runs a short, read-only command with each installed tool and prints the output (does not open a live TUI).

[10_check_system_health](10_check_system_health.md) is the “current health summary” (load, RAM, disk, top processes…). This playbook keeps the **monitoring tools you will use later over SSH** installed on the node and prints sample output. Using both together is useful: 10 for the overall picture, 11 for detailed diagnostics.

⚠️ It **actually installs** missing packages (`apt install`). The sample commands do not change the system; the install step does.

## Multi-host output

The **first block** of the report is machine identity (`HOST` = inventory name/IP, `hostname` = the server's own name). When you run it on several nodes, use that to see which tool output belongs to which machine.

## Per-tool approach

| Tool | Package | What the playbook does | When it helps |
|---|---|---|---|
| vmstat | `procps` | `vmstat 1 3` | CPU, memory, swap, I/O wait overview |
| iostat | `sysstat` | `iostat -xz 1 2` | Per-disk/device I/O, util%, await |
| sar | `sysstat` | `sar 1 2` | CPU breakdown (user/system/iowait/idle) |
| htop | `htop` | Install only | Interactive process view (run `htop` yourself over SSH) |
| dstat | `dstat` | `dstat -cdngy 1 1` | CPU+disk+net+sys on one line |
| iotop | `iotop` | `iotop -b -n 1 -o` | Which process is reading/writing disk |
| atop | `atop` | System summary (PID list truncated) | CPU/mem/disk/net panel; atop logs for history |
| perf | `linux-tools-*` | `perf stat -a -- sleep 1` | Hardware/software counters, CPU efficiency |
| bpftrace | `bpftrace` | `--version` only | Deep kernel/eBPF tracing (you write the script) |
| glances | `glances` | Short sample via `--stdout` | CPU/mem/load at a glance |

## Requirements

- `hosts: all` — runs on every node.
- `become: true` (sudo) is required for apt installs and for `iotop` / `atop` / `perf` → inventory must have `ansible_become_pass`.
- If a tool cannot be installed (missing from the repo, kernel package mismatch) the playbook **does not fail**; that row shows `install failed` plus any error message.

## How to run

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/11_check_monitoring_tools.yml

# Specific host/group:
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/11_check_monitoring_tools.yml --limit singlenode
```

---

## How to read the output

The report prints a **status** (`installed` / `install failed`) and, when available, a **sample** for each tool. The keys below are “what to look at / what is a red flag”. Values depend on workload; remember to normalize against core count.

### vmstat (`vmstat 1 3`)

The first line may be an average since boot; look at the **last 1–2 lines**.

| Column | Meaning | Watch for |
|---|---|---|
| `r` | Runnable / running processes | Persistently well above core count → CPU queue |
| `b` | Uninterruptible sleep (usually I/O) | Persistently >0 → disk or lock wait |
| `si` / `so` | Swap in / out | Regular `so` > 0 → not enough memory |
| `us` / `sy` | User / system CPU % | Both high + low `id` → busy CPU |
| `id` | Idle % | Low idle = busy CPU |
| `wa` | I/O wait % | High `wa` → suspected disk/network I/O bottleneck |
| `st` | Steal (VM) | High steal → noisy neighbor on the hypervisor |

### iostat (`iostat -xz 1 2`)

`-x` extended, `-z` hides zero activity. The first sample is often a summary; the **second sample** is closer to “right now”.

| Field | Meaning | Watch for |
|---|---|---|
| `%util` | Percent of time the device was busy | Persistently ~100 → disk saturated |
| `await` / `aqu-sz` | Average wait / queue | High await + full queue → slow storage |
| `r/s` `w/s` | Read/write IOPS | Sudden spike → use `iotop` for the process |
| `rkB/s` `wkB/s` | Throughput | Does it match a large backup/compaction? |

### sar (`sar 1 2`)

CPU percentages (average across all cores).

| Field | Meaning | Watch for |
|---|---|---|
| `%user` / `%system` | Application / kernel CPU | Persistently high → profile (`perf`, `htop`) |
| `%iowait` | CPU waiting on I/O | High → look at disk (`iostat`) |
| `%idle` | Idle | Low idle = capacity full |
| `%steal` | VM steal | Hypervisor pressure |

### htop

The playbook does not produce a sample (TUI). Over SSH, `htop`: colored bars, process tree, sort with F6. Use it for “who is eating CPU/RAM right now?”.

### dstat

CPU / disk / net / system on one line. `dstat` may have been dropped from the package set on some newer Ubuntu releases (`install failed` is expected); `pcp`/`dstat` alternatives or `vmstat`+`iostat` are enough.

### iotop (`-b -n 1 -o`)

Only processes doing disk I/O (`-o`). High `DISK READ` / `DISK WRITE` rows → which pod/process is stressing the disk. An empty list = no meaningful disk I/O at that moment.

### atop (system summary)

CPU/MEM/DSK/NET blocks. The process table is truncated on purpose (noise). Many network interfaces (for example Calico veth) lengthen the NET section; that is not an error. For historical analysis, look at `atop` logs on the host (depends on package install).

### perf (`perf stat -a -- sleep 1`)

1-second system-wide counter summary. Output is often on **stderr**; the playbook includes that in the report.

| Signal | Rough interpretation |
|---|---|
| `cycles` / `instructions` | Low IPC (few instructions / many cycles) → stall, cache, I/O wait |
| `cache-misses` | High miss rate → memory access cost |
| `context-switches` / `cpu-migrations` | Excessively high → over-scheduling / thread thrash |
| `<not supported>` | No hardware counters in a VM/cloud — **not an error** |

### bpftrace

Only the version is verified; no automatic script (a wrong one-liner is risky in production). If installed, run I/O or syscall tracing scripts yourself over SSH.

### glances (`--stdout` sample)

| Field | Meaning |
|---|---|
| `cpu.total` | Total CPU usage % |
| `mem.percent` / `mem.used` | Memory fullness |
| `load.min1` | 1-min load — compare with core count (e.g. load 8 on 8 cores ≈ fully busy) |

---

## Sample report (shortened)

```text
TASK [Monitoring tools report] ***
ok: [203.0.113.10] => {
  "msg": [
    "=== vmstat ===\nStatus: installed\nComment: r/b queue; si/so swap; us/sy/id/wa CPU\nprocs -----------memory---------- ...",
    "=== iostat ===\nStatus: installed\nComment: look at %util and await\n...",
    "=== htop ===\nStatus: installed (interactive; run manually over SSH)",
    "=== perf ===\nStatus: installed\n... <not supported> lines are normal on a VM ...",
    ...
  ]
}
```

## Notes

- `perf stat` output goes to stderr; the report merges it.
- `glances --stdout` is bounded with `timeout` so it does not loop forever.
- `dstat` / `linux-tools-<kernel>` may be missing from apt in some environments → `install failed` + error line; other tools are unaffected.
- On re-run, `apt` is a no-op for already-installed packages; sample commands refresh every time.
