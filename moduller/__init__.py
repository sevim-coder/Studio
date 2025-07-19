# moduller package - AI Video Studio Modules
"""
AI Video Studio modüllerini içeren package.

Modüller:
- senarist_multiapi: Google/Gemini API ile senaryo üretimi
- gorsel_yonetmen_multiapi: Imagen API ile görsel üretimi  
- seslendirmen_multiapi: Google TTS ile ses üretimi
- kurgu: FFmpeg ile video kurgu
- yonetmen: Video prodüksiyon yönetimi
- youtube_uploader: YouTube yükleme
"""

__version__ = "1.0.0"
__author__ = "AI Video Studio"

# Modül listesi
__all__ = [
    'senarist_multiapi',
    'gorsel_yonetmen_multiapi', 
    'seslendirmen_multiapi',
    'kurgu',
    'yonetmen',
    'youtube_uploader',
    'config_cli'
]