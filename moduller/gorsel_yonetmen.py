# gorsel-yonetmen.py

import os
import json
import argparse
from google import genai
from google.genai import types

class GorselYonetmen:
    """
    proje.json dosyasındaki görsel prompt'ları kullanarak sahneler için görseller üretir.
    """
    def __init__(self):
        print("🎨 Görsel Yönetmen başlatılıyor...")
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY ortam değişkeni bulunamadı!")
            
        self.client = genai.Client(api_key=api_key)
        print("🤖 AI görsel üretim sistemi hazır!")

    def json_oku(self, json_dosya_yolu):
        """Proje JSON dosyasını okur ve içeriğini döndürür."""
        print(f"📖 Proje dosyası okunuyor: {json_dosya_yolu}")
        try:
            with open(json_dosya_yolu, 'r', encoding='utf-8') as f:
                veri = json.load(f)
            print("✅ Proje dosyası başarıyla okundu!")
            return veri
        except FileNotFoundError:
            print(f"❌ Hata: '{json_dosya_yolu}' dosyası bulunamadı.")
            return None
        except Exception as e:
            print(f"❌ Hata: JSON okuma sırasında problem: {e}")
            return None

    def tum_gorselleri_olustur(self, json_dosya_yolu, cikti_klasoru):
        """JSON dosyasındaki tüm segmentler için görselleri oluşturur."""
        
        print("🎬 Görsel üretim süreci başlatılıyor...")
        
        proje_verisi = self.json_oku(json_dosya_yolu)
        if not proje_verisi:
            return

        print(f"📁 Çıktı klasörü oluşturuluyor: {cikti_klasoru}")
        os.makedirs(cikti_klasoru, exist_ok=True)
        
        hikaye_yapisi = proje_verisi["hikaye_yapisi"]
        toplam_segment = 0
        basarili_istek = 0
        
        print("\n🎨 Sahneler için görseller üretilmeye başlanıyor...")
        
        for bolum_adi, bolum_verisi in hikaye_yapisi.items():
            bolum_kisaltmasi = bolum_verisi["bolum_kisaltmasi"]
            print(f"\n📖 Bölüm: {bolum_adi.upper()} ({bolum_kisaltmasi})")
            
            for paragraf in bolum_verisi["paragraflar"]:
                paragraf_no = paragraf["paragraf_numarasi"]
                
                for segment in paragraf["segmentler"]:
                    toplam_segment += 1
                    segment_no = segment["segment_numarasi"]
                    gorsel_prompt = segment["gorsel_prompt"]
                    
                    # EKLENDİ: Her segment için en-boy oranını JSON'dan oku.
                    # Eğer JSON'da bu alan yoksa veya hatalıysa, varsayılan olarak "LANDSCAPE" kullan.
                    # DEĞİŞTİRİLDİ: Geçerli oranlar listesi ve varsayılan değer güncellendi.
                    gecerli_oranlar = ["1:1", "4:3", "3:4", "16:9", "9:16"]
                    en_boy_orani = segment.get("en_boy_orani", "16:9") # Varsayılan yatay (16:9)
                    if en_boy_orani not in gecerli_oranlar:
                        print(f"  ⚠️ Uyarı: Geçersiz en_boy_orani '{en_boy_orani}', varsayılan '16:9' kullanılacak.")
                        en_boy_orani = "16:9"

                    temel_dosya_adi = f"{bolum_kisaltmasi}-{paragraf_no}-{segment_no}"
                    print(f"  🖼️  İşleniyor: {temel_dosya_adi} [{en_boy_orani}] -> \"{gorsel_prompt[:60]}...\"")

                    try:
                        response = self.client.models.generate_images(
                            model='imagen-4.0-generate-preview-06-06',
                            prompt=gorsel_prompt,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                # DEĞİŞTİRİLDİ: 'aspect_ratio' artık dinamik olarak JSON'dan okunuyor.
                                aspect_ratio=en_boy_orani
                            )
                        )
                        
                        if response.generated_images:
                            generated_image = response.generated_images[0]
                            image_filename = f"{temel_dosya_adi}.png"
                            dosya_yolu = os.path.join(cikti_klasoru, image_filename)
                            generated_image.image.save(dosya_yolu)
                            print(f"    ✅ Kaydedildi: {dosya_yolu}")
                            basarili_istek += 1
                        else:
                            print(f"    ❌ Hata ({temel_dosya_adi}): AI tarafından görsel üretilmedi.")

                    except Exception as e:
                        print(f"    ❌ Hata ({temel_dosya_adi}): Görsel oluşturulamadı - {e}")

        # Özet bilgi
        print("\n" + "=" * 50)
        print("🎉 GÖRSEL ÜRETİMİ TAMAMLANDI!")
        print("=" * 50)
        print(f"📊 Toplam segment: {toplam_segment}")
        print(f"✅ Başarılı istek: {basarili_istek}")
        print(f"❌ Başarısız istek: {toplam_segment - basarili_istek}")
        print(f"📁 Görsellerin kaydedildiği klasör: {cikti_klasoru}")
        print("=" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSON dosyasındaki görsel prompt'ları kullanarak görseller üretir.")
    parser.add_argument("json_dosyasi", help="Proje JSON dosyasının yolu")
    parser.add_argument("cikti_klasoru", help="Oluşturulan görsellerin kaydedileceği klasör")
    args = parser.parse_args()
    
    try:
        print("🎨 GÖRSEL YÖNETMEN ÇALIŞMAYA BAŞLADI")
        print("=" * 50)
        
        gorsel_yonetmen = GorselYonetmen()
        gorsel_yonetmen.tum_gorselleri_olustur(args.json_dosyasi, args.cikti_klasoru)

        print("\n🎬 Sonraki adım için komut:")
        print(f"python moduller/kurgu.py \"{args.cikti_klasoru}\"")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Beklenmeyen bir hata oluştu: {e}")
