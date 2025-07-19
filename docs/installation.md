# 📥 Kurulum Rehberi - AI Video Studio

Bu rehber, AI Video Studio'nun adım adım kurulum sürecini açıklar.

## 🔧 Sistem Gereksinimleri

### Minimum Gereksinimler
- **Python**: 3.8 veya üzeri
- **İşletim Sistemi**: Windows 10, macOS 10.14, Ubuntu 18.04+
- **RAM**: 4GB (8GB önerilen)
- **Disk Alanı**: 5GB boş alan
- **İnternet**: Stabil bağlantı (API çağrıları için)

### Önerilen Gereksinimler
- **Python**: 3.10+
- **RAM**: 16GB
- **Disk Alanı**: 20GB SSD
- **İşlemci**: 4 çekirdek+

## 📦 Temel Kurulum

### 1. Python Kurulumu

#### Windows
```bash
# Python.org'dan Python 3.10+ indirin
# https://www.python.org/downloads/windows/

# Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin
# PowerShell'de kontrol edin:
python --version
pip --version
```

#### macOS
```bash
# Homebrew ile kurulum (önerilen)
brew install python@3.10

# Alternatif: Python.org'dan indirin
# https://www.python.org/downloads/macos/

# Kontrol
python3 --version
pip3 --version
```

#### Ubuntu/Debian
```bash
# Sistem paketlerini güncelleyin
sudo apt update

# Python ve pip kurun
sudo apt install python3.10 python3.10-pip python3.10-venv

# Kontrol
python3 --version
pip3 --version
```

### 2. FFmpeg Kurulumu

#### Windows
```bash
# Chocolatey ile (önerilen)
choco install ffmpeg

# Alternatif: Manuel kurulum
# 1. https://ffmpeg.org/download.html#build-windows
# 2. ffmpeg.exe'yi PATH'e ekleyin
# 3. Kontrol:
ffmpeg -version
```

#### macOS
```bash
# Homebrew ile kurulum
brew install ffmpeg

# Kontrol
ffmpeg -version
```

#### Ubuntu/Debian
```bash
# Resmi repository'den kurulum
sudo apt update
sudo apt install ffmpeg

# Snap ile alternatif kurulum
sudo snap install ffmpeg

# Kontrol
ffmpeg -version
```

### 3. AI Video Studio Kurulumu

#### Repository Klonlama
```bash
# HTTPS ile klonlama
git clone https://github.com/sevim-coder/Studio.git
cd Studio

# SSH ile klonlama (SSH key gerekli)
git clone git@github.com:sevim-coder/Studio.git
cd Studio
```

#### Sanal Ortam Oluşturma
```bash
# Python venv ile sanal ortam
python3 -m venv venv

# Sanal ortamı aktifleştirin
# Linux/macOS:
source venv/bin/activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate.bat

# Aktif olduğunu kontrol edin (terminal prompt'unda (venv) görünmeli)
which python  # Linux/macOS
where python   # Windows
```

#### Bağımlılıkları Yükleme
```bash
# requirements.txt'den yükleme
pip install -r requirements.txt

# Başarılı kurulum kontrolü
python -c "from google import genai; print('✅ Google Genai kurulu')"
python -c "import ffmpeg; print('✅ FFmpeg-python kurulu')"
python -c "import PIL; print('✅ Pillow kurulu')"
```

## 🔑 API Yapılandırması

### 1. Environment Variables Dosyası
```bash
# Template'i kopyalayın
cp .env.example .env

# Dosyayı düzenleyin
nano .env        # Linux/macOS
notepad .env     # Windows
```

### 2. Google Gemini API Key Alma

#### Adım 1: Google AI Studio'ya Giriş
1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresine gidin
2. Google hesabınızla giriş yapın
3. Hizmet şartlarını kabul edin

#### Adım 2: API Key Oluşturma
1. "Create API Key" butonuna tıklayın
2. "Create API key in new project" seçin
3. Oluşturulan key'i kopyalayın

#### Adım 3: Key'i .env Dosyasına Ekleme
```bash
# .env dosyasını açın ve ekleyin:
GEMINI_API_KEY_1=AIzaSyD...your_actual_key_here
GEMINI_API_KEY_2=AIzaSyC...your_second_key_here
GEMINI_API_KEY_3=AIzaSyB...your_third_key_here
```

### 3. Çoklu API Key Desteği
```bash
# Farklı projeler için farklı keyler oluşturun
# Her key için aylık ücretsiz kota: 1000 istek
# Sistem otomatik olarak kotası biten keyden diğerine geçer

# Minimum 1 key gerekli, 3 key'e kadar desteklenir
GEMINI_API_KEY_1=primary_key_here      # Zorunlu
GEMINI_API_KEY_2=secondary_key_here    # Opsiyonel  
GEMINI_API_KEY_3=tertiary_key_here     # Opsiyonel
```

## 🎮 YouTube Entegrasyonu (Opsiyonel)

