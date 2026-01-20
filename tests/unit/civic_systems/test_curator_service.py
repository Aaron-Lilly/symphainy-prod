"""
Unit tests for Curator Service - Platform DNA Promotion.

Tests the promotion workflow from Purpose-Bound Outcome to Platform DNA.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from symphainy_platform.civic_systems.smart_city.services.curator_service import CuratorService
from symphainy_platform.civic_systems.smart_city.primitives.curator_primitives import PromotionValidation


@pytest.mark.unit
@pytest.mark.civic_systems
class TestCuratorService:
    """Test Curator Service promotion to Platform DNA."""
    
    @pytest.fixture
    def mock_supabase_adapter(self):
        """Mock Supabase adapter."""
        adapter = Mock()
        adapter.service_client = Mock()
        adapter.service_client.table = Mock(return_value=Mock())
        return adapter
    
    @pytest.fixture
    def mock_artifact_plane(self):
        """Mock Artifact Plane."""
        plane = Mock()
        plane.get_artifact = AsyncMock(return_value=None)
        return plane
    
    @pytest.fixture
    def mock_curator_primitives(self):
        """Mock Curator Primitives."""
        primitives = Mock()
        primitives.validate_promotion = AsyncMock(return_value=PromotionValidation(
            is_allowed=True,
            registry_type="solution",
            reason="Promotion allowed",
            policy_basis="mvp_permissive_policy"
        ))
        return primitives
    
    @pytest.fixture
    def curator_service(self, mock_supabase_adapter, mock_artifact_plane, mock_curator_primitives):
        """Create CuratorService instance with mocked dependencies."""
        return CuratorService(
            supabase_adapter=mock_supabase_adapter,
            artifact_plane=mock_artifact_plane,
            curator_primitives=mock_curator_primitives
        )
    
    @pytest.mark.asyncio
    async def test_promote_to_platform_dna_solution(
        self, curator_service, mock_supabase_adapter, mock_artifact_plane
    ):
        """Test promoting solution artifact to Platform DNA."""
        # Mock artifact retrieval
        mock_artifact = {
            "artifact_id": "artifact_123",
            "tenant_id": "tenant_123",
            "artifact_type": "blueprint",
            "lifecycle_state": "accepted",
            "payload": {
                "semantic_payload": {
                    "blueprint_id": "blueprint_123",
                    "components": {"component1": "value1"}
                }
            }
        }
        mock_artifact_plane.get_artifact.return_value = mock_artifact
        
        # Mock registry entry creation
        mock_table = Mock()
        mock_insert = Mock()
        mock_insert.execute.return_value = Mock(
            data=[{
                "registry_id": "registry_123"
            }]
        )
        mock_table.insert.return_value = mock_insert
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        registry_id = await curator_service.promote_to_platform_dna(
            artifact_id="artifact_123",
            tenant_id="tenant_123",
            registry_type="solution",
            registry_name="Test Solution",
            promoted_by="curator_123"
        )
        
        assert registry_id == "registry_123"
        assert mock_table.insert.called
    
    @pytest.mark.asyncio
    async def test_promote_to_platform_dna_validation_fails_draft(
        self, curator_service, mock_artifact_plane, mock_curator_primitives
    ):
        """Test that promotion fails if artifact is not in 'accepted' state."""
        # Mock artifact in draft state
        mock_artifact = {
            "artifact_id": "artifact_123",
            "lifecycle_state": "draft",  # Not accepted
            "artifact_type": "blueprint"
        }
        mock_artifact_plane.get_artifact.return_value = mock_artifact
        
        # Mock primitives to reject draft state
        mock_curator_primitives.validate_promotion.return_value = PromotionValidation(
            is_allowed=False,
            registry_type="solution",
            reason="Artifact must be in 'accepted' state",
            policy_basis="lifecycle_state_policy"
        )
        
        registry_id = await curator_service.promote_to_platform_dna(
            artifact_id="artifact_123",
            tenant_id="tenant_123",
            registry_type="solution",
            registry_name="Test Solution"
        )
        
        assert registry_id is None
    
    @pytest.mark.asyncio
    async def test_promote_to_platform_dna_validation_fails_wrong_type(
        self, curator_service, mock_artifact_plane, mock_curator_primitives
    ):
        """Test that promotion fails if artifact type doesn't match registry type."""
        # Mock artifact with wrong type
        mock_artifact = {
            "artifact_id": "artifact_123",
            "lifecycle_state": "accepted",
            "artifact_type": "sop"  # Cannot be promoted to solution registry
        }
        mock_artifact_plane.get_artifact.return_value = mock_artifact
        
        # Mock primitives to reject wrong type
        mock_curator_primitives.validate_promotion.return_value = PromotionValidation(
            is_allowed=False,
            registry_type="solution",
            reason="Artifact type 'sop' cannot be promoted to solution registry",
            policy_basis="artifact_type_policy"
        )
        
        registry_id = await curator_service.promote_to_platform_dna(
            artifact_id="artifact_123",
            tenant_id="tenant_123",
            registry_type="solution",
            registry_name="Test Solution"
        )
        
        assert registry_id is None
    
    @pytest.mark.asyncio
    async def test_generalize_outcome_removes_client_context(
        self, curator_service
    ):
        """Test that generalization removes client-specific context."""
        test_data = {
            "blueprint_id": "blueprint_123",
            "tenant_id": "tenant_123",  # Should be removed
            "user_id": "user_123",  # Should be removed
            "session_id": "session_123",  # Should be removed
            "components": {
                "component1": "value1",
                "client_name": "Client Corp"  # Should be removed
            }
        }
        
        generalized = curator_service._remove_client_context(test_data)
        
        assert "tenant_id" not in generalized
        assert "user_id" not in generalized
        assert "session_id" not in generalized
        assert "blueprint_id" in generalized  # Should be kept
        assert "components" in generalized
        assert "client_name" not in generalized.get("components", {})
    
    @pytest.mark.asyncio
    async def test_promote_to_platform_dna_intent(
        self, curator_service, mock_supabase_adapter, mock_artifact_plane
    ):
        """Test promoting intent artifact to Platform DNA."""
        # Mock artifact
        mock_artifact = {
            "artifact_id": "artifact_456",
            "tenant_id": "tenant_123",
            "artifact_type": "workflow",
            "lifecycle_state": "accepted",
            "payload": {
                "semantic_payload": {
                    "workflow_id": "workflow_456",
                    "steps": ["step1", "step2"]
                }
            }
        }
        mock_artifact_plane.get_artifact.return_value = mock_artifact
        
        # Mock registry entry creation
        mock_table = Mock()
        mock_insert = Mock()
        mock_insert.execute.return_value = Mock(
            data=[{
                "registry_id": "intent_registry_123"
            }]
        )
        mock_table.insert.return_value = mock_insert
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        registry_id = await curator_service.promote_to_platform_dna(
            artifact_id="artifact_456",
            tenant_id="tenant_123",
            registry_type="intent",
            registry_name="Test Intent",
            promoted_by="curator_123"
        )
        
        assert registry_id == "intent_registry_123"
    
    @pytest.mark.asyncio
    async def test_promote_to_platform_dna_no_artifact_plane(
        self, curator_service
    ):
        """Test that promotion fails if Artifact Plane not available."""
        curator_service.artifact_plane = None
        
        registry_id = await curator_service.promote_to_platform_dna(
            artifact_id="artifact_123",
            tenant_id="tenant_123",
            registry_type="solution",
            registry_name="Test Solution"
        )
        
        assert registry_id is None
    
    @pytest.mark.asyncio
    async def test_promote_to_platform_dna_invalid_registry_type(
        self, curator_service
    ):
        """Test that promotion fails for invalid registry type."""
        registry_id = await curator_service.promote_to_platform_dna(
            artifact_id="artifact_123",
            tenant_id="tenant_123",
            registry_type="invalid_type",
            registry_name="Test"
        )
        
        assert registry_id is None
