# 42_generate_support_bundle.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Writes_Archive-F59E0B?style=flat) ![Support](https://img.shields.io/badge/Support-Redacted_Bundle-6366F1?style=flat)

## Amaç

İlk control-plane host'undan Kubernetes ve işletim sistemi tanı verilerini toplayıp `.tar.gz` arşivini controller üzerindeki `support-bundles/` dizinine getirir.

Toplanan başlıca veriler:

- Cluster/version/node/pod/workload listeleri
- Service ve EndpointSlice
- Event, storage, PDB, NetworkPolicy, APIService ve CSR
- Disk, RAM, uptime, başarısız servisler ve son journal uyarıları

Kubernetes Secret ve ConfigMap içerikleri hiçbir zaman istenmez. Varsayılan redaksiyon IP, e-posta ve bilinen token/password kalıplarını maskeler.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `support_bundle_redact` | `true` | Sezgisel hassas veri maskelemesi |
| `support_bundle_keep_remote` | `false` | `/tmp` altındaki hedef arşivi tutar |
| `support_bundle_local_dir` | `support-bundles/` | Controller çıktı dizini |

## Çalıştırma

```bash
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/42_generate_support_bundle.yml
```

Redaksiyon sezgiseldir. Arşivi üçüncü tarafla paylaşmadan önce içeriği manuel olarak inceleyin. `support-bundles/` Git tarafından yok sayılır ve dizin `0700`, arşiv `0600` izinleriyle oluşturulur.
