# 41_patch_and_reboot_nodes.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![Maintenance](https://img.shields.io/badge/Maintenance-Serial_1-F59E0B?style=flat)

## ⚠️ Canlı node'larda paket güncelleme ve reboot yapabilir

Varsayılan çalıştırma yalnızca bekleyen paketleri ve reboot ihtiyacını raporlar. Değişiklik için `node_patch_confirm=true` zorunludur.

Onaylı bakım akışı:

1. Kubernetes node ise ilk control-plane üzerinden drain
2. Debian'da `apt dist-upgrade`, RedHat'te `dnf update`
3. Reboot ayrıca onaylandıysa ve gerekiyorsa reboot
4. Node'u uncordon
5. Hata durumunda rescue bloğuyla uncordon denemesi

Host'lar `serial: 1` ile sırayla işlenir.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `node_patch_confirm` | `false` | Paket güncellemesini açar |
| `node_reboot_confirm` | `false` | Gerekiyorsa reboot yapılmasına izin verir |
| `node_reboot_always` | `false` | Reboot işareti olmasa da reboot eder |
| `node_allow_single_node_maintenance` | `false` | Singlenode bakımını ayrıca onaylar |
| `kubernetes_node_name` | `ansible_hostname` | Kubernetes API içindeki node adı |

## Çalıştırma

```bash
# Yalnızca rapor:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/41_patch_and_reboot_nodes.yml

# Bir worker üzerinde patch ve gerekiyorsa reboot:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/41_patch_and_reboot_nodes.yml \
  --limit worker1 \
  --extra-vars 'node_patch_confirm=true node_reboot_confirm=true'
```

Singlenode cluster için ayrıca `node_allow_single_node_maintenance=true` verilmelidir. Bakım öncesinde güncel etcd yedeğini `32_verify_etcd_backup.yml` ile doğrulayın.
