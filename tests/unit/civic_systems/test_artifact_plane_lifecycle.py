"""
Unit tests for Artifact Plane lifecycle state transitions.

Tests lifecycle state management:
- Creating artifacts with lifecycle states
- Transitioning between states
- Validating transitions
- Recording transition audit trail
"""

import pytest
from unittest.mock import Mock, AsyncMock
from symphainy_platform.civic_systems.artifact_plane.artifact_plane import ArtifactPlane
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent import Intent


@pytest.mark.unit
@pytest.mark.civic_systems
class TestArtifactPlaneLifecycle:
    """Test Artifact Plane lifecycle state transitions."""
    
    @pytest.fixture
    def mock_artifact_storage(self):
        """Mock artifact storage protocol."""
        storage = Mock()
        storage.store_artifact = AsyncMock(return_value={
            "success": True,
            "artifact_id": "test_artifact_123",
            "storage_path": "gs://bucket/test_artifact_123"
        })
        storage.get_artifact = AsyncMock(return_value={"data": "test_payload"})
        return storage
    
    @pytest.fixture
    def mock_state_management(self):
        """Mock state management protocol."""
        state_mgmt = Mock()
        state_mgmt.store_state = AsyncMock(return_value=True)
        state_mgmt.retrieve_state = AsyncMock(return_value=None)
        return state_mgmt
    
    @pytest.fixture
    def artifact_plane(self, mock_artifact_storage, mock_state_management):
        """Create ArtifactPlane instance with mocked dependencies."""
        return ArtifactPlane(
            artifact_storage=mock_artifact_storage,
            state_management=mock_state_management
        )
    
    @pytest.fixture
    def execution_context(self):
        """Create execution context for testing."""
        intent = Intent(
            intent_type="generate_roadmap",
            intent_id="intent_123",
            tenant_id="tenant_123"
        )
        context = ExecutionContext(
            intent=intent,
            tenant_id="tenant_123",
            session_id="session_123",
            solution_id="solution_123",
            execution_id="exec_123"
        )
        return context
    
    @pytest.mark.asyncio
    async def test_create_artifact_with_lifecycle_state(self, artifact_plane, execution_context):
        """Test creating artifact with lifecycle state."""
        result = await artifact_plane.create_artifact(
            artifact_type="roadmap",
            artifact_id=None,
            payload={"data": "test"},
            context=execution_context,
            lifecycle_state="draft",
            owner="client",
            purpose="delivery"
        )
        
        assert result is not None
        assert "artifact_id" in result
        
        # Verify state_management.store_state was called with lifecycle fields
        call_args = artifact_plane.state_management.store_state.call_args
        assert call_args is not None
        state_data = call_args.kwargs.get("state_data", {})
        assert state_data.get("lifecycle_state") == "draft"
        assert state_data.get("owner") == "client"
        assert state_data.get("purpose") == "delivery"
        assert state_data.get("lifecycle_transitions") == []
    
    @pytest.mark.asyncio
    async def test_create_artifact_default_lifecycle_state(self, artifact_plane, execution_context):
        """Test creating artifact with default lifecycle state (draft)."""
        result = await artifact_plane.create_artifact(
            artifact_type="roadmap",
            artifact_id=None,
            payload={"data": "test"},
            context=execution_context
        )
        
        assert result is not None
        
        # Verify default lifecycle state
        call_args = artifact_plane.state_management.store_state.call_args
        state_data = call_args.kwargs.get("state_data", {})
        assert state_data.get("lifecycle_state") == "draft"
        assert state_data.get("owner") == "client"
        assert state_data.get("purpose") == "delivery"
    
    @pytest.mark.asyncio
    async def test_create_artifact_invalid_lifecycle_state(self, artifact_plane, execution_context):
        """Test creating artifact with invalid lifecycle state raises error."""
        with pytest.raises(ValueError, match="Invalid lifecycle_state"):
            await artifact_plane.create_artifact(
                artifact_type="roadmap",
                artifact_id=None,
                payload={"data": "test"},
                context=execution_context,
                lifecycle_state="invalid_state"
            )
    
    @pytest.mark.asyncio
    async def test_create_artifact_invalid_owner(self, artifact_plane, execution_context):
        """Test creating artifact with invalid owner raises error."""
        with pytest.raises(ValueError, match="Invalid owner"):
            await artifact_plane.create_artifact(
                artifact_type="roadmap",
                artifact_id=None,
                payload={"data": "test"},
                context=execution_context,
                owner="invalid_owner"
            )
    
    @pytest.mark.asyncio
    async def test_create_artifact_invalid_purpose(self, artifact_plane, execution_context):
        """Test creating artifact with invalid purpose raises error."""
        with pytest.raises(ValueError, match="Invalid purpose"):
            await artifact_plane.create_artifact(
                artifact_type="roadmap",
                artifact_id=None,
                payload={"data": "test"},
                context=execution_context,
                purpose="invalid_purpose"
            )
    
    @pytest.mark.asyncio
    async def test_transition_lifecycle_state_draft_to_accepted(self, artifact_plane, mock_state_management):
        """Test transitioning artifact from draft to accepted."""
        # Setup: Mock existing artifact in draft state
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "draft",
            "lifecycle_transitions": []
        })
        
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            new_state="accepted",
            transitioned_by="user_123",
            reason="Artifact approved"
        )
        
        assert result is True
        
        # Verify state was updated
        call_args = mock_state_management.store_state.call_args
        state_data = call_args.kwargs.get("state_data", {})
        assert state_data.get("lifecycle_state") == "accepted"
        
        # Verify transition was recorded
        transitions = state_data.get("lifecycle_transitions", [])
        assert len(transitions) == 1
        assert transitions[0]["from_state"] == "draft"
        assert transitions[0]["to_state"] == "accepted"
        assert transitions[0]["transitioned_by"] == "user_123"
        assert transitions[0]["reason"] == "Artifact approved"
    
    @pytest.mark.asyncio
    async def test_transition_lifecycle_state_draft_to_obsolete(self, artifact_plane, mock_state_management):
        """Test transitioning artifact from draft to obsolete."""
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "draft",
            "lifecycle_transitions": []
        })
        
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            new_state="obsolete"
        )
        
        assert result is True
        
        call_args = mock_state_management.store_state.call_args
        state_data = call_args.kwargs.get("state_data", {})
        assert state_data.get("lifecycle_state") == "obsolete"
    
    @pytest.mark.asyncio
    async def test_transition_lifecycle_state_accepted_to_obsolete(self, artifact_plane, mock_state_management):
        """Test transitioning artifact from accepted to obsolete."""
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "accepted",
            "lifecycle_transitions": []
        })
        
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            new_state="obsolete"
        )
        
        assert result is True
        
        call_args = mock_state_management.store_state.call_args
        state_data = call_args.kwargs.get("state_data", {})
        assert state_data.get("lifecycle_state") == "obsolete"
    
    @pytest.mark.asyncio
    async def test_transition_lifecycle_state_invalid_transition(self, artifact_plane, mock_state_management):
        """Test that invalid transitions are rejected."""
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "accepted",
            "lifecycle_transitions": []
        })
        
        # Cannot transition from accepted back to draft
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            new_state="draft"
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_transition_lifecycle_state_obsolete_is_terminal(self, artifact_plane, mock_state_management):
        """Test that obsolete is a terminal state (no transitions allowed)."""
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "obsolete",
            "lifecycle_transitions": []
        })
        
        # Cannot transition from obsolete to any other state
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            new_state="accepted"
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_transition_lifecycle_state_idempotent(self, artifact_plane, mock_state_management):
        """Test that transitioning to the same state is idempotent."""
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "draft",
            "lifecycle_transitions": []
        })
        
        # Transition to same state should succeed (idempotent)
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            new_state="draft"
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_transition_lifecycle_state_artifact_not_found(self, artifact_plane, mock_state_management):
        """Test that transitioning non-existent artifact returns False."""
        mock_state_management.retrieve_state = AsyncMock(return_value=None)
        
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="nonexistent_artifact",
            tenant_id="tenant_123",
            new_state="accepted"
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_transition_lifecycle_state_invalid_state(self, artifact_plane, mock_state_management):
        """Test that invalid new_state is rejected."""
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "draft",
            "lifecycle_transitions": []
        })
        
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            new_state="invalid_state"
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_transition_lifecycle_state_multiple_transitions(self, artifact_plane, mock_state_management):
        """Test that multiple transitions are recorded in audit trail."""
        # Setup: Artifact with existing transitions
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "accepted",
            "lifecycle_transitions": [
                {
                    "from_state": "draft",
                    "to_state": "accepted",
                    "transitioned_at": "2026-01-20T10:00:00Z",
                    "transitioned_by": "user_123"
                }
            ]
        })
        
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            new_state="obsolete",
            transitioned_by="user_456"
        )
        
        assert result is True
        
        # Verify both transitions are recorded
        call_args = mock_state_management.store_state.call_args
        state_data = call_args.kwargs.get("state_data", {})
        transitions = state_data.get("lifecycle_transitions", [])
        assert len(transitions) == 2
        assert transitions[0]["from_state"] == "draft"
        assert transitions[0]["to_state"] == "accepted"
        assert transitions[1]["from_state"] == "accepted"
        assert transitions[1]["to_state"] == "obsolete"
        assert transitions[1]["transitioned_by"] == "user_456"
    
    @pytest.mark.asyncio
    async def test_version_created_on_acceptance(self, artifact_plane, mock_state_management):
        """Test that version is set to 1 when artifact transitions to accepted."""
        # Setup: Mock artifact in draft state (no version set)
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "draft",
            "lifecycle_transitions": []
        })
        
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            new_state="accepted"
        )
        
        assert result is True
        
        # Verify version was set
        call_args = mock_state_management.store_state.call_args
        state_data = call_args.kwargs.get("state_data", {})
        assert state_data.get("version") == 1
        assert state_data.get("is_current_version") is True
        assert state_data.get("parent_artifact_id") is None
    
    @pytest.mark.asyncio
    async def test_version_not_changed_if_already_set(self, artifact_plane, mock_state_management):
        """Test that version is not changed if already set when transitioning to accepted."""
        # Setup: Mock artifact already with version
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "draft",
            "lifecycle_transitions": [],
            "version": 2,
            "is_current_version": True
        })
        
        result = await artifact_plane.transition_lifecycle_state(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            new_state="accepted"
        )
        
        assert result is True
        
        # Verify version was not changed
        call_args = mock_state_management.store_state.call_args
        state_data = call_args.kwargs.get("state_data", {})
        assert state_data.get("version") == 2
    
    @pytest.mark.asyncio
    async def test_get_artifact_version_current(self, artifact_plane, mock_state_management):
        """Test getting current version of artifact."""
        # Setup: Mock artifact retrieval
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "accepted",
            "version": 1,
            "is_current_version": True
        })
        
        result = await artifact_plane.get_artifact_version(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123"
        )
        
        # Should return artifact (via get_artifact)
        assert artifact_plane.artifact_storage.get_artifact.called
    
    @pytest.mark.asyncio
    async def test_get_artifact_version_specific(self, artifact_plane, mock_state_management):
        """Test getting specific version of artifact."""
        # Setup: Mock artifact with version
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "accepted",
            "version": 1,
            "is_current_version": True
        })
        
        result = await artifact_plane.get_artifact_version(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123",
            version=1
        )
        
        # Should return artifact if version matches
        assert artifact_plane.artifact_storage.get_artifact.called
    
    @pytest.mark.asyncio
    async def test_list_artifact_versions(self, artifact_plane, mock_state_management):
        """Test listing all versions of an artifact."""
        # Setup: Mock artifact retrieval
        mock_state_management.retrieve_state = AsyncMock(return_value={
            "artifact_id": "test_artifact_123",
            "lifecycle_state": "accepted",
            "version": 1,
            "is_current_version": True
        })
        
        result = await artifact_plane.list_artifact_versions(
            artifact_id="test_artifact_123",
            tenant_id="tenant_123"
        )
        
        # Should return list (for MVP, just current version)
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_create_artifact_sets_version(self, artifact_plane, execution_context):
        """Test that creating artifact sets version to 1."""
        result = await artifact_plane.create_artifact(
            artifact_type="roadmap",
            artifact_id=None,
            payload={"data": "test"},
            context=execution_context
        )
        
        assert result is not None
        
        # Verify version fields are set
        call_args = artifact_plane.state_management.store_state.call_args
        state_data = call_args.kwargs.get("state_data", {})
        assert state_data.get("version") == 1
        assert state_data.get("is_current_version") is True
        assert state_data.get("parent_artifact_id") is None
