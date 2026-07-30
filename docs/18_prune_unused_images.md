# 18_prune_unused_images.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Docker](https://img.shields.io/badge/Runtime-Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Amaç

[17_check_container_images](17_check_container_images.md) ile aynı mantıkta `IN_USE=no` olan imajları:

1. **Varsayılan:** sadece **aday listesi** olarak gösterir (silmez)
2. **Onaylı:** `docker rmi` / `crictl rmi` ile host’tan siler

⚠️ Cluster’ı / host diskini değiştirir (onay verilirse). Yanlışlıkla silinen imaj bir sonraki pod schedule’da yeniden pull edilir (registry erişimi + süre/maliyet).

## Host kapsamı (önemli)

Kullanımda olmayan imajlar **yalnızca playbook’un çalıştığı host(lar)ın kendi diskinde** listelenir / silinir.

- Her node’un containerd/Docker imaj deposu **ayrıdır**.
- Sadece `master` / `singlenode` üzerinde çalıştırmak **worker disklerine dokunmaz**.
- Çok nodeli cluster’da tüm node’ları temizlemek için inventory’de worker’lar da olmalı ve playbook `hosts: all` ile (veya `--limit workers` / ilgili gruplarla) **her hedef hostta** çalışmalı.
- Master’dan “cluster geneli tek komutla herkesin diski” temizlenmez; Ansible her hosta ayrı bağlanıp o hosttaki `IN_USE=no` imajları işler.

Ortak script/task: `files/container_images_inventory.py`, `tasks/container_images_inventory.yml`

## Güvenlik kilidi

| `image_prune_confirm` | Davranış |
|---|---|
| `false` (varsayılan) | Sadece kullanılmayan adayları listeler |
| `true` | Adayları siler |

## Çalıştırma

```bash
# 1) Önce adayları gör (silmez):
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/18_prune_unused_images.yml

# 2) Gerçekten sil:
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/18_prune_unused_images.yml \
  --extra-vars 'image_prune_confirm=true'

# Belirli host:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/18_prune_unused_images.yml \
  --limit worker1 --extra-vars 'image_prune_confirm=true'
```

## Ne silinir / ne silinmez?

- **Silinir:** Bu host’ta hiçbir container’ın (çalışan veya durmuş) referans etmediği imajlar — 17’deki `IN_USE=no`.
- **Silinmez:** `IN_USE=yes` (çalışan veya exited container hâlâ tutuyorsa).
- Bazı silmeler **HATA** ile bitebilir (paylaşılan katman, “image is in use”, aynı anda başka referans); rapor satırında görünür, playbook fail olmaz.
- `DeadlineExceeded` / `RST_STREAM` / `CANCEL` genelde containerd’ye giden geçici RPC timeout’udur (imaj hâlâ “kullanımda” demek değildir). Script bu durumda birkaç kez yeniden dener; yine olursa 18’i tekrar çalıştırmak yeterli.

## 17 ile ilişki

| Playbook | Ne yapar |
|---|---|
| 17 | Tam envanter (kullanımda + değil) |
| 18 (confirm=false) | Sadece kullanılmayan adaylar |
| 18 (confirm=true) | Adayları sil + sonuç |

Öneri: önce 17 veya 18’i onaysız çalıştır, listeye bak, sonra confirm=true.

## Notlar

- Host-local temizliktir; başka node’daki aynı imajı etkilemez. Kullanımda olmayanlar = **sadece playbook’un çalıştığı host’taki** `IN_USE=no` imajlar.
- k3s/containerd’de çok birikmiş digest-only imajlar (eski CI tag’leri) genelde burada temizlenir.
- `become: true` gerekir.
