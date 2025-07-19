import os
import sys
import json
import re
import hashlib
from datetime import datetime

# Path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from google import genai
from google.genai import types
import openai
import anthropic
from api_manager import get_api_manager, APIType

class MultiAPISenarist:
    def __init__(self):
        print("🎭 Multi-API Senarist başlatılıyor...")
        self.api_manager = get_api_manager()
        
        self.kanal_talimatlari = {
            "İlham Perisi": "Sen kadınlara ilham veren, güçlendiren konuları sıcak ve samimi bir üslupla anlatan bir rehbersin.",
            "Perspektif": "Sen olayları objektif bir şekilde, derinlemesine analiz eden bir tarihçi ve düşünürsün.",
            "Nolmuş Çocuk": "Sen eğlenceli, hafif ve gündelik konuları neşeli bir dille anlatan çocuklar ile çok iyi anlaşan bilge birisin",
            "Sahne ve Sanat": "Sen sanat ve kültür konularını etkileyici bir şekilde anlatan bir sanat tarihçisi, sinema eleştirmeni, opera ve tiyatro izleyicisisin.",
            "Techsen": "Sen teknolojik gelişmeleri anlaşılır ve net bir şekilde açıklayan bir teknoloji uzmanısın."
        }
        print("✅ Multi-API Senarist hazır!")
    
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

    def text_request_wrapper(self, system_instruction, konu):
        """Multi-API text generation wrapper"""
        
        def gemini_request(client, config):
            response = client.models.generate_content(
                model=config['model_text'],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                ),
                contents=f"Konu: {konu}"
            )
            return response.text.strip()
        
        def openai_request(client, config):
            response = client.chat.completions.create(
                model=config['model_text'],
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Konu: {konu}"}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            return response.choices[0].message.content.strip()
        
        def anthropic_request(client, config):
            response = client.messages.create(
                model=config['model_text'],
                system=system_instruction,
                messages=[{"role": "user", "content": f"Konu: {konu}"}],
                max_tokens=4000
            )
            return response.content[0].text.strip()
        
        # Provider'a göre doğru request fonksiyonunu seç
        def unified_request(client, config):
            provider = config.get('provider_type', 'gemini')
            
            if hasattr(client, 'models') and hasattr(client.models, 'generate_content'):  # Gemini
                return gemini_request(client, config)
            elif hasattr(client, 'chat') and hasattr(client.chat, 'completions'):  # OpenAI
                return openai_request(client, config)
            elif hasattr(client, 'messages') and hasattr(client.messages, 'create'):  # Anthropic
                return anthropic_request(client, config)
            else:
                raise Exception(f"Bilinmeyen API client tipi: {type(client)}")
        
        return self.api_manager.make_request(APIType.TEXT, unified_request)

    def senaryo_uret_ile_yol(self, kanal_adi, konu, harf_sayisi, cikti_yolu=None):
        """Multi-API ile senaryo üretir ve belirtilen yola kaydeder."""
        print(f"🎬 Multi-API Senaryo üretimi başlıyor...")
        print(f"📺 Kanal: {kanal_adi}")
        print(f"📝 Konu: {konu}")
        print(f"📏 Hedef harf sayısı: {harf_sayisi}")
        
        if cikti_yolu:
            print(f"📁 Özel çıktı yolu: {cikti_yolu}")
        
        # Cache kontrolü sadece özel yol belirtilmemişse
        cache_sonuc = None
        if not cikti_yolu:
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
3. Giriş bölümünde konuyu tanıt ve ilgi çek
4. Gelişme bölümünde ana konuyu detaylandır
5. Sonuç bölümünde özetle ve düşündürücü sonla bitir
6. Bazen Kelime oyunları(pun), eş anlamlı kelimeler(double entendre) ve kültürel referanslarla küçük şakalar yapabilirsin
7. Uzun metinlerde kendi içinde bir bütün olan ve kendinden sonra geleceklerden farkı açık olan kısımları paragraflar halinde böl, paragraf başlarında girinti koy
8. Sadece anlatı metnini yaz - başka hiçbir şey yazma
9. Emoji, özel karakter, yorum kullanma
10. Metni, nokta soru işareti ünlem işareti gibi cümle bitiren noktalama işaretleri ile bitir. Yani orta yerde bırakma.

YAPISAL DÜZEN:
- Giriş: Etkili ve dikkat çekici bir girişle başla. Anlatacaklarının bir önizlemesi olsun, metnin öne çıkanları hakkında ufak ipuçları vererek ilgiyi kendine çek
- Gelişme: Ana konunun detaylı işlenmesi; daha önce kendi etrafında topladığın seyirciyi sıkmadan konuyu irdele. Kilit noktaları, öne çıkanları dikkat çekici bir tonla yaz.
- Sonuç: Anlattığın konuyu toparla sonuca var, gerekirse izleyiciyi düşündürecek yarım kalmış sorular sor. Metni tatmin edici şekilde bitir. 

Sadece anlatı metni döndür. Başka hiçbir açıklama yapma."""

        print(f"🤖 Multi-API sisteme düzeltilmiş talimatlarla istek gönderiliyor...")
        
        try:
            senaryo_metni = self.text_request_wrapper(system_instruction, konu)
            print("✅ Multi-API'den senaryo başarıyla alındı!")
                
        except Exception as e:
            print(f"❌ Tüm API'ler başarısız oldu: {e}")
            sys.exit(1)
        
        print(f"📊 Son senaryo uzunluğu: {len(senaryo_metni)} karakter")
        print(f"📊 Son harf sayısı: {self.harf_sayisi_hesapla(senaryo_metni)}")
        
        # Dosya yolu belirleme
        if cikti_yolu:
            dosya_yolu = cikti_yolu
            klasor_yolu = os.path.dirname(dosya_yolu)
            os.makedirs(klasor_yolu, exist_ok=True)
        else:
            klasor_yolu = self.klasor_olustur(kanal_adi, konu)
            dosya_adi = "senaryo.txt"
            dosya_yolu = os.path.join(klasor_yolu, dosya_adi)
        
        print(f"💾 Senaryo dosyaya kaydediliyor...")
        
        try:
            with open(dosya_yolu, 'w', encoding='utf-8') as f:
                f.write(senaryo_metni)
            print(f"✅ Senaryo başarıyla oluşturuldu: {dosya_yolu}")
        except Exception as e:
            print(f"❌ Dosya yazma hatası: {e}")
            sys.exit(1)
        
        sonuc = {
            "senaryo_metni": senaryo_metni,
            "dosya_yolu": dosya_yolu,
            "klasor_yolu": klasor_yolu,
            "kanal_adi": kanal_adi,
            "konu": konu
        }
        
        # Sadece varsayılan yol kullanıldıysa cache'e kaydet
        if not cikti_yolu:  
            self.cache_kaydet(kanal_adi, konu, harf_sayisi, sonuc)
        
        return sonuc

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-API Senarist - Belirtilen kanal, konu ve uzunlukta senaryo üreten senarist.")
    parser.add_argument("kanal_adi", help="Hedef kanal adı (İlham Perisi, Perspektif, vb.)")
    parser.add_argument("konu", help="Senaryo konusu")
    parser.add_argument("harf_sayisi", type=int, help="Hedef harf sayısı")
    parser.add_argument("--cikti_yolu", help="Senaryo dosyasının kaydedileceği tam yol", default=None)
    args = parser.parse_args()
    
    try:
        print("🎭 MULTI-API SENARYO ÜRETİCİ BAŞLADI")
        print("=" * 50)
        
        senarist = MultiAPISenarist()
        sonuc = senarist.senaryo_uret_ile_yol(args.kanal_adi, args.konu, args.harf_sayisi, args.cikti_yolu)
        
        print("\n" + "=" * 50)
        print("🎉 MULTI-API SENARYO ÜRETİMİ TAMAMLANDI!")
        print("=" * 50)
        print(f"📺 Kanal: {sonuc['kanal_adi']}")
        print(f"📝 Konu: {sonuc['konu']}")
        print(f"📁 Dosya konumu: {sonuc['dosya_yolu']}")
        print(f"📏 Metin uzunluğu: {len(sonuc['senaryo_metni'])} karakter")
        
        # API kullanım raporu
        from api_manager import get_api_manager
        api_manager = get_api_manager()
        print(api_manager.get_usage_report())
        
        if not args.cikti_yolu:  
            print("\n🎬 Sonraki adım için komut:")
            print(f"python moduller/yonetmen.py \"{sonuc['dosya_yolu']}\" \"{sonuc['klasor_yolu']}/proje.json\"")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        sys.exit(1)
