# 🎮 Kullanım Rehberi - AI Video Studio

Bu rehber, AI Video Studio'nun detaylı kullanım kılavuzunu içerir.

## 🚀 Hızlı Başlangıç

### 1. Basit Video Üretimi
```bash
# Sanal ortamı aktifleştirin
source venv/bin/activate

# Manuel modda başlatın
python yapimci_flexible.py

# Sistemi soracağı bilgiler:
# 1. Kanal adı: Teknoloji Dünyası
# 2. Video konusu: Yapay Zeka'nın Geleceği
# 3. Hedef harf sayısı: 2000
```

### 2. Otomatik Video Üretimi
```bash
# Otomatik modda başlatın (config ile)
python yapimci_flexible.py --config config_advanced.json

# Sistem günlük görevleri kontrol eder ve otomatik çalışır
```

## 📋 Detaylı Kullanım

### Manuel Mod İşlem Akışı

#### Adım 1: Sistem Başlatma
```bash
python yapimci_flexible.py
```

Sistem çıktısı:
```
🎬 FLEXIBLE MULTI-API YAPIMCI BAŞLADI
============================================================
🔧 Esnek yapılandırma sistemi aktif
🔄 Multi-API otomatik failover sistemi aktif
📊 API kullanım takibi ve maliyet hesaplama aktif
⚡ Gelişmiş hata yakalama ve kurtarma sistemi aktif
============================================================
```

#### Adım 2: Kanal Seçimi
```
Kanal adı giriniz: Teknoloji Dünyası
```

Sistemin desteklediği önceden tanımlı kanallar:
- İlham Perisi (Kadın odaklı içerik)
- Perspektif (Tarih ve analiz)
- Nolmuş Çocuk (Eğlenceli içerik)
- Sahne ve Sanat (Sanat ve kültür)
- Techsen (Teknoloji)

#### Adım 3: Konu Belirleme
```
Video konusunu giriniz: Yapay Zeka'nın Günlük Hayattaki Yeri
```

#### Adım 4: Uzunluk Belirleme
```
Hedef harf sayısını giriniz: 2000
```

Önerilen harf sayıları:
- Kısa video (1-2 dk): 800-1200 harf
- Orta video (3-4 dk): 1500-2500 harf  
- Uzun video (5+ dk): 3000+ harf

### Checkpoint/Resume Sistemi

#### Devam Etme Durumu
Eğer yarım kalmış proje varsa:
```
📊 Proje Durumu: teknoloji_dunyasi_yapay_zekanin_gunluk_hayattaki_yeri
🕐 Son güncelleme: 2024-01-15T14:30:45
  ✅ senaryo: completed (1/1)
  ✅ yonetmen: completed (1/1)
  🟡 varlik_uretimi: in_progress (3/10)
  ⚪ kurgu: not_started
  ⚪ youtube_upload: not_started

Yarım kalmış proje bulundu. Devam edilsin mi? (E/H) > E
🔄 Operasyon devam ettiriliyor: varlik_uretimi - 3/10
```

#### Otomatik Devam
```bash
# Otomatik modda sistem devam sorusu sormaz
python yapimci_flexible.py --config config_advanced.json
```

## 🎬 Üretim Aşamaları

### 1. Senaryo Üretimi
```
Adım 1: Multi-API Senaryo Üretimi
🎭 Multi-API Senarist başlatılıyor...
📝 Kanal: Teknoloji Dünyası  
📚 Konu: Yapay Zeka'nın Günlük Hayattaki Yeri
📊 Hedef uzunluk: 2000 harf
```

Sistem çıktısı:
```
✅ Gemini API ile senaryo üretildi
📁 Senaryo kaydedildi: kanallar/teknoloji_dunyasi/yapay_zekanin_gunluk_hayattaki_yeri/senaryo.txt
✅ Operasyon tamamlandı: senaryo
```

### 2. Proje Planlama
```
Adım 2: Yönetmenlik (JSON Proje Oluşturma)
🎬 Proje dosyası oluşturuluyor...
📋 Senaryo analiz ediliyor...
🎯 Video segmentleri belirleniyor...
```

Sistem çıktısı:
```
✅ Proje dosyası oluşturuldu: proje.json
📊 Video segmentleri: 8 adet
⏱️ Tahmini süre: 3.5 dakika
✅ Operasyon tamamlandı: yonetmen
```

### 3. Varlık Üretimi (Ses + Görsel)
```
Adım 3: Multi-API Varlık Üretimi (Ses ve Görsel - Sıralı)
```

#### 3a. Ses Üretimi
```
Adım 3a: Multi-API Seslendirme
🎙️ Multi-API Seslendirmen başlatılıyor...
🎵 Google TTS ile ses üretimi
📊 İşlenecek segment sayısı: 8
```

