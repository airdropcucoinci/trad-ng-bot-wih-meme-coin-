#!/usr/bin/env python3
"""
Daemon Runner
=============
Trading daemon'u başlatma scripti.
"""

import argparse
import yaml
import logging
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from daemon.trading_daemon import TradingDaemon

def setup_logging(log_level: str = "INFO", log_file: str = "output/daemon.log"):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    parser = argparse.ArgumentParser(description='HybridTrader Daemon')
    parser.add_argument('--config', default='config/settings.yaml', help='Config dosyası')
    parser.add_argument('--mode', default='daemon', choices=['daemon', 'once'], 
                       help='Çalışma modu: daemon (sürekli) veya once (tek sefer)')
    parser.add_argument('--report-mode', default='none', 
                       choices=['none', 'hourly_email', 'telegram_4h'],
                       help='Rapor modu (GitHub Actions için)')
    
    args = parser.parse_args()
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config dosyası bulunamadı: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    setup_logging(
        config.get('general', {}).get('log_level', 'INFO'),
        config.get('daemon', {}).get('log_file', 'output/daemon.log')
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"HybridTrader v2 başlatılıyor... Mod: {args.mode}")
    
    daemon = TradingDaemon(config)
    
    if args.mode == 'daemon':
        daemon.start()
    elif args.mode == 'once':
        logger.info("Tek seferlik analiz modu...")
        daemon._run_cycle()
        
        if args.report_mode == 'hourly_email':
            daemon._send_email_report()
        elif args.report_mode == 'telegram_4h':
            daemon._send_telegram_summary()

if __name__ == "__main__":
    main()
