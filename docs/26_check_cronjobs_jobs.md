# 26_check_cronjobs_jobs.yml - Kullanım Kılavuzu

## Amaç

CronJob envanteri (schedule, suspend, lastSchedule, active) ve Job durumları; **Failed** olanlar öne çıkar.

## Değişkenler

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `jobs_namespace` | `""` | Doluysa sadece o ns; boşsa tümü |

```bash
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/26_check_cronjobs_jobs.yml
ansible-playbook -i inventories/cagatayuresincom/hosts.ini playbooks/26_check_cronjobs_jobs.yml \
  --extra-vars 'jobs_namespace=n8n'
```

Script: `playbooks/files/k8s_cronjobs_jobs_check.py`
