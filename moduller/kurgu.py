# kurgu.py

import os
import sys
import json
import random
import ffmpeg
from mutagen.wave import WAVE

class Kurgu:
    def __init__(self, proje_json_yolu, ses_klasoru, gorsel_klasoru, cikti_yolu):
        self.proje = self.json_oku(proje_json_yolu)
        self.ses_klasoru = ses_klasoru
        self.gorsel_klasoru = gorsel_klasoru
        self.cikti_yolu = cikti_yolu
        self.gecici_klasor = os.path.join(os.path.dirname(cikti_yolu), "gecici_klipler")
        os.makedirs(self.gecici_klasor, exist_ok=True)
    
    def json_oku(self, dosya_yolu):
        print(f"📖 Proje dosyası okunuyor: {dosya_yolu}")
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            return json.load(f)

    def ses_suresi_al(self, dosya_yolu):
        """WAV dosyasının süresini saniye olarak döndürür."""
        try:
            audio = WAVE(dosya_yolu)
            return audio.info.length
        except Exception as e:
            print(f"⚠️ Ses süresi okuma hatası: {dosya_yolu} - {e}")
            return 2 # Hata durumunda varsayılan süre

    def sessiz_klip_olustur(self, segment_bilgisi, ses_suresi, gecis_payi):
        """Her segment için animasyonlu, sessiz bir klip oluşturur."""
        gorsel_yolu = os.path.join(self.gorsel_klasoru, f"{segment_bilgisi['id']}.png")
        klip_suresi = ses_suresi + gecis_payi
        cikti_klip_yolu = os.path.join(self.gecici_klasor, f"{segment_bilgisi['id']}.mp4")

        if not os.path.exists(gorsel_yolu):
            print(f"❌ Görsel bulunamadı: {gorsel_yolu}. Bu segment atlanıyor.")
            return None

        print(f"  🎬 Klip oluşturuluyor: {os.path.basename(cikti_klip_yolu)} ({klip_suresi:.2f}s)")

        stream = ffmpeg.input(gorsel_yolu, loop=1, t=klip_suresi, framerate=30)
        
        # Animasyon (iç efekt) uygulama
        efekt = segment_bilgisi['efekt']
        if efekt['tip'] == 'zoom_in':
            stream = ffmpeg.filter(stream, 'zoompan', z='min(zoom+0.0010,1.5)', d=klip_suresi*30, s='1920x1080')
        elif efekt['tip'] == 'pan':
            # Bu kısım daha karmaşık ve özel bir mantık gerektirir. Şimdilik sabit bırakıldı.
            pass

        stream = ffmpeg.output(stream, cikti_klip_yolu, pix_fmt='yuv420p')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        return cikti_klip_yolu

    def calistir(self):
        # 1. Tüm segment bilgilerini ve ses sürelerini topla
        segmentler = []
        for bolum in self.proje['hikaye_yapisi'].values():
            for paragraf in bolum['paragraflar']:
                for s in paragraf['segmentler']:
                    segment_id = f"{bolum['bolum_kisaltmasi']}-{paragraf['paragraf_numarasi']}-{s['segment_numarasi']}"
                    ses_yolu = os.path.join(self.ses_klasoru, f"{segment_id}.wav")
                    segmentler.append({
                        "id": segment_id,
                        "sure": self.ses_suresi_al(ses_yolu),
                        "efekt": s['ic_efekt'],
                        "gecis": s['gecis_efekti']
                    })

        # 2. Sessiz klipleri oluştur
        klip_yollari = []
        for i, s_bilgi in enumerate(segmentler):
            gecis_payi = 1.0 if i < len(segmentler) - 1 else 0.0 # Son klip hariç 1sn ekle
            klip_yolu = self.sessiz_klip_olustur(s_bilgi, s_bilgi['sure'], gecis_payi)
            if klip_yolu:
                klip_yollari.append(klip_yolu)
        
        # 3. Klipleri birleştir (Geçişlerle)
        print("🎥 Klipler birleştiriliyor (geçiş efektleriyle)...")
        # Bu kısım ffmpeg-python ile oldukça karmaşıktır.
        # Basit bir birleştirme (concat) yapılıyor. Geçiş efektleri daha sonra eklenebilir.
        gecici_liste_dosyasi = os.path.join(self.gecici_klasor, "liste.txt")
        with open(gecici_liste_dosyasi, "w") as f:
            for klip in klip_yollari:
                f.write(f"file '{os.path.abspath(klip)}'\n")

        final_sessiz_video = os.path.join(self.gecici_klasor, "final_sessiz.mp4")
        (
            ffmpeg
            .input(gecici_liste_dosyasi, format='concat', safe=0)
            .output(final_sessiz_video, c='copy')
            .run(overwrite_output=True, quiet=True)
        )

        # 4. Müzik kuşağını hazırla
        print("🎵 Arka plan müziği hazırlanıyor...")
        muzik_klasoru = "muzikler"
        muzik_dosyalari = [os.path.join(muzik_klasoru, f) for f in os.listdir(muzik_klasoru)]
        secilen_muzik = random.choice(muzik_dosyalari)
        
        video_suresi = sum(s['sure'] for s in segmentler) + len(segmentler) - 1
        
        muzik_stream = (
            ffmpeg
            .input(secilen_muzik, stream_loop=-1)
            .filter('atrim', duration=video_suresi)
        )

        # 5. Ses kuşağını hazırla ve miksle
        print("🎙️ Anlatım sesleri ve müzik miksleniyor...")
        anlatim_ses_yollari = [ffmpeg.input(os.path.join(self.ses_klasoru, f"{s['id']}.wav")) for s in segmentler]
        birlestirilmis_anlatim = ffmpeg.concat(*anlatim_ses_yollari, v=0, a=1)

        mikslenmis_ses = ffmpeg.filter([birlestirilmis_anlatim, muzik_stream], 'amix', inputs=2, duration='first', weights="1 0.2")

        # 6. Final montaj ve sessizlik ekleme
        print("🎞️ Final montaj yapılıyor...")
        final_stream = ffmpeg.input(final_sessiz_video)
        
        (
            ffmpeg
            .concat(final_stream, mikslenmis_ses, v=1, a=1)
            .output(self.cikti_yolu)
            .run(overwrite_output=True, quiet=True)
        )

        # Not: Başa ve sona sessizlik ekleme bu temel yapıda atlanmıştır, 
        # daha karmaşık bir filtre zinciri gerektirir.

        print(f"✅ KURGU TAMAMLANDI! Video kaydedildi: {self.cikti_yolu}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Kullanım: python kurgu.py [proje.json] [ses_klasoru] [gorsel_klasoru] [cikti_video.mp4]")
        sys.exit(1)
    
    kurgu_op = Kurgu(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    kurgu_op.calistir()
