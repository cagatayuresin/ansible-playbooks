---
lang: en
title: Installation
nav_order: 2
---

# Installation

Running the playbooks in this repository requires a control machine with Ansible installed. The Ansible control node runs **only on Linux/macOS/WSL** — it does not run natively on Windows (managed/target hosts can be Windows, but the control node cannot).

## Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y ansible sshpass

# For a more recent version via pip:
python3 -m pip install --user ansible
```

`sshpass` is required when connecting with **password SSH** via `ansible_ssh_pass` in inventory. It is optional if you use SSH keys; the sample inventories in this repo use passwords, so installing it is recommended.

Verify:

```bash
ansible --version
sshpass -V
```

## macOS

With [Homebrew](https://brew.sh):

```bash
brew install ansible
brew install hudochenkov/sshpass/sshpass
```

If Homebrew is not installed, install it first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

`sshpass` is required when connecting with **password SSH** via `ansible_ssh_pass` in inventory. It is optional if you use SSH keys.

Verify:

```bash
ansible --version
sshpass -V
```

## Windows

The Ansible control node does not run natively on Windows. Two options:

### Option 1: WSL2 (recommended)

1. Open PowerShell **as administrator** and run:
   ```powershell
   wsl --install
   ```
2. Reboot the machine and finish the Ubuntu setup (it will prompt for a username/password).
3. In the WSL2 Ubuntu terminal, follow the **Linux (Ubuntu/Debian)** steps above (`ansible` + `sshpass`).
4. Clone this repo into the WSL2 filesystem (under `~/`) — running from the Windows side via `/mnt/c/...` can cause SSH and performance issues.

### Option 2: A remote Linux machine / VM

Install Ansible on a Linux server or VM (VirtualBox, Hyper-V, a cloud provider, and so on) and run the playbooks from there; your Windows machine is used only to SSH into that host.

## After installation

1. Clone this repository:
   ```bash
   git clone <repo-url>
   cd ansible-playbooks
   ```
2. Copy the sample inventory into a real-environment directory:
   ```bash
   mkdir -p inventories/musteri_a
   cp inventories-example/musteri_a/hosts.ini inventories/musteri_a/hosts.ini
   ```
3. Edit the sample host/IP/credentials in `inventories/musteri_a/hosts.ini` for your environment. If SSH uses a port other than the default 22, add something like `ansible_port=1993`.
4. Validate the inventory and run the first playbook:
   ```bash
   ansible-inventory -i inventories/musteri_a/hosts.ini --graph
   ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/01_check_pod_health.yml
   ```

Real customer/production inventories are intentionally excluded from this repository via `.gitignore`.

## Playbook documentation

Each playbook's purpose, requirements, and sample output are described in a matching numbered file under `docs/` (for example `playbooks/04_check_k8s_versions.yml` → `docs/04_check_k8s_versions.md`). See the table in [README.md](../README.md) for the full list.
