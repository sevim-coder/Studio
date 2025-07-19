# kurgu.py - MÜKEMMEL KALİTE KONTROLÜ İLE (16:9 Format Garantili)

import os
import sys
import json
import random
import ffmpeg
import shutil
import psutil
import hashlib
import time
from mutagen.wave import WAVE
from PIL import Image
import subprocess

class KaliteKontrol:
    """Video üretim kalite kontrol sistemi"""
    
    @staticmethod
    def dosya_hash_kontrol(dosya_yolu):
        """Dosya bütünlük kontrolü"""
        try:
            with open(dosya_yolu, 'rb') as f:
                hash_md5 = hashlib.md5()
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"❌ KRITIK HATA: Dosya hash kontrolü başarısız: {e}")
            sys.exit(1)
    
    @staticmethod
    def disk_alan_kontrol(gerekli_mb=1000):
        """Disk alanı yeterliliği kontrolü"""
        try:
            disk_usage = shutil.disk_usage(".")
            bos_alan_mb = disk_usage.free / (1024 * 1024)
            if bos_alan_mb < gerekli_mb:
                print(f"❌ KRITIK HATA: Yetersiz disk alanı! Gerekli: {gerekli_mb}MB, Mevcut: {bos_alan_mb:.1f}MB")
                sys.exit(1)
            print(f"✅ Disk alanı yeterli: {bos_alan_mb:.1f}MB mevcut")
        except Exception as e:
            print(f"❌ KRITIK HATA: Disk alanı kontrolü başarısız: {e}")
            sys.exit(1)
    
    @staticmethod
    def memory_kontrol():
        """Bellek kullanım kontrolü"""
        try:
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                print(f"❌ KRITIK HATA: Bellek kullanımı çok yüksek: %{memory.percent}")
                sys.exit(1)
            print(f"✅ Bellek kullanımı normal: %{memory.percent}")
        except Exception as e:
            print(f"❌ KRITIK HATA: Bellek kontrolü başarısız: {e}")
            sys.exit(1)
    
    @staticmethod
    def ses_dosyasi_kalite_kontrol(dosya_yolu):
        """Ses dosyası detaylı kalite kontrolü"""
        if not os.path.exists(dosya_yolu):
            print(f"❌ KRITIK HATA: Ses dosyası bulunamadı: {dosya_yolu}")
            sys.exit(1)
        
        try:
            # WAVE dosyası header kontrolü
            audio = WAVE(dosya_yolu)
            info = audio.info
            
            # Süre kontrolü
            if info.length < 0.1:
                print(f"❌ KRITIK HATA: Ses dosyası çok kısa ({info.length}s): {dosya_yolu}")
                sys.exit(1)
            
            if info.length > 300:  # 5 dakikadan uzun
                print(f"❌ KRITIK HATA: Ses dosyası çok uzun ({info.length}s): {dosya_yolu}")
                sys.exit(1)
            
            # Bit rate kontrolü
            if info.bitrate < 64000:  # 64kbps minimum
                print(f"❌ KRITIK HATA: Ses kalitesi çok düşük ({info.bitrate}bps): {dosya_yolu}")
                sys.exit(1)
            
            # Sample rate kontrolü
            if info.sample_rate < 16000:
                print(f"❌ KRITIK HATA: Sample rate çok düşük ({info.sample_rate}Hz): {dosya_yolu}")
                sys.exit(1)
            
            # Dosya boyutu kontrolü (çok küçükse bozuk olabilir)
            dosya_boyutu = os.path.getsize(dosya_yolu)
            if dosya_boyutu < 1024:  # 1KB'den küçük
                print(f"❌ KRITIK HATA: Ses dosyası çok küçük ({dosya_boyutu} bytes): {dosya_yolu}")
                sys.exit(1)
            
            print(f"✅ Ses kalite kontrolü başarılı: {os.path.basename(dosya_yolu)} ({info.length:.2f}s, {info.bitrate}bps)")
            return info.length
            
        except Exception as e:
            print(f"❌ KRITIK HATA: Ses dosyası bozuk veya okunamıyor: {dosya_yolu} - {e}")
            sys.exit(1)
    
    @staticmethod
    def gorsel_dosyasi_kalite_kontrol(dosya_yolu):
        """Görsel dosyası detaylı kalite kontrolü"""
        if not os.path.exists(dosya_yolu):
            print(f"❌ KRITIK HATA: Görsel dosyası bulunamadı: {dosya_yolu}")
            sys.exit(1)
        
        try:
            # PIL ile görsel kontrolü
            with Image.open(dosya_yolu) as img:
                width, height = img.size
                
                # Boyut kontrolü
                if width < 100 or height < 100:
                    print(f"❌ KRITIK HATA: Görsel çok küçük ({width}x{height}): {dosya_yolu}")
                    sys.exit(1)
                
                if width > 4096 or height > 4096:
                    print(f"❌ KRITIK HATA: Görsel çok büyük ({width}x{height}): {dosya_yolu}")
                    sys.exit(1)
                
                # Format kontrolü
                if img.format not in ['PNG', 'JPEG', 'JPG']:
                    print(f"❌ KRITIK HATA: Desteklenmeyen görsel format ({img.format}): {dosya_yolu}")
                    sys.exit(1)
                
                # Dosya boyutu kontrolü
                dosya_boyutu = os.path.getsize(dosya_yolu)
                if dosya_boyutu < 1024:  # 1KB'den küçük
                    print(f"❌ KRITIK HATA: Görsel dosyası çok küçük ({dosya_boyutu} bytes): {dosya_yolu}")
                    sys.exit(1)
                
                if dosya_boyutu > 50 * 1024 * 1024:  # 50MB'den büyük
                    print(f"❌ KRITIK HATA: Görsel dosyası çok büyük ({dosya_boyutu / (1024*1024):.1f}MB): {dosya_yolu}")
                    sys.exit(1)
                
                print(f"✅ Görsel kalite kontrolü başarılı: {os.path.basename(dosya_yolu)} ({width}x{height}, {img.format})")
                
        except Exception as e:
            print(f"❌ KRITIK HATA: Görsel dosyası bozuk veya okunamıyor: {dosya_yolu} - {e}")
            sys.exit(1)
    
    @staticmethod
    def video_kalite_kontrol(video_yolu):
        """Video dosyası detaylı kalite kontrolü"""
        if not os.path.exists(video_yolu):
            print(f"❌ KRITIK HATA: Video dosyası bulunamadı: {video_yolu}")
            sys.exit(1)
        
        try:
            # FFprobe ile video analizi
            probe = ffmpeg.probe(video_yolu)
            
            # Stream kontrolü
            video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
            
            if not video_streams:
                print(f"❌ KRITIK HATA: Video akışı bulunamadı: {video_yolu}")
                sys.exit(1)
            
            video_stream = video_streams[0]
            
            # Video süresi kontrolü
            video_sure = float(video_stream.get('duration', 0))
            if video_sure < 0.5:
                print(f"❌ KRITIK HATA: Video çok kısa ({video_sure}s): {video_yolu}")
                sys.exit(1)
            
            # Çözünürlük kontrolü
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            
            if width < 320 or height < 240:
                print(f"❌ KRITIK HATA: Video çözünürlüğü çok düşük ({width}x{height}): {video_yolu}")
                sys.exit(1)
            
            # Dosya boyutu kontrolü
            dosya_boyutu = os.path.getsize(video_yolu)
            if dosya_boyutu < 1024:  # 1KB'den küçük
                print(f"❌ KRITIK HATA: Video dosyası çok küçük ({dosya_boyutu} bytes): {video_yolu}")
                sys.exit(1)
            
            print(f"✅ Video kalite kontrolü başarılı: {os.path.basename(video_yolu)}")
            print(f"   📊 Süre: {video_sure:.2f}s, Çözünürlük: {width}x{height}, Boyut: {dosya_boyutu/(1024*1024):.1f}MB")
            
            return True
            
        except Exception as e:
            print(f"❌ KRITIK HATA: Video kalite kontrolü başarısız: {video_yolu} - {e}")
            sys.exit(1)

