# 03_check_docker_containers.yml - Kullanım Kılavuzu

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat) ![Docker](https://img.shields.io/badge/Runtime-Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Amaç

Bu playbook, inventory'deki sunucularda Docker'ın kurulu olup olmadığını kontrol eder. Eğer Docker mevcutsa, `docker ps -a` benzeri bir komut çalıştırarak sunucudaki tüm container'ların isimlerini, sağlık durumlarını/ne zamandır ayakta olduklarını (Status/Uptime) ve açık portlarını ekrana tablo düzeninde yazdırır. Ayrıca genel ağa açık olan (0.0.0.0) portlar için tıklanabilir browser linkleri üretir.

## Gereksinimler

- Hedef sunucularda Docker yüklü olmalıdır. (Yüklü değilse hata vermez, sadece yüklü olmadığını belirtir.)
- Ansible inventory'nizde ilgili gruplar (örn. `workers`, `master`) tanımlanmış olmalıdır.

Container tablosu okunaklı olması için Docker'ın kendi `table` formatıyla ayrıca alınır (görüntüleme amaçlı); link üretimi ise `docker ps --format '{{json .}}'` ile alınan yapılandırılmış JSON çıktısı üzerinden yapılır (önceki `sed` regex tabanlı yaklaşımın yerine). Bu sayede birden fazla porta açık olan container'ların tüm portları için ayrı ayrı link üretilir; eski yaklaşım satır başına yalnızca ilk portu yakalıyordu.

## Çalıştırma Komutu

```bash
# Tüm sunucularda (master + workers + datanode) çalıştırmak için:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/03_check_docker_containers.yml

# Sadece workers grubunda (worker1, worker2, worker3) çalıştırmak için limit verebilirsiniz:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/03_check_docker_containers.yml --limit workers
```

## Örnek Çıktı

Komut çalıştırıldığında öncelikle "Ping pong" ile bağlantılar kontrol edilir. Docker yüklüyse, formatlanmış container listesi verilir:

```text
TASK [Ping pong] ***************************************************************
ok: [192.168.1.21]

TASK [Check if Docker is installed] ********************************************
ok: [192.168.1.21]

TASK [Get Docker containers info as table] *************************************
ok: [192.168.1.21]

TASK [Display Docker containers status] ****************************************
ok: [192.168.1.21] => {
    "msg": "NAMES                  STATUS                  PORTS\nnginx-proxy            Up 4 days (healthy)     0.0.0.0:80->80/tcp, :::80->80/tcp\npayment-api            Up 2 hours              0.0.0.0:8080->8080/tcp\nold-container          Exited (0) 5 days ago   "
}

TASK [Get Docker containers info as JSON] **************************************
ok: [192.168.1.21]

TASK [Parse container JSON output] *********************************************
ok: [192.168.1.21]

TASK [Generate browser accessible links for containers] ************************
ok: [192.168.1.21] => (item=nginx-proxy)
ok: [192.168.1.21] => (item=payment-api)
ok: [192.168.1.21] => (item=old-container)

TASK [Display container links] *************************************************
ok: [192.168.1.21] => {
    "msg": "Aşağıdaki container portlarına browser üzerinden erişebilirsiniz:\n\n- nginx-proxy -> http://192.168.1.21:80\n- payment-api -> http://192.168.1.21:8080"
}

TASK [Docker not found message] ************************************************
skipping: [192.168.1.21]
```
