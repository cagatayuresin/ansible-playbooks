---
lang: tr
title: "17 · check_container_images"
parent: Playbook Kılavuzları
nav_order: 17
---

# 17_check_container_images.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Docker](https://img.shields.io/badge/Runtime-Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Amaç

Her host’ta yüklü **container imajlarını** envanterler:

| Sütun | Anlam |
|---|---|
| `IN_USE` | `yes` = bu host’ta en az bir container (çalışan veya durmuş) bu imajı kullanıyor; `no` = şu an referans yok |
| `CREATED_AT/AGE` | Docker: mutlak oluşturma zamanı. containerd/k3s: çoğu sürümde `createdAt` yok → `ctr content` **AGE** (örn. `6 months`, `5 weeks`) |
| `SIZE` | Disk boyutu |
| `IMAGE` | Repo:tag (ve kısa image id) |

Runtime otomatik bulunur:

- **Docker** varsa → `docker images` + `docker ps -a`
- **crictl / containerd** (K8s/k3s) varsa → `crictl images` + `crictl ps -a`

İkisi birden varsa iki bölüm de basılır. Hiçbiri yoksa host atlanır / “yok” mesajı verilir.

Salt-okunur; imaj silmez / prune yapmaz.

## Host kapsamı (önemli)

Envanter **yalnızca playbook’un çalıştığı host(lar)** içindir. Her node kendi imaj deposuna sahiptir; master’da görmek worker’dakileri göstermez. Tüm cluster için her node’u inventory’ye alıp `hosts: all` (veya uygun `--limit`) ile çalıştırın. Silme için aynı kural: [18_prune_unused_images](18_prune_unused_images.md).

Ortak görev: [tasks/container_images_inventory.yml](../../playbooks/tasks/container_images_inventory.yml)

## 03 ile farkı

[03_check_docker_containers](03_check_docker_containers.md) container **süreçleri** ve port linkleridir.  
**17** imaj **katmanı**dır: hangi imaj diskte, hangisi kullanımda, ne zaman gelmiş — prune / drift / disk doluluğu teşhisi için.

## Gereksinimler

- `hosts: all` (master, worker, singlenode, datanode…)
- `become: true` (sudo) — crictl/containerd genelde root ister
- Hedefte `python3` (rapor birleştirmesi için; modern Ubuntu’da varsayılan)

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/17_check_container_images.yml

# Sadece worker'lar:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/17_check_container_images.yml --limit workers
```

## Çoklu makine

Her raporun başında:

```text
# HOST: <inventory adı/IP>
# hostname: <sunucu hostname>
```

## Çıktı nasıl okunur?

- **IN_USE=yes** üstte listelenir — canlı / yeni durmuş iş yükleri.
- **IN_USE=no** → prune adayı; silmeden önce başka node’un aynı imajı kullanıp kullanmadığına bak (cluster-wide `kubectl get pods -A -o jsonpath='{..image}'` ayrı kontrol).
- Aynı imajın birden fazla tag’i olabilir; id sütunu (`abcdef123456`) eşleştirmede yardımcı olur.
- `<none>:<none>` / `<untagged>` → dangling imaj; genelde temizlenebilir.
- CREATED_AT, “ne zaman pull/build edildi” ipucudur; her zaman registry push zamanı değildir.

## Örnek (kısaltılmış)

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

## Notlar

- Çok imajlı host’ta `crictl inspecti` ile tarih toplama biraz sürebilir.
- Rapor host-local’dir; cluster’ın tamamında “şu imaj bir yerde kullanılıyor mu?” sorusu için tüm node’larda 17 çalıştırıp `IN_USE` satırlarını birleştirmek gerekir.

## Kullanılmayanları silmek

Aday listesi / silme: [18_prune_unused_images](18_prune_unused_images.md)

```bash
# Sadece adaylar (silmez)
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/18_prune_unused_images.yml

# Sil
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/18_prune_unused_images.yml \
  --extra-vars 'image_prune_confirm=true'
```
