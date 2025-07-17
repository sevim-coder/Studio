# NOTLAR:
# 1. BU SCRIPT'İ KULLANMADAN ÖNCE GEREKLİ KÜTÜPHANELERİ YÜKLEYİN:
#    pip install google-genai pydantic
#
# 2. GEMINI_API_KEY'İNİZİ BİR ORTAM DEĞİŞKENİ OLARAK AYARLAYIN:
#    - Windows: set GEMINI_API_KEY=senin_api_anahtarin
#    - macOS/Linux: export GEMINI_API_KEY=senin_api_anahtarin
#
# 3. KULLANIM ŞEKLİ (Terminal veya Komut İstemi üzerinden):
#    python yonetmen.py senarist_txt_dosyasi.txt cikti_json_dosyasi.json
#
# 4. Bu script, senaristin yazdığı hikaye metnini alıp yapay zekaya gönderir ve ondan,
#    karmaşık JSON yapısına uygun bir proje dosyası oluşturmasını ister.

import os
import json
import argparse
from typing import List
from google import genai
from pydantic import BaseModel

# --- JSON ŞEMASI TANIMLAMALARI (PYDANTIC MODELLERİ) ---

class IcEfekt(BaseModel):
    tip: str
    yon: str
    hiz: str

class Segment(BaseModel):
    segment_numarasi: str
    metin: str
    gorsel_prompt: str
    tts_prompt: str
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
    """Yapay zekadan istenecek olan en üst seviye JSON yapısı."""
    ffmpeg_ayarlari: FFmpegAyarlari
    youtube_bilgileri: YoutubeBilgileri
    hikaye_yapisi: HikayeYapisi

# --- ANA SCRIPT FONKSİYONLARI ---

def dosya_yolu_analiz_et(dosya_yolu: str):
    """
    Dosya yolunu analiz ederek kanal bilgisini çıkarır
    Örnek: studio-v3/kanallar/Ilham_Perisi/Kadin_sagligi-16-07-25/Kadin.txt
    """
    yol_parcalari = dosya_yolu.split('/')
    
    if len(yol_parcalari) >= 4 and 'kanallar' in yol_parcalari:
        kanal_index = yol_parcalari.index('kanallar')
        if kanal_index + 1 < len(yol_parcalari):
            kanal_slug = yol_parcalari[kanal_index + 1]
            
            # Slug'dan kanal adını çıkar
            kanal_map = {
                "Ilham_Perisi": "İlham Perisi",
                "Perspektif": "Perspektif", 
                "Nolmus_Cocuk": "Nolmuş Çocuk",
                "Sahne_ve_Sanat": "Sahne ve Sanat",
                "Techsen": "Techsen"
            }
            
            return kanal_map.get(kanal_slug, kanal_slug.replace('_', ' '))
    
    return None

def dosya_oku(dosya_yolu: str) -> str:
    """Verilen yoldaki metin dosyasını okur."""
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Hata: '{dosya_yolu}' dosyası bulunamadı.")
        exit()
    except Exception as e:
        print(f"Hata: Dosya okunurken bir problem oluştu: {e}")
        exit()

