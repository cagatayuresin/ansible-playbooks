# 06_update_k8s_services.yml - Kullanım Kılavuzu

![Modifies State](https://img.shields.io/badge/State-Modifies-E3000F?style=flat) ![kubeadm](https://img.shields.io/badge/Kubernetes-kubeadm-326CE5?style=flat&logo=kubernetes&logoColor=white)

## ⚠️ Bu playbook canlı bir Kubernetes cluster'ını günceller

Salt-okunur değildir; `kubeadm`, `kubelet`, `kubectl`, `containerd` paketlerini gerçekten günceller ve node'ları sırayla drain/uncordon eder. Docker bu playbook'un kapsamında değildir. Calico ayrı bir konu olduğu için [07_check_calico.yml](../playbooks/07_check_calico.yml) içindedir.

Çalıştırmadan önce mutlaka `--check --diff` ile kuru çalıştırma yapın ve önce kritik olmayan bir cluster'da (ör. tek node'luk lab ortamı) deneyin.

## Amaç ve Yaklaşım

Kubernetes'in resmi `kubeadm` upgrade akışını izler:

1. **Kontrol düzlemi (`master`/`singlenode`, `serial: 1` — node'lar tek tek işlenir):**
   - İlk control-plane node: `kubeadm upgrade plan` + `kubeadm upgrade apply v<version>`
   - Ek control-plane node'lar (varsa): `kubeadm upgrade node`
   - Node drain edilir (`kubectl drain`, ilk control-plane node üzerinden `delegate_to` ile)
   - `kubeadm`/`kubelet`/`kubectl` apt paketleri hedef sürüme sabitlenir (`apt-mark hold` ile korunan paketler geçici olarak unhold edilip güncellenir, sonra tekrar hold'a alınır)
   - `containerd` mevcut apt reposundan en güncel sürüme yükseltilir (k8s sürümüyle sıkı sıkıya versiyon eşleşmesi gerekmediği için "latest" kullanılır)
   - kubelet yeniden başlatılır, node uncordon edilir
2. **Worker node'lar (`workers`, `serial: 1`):** Aynı adımlar, ama her zaman `kubeadm upgrade node` (asla `apply`).

Güncelleme öncesi ve sonrası sürümler, [04_check_k8s_versions.yml](../playbooks/04_check_k8s_versions.yml) ile aynı paylaşılan [tasks/k8s_versions.yml](../playbooks/tasks/k8s_versions.yml) görev listesiyle tespit edilir (kubectl/kubeadm/kubelet/containerd/runc/etcd) — sürüm tespiti iki yerde ayrı ayrı yazılmaz.

`etcd` ayrıca bir adım gerektirmez — standart kubeadm (stacked etcd) kurulumlarında etcd static pod olarak çalışır ve `kubeadm upgrade apply/node` sırasında otomatik güncellenir.

## Gereksinimler / Ön Koşullar

- **`kube_version` değişkeni zorunludur** (ör. `1.34.3`), varsayılan/otomatik "latest" YOKTUR. kubeadm resmi kısıtı gereği **tek seferde yalnızca bir minor sürüm ileri gidilebilir** (ör. 1.33.x → 1.34.x); birden fazla minor atlamak cluster'ı bozabilir.
- **Yeni bir minor sürüme geçiyorsanız**, playbook'u çalıştırmadan ÖNCE `/etc/apt/sources.list.d/kubernetes.list` dosyasını hedef minor'ün resmi reposuna (`https://pkgs.k8s.io/core:/stable:/v1.XX/deb/`) manuel olarak güncelleyip `apt-get update` çalıştırmanız gerekir — bu playbook apt repo dosyanıza dokunmaz (farklı kurulumlarda keyring/dosya yapısı farklı olabileceği için otomatik değiştirmek riskli bulundu).
- `become: true` (sudo) kullanılır — `ansible_become_pass` inventory'de tanımlı olmalı.
- Node drain/uncordon işlemleri ilk control-plane node'a `delegate_to` ile, `become: true` (root) altında çalışır; bu yüzden `KUBECONFIG=/etc/kubernetes/admin.conf` doğrudan task'a `environment:` olarak verilir (root kullanıcısının kendi `~/.kube/config`'i genelde olmadığı için).
- kubeadm kurulu olmayan host'larda (ör. `datanode`) güncelleme adımları otomatik atlanır, hata vermez.

## Çalıştırma Komutu

```bash
# Önce ne değişeceğini görmek için (ZORUNLU ilk adım):
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/06_update_k8s_services.yml \
  --extra-vars "kube_version=1.34.3" --check --diff

# Gerçekten uygulamak için:
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/06_update_k8s_services.yml \
  --extra-vars "kube_version=1.34.3"

# Tek bir node ile sınırlamak için (ör. önce sadece bir worker'da denemek):
ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/06_update_k8s_services.yml \
  --extra-vars "kube_version=1.34.3" --limit worker1
```

## Notlar

- `serial: 1` ile her play'de node'lar teker teker işlenir — cluster'ın tamamı aynı anda güncellenmez, bu yüzden çalışan workload'lar için kesinti minimumda tutulur.
- Paket sürümü `apt-cache madison` ile tam paket sürüm string'i (ör. `1.34.3-1.1`) bulunarak sabitlenir; sadece `1.34.3` yazmak apt'ta genelde eşleşmez.
- İlk çalıştırmayı mutlaka `--check --diff` ile ve kritik olmayan bir node/cluster üzerinde yapın.
- `kubeadm upgrade apply` transient bir hatayla (ör. etcd restart sonrası bağlantı timeout'u) başarısız olursa cluster kısmen güncellenmiş durumda kalabilir; kubeadm bu duruma karşı idempotenttir — playbook'u aynı `kube_version` ile tekrar çalıştırmak, zaten tamamlanmış bileşenleri (ör. etcd) atlayıp kaldığı yerden devam eder.