class FFmpegGuvenceli:
    """Güvenli FFmpeg işlem yöneticisi"""
    
    @staticmethod
    def guvenceli_calistir_subprocess(komut_listesi, aciklama, kritik=True):
        """FFmpeg komutunu subprocess ile güvenli şekilde çalıştırır"""
        print(f"🔧 {aciklama}...")
        
        try:
            # FFmpeg komutunu çalıştır
            result = subprocess.run(
                komut_listesi,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Return code kontrolü
            if result.returncode != 0:
                print(f"❌ KRITIK HATA: FFmpeg işlemi başarısız ({aciklama})")
                print(f"   Komut: {' '.join(komut_listesi)}")
                print(f"   Return code: {result.returncode}")
                if result.stderr:
                    print(f"   Stderr: {result.stderr}")
                if result.stdout:
                    print(f"   Stdout: {result.stdout}")
                if kritik:
                    sys.exit(1)
                return False
            
            print(f"✅ {aciklama} başarılı")
            return True
            
        except Exception as e:
            print(f"❌ KRITIK HATA: FFmpeg çalıştırılamadı ({aciklama}): {e}")
            if kritik:
                sys.exit(1)
            return False

class Kurgu:
    def __init__(self, proje_json_yolu, ses_klasoru, gorsel_klasoru, cikti_yolu):
        print("🎞️ Kurgu modülü başlatılıyor...")
        print("🔍 Kapsamlı kalite kontrol sistemi aktif...")
        
        # Sistem kontrolleri
        KaliteKontrol.disk_alan_kontrol(2000)  # 2GB minimum
        KaliteKontrol.memory_kontrol()
        
        try:
            self.proje = self.json_oku(proje_json_yolu)
            self.ses_klasoru = ses_klasoru
            self.gorsel_klasoru = gorsel_klasoru
            self.cikti_yolu = cikti_yolu
            self.gecici_klasor = os.path.join(os.path.dirname(cikti_yolu), "gecici_klipler")
            self.temizlik_listesi = []  # Temizlenecek dosyalar
            
            # Çıktı klasörü oluştur
            os.makedirs(self.gecici_klasor, exist_ok=True)
            
            # Yazma izni kontrolü
            test_dosya = os.path.join(self.gecici_klasor, "test_write.tmp")
            try:
                with open(test_dosya, 'w') as f:
                    f.write("test")
                os.remove(test_dosya)
            except Exception as e:
                print(f"❌ KRITIK HATA: Yazma izni yok: {self.gecici_klasor} - {e}")
                sys.exit(1)
            
            print("✅ Kurgu modülü hazır!")
        except Exception as e:
            print(f"❌ HATA: Kurgu modülü başlatılamadı: {e}")
            sys.exit(1)
    
    def __del__(self):
        """Yıkıcı - temizlik işlemleri"""
        self.temizlik_yap()
    
    def temizlik_yap(self):
        """Geçici dosyaları temizle"""
        try:
            for dosya in self.temizlik_listesi:
                if os.path.exists(dosya):
                    os.remove(dosya)
            
            if os.path.exists(self.gecici_klasor):
                shutil.rmtree(self.gecici_klasor)
                print("🧹 Geçici dosyalar temizlendi")
                
        except Exception as e:
            print(f"⚠️ Temizlik hatası: {e}")
    
    def json_oku(self, dosya_yolu):
        print(f"📖 Proje dosyası okunuyor: {dosya_yolu}")
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # JSON yapı doğrulama
            self.json_yapisini_dogrula(data)
            return data
            
        except FileNotFoundError:
            print(f"❌ HATA: '{dosya_yolu}' dosyası bulunamadı.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ HATA: '{dosya_yolu}' geçerli bir JSON dosyası değil: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ HATA: JSON okuma sırasında problem: {e}")
            sys.exit(1)
    
    def json_yapisini_dogrula(self, data):
        """JSON yapısının tam doğrulaması"""
        print("🔍 JSON yapısı doğrulanıyor...")
        
        gerekli_alanlar = ['hikaye_yapisi', 'youtube_bilgileri', 'ffmpeg_ayarlari']
        for alan in gerekli_alanlar:
            if alan not in data:
                print(f"❌ KRITIK HATA: JSON'da '{alan}' alanı eksik!")
                sys.exit(1)
        
        hikaye = data['hikaye_yapisi']
        gerekli_bolumler = ['giris', 'gelisme', 'sonuc']
        
        toplam_segment = 0
        for bolum_adi in gerekli_bolumler:
            if bolum_adi not in hikaye:
                print(f"❌ KRITIK HATA: '{bolum_adi}' bölümü eksik!")
                sys.exit(1)
            
            bolum = hikaye[bolum_adi]
            if 'bolum_kisaltmasi' not in bolum:
                print(f"❌ KRITIK HATA: '{bolum_adi}' bölümünde 'bolum_kisaltmasi' eksik!")
                sys.exit(1)
            
            if 'paragraflar' not in bolum:
                print(f"❌ KRITIK HATA: '{bolum_adi}' bölümünde 'paragraflar' eksik!")
                sys.exit(1)
            
            for paragraf in bolum['paragraflar']:
                if 'segmentler' not in paragraf:
                    print(f"❌ KRITIK HATA: Paragrafta 'segmentler' eksik!")
                    sys.exit(1)
                
                for segment in paragraf['segmentler']:
                    gerekli_segment_alanlari = ['segment_numarasi', 'metin', 'gorsel_prompt']
                    for alan in gerekli_segment_alanlari:
                        if alan not in segment:
                            print(f"❌ KRITIK HATA: Segmentte '{alan}' eksik!")
                            sys.exit(1)
                    
                    toplam_segment += 1
        
        if toplam_segment == 0:
            print("❌ KRITIK HATA: Hiçbir segment bulunamadı!")
            sys.exit(1)
        
        if toplam_segment > 100:
            print(f"❌ KRITIK HATA: Çok fazla segment ({toplam_segment}), maksimum 100!")
            sys.exit(1)
        
        print(f"✅ JSON yapısı geçerli: {toplam_segment} segment bulundu")

    def sessiz_klip_olustur(self, segment_bilgisi, ses_suresi):
        """Her segment için mükemmel kalitede animasyonlu klip oluşturur - TÜM FORMATLAR 16:9'a DÖNÜŞTÜRÜLECEKTİR"""
        gorsel_yolu = os.path.join(self.gorsel_klasoru, f"{segment_bilgisi['id']}.png")
        klip_suresi = ses_suresi + 1.0
        cikti_klip_yolu = os.path.join(self.gecici_klasor, f"{segment_bilgisi['id']}.mp4")
        
        # Görsel kalite kontrolü
        KaliteKontrol.gorsel_dosyasi_kalite_kontrol(gorsel_yolu)
        
        # Görsel boyutlarını kontrol et
        try:
            with Image.open(gorsel_yolu) as img:
                original_width, original_height = img.size
                original_ratio = original_width / original_height
                target_ratio = 16 / 9  # 1.777...
                
                print(f"  📐 Orijinal boyut: {original_width}x{original_height} (oran: {original_ratio:.3f})")
                print(f"  🎯 Hedef oran: 16:9 ({target_ratio:.3f})")
                
        except Exception as e:
            print(f"❌ KRITIK HATA: Görsel boyut analizi başarısız: {e}")
            sys.exit(1)
        
        print(f"  🎬 Klip oluşturuluyor: {os.path.basename(cikti_klip_yolu)} ({klip_suresi:.2f}s)")
        
        try:
            # Efekt kontrolü
            efekt = segment_bilgisi.get('ic_efekt', {})
            print(f"  🎭 Efekt kontrolü: {efekt}")
            
            # Video filtresi oluştur
            video_filter = self.build_video_filter(original_ratio, target_ratio, efekt, klip_suresi)
            
            # FFmpeg komutu
            komut = [
                'ffmpeg',
                '-loop', '1',
                '-i', gorsel_yolu,
                '-t', str(klip_suresi),
                '-vf', video_filter,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                '-y',
                cikti_klip_yolu
            ]
            
            # FFmpeg komutunu çalıştır
            FFmpegGuvenceli.guvenceli_calistir_subprocess(
                komut, 
                f"Video klip oluşturma: {os.path.basename(cikti_klip_yolu)}"
            )
            
            # Oluşturulan klibi kontrol et - 16:9 formatını doğrula
            self.validate_video_format(cikti_klip_yolu, target_ratio)
            
            # Genel kalite kontrolü
            KaliteKontrol.video_kalite_kontrol(cikti_klip_yolu)
            
            self.temizlik_listesi.append(cikti_klip_yolu)
            return cikti_klip_yolu
            
        except Exception as e:
            print(f"❌ KRITIK HATA: Video klip oluşturulamadı: {e}")
            sys.exit(1)

    def build_video_filter(self, original_ratio, target_ratio, efekt, klip_suresi):
        """Video filtresi oluşturur"""
        
        # Temel 16:9 dönüştürme filtresi
        if abs(original_ratio - target_ratio) < 0.01:
            # Zaten 16:9 oranında
            base_filter = 'scale=1920:1080:force_original_aspect_ratio=exact'
        elif original_ratio > target_ratio:
            # Yatay görsel (daha geniş) - üst ve alt boşluk
            base_filter = 'scale=1920:-1:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black'
        else:
            # Dikey görsel (portre) - sol ve sağ boşluk  
            base_filter = 'scale=-1:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black'
        
        # Efekt ekleme
        if efekt and efekt.get('tip') == 'zoom':
            return self.add_zoom_effect(base_filter, efekt, klip_suresi)
        elif efekt and efekt.get('tip') == 'pan':
            return self.add_pan_effect(base_filter, efekt, klip_suresi)
        else:
            # Efekt yok
            return base_filter

    def add_zoom_effect(self, base_filter, efekt, klip_suresi):
        """Zoom efekti ekler"""
        yon = efekt.get('yon', 'in')
        hiz = efekt.get('hiz', 'normal')
        
        # Türkçe kelimeleri İngilizce'ye çevir
        if hiz == 'yavas':
            hiz = 'slow'
        elif hiz == 'hizli':
            hiz = 'fast'
        elif hiz == 'cok_yavas':
            hiz = 'slow'
        
        if yon == 'in':
            zoom_carpan = {'slow': 0.0008, 'normal': 0.0015, 'fast': 0.0025}.get(hiz, 0.0015)
            zoom_filter = f"zoompan=z='min(zoom+{zoom_carpan},1.5)':d={int(klip_suresi*30)}:s=1920x1080:fps=30"
            print(f"  🔍 Zoom In efekti uygulanıyor (hız: {hiz})")
        else:  # zoom out
            zoom_carpan = {'slow': 0.0005, 'normal': 0.0010, 'fast': 0.0020}.get(hiz, 0.0010)
            zoom_filter = f"zoompan=z='max(zoom-{zoom_carpan},1.0)':d={int(klip_suresi*30)}:s=1920x1080:fps=30"
            print(f"  🔍 Zoom Out efekti uygulanıyor (hız: {hiz})")
        
        return f"{base_filter},{zoom_filter}"

    def add_pan_effect(self, base_filter, efekt, klip_suresi):
        """Pan efekti ekler"""
        yon = efekt.get('yon', 'left')
        hiz = efekt.get('hiz', 'normal')
        
        # Türkçe kelimeleri İngilizce'ye çevir
        if yon == 'sag':
            yon = 'right'
        elif yon == 'sol':
            yon = 'left'
        elif yon == 'yukari':
            yon = 'up'
        elif yon == 'asagi':
            yon = 'down'
        
        if hiz == 'yavas':
            hiz = 'slow'
        elif hiz == 'hizli':
            hiz = 'fast'
        elif hiz == 'cok_yavas':
            hiz = 'slow'
        
        # Pan filtreleri
        if yon == 'left':
            pan_filter = f"zoompan=x='min(max(x,0),iw-iw/zoom)':y='ih/zoom/2':z=1.2:d={int(klip_suresi*30)}:s=1920x1080:fps=30"
        elif yon == 'right':
            pan_filter = f"zoompan=x='max(min(x,iw-iw/zoom),0)':y='ih/zoom/2':z=1.2:d={int(klip_suresi*30)}:s=1920x1080:fps=30"
        elif yon == 'up':
            pan_filter = f"zoompan=x='iw/zoom/2':y='min(max(y,0),ih-ih/zoom)':z=1.2:d={int(klip_suresi*30)}:s=1920x1080:fps=30"
        elif yon == 'down':
            pan_filter = f"zoompan=x='iw/zoom/2':y='max(min(y,ih-ih/zoom),0)':z=1.2:d={int(klip_suresi*30)}:s=1920x1080:fps=30"
        else:
            pan_filter = f"zoompan=z=1.0:d={int(klip_suresi*30)}:s=1920x1080:fps=30"
        
        print(f"  🎬 Pan {yon.upper()} efekti uygulanıyor (hız: {hiz})")
        return f"{base_filter},{pan_filter}"

    def validate_video_format(self, video_yolu, target_ratio):
        """Video formatını doğrular"""
        try:
            probe = ffmpeg.probe(video_yolu)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            
            if video_stream:
                width = int(video_stream.get('width', 0))
                height = int(video_stream.get('height', 0))
                
                if width != 1920 or height != 1080:
                    print(f"❌ KRITIK HATA: Video 16:9 formatında değil! Boyut: {width}x{height}")
                    sys.exit(1)
                
                actual_ratio = width / height
                if abs(actual_ratio - target_ratio) > 0.01:
                    print(f"❌ KRITIK HATA: Video oranı 16:9 değil! Oran: {actual_ratio:.3f}")
                    sys.exit(1)
                
                print(f"  ✅ 16:9 format kontrolü başarılı: {width}x{height}")
                
        except Exception as e:
            print(f"❌ KRITIK HATA: Video format kontrolü başarısız: {e}")
            sys.exit(1)

    def get_video_duration(self, video_yolu):
        """Video süresini alır"""
        try:
            probe = ffmpeg.probe(video_yolu)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if video_stream:
                return float(video_stream.get('duration', 0))
            return 0.0
        except Exception as e:
            print(f"⚠️ Video süre ölçümü başarısız: {e}")
            return 0.0

    def gecis_efekti_uygula_duzeltilmis(self, klip1_yolu, klip2_yolu, gecis_tipi, cikti_yolu, gecis_suresi=0.5):
        """İki klip arasında DOĞRU geçiş efekti uygular - Offset hesaplamasıyla"""
        print(f"  🎭 Geçiş efekti uygulanıyor: {gecis_tipi}")
        
        try:
            # Video sürelerini al
            klip1_sure = self.get_video_duration(klip1_yolu)
            klip2_sure = self.get_video_duration(klip2_yolu)
            
            # Offset hesapla - ilk videonun sonundan gecis_suresi kadar önce başla
            offset = max(0, klip1_sure - gecis_suresi)
            
            print(f"    📊 Klip1 süre: {klip1_sure:.2f}s, Klip2 süre: {klip2_sure:.2f}s, Offset: {offset:.2f}s")
            
            if gecis_tipi == 'crossfade':
                # Crossfade geçişi - OFFSET DÜZELTME
                komut = [
                    'ffmpeg',
                    '-i', klip1_yolu,
                    '-i', klip2_yolu,
                    '-filter_complex', f'[0][1]xfade=transition=fade:duration={gecis_suresi}:offset={offset}',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-y',
                    cikti_yolu
                ]
            elif gecis_tipi == 'slide_left':
                # Sola kaydırma geçişi
                komut = [
                    'ffmpeg',
                    '-i', klip1_yolu,
                    '-i', klip2_yolu,
                    '-filter_complex', f'[0][1]xfade=transition=slideleft:duration={gecis_suresi}:offset={offset}',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-y',
                    cikti_yolu
                ]
            elif gecis_tipi == 'slide_right':
                # Sağa kaydırma geçişi
                komut = [
                    'ffmpeg',
                    '-i', klip1_yolu,
                    '-i', klip2_yolu,
                    '-filter_complex', f'[0][1]xfade=transition=slideright:duration={gecis_suresi}:offset={offset}',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-y',
                    cikti_yolu
                ]
            elif gecis_tipi == 'glitch':
                # Glitch efekti
                komut = [
                    'ffmpeg',
                    '-i', klip1_yolu,
                    '-i', klip2_yolu,
                    '-filter_complex', f'[0][1]xfade=transition=pixelize:duration={gecis_suresi}:offset={offset}',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-y',
                    cikti_yolu
                ]
            elif gecis_tipi == 'fade_to_black':
                # Siyaha solma geçişi
                komut = [
                    'ffmpeg',
                    '-i', klip1_yolu,
                    '-i', klip2_yolu,
                    '-filter_complex', f'[0][1]xfade=transition=fadeblack:duration={gecis_suresi}:offset={offset}',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-y',
                    cikti_yolu
                ]
            else:
                # Varsayılan: basit crossfade
                print(f"  ⚠️ Bilinmeyen geçiş efekti '{gecis_tipi}', crossfade kullanılıyor")
                komut = [
                    'ffmpeg',
                    '-i', klip1_yolu,
                    '-i', klip2_yolu,
                    '-filter_complex', f'[0][1]xfade=transition=fade:duration={gecis_suresi}:offset={offset}',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-y',
                    cikti_yolu
                ]
            
            # Geçiş efektini uygula
            FFmpegGuvenceli.guvenceli_calistir_subprocess(
                komut, 
                f"Geçiş efekti uygulama: {gecis_tipi}"
            )
            
            # Sonucu kontrol et
            KaliteKontrol.video_kalite_kontrol(cikti_yolu)
            return True
            
        except Exception as e:
            print(f"❌ KRITIK HATA: Geçiş efekti uygulanamadı: {e}")
            return False

    def klipleri_gercis_efektleri_ile_birlestir(self, klip_bilgileri):
        """Klipleri geçiş efektleri ile birleştirir - DÜZELTİLMİŞ VERSİYON"""
        print("\n🎬 Klipleri geçiş efektleri ile birleştiriliyor...")
        
        if len(klip_bilgileri) == 0:
            print("❌ KRITIK HATA: Birleştirilecek klip yok!")
            sys.exit(1)
        
        if len(klip_bilgileri) == 1:
            # Tek klip varsa, direkt kopyala
            print("  ℹ️ Tek klip mevcut, geçiş efekti uygulanmayacak")
            final_video = os.path.join(self.gecici_klasor, "final_gecisli.mp4")
            shutil.copy2(klip_bilgileri[0]['klip_yolu'], final_video)
            self.temizlik_listesi.append(final_video)
            return final_video
        
        # İlk klipten başla
        onceki_klip = klip_bilgileri[0]['klip_yolu']
        
        for i in range(1, len(klip_bilgileri)):
            sonraki_klip = klip_bilgileri[i]['klip_yolu']
            gecis_efekti = klip_bilgileri[i-1]['gecis_efekti']  # Önceki segmentin geçiş efekti
            
            # Geçici dosya adı
            gecici_cikti = os.path.join(self.gecici_klasor, f"gecis_{i}.mp4")
            
            print(f"  🔄 Klip {i}/{len(klip_bilgileri)-1}: {gecis_efekti} geçişi uygulanıyor")
            
            # DÜZELTME: Geçiş efektini doğru fonksiyonla uygula
            success = self.gecis_efekti_uygula_duzeltilmis(onceki_klip, sonraki_klip, gecis_efekti, gecici_cikti)
            
            if success:
                # Eski geçici dosyayı temizle (ilk klip değilse)
                if i > 1 and os.path.exists(onceki_klip) and onceki_klip != klip_bilgileri[0]['klip_yolu']:
                    os.remove(onceki_klip)
                
                # Bir sonraki iterasyon için güncelle
                onceki_klip = gecici_cikti
                self.temizlik_listesi.append(gecici_cikti)
            else:
                # Geçiş efekti başarısızsa, klipleri basit concat ile birleştir
                print(f"  ⚠️ Geçiş efekti başarısız, basit birleştirme yapılıyor")
                return self.klipleri_basit_birlestir([item['klip_yolu'] for item in klip_bilgileri])
        
        # Final dosyasını yeniden adlandır
        final_video = os.path.join(self.gecici_klasor, "final_gecisli.mp4")
        if os.path.exists(final_video):
            os.remove(final_video)
        shutil.move(onceki_klip, final_video)
        self.temizlik_listesi.append(final_video)
        
        print(f"  ✅ Geçiş efektleri ile birleştirme tamamlandı")
        return final_video

    def klipleri_basit_birlestir(self, klip_yollari):
        """Klipleri basit concat ile birleştirir (fallback)"""
        print("  🔧 Basit birleştirme (concat) yapılıyor...")
        
        final_video = os.path.join(self.gecici_klasor, "final_basit.mp4")
        gecici_liste = os.path.join(self.gecici_klasor, "basit_liste.txt")
        
        try:
            with open(gecici_liste, "w", encoding='utf-8') as f:
                for klip in klip_yollari:
                    normalized_path = os.path.abspath(klip).replace('\\', '/')
                    f.write(f"file '{normalized_path}'\n")
            
            self.temizlik_listesi.append(gecici_liste)
            
            # Concat komutu
            komut = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', gecici_liste,
                '-c', 'copy',
                '-y',
                final_video
            ]
            
            FFmpegGuvenceli.guvenceli_calistir_subprocess(komut, "Basit klip birleştirme")
            self.temizlik_listesi.append(final_video)
            return final_video
            
        except Exception as e:
            print(f"❌ KRITIK HATA: Basit birleştirme başarısız: {e}")
            sys.exit(1)

    def calistir(self):
        print("🎬 Kurgu süreci başlatılıyor...")
        print("🔍 Mükemmel kalite kontrol sistemi çalışıyor...")
        
        start_time = time.time()
        
        try:
            # 1. Segment bilgilerini topla ve kontrol et
            print("\n📋 Segment bilgileri toplanıyor...")
            segmentler = []
            
            for bolum_adi, bolum in self.proje['hikaye_yapisi'].items():
                for paragraf in bolum['paragraflar']:
                    for s in paragraf['segmentler']:
                        segment_id = f"{bolum['bolum_kisaltmasi']}-{paragraf['paragraf_numarasi']}-{s['segment_numarasi']}"
                        ses_yolu = os.path.join(self.ses_klasoru, f"{segment_id}.wav")
                        
                        # Her ses dosyasını kalite kontrolünden geçir
                        ses_suresi = KaliteKontrol.ses_dosyasi_kalite_kontrol(ses_yolu)
                        
                        segmentler.append({
                            "id": segment_id,
                            "sure": ses_suresi,
                            "ic_efekt": s.get('ic_efekt', {}),
                            "gecis_efekti": s.get('gecis_efekti', 'crossfade')
                        })

            if not segmentler:
                print("❌ KRITIK HATA: Hiçbir segment bulunamadı!")
                sys.exit(1)

            print(f"✅ {len(segmentler)} segment başarıyla kontrol edildi")
            toplam_sure = sum(s['sure'] for s in segmentler)
            print(f"📊 Toplam video süresi: {toplam_sure:.2f} saniye")

            # 2. Video klipleri oluştur (iç efektler ile)
            print("\n🎥 Video klipleri oluşturuluyor (iç efektler ile)...")
            klip_bilgileri = []
            
            for i, s_bilgi in enumerate(segmentler):
                klip_yolu = self.sessiz_klip_olustur(s_bilgi, s_bilgi['sure'])
                if klip_yolu:
                    klip_bilgileri.append({
                        'klip_yolu': klip_yolu,
                        'segment_id': s_bilgi['id'],
                        'gecis_efekti': s_bilgi['gecis_efekti']
                    })
                
                # İlerleme gösterimi
                progress = ((i + 1) / len(segmentler)) * 100
                print(f"  📈 İlerleme: {progress:.1f}% ({i+1}/{len(segmentler)})")
            
            if not klip_bilgileri:
                print("❌ KRITIK HATA: Hiçbir video klip oluşturulamadı!")
                sys.exit(1)
            
            print(f"✅ {len(klip_bilgileri)} video klip başarıyla oluşturuldu")
            
            # 3. Klipleri geçiş efektleri ile birleştir - DÜZELTİLMİŞ VERSİYON
            print("\n🎬 Klipleri geçiş efektleri ile birleştiriliyor (DÜZELTME)...")
            final_sessiz_video = self.klipleri_gercis_efektleri_ile_birlestir(klip_bilgileri)

            # 4. Ses dosyalarını birleştir
            print("\n🎙️ Anlatım sesleri birleştiriliyor...")
            ses_liste_dosyasi = os.path.join(self.gecici_klasor, "ses_listesi.txt")
            
            try:
                with open(ses_liste_dosyasi, "w", encoding='utf-8') as f:
                    for s in segmentler:
                        ses_yolu = os.path.join(self.ses_klasoru, f"{s['id']}.wav")
                        normalized_path = os.path.abspath(ses_yolu).replace('\\', '/')
                        f.write(f"file '{normalized_path}'\n")
                        
                self.temizlik_listesi.append(ses_liste_dosyasi)
            except Exception as e:
                print(f"❌ KRITIK HATA: Ses listesi oluşturulamadı: {e}")
                sys.exit(1)

            birlesik_ses = os.path.join(self.gecici_klasor, "birlesik_ses.wav")
            
            # Ses birleştirme komutu
            ses_birlesim_komutu = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', ses_liste_dosyasi,
                '-c', 'copy',
                '-y',
                birlesik_ses
            ]
            
            FFmpegGuvenceli.guvenceli_calistir_subprocess(ses_birlesim_komutu, "Ses dosyalarını birleştirme")
            self.temizlik_listesi.append(birlesik_ses)

            # 5. Müzik hazırlama (opsiyonel)
            print("\n🎵 Arka plan müziği kontrol ediliyor...")
            muzik_dosyasi = None
            video_suresi = toplam_sure
            
            muzik_klasoru = os.path.join(os.path.dirname(os.path.dirname(__file__)), "muzikler")
            if not os.path.exists(muzik_klasoru):
                muzik_klasoru = "muzikler"  # Fallback: mevcut klasörde ara
            if os.path.exists(muzik_klasoru):
                try:
                    muzik_dosyalari = []
                    for dosya in os.listdir(muzik_klasoru):
                        if dosya.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac')):
                            muzik_yolu = os.path.join(muzik_klasoru, dosya)
                            muzik_dosyalari.append(muzik_yolu)
                    
                    if muzik_dosyalari:
                        muzik_dosyasi = random.choice(muzik_dosyalari)
                        print(f"🎵 Seçilen müzik: {os.path.basename(muzik_dosyasi)}")
                    else:
                        print("⚠️ Kullanılabilir müzik dosyası bulunamadı")
                        
                except Exception as e:
                    print(f"⚠️ Müzik hazırlama hatası: {e}")
                    muzik_dosyasi = None
            else:
                print("⚠️ Müzik klasörü bulunamadı")

            # 6. Final montaj
            print("\n🎞️ Final video montajı yapılıyor...")
            
            if muzik_dosyasi:
                # Müzik ile montaj
                final_komutu = [
                    'ffmpeg',
                    '-i', final_sessiz_video,
                    '-i', birlesik_ses,
                    '-i', muzik_dosyasi,
                    '-filter_complex', f'[1]volume=1.0[a1];[2]volume=0.15,atrim=duration={video_suresi}[a2];[a1][a2]amix=inputs=2:duration=first[aout]',
                    '-map', '0:v',
                    '-map', '[aout]',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-movflags', 'faststart',
                    '-y',
                    self.cikti_yolu
                ]
            else:
                # Müzik olmadan montaj
                final_komutu = [
                    'ffmpeg',
                    '-i', final_sessiz_video,
                    '-i', birlesik_ses,
                    '-map', '0:v',
                    '-map', '1:a',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-movflags', 'faststart',
                    '-y',
                    self.cikti_yolu
                ]
            
            FFmpegGuvenceli.guvenceli_calistir_subprocess(final_komutu, "Final video montajı")

            # 7. Final kalite kontrolü
            print("\n🔍 Final video kalite kontrolü...")
            KaliteKontrol.video_kalite_kontrol(self.cikti_yolu)
            
            # 8. Final rapor
            end_time = time.time()
            islem_suresi = end_time - start_time
            final_boyut = os.path.getsize(self.cikti_yolu) / (1024 * 1024)
            
            print("\n" + "=" * 60)
            print("🎉 KURGU BAŞARIYLA TAMAMLANDI!")
            print("=" * 60)
            print(f"📹 Final video: {os.path.basename(self.cikti_yolu)}")
            print(f"📊 Video boyutu: {final_boyut:.1f}MB")
            print(f"⏱️ İşlem süresi: {islem_suresi:.1f} saniye")
            print(f"🎬 Segment sayısı: {len(segmentler)}")
            print(f"🎵 Müzik: {'Evet' if muzik_dosyasi else 'Hayır'}")
            print(f"✅ Kalite kontrolü: BAŞARILI")
            print(f"🎭 Geçiş efektleri: DÜZELTME UYGULANARAK ÇALIŞIYOR")
            print("=" * 60)

        except Exception as e:
            print(f"❌ KRITIK HATA: Beklenmeyen kurgu hatası: {e}")
            self.temizlik_yap()
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Kullanım: python kurgu.py [proje.json] [ses_klasoru] [gorsel_klasoru] [cikti_video.mp4]")
        sys.exit(1)
    
    # Argüman kontrolü
    proje_json = sys.argv[1]
    ses_klasoru = sys.argv[2]
    gorsel_klasoru = sys.argv[3]
    cikti_video = sys.argv[4]
    
    # Dosya varlık kontrolleri
    kontrol_dosyalari = [
        (proje_json, "Proje JSON dosyası"),
        (ses_klasoru, "Ses klasörü"),
        (gorsel_klasoru, "Görsel klasörü")
    ]
    
    for dosya_yolu, aciklama in kontrol_dosyalari:
        if not os.path.exists(dosya_yolu):
            print(f"❌ KRITIK HATA: {aciklama} bulunamadı: {dosya_yolu}")
            sys.exit(1)
    
    # Çıktı klasörü hazırlığı
    cikti_klasoru = os.path.dirname(cikti_video)
    if cikti_klasoru and not os.path.exists(cikti_klasoru):
        try:
            os.makedirs(cikti_klasoru, exist_ok=True)
        except Exception as e:
            print(f"❌ KRITIK HATA: Çıktı klasörü oluşturulamadı: {e}")
            sys.exit(1)
    
    try:
        print("🎞️ MÜKEMMEL KALİTE KURGU MODÜLÜ BAŞLADI")
        print("=" * 60)
        print("🔍 Kapsamlı kalite kontrol sistemi aktif")
        print("⚠️ En ufak hata durumunda işlem durdurulacak")
        print("🎯 TÜM VİDEOLAR 16:9 FORMATINDA GARANTİLİ")
        print("🎭 İÇ EFEKTLER VE GEÇİŞ EFEKTLERİ AKTİF")
        print("🔧 GEÇİŞ EFEKTLERİ OFFSET DÜZELTME UYGULANMIŞ")
        print("=" * 60)
        
        kurgu_op = Kurgu(proje_json, ses_klasoru, gorsel_klasoru, cikti_video)
        kurgu_op.calistir()
        
        print("\n🎬 Sonraki adım için komut:")
        print(f"python moduller/youtube_uploader.py \"{cikti_video}\" \"{proje_json}\"")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu.")
        if 'kurgu_op' in locals():
            kurgu_op.temizlik_yap()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Beklenmeyen sistem hatası: {e}")
        if 'kurgu_op' in locals():
            kurgu_op.temizlik_yap()
        sys.exit(1)
