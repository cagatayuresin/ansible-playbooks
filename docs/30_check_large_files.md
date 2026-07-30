---
title: "30 · check_large_files"
parent: Playbook Kılavuzları
nav_order: 30
---

# 30. Büyük Dosyaları Tespit Etme

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

Sunucularda diski doldurma potansiyeli olan çok büyük ve yakın zamanda güncellenmiş dosyaları bulur.

**Playbook:** `playbooks/30_check_large_files.yml`

## Ne Yapar?
* Tüm diskte belirtilen boyuttan büyük (örn: 1GB) dosyaları tarar.
* Sadece son `X` günde değişiklik yapılmış olanları listeler.
* Bu sayede eski, statik büyük dosyalar (örn: iso imajları) yerine aniden büyüyen logları tespit etmeyi kolaylaştırır.

## Parametreler (Opsiyonel)
Aşağıdaki değişkenleri (vars) ezerek filtreyi değiştirebilirsiniz:
* `min_size`: Aranacak minimum boyut (Varsayılan: `1G`)
* `max_age_days`: Son X günde değişenler (Varsayılan: `30`)

## Örnek Kullanım

```bash
# Sadece 500MB'dan büyük dosyaları aramak için:
ansible-playbook ... playbooks/30_check_large_files.yml -e "min_size=500M"
```
