# yonetmen.py

import os
import json
import argparse
from typing import List
from google import genai
from pydantic import BaseModel
import sys

# --- JSON ŞEMASI TANIMLAMALARI (PYDANTIC MODELLERİ) ---

class IcEfekt(BaseModel):
    tip: str
    yon: str
    hiz: str

class Segment(BaseModel):
    segment_numarasi: str
    metin: str
    gorsel_prompt: str
    en_boy_orani: str
    ic_efekt: IcEfekt
    gecis_efekti: str

class Paragraf(BaseModel):
    paragraf_numarasi: str
    segmentler: List[Segment]

class Bolum(BaseModel):
    bolum_kisaltmasi: str
    paragraflar: List[Paragraf]

class HikayeYapisi(BaseModel):
    giris: Bolum
    gelisme: Bolum
    sonuc: Bolum

class VideoAyarlari(BaseModel):
    codec: str = "libx264"
    bitrate: str = "5000k"
    fps: str = "24"
    cozunurluk: str = "1920x1080"

class SesAyarlari(BaseModel):
    codec: str = "aac"
    bitrate: str = "192k"

class FFmpegAyarlari(BaseModel):
    cikti_dosyasi: str = "son_video.mp4"
    video_ayarlari: VideoAyarlari = VideoAyarlari()
    ses_ayarlari: SesAyarlari = SesAyarlari()

class YoutubeBilgileri(BaseModel):
    Kanal: str
    baslik: str
    aciklama: str
    seslendirmen: str
    muzikler: str
    etiketler: List[str]
    kategori: str = "Hikaye Anlatımı"
    gizlilik_durumu: str = "private"

class VideoProjesi(BaseModel):
    ffmpeg_ayarlari: FFmpegAyarlari
    youtube_bilgileri: YoutubeBilgileri
    hikaye_yapisi: HikayeYapisi

# --- ANA SCRIPT FONKSİYONLARI ---

def dosya_yolu_analiz_et(dosya_yolu: str):
    print(f"📂 Dosya yolu analiz ediliyor: {dosya_yolu}")
    yol_parcalari = dosya_yolu.replace('\\', '/').split('/')
    if len(yol_parcalari) >= 4 and 'kanallar' in yol_parcalari:
        kanal_index = yol_parcalari.index('kanallar')
        if kanal_index + 1 < len(yol_parcalari):
            kanal_slug = yol_parcalari[kanal_index + 1]
            kanal_map = {
                "Ilham_Perisi": "İlham Perisi", 
                "Perspektif": "Perspektif", 
                "Nolmus_Cocuk": "Nolmuş Çocuk", 
                "Sahne_ve_Sanat": "Sahne ve Sanat", 
                "Techsen": "Techsen"
            }
            kanal_adi = kanal_map.get(kanal_slug, kanal_slug.replace('_', ' '))
            print(f"📺 Tespit edilen kanal: {kanal_adi}")
            return kanal_adi
    print("⚠️ Kanal bilgisi tespit edilemedi")
    return "Genel"

def dosya_oku(dosya_yolu: str) -> str:
    print(f"📖 Dosya okunuyor: {dosya_yolu}")
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        print(f"✅ Dosya başarıyla okundu ({len(icerik)} karakter)")
        return icerik
    except FileNotFoundError:
        print(f"❌ HATA: '{dosya_yolu}' dosyası bulunamadı.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ HATA: Dosya okunurken bir problem oluştu: {e}")
        sys.exit(1)

