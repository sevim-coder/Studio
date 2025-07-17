from google import genai
from google.genai import types
import os
from datetime import datetime
import unicodedata
import re

class Senarist:
    def __init__(self):
        # API anahtarını environment'tan al
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not found")
        
        self.client = genai.Client(api_key=api_key)
        
        # Güncellenmiş kanal başına özel sistem talimatları
        self.kanal_talimatlari = {
            "İlham Perisi": "Sen kadınlara ilham veren, güçlendiren konuları sıcak ve samimi bir üslupla anlatan bir rehbersin.",
            "Perspektif": "Sen olayları objektif bir şekilde, derinlemesine analiz eden bir tarihçi ve düşünürsün.",
            "Nolmuş Çocuk": "Sen eğlenceli, hafif ve gündelik konuları neşeli bir dille anlatan bir hikaye anlatıcısısın.",
            "Sahne ve Sanat": "Sen sanat ve kültür konularını etkileyici bir şekilde anlatan bir sanat tarihçisisin.",
            "Techsen": "Sen teknolojik gelişmeleri anlaşılır ve net bir şekilde açıklayan bir teknoloji uzmanısın."
        }
    
    def slug_olustur(self, metin):
        """
        Türkçe karakterleri ve özel karakterleri dosya sistemi uyumlu hale getirir
        """
        # Türkçe karakterleri dönüştür
        turkce_karakterler = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
        }
        
        for tr_char, en_char in turkce_karakterler.items():
            metin = metin.replace(tr_char, en_char)
        
        # Özel karakterleri temizle ve alt çizgi ile değiştir
        metin = re.sub(r'[^\w\s-]', '', metin)
        metin = re.sub(r'[-\s]+', '_', metin)
        
        return metin.strip('_')
    
    def proje_kok_klasorunu_bul(self):
        """
        Moduller klasörünün bir üst klasörünü (studio-v3) bulur
        """
        # Mevcut dosyanın bulunduğu klasörü al
        mevcut_klasor = os.path.dirname(os.path.abspath(__file__))
        
        # Eğer moduller klasöründeyse, bir üst klasöre çık
        if mevcut_klasor.endswith('moduller'):
            kok_klasor = os.path.dirname(mevcut_klasor)
        else:
            # Eğer moduller klasöründe değilse, mevcut klasörü kullan
            kok_klasor = mevcut_klasor
        
        return kok_klasor
    
    def klasor_olustur(self, kanal_adi, konu):
        """
        Proje kök klasörü altında klasör yapısını oluşturur
        kanallar/Kanal_Adi/Konu_ilk_kelime-DD-MM-YY
        """
        # Bugünün tarihini al (DD-MM-YY formatında)
        bugun = datetime.now().strftime("%d-%m-%y")
        
        # Konunun ilk kelimesini al
        konu_ilk_kelime = konu.split()[0]
        konu_slug = self.slug_olustur(konu_ilk_kelime)
        
        # Kanal adını slug haline getir
        kanal_slug = self.slug_olustur(kanal_adi)
        
        # Proje kök klasörünü bul
        kok_klasor = self.proje_kok_klasorunu_bul()
        
        # Klasör yolunu oluştur: [proje_kök]/kanallar/Kanal_Adi/Konu_ilk_kelime-DD-MM-YY
        klasor_yolu = os.path.join(kok_klasor, "kanallar", kanal_slug, f"{konu_slug}-{bugun}")
        
        # Klasörü oluştur
        os.makedirs(klasor_yolu, exist_ok=True)
        
        print(f"Klasör oluşturuldu: {klasor_yolu}")
        
        return klasor_yolu
    
    def senaryo_uret(self, kanal_adi, konu, harf_sayisi):
        """
        Kanal adı, konu ve harf sayısı alır, 
        Giriş-Gelişme-Sonuç düzeninde anlatım metni üretir.
        Oluşturulan metni uygun klasöre kaydeder.
        """
        
        kanal_talimati = self.kanal_talimatlari.get(kanal_adi, "Sen bir içerik üreticisisin.")
        
        system_instruction = f"""{kanal_talimati}

Verilen konu hakkında tam olarak {harf_sayisi} harf içeren anlatım metni yaz.

ÖNEMLİ: Harf sayısı sadece alfabetik karakterleri (A-Z, a-z, Türkçe harfler) kapsar. Boşluk, noktalama işaretleri sayılmaz.

YAPISAL KURALLAR:
- Giriş, Gelişme, Sonuç düzenine sadık kal
- Giriş: Konuya dikkat çekici bir başlangıç yap (%20-25)
- Gelişme: Ana konuyu detaylı şekilde işle (%50-60)
- Sonuç: Özetleyici ve etkileyici bir bitiş yap (%15-25)
- Her bölümü ayrı paragraflar halinde yaz
- Paragraflar arasında boş satır bırak

YAZIM KURALLARI:
- Sadece anlatım metnini yaz, başka hiçbir şey yazma
- "Senaryo oluşturuyorum" gibi yorumlar yapma  
- Görsel önerileri verme
- Seslendirme önerileri verme
- Sadece hikaye metnini yaz
- {kanal_adi} kanalının tonuna uygun yaz
- Hedef harf sayısı: {harf_sayisi}

ÇIKTI FORMATI:
- Yalnızca metin döndür
- Başlık ya da açıklama ekleme
- Düz metin formatında yaz"""

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            ),
            contents=f"Konu: {konu}"
        )
        
        senaryo_metni = response.text.strip()
        
        # Klasörü oluştur ve dosya yolunu al
        klasor_yolu = self.klasor_olustur(kanal_adi, konu)
        
        # Dosya adını oluştur
        konu_slug = self.slug_olustur(konu.split()[0])
        dosya_adi = f"{konu_slug}.txt"
        dosya_yolu = os.path.join(klasor_yolu, dosya_adi)
        
        # Dosyayı kaydet
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            f.write(senaryo_metni)
        
        print(f"Senaryo başarıyla oluşturuldu: {dosya_yolu}")
        
        return {
            "senaryo_metni": senaryo_metni,
            "dosya_yolu": dosya_yolu,
            "klasor_yolu": klasor_yolu,
            "kanal_adi": kanal_adi,
            "konu": konu
        }

# Kullanım örneği
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Belirtilen kanal, konu ve uzunlukta senaryo üreten senarist.")
    parser.add_argument("kanal_adi", help="Hedef kanal adı (İlham Perisi, Perspektif, vb.)")
    parser.add_argument("konu", help="Senaryo konusu")
    parser.add_argument("harf_sayisi", type=int, help="Hedef harf sayısı")
    args = parser.parse_args()
    
    try:
        senarist = Senarist()
        sonuc = senarist.senaryo_uret(args.kanal_adi, args.konu, args.harf_sayisi)
        
        print(f"\nSenaryo üretimi tamamlandı!")
        print(f"Kanal: {sonuc['kanal_adi']}")
        print(f"Konu: {sonuc['konu']}")
        print(f"Dosya konumu: {sonuc['dosya_yolu']}")
        print(f"Metin uzunluğu: {len(sonuc['senaryo_metni'])} karakter")
        
        # Yönetmen için bilgi
        print(f"\nYönetmen komutu:")
        print(f"python moduller/yonetmen.py {sonuc['dosya_yolu']} {sonuc['klasor_yolu']}/proje.json")
        
    except Exception as e:
        print(f"Hata: {e}")
