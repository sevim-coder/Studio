from google import genai
from google.genai import types
import wave
import json
import os
import argparse

class Seslendirmen:
    def __init__(self):
        # Gemini API istemcisini başlat
        self.client = genai.Client()
    
    def wave_file(self, filename, pcm, channels=1, rate=24000, sample_width=2):
        """WAV dosyası oluşturur"""
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)
    
    def json_oku(self, json_dosya_yolu):
        """JSON dosyasını okur"""
        try:
            with open(json_dosya_yolu, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Hata: '{json_dosya_yolu}' dosyası bulunamadı.")
            return None
        except json.JSONDecodeError:
            print(f"Hata: '{json_dosya_yolu}' geçerli bir JSON dosyası değil.")
            return None
        except Exception as e:
            print(f"Hata: JSON okuma sırasında problem: {e}")
            return None
    
    def segment_seslendiry(self, tts_prompt, metin, ses_ismi, dosya_yolu):
        """Tek bir segmenti seslendirir"""
        try:
            # TTS prompt'u ve metni birleştir
            tam_prompt = f'{tts_prompt} "{metin}"'
            
            print(f"Seslendiriliyor: {tam_prompt[:60]}...")
            
            # Gemini TTS ile seslendirme
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
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
            
            # Ses verisini al
            data = response.candidates[0].content.parts[0].inline_data.data
            
            # WAV dosyası olarak kaydet
            self.wave_file(dosya_yolu, data)
            print(f"✓ Kaydedildi: {dosya_yolu}")
            
            return True
            
        except Exception as e:
            print(f"✗ Hata: {dosya_yolu} - {e}")
            return False
    
    def tum_segmentleri_seslendiry(self, json_dosya_yolu, cikti_klasoru):
        """JSON dosyasındaki tüm segmentleri seslendirir"""
        
        # JSON dosyasını oku
        proje_verisi = self.json_oku(json_dosya_yolu)
        if not proje_verisi:
            return
        
        # Çıktı klasörünü oluştur
        os.makedirs(cikti_klasoru, exist_ok=True)
        
        # Ses sanatçısını al
        ses_ismi = proje_verisi["youtube_bilgileri"]["seslendirmen"]
        print(f"Seslendirmen: {ses_ismi}")
        
        # Hikaye yapısını işle
        hikaye_yapisi = proje_verisi["hikaye_yapisi"]
        toplam_segment = 0
        basarili_segment = 0
        
        # Her bölümü işle (giris, gelisme, sonuc)
        for bolum_adi, bolum_verisi in hikaye_yapisi.items():
            bolum_kisaltmasi = bolum_verisi["bolum_kisaltmasi"]
            print(f"\n🎬 {bolum_adi.upper()} bölümü işleniyor ({bolum_kisaltmasi})...")
            
            # Her paragrafı işle
            for paragraf in bolum_verisi["paragraflar"]:
                paragraf_no = paragraf["paragraf_numarasi"]
                
                # Her segmenti işle
                for segment in paragraf["segmentler"]:
                    segment_no = segment["segment_numarasi"]
                    metin = segment["metin"]
                    tts_prompt = segment["tts_prompt"]
                    
                    # Dosya adını oluştur: BOLUM-PARAGRAF-SEGMENT.wav
                    dosya_adi = f"{bolum_kisaltmasi}-{paragraf_no}-{segment_no}.wav"
                    dosya_yolu = os.path.join(cikti_klasoru, dosya_adi)
                    
                    # Segmenti seslendiry
                    toplam_segment += 1
                    if self.segment_seslendiry(tts_prompt, metin, ses_ismi, dosya_yolu):
                        basarili_segment += 1
        
        # Özet bilgi
        print(f"\n📊 Seslendirme tamamlandı!")
        print(f"Toplam segment: {toplam_segment}")
        print(f"Başarılı: {basarili_segment}")
        print(f"Başarısız: {toplam_segment - basarili_segment}")
        print(f"Dosyalar kaydedildi: {cikti_klasoru}")

if __name__ == "__main__":
    # Komut satırı argümanları
    parser = argparse.ArgumentParser(description="JSON dosyasındaki metinleri seslendirir ve WAV dosyaları oluşturur.")
    parser.add_argument("json_dosyasi", help="Proje JSON dosyasının yolu")
    parser.add_argument("cikti_klasoru", help="WAV dosyalarının kaydedileceği klasör")
    args = parser.parse_args()
    
    try:
        seslendirmen = Seslendirmen()
        seslendirmen.tum_segmentleri_seslendiry(args.json_dosyasi, args.cikti_klasoru)
        
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")