### 1. YouTube API Credentials
```bash
# Google Cloud Console'a gidin
# https://console.cloud.google.com/

# Yeni proje oluşturun veya mevcut projeyi seçin
# YouTube Data API v3'ü etkinleştirin
# OAuth 2.0 credentials oluşturun
```

### 2. Credentials Dosyası
```bash
# İndirilen credentials.json dosyasını proje kök dizinine koyun
cp ~/Downloads/credentials.json ./credentials.json

# Alternatif: Service account kullanımı
cp ~/Downloads/service_account.json ./service_account.json
```

## ✅ Kurulum Testi

### 1. Temel Fonksiyon Testi
```bash
# Sanal ortamın aktif olduğundan emin olun
source venv/bin/activate  # Linux/macOS

# Temel import testleri
python -c "
import sys
print(f'Python version: {sys.version}')

from google import genai
print('✅ Google Genai import başarılı')

import ffmpeg
print('✅ FFmpeg-python import başarılı')

from checkpoint_manager import CheckpointManager
print('✅ Checkpoint Manager import başarılı')

print('🎉 Tüm temel testler başarılı!')
"
```

### 2. Yapılandırma Testi
```bash
# Config dosyasını test edin
python -c "
from config_manager import config
print('✅ Config manager başarılı')

from api_manager import get_api_manager
api_manager = get_api_manager()
print('✅ API manager başarılı')

print('🎉 Yapılandırma testleri başarılı!')
"
```

### 3. Tam Sistem Testi
```bash
# Ana script'i test modunda çalıştırın
python yapimci_flexible.py --config config_advanced.json

# Manuel mod testi (Ctrl+C ile çıkın)
python yapimci_flexible.py
```

## 🚨 Yaygın Kurulum Sorunları

### 1. Python Import Hatası
```bash
❌ ModuleNotFoundError: No module named 'google'

# Çözüm:
pip install google-genai
# Sanal ortamın aktif olduğundan emin olun
```

### 2. FFmpeg Bulunamadı
```bash
❌ FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'

# Çözüm:
# FFmpeg'i sistem PATH'ine ekleyin
# Windows: Environment Variables > PATH > Add ffmpeg/bin
# Linux/macOS: ~/.bashrc veya ~/.zshrc dosyasına ekleyin
export PATH="/usr/local/bin:$PATH"
```

### 3. Permission Denied Hatası
```bash
❌ PermissionError: [Errno 13] Permission denied

# Çözüm:
# pip için:
pip install --user -r requirements.txt

# Dosya izinleri için:
chmod +x yapimci_flexible.py
```

### 4. SSL Certificate Hatası
```bash
❌ SSL: CERTIFICATE_VERIFY_FAILED

# Çözüm:
# macOS:
/Applications/Python\ 3.x/Install\ Certificates.command

# Linux:
pip install --upgrade certifi
```

### 5. API Key Hatası
```bash
❌ KRITIK HATA: GEMINI_API_KEY_1 environment variable bulunamadı

# Çözüm:
# .env dosyasının doğru konumda olduğundan emin olun
ls -la .env

# .env dosyasının içeriğini kontrol edin
cat .env | grep GEMINI

# Boşluk karakterleri ve özel karakterler olmadığından emin olun
```

## 🔧 Gelişmiş Kurulum

### 1. Docker ile Kurulum (Gelecek sürümde)
```bash
# Dockerfile yakında eklenecek
# docker build -t ai-video-studio .
# docker run -it ai-video-studio
```

### 2. Conda ile Kurulum
```bash
# Conda environment oluşturma
conda create -n ai-video-studio python=3.10
conda activate ai-video-studio

# Bağımlılıkları yükleme
pip install -r requirements.txt
```

### 3. Sistem Servisi Olarak Kurulum (Linux)
```bash
# Systemd service dosyası oluşturun
sudo nano /etc/systemd/system/ai-video-studio.service

# İçerik:
[Unit]
Description=AI Video Studio
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/Studio
ExecStart=/path/to/Studio/venv/bin/python yapimci_flexible.py
Restart=always

[Install]
WantedBy=multi-user.target

# Servisi etkinleştirin
sudo systemctl enable ai-video-studio
sudo systemctl start ai-video-studio
```

## 📊 Performans Optimizasyonu

### 1. Disk Alanı Optimizasyonu
```bash
# Yeterli disk alanı kontrolü
df -h .

# Geçici dosya temizliği
rm -rf .cache/ gecici_klipler/

# Cache boyutu sınırlama (config_advanced.json)
{
  "sistem_ayarlari": {
    "disk_min_alan_mb": 2000
  }
}
```

### 2. Bellek Optimizasyonu
```bash
# Sistem bellek kontrolü
free -h

# Swap alanı artırma (gerekirse)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 3. Network Optimizasyonu
```bash
# API çağrıları için stable internet gerekli
# Minimum: 1 Mbps
# Önerilen: 10 Mbps+

# Proxy ayarları (gerekirse)
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

---

**✅ Kurulum tamamlandıktan sonra [Configuration Guide](configuration.md)'a geçin.**