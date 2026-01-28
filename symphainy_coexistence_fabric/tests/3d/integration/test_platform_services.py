"""
Test Platform Services Integration

Tests that validate platform services work correctly when running.
These tests require the docker-compose services to be running.

Tests:
- Redis connectivity
- ArangoDB connectivity
- Consul connectivity
- Service health checks
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestRedisService:
    """Test Redis service connectivity."""
    
    @pytest.mark.integration
    def test_redis_connection(self):
        """Redis should be accessible."""
        import redis
        
        try:
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            result = client.ping()
            assert result is True, "Redis should respond to ping"
        except redis.ConnectionError as e:
            pytest.skip(f"Redis not available: {e}")
    
    @pytest.mark.integration
    def test_redis_set_get(self):
        """Redis should store and retrieve values."""
        import redis
        
        try:
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.set("test_key", "test_value")
            value = client.get("test_key")
            assert value == "test_value", "Redis should retrieve stored value"
            client.delete("test_key")  # Cleanup
        except redis.ConnectionError as e:
            pytest.skip(f"Redis not available: {e}")


class TestArangoDBService:
    """Test ArangoDB service connectivity."""
    
    @pytest.mark.integration
    def test_arangodb_connection(self):
        """ArangoDB should be accessible."""
        import requests
        
        try:
            response = requests.get(
                "http://localhost:8529/_api/version",
                auth=("root", "test_password"),
                timeout=5
            )
            assert response.status_code == 200, "ArangoDB should respond"
            assert "version" in response.json(), "ArangoDB should return version"
        except requests.exceptions.RequestException as e:
            pytest.skip(f"ArangoDB not available: {e}")


class TestConsulService:
    """Test Consul service connectivity."""
    
    @pytest.mark.integration
    def test_consul_connection(self):
        """Consul should be accessible."""
        import requests
        
        try:
            response = requests.get(
                "http://localhost:8500/v1/status/leader",
                timeout=5
            )
            assert response.status_code == 200, "Consul should respond"
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Consul not available: {e}")


class TestServiceIntegration:
    """Test services work together."""
    
    @pytest.mark.integration
    def test_all_services_accessible(self):
        """All basic services should be accessible."""
        import redis
        import requests
        
        services_ok = []
        
        # Check Redis
        try:
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            services_ok.append("redis")
        except:
            pass
        
        # Check ArangoDB
        try:
            response = requests.get(
                "http://localhost:8529/_api/version",
                auth=("root", "test_password"),
                timeout=5
            )
            if response.status_code == 200:
                services_ok.append("arangodb")
        except:
            pass
        
        # Check Consul
        try:
            response = requests.get(
                "http://localhost:8500/v1/status/leader",
                timeout=5
            )
            if response.status_code == 200:
                services_ok.append("consul")
        except:
            pass
        
        # At least Redis should be available (required for Phase 3)
        assert "redis" in services_ok, "Redis should be available for integration tests"
        
        # Log which services are available
        print(f"\n✅ Available services: {', '.join(services_ok)}")
