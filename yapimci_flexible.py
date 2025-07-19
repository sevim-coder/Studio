# yapimci_flexible.py - Multi-API Entegrasyonlu Esnek Yapımcı

import os
import sys
import json
import subprocess
import argparse
import hashlib
import datetime
import shutil
from config_manager import config
from api_manager import get_api_manager
from checkpoint_manager import CheckpointManager, OperationType

# Custom Exception Classes
class YapimciError(Exception):
    """Base exception for production errors"""
    pass

class ConfigurationError(YapimciError):
    """Configuration related errors"""
    pass

class ModuleExecutionError(YapimciError):
    """Module execution errors"""
    pass

class ResourceError(YapimciError):
    """Resource availability errors (disk space, etc.)"""
    pass

LOG_FILE = "yapimci_logs.txt"

def log(mesaj, seviye="INFO"):
    log_mesaji = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{seviye}] {mesaj}"
    print(log_mesaji)
    log_dosyasi = config.get('sistem_ayarlari', 'log_dosyasi', default=LOG_FILE)
    with open(log_dosyasi, "a", encoding="utf-8") as f:
        f.write(log_mesaji + "\n")

def dosya_hash_hesapla(dosya_yolu):
    sha256_hash = hashlib.sha256()
    if not os.path.exists(dosya_yolu): return None
    with open(dosya_yolu, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def komut_calistir(komut_listesi):
    try:
        log(f"Komut çalıştırılıyor: {' '.join(komut_listesi)}")
        process = subprocess.run(komut_listesi, check=True, capture_output=True, text=True, encoding='utf-8')
        if process.stdout:
            log(f"Komut Çıktısı:\n--- \n{process.stdout}\n---")
        log(f"Komut başarıyla tamamlandı.")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Komut hatası! Return Code: {e.returncode}\n--- HATA ---\n{e.stderr}", "ERROR")
        return False

class FlexibleYapimci:
    def __init__(self, config_file=None):
        print("🎬 Flexible Multi-API Yapımcı başlatılıyor...")
        
        # Config manager'ı başlat
        if config_file:
            from config_manager import ConfigManager
            self.config_manager = ConfigManager(config_file)
        else:
            self.config_manager = config
        
        # API Manager'ı başlat
        self.api_manager = get_api_manager()
        
        # Checkpoint manager - initially None, will be set when project starts
        self.checkpoint_manager = None
        
        # Ayarları config'den al
        self.log_file = self.config_manager.get('sistem_ayarlari', 'log_dosyasi', default='yapimci_logs.txt')
        self.max_segments = self.config_manager.get('sistem_ayarlari', 'max_segment_sayisi', default=100)
        self.disk_min = self.config_manager.get('sistem_ayarlari', 'disk_min_alan_mb', default=2000)
        self.cache_klasoru = self.config_manager.get('sistem_ayarlari', 'cache_klasoru', default='.cache')
        self.gecici_klasor = self.config_manager.get('sistem_ayarlari', 'gecici_klasor', default='gecici_klipler')
        
        # FFmpeg ayarları
        self.ffmpeg_config = self.config_manager.get('ffmpeg_ayarlari', default={})
        
        # Kalite kontrol ayarları
        self.kalite_config = self.config_manager.get('kalite_kontrol', default={})
        
        # Workflow ayarları
        self.proje_yolu = ""
        self.durum = {}
        self.hash_durumu = {}
        self.is_manual = True  # Başlangıçta manuel, config ile değişebilir
        
        print("✅ Flexible Multi-API Yapımcı hazır!")

    def durumu_yukle(self):
        """Genel proje durumunu yükler"""
        durum_dosyasi = os.path.join(self.proje_yolu, "status.json")
        if os.path.exists(durum_dosyasi):
            with open(durum_dosyasi, 'r', encoding='utf-8') as f: 
                self.durum = json.load(f)
            log("Mevcut proje durumu yüklendi.")
        else:
            self.durum = {"tamamlanan_adimlar": []}
            log("Yeni proje için durum dosyası oluşturuluyor.")

    def hash_durumunu_yukle(self):
        """Hash kontrolü durumunu yükler"""
        hash_dosyasi = os.path.join(self.proje_yolu, "integrity.json")
        if os.path.exists(hash_dosyasi):
            with open(hash_dosyasi, 'r', encoding='utf-8') as f: 
                self.hash_durumu = json.load(f)
            log("Hash kontrol durumu yüklendi.")
        else:
            self.hash_durumu = {"dosya_hashleri": {}}
            log("Yeni hash kontrol dosyası oluşturuluyor.")

    def durumu_kaydet(self):
        """Genel durum dosyasını kaydeder"""
        durum_dosyasi = os.path.join(self.proje_yolu, "status.json")
        with open(durum_dosyasi, 'w', encoding='utf-8') as f: 
            json.dump(self.durum, f, indent=2, ensure_ascii=False)

    def hash_durumunu_kaydet(self):
        """Hash kontrol dosyasını kaydeder"""
        hash_dosyasi = os.path.join(self.proje_yolu, "integrity.json")
        with open(hash_dosyasi, 'w', encoding='utf-8') as f: 
            json.dump(self.hash_durumu, f, indent=2, ensure_ascii=False)

    def adimi_gec(self, adim_adi):
        return adim_adi in self.durum.get("tamamlanan_adimlar", [])

    def adimi_tamamla(self, adim_adi, dosyalar=[]):
        """Adımı tamamlanmış olarak işaretler ve hash'leri kaydeder"""
        # Durum güncelleme
        if adim_adi not in self.durum["tamamlanan_adimlar"]:
            self.durum["tamamlanan_adimlar"].append(adim_adi)
        
        # Hash kaydetme (sadece senaryo ve varlık dosyaları için)
        if adim_adi in ["senaryo", "varlik_uretimi"]:
            for dosya in dosyalar:
                if os.path.exists(dosya):
                    self.hash_durumu["dosya_hashleri"][dosya] = dosya_hash_hesapla(dosya)
        
        self.durumu_kaydet()
        if adim_adi in ["senaryo", "varlik_uretimi"]:
            self.hash_durumunu_kaydet()
        
        log(f"Adım tamamlandı ve durum kaydedildi: {adim_adi}")

    def disk_alan_kontrol(self):
        """Config'den alınan minimum disk alanı kontrolü"""
        gerekli_mb = self.disk_min
        try:
            disk_usage = shutil.disk_usage(".")
            bos_alan_mb = disk_usage.free / (1024 * 1024)
            if bos_alan_mb < gerekli_mb:
                log(f"❌ KRITIK HATA: Yetersiz disk alanı! Gerekli: {gerekli_mb}MB, Mevcut: {bos_alan_mb:.1f}MB", "ERROR")
                sys.exit(1)
            log(f"✅ Disk alanı yeterli: {bos_alan_mb:.1f}MB mevcut")
        except Exception as e:
            log(f"❌ KRITIK HATA: Disk alanı kontrolü başarısız: {e}", "ERROR")
            sys.exit(1)

    def montaj_oncesi_hash_kontrol(self):
        """KURGU ÖNCESİ SON KONTROL: Senaryo + Ses + Görsel dosyalarının uyumu"""
        log("🔍 MONTAJ ÖNCESİ HASH KONTROLÜ başlatılıyor...")
        
        if not self.hash_durumu.get("dosya_hashleri"): 
            log("⚠️ Hash kayıtları bulunamadı, kontrol atlanıyor", "WARNING")
            return True
        
        # Kontrol edilecek dosyalar
        kontrol_edilecek_dosyalar = []
        
        # 1. Senaryo dosyası
        senaryo_yolu = os.path.join(self.proje_yolu, "senaryo.txt")
        if os.path.exists(senaryo_yolu):
            kontrol_edilecek_dosyalar.append(senaryo_yolu)
        
        # 2. Ses dosyaları
        ses_klasoru = os.path.join(self.proje_yolu, "sesler")
        if os.path.exists(ses_klasoru):
            for dosya in os.listdir(ses_klasoru):
                if dosya.endswith('.wav'):
                    kontrol_edilecek_dosyalar.append(os.path.join(ses_klasoru, dosya))
        
        # 3. Görsel dosyaları
        gorsel_klasoru = os.path.join(self.proje_yolu, "gorseller")
        if os.path.exists(gorsel_klasoru):
            for dosya in os.listdir(gorsel_klasoru):
                if dosya.endswith('.png'):
                    kontrol_edilecek_dosyalar.append(os.path.join(gorsel_klasoru, dosya))
        
        log(f"📋 {len(kontrol_edilecek_dosyalar)} dosya kontrol edilecek")
        
        # Hash kontrolü
        uyumsuz_dosyalar = []
        for dosya_yolu in kontrol_edilecek_dosyalar:
            if dosya_yolu in self.hash_durumu["dosya_hashleri"]:
                kayitli_hash = self.hash_durumu["dosya_hashleri"][dosya_yolu]
                mevcut_hash = dosya_hash_hesapla(dosya_yolu)
                
                if mevcut_hash != kayitli_hash:
                    uyumsuz_dosyalar.append(os.path.basename(dosya_yolu))
                    log(f"❌ UYUMSUZLUK: {os.path.basename(dosya_yolu)}", "WARNING")
                else:
                    log(f"✅ UYUMLU: {os.path.basename(dosya_yolu)}")
            else:
                log(f"⚠️ Hash kaydı yok: {os.path.basename(dosya_yolu)}", "WARNING")
        
        if uyumsuz_dosyalar:
            log(f"🚨 {len(uyumsuz_dosyalar)} dosyada uyumsuzluk tespit edildi!", "ERROR")
            log(f"Uyumsuz dosyalar: {', '.join(uyumsuz_dosyalar)}", "ERROR")
            log("MONTAJ İÇİN HAZIR DEĞİL - Varlık dosyaları yeniden üretilmeli", "ERROR")
            return False
        
        log("✅ TÜM DOSYALAR UYUMLU - Montaj için hazır!", "SUCCESS")
        return True

    def montaj_icin_gereksiz_dosyalari_temizle(self):
        """Montaj öncesi gereksiz dosyaları temizler"""
        log("🧹 Montaj öncesi temizlik yapılıyor...")
        
        temizlenecek_dosyalar = [
            "final_video.mp4",
            self.gecici_klasor
        ]
        
        for item in temizlenecek_dosyalar:
            item_yolu = os.path.join(self.proje_yolu, item)
            
            try:
                if os.path.isfile(item_yolu):
                    os.remove(item_yolu)
                    log(f"🗑️ Dosya silindi: {item}")
                elif os.path.isdir(item_yolu):
                    shutil.rmtree(item_yolu)
                    log(f"🗑️ Klasör silindi: {item}")
            except Exception as e:
                log(f"⚠️ Temizlik hatası ({item}): {e}", "WARNING")
        
        log("✅ Montaj öncesi temizlik tamamlandı")

    def varlik_uyumsuzlugu_coz(self):
        """Varlık uyumsuzluğu durumunda yapılacaklar"""
        log("🔧 Varlık uyumsuzluğu çözülüyor...", "WARNING")
        
        if self.is_manual:
            print("\n🚨 VARLIK UYUMSUZLUĞU TESPİT EDİLDİ!")
            print("📝 Senaryo, ses veya görsel dosyaları değiştirilmiş")
            print("🔄 Varlık üretimi yeniden yapılmalı")
            cevap = input("Varlık üretimini yeniden başlatmak istiyor musunuz? (E/H) > ").lower()
            if cevap != 'e': 
                log("❌ Kullanıcı varlık üretimini redetti, işlem durduruldu", "ERROR")
                sys.exit(1)
        else:
            log("🤖 Otomatik modda varlık uyumsuzluğu - yeniden üretim başlatılıyor", "WARNING")
        
        # Varlık üretimi adımlarını sıfırla
        adimlar_to_reset = ["varlik_uretimi", "kurgu", "youtube_upload"]
        for adim in adimlar_to_reset:
            if adim in self.durum.get("tamamlanan_adimlar", []):
                self.durum["tamamlanan_adimlar"].remove(adim)
        
        # Varlık dosyalarının hash'lerini sil
        yeni_hash_durumu = {"dosya_hashleri": {}}
        # Sadece senaryo hash'ini koru
        senaryo_yolu = os.path.join(self.proje_yolu, "senaryo.txt")
        if senaryo_yolu in self.hash_durumu.get("dosya_hashleri", {}):
            yeni_hash_durumu["dosya_hashleri"][senaryo_yolu] = self.hash_durumu["dosya_hashleri"][senaryo_yolu]
        
        self.hash_durumu = yeni_hash_durumu
        
        # Geçici dosyaları temizle
        self.montaj_icin_gereksiz_dosyalari_temizle()
        
        # Varlık klasörlerini temizle
        for klasor in ["sesler", "gorseller"]:
            klasor_yolu = os.path.join(self.proje_yolu, klasor)
            if os.path.exists(klasor_yolu):
                shutil.rmtree(klasor_yolu)
                log(f"🗑️ {klasor} klasörü temizlendi")
        
        # Durumu kaydet
        self.durumu_kaydet()
        self.hash_durumunu_kaydet()
        
        log("✅ Varlık uyumsuzluğu çözüldü, yeniden üretim için hazır", "SUCCESS")

    def kanal_ayarlarini_al(self, kanal_adi):
        """Kanal-specific ayarları config'den alma"""
        kanal_config = self.config_manager.get('kanal_ayarlari', kanal_adi, default={})
        return {
            'talimat': kanal_config.get('talimat', 'Varsayılan talimat'),
            'ses': kanal_config.get('varsayilan_ses', 'Puck'),
            'kategori': kanal_config.get('kategori', 'Education'),
            'slug': kanal_config.get('slug', kanal_adi.replace(' ', '_'))
        }

    def gunu_al(self):
        gun_map = {"monday": "pazartesi", "tuesday": "sali", "wednesday": "carsamba", 
                  "thursday": "persembe", "friday": "cuma", "saturday": "cumartesi", "sunday": "pazar"}
        today_str = datetime.datetime.now().strftime("%A").lower()
        return gun_map.get(today_str, today_str)

    def slugify(self, text):
        return "".join(c for c in text if c.isalnum() or c in " _-").rstrip().replace(" ", "_")

    def gunluk_gorev_al(self):
        """Config'den günlük görevi al"""
        gun = self.gunu_al()
        gunluk_gorevler = self.config_manager.get('gunluk_gorevler', default={})
        
        if gun not in gunluk_gorevler:
            log(f"Bugün ({gun}) için config'da bir görev yok. Manuel moda geçiliyor.")
            return None
        
        return gunluk_gorevler[gun]

    def modulleri_calistir(self, kanal, konu, harf_sayisi):
        """Multi-API modüllerini sırasıyla çalıştır - Checkpoint/Resume destekli"""
        
        txt_yolu = os.path.join(self.proje_yolu, "senaryo.txt")
        json_yolu = os.path.join(self.proje_yolu, "proje.json")
        ses_klasoru = os.path.join(self.proje_yolu, "sesler")
        gorsel_klasoru = os.path.join(self.proje_yolu, "gorseller")
        final_video_yolu = os.path.join(self.proje_yolu, "final_video.mp4")

        try:
            # Adım 1: Multi-API Senaryo Üretimi
            if not self.checkpoint_manager.start_operation("senaryo", OperationType.SCENARIO):
                log("Adım 1: Multi-API Senaryo Üretimi")
                if not komut_calistir(["python", "moduller/senarist_multiapi.py", kanal, konu, harf_sayisi, "--cikti_yolu", txt_yolu]):
                    self.checkpoint_manager.fail_operation("senaryo", "Multi-API Senarist modülü başarısız oldu")
                self.checkpoint_manager.complete_operation("senaryo", [txt_yolu])
                # Legacy support
                self.adimi_tamamla("senaryo", [txt_yolu])

            # Adım 2: Yönetmenlik (JSON oluşturuluyor - değişiklik yok)
            if not self.checkpoint_manager.start_operation("yonetmen", OperationType.SCENARIO):
                log("Adım 2: Yönetmenlik (JSON Proje Oluşturma)")
                if not komut_calistir(["python", "moduller/yonetmen.py", txt_yolu, json_yolu]):
                    self.checkpoint_manager.fail_operation("yonetmen", "Yönetmen modülü başarısız oldu")
                self.checkpoint_manager.complete_operation("yonetmen", [json_yolu])
                # Legacy support
                self.adimi_tamamla("yonetmen")

            # Adım 3: Multi-API Varlık Üretimi (SIRALİ)
            if not self.checkpoint_manager.start_operation("varlik_uretimi", OperationType.AUDIO):
                log("Adım 3: Multi-API Varlık Üretimi (Ses ve Görsel - Sıralı)")
                os.makedirs(ses_klasoru, exist_ok=True)
                os.makedirs(gorsel_klasoru, exist_ok=True)
                
                # Önce Multi-API seslendirme
                log("Adım 3a: Multi-API Seslendirme")
                if not komut_calistir(["python", "moduller/seslendirmen_multiapi.py", json_yolu, ses_klasoru]):
                    self.checkpoint_manager.fail_operation("varlik_uretimi", "Multi-API Seslendirmen modülü başarısız oldu")
                
                # Sonra Multi-API görsel üretimi
                log("Adım 3b: Multi-API Görsel Üretimi")
                if not komut_calistir(["python", "moduller/gorsel_yonetmen_multiapi.py", json_yolu, gorsel_klasoru]):
                    self.checkpoint_manager.fail_operation("varlik_uretimi", "Multi-API Görsel yönetmen modülü başarısız oldu")
                
                # Üretilen dosyaları topla
                ses_dosyalari = [os.path.join(ses_klasoru, f) for f in os.listdir(ses_klasoru) if f.endswith('.wav')]
                gorsel_dosyalari = [os.path.join(gorsel_klasoru, f) for f in os.listdir(gorsel_klasoru) if f.endswith('.png')]
                all_files = ses_dosyalari + gorsel_dosyalari
                self.checkpoint_manager.complete_operation("varlik_uretimi", all_files)
                # Legacy support
                self.adimi_tamamla("varlik_uretimi", all_files)

            # Adım 4: MONTAJ ÖNCESİ HASH KONTROLÜ + KURGU
            if not self.checkpoint_manager.start_operation("kurgu", OperationType.VIDEO):
                log("Adım 4: Montaj Öncesi Hash Kontrolü")
                if not self.montaj_oncesi_hash_kontrol():
                    log("❌ MONTAJ İÇİN HAZIR DEĞİL - Varlık uyumsuzluğu tespit edildi", "ERROR")
                    self.varlik_uyumsuzlugu_coz()
                    # Varlık üretimini yeniden yap
                    return self.modulleri_calistir(kanal, konu, harf_sayisi)  # Recursive call
                
                # Hash kontrolü başarılı - montaja başla
                self.montaj_icin_gereksiz_dosyalari_temizle()
                
                log("Adım 4: Kurgu ve Montaj")
                if not komut_calistir(["python", "moduller/kurgu.py", json_yolu, ses_klasoru, gorsel_klasoru, final_video_yolu]):
                    self.checkpoint_manager.fail_operation("kurgu", "Kurgu modülü başarısız oldu")
                self.checkpoint_manager.complete_operation("kurgu", [final_video_yolu])
                # Legacy support
                self.adimi_tamamla("kurgu")
            
            # Adım 5: YouTube Yükleme
            if not self.checkpoint_manager.start_operation("youtube_upload", OperationType.UPLOAD):
                log("Adım 5: YouTube Yükleme")
                
                # Service account kontrolü
                service_account_file = "service_account.json"
                credentials_file = "credentials.json"
                
                if not os.path.exists(service_account_file) and not os.path.exists(credentials_file):
                    self.checkpoint_manager.fail_operation("youtube_upload", "YouTube için kimlik doğrulama dosyası bulunamadı! (service_account.json veya credentials.json gerekli)")

                if not komut_calistir(["python", "moduller/youtube_uploader.py", final_video_yolu, json_yolu]):
                    self.checkpoint_manager.fail_operation("youtube_upload", "YouTube Uploader modülü başarısız oldu")
                self.checkpoint_manager.complete_operation("youtube_upload")
                # Legacy support
                self.adimi_tamamla("youtube_upload")

            # API kullanım raporunu göster
            log("📊 Multi-API Kullanım Raporu:")
            print(self.api_manager.get_usage_report())
            
            # Clean up on complete success
            self.checkpoint_manager.cleanup_on_complete_success()
            
            log("🎉 FLEXIBLE MULTI-API PRODÜKSİYON BAŞARIYLA TAMAMLANDI!", "SUCCESS")

        except Exception as e:
            log(f"Prodüksiyon sırasında kritik bir hata oluştu: {e}", "CRITICAL")
            log("Program durduruluyor. Hatayı düzelttikten sonra tekrar çalıştırın.", "CRITICAL")
            
            # API kullanım durumunu da logla
            try:
                log("📊 Hata anındaki API durumu:")
                print(self.api_manager.get_usage_report())
            except:
                pass
            
            sys.exit(1)

    def baslat(self):
        """Ana workflow başlatma fonksiyonu"""
        log("🎬 Flexible Multi-API Yapımcı başlatılıyor...")
        
        # Sistem kontrolleri
        self.disk_alan_kontrol()
        
        # Günlük görev kontrolü
        gunluk_gorev = self.gunluk_gorev_al()
        
        if gunluk_gorev:
            # Otomatik mod
            self.is_manual = False
            log("🤖 Tam Otomatik Modda başlatılıyor...")
            kanal = gunluk_gorev["kanal_adi"]
            konu = gunluk_gorev["konu"]
            harf_sayisi = str(gunluk_gorev["harf_sayisi"])
            log(f"📅 Günlük görev: {kanal} - {konu}")
        else:
            # Manuel mod
            self.is_manual = True
            log("👤 Manuel İnteraktif Modda başlatılıyor...")
            kanal = input("Hangi kanalda video üretilecek? > ")
            konu = input("Videonun konusu ne olacak? > ")
            harf_sayisi = input("Hedef harf sayısı ne kadar olmalı? > ")
        
        # Proje klasörü oluştur
        proje_konu_slug = self.slugify(konu)[:50]
        kanal_ayarlari = self.kanal_ayarlarini_al(kanal)
        kanal_slug = kanal_ayarlari.get('slug', self.slugify(kanal))
        
        self.proje_yolu = os.path.join("kanallar", kanal_slug, proje_konu_slug)
        os.makedirs(self.proje_yolu, exist_ok=True)
        
        log(f"📁 Proje klasörü: {self.proje_yolu}")
        
        # Initialize checkpoint manager for this project
        project_name = f"{kanal_slug}_{proje_konu_slug}"
        self.checkpoint_manager = CheckpointManager(project_name, self.proje_yolu)
        
        # Durum dosyalarını yükle (legacy support)
        self.durumu_yukle()
        self.hash_durumunu_yukle()

        # Devam etme kontrolü
        if self.durum["tamamlanan_adimlar"]:
            if self.is_manual:
                cevap = input("Yarım kalmış proje bulundu. Devam edilsin mi? (E/H) > ").lower()
                if cevap != 'e': 
                    log("İşlem iptal edildi."); 
                    return
            else:
                log("Yarım kalmış proje bulundu. Otomatik olarak devam ediliyor.")
        
        # Modülleri çalıştır
        self.modulleri_calistir(kanal, konu, harf_sayisi)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flexible Multi-API Video Prodüksiyon Sistemi")
    parser.add_argument("--config", help="Otomatik mod için config dosyasının yolu")
    args = parser.parse_args()
    
    try:
        print("🎬 FLEXIBLE MULTI-API YAPIMCI BAŞLADI")
        print("=" * 60)
        print("🔧 Esnek yapılandırma sistemi aktif")
        print("🔄 Multi-API otomatik failover sistemi aktif")
        print("📊 API kullanım takibi ve maliyet hesaplama aktif")
        print("⚡ Gelişmiş hata yakalama ve kurtarma sistemi aktif")
        print("=" * 60)
        
        yapimci = FlexibleYapimci(config_file=args.config)
        yapimci.baslat()
        
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ KRITIK HATA: Beklenmeyen sistem hatası: {e}")
        
        # API durumunu da göster
        try:
            from api_manager import get_api_manager
            api_manager = get_api_manager()
            print("\n📊 Hata anındaki API durumu:")
            print(api_manager.get_usage_report())
        except:
            pass
        
        sys.exit(1)