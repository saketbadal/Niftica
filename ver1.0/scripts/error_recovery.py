# scripts/error_recovery.py
#!/usr/bin/env python3
"""
Error recovery and system health restoration
"""
import sys
import time
from datetime import datetime
from utils.telegram import send_telegram_message
from scanner.data_fetcher import DataFetcher

class ErrorRecovery:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 60  # seconds
        
    def check_kite_connection(self):
        """Check and restore Kite connection"""
        print("Checking Kite Connect connection...")
        
        for attempt in range(self.max_retries):
            try:
                fetcher = DataFetcher()
                # Try to fetch a known symbol
                ltp = fetcher.get_ltp("NIFTY")
                if ltp:
                    print(f"✅ Kite connection working (NIFTY LTP: {ltp})")
                    return True
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
        
        return False
    
    def check_telegram_bot(self):
        """Check Telegram bot connectivity"""
        print("\nChecking Telegram bot...")
        
        try:
            success = send_telegram_message("🔧 System health check - test message")
            if success:
                print("✅ Telegram bot working")
                return True
            else:
                print("❌ Telegram bot not responding")
                return False
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def check_firestore(self):
        """Check Firestore connectivity"""
        print("\nChecking Firestore...")
        
        try:
            from google.cloud import firestore
            db = firestore.Client()
            
            # Try to read a document
            doc = db.collection('system_config').document('default').get()
            if doc.exists:
                print("✅ Firestore connection working")
                return True
            else:
                print("⚠️  Firestore connected but config not found")
                return True
        except Exception as e:
            print(f"❌ Firestore error: {e}")
            return False
    
    def run_health_check(self):
        """Run complete health check"""
        print(f"\n{'='*50}")
        print(f"System Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        results = {
            'kite': self.check_kite_connection(),
            'telegram': self.check_telegram_bot(),
            'firestore': self.check_firestore()
        }
        
        # Summary
        print(f"\n{'='*50}")
        print("Health Check Summary:")
        
        all_healthy = True
        for service, status in results.items():
            status_emoji = "✅" if status else "❌"
            print(f"{status_emoji} {service.capitalize()}: {'Healthy' if status else 'Failed'}")
            if not status:
                all_healthy = False
        
        if all_healthy:
            print("\n✅ All systems operational!")
            send_telegram_message("✅ System health check passed - all services operational")
        else:
            print("\n⚠️  Some services are failing!")
            failed_services = [s for s, status in results.items() if not status]
            send_telegram_message(
                f"⚠️ System health check failed!\n\n"
                f"Failed services: {', '.join(failed_services)}\n"
                f"Please check logs for details."
            )
        
        return all_healthy

if __name__ == "__main__":
    recovery = ErrorRecovery()
    
    # Check if specific service provided
    if len(sys.argv) > 1:
        service = sys.argv[1].lower()
        if service == 'kite':
            recovery.check_kite_connection()
        elif service == 'telegram':
            recovery.check_telegram_bot()
        elif service == 'firestore':
            recovery.check_firestore()
        else:
            print(f"Unknown service: {service}")
            print("Valid services: kite, telegram, firestore")
    else:
        # Run full health check
        recovery.run_health_check()