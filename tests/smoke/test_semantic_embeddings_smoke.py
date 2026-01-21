"""
Smoke Test: Semantic Embeddings

Quick validation that semantic embedding service works.
"""

import pytest
from typing import Dict, Any

from symphainy_platform.realms.content.enabling_services.embedding_service import EmbeddingService


@pytest.mark.asyncio
@pytest.mark.smoke
class TestSemanticEmbeddingsSmoke:
    """Smoke tests for semantic embeddings."""
    
    async def test_embedding_service_initialization(self):
        """Test service initialization."""
        service = EmbeddingService(public_works=None)
        assert service is not None
        assert hasattr(service, 'create_semantic_embeddings')
    
    async def test_representative_sampling(self):
        """Test representative sampling logic."""
        service = EmbeddingService(public_works=None)
        
        # Create test parsed content
        parsed_content = {
            "data": [
                {"col1": f"value_{i}", "col2": i} for i in range(100)
            ]
        }
        
        # Sample every 10th row
        sampled = service._sample_representative(parsed_content, n=10)
        
        assert len(sampled) == 10  # 0, 10, 20, ..., 90
        assert sampled[0]["col2"] == 0
        assert sampled[1]["col2"] == 10
        assert sampled[9]["col2"] == 90
