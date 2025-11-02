# scripts/monitor_health.py
#!/usr/bin/env python3
"""
Health monitoring script for the recommendation system
"""
import requests
import time
from datetime import datetime

def check_health(service_url):
    """Check service health"""
    try:
        response = requests.get(f"{service_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service is {data['status']} at {data['time']}")
            print(f"   Market: {data.get('market', 'unknown')}")
            print(f"   Monitoring: {data.get('monitoring', 0)} symbols")
            print(f"   Active positions: {data.get('positions', 0)}")
            return True
        else:
            print(f"❌ Service returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False

def monitor_continuously(service_url, interval=300):
    """Monitor service health continuously"""
    print(f"Starting health monitoring for {service_url}")
    print(f"Checking every {interval} seconds...")
    
    consecutive_failures = 0
    
    while True:
        try:
            success = check_health(service_url)
            
            if success:
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                
                if consecutive_failures >= 3:
                    print(f"⚠️ ALERT: Service has failed {consecutive_failures} consecutive health checks!")
                    # Here you could send alerts via email/SMS
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python monitor_health.py <service_url>")
        print("Example: python monitor_health.py https://your-service.run.app")
        sys.exit(1)
    
    service_url = sys.argv[1]
    monitor_continuously(service_url)