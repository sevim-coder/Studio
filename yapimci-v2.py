# yapimci.py (Hata Düzeltilmiş Hali)

import os
import sys
import json
import subprocess
import argparse
import hashlib
import datetime
import shutil

# --- Proje Modüllerini İçeri Aktarma ---

# DEĞİŞTİRİLDİ: 'Yonetmen' sınıfı yerine, 'yonetmen.py' içindeki gerekli fonksiyonlar doğrudan import edildi.
from moduller.senarist import Senarist
from moduller.yonetmen import json_olustur as yonetmen_json_olustur
from moduller.yonetmen import dosya_oku as yonetmen_dosya_oku
from moduller.yonetmen import dosya_yaz as yonetmen_dosya_yaz
from moduller.seslendirmen import Seslendirmen
from moduller.gorsel_yonetmen import GorselYonetmen
# kurgu ve youtube_uploader'ı subprocess ile çağırmak daha stabil.

LOG_FILE = "yapimci_logs.txt"

def log(mesaj, seviye="INFO"):
    log_mesaji = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}][{seviye}] {mesaj}"
    print(log_mesaji)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
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
        surec = subprocess.run(komut_listesi, check=True, capture_output=True, text=True, encoding='utf-8')
        log(f"Komut başarıyla tamamlandı.")
        # İsteğe bağlı olarak stdout çıktısını loglayabilirsiniz:
        # if surec.stdout: log(f"Çıktı:\n{surec.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Komut hatası! Return Code: {e.returncode}\n--- HATA ---\n{e.stderr}", "ERROR")
        return False

