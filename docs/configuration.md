# ⚙️ Yapılandırma Rehberi - AI Video Studio

Bu rehber, AI Video Studio'nun detaylı yapılandırma seçeneklerini açıklar.

## 📋 Yapılandırma Dosyaları

### 1. Ana Yapılandırma: config_advanced.json
```json
{
  "api_providers": {
    "gemini": {
      "primary": {
        "api_key": "${GEMINI_API_KEY_1}",
        "model_text": "gemini-2.5-pro",
        "model_tts": "gemini-2.5-flash-preview-tts",
        "model_image": "imagen-4.0-generate-preview-06-06",
        "daily_quota": 1000,
        "cost_per_request": 0.01,
        "priority": 1
      }
    }
  }
}
```

### 2. Environment Variables: .env
```bash
# Google/Gemini API Keys
GEMINI_API_KEY_1=your_primary_key
GEMINI_API_KEY_2=your_secondary_key
GEMINI_API_KEY_3=your_tertiary_key

# YouTube API (Opsiyonel)
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret

# Sistem Ayarları
YAPIMCI_LOG_LEVEL=INFO
YAPIMCI_MAX_SEGMENTS=100
```

## 🤖 API Yapılandırması

### Google/Gemini Ayarları
```json
{
  "api_providers": {
    "gemini": {
      "primary": {
        "api_key": "${GEMINI_API_KEY_1}",
        "model_text": "gemini-2.5-pro",           // Metin üretimi
        "model_tts": "gemini-2.5-flash-preview-tts", // Ses sentezi  
        "model_image": "imagen-4.0-generate-preview-06-06", // Görsel üretimi
        "daily_quota": 1000,                        // Günlük istek limiti
        "cost_per_request": 0.01,                   // İstek başına maliyet
        "priority": 1                               // Öncelik sırası
      },
      "secondary": {
        "api_key": "${GEMINI_API_KEY_2}",
        "priority": 2                               // Yedek API
      },
      "tertiary": {
        "api_key": "${GEMINI_API_KEY_3}",
        "priority": 3                               // 3. yedek API
      }
    }
  }
}
```

### Failover Ayarları
```json
{
  "failover_ayarlari": {
    "max_retry_per_api": 3,                 // API başına max deneme
    "retry_delay_seconds": 5,               // Denemeler arası bekleme
    "quota_check_enabled": true,            // Kota kontrolü
    "cost_tracking_enabled": true,          // Maliyet takibi
    "fallback_strategy": "priority_order"   // Yedekleme stratejisi
  }
}
```

## 🎬 Kanal Yapılandırması

### Kanal Özelleştirme
```json
{
  "kanal_ayarlari": {
    "Teknoloji Dünyası": {
      "talimat": "Sen teknolojik gelişmeleri anlaşılır ve net bir şekilde açıklayan bir teknoloji uzmanısın. Karmaşık konuları basit örneklerle anlat.",
      "varsayilan_ses": "tr-TR-Wavenet-E",
      "kategori": "Science & Technology",
      "slug": "teknoloji_dunyasi",
      "video_süresi_dakika": 3,
      "hedef_kitle": "genel"
    },
    "Bilim Kapısı": {
      "talimat": "Sen bilimsel konuları meraklı ve öğretici bir şekilde anlatan bir bilim insanısın.",
      "varsayilan_ses": "tr-TR-Wavenet-D", 
      "kategori": "Education",
      "slug": "bilim_kapisi",
      "video_süresi_dakika": 5,
      "hedef_kitle": "akademik"
    }
  }
}
```

### Günlük Görev Programlama
```json
{
  "gunluk_gorevler": {
    "pazartesi": {
      "kanal_adi": "Teknoloji Dünyası",
      "konu": "Haftanın Teknoloji Haberleri",
      "harf_sayisi": 1500,
      "saat": "09:00",
      "otomatik_yukle": true
    },
    "carsamba": {
      "kanal_adi": "Bilim Kapısı",
      "konu": "Uzay Keşifleri",
      "harf_sayisi": 2000,
      "saat": "14:00", 
      "otomatik_yukle": false
    },
    "cuma": {
      "kanal_adi": "Teknoloji Dünyası",
      "konu": "AI ve Yapay Zeka Gelişmeleri",
      "harf_sayisi": 1800,
      "saat": "16:00",
      "otomatik_yukle": true
    }
  }
}
```

## 🎥 Video Yapılandırması

### FFmpeg Ayarları
```json
{
  "ffmpeg_ayarlari": {
    "video_codec": "libx264",               // H.264 codec
    "video_preset": "medium",               // Kalite/hız dengesi
    "video_crf": 23,                        // Kalite (18=yüksek, 28=düşük)
    "audio_codec": "aac",                   // AAC ses codec
    "audio_bitrate": "192k",                // Ses kalitesi
    "output_format": "mp4",                 // Çıktı formatı
    "resolution": "1920x1080",             // Video çözünürlüğü
    "framerate": 30,                        // FPS
    "keyframe_interval": 60                 // Keyframe aralığı
  }
}
```

