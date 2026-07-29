# 21_check_tls_certificates.yml - Kullanım Kılavuzu

## Amaç

Salt-okunur TLS / sertifika envanteri (ilk control-plane üzerinde):

1. **kubeadm** `certs check-expiration` (varsa)
2. **Control-plane PEM dosyaları** — `/etc/kubernetes/pki`, `/var/lib/rancher/k3s/server/tls` (openssl bitiş + kalan gün)
3. **Ingress TLS** — her Ingress için domain’ler, secret, issuer, SAN, bitiş tarihi, kalan gün, seviye
4. **cert-manager** `Certificate` kaynakları (CRD varsa)
5. **Tüm `kubernetes.io/tls` secret’ları** — en kritik 25 (kalan güne göre)

## Seviyeler

| Seviye | Kalan gün |
|---|---|
| `SURESI_DOLMUS` | < 0 |
| `KRITIK` | ≤ 7 |
| `UYARI` | ≤ 30 |
| `YAKLASIYOR` | ≤ 90 |
| `OK` | > 90 |

## Gereksinimler

- `hosts: master:singlenode` — yalnızca `first_control_plane`
- `become: true` (PKI dizinleri genelde root)
- `kubectl` + `openssl` + `python3`
- `KUBECONFIG` play seviyesinde `~/.kube/config`

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/21_check_tls_certificates.yml
```

## Ingress çıktısı nasıl okunur?

Her kayıtta:

- **domains** — Ingress rule / TLS hosts
- **secret** — `namespace/secretName`
- **issuer / SAN** — sertifika kimliği
- **KALAN / BITIS / SEVIYE** — yenileme aciliyeti

`TLS_YOK` / `SECRET_EKSIK` / `CERT_YOK` → yapılandırma eksik, süre değil.

## Notlar

- Script: `playbooks/files/k8s_tls_certificates_check.py`
- Cluster’ı değiştirmez.
