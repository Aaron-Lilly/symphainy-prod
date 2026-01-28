"""
Test Real Infrastructure Connectivity - SRE Tests

Validates that platform can actually connect to and use real infrastructure.
"""
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestRealRedisConnectivity:
    """Test real Redis connectivity and operations."""
    
    @pytest.mark.real_infrastructure
    @pytest.mark.sre
    def test_redis_connection(self, real_redis_client):
        """Redis should be accessible."""
        result = real_redis_client.ping()
        assert result is True
    
    @pytest.mark.real_infrastructure
    @pytest.mark.sre
    def test_redis_set_get(self, real_redis_client):
        """Redis should store and retrieve values."""
        real_redis_client.set("test_key_real", "test_value_real", ex=60)
        value = real_redis_client.get("test_key_real")
        assert value == "test_value_real"
        real_redis_client.delete("test_key_real")


class TestRealArangoDBConnectivity:
    """Test real ArangoDB connectivity and operations."""
    
    @pytest.mark.real_infrastructure
    @pytest.mark.sre
    def test_arangodb_connection(self, real_arangodb_client):
        """ArangoDB should be accessible."""
        assert real_arangodb_client is not None
    
    @pytest.mark.real_infrastructure
    @pytest.mark.sre
    def test_arangodb_create_read(self, real_arangodb_client):
        """ArangoDB should create and read documents."""
        collection_name = "test_real_docs"
        if not real_arangodb_client.has_collection(collection_name):
            real_arangodb_client.create_collection(collection_name)
        document = {"_key": "test_doc_real", "name": "Test", "value": 123}
        result = real_arangodb_client.insert_document(collection_name, document)
        assert result is not None
        retrieved = real_arangodb_client.get_document(collection_name, "test_doc_real")
        assert retrieved["name"] == "Test"
        real_arangodb_client.delete_document(collection_name, "test_doc_real")
