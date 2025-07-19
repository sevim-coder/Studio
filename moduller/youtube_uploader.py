import os
import sys
import json
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# --- Sabit Ayarlar ---
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SERVICE_ACCOUNT_FILE = "service_account.json"

class YoutubeUploader:
    def __init__(self):
        print("🚀 YouTube Uploader başlatılıyor...")
        self.youtube_service = self.get_authenticated_service()
    
    def get_authenticated_service(self):
        """OAuth 2.0 ve Service Account hibrit kimlik doğrulama - TEK METOD"""
        print("🔑 Kimlik doğrulama başlatılıyor...")
        
        # 1. Önce OAuth dene (öncelikli)
        if os.path.exists("credentials.json"):
            print("📱 OAuth 2.0 kimlik doğrulaması deneniyor...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES)
                credentials = flow.run_local_server(port=0)
                print("✅ OAuth kimlik doğrulama başarılı!")
                return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, 
                                                     credentials=credentials)
            except Exception as e:
                print(f"⚠️ OAuth kimlik doğrulama başarısız: {e}")
                print("🔄 Service Account'a geçiliyor...")
        
        # 2. Fallback: Service Account
        elif os.path.exists(SERVICE_ACCOUNT_FILE):
            print("🔐 Service Account kimlik doğrulaması deneniyor...")
            try:
                credentials = Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
                print("✅ Service Account kimlik doğrulama başarılı!")
                return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, 
                                                     credentials=credentials)
            except Exception as e:
                print(f"❌ KRITIK HATA: Service Account kimlik doğrulama başarısız: {e}")
                sys.exit(1)
        
        # 3. Hiçbiri bulunamadı
        else:
            print("❌ KRITIK HATA: Kimlik doğrulama dosyası bulunamadı!")
            print("💡 Gerekli dosyalar:")
            print("   - credentials.json (OAuth 2.0) VEYA")
            print("   - service_account.json (Service Account)")
            sys.exit(1)

    def upload_video(self, video_path, title, description, category_id, tags, privacy_status):
        """Videoyu YouTube'a yükler - ANINDA DURMA GARANTİLİ"""
        try:
            print(f"📤 '{os.path.basename(video_path)}' videosu yükleniyor...")
            
            # Video dosyası kontrolü
            if not os.path.exists(video_path):
                print(f"❌ KRITIK HATA: Video dosyası bulunamadı: {video_path}")
                sys.exit(1)
            
            # Video dosyası boyut kontrolü
            file_size = os.path.getsize(video_path)
            if file_size == 0:
                print(f"❌ KRITIK HATA: Video dosyası boş: {video_path}")
                sys.exit(1)
            
            # Video format kontrolü
            if not video_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                print(f"❌ KRITIK HATA: Desteklenmeyen video formatı: {video_path}")
                sys.exit(1)
            
            print(f"📊 Video boyutu: {file_size / (1024*1024):.1f} MB")
            
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
            error = None
            
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if 'id' in response:
                        print(f"\n✅ Video başarıyla yüklendi!")
                        print(f"🔗 YouTube Link: http://www.youtube.com/watch?v={response['id']}")
                        return True
                    elif status:
                        # İlerleme gösterimi
                        progress = int(status.progress() * 100)
                        print(f"  📤 Yükleme: %{progress}", end='\r')
                except Exception as e:
                    error_msg = str(e)
                    print(f"\n❌ KRITIK HATA: Video yükleme başarısız: {error_msg}")
                    
                    # YouTube API özel hata kodları
                    if "quotaExceeded" in error_msg:
                        print("💔 YouTube API quota'sı aşıldı. Yarın tekrar deneyin.")
                    elif "forbidden" in error_msg.lower():
                        print("🚫 YouTube kanalına erişim izni yok.")
                    elif "unauthorized" in error_msg.lower():
                        print("🔐 Kimlik doğrulama geçersiz.")
                    
                    sys.exit(1)  # ANINDA DUR
            
            return True
            
        except Exception as e:
            print(f"\n❌ KRITIK HATA: Beklenmeyen video yükleme hatası: {e}")
            sys.exit(1)  # ANINDA DUR

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("❌ KRITIK HATA: Yanlış parametre sayısı!")
        print("Kullanım: python youtube_uploader.py [video_dosya_yolu] [proje_json_yolu]")
        sys.exit(1)
    
    video_dosyasi = sys.argv[1]
    proje_json_dosyasi = sys.argv[2]

    # Dosya varlık kontrolleri - ANINDA DUR
    if not os.path.exists(video_dosyasi):
        print(f"❌ KRITIK HATA: Video dosyası bulunamadı: '{video_dosyasi}'")
        sys.exit(1)
        
    if not os.path.exists(proje_json_dosyasi):
        print(f"❌ KRITIK HATA: Proje JSON dosyası bulunamadı: '{proje_json_dosyasi}'")
        sys.exit(1)
    
    # JSON okuma - ANINDA DUR
    try:
        with open(proje_json_dosyasi, 'r', encoding='utf-8') as f:
            proje_data = json.load(f)
        proje_bilgileri = proje_data["youtube_bilgileri"]
    except KeyError:
        print("❌ KRITIK HATA: Proje dosyasında youtube_bilgileri bulunamadı!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ KRITIK HATA: JSON parse hatası: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ KRITIK HATA: Proje dosyası okunamadı: {e}")
        sys.exit(1)
    
    # YouTube bilgileri hazırlama
    baslik = proje_bilgileri.get("baslik", "Başlık Belirtilmemiş")
    aciklama = proje_bilgileri.get("aciklama", "Açıklama Belirtilmemiş")
    etiketler = proje_bilgileri.get("etiketler", [])
    kategori_map = {"Hikaye Anlatımı": "22", "Science & Technology": "28", "Education": "27"}
    kategori_id = kategori_map.get(proje_bilgileri.get("kategori"), "22")
    gizlilik = proje_bilgileri.get("gizlilik_durumu", "private")
    
    try:
        print("🚀 YOUTUBE UPLOADER ÇALIŞMAYA BAŞLADI")
        print("=" * 50)
        print(f"📹 Video: {os.path.basename(video_dosyasi)}")
        print(f"🏷️ Başlık: {baslik}")
        print(f"🔒 Gizlilik: {gizlilik}")
        print("=" * 50)
        
        uploader = YoutubeUploader()
        uploader.upload_video(video_dosyasi, baslik, aciklama, kategori_id, etiketler, gizlilik)
        
        print("\n" + "=" * 50)
        print("🎉 YOUTUBE YÜKLEME TAMAMLANDI!")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ KRITIK HATA: Beklenmeyen sistem hatası: {e}")
        sys.exit(1)