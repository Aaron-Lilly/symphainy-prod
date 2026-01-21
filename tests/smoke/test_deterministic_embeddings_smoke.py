"""
Smoke Test: Deterministic Embeddings

Quick validation that deterministic embedding service works.
"""

import pytest
from typing import Dict, Any

from symphainy_platform.realms.content.enabling_services.deterministic_embedding_service import DeterministicEmbeddingService
from symphainy_platform.runtime.execution_context import ExecutionContext


@pytest.mark.asyncio
@pytest.mark.smoke
class TestDeterministicEmbeddingsSmoke:
    """Smoke tests for deterministic embeddings."""
    
    async def test_deterministic_embedding_service_initialization(self):
        """Test service initialization."""
        service = DeterministicEmbeddingService(public_works=None)
        assert service is not None
        assert hasattr(service, 'create_deterministic_embeddings')
    
    async def test_schema_fingerprint_creation(self):
        """Test schema fingerprint creation."""
        service = DeterministicEmbeddingService(public_works=None)
        
        # Create test schema
        schema = [
            {"name": "policy_number", "type": "string", "position": 0, "nullable": False},
            {"name": "premium", "type": "float", "position": 1, "nullable": True},
            {"name": "coverage_type", "type": "string", "position": 2, "nullable": False}
        ]
        
        fingerprint = service._create_schema_fingerprint(schema)
        
        assert fingerprint is not None
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hex length
        
        # Same schema should produce same fingerprint
        fingerprint2 = service._create_schema_fingerprint(schema)
        assert fingerprint == fingerprint2
    
    async def test_pattern_signature_creation(self):
        """Test pattern signature creation."""
        service = DeterministicEmbeddingService(public_works=None)
        
        # Create test parsed content
        parsed_content = {
            "data": [
                {"policy_number": "POL001", "premium": 1000.0, "coverage_type": "life"},
                {"policy_number": "POL002", "premium": 2000.0, "coverage_type": "life"},
                {"policy_number": "POL003", "premium": 1500.0, "coverage_type": "health"}
            ],
            "metadata": {
                "columns": [
                    {"name": "policy_number", "type": "string"},
                    {"name": "premium", "type": "float"},
                    {"name": "coverage_type", "type": "string"}
                ]
            }
        }
        
        schema = service._extract_schema(parsed_content)
        signature = await service._create_pattern_signature(parsed_content, schema)
        
        assert signature is not None
        assert isinstance(signature, dict)
        assert "policy_number" in signature
        assert "premium" in signature
        assert "coverage_type" in signature
        
        # Validate signature structure
        policy_sig = signature["policy_number"]
        assert "type" in policy_sig
        assert "total_count" in policy_sig
        assert policy_sig["total_count"] == 3
        
        premium_sig = signature["premium"]
        assert "min" in premium_sig
        assert "max" in premium_sig
        assert "mean" in premium_sig
        assert premium_sig["min"] == 1000.0
        assert premium_sig["max"] == 2000.0
