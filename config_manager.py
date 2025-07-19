import os
import json
import sys
from typing import Dict, Any, Optional

class ConfigManager:
    """Gelişmiş yapılandırma yöneticisi - JSON + ENV hibrit"""
    
    def __init__(self, config_file: str = "config_advanced.json"):
        self.config_file = config_file
        self.config = {}
        self.env_prefix = "YAPIMCI_"
        self.load_config()
    
    def load_config(self):
        """Config dosyasını yükle ve ENV değişkenleriyle override et"""
        # 1. JSON dosyasını yükle
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Environment variable substitution
                    content = self._substitute_env_vars(content)
                    self.config = json.loads(content)
                print(f"✅ Config dosyası yüklendi: {self.config_file}")
            else:
                print(f"⚠️ Config dosyası bulunamadı: {self.config_file}")
                self.config = self._get_default_config()
        except Exception as e:
            print(f"❌ Config yükleme hatası: {e}")
            self.config = self._get_default_config()
        
        # 2. Environment variables ile override et
        self._override_with_env()
        
        # 3. Zorunlu alanları kontrol et
        self._validate_config()
    
    def _substitute_env_vars(self, content: str) -> str:
        """${VAR_NAME} formatındaki environment variable'ları değiştir"""
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            env_value = os.getenv(var_name)
            if env_value is None:
                print(f"⚠️ Environment variable bulunamadı: {var_name}")
                return match.group(0)  # Değiştirme, orijinal metni bırak
            return env_value
        
        # ${VARIABLE_NAME} formatını bul ve değiştir
        pattern = r'\$\{([^}]+)\}'
        result = re.sub(pattern, replace_var, content)
        return result
    
    def _override_with_env(self):
        """Environment variables ile config değerlerini override et"""
        env_mappings = {
            f"{self.env_prefix}GEMINI_API_KEY": ["api_ayarlari", "gemini_api_key"],
            f"{self.env_prefix}LOG_LEVEL": ["sistem_ayarlari", "log_level"],
            f"{self.env_prefix}MAX_SEGMENTS": ["sistem_ayarlari", "max_segment_sayisi"],
            f"{self.env_prefix}DISK_MIN_MB": ["sistem_ayarlari", "disk_min_alan_mb"],
            f"{self.env_prefix}VIDEO_QUALITY": ["ffmpeg_ayarlari", "video_crf"],
            f"{self.env_prefix}YOUTUBE_PRIVACY": ["youtube_ayarlari", "varsayilan_gizlilik"],
            f"{self.env_prefix}CACHE_DIR": ["sistem_ayarlari", "cache_klasoru"],
            f"{self.env_prefix}TEMP_DIR": ["sistem_ayarlari", "gecici_klasor"]
        }
        
        for env_key, config_path in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value:
                self._set_nested_value(self.config, config_path, env_value)
                print(f"🔧 ENV override: {env_key} -> {'.'.join(config_path)}")
    
    def _set_nested_value(self, dictionary: Dict, path: list, value: Any):
        """Nested dictionary'de değer set etme"""
        for key in path[:-1]:
            dictionary = dictionary.setdefault(key, {})
        
        # Type conversion
        if isinstance(dictionary.get(path[-1]), int):
            value = int(value)
        elif isinstance(dictionary.get(path[-1]), float):
            value = float(value)
        elif isinstance(dictionary.get(path[-1]), bool):
            value = value.lower() in ('true', '1', 'yes', 'on')
        
        dictionary[path[-1]] = value
    
    def _validate_config(self):
        """Zorunlu config alanlarını kontrol et"""
        required_paths = [
            ["sistem_ayarlari", "max_segment_sayisi"],
            ["ffmpeg_ayarlari", "video_codec"],
            ["kalite_kontrol", "min_ses_suresi"]
        ]
        
        for path in required_paths:
            if not self._get_nested_value(self.config, path):
                raise ValueError(f"Zorunlu config eksik: {'.'.join(path)}")
    
    def _get_nested_value(self, dictionary: Dict, path: list) -> Any:
        """Nested dictionary'den değer alma"""
        for key in path:
            if isinstance(dictionary, dict) and key in dictionary:
                dictionary = dictionary[key]
            else:
                return None
        return dictionary
    
    def get(self, *path, default=None) -> Any:
        """Config değeri alma - path olarak: get('sistem_ayarlari', 'log_dosyasi')"""
        value = self._get_nested_value(self.config, list(path))
        return value if value is not None else default
    
    def get_kanal_config(self, kanal_adi: str) -> Dict:
        """Belirli bir kanal için config alma"""
        return self.get('kanal_ayarlari', kanal_adi, default={})
    
    def get_ffmpeg_config(self) -> Dict:
        """FFmpeg ayarlarını alma"""
        return self.get('ffmpeg_ayarlari', default={})
    
    def get_kalite_config(self) -> Dict:
        """Kalite kontrol ayarlarını alma"""
        return self.get('kalite_kontrol', default={})
    
    def save_config(self, config_file: Optional[str] = None):
        """Config'i dosyaya kaydetme"""
        file_path = config_file or self.config_file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Config kaydedildi: {file_path}")
        except Exception as e:
            print(f"❌ Config kaydetme hatası: {e}")
    
    def _get_default_config(self) -> Dict:
        """Varsayılan config değerleri"""
        return {
            "sistem_ayarlari": {
                "log_dosyasi": "yapimci_logs.txt",
                "max_segment_sayisi": 100,
                "disk_min_alan_mb": 2000
            },
            "ffmpeg_ayarlari": {
                "video_codec": "libx264",
                "video_crf": "23"
            },
            "kalite_kontrol": {
                "min_ses_suresi": 0.1,
                "max_ses_suresi": 300
            }
        }
    
    def update_daily_task(self, gun: str, kanal: str, konu: str, harf_sayisi: int):
        """Günlük görev güncelleme"""
        if 'gunluk_gorevler' not in self.config:
            self.config['gunluk_gorevler'] = {}
        
        self.config['gunluk_gorevler'][gun] = {
            "kanal_adi": kanal,
            "konu": konu, 
            "harf_sayisi": harf_sayisi
        }
        self.save_config()
        print(f"✅ {gun} günü için görev güncellendi")

# Global config instance
config = ConfigManager()