### Kalite Kontrol
```json
{
  "kalite_kontrol": {
    "min_ses_suresi": 0.5,                 // Minimum ses süresi (saniye)
    "min_video_resolution": "1280x720",    // Minimum çözünürlük
    "min_file_size_bytes": 1048576,        // Minimum dosya boyutu (1MB)
    "max_file_size_mb": 500,               // Maximum dosya boyutu
    "ses_kalite_kontrol": true,            // Ses kalite kontrolü
    "gorsel_kalite_kontrol": true,         // Görsel kalite kontrolü
    "hash_verification": true              // Dosya bütünlük kontrolü
  }
}
```

## 🛠️ Sistem Yapılandırması

### Temel Sistem Ayarları
```json
{
  "sistem_ayarlari": {
    "log_dosyasi": "yapimci_logs.txt",     // Log dosyası
    "log_level": "INFO",                    // Log seviyesi
    "max_segment_sayisi": 100,              // Maximum segment sayısı
    "disk_min_alan_mb": 2000,              // Minimum disk alanı
    "cache_klasoru": ".cache",              // Cache klasörü
    "gecici_klasor": "gecici_klipler",     // Geçici dosya klasörü
    "checkpoint_enabled": true,             // Checkpoint sistemi
    "auto_cleanup": true,                   // Otomatik temizlik
    "parallel_processing": false           // Paralel işleme (gelecek)
  }
}
```

### Checkpoint Yapılandırması
```json
{
  "checkpoint_ayarlari": {
    "auto_save_interval": 30,               // Otomatik kaydetme (saniye)
    "max_checkpoint_files": 5,              // Maximum checkpoint dosyası
    "cleanup_on_success": true,             // Başarıda temizlik
    "backup_checkpoints": true,             // Checkpoint yedekleme
    "resume_on_startup": true               // Başlangıçta devam et
  }
}
```

## 📤 YouTube Yapılandırması

### YouTube Ayarları
```json
{
  "youtube_ayarlari": {
    "varsayilan_gizlilik": "private",       // private, unlisted, public
    "varsayilan_kategori": "22",            // People & Blogs
    "max_baslik_uzunluk": 100,             // Maximum başlık uzunluğu
    "max_aciklama_uzunluk": 5000,          // Maximum açıklama uzunluğu
    "otomatik_etiket": true,               // Otomatik etiket ekleme
    "thumbnail_upload": true,               // Thumbnail yükleme
    "playlist_ekleme": true                 // Playlist'e ekleme
  }
}
```

### OAuth Yapılandırması
```json
{
  "youtube_oauth": {
    "client_id": "${YOUTUBE_CLIENT_ID}",
    "client_secret": "${YOUTUBE_CLIENT_SECRET}",
    "redirect_uri": "http://localhost:8080",
    "scope": [
      "https://www.googleapis.com/auth/youtube.upload",
      "https://www.googleapis.com/auth/youtube"
    ]
  }
}
```

## 🎨 Görsel Yapılandırması

### Imagen Ayarları
```json
{
  "imagen_ayarlari": {
    "default_style": "photorealistic",      // Görsel stili
    "aspect_ratio": "16:9",                 // En boy oranı
    "quality": "standard",                  // standard, premium
    "safety_level": "block_most",           // Güvenlik seviyesi
    "prompt_enhancement": true,             // Prompt geliştirme
    "negative_prompt": "blurry, low quality" // Negatif prompt
  }
}
```

### Görsel İşleme
```json
{
  "gorsel_isleme": {
    "output_format": "PNG",                 // PNG, JPEG
    "compression_quality": 95,              // JPEG kalitesi (1-100)
    "resize_enabled": true,                 // Yeniden boyutlandırma
    "target_width": 1920,                  // Hedef genişlik
    "target_height": 1080,                 // Hedef yükseklik
    "watermark_enabled": false,            // Watermark ekleme
    "metadata_preservation": true          // Metadata koruma
  }
}
```

## 🔊 Ses Yapılandırması

### Google TTS Ayarları
```json
{
  "tts_ayarlari": {
    "default_voice": "tr-TR-Wavenet-E",    // Varsayılan ses
    "speaking_rate": 1.0,                  // Konuşma hızı
    "pitch": 0.0,                          // Ses tonu
    "volume_gain_db": 0.0,                 // Ses seviyesi
    "sample_rate": 24000,                  // Örnekleme oranı
    "audio_encoding": "LINEAR16"           // Ses kodlaması
  }
}
```

### Ses İşleme
```json
{
  "ses_isleme": {
    "normalization": true,                  // Ses normalizasyonu
    "noise_reduction": false,               // Gürültü azaltma
    "echo_cancellation": false,             // Yankı iptali
    "compression": true,                    // Ses sıkıştırma
    "fade_in_ms": 100,                     // Fade in süresi
    "fade_out_ms": 100,                    // Fade out süresi
    "silence_detection": true              // Sessizlik tespiti
  }
}
```

