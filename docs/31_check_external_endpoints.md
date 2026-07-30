# 31. Dış Endpoint Bağlantı Testi

![Read-Only](https://img.shields.io/badge/State-Read--Only-10B981?style=flat)

Projenizin çalışması için kritik olan dış API ve web sitelerinin (Payment API'leri, SMS servisleri vb.) erişilebilirliğini ve hızını kontrol eder.

**Playbook:** `playbooks/31_check_external_endpoints.yml`

## Ne Yapar?
* Playbook içine tanımlanmış olan kritik URL listesine HTTP GET istekleri gönderir.
* Dönen HTTP durum kodunu (200 OK) ve isteğin milisaniye cinsinden ne kadar sürdüğünü raporlar.
* Bu playbook `localhost` üzerinde çalışır; SSH ile hedef sunuculara gitmez, çalıştığı makineden ağ testleri yapar.

## Parametreler
Playbook içindeki `endpoints` listesini kendi kritik servislerinize göre güncellemelisiniz.

## Örnek Çıktı

```
[BAŞARILI] Google API (https://www.google.com)
Durum Kodu: 200
Geçen Süre: 0.231 saniye

[HATA] Örnek Endpoint (https://api.github.com/hata)
Durum Kodu: 404
Geçen Süre: 0.150 saniye
```
