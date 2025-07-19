import os
import json
import argparse
import sys
import base64
import requests

# Path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from google import genai
from google.genai import types
import openai
from api_manager import get_api_manager, APIType

class MultiAPIGorselYonetmen:
    """Multi-API ile görsel üretimi"""
    def __init__(self):
        print("🎨 Multi-API Görsel Yönetmen başlatılıyor...")
        self.api_manager = get_api_manager()
        print("🤖 Multi-API görsel üretim sistemi hazır!")

    def json_oku(self, json_dosya_yolu):
        """Proje JSON dosyasını okur ve içeriğini döndürür."""
        print(f"📖 Proje dosyası okunuyor: {json_dosya_yolu}")
        try:
            with open(json_dosya_yolu, 'r', encoding='utf-8') as f:
                veri = json.load(f)
            print("✅ Proje dosyası başarıyla okundu!")
            return veri
        except FileNotFoundError:
            print(f"❌ HATA: '{json_dosya_yolu}' dosyası bulunamadı.")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"❌ HATA: '{json_dosya_yolu}' geçerli bir JSON dosyası değil.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ HATA: JSON okuma sırasında problem: {e}")
            sys.exit(1)

    def image_request_wrapper(self, gorsel_prompt, en_boy_orani):
        """Multi-API image generation wrapper"""
        
        def gemini_image_request(client, config):
            response = client.models.generate_images(
                model=config['model_image'],
                prompt=gorsel_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=en_boy_orani
                )
            )
            
            if response.generated_images:
                return response.generated_images[0].image
            else:
                raise Exception("Gemini'den görsel üretilemedi")
        
        def openai_image_request(client, config):
            # DALL-E aspect ratio mapping
            size_mapping = {
                "1:1": "1024x1024",
                "16:9": "1792x1024", 
                "9:16": "1024x1792",
                "4:3": "1024x1024",  # En yakın kare
                "3:4": "1024x1024"   # En yakın kare
            }
            
            size = size_mapping.get(en_boy_orani, "1024x1024")
            
            response = client.images.generate(
                model=config.get('model_image', 'dall-e-3'),
                prompt=gorsel_prompt,
                size=size,
                quality="standard",
                n=1,
            )
            
            # URL'den görsel indir
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            
            if image_response.status_code == 200:
                # Temp dosya oluştur ve PIL Image döndür
                import tempfile
                from PIL import Image
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_file.write(image_response.content)
                    temp_path = temp_file.name
                
                image = Image.open(temp_path)
                os.unlink(temp_path)  # Temp dosyayı sil
                return image
            else:
                raise Exception(f"OpenAI görsel indirme hatası: {image_response.status_code}")
        
        def unified_image_request(client, config):
            if hasattr(client, 'models') and hasattr(client.models, 'generate_images'):  # Gemini
                return gemini_image_request(client, config)
            elif hasattr(client, 'images') and hasattr(client.images, 'generate'):  # OpenAI  
                return openai_image_request(client, config)
            else:
                raise Exception(f"Image generation desteklenmeyen API client: {type(client)}")
        
        return self.api_manager.make_request(APIType.IMAGE, unified_image_request)

    def tum_gorselleri_olustur(self, json_dosya_yolu, cikti_klasoru):
        """JSON dosyasındaki tüm segmentler için Multi-API ile görselleri oluşturur."""
        
        print("🎬 Multi-API Görsel üretim süreci başlatılıyor...")
        
        proje_verisi = self.json_oku(json_dosya_yolu)

        print(f"📁 Çıktı klasörü oluşturuluyor: {cikti_klasoru}")
        os.makedirs(cikti_klasoru, exist_ok=True)
        
        try:
            hikaye_yapisi = proje_verisi["hikaye_yapisi"]
        except KeyError:
            print("❌ HATA: Proje dosyasında hikaye_yapisi bulunamadı!")
            sys.exit(1)
            
        toplam_segment = 0
        basarili_istek = 0
        
        print("\n🎨 Sahneler için Multi-API ile görseller üretilmeye başlanıyor...")
        
        for bolum_adi, bolum_verisi in hikaye_yapisi.items():
            try:
                bolum_kisaltmasi = bolum_verisi["bolum_kisaltmasi"]
                print(f"\n📖 Bölüm: {bolum_adi.upper()} ({bolum_kisaltmasi})")
                
                for paragraf in bolum_verisi["paragraflar"]:
                    paragraf_no = paragraf["paragraf_numarasi"]
                    
                    for segment in paragraf["segmentler"]:
                        toplam_segment += 1
                        segment_no = segment["segment_numarasi"]
                        gorsel_prompt = segment["gorsel_prompt"]
                        
                        # Her segment için en-boy oranını JSON'dan oku
                        gecerli_oranlar = ["1:1", "4:3", "3:4", "16:9", "9:16"]
                        en_boy_orani = segment.get("en_boy_orani", "16:9")  # Varsayılan yatay (16:9)
                        if en_boy_orani not in gecerli_oranlar:
                            print(f"  ⚠️ Uyarı: Geçersiz en_boy_orani '{en_boy_orani}', varsayılan '16:9' kullanılacak.")
                            en_boy_orani = "16:9"

                        temel_dosya_adi = f"{bolum_kisaltmasi}-{paragraf_no}-{segment_no}"
                        print(f"  🖼️  İşleniyor: {temel_dosya_adi} [{en_boy_orani}] -> \"{gorsel_prompt[:60]}...\"")

                        try:
                            # Multi-API ile görsel üret
                            generated_image = self.image_request_wrapper(gorsel_prompt, en_boy_orani)
                            
                            image_filename = f"{temel_dosya_adi}.png"
                            dosya_yolu = os.path.join(cikti_klasoru, image_filename)
                            generated_image.save(dosya_yolu)
                            print(f"    ✅ Kaydedildi: {dosya_yolu}")
                            basarili_istek += 1

                        except Exception as e:
                            print(f"    ❌ KRITIK HATA: Görsel oluşturulamadı ({temel_dosya_adi}): {e}")
                            sys.exit(1)  # Görsel üretilemezse dur

            except KeyError as e:
                print(f"❌ HATA: Bölüm yapısında eksik alan: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"❌ HATA: Bölüm işleme sırasında hata: {e}")
                sys.exit(1)

        # Özet bilgi
        print("\n" + "=" * 50)
        print("🎉 MULTI-API GÖRSEL ÜRETİMİ TAMAMLANDI!")
        print("=" * 50)
        print(f"📊 Toplam segment: {toplam_segment}")
        print(f"✅ Başarılı istek: {basarili_istek}")
        print(f"❌ Başarısız istek: {toplam_segment - basarili_istek}")
        print(f"📁 Görsellerin kaydedildiği klasör: {cikti_klasoru}")
        
        # API kullanım raporu
        print(self.api_manager.get_usage_report())
        
        if basarili_istek != toplam_segment:
            print("❌ KRITIK HATA: Tüm görseller üretilemedi!")
            sys.exit(1)
            
        print("=" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-API Görsel Yönetmen - JSON dosyasındaki görsel prompt'ları kullanarak görseller üretir.")
    parser.add_argument("json_dosyasi", help="Proje JSON dosyasının yolu")
    parser.add_argument("cikti_klasoru", help="Oluşturulan görsellerin kaydedileceği klasör")
    args = parser.parse_args()
    
    try:
        print("🎨 MULTI-API GÖRSEL YÖNETMEN ÇALIŞMAYA BAŞLADI")
        print("=" * 50)
        
        gorsel_yonetmen = MultiAPIGorselYonetmen()
        gorsel_yonetmen.tum_gorselleri_olustur(args.json_dosyasi, args.cikti_klasoru)

        print("\n🎬 Sonraki adım için komut:")
        proje_klasoru = os.path.dirname(args.cikti_klasoru)
        ses_klasoru = os.path.join(proje_klasoru, "sesler")
        final_video = os.path.join(proje_klasoru, "final_video.mp4")
        print(f"python moduller/kurgu.py \"{args.json_dosyasi}\" \"{ses_klasoru}\" \"{args.cikti_klasoru}\" \"{final_video}\"")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Beklenmeyen bir hata oluştu: {e}")
        sys.exit(1)