def json_olustur(hikaye_metni: str, dosya_yolu: str) -> str:
    """Hikaye metnini alıp Google AI ile JSON oluşturur."""
    print("Yapay zeka ile iletişime geçiliyor...")

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Hata: GEMINI_API_KEY ortam değişkeni bulunamadı.")
            print("Lütfen API anahtarınızı ayarlayın.")
            exit()
        
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Hata: Google AI istemcisi başlatılamadı: {e}")
        exit()

    # Dosya yolundan kanal bilgisini çıkar
    kanal_adi = dosya_yolu_analiz_et(dosya_yolu)
    kanal_bilgisi = f"Bu metin '{kanal_adi}' kanalı için yazılmıştır." if kanal_adi else ""

    # Mevcut ses seçenekleri ve kanallar
    ses_secenekleri = """
    SES SEÇENEKLERİ:
    'Aoede': 'Breezy and natural, female',
    'Kore': 'Firm and confident, female',
    'Leda': 'Youthful and energetic, female',
    'Zephyr': 'Bright and cheerful, female',
    'Autonoe': 'Bright and optimistic, female',
    'Callirhoe': 'Easy-going and relaxed, female',
    'Despina': 'Smooth and flowing, female',
    'Erinome': 'Clear and precise, female',
    'Gacrux': 'Mature and experienced, female',
    'Laomedeia': 'Upbeat and lively, female',
    'Sulafat': 'Warm and welcoming, female',
    'Vindemiatrix': 'Gentle and kind, female',
    'Achernar': 'Soft and gentle, female',
    'Puck': 'Upbeat and energetic, male (default)',
    'Charon': 'Informative and clear, male',
    'Fenrir': 'Excitable and dynamic, male',
    'Orus': 'Firm and decisive, male',
    'Achird': 'Friendly and approachable, male',
    'Algenib': 'Gravelly texture, male',
    'Algieba': 'Smooth and pleasant, male',
    'Alnilam': 'Firm and strong, male',
    'Enceladus': 'Breathy and soft, male',
    'Iapetus': 'Clear and articulate, male',
    'Rasalgethi': 'Informative and professional, male',
    'Sadachbia': 'Lively and animated, male',
    'Sadaltager': 'Knowledgeable and authoritative, male',
    'Schedar': 'Even and balanced, male',
    'Umbriel': 'Easy-going and calm, male',
    'Zubenelgenubi': 'Casual and conversational, male'
    """

    kanal_secenekleri = """
    KANAL SEÇENEKLERİ:
    - İlham Perisi: Kadınlara özel ilham verici, motivasyonel, kişisel gelişim içerikleri ve makyaj moda dekorasyon
    - Perspektif: Analitik, düşündürücü ve farklı bakış açıları sunan belgesel tadından eğitici içerikler
    - Nolmuş Çocuk: Eğlenceli, hafif Çocuk kanalı
    - Sahne ve Sanat: Sanat, kültür, sinema tiyatro, opera ve bunlarla ilgi içerikler
    - Techsen: Teknoloji, bilim ve modern konular, AI'da son gelişmeler
    """

    tts_prompt_ornekleri = """
    TTS_PROMPT ÖRNEKLERİ:
    - Samimi konuşma: "Say in warm and intimate voice"
    - Enerjik anlatım: "Say in energetic and enthusiastic tone"
    - Sakin açıklama: "Say in calm and soothing voice"
    - Gizemli atmosfer: "Say in mysterious whisper"
    - Güçlü mesaj: "Say in confident and strong voice"
    - Neşeli anlatım: "Say in cheerful and bright tone"
    - Heyecanlı paylaşım: "Say in excited giggle"
    - Düşünceli ton: "Say in thoughtful and gentle voice"
    - Dramatik vurgu: "Say in dramatic and intense tone"
    - Rahatlatıcı ses: "Say in soft and comforting whisper"
    """

    # Yapay zekaya ne yapması gerektiğini detaylıca anlatan prompt
    prompt = f"""
    Sen, metinden video üreten bir otomasyon için proje dosyası hazırlayan bir yönetmensin.
    Sana verilen aşağıdaki hikayeyi analiz et ve eksiksiz bir video projesi JSON dosyası oluştur.

    {kanal_bilgisi}

    {ses_secenekleri}

    {kanal_secenekleri}

    {tts_prompt_ornekleri}

    GÖREVLERİN:
    1.  Hikayeyi mantıksal olarak "giriş", "gelişme" ve "sonuç" bölümlerine ayır.
    2.  Her bölümü paragraflara, her paragrafı da kısa ve anlamlı segmentlere böl.
    3.  Her bir metin segmenti için, o sahneyi en iyi anlatan, sanatsal ve sinematik bir 'gorsel_prompt' oluştur.
    4.  Her segment için, metnin atmosferine uygun bir 'tts_prompt' belirle.
    5.  Her segmente hikayenin akışına uygun bir 'ic_efekt' (zoom, pan vb.) ve 'gecis_efekti' ata.
    6.  Hikayenin konusuna ve atmosferine en uygun KANALI seç (yukarıdaki listeden veya dosya yolundan çıkarılan kanal bilgisini kullan).
    7.  Seçtiğin kanal ve hikayenin temasiyla uyumlu olan SESLENDİRMEN'i seç (yukarıdaki listeden sadece ses ismini kullan, örn: 'Aoede').
    8.  Hikayenin geneline uygun bir YouTube 'baslik', 'aciklama' ve 'etiketler' oluştur.
    9.  Tüm bu bilgileri, sana verilen JSON şemasına harfiyen uyarak doldur. Boş alan bırakma.

    ÖNEMLİ TTS_PROMPT KURALLARI:
    - 'tts_prompt' alanı mutlaka "Say in [tone/style] [voice_type]" formatında olmalıdır
    - Örnekler: 
      * "Say in warm and intimate voice"
      * "Say in energetic and cheerful tone"
      * "Say in mysterious whisper"
      * "Say in confident and strong voice"
      * "Say in gentle and soothing tone"
      * "Say in excited giggle"
    - Sadece İngilizce kullan
    - Ses tipi olarak: voice, tone, whisper, giggle, shout gibi çeşitliliği kullan
    - 'tts_prompt' alanını anlatımın akışkanlığını bozmamak adına çok nadir kullan, çoğunlukla boş bırak
    - Sadece hikayenin ilgili segmentindeki metinde gerçekten bir duygu zıplaması, ton değişikliği veya özel vurgu gerekiyorsa kullan
    - Normal anlatım segmentlerinde tts_prompt'u boş ("") bırak

    DİĞER ÖNEMLİ KURALLAR:
    - 'seslendirmen' alanına sadece ses ismini yaz (örn: 'Aoede'), açıklamayı değil.
    - 'Kanal' alanına sadece kanal ismini yaz (örn: 'İlham Perisi'), açıklamayı değil.

    İŞLENECEK HİKAYE:
    ---
    {hikaye_metni}
    ---
    """

    print("İstek yapay zekaya gönderiliyor ve yanıt bekleniyor... (Bu işlem biraz sürebilir)")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": VideoProjesi,
            },
        )
        print("Yapay zekadan geçerli bir JSON yanıtı alındı.")
        return response.text
    except Exception as e:
        print(f"Hata: Yapay zeka ile iletişim sırasında bir sorun oluştu: {e}")
        exit()


