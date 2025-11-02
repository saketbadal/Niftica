
### **27. Final Testing Script**

```python
# tests/integration_test.py
#!/usr/bin/env python3
"""
Integration tests for the complete system
"""
import pytest
import requests
import time
from datetime import datetime
from utils.telegram import send_telegram_message

class TestIntegration:
    
    @pytest.fixture
    def service_url(self):
        """Get service URL from environment or use localhost"""
        import os
        return os.getenv('SERVICE_URL', 'http://localhost:8080')
    
    def test_health_endpoint(self, service_url):
        """Test health endpoint"""
        response = requests.get(f"{service_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_status_endpoint(self, service_url):
        """Test status endpoint"""
        response = requests.get(f"{service_url}/status")
        assert response.status_code == 200
        data = response.json()
        assert 'market_open' in data
    
    def test_metrics_endpoint(self, service_url):
        """Test metrics endpoint"""
        response = requests.get(f"{service_url}/metrics")
        assert response.status_code == 200
        data = response.json()
        assert 'daily' in data
        assert 'weekly' in data
    
    def test_telegram_webhook(self, service_url):
        """Test Telegram webhook"""
        webhook_data = {
            'message': {
                'chat': {'id': '12345'},
                'text': '/help'
            }
        }
        
        response = requests.post(
            f"{service_url}/telegram-webhook",
            json=webhook_data
        )
        assert response.status_code == 200

def run_integration_tests(service_url):
    """Run all integration tests"""
    print(f"Running integration tests against: {service_url}")
    print("-" * 50)
    
    tests = TestIntegration()
    
    # Test 1: Health check
    print("Testing health endpoint...", end=" ")
    try:
        tests.test_health_endpoint(service_url)
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 2: Status
    print("Testing status endpoint...", end=" ")
    try:
        tests.test_status_endpoint(service_url)
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 3: Metrics
    print("Testing metrics endpoint...", end=" ")
    try:
        tests.test_metrics_endpoint(service_url)
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 4: Telegram webhook
    print("Testing Telegram webhook...", end=" ")
    try:
        tests.test_telegram_webhook(service_url)
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    print("-" * 50)
    print("Integration tests completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        service_url = sys.argv[1]
    else:
        service_url = "http://localhost:8080"
    
    run_integration_tests(service_url)