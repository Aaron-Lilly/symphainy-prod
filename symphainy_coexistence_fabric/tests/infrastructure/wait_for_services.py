#!/usr/bin/env python3
"""
Wait for Services - Health Check Script

Waits for all test services to be healthy before running tests.
"""

import sys
import time
import requests
from typing import Dict, List

SERVICES = {
    "redis": {"url": "http://localhost:6379", "type": "tcp"},
    "arangodb": {"url": "http://localhost:8529/_api/version", "type": "http", "auth": ("root", "test_password")},
    "consul": {"url": "http://localhost:8500/v1/status/leader", "type": "http"},
    "runtime": {"url": "http://localhost:8000/health", "type": "http", "optional": True},
    "experience": {"url": "http://localhost:8001/health", "type": "http", "optional": True},
}

MAX_WAIT_SECONDS = 120
CHECK_INTERVAL = 5


def check_http_service(name: str, url: str, auth: tuple = None) -> bool:
    """Check if HTTP service is healthy."""
    try:
        response = requests.get(url, timeout=5, auth=auth)
        if response.status_code < 400:
            print(f"  ✅ {name} is healthy")
            return True
        else:
            print(f"  ⏳ {name} returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ⏳ {name} not ready: {e}")
        return False


def check_tcp_service(name: str, url: str) -> bool:
    """Check if TCP service is accepting connections."""
    import socket
    
    # Parse host:port from URL
    host = "localhost"
    port = int(url.split(":")[-1])
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"  ✅ {name} is healthy")
            return True
        else:
            print(f"  ⏳ {name} not ready")
            return False
    except Exception as e:
        print(f"  ⏳ {name} not ready: {e}")
        return False


def wait_for_services(services: Dict) -> bool:
    """Wait for all services to be healthy."""
    print("🔍 Waiting for services to be healthy...")
    
    start_time = time.time()
    
    while time.time() - start_time < MAX_WAIT_SECONDS:
        all_healthy = True
        
        for name, config in services.items():
            service_type = config.get("type", "http")
            url = config["url"]
            auth = config.get("auth")
            is_optional = config.get("optional", False)
            
            if service_type == "http":
                healthy = check_http_service(name, url, auth=auth)
            else:
                healthy = check_tcp_service(name, url)
            
            if not healthy:
                if is_optional:
                    print(f"  ⚠️  {name} is optional, skipping")
                else:
                    all_healthy = False
        
        if all_healthy:
            print("\n✅ All services are healthy!")
            return True
        
        print(f"\n⏳ Waiting {CHECK_INTERVAL}s before next check...")
        time.sleep(CHECK_INTERVAL)
    
    print(f"\n❌ Timeout waiting for services after {MAX_WAIT_SECONDS}s")
    return False


if __name__ == "__main__":
    success = wait_for_services(SERVICES)
    sys.exit(0 if success else 1)
