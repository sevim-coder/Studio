# moduller/youtube_uploader.py

import os
import sys
import json
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

# --- Sabit Ayarlar ---
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
# Servis Hesabı anahtar dosyanızın adı
SERVICE_ACCOUNT_FILE = "service_account.json"

class YoutubeUploader:
    def __init__(self):
        print("🚀 YouTube Uploader başlatılıyor...")
        self.youtube_service = self.get_authenticated_service()
    
    def get_authenticated_service(self):
        """Servis Hesabı anahtarını kullanarak YouTube API servisini başlatır."""
        print("🔑 Servis Hesabı ile kimlik doğrulanıyor...")
        try:
            credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            print("✅ Kimlik doğrulama başarılı.")
            return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
        except FileNotFoundError:
            print(f"❌ HATA: '{SERVICE_ACCOUNT_FILE}' dosyası bulunamadı. Lütfen kurulum adımlarını tamamlayın.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ HATA: Kimlik doğrulama sırasında bir sorun oluştu: {e}")
            sys.exit(1)

    def upload_video(self, video_path, title, description, category_id, tags, privacy_status):
        """Belirtilen videoyu YouTube'a yükler."""
        try:
            print(f"'{os.path.basename(video_path)}' videosu yükleniyor...")
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = self.youtube_service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if 'id' in response:
                    print(f"\n✅ Video başarıyla yüklendi! Link: http://www.youtube.com/watch?v={response['id']}")
                elif status:
                    # Konsolda ilerleme çubuğu gibi görünmesi için \r kullanılıyor
                    print(f"  Yükleniyor: {int(status.progress() * 100)}%", end='\r')
            
            return True
        except Exception as e:
            print(f"\n❌ HATA: Video yükleme sırasında bir sorun oluştu: {e}")
            return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Kullanım: python youtube_uploader.py [video_dosya_yolu] [proje_json_yolu]")
        sys.exit(1)
    
    video_dosyasi = sys.argv[1]
    proje_json_dosyasi = sys.argv[2]

    # Gerekli dosyaların varlığını kontrol et
    if not os.path.exists(video_dosyasi):
        print(f"❌ HATA: Video dosyası bulunamadı: '{video_dosyasi}'")
        sys.exit(1)
    if not os.path.exists(proje_json_dosyasi):
        print(f"❌ HATA: Proje JSON dosyası bulunamadı: '{proje_json_dosyasi}'")
        sys.exit(1)
    
    # Proje JSON dosyasından video bilgilerini oku
    with open(proje_json_dosyasi, 'r', encoding='utf-8') as f:
        proje_bilgileri = json.load(f)["youtube_bilgileri"]
    
    baslik = proje_bilgileri.get("baslik", "Başlık Belirtilmemiş")
    aciklama = proje_bilgileri.get("aciklama", "Açıklama Belirtilmemiş")
    etiketler = proje_bilgileri.get("etiketler", [])
    kategori_map = {"Hikaye Anlatımı": "22", "Bilim ve Teknoloji": "28"}
    kategori_id = kategori_map.get(proje_bilgileri.get("kategori"), "22") # Varsayılan: İnsanlar ve Bloglar
    gizlilik = proje_bilgileri.get("gizlilik_durumu", "private")
    
    try:
        uploader = YoutubeUploader()
        uploader.upload_video(video_dosyasi, baslik, aciklama, kategori_id, etiketler, gizlilik)
    except Exception as e:
        print(f"\n❌ Beklenmeyen bir hata oluştu: {e}")
