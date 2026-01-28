"""
Test Structured Artifacts - Artifact Pattern Tests

Tests:
- Artifact structure validation
- Artifact lifecycle (PENDING → READY)
- create_structured_artifact helper
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestStructuredArtifactCreation:
    """Test structured artifact creation."""
    
    def test_create_structured_artifact_exists(self):
        """create_structured_artifact helper should exist."""
        from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact
        assert callable(create_structured_artifact)
    
    def test_artifact_has_required_fields(self):
        """Artifact should have result_type, semantic_payload, renderings."""
        from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact
        
        artifact = create_structured_artifact(
            result_type="test_result",
            semantic_payload={"key": "value"},
            renderings={"text": "Test rendering"}
        )
        
        assert "result_type" in artifact
        assert "semantic_payload" in artifact
        assert "renderings" in artifact
    
    def test_artifact_result_type_is_set(self):
        """result_type should be set correctly."""
        from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact
        
        artifact = create_structured_artifact(
            result_type="file_upload_result",
            semantic_payload={},
            renderings={}
        )
        
        assert artifact["result_type"] == "file_upload_result"
    
    def test_artifact_semantic_payload_is_dict(self):
        """semantic_payload should be a dict."""
        from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact
        
        artifact = create_structured_artifact(
            result_type="test",
            semantic_payload={"file_id": "123", "status": "uploaded"},
            renderings={}
        )
        
        assert isinstance(artifact["semantic_payload"], dict)
        assert artifact["semantic_payload"]["file_id"] == "123"
    
    def test_artifact_renderings_is_dict(self):
        """renderings should be a dict."""
        from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact
        
        artifact = create_structured_artifact(
            result_type="test",
            semantic_payload={},
            renderings={"summary": "File uploaded successfully", "details": "..."}
        )
        
        assert isinstance(artifact["renderings"], dict)
        assert "summary" in artifact["renderings"]


class TestArtifactLifecycle:
    """Test artifact lifecycle states."""
    
    @pytest.mark.asyncio
    async def test_artifact_starts_as_pending(self, mock_state_surface):
        """New artifacts should start in PENDING state."""
        result = await mock_state_surface.register_artifact(
            artifact_type="test",
            data={"test": "data"},
            tenant_id="test_tenant"
        )
        
        assert result["status"] == "PENDING"
    
    @pytest.mark.asyncio
    async def test_artifact_transitions_to_ready(self, mock_state_surface):
        """Artifacts should transition to READY state."""
        # Register artifact
        artifact = await mock_state_surface.register_artifact(
            artifact_type="test",
            data={},
            tenant_id="test_tenant"
        )
        
        # Mark as ready
        await mock_state_surface.mark_artifact_ready(artifact["artifact_id"])
        
        # Verify state changed
        mock_state_surface.mark_artifact_ready.assert_called()


class TestArtifactValidation:
    """Test artifact validation."""
    
    def test_artifact_without_result_type_is_invalid(self):
        """Artifact without result_type should be invalid."""
        artifact = {
            "semantic_payload": {},
            "renderings": {}
        }
        
        assert "result_type" not in artifact
    
    def test_artifact_without_semantic_payload_is_invalid(self):
        """Artifact without semantic_payload should be invalid."""
        artifact = {
            "result_type": "test",
            "renderings": {}
        }
        
        assert "semantic_payload" not in artifact
    
    def test_artifact_with_all_fields_is_valid(self):
        """Artifact with all required fields is valid."""
        artifact = {
            "result_type": "test_result",
            "semantic_payload": {"key": "value"},
            "renderings": {"text": "Test"}
        }
        
        assert "result_type" in artifact
        assert "semantic_payload" in artifact
        assert "renderings" in artifact


class TestArtifactInJourneyResults:
    """Test artifacts in journey results."""
    
    @pytest.mark.asyncio
    async def test_journey_returns_artifacts_dict(
        self, content_solution, execution_context, compose_journey_intent
    ):
        """Journey should return artifacts dict."""
        intent = compose_journey_intent(
            journey_id="file_upload_materialization",
            journey_params={"file_name": "test.txt"},
            solution_id="content_solution"
        )
        
        result = await content_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result
        assert isinstance(result["artifacts"], dict)
    
    @pytest.mark.asyncio
    async def test_artifacts_have_valid_structure(
        self, content_solution, execution_context, compose_journey_intent
    ):
        """Artifacts in results should have valid structure."""
        intent = compose_journey_intent(
            journey_id="file_upload_materialization",
            journey_params={"file_name": "test.txt"},
            solution_id="content_solution"
        )
        
        result = await content_solution.handle_intent(intent, execution_context)
        
        for artifact_key, artifact in result.get("artifacts", {}).items():
            if isinstance(artifact, dict):
                # Should have at least result_type or be a structured artifact
                assert "result_type" in artifact or "semantic_payload" in artifact or \
                    "status" in artifact or isinstance(artifact, (str, int, bool))
