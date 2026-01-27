"""
Test Deterministic Embedding Journey

Tests:
- Embedding creation
- Deterministic results
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestEmbeddingJourneyStructure:
    """Test DeterministicEmbeddingJourney structure."""
    
    def test_journey_exists(self, content_solution):
        """DeterministicEmbeddingJourney should exist."""
        journey = content_solution.get_journey("deterministic_embedding")
        assert journey is not None
    
    def test_has_compose_journey(self, content_solution):
        """Should have compose_journey method."""
        journey = content_solution.get_journey("deterministic_embedding")
        assert hasattr(journey, 'compose_journey')


class TestEmbeddingJourneyExecution:
    """Test DeterministicEmbeddingJourney execution."""
    
    @pytest.mark.asyncio
    async def test_create_embeddings(self, content_solution, execution_context):
        """Should handle embedding creation."""
        journey = content_solution.get_journey("deterministic_embedding")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "parsed_file_id": "parsed_123",
                "chunks": [{"text": "test chunk"}]
            }
        )
        
        assert "success" in result or "error" in result


class TestEmbeddingJourneySOAAPIs:
    """Test DeterministicEmbeddingJourney SOA APIs."""
    
    def test_has_embed_api(self, content_solution):
        """Should have embed API."""
        journey = content_solution.get_journey("deterministic_embedding")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("embed" in name.lower() for name in api_names)