def json_olustur(hikaye_metni: str, dosya_yolu: str) -> str:
    print("🎬 Yönetmen devreye giriyor...")
    print("🤖 Yapay zeka ile iletişime geçiliyor...")

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ HATA: GEMINI_API_KEY ortam değişkeni bulunamadı.")
            sys.exit(1)
        print("🔑 API anahtarı doğrulandı...")
        client = genai.Client(api_key=api_key)
        print("🤖 AI istemcisi hazır...")
    except Exception as e:
        print(f"❌ HATA: Google AI istemcisi başlatılamadı: {e}")
        sys.exit(1)

    kanal_adi = dosya_yolu_analiz_et(dosya_yolu)
    kanal_bilgisi = f"Bu metin '{kanal_adi}' kanalı için yazılmıştır." if kanal_adi else ""

    ses_secenekleri = """
    SES SEÇENEKLERİ:
    'Aoede': 'Breezy and natural, female', 'Kore': 'Firm and confident, female', 'Leda': 'Youthful and energetic, female', 'Zephyr': 'Bright and cheerful, female', 'Autonoe': 'Bright and optimistic, female', 'Callirhoe': 'Easy-going and relaxed, female', 'Despina': 'Smooth and flowing, female', 'Erinome': 'Clear and precise, female', 'Gacrux': 'Mature and experienced, female', 'Laomedeia': 'Upbeat and lively, female', 'Sulafat': 'Warm and welcoming, female', 'Vindemiatrix': 'Gentle and kind, female', 'Achernar': 'Soft and gentle, female',
    'Puck': 'Upbeat and energetic, male (default)', 'Charon': 'Informative and clear, male', 'Fenrir': 'Excitable and dynamic, male', 'Orus': 'Firm and decisive, male', 'Achird': 'Friendly and approachable, male', 'Algenib': 'Gravelly texture, male', 'Algieba': 'Smooth and pleasant, male', 'Alnilam': 'Firm and strong, male', 'Enceladus': 'Breathy and soft, male', 'Iapetus': 'Clear and articulate, male', 'Rasalgethi': 'Informative and professional, male', 'Sadachbia': 'Lively and animated, male', 'Sadaltager': 'Knowledgeable and authoritative, male', 'Schedar': 'Even and balanced, male', 'Umbriel': 'Easy-going and calm, male', 'Zubenelgenubi': 'Casual and conversational, male'
    """

    kanal_secenekleri = """
    KANAL SEÇENEKLERİ:
    - İlham Perisi, Perspektif, Nolmuş Çocuk, Sahne ve Sanat, Techsen
    """
    
    print("📝 AI talimatları hazırlanıyor...")
    
    prompt = f"""
    Sen, metinden video üreten bir otomasyon için proje dosyası hazırlayan bir yönetmensin.
    Sana verilen aşağıdaki hikayeyi analiz et ve eksiksiz bir video projesi JSON dosyası oluştur.

    {kanal_bilgisi}
    {ses_secenekleri}
    {kanal_secenekleri}

    GÖREVLERİN:
    1.  Hikaye metnini mantıksal olarak "giriş", "gelişme" ve "sonuç" bölümlerine ayır.
    2.  Her bölümü paragraflara, her paragrafı da kısa ve anlamlı segmentlere böl.
    3.  Her bir metin segmenti için, o sahneyi en iyi anlatan, sanatsal ve sinematik bir 'gorsel_prompt' oluştur.
    4.  Her segment için, sahnenin anlatımına en uygun 'en_boy_orani' belirle ('1:1', '4:3', '3:4', '16:9', '9:16' seçeneklerinden birini kullan).
    5.  Eğer metin, short video niteliği taşıyacak kadar çok kısa değilse, önceliğin '16:9' (yatay) olacak.
    6.  Bazen uzun videolarda bile resmin niteliğine göre diğer oranların kullanılması daha makbul olabilir (örn: karakter portresi için '9:16').
    7.  Her segmente hikayenin akışına uygun bir 'ic_efekt' ve 'gecis_efekti' ata.
    8.  Hikaye metninin konusuna ve atmosferine en uygun KANALI ve SESLENDİRMEN'i seç.
    9.  Hikayenin geneline uygun bir YouTube 'baslik', 'aciklama' ve 'etiketler' oluştur.
    10. Tüm bu bilgileri, sana verilen JSON şemasına harfiyen uyarak doldur.
    11. Her ne olursa olsun 99 segment maksimum sınır. Metni 99 segmentten daha fazla asla ayırmayacaksın.
    12. KRITIK: Herhangi bir hata olursa programı durduracak şekilde valid JSON oluştur.
    
    İŞLENECEK HİKAYE:
    ---
    {hikaye_metni}
    ---
    """
    
    print("🚀 AI'ye proje dosyası oluşturma talebi gönderiliyor...")
    print("⏳ Bu işlem biraz zaman alabilir, lütfen bekleyin...")
    print("📊 AI hikayeyi analiz ediyor ve JSON yapısını oluşturuyor...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": VideoProjesi,
            },
        )
        print("✅ AI'den geçerli bir JSON yanıtı alındı!")
        return response.text
    except Exception as e:
        print(f"❌ HATA: Yapay zeka ile iletişim sırasında bir sorun oluştu: {e}")
        sys.exit(1)

def dosya_yaz(icerik: str, dosya_yolu: str):
    print(f"💾 JSON dosyası kaydediliyor: {dosya_yolu}")
    try:
        parsed_json = json.loads(icerik)
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=2)
        print(f"✅ Proje dosyası başarıyla kaydedildi!")
    except json.JSONDecodeError as e:
        print(f"❌ HATA: Geçersiz JSON formatı: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ HATA: JSON dosyası yazılırken bir problem oluştu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Senaristin yazdığı hikaye dosyasından otomatik video projesi JSON'u oluşturan yönetmen script'i.")
    parser.add_argument("girdi_dosyasi", help="Senaristin oluşturduğu .txt dosyasının yolu.")
    parser.add_argument("cikti_dosyasi", help="Oluşturulacak .json proje dosyasının yolu.")
    args = parser.parse_args()

    try:
        print("🎬 YÖNETMEN ÇALIŞMAYA BAŞLADI")
        print("=" * 50)

        hikaye_icerigi = dosya_oku(args.girdi_dosyasi)
        json_icerigi = json_olustur(hikaye_icerigi, args.girdi_dosyasi)
        dosya_yaz(json_icerigi, args.cikti_dosyasi)

        print("\n" + "=" * 50)
        print("🎉 YÖNETMEN ÇALIŞMASINI TAMAMLADI!")
        print("=" * 50)
        print(f"📁 Proje dosyası: {args.cikti_dosyasi}")
        
        proje_klasoru = os.path.dirname(args.cikti_dosyasi)
        ses_cikti_klasoru = os.path.join(proje_klasoru, "sesler")
        gorsel_cikti_klasoru = os.path.join(proje_klasoru, "gorseller")
        
        print("\n🎙️ Sonraki adım için komutlar:")
        print(f"python moduller/seslendirmen.py \"{args.cikti_dosyasi}\" \"{ses_cikti_klasoru}\"")
        print(f"python moduller/gorsel_yonetmen.py \"{args.cikti_dosyasi}\" \"{gorsel_cikti_klasoru}\"")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        sys.exit(1)