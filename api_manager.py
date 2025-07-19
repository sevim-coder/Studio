import os
import json
import time
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class APIType(Enum):
    TEXT = "text"
    TTS = "tts" 
    IMAGE = "image"

class APIStatus(Enum):
    ACTIVE = "active"
    QUOTA_EXCEEDED = "quota_exceeded"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class APIUsage:
    provider: str
    config_name: str
    requests_today: int = 0
    total_cost_today: float = 0.0
    last_error: Optional[str] = None
    status: APIStatus = APIStatus.ACTIVE
    last_used: Optional[datetime] = None

class MultiAPIManager:
    """Çoklu API sağlayıcı yöneticisi - Otomatik failover"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.usage_file = "api_usage.json"
        self.usage_data: Dict[str, APIUsage] = {}
        self.active_providers: Dict[APIType, List[Tuple[str, str]]] = {
            APIType.TEXT: [],
            APIType.TTS: [],
            APIType.IMAGE: []
        }
        
        self.load_usage_data()
        self.initialize_providers()
        
        # API client'ları lazy loading ile
        self._clients = {}
    
    def load_usage_data(self):
        """Günlük kullanım verilerini yükle"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                
                # Bugünün verilerini al
                today_str = date.today().isoformat()
                today_data = data.get(today_str, {})
                
                for key, usage_dict in today_data.items():
                    self.usage_data[key] = APIUsage(**usage_dict)
                    
            except Exception as e:
                logging.error(f"Usage data yükleme hatası: {e}")
    
    def save_usage_data(self):
        """Kullanım verilerini kaydet"""
        try:
            # Mevcut dosyayı oku
            all_data = {}
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r') as f:
                    all_data = json.load(f)
            
            # Bugünün verisini güncelle
            today_str = date.today().isoformat()
            today_data = {}
            
            for key, usage in self.usage_data.items():
                today_data[key] = {
                    'provider': usage.provider,
                    'config_name': usage.config_name,
                    'requests_today': usage.requests_today,
                    'total_cost_today': usage.total_cost_today,
                    'last_error': usage.last_error,
                    'status': usage.status.value,
                    'last_used': usage.last_used.isoformat() if usage.last_used else None
                }
            
            all_data[today_str] = today_data
            
            # Son 30 günü koru
            all_dates = list(all_data.keys())
            if len(all_dates) > 30:
                for old_date in all_dates[:-30]:
                    del all_data[old_date]
            
            with open(self.usage_file, 'w') as f:
                json.dump(all_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Usage data kaydetme hatası: {e}")
    
    def initialize_providers(self):
        """API sağlayıcılarını başlat ve sırala"""
        api_providers = self.config.get('api_providers', default={})
        
        # Her API tipi için sağlayıcıları topla ve sırala
        all_configs = []
        
        for provider_name, provider_configs in api_providers.items():
            for config_name, config in provider_configs.items():
                if config.get('api_key'):
                    all_configs.append({
                        'provider': provider_name,
                        'config_name': config_name,
                        'config': config,
                        'priority': config.get('priority', 999)
                    })
        
        # Önceliğe göre sırala
        all_configs.sort(key=lambda x: x['priority'])
        
        # Her API tipi için uygun sağlayıcıları ekle
        for item in all_configs:
            provider = item['provider']
            config_name = item['config_name']
            config = item['config']
            
            # Usage key oluştur
            usage_key = f"{provider}_{config_name}"
            if usage_key not in self.usage_data:
                self.usage_data[usage_key] = APIUsage(provider, config_name)
            
            # Hangi API tiplerini destekliyor kontrol et
            if config.get('model_text'):
                self.active_providers[APIType.TEXT].append((provider, config_name))
            if config.get('model_tts'):
                self.active_providers[APIType.TTS].append((provider, config_name))
            if config.get('model_image'):
                self.active_providers[APIType.IMAGE].append((provider, config_name))
        
        print(f"✅ API sağlayıcıları yüklendi:")
        for api_type, providers in self.active_providers.items():
            print(f"  {api_type.value}: {len(providers)} sağlayıcı")
    
    def get_available_provider(self, api_type: APIType) -> Optional[Tuple[str, str]]:
        """Belirtilen API tipi için kullanılabilir sağlayıcı döndür"""
        providers = self.active_providers.get(api_type, [])
        
        for provider, config_name in providers:
            usage_key = f"{provider}_{config_name}"
            usage = self.usage_data.get(usage_key)
            
            if not usage or usage.status == APIStatus.ACTIVE:
                # Quota kontrolü
                if self._check_quota(provider, config_name):
                    return provider, config_name
                else:
                    # Quota aşıldı, status güncelle
                    if usage:
                        usage.status = APIStatus.QUOTA_EXCEEDED
                        print(f"⚠️ {provider}_{config_name} quota aşıldı")
        
        print(f"❌ {api_type.value} için kullanılabilir API yok!")
        return None
    
    def _check_quota(self, provider: str, config_name: str) -> bool:
        """API quota kontrolü"""
        config = self.config.get('api_providers', provider, config_name, default={})
        daily_quota = config.get('daily_quota', float('inf'))
        
        usage_key = f"{provider}_{config_name}"
        usage = self.usage_data.get(usage_key)
        
        if not usage:
            return True
        
        return usage.requests_today < daily_quota
    
    def record_usage(self, provider: str, config_name: str, success: bool, error: str = None):
        """API kullanımını kaydet"""
        usage_key = f"{provider}_{config_name}"
        usage = self.usage_data.get(usage_key)
        
        if not usage:
            usage = APIUsage(provider, config_name)
            self.usage_data[usage_key] = usage
        
        usage.requests_today += 1
        usage.last_used = datetime.now()
        
        # Maliyet hesapla
        config = self.config.get('api_providers', provider, config_name, default={})
        cost_per_request = config.get('cost_per_request', 0)
        usage.total_cost_today += cost_per_request
        
        if success:
            usage.status = APIStatus.ACTIVE
            usage.last_error = None
        else:
            usage.last_error = error
            if "quota" in (error or "").lower():
                usage.status = APIStatus.QUOTA_EXCEEDED
            else:
                usage.status = APIStatus.ERROR
        
        self.save_usage_data()
    
    def get_client(self, provider: str, config_name: str):
        """API client'ı lazy loading ile al"""
        client_key = f"{provider}_{config_name}"
        
        if client_key not in self._clients:
            config = self.config.get('api_providers', provider, config_name, default={})
            api_key = os.getenv(config.get('api_key', '').replace('${', '').replace('}', ''))
            
            if provider == 'gemini':
                from google import genai
                self._clients[client_key] = genai.Client(api_key=api_key)
            elif provider == 'openai':
                import openai
                self._clients[client_key] = openai.OpenAI(api_key=api_key)
            elif provider == 'anthropic':
                import anthropic
                self._clients[client_key] = anthropic.Anthropic(api_key=api_key)
        
        return self._clients[client_key]
    
    def make_request(self, api_type: APIType, request_func, max_retries: int = None):
        """Failover ile API isteği yap"""
        if max_retries is None:
            max_retries = self.config.get('failover_ayarlari', 'max_retry_per_api', default=3)
        
        retry_delay = self.config.get('failover_ayarlari', 'retry_delay_seconds', default=5)
        providers = self.active_providers.get(api_type, [])
        
        for provider, config_name in providers:
            print(f"🔄 {api_type.value} isteği: {provider}_{config_name}")
            
            for attempt in range(max_retries):
                try:
                    client = self.get_client(provider, config_name)
                    config = self.config.get('api_providers', provider, config_name, default={})
                    
                    # Request'i yap
                    result = request_func(client, config)
                    
                    # Başarılı
                    self.record_usage(provider, config_name, True)
                    print(f"✅ {provider}_{config_name} başarılı")
                    return result
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ {provider}_{config_name} hata (deneme {attempt+1}): {error_msg}")
                    
                    # Son deneme mi?
                    if attempt == max_retries - 1:
                        self.record_usage(provider, config_name, False, error_msg)
                        break
                    
                    # Bekle ve tekrar dene
                    time.sleep(retry_delay)
            
            print(f"⏭️ {provider}_{config_name} başarısız, sonraki sağlayıcıya geçiliyor...")
        
        raise Exception(f"Tüm {api_type.value} API sağlayıcıları başarısız!")
    
    def get_usage_report(self) -> str:
        """Günlük kullanım raporu"""
        report = "\n📊 GÜNLÜK API KULLANIM RAPORU\n" + "="*50 + "\n"
        
        total_requests = 0
        total_cost = 0.0
        
        for usage_key, usage in self.usage_data.items():
            total_requests += usage.requests_today
            total_cost += usage.total_cost_today
            
            status_emoji = {
                APIStatus.ACTIVE: "✅",
                APIStatus.QUOTA_EXCEEDED: "⚠️", 
                APIStatus.ERROR: "❌",
                APIStatus.DISABLED: "🚫"
            }.get(usage.status, "❓")
            
            report += f"{status_emoji} {usage_key}: {usage.requests_today} istek, ${usage.total_cost_today:.4f}\n"
        
        report += "="*50 + "\n"
        report += f"💰 Toplam: {total_requests} istek, ${total_cost:.4f}\n"
        
        return report

# Global instance
api_manager = None

def get_api_manager():
    global api_manager
    if api_manager is None:
        from config_manager import config
        api_manager = MultiAPIManager(config)
    return api_manager