class Yapimci:
    def __init__(self, config=None):
        self.config = config
        self.proje_yolu = ""
        self.durum = {}
        self.is_manual = not bool(config)

    def durumu_yukle(self):
        durum_dosyasi = os.path.join(self.proje_yolu, "status.json")
        if os.path.exists(durum_dosyasi):
            with open(durum_dosyasi, 'r', encoding='utf-8') as f: self.durum = json.load(f)
            log("Mevcut proje durumu yüklendi.")
        else:
            self.durum = {"tamamlanan_adımlar": [], "dosya_hashleri": {}}
            log("Yeni proje için durum dosyası oluşturuluyor.")

    def durumu_kaydet(self):
        durum_dosyasi = os.path.join(self.proje_yolu, "status.json")
        with open(durum_dosyasi, 'w', encoding='utf-8') as f: json.dump(self.durum, f, indent=2, ensure_ascii=False)

    def adimi_gec(self, adim_adi):
        return adim_adi in self.durum.get("tamamlanan_adımlar", [])

    def adimi_tamamla(self, adim_adi, dosyalar=[]):
        self.durum["tamamlanan_adımlar"].append(adim_adi)
        for dosya in dosyalar:
            if os.path.exists(dosya):
                self.durum["dosya_hashleri"][dosya] = dosya_hash_hesapla(dosya)
        self.durumu_kaydet()
        log(f"Adım tamamlandı ve durum kaydedildi: {adim_adi}")

    def hashleri_dogrula(self):
        if not self.durum.get("dosya_hashleri"): return True
        log("Varlık bütünlüğü kontrol ediliyor (hash check)...")
        for dosya, kayitli_hash in self.durum["dosya_hashleri"].items():
            if not os.path.exists(dosya):
                log(f"'{os.path.basename(dosya)}' dosyası eksik!", "WARNING")
                return False
            mevcut_hash = dosya_hash_hesapla(dosya)
            if mevcut_hash != kayitli_hash:
                log(f"'{os.path.basename(dosya)}' dosyası değiştirilmiş! Hash uyuşmazlığı.", "WARNING")
                return False
        log("Tüm varlıklar geçerli.")
        return True

    def gunu_al(self):
        gun_map = {"monday": "pazartesi", "tuesday": "sali", "wednesday": "carsamba", "thursday": "persembe", "friday": "cuma", "saturday": "cumartesi", "sunday": "pazar"}
        today_str = datetime.datetime.now().strftime("%A").lower()
        return gun_map.get(today_str, today_str)

    def baslat(self):
        if self.is_manual:
            log("Manuel İnteraktif Modda başlatılıyor...")
            kanal = input("Hangi kanalda video üretilecek? > ")
            konu = input("Videonun konusu ne olacak? > ")
            harf_sayisi = input("Hedef harf sayısı ne kadar olmalı? > ")
        else:
            log("Tam Otomatik Modda başlatılıyor...")
            gun = self.gunu_al()
            if gun not in self.config:
                log(f"Bugün ({gun}) için config.json'da bir görev yok. Çıkılıyor.")
                return
            # --- DOĞRU HALİ ---
            bugunun_gorevi = self.config[gun]
            kanal = bugunun_gorevi["kanal_adi"]
            konu = bugunun_gorevi["konu"]
            harf_sayisi = str(bugunun_gorevi["harf_sayisi"])
        
        proje_konu_slug = konu.replace(" ", "_").replace("?", "")
        self.proje_yolu = os.path.join("kanallar", kanal.replace(" ", "_"), proje_konu_slug)
        os.makedirs(self.proje_yolu, exist_ok=True)
        self.durumu_yukle()

        if self.durum["tamamlanan_adımlar"]:
            if not self.hashleri_dogrula():
                if self.is_manual:
                    cevap = input("Dosyalar değiştirilmiş. Proje sıfırlansın mı? (E/H) > ").lower()
                    if cevap != 'e': log("İşlem iptal edildi."); return
                else:
                    log("Otomatik modda hash uyuşmazlığı tespit edildi. Proje sıfırlanıyor...", "WARNING")
                    shutil.rmtree(self.proje_yolu)
                    os.makedirs(self.proje_yolu, exist_ok=True)
                self.durum = {"tamamlanan_adımlar": [], "dosya_hashleri": {}}
            else:
                if self.is_manual:
                    cevap = input("Yarım kalmış proje bulundu. Devam edilsin mi? (E/H) > ").lower()
                    if cevap != 'e': log("İşlem iptal edildi."); return
                else:
                    log("Yarım kalmış proje bulundu. Otomatik olarak devam ediliyor.")
        
        txt_yolu = os.path.join(self.proje_yolu, "senaryo.txt")
        json_yolu = os.path.join(self.proje_yolu, "proje.json")
        ses_klasoru = os.path.join(self.proje_yolu, "sesler")
        gorsel_klasoru = os.path.join(self.proje_yolu, "gorseller")
        final_video_yolu = os.path.join(self.proje_yolu, "final_video.mp4")

        try:
            if not self.adimi_gec("senaryo"):
                log("Adım 1: Senaryo Üretimi")
                senarist = Senarist()
                # Senaristin kendi dosya oluşturma mantığı var, bu yüzden onu direkt çağırıyoruz.
                # Ancak yapımcıya daha uyumlu olması için senarist.py'nin de düzenlenmesi gerekebilir.
                # Şimdilik en güvenli yol, orijinal modülleri subprocess ile çağırmak.
                if not komut_calistir(["python", "moduller/senarist.py", kanal, konu, harf_sayisi]):
                     raise Exception("Senarist modülü başarısız oldu.")
                self.adimi_tamamla("senaryo", [txt_yolu])

            if not self.adimi_gec("yonetmen"):
                log("Adım 2: Yönetmenlik (JSON Proje Oluşturma)")
                if not komut_calistir(["python", "moduller/yonetmen.py", txt_yolu, json_yolu]):
                    raise Exception("Yonetmen modülü başarısız oldu.")
                self.adimi_tamamla("yonetmen", [json_yolu])

            if not self.adimi_gec("varlik_uretimi"):
                log("Adım 3: Varlık Üretimi (Ses ve Görsel - Paralel)")
                ses_proses = subprocess.Popen(["python", "moduller/seslendirmen.py", json_yolu, ses_klasoru])
                gorsel_proses = subprocess.Popen(["python", "moduller/gorsel_yonetmen.py", json_yolu, gorsel_klasoru])
                
                ses_exit_code = ses_proses.wait()
                gorsel_exit_code = gorsel_proses.wait()

                if ses_exit_code != 0 or gorsel_exit_code != 0:
                    raise Exception("Ses veya görsel üretim adımı başarısız oldu.")
                
                ses_dosyalari = [os.path.join(ses_klasoru, f) for f in os.listdir(ses_klasoru)]
                gorsel_dosyalari = [os.path.join(gorsel_klasoru, f) for f in os.listdir(gorsel_klasoru)]
                self.adimi_tamamla("varlik_uretimi", ses_dosyalari + gorsel_dosyalari)

            if not self.adimi_gec("kurgu"):
                log("Adım 4: Kurgu ve Montaj")
                if not komut_calistir(["python", "moduller/kurgu.py", json_yolu, ses_klasoru, gorsel_klasoru, final_video_yolu]):
                    raise Exception("Kurgu modülü başarısız oldu.")
                self.adimi_tamamla("kurgu", [final_video_yolu])
            
            if not self.adimi_gec("youtube_upload"):
                log("Adım 5: YouTube Yükleme")
                if not komut_calistir(["python", "moduller/youtube_uploader.py", final_video_yolu, json_yolu]):
                   raise Exception("YouTube Uploader modülü başarısız oldu.")
                self.adimi_tamamla("youtube_upload")

            log("PRODÜKSİYON BAŞARIYLA TAMAMLANDI!", "SUCCESS")

        except Exception as e:
            log(f"Prodüksiyon sırasında kritik bir hata oluştu: {e}", "CRITICAL")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Oktabot Video Prodüksiyon Sistemi")
    parser.add_argument("--config", help="Otomatik mod için config.json dosyasının yolu")
    args = parser.parse_args()
    
    config_data = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception as e:
            log(f"Config dosyası okunamadı: {e}", "CRITICAL")
            sys.exit(1)
            
    yapimci = Yapimci(config=config_data)
    yapimci.baslat()
