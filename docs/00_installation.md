# Kurulum

Bu depodaki playbook'ları çalıştırmak için Ansible'ın kurulu olduğu bir kontrol makinesi gerekir. Ansible control node **yalnızca Linux/macOS/WSL üzerinde** çalışır — Windows'ta doğrudan çalışmaz (yönetilen/hedef makine Windows olabilir ama kontrol makinesi olamaz).

## Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y ansible

# Daha güncel bir sürüm isterseniz pip ile:
python3 -m pip install --user ansible
```

Doğrulama:

```bash
ansible --version
```

## macOS

[Homebrew](https://brew.sh) ile:

```bash
brew install ansible
```

Homebrew yoksa önce onu kurun:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Doğrulama:

```bash
ansible --version
```

## Windows

Ansible control node Windows'ta native çalışmaz. İki seçenek:

### Seçenek 1: WSL2 (önerilen)

1. PowerShell'i **yönetici olarak** açıp:
   ```powershell
   wsl --install
   ```
2. Bilgisayarı yeniden başlatın, Ubuntu kurulumunu tamamlayın (kullanıcı adı/şifre sorar).
3. Açılan WSL2 Ubuntu terminalinde, yukarıdaki **Linux (Ubuntu/Debian)** adımlarını izleyin.
4. Bu repoyu WSL2 dosya sistemi içine (`~/` altına) klonlayın — Windows tarafındaki `/mnt/c/...` üzerinden çalıştırmak SSH/performans sorunlarına yol açabilir.

### Seçenek 2: Uzak bir Linux makine / VM üzerinden

Ansible'ı doğrudan bir Linux sunucusunda veya VM'de (VirtualBox, Hyper-V, bulut sağlayıcı vb.) kurup playbook'ları oradan çalıştırın; Windows makineniz sadece SSH ile o makineye bağlanmak için kullanılır.

## Kurulumdan Sonra

1. Bu repoyu klonlayın:
   ```bash
   git clone <repo-url>
   cd ansible-playbooks
   ```
2. Örnek inventory ile bir playbook'u deneyin:
   ```bash
   ansible-playbook -i inventories/musteri_a/hosts.ini playbooks/01_check_pod_health.yml
   ```
3. Kendi ortamınız için `inventories/` altında yeni bir klasör oluşturup `musteri_a/hosts.ini`'yi örnek alarak kendi host/IP/kimlik bilgilerinizi girin. Gerçek müşteri/production ortam inventory'leri bilinçli olarak `.gitignore` ile bu repodan hariç tutulmuştur.

## Playbook Dokümantasyonu

Her playbook'un amacı, gereksinimleri ve örnek çıktısı `docs/` klasöründe numaraya göre eşleşen dosyada anlatılır (ör. `playbooks/04_check_k8s_versions.yml` → `docs/04_check_k8s_versions.md`). Tam liste için [README.md](../README.md) içindeki tabloya bakın.
