# 14_check_metrics_server.yml - Kullanım Kılavuzu

## Amaç

İlk control-plane node (`master` / `singlenode` grubundaki ilk host) üzerinde **metrics-server** kurulu ve API’sinin Available olup olmadığını kontrol eder. Kurulum yapmaz; istatistik çekmez.

Ortak görev: [tasks/metrics_server_check.yml](../playbooks/tasks/metrics_server_check.yml)

## Ne kontrol edilir?

| Kontrol | Komut / kaynak |
|---|---|
| kubectl erişimi | `kubectl cluster-info` |
| Deployment | `kubectl -n kube-system get deploy metrics-server` |
| API | `v1beta1.metrics.k8s.io` → `Available=True` |
| Pod’lar | `k8s-app=metrics-server` label |

`metrics_server_ready` = deployment var **ve** API Available.

## Gereksinimler

- Inventory’de `master` ve/veya `singlenode`
- Çalışma yalnızca `first_control_plane` üzerinde
- `KUBECONFIG` play seviyesinde `~/.kube/config` (k3s uyumu)

## Çalıştırma

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/14_check_metrics_server.yml
```

## Sonraki adımlar

- Hazırsa istatistik: [15_get_metrics_server_stats](15_get_metrics_server_stats.md)
- Değilse kur + istatistik: [16_ensure_metrics_server](16_ensure_metrics_server.md)

## Çoklu makine

Rapor başında `HOST` / `hostname` vardır. metrics-server cluster-scope olduğu için sorgu tek control-plane’den yapılır.