Segment bazlı ilerleme:
```
🎙️ Segment 1/8: "Yapay zeka artık günlük hayatımızın..."
✅ ses_1.wav oluşturuldu
🎙️ Segment 2/8: "Sabah uyandığımızda akıllı telefonumuz..."
✅ ses_2.wav oluşturuldu
...
✅ Tüm ses dosyaları oluşturuldu: 8/8
```

#### 3b. Görsel Üretimi
```
Adım 3b: Multi-API Görsel Üretimi
🎨 Multi-API Görsel Yönetmen başlatılıyor...
🖼️ Imagen 4.0 ile görsel üretimi
📊 İşlenecek görsel sayısı: 8
```

Görsel bazlı ilerleme:
```
🎨 Görsel 1/8: "Yapay zeka teknolojileri ve modern yaşam"
✅ gorsel_1.png oluşturuldu (1920x1080)
🎨 Görsel 2/8: "Akıllı telefon ve AI asistanları"  
✅ gorsel_2.png oluşturuldu (1920x1080)
...
✅ Tüm görseller oluşturuldu: 8/8
```

### 4. Video Kurgu
```
Adım 4: Montaj Öncesi Hash Kontrolü
🔍 Dosya bütünlük kontrolü yapılıyor...
✅ Tüm ses dosyaları doğrulandı
✅ Tüm görsel dosyaları doğrulandı
🧹 Montaj öncesi temizlik yapılıyor...

Adım 4: Kurgu ve Montaj
🎬 FFmpeg ile video oluşturuluyor...
📊 Video ayarları: 1920x1080, 30fps, H.264
```

Kurgu ilerleme çıktısı:
```
🔧 Video codec: libx264
🔊 Ses codec: aac
⚡ Preset: medium
🎯 CRF: 23 (yüksek kalite)
📹 final_video.mp4 oluşturuluyor...
✅ Video kurgu tamamlandı
```

### 5. YouTube Yükleme (Opsiyonel)
```
Adım 5: YouTube Yükleme
📤 YouTube Uploader başlatılıyor...
🔐 OAuth kimlik doğrulama kontrol ediliyor...
📋 Video metadata hazırlanıyor...
```

Yükleme süreci:
```
📺 Başlık: "Yapay Zeka'nın Günlük Hayattaki Yeri"
📝 Açıklama: Senaryo'dan otomatik üretildi
🏷️ Etiketler: #yapayZeka #teknoloji #AI
🔒 Gizlilik: private (varsayılan)
📤 Video yükleniyor...
✅ YouTube'a başarıyla yüklendi
```

## 📊 İzleme ve Kontrol

### API Kullanım Raporu
```
📊 Multi-API Kullanım Raporu:
┌─────────────────┬──────────┬─────────┬──────────┐
│ API Provider    │ Kullanım │ Başarı  │ Maliyet  │
├─────────────────┼──────────┼─────────┼──────────┤
│ Gemini Primary  │ 12/1000  │ 100%    │ $0.12    │
│ Gemini Secondary│ 0/1000   │ -       │ $0.00    │
│ Gemini Tertiary │ 0/1000   │ -       │ $0.00    │
└─────────────────┴──────────┴─────────┴──────────┘
```

### Checkpoint Durumu
```bash
# Checkpoint dosyasını görüntüleyin
cat .checkpoint_teknoloji_dunyasi_yapay_zekanin_gunluk_hayattaki_yeri.json
```

### Log Analizi
```bash
# Canlı log izleme
tail -f yapimci_logs.txt

# Hata logları
grep "ERROR\|KRITIK" yapimci_logs.txt

# Başarı logları
grep "SUCCESS\|✅" yapimci_logs.txt
```

## 🛠️ İleri Seviye Kullanım

### 1. Özel Kanal Oluşturma
config_advanced.json dosyasına yeni kanal ekleyin:
```json
{
  "kanal_ayarlari": {
    "Yeni Kanal": {
      "talimat": "Sen... [özel talimat]",
      "varsayilan_ses": "tr-TR-Wavenet-E",
      "kategori": "Education",
      "slug": "yeni_kanal"
    }
  }
}
```

### 2. Toplu Video Üretimi
```bash
# Haftalık video planı için script oluşturun
#!/bin/bash
# weekly_production.sh

# Pazartesi
python yapimci_flexible.py --config config_monday.json

# Çarşamba  
python yapimci_flexible.py --config config_wednesday.json

# Cuma
python yapimci_flexible.py --config config_friday.json
```

### 3. A/B Test Video Üretimi
```bash
# Aynı konu için farklı yaklaşımlar
python yapimci_flexible.py # Versiyon A
# Farklı talimat ile
python yapimci_flexible.py # Versiyon B
```

### 4. Video Seri Üretimi
```json
{
  "seri_ayarlari": {
    "ai_serisi": {
      "bolum_1": "Yapay Zeka Nedir?",
      "bolum_2": "AI'nin Tarihçesi", 
      "bolum_3": "Günlük Hayatta AI",
      "bolum_4": "AI'nin Geleceği"
    }
  }
}
```

## 🔧 Sorun Giderme

### Yaygın Sorunlar ve Çözümleri

