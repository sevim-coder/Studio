from google import genai
from google.genai import types # EKLENDİ: İstenen yapı için gerekli modül.
import os
from datetime import datetime
import re
import hashlib
import json

class Senarist:
    def __init__(self):
        print("🎭 Senarist başlatılıyor...")
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not found")
        
        print("🔑 API anahtarı doğrulandı...")
        
        # DEĞİŞTİRİLDİ: Sizin belirttiğiniz en güncel yapıya uygun olarak 'genai.Client' kullanımına geri dönüldü.
        self.client = genai.Client(api_key=api_key)
        print("🤖 AI istemcisi hazır...")
        
        self.kanal_talimatlari = {
            "İlham Perisi": "Sen kadınlara ilham veren, güçlendiren konuları sıcak ve samimi bir üslupla anlatan bir rehbersin.",
            "Perspektif": "Sen olayları objektif bir şekilde, derinlemesine analiz eden bir tarihçi ve düşünürsün.",
            "Nolmuş Çocuk": "Sen eğlenceli, hafif ve gündelik konuları neşeli bir dille anlatan çocuklar ile çok iyi anlaşan bilge birisin",
            "Sahne ve Sanat": "Sen sanat ve kültür konularını etkileyici bir şekilde anlatan bir sanat tarihçisi, sinema eleştirmeni, opera ve tiyatro izleyicisisin.",
            "Techsen": "Sen teknolojik gelişmeleri anlaşılır ve net bir şekilde açıklayan bir teknoloji uzmanısın."
        }
        print("✅ Senarist hazır!")
    
    def slug_olustur(self, metin):
        turkce_karakterler = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
        }
        for tr_char, en_char in turkce_karakterler.items():
            metin = metin.replace(tr_char, en_char)
        metin = re.sub(r'[^\w\s-]', '', metin)
        metin = re.sub(r'[-\s]+', '_', metin)
        return metin.strip('_')

    def proje_kok_klasorunu_bul(self):
        mevcut_klasor = os.path.dirname(os.path.abspath(__file__))
        if mevcut_klasor.endswith('moduller'):
            kok_klasor = os.path.dirname(mevcut_klasor)
        else:
            kok_klasor = mevcut_klasor
        return kok_klasor

    def hash_olustur(self, kanal_adi, konu, harf_sayisi):
        veri = f"{kanal_adi}|{konu}|{harf_sayisi}"
        return hashlib.md5(veri.encode('utf-8')).hexdigest()

    def cache_dosya_yolu(self, hash_kodu):
        kok_klasor = self.proje_kok_klasorunu_bul()
        cache_klasor = os.path.join(kok_klasor, ".cache")
        os.makedirs(cache_klasor, exist_ok=True)
        return os.path.join(cache_klasor, f"{hash_kodu}.json")

    def cache_kontrol(self, kanal_adi, konu, harf_sayisi):
        hash_kodu = self.hash_olustur(kanal_adi, konu, harf_sayisi)
        cache_dosyasi = self.cache_dosya_yolu(hash_kodu)
        if os.path.exists(cache_dosyasi):
            print("📋 Daha önce üretilmiş hikaye bulundu, kontrol ediliyor...")
            try:
                with open(cache_dosyasi, 'r', encoding='utf-8') as f:
                    cache_verisi = json.load(f)
                if os.path.exists(cache_verisi['dosya_yolu']):
                    with open(cache_verisi['dosya_yolu'], 'r', encoding='utf-8') as f:
                        mevcut_icerik = f.read()
                    if mevcut_icerik == cache_verisi['senaryo_metni']:
                        print("✅ Mevcut hikaye değişmemiş, kullanılıyor...")
                        return cache_verisi
                    else:
                        print("⚠️ Hikaye dosyası değiştirilmiş, yeniden üretiliyor...")
                else:
                    print("⚠️ Hikaye dosyası silinmiş, yeniden üretiliyor...")
            except Exception as e:
                print(f"⚠️ Cache okuma hatası: {e}, yeniden üretiliyor...")
        return None

    def cache_kaydet(self, kanal_adi, konu, harf_sayisi, sonuc):
        hash_kodu = self.hash_olustur(kanal_adi, konu, harf_sayisi)
        cache_dosyasi = self.cache_dosya_yolu(hash_kodu)
        cache_verisi = {
            "hash": hash_kodu,
            "kanal_adi": kanal_adi,
            "konu": konu,
            "harf_sayisi": harf_sayisi,
            "tarih": datetime.now().isoformat(),
            **sonuc
        }
        try:
            with open(cache_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(cache_verisi, f, ensure_ascii=False, indent=2)
            print("💾 Hikaye cache'e kaydedildi")
        except Exception as e:
            print(f"⚠️ Cache kaydetme hatası: {e}")

    def klasor_olustur(self, kanal_adi, konu):
        print(f"📁 Klasör yapısı oluşturuluyor...")
        bugun = datetime.now().strftime("%d-%m-%y")
        konu_ilk_kelime = konu.split()[0]
        konu_slug = self.slug_olustur(konu_ilk_kelime)
        kanal_slug = self.slug_olustur(kanal_adi)
        kok_klasor = self.proje_kok_klasorunu_bul()
        klasor_yolu = os.path.join(kok_klasor, "kanallar", kanal_slug, f"{konu_slug}-{bugun}")
        os.makedirs(klasor_yolu, exist_ok=True)
        print(f"✅ Klasör oluşturuldu: {klasor_yolu}")
        return klasor_yolu

    def harf_sayisi_hesapla(self, metin):
        harfler = re.findall(r'[a-zA-ZçğıöşüÇĞIİÖŞÜ]', metin)
        return len(harfler)
    
    def senaryo_uret(self, kanal_adi, konu, harf_sayisi):
        print(f"🎬 Senaryo üretimi başlıyor...")
        print(f"📺 Kanal: {kanal_adi}")
        print(f"📝 Konu: {konu}")
        print(f"📏 Hedef harf sayısı: {harf_sayisi}")
        
        cache_sonuc = self.cache_kontrol(kanal_adi, konu, harf_sayisi)
        if cache_sonuc:
            return cache_sonuc
        
        kanal_talimati = self.kanal_talimatlari.get(kanal_adi, "Sen bir içerik üreticisisin.")
        print(f"🎯 Kanal talimatı belirlendi...")
        
        system_instruction = f"""{kanal_talimati}

Verilen konu hakkında yaklaşık {harf_sayisi} harf uzunluğunda eksiksiz bir youtube video anlatısı yaz.
Sana verilen konuyu iyi düşün, Youtube içerikleri için yazacaksın.
Sana verilen konunun uzmanısın. Bilgesin, eğlencelisin, sorgulayansın, sorgulatansın, düşünensin, düşündürensin.
Kısaca sen hitabet yeteneği harika olan usta bir anlatıcısın.
Yazacağın anlatı konuya veya kanala göre, Youtube istatistiklerine göre en çok ilgi gören tarzda olacak.

ZORUNLU KURALLAR:
1. Anlatıyı mutlaka tamamla - yarım bırakma
2. Edebiyat kurallarına uygun yaz: Giriş, Gelişme, Sonuç
3. Giriş bölümünde 
4. Gelişme bölümünde, 
5. Sonuç bölümünde,  
6. Bazen Kelime oyunları(pun), eş anlamlı kelimeler(double entendre) ve kültürel referanslarla küçük şakalar yapabilirsin
3. Uzun metinlerde kendi içinde bir bütün olan ve kendinden sonra geleceklerden farkı açık olan kısımları paragraflar halinde böl, paragraf başlarında girinti koy
4. Sadece anlatı metnini yaz - başka hiçbir şey yazma
5. Emoji, özel karakter, yorum kullanma
6. Metni, nokta soru işareti ünlem işareti gibi cümle bitiren noktalama işaretleri ile bitir. Yani orta yerde bırakma.
7

YAPISAL DÜZEN:
- Giriş: Etkili ve dikkat çekici bir girişle başla. Anlatacaklarının bir önizlemesi olsun, metnin öne çıkanları hakkında ufak ipuçları vererek ilgiyi kendine çek
- Gelişme: Ana konunun detaylı işlenmesi; daha önce kendi etrafında topladığın seyirciyi sıkmadan konuyu irdele. Kilit noktaları, öne çıkanları dikkat çekici bir tonla yaz.
- Sonuç: Anlattığın konuyu toparla sonuca var, gerekirse izleyiciyi düşündürecek yarım kalmış sorular sor. Metni tatmin edici şekilde bitir. 

Sadece anlatı metni döndür. Başka hiçbir açıklama yapma."""

        print(f"🤖 AI'ye düzeltilmiş talimatlarla istek gönderiliyor...")
        
        try:
            # --- DEĞİŞİKLİK ---
            # API isteği, sağladığınız en güncel yapıya göre güncellendi.
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction),
                contents=f"Konu: {konu}"
            )
            senaryo_metni = response.text.strip()
            print("✅ AI'den senaryo başarıyla alındı!")
                
        except Exception as e:
            print(f"❌ AI isteği sırasında bir hata oluştu: {e}")
            raise
        
        print(f"📊 Son senaryo uzunluğu: {len(senaryo_metni)} karakter")
        print(f"📊 Son harf sayısı: {self.harf_sayisi_hesapla(senaryo_metni)}")
        
        klasor_yolu = self.klasor_olustur(kanal_adi, konu)
        konu_slug = self.slug_olustur(konu.split()[0])
        dosya_adi = f"{konu_slug}.txt"
        dosya_yolu = os.path.join(klasor_yolu, dosya_adi)
        
        print(f"💾 Senaryo dosyaya kaydediliyor...")
        
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            f.write(senaryo_metni)
        
        print(f"✅ Senaryo başarıyla oluşturuldu: {dosya_yolu}")
        
        sonuc = {
            "senaryo_metni": senaryo_metni,
            "dosya_yolu": dosya_yolu,
            "klasor_yolu": klasor_yolu,
            "kanal_adi": kanal_adi,
            "konu": konu
        }
        
        self.cache_kaydet(kanal_adi, konu, harf_sayisi, sonuc)
        
        return sonuc

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Belirtilen kanal, konu ve uzunlukta senaryo üreten senarist.")
    parser.add_argument("kanal_adi", help="Hedef kanal adı (İlham Perisi, Perspektif, vb.)")
    parser.add_argument("konu", help="Senaryo konusu")
    parser.add_argument("harf_sayisi", type=int, help="Hedef harf sayısı")
    args = parser.parse_args()
    
    try:
        print("🎭 SENARYO ÜRETİCİ BAŞLADI")
        print("=" * 50)
        
        senarist = Senarist()
        sonuc = senarist.senaryo_uret(args.kanal_adi, args.konu, args.harf_sayisi)
        
        print("\n" + "=" * 50)
        print("🎉 SENARYO ÜRETİMİ TAMAMLANDI!")
        print("=" * 50)
        print(f"📺 Kanal: {sonuc['kanal_adi']}")
        print(f"📝 Konu: {sonuc['konu']}")
        print(f"📁 Dosya konumu: {sonuc['dosya_yolu']}")
        print(f"📏 Metin uzunluğu: {len(sonuc['senaryo_metni'])} karakter")
        
        print("\n🎬 Sonraki adım için komut:")
        print(f"python moduller/yonetmen.py {sonuc['dosya_yolu']} {sonuc['klasor_yolu']}/proje.json")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Hata: {e}")
