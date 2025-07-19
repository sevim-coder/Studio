import wave
import json
import os
import argparse
import sys
import base64

# Path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from google import genai
from google.genai import types
from api_manager import get_api_manager, APIType

class MultiAPISeslendirmen:
    def __init__(self):
        print("🎙️ Multi-API Seslendirmen başlatılıyor...")
        self.api_manager = get_api_manager()
        print("🤖 Multi-API seslendirme sistemi hazır!")
    
    def wave_file(self, filename, pcm, channels=1, rate=24000, sample_width=2):
        """WAV dosyası oluşturur - Robust error handling with sys.exit(1) on corruption"""
        try:
            # Validate input parameters
            if not filename or not pcm:
                print(f"❌ KRITIK HATA: Geçersiz WAV dosyası parametreleri - filename: {filename}, pcm data: {len(pcm) if pcm else 0} bytes")
                sys.exit(1)
                
            if channels < 1 or channels > 2:
                print(f"❌ KRITIK HATA: Geçersiz kanal sayısı: {channels} (1 veya 2 olmalı)")
                sys.exit(1)
                
            if rate < 8000 or rate > 48000:
                print(f"❌ KRITIK HATA: Geçersiz sample rate: {rate} Hz (8000-48000 arası olmalı)")
                sys.exit(1)
                
            if sample_width not in [1, 2, 4]:
                print(f"❌ KRITIK HATA: Geçersiz sample width: {sample_width} (1, 2 veya 4 olmalı)")
                sys.exit(1)
            
            # Create WAV file with robust error handling
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(rate)
                wf.writeframes(pcm)
                
            # Verify the created file
            if not os.path.exists(filename):
                print(f"❌ KRITIK HATA: WAV dosyası oluşturulamadı: {filename}")
                sys.exit(1)
                
            # Verify file size is reasonable
            file_size = os.path.getsize(filename)
            if file_size < 100:  # Less than 100 bytes is likely corrupted
                print(f"❌ KRITIK HATA: WAV dosyası çok küçük (bozuk olabilir): {filename} - {file_size} bytes")
                os.remove(filename)  # Clean up corrupted file
                sys.exit(1)
                
        except wave.Error as e:
            print(f"❌ KRITIK HATA: WAV dosyası formatı hatası: {e} - Dosya: {filename}")
            if os.path.exists(filename):
                os.remove(filename)  # Clean up corrupted file
            sys.exit(1)
        except IOError as e:
            print(f"❌ KRITIK HATA: WAV dosyası yazma hatası: {e} - Dosya: {filename}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ KRITIK HATA: WAV dosyası oluşturma sırasında beklenmeyen hata: {e} - Dosya: {filename}")
            if os.path.exists(filename):
                os.remove(filename)  # Clean up corrupted file
            sys.exit(1)
    
    def json_oku(self, json_dosya_yolu):
        """JSON dosyasını okur"""
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
    
    def tts_request_wrapper(self, metin, ses_ismi):
        """Multi-API TTS wrapper"""
        
        def gemini_tts_request(client, config):
            tam_prompt = f' "{metin}"'
            
            response = client.models.generate_content(
                model=config['model_tts'],
                contents=tam_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=ses_ismi,
                            )
                        )
                    ),
                )
            )
            
            if not response.candidates or not response.candidates[0].content.parts:
                raise Exception("AI'den geçerli ses yanıtı alınamadı")
            
            return response.candidates[0].content.parts[0].inline_data.data
        
        def openai_tts_request(client, config):
            # OpenAI ses isimlerini map et
            voice_mapping = {
                'Aoede': 'nova', 'Kore': 'alloy', 'Leda': 'echo', 'Zephyr': 'fable',
                'Puck': 'onyx', 'Charon': 'shimmer', 'Fenrir': 'nova', 'Orus': 'onyx'
            }
            
            openai_voice = voice_mapping.get(ses_ismi, 'alloy')
            
            response = client.audio.speech.create(
                model=config.get('model_tts', 'tts-1'),
                voice=openai_voice,
                input=metin
            )
            
            return response.content
        
        def unified_tts_request(client, config):
            if hasattr(client, 'models') and hasattr(client.models, 'generate_content'):  # Gemini
                return gemini_tts_request(client, config)
            elif hasattr(client, 'audio') and hasattr(client.audio, 'speech'):  # OpenAI
                return openai_tts_request(client, config)
            else:
                raise Exception(f"TTS desteklenmeyen API client: {type(client)}")
        
        return self.api_manager.make_request(APIType.TTS, unified_tts_request)
    
    def segment_seslendiry(self, metin, ses_ismi, dosya_yolu):
        """Multi-API ile tek bir segmenti seslendirir"""
        try:
            print(f"🎤 Seslendiriliyor: {metin[:60]}...")
            
            # Multi-API TTS isteği
            audio_data = self.tts_request_wrapper(metin, ses_ismi)
            
            # WAV dosyası olarak kaydet
            self.wave_file(dosya_yolu, audio_data)
            print(f"✅ Kaydedildi: {dosya_yolu}")
            
            return True
            
        except Exception as e:
            print(f"❌ HATA: {dosya_yolu} - {e}")
            return False
    
    def tum_segmentleri_seslendiry(self, json_dosya_yolu, cikti_klasoru):
        """JSON dosyasındaki tüm segmentleri Multi-API ile seslendirir"""
        
        print("🎬 Multi-API Seslendirme süreci başlatılıyor...")
        
        # JSON dosyasını oku
        proje_verisi = self.json_oku(json_dosya_yolu)
        
        # Çıktı klasörünü oluştur
        print(f"📁 Çıktı klasörü oluşturuluyor: {cikti_klasoru}")
        os.makedirs(cikti_klasoru, exist_ok=True)
        
        # Ses sanatçısını al
        try:
            ses_ismi = proje_verisi["youtube_bilgileri"]["seslendirmen"]
            print(f"🎭 Seslendirmen: {ses_ismi}")
        except KeyError:
            print("❌ HATA: Proje dosyasında seslendirmen bilgisi bulunamadı!")
            sys.exit(1)
        
        # Hikaye yapısını işle
        try:
            hikaye_yapisi = proje_verisi["hikaye_yapisi"]
        except KeyError:
            print("❌ HATA: Proje dosyasında hikaye_yapisi bulunamadı!")
            sys.exit(1)
            
        toplam_segment = 0
        basarili_segment = 0
        
        print("\n🎬 Bölümler Multi-API ile işlenmeye başlanıyor...")
        
        # Her bölümü işle (giris, gelisme, sonuc)
        for bolum_adi, bolum_verisi in hikaye_yapisi.items():
            try:
                bolum_kisaltmasi = bolum_verisi["bolum_kisaltmasi"]
                print(f"\n📖 {bolum_adi.upper()} bölümü işleniyor ({bolum_kisaltmasi})...")
                
                # Her paragrafı işle
                for paragraf in bolum_verisi["paragraflar"]:
                    paragraf_no = paragraf["paragraf_numarasi"]
                    print(f"  📝 Paragraf {paragraf_no} işleniyor...")
                    
                    # Her segmenti işle
                    for segment in paragraf["segmentler"]:
                        segment_no = segment["segment_numarasi"]
                        metin = segment["metin"]                
                        
                        # Dosya adını oluştur: BOLUM-PARAGRAF-SEGMENT.wav
                        dosya_adi = f"{bolum_kisaltmasi}-{paragraf_no}-{segment_no}.wav"
                        dosya_yolu = os.path.join(cikti_klasoru, dosya_adi)
                        
                        # Segmenti Multi-API ile seslendiry
                        toplam_segment += 1
                        if self.segment_seslendiry(metin, ses_ismi, dosya_yolu):
                            basarili_segment += 1
                        else:
                            print(f"❌ KRITIK HATA: Segment seslendirilmedi: {dosya_adi}")
                            sys.exit(1)  # Herhangi bir segment başarısız olursa dur
                            
            except KeyError as e:
                print(f"❌ HATA: Bölüm yapısında eksik alan: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"❌ HATA: Bölüm işleme sırasında hata: {e}")
                sys.exit(1)
        
        # Özet bilgi
        print(f"\n" + "=" * 50)
        print(f"🎉 MULTI-API SESLENDİRME TAMAMLANDI!")
        print(f"=" * 50)
        print(f"📊 Toplam segment: {toplam_segment}")
        print(f"✅ Başarılı: {basarili_segment}")
        print(f"❌ Başarısız: {toplam_segment - basarili_segment}")
        print(f"📁 Dosyalar kaydedildi: {cikti_klasoru}")
        
        # API kullanım raporu
        print(self.api_manager.get_usage_report())
        
        if basarili_segment != toplam_segment:
            print("❌ KRITIK HATA: Tüm segmentler tamamlanamadı!")
            sys.exit(1)
            
        print("=" * 50)

if __name__ == "__main__":
    # Komut satırı argümanları
    parser = argparse.ArgumentParser(description="Multi-API Seslendirmen - JSON dosyasındaki metinleri seslendirir ve WAV dosyaları oluşturur.")
    parser.add_argument("json_dosyasi", help="Proje JSON dosyasının yolu")
    parser.add_argument("cikti_klasoru", help="WAV dosyalarının kaydedileceği klasör")
    args = parser.parse_args()
    
    try:
        print("🎙️ MULTI-API SESLENDİRMEN ÇALIŞMAYA BAŞLADI")
        print("=" * 50)
        
        seslendirmen = MultiAPISeslendirmen()
        seslendirmen.tum_segmentleri_seslendiry(args.json_dosyasi, args.cikti_klasoru)
        
        print("\n🎬 Sonraki adım için komut:")
        print(f"python moduller/gorsel_yonetmen_multiapi.py \"{args.json_dosyasi}\" \"{os.path.dirname(args.cikti_klasoru)}/gorseller\"")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        sys.exit(1)