## 🔐 Güvenlik Yapılandırması

### API Güvenlik
```json
{
  "guvenlik_ayarlari": {
    "api_key_rotation": true,               // API key rotasyonu
    "rate_limiting": true,                  // Hız sınırlama
    "request_timeout": 30,                  // İstek timeout (saniye)
    "ssl_verification": true,               // SSL doğrulama
    "proxy_support": false,                 // Proxy desteği
    "audit_logging": true                   // Audit loglama
  }
}
```

### Dosya Güvenlik
```json
{
  "dosya_guvenlik": {
    "file_permissions": "600",              // Dosya izinleri
    "secure_deletion": true,                // Güvenli silme
    "encryption_enabled": false,            // Şifreleme (gelecek)
    "backup_enabled": true,                 // Yedekleme
    "temp_file_cleanup": true              // Geçici dosya temizliği
  }
}
```

## 📊 Monitoring ve Analitik

### Performans İzleme
```json
{
  "monitoring": {
    "performance_tracking": true,           // Performans takibi
    "memory_monitoring": true,              // Bellek izleme
    "disk_usage_alerts": true,             // Disk kullanım uyarıları
    "api_usage_tracking": true,            // API kullanım takibi
    "error_reporting": true,               // Hata raporlama
    "health_check_interval": 300           // Sağlık kontrolü (saniye)
  }
}
```

### Analitik Ayarları
```json
{
  "analitik": {
    "usage_statistics": true,               // Kullanım istatistikleri
    "performance_metrics": true,            // Performans metrikleri
    "cost_analysis": true,                  // Maliyet analizi
    "success_rate_tracking": true,          // Başarı oranı takibi
    "export_reports": true,                 // Rapor dışa aktarma
    "retention_days": 30                    // Veri saklama süresi
  }
}
```

## 🔧 Gelişmiş Yapılandırma

### Debug Modu
```json
{
  "debug_ayarlari": {
    "debug_mode": false,                    // Debug modu
    "verbose_logging": false,               // Detaylı loglama
    "save_intermediate_files": false,       // Ara dosyaları sakla
    "api_call_logging": false,             // API çağrı loglama
    "timing_analysis": false,              // Zamanlama analizi
    "memory_profiling": false              // Bellek profilleme
  }
}
```

### Geliştirici Seçenekleri
```json
{
  "developer_options": {
    "mock_api_calls": false,               // Sahte API çağrıları
    "skip_video_generation": false,        // Video üretimini atla
    "use_sample_data": false,              // Örnek veri kullan
    "force_regeneration": false,           // Zorla yeniden üret
    "experimental_features": false         // Deneysel özellikler
  }
}
```

## 📝 Örnekler

### Örnek 1: Teknoloji Kanalı
```json
{
  "kanal_adi": "Tech Talk TR",
  "talimat": "Sen teknoloji haberlerini güncel ve anlaşılır bir dille sunan bir editörsün.",
  "varsayilan_ses": "tr-TR-Wavenet-E",
  "video_süresi": 180,
  "ffmpeg_preset": "fast",
  "kalite": "1080p"
}
```

### Örnek 2: Eğitim Kanalı
```json
{
  "kanal_adi": "Bilim Öğren",
  "talimat": "Sen bilimsel konuları öğrencilere öğretici bir dille anlatan bir öğretmensin.",
  "varsayilan_ses": "tr-TR-Wavenet-D",
  "video_süresi": 300,
  "ffmpeg_preset": "medium",
  "kalite": "720p"
}
```

### Örnek 3: Haber Kanalı
```json
{
  "kanal_adi": "Güncel Haber",
  "talimat": "Sen güncel haberleri objektif ve hızlı bir şekilde sunan bir muhabirsin.",
  "varsayilan_ses": "tr-TR-Wavenet-C",
  "video_süresi": 120,
  "ffmpeg_preset": "ultrafast",
  "kalite": "1080p"
}
```

## 🔄 Yapılandırma Yönetimi

### Config Doğrulama
```bash
# Yapılandırma dosyasını doğrulayın
python -c "
from config_manager import ConfigManager
config = ConfigManager('config_advanced.json')
print('✅ Yapılandırma geçerli')
"
```

### Config Yedekleme
```bash
# Yapılandırmaları yedekleyin
cp config_advanced.json config_backup_$(date +%Y%m%d).json
cp .env .env_backup_$(date +%Y%m%d)
```

### Config Güncelleme
```bash
# Git üzerinden güncellemeleri çekin
git pull origin main

# Yapılandırmanızı birleştirin
# Manuel olarak config_advanced.json dosyasını kontrol edin
```

---

**⚙️ Yapılandırma tamamlandıktan sonra [Usage Guide](usage.md)'a geçin.**