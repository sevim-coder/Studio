# 🎬 AI Video Studio - Profesyonel Video Üretim Sistemi

AI Video Studio, Google/Gemini API'leri kullanarak otomatik video üretimi sağlayan profesyonel bir sistemdir. Senaryo yazımından video yayınlama aşamasına kadar tüm süreci otomatikleştirir.

## ✨ Özellikler

### 🤖 AI Destekli İçerik Üretimi
- **Google Gemini Pro** ile akıllı senaryo yazımı
- **Imagen 4.0** ile yüksek kaliteli görsel üretimi  
- **Google TTS** ile doğal ses sentezi
- Kanal bazlı özelleştirilmiş içerik

### 🔄 Resume-from-Checkpoint Sistemi
- **Otomatik durum takibi**: Her operasyon için JSON tabanlı checkpoint sistemi
- **Kesintisiz devam**: Sistem hatalarında kaldığı yerden devam etme
- **Granüler kontrol**: 3/10 görsel tamamsa → 4. görselden devam
- **Akıllı temizlik**: Sadece tam başarı sonrası geçici dosya temizliği

### ⚡ Güvenilir Hata Yönetimi
- **sys.exit(1) davranışı korundu**: Hatalar anında sistem durdurma
- **Robustu environment variable parsing**: ${GEMINI_API_KEY_1} desteği
- **Gelişmiş ses dosyası kontrolü**: Wave corruption detection ve cleanup
- **Multi-API failover**: API kotası bittiğinde otomatik geçiş

### 🎯 Google/Gemini Özel Entegrasyonu
- **Sadece Google/Gemini**: OpenAI ve Anthropic entegrasyonları tamamen kaldırıldı
- **Çoklu API key desteği**: GEMINI_API_KEY_1, GEMINI_API_KEY_2, GEMINI_API_KEY_3
- **Model çeşitliliği**: gemini-2.5-pro, imagen-4.0-generate-preview-06-06

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler

```bash
# Python 3.8+ gerekli
python --version

# FFmpeg kurulumu (Ubuntu/Debian)
sudo apt update
sudo apt install ffmpeg

# FFmpeg kurulumu (macOS)
brew install ffmpeg

# FFmpeg kurulumu (Windows)
# https://ffmpeg.org/download.html adresinden indirin
```

### 2. Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/sevim-coder/Studio.git
cd Studio

# Sanal ortam oluşturun
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate     # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

### 3. Yapılandırma

```bash
# Environment variables template'ini kopyalayın
cp .env.example .env

# .env dosyasını düzenleyin
nano .env
```

**.env dosyasına API keylerini ekleyin:**
```bash
GEMINI_API_KEY_1=your_primary_gemini_api_key_here
GEMINI_API_KEY_2=your_secondary_gemini_api_key_here
GEMINI_API_KEY_3=your_tertiary_gemini_api_key_here
```

**Google Gemini API key'i almak için:**
1. [Google AI Studio](https://makersuite.google.com/app/apikey) adresine gidin
2. "Create API Key" butonuna tıklayın
3. Oluşturulan key'i kopyalayın ve .env dosyasına yapıştırın

### 4. İlk Çalıştırma

```bash
# Manuel modda çalıştırma
python yapimci_flexible.py

# Otomatik modda çalıştırma (config dosyası ile)
python yapimci_flexible.py --config config_advanced.json
```

## 📊 Checkpoint/Resume Sistemi

### Otomatik Durum Takibi
Sistem her operasyon için durumu JSON dosyalarında saklar:

```json
{
  "project_name": "kanal_konu",
  "operations": {
    "senaryo": {
      "status": "completed",
      "progress": 1.0,
      "output_files": ["senaryo.txt"]
    },
    "varlik_uretimi": {
      "status": "in_progress", 
      "current_item": 3,
      "total_items": 10,
      "progress": 0.3
    }
  }
}
```

### Kesintiden Kurtarma

**Örnek Senaryo 1: Görsel üretimi yarıda kesildi**
```bash
# Sistem çıktısı:
📊 Proje Durumu: kanal_teknoloji
🕐 Son güncelleme: 2024-01-15T14:30:45
  ✅ senaryo: completed (1/1)
  ✅ yonetmen: completed (1/1) 
  🟡 varlik_uretimi: in_progress (3/10)
  ⚪ kurgu: not_started
  ⚪ youtube_upload: not_started

🔄 Operasyon devam ettiriliyor: varlik_uretimi - 3/10
# 4. görselden devam eder
```

**Örnek Senaryo 2: Video kurgu sırasında hata**
```bash
# Sistem çıktısı:
❌ KRITIK HATA: FFmpeg işlemi başarısız oldu
# Geçici dosyalar korunur, sadece başarısız operasyon yeniden çalışır
```

## 🎮 Kullanım Örnekleri

### Manuel Video Üretimi
```bash
python yapimci_flexible.py

# Sistem soracak:
# Kanal adı: Teknoloji Dünyası
# Video konusu: Yapay Zeka'nın Günlük Hayattaki Yeri
# Hedef harf sayısı: 2000
```

### Otomatik Günlük Üretim
`config_advanced.json` dosyasında günlük görevler tanımlayın:

```json
{
  "gunluk_gorevler": {
    "pazartesi": {
      "kanal_adi": "Teknoloji Dünyası",
      "konu": "Haftanın Teknoloji Haberleri",
      "harf_sayisi": 1500
    },
    "carsamba": {
      "kanal_adi": "Bilim Kapısı", 
      "konu": "Uzay Araştırmaları",
      "harf_sayisi": 2000
    }
  }
}
```

### Toplu API Key Yönetimi
```bash
# .env dosyasında çoklu key desteği
GEMINI_API_KEY_1=key_for_primary_quota
GEMINI_API_KEY_2=key_for_secondary_quota  
GEMINI_API_KEY_3=key_for_emergency_quota

# Sistem otomatik olarak kota biten key'lerden diğerine geçer
```

## 🗂️ Proje Yapısı

```
AI-Video-Studio/
├── README.md                     # Bu dosya
├── requirements.txt              # Python bağımlılıkları
├── .env.example                  # Environment template
├── .gitignore                   # Git ignore kuralları
├── config_advanced.json         # Ana yapılandırma
├── config_manager.py            # Yapılandırma yöneticisi
├── api_manager.py               # Google/Gemini API yöneticisi
├── checkpoint_manager.py        # Resume sistemi yöneticisi
├── yapimci_flexible.py          # Ana orkestrasyon (GİRİŞ NOKTASI)
├── moduller/                    # AI Video Studio modülleri
│   ├── __init__.py
│   ├── senarist_multiapi.py     # Gemini ile senaryo üretimi
│   ├── yonetmen.py              # Video planlama ve yapılandırma
│   ├── seslendirmen_multiapi.py # Google TTS ile ses üretimi
│   ├── gorsel_yonetmen_multiapi.py # Imagen ile görsel üretimi
│   ├── kurgu.py                 # FFmpeg ile video montaj
│   ├── youtube_uploader.py      # YouTube otomatik yükleme
│   └── config_cli.py           # CLI yapılandırma aracı
├── docs/                        # Detaylı belgeler
│   ├── installation.md
│   ├── configuration.md
│   └── usage.md
└── examples/                    # Örnek dosyalar
    └── .env.example
```

## ⚙️ Gelişmiş Yapılandırma

### Kanal Özelleştirme
```json
{
  "kanal_ayarlari": {
    "Teknoloji Dünyası": {
      "talimat": "Sen teknolojik gelişmeleri anlaşılır bir şekilde açıklayan bir uzman...",
      "varsayilan_ses": "tr-TR-Wavenet-E",
      "kategori": "Science & Technology"
    }
  }
}
```

### FFmpeg Optimizasyonu
```json
{
  "ffmpeg_ayarlari": {
    "video_codec": "libx264",
    "video_preset": "medium",
    "video_crf": 23,
    "audio_codec": "aac",
    "audio_bitrate": "192k"
  }
}
```

### Kalite Kontrol
```json
{
  "kalite_kontrol": {
    "min_ses_suresi": 0.5,
    "min_video_resolution": "1920x1080", 
    "max_file_size_mb": 500
  }
}
```

## 🛠️ Sorun Giderme

### Yaygın Hatalar

**1. Environment Variable Bulunamadı**
```bash
❌ KRITIK HATA: GEMINI_API_KEY_1 environment variable bulunamadı!

# Çözüm:
# .env dosyasını kontrol edin
# API key'in doğru yazıldığını kontrol edin
```

**2. FFmpeg Bulunamadı**
```bash
❌ KRITIK HATA: FFmpeg bulunamadı

# Çözüm:
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

**3. Checkpoint Dosyası Bozuk**
```bash
❌ KRITIK HATA: Checkpoint dosyası yüklenemedi

# Çözüm:
# .checkpoint_*.json dosyasını silin
rm .checkpoint_*.json
# Sistem yeni checkpoint oluşturacak
```

### Log Analizi
```bash
# Detaylı logları görüntüleyin
tail -f yapimci_logs.txt

# Hata seviyesi logları filtreleyin  
grep "ERROR\|CRITICAL" yapimci_logs.txt
```

## 🔒 Güvenlik

### API Key Güvenliği
- **✅ .env dosyası Git'te ignore edilir**
- **✅ API keyleri asla kod içinde hardcode edilmez**
- **✅ Çoklu key desteği ile risk dağıtımı**

### Dosya Güvenliği
```bash
# .env dosyası izinlerini kısıtlayın
chmod 600 .env

# Geçici dosyaları düzenli olarak temizleyin
# (Sistem otomatik yapar ama manuel de yapabilirsiniz)
rm -rf .cache/ gecici_klipler/
```

## 📈 Performans Optimizasyonu

### Disk Alanı Yönetimi
```json
{
  "sistem_ayarlari": {
    "disk_min_alan_mb": 2000,        # Minimum disk alanı kontrolü
    "cache_klasoru": ".cache",       # Cache klasörü
    "gecici_klasor": "gecici_klipler" # Geçici dosya klasörü
  }
}
```

### Bellek Kullanımı
- Sistem otomatik bellek kontrolü yapar
- Büyük videolar için swap alanı artırın
- Çoklu API key ile yük dağıtımı

## 🤝 Katkıda Bulunma

### Geliştirme Ortamı Kurulumu
```bash
# Development bağımlılıklarını yükleyin
pip install -r requirements.txt

# Code formatting
black . --line-length 88

# Linting
flake8 . --max-line-length 88

# Testing (opsiyonel)
python -m pytest
```

### Pull Request Süreci
1. Fork oluşturun
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🆘 Destek

### Dokümantasyon
- **Kurulum**: `docs/installation.md`
- **Yapılandırma**: `docs/configuration.md`  
- **Kullanım**: `docs/usage.md`

### İletişim
- **Issues**: GitHub Issues aracılığıyla hata bildirin
- **Discussions**: Sorularınız için GitHub Discussions kullanın
- **Wiki**: Detaylı bilgi için GitHub Wiki'ye bakın

## 🎯 Roadmap

### v1.1 (Yakında)
- [ ] Web arayüzü
- [ ] Video kalite seçenekleri (4K, 1080p, 720p)
- [ ] Çoklu dil desteği
- [ ] Video önizleme sistemi

### v1.2 (Planlanan)
- [ ] Batch processing
- [ ] Video şablonları
- [ ] Advanced scheduling
- [ ] Analytics dashboard

---

**🎬 AI Video Studio** - Yapay zeka destekli profesyonel video üretiminin geleceği!
