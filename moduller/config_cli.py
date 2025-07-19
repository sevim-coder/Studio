import argparse
import sys
import os

# Path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config_manager import ConfigManager

def main():
    parser = argparse.ArgumentParser(description="Config Yönetici")
    parser.add_argument('--get', help='Config değeri alma: sistem_ayarlari.log_dosyasi')
    parser.add_argument('--set', nargs=2, help='Config değeri set etme: key value')
    parser.add_argument('--add-task', nargs=4, help='Günlük görev ekleme: gun kanal konu harf_sayisi')
    
    args = parser.parse_args()
    config_manager = ConfigManager()
    
    if args.get:
        path = args.get.split('.')
        value = config_manager.get(*path)
        print(f"{args.get}: {value}")
    
    elif args.set:
        # Implement set functionality
        pass
    
    elif args.add_task:
        gun, kanal, konu, harf_sayisi = args.add_task
        config_manager.update_daily_task(gun, kanal, konu, int(harf_sayisi))

if __name__ == "__main__":
    main()