#### 1. API Key Hatası
```
❌ KRITIK HATA: GEMINI_API_KEY_1 environment variable bulunamadı!
```

**Çözüm:**
```bash
# .env dosyasını kontrol edin
cat .env | grep GEMINI

# Eksik varsa ekleyin
echo "GEMINI_API_KEY_1=your_actual_key" >> .env
```

#### 2. FFmpeg Hatası
```
❌ KRITIK HATA: FFmpeg bulunamadı
```

**Çözüm:**
```bash
# FFmpeg kurulumunu kontrol edin
ffmpeg -version

# Kurulu değilse kurun
sudo apt install ffmpeg  # Ubuntu
brew install ffmpeg      # macOS
```

#### 3. Disk Alanı Yetersiz
```
❌ KRITIK HATA: Yetersiz disk alanı! Gerekli: 2000MB, Mevcut: 1500MB
```

**Çözüm:**
```bash
# Disk alanını kontrol edin
df -h .

# Geçici dosyaları temizleyin
rm -rf .cache/ gecici_klipler/

# Eski projeleri temizleyin
rm -rf kanallar/*/2023-*
```

#### 4. Video Kurgu Hatası
```
❌ KRITIK HATA: FFmpeg işlemi başarısız oldu
```

**Çözüm:**
```bash
# Ses ve görsel dosyaları kontrol edin
ls -la kanallar/*/ses*/
ls -la kanallar/*/gorseller/

# Bozuk dosyaları silin ve tekrar çalıştırın
rm ses_bozuk.wav
python yapimci_flexible.py  # Checkpoint'ten devam eder
```

#### 5. YouTube Yükleme Hatası
```
❌ KRITIK HATA: YouTube için kimlik doğrulama dosyası bulunamadı!
```

**Çözüm:**
```bash
# Credentials dosyasını kontrol edin
ls -la credentials.json service_account.json

# Eksikse Google Cloud Console'dan indirin
# https://console.cloud.google.com/
```

### Debug Modu
```bash
# Debug modunda çalıştırın
DEBUG=1 python yapimci_flexible.py

# Detaylı log ile çalıştırın
python yapimci_flexible.py --verbose
```

### Manuel Müdahale
```bash
# Belirli bir aşamayı atlamak için checkpoint'i düzenleyin
nano .checkpoint_*.json

# İstenen aşamayı "completed" olarak işaretleyin
# Sistem bir sonraki aşamadan devam eder
```

## 📈 Performans Optimizasyonu

### 1. Hız Optimizasyonu
```json
{
  "ffmpeg_ayarlari": {
    "video_preset": "ultrafast",  // Hızlı kurgu
    "video_crf": 28               // Düşük kalite, yüksek hız
  }
}
```

### 2. Kalite Optimizasyonu
```json
{
  "ffmpeg_ayarlari": {
    "video_preset": "slow",       // Yavaş ama kaliteli
    "video_crf": 18               // Yüksek kalite
  }
}
```

### 3. Kaynak Optimizasyonu
```bash
# Bellek kullanımını izleyin
htop

# Disk I/O izleyin
iotop

# Sistem kaynaklarını optimize edin
```

## 📊 Analitik ve Raporlama

### Üretim İstatistikleri
```bash
# Toplam üretilen video sayısı
find kanallar/ -name "final_video.mp4" | wc -l

# Kanal bazında video sayısı
ls kanallar/*/

# Ortalama video süresi
# ffprobe ile analiz yapılabilir
```

### Maliyet Analizi
```bash
# API kullanım maliyeti
grep "Maliyet" yapimci_logs.txt

# Günlük/aylık toplam
```

### Kalite Metrikleri
```bash
# Başarı oranı
grep -c "BAŞARIYLA TAMAMLANDI" yapimci_logs.txt

# Hata oranı  
grep -c "KRITIK HATA" yapimci_logs.txt
```

## 🔄 Bakım ve Güncelleme

### Düzenli Bakım
```bash
# Haftalık bakım scripti
#!/bin/bash
# maintenance.sh

# Log dosyalarını temizle (30 günden eski)
find . -name "*.log" -mtime +30 -delete

# Checkpoint dosyalarını temizle (tamamlanmış projeler)
find . -name ".checkpoint_*" -mtime +7 -delete

# Cache temizliği
rm -rf .cache/*

# API usage istatistikleri backup
cp api_usage.json backups/api_usage_$(date +%Y%m%d).json
```

### Sistem Güncellemeleri
```bash
# Repository güncellemesi
git pull origin main

# Dependency güncellemeleri
pip install --upgrade -r requirements.txt

# Config validation
python -c "from config_manager import config; print('✅ Config OK')"
```

---

**🎬 AI Video Studio ile profesyonel video üretiminin keyfini çıkarın!**

**Daha fazla yardım için:**
- GitHub Issues: Hata bildirimi
- GitHub Discussions: Sorular ve öneriler
- Wiki: Detaylı dokümantasyon