def dosya_yaz(icerik: str, dosya_yolu: str):
    """Verilen içeriği belirtilen yola JSON dosyası olarak yazar."""
    try:
        # JSON'u daha okunaklı olması için formatlayarak yazıyoruz
        parsed_json = json.loads(icerik)
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=2)
        print(f"Başarılı! Proje dosyası '{dosya_yolu}' olarak kaydedildi.")
    except Exception as e:
        print(f"Hata: JSON dosyası yazılırken bir problem oluştu: {e}")
        exit()


if __name__ == "__main__":
    # Komut satırı argümanlarını almak için parser oluşturuyoruz
    parser = argparse.ArgumentParser(description="Senaristin yazdığı hikaye dosyasından otomatik video projesi JSON'u oluşturan yönetmen script'i.")
    parser.add_argument("girdi_dosyasi", help="Senaristin oluşturduğu .txt dosyasının yolu.")
    parser.add_argument("cikti_dosyasi", help="Oluşturulacak .json proje dosyasının yolu.")
    args = parser.parse_args()

    # Adım 1: Senaristin hikaye dosyasını oku
    hikaye_icerigi = dosya_oku(args.girdi_dosyasi)

    # Adım 2: Yapay zeka ile JSON içeriğini oluştur
    json_icerigi = json_olustur(hikaye_icerigi, args.girdi_dosyasi)

    # Adım 3: Oluşturulan JSON'u dosyaya yaz
    dosya_yaz(json_icerigi, args.cikti_dosyasi)