"""
StateSurface Integration Tests

Tests StateSurface with real Redis and ArangoDB instances.

WHAT (Test Role): I verify StateSurface execution state management works
HOW (Test Implementation): I use docker-compose Redis and ArangoDB and test state operations
"""

import pytest
from typing import Dict, Any
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter
from symphainy_platform.foundations.public_works.adapters.arango_adapter import ArangoAdapter
from symphainy_platform.foundations.public_works.abstractions.state_abstraction import StateManagementAbstraction
from symphainy_platform.runtime.state_surface import StateSurface
from tests.infrastructure.test_fixtures import test_redis, test_arango, clean_test_db


@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.runtime
class TestStateSurface:
    """Test StateSurface with real Redis and ArangoDB."""
    
    @pytest.fixture
    def state_surface(
        self,
        test_redis: RedisAdapter,
        test_arango: ArangoAdapter
    ) -> StateSurface:
        """Create StateSurface with real adapters."""
        state_abstraction = StateManagementAbstraction(
            redis_adapter=test_redis,
            arango_adapter=test_arango
        )
        return StateSurface(state_abstraction=state_abstraction)
    
    @pytest.mark.asyncio
    async def test_set_get_execution_state(
        self,
        state_surface: StateSurface
    ):
        """Test setting and getting execution state."""
        execution_id = "exec_test_1"
        tenant_id = "tenant_1"
        state = {
            "status": "running",
            "step": 1,
            "data": {"key": "value"}
        }
        
        # Set execution state
        success = await state_surface.set_execution_state(execution_id, tenant_id, state)
        assert success, "Execution state should be set"
        
        # Get execution state
        retrieved = await state_surface.get_execution_state(execution_id, tenant_id)
        assert retrieved is not None, "Execution state should be retrievable"
        assert retrieved["status"] == "running", "State should match"
        assert retrieved["step"] == 1, "State should match"
        assert retrieved["data"]["key"] == "value", "Nested state should match"
    
    @pytest.mark.asyncio
    async def test_set_get_session_state(
        self,
        state_surface: StateSurface
    ):
        """Test setting and getting session state."""
        session_id = "session_test_1"
        tenant_id = "tenant_1"
        session_state = {
            "user_id": "user_123",
            "active_executions": [],
            "metadata": {"source": "test"}
        }
        
        # Set session state
        success = await state_surface.set_session_state(session_id, tenant_id, session_state)
        assert success, "Session state should be set"
        
        # Get session state
        retrieved = await state_surface.get_session_state(session_id, tenant_id)
        assert retrieved is not None, "Session state should be retrievable"
        assert retrieved["user_id"] == "user_123", "Session state should match"
        assert retrieved["metadata"]["source"] == "test", "Session metadata should match"
    
    @pytest.mark.asyncio
    async def test_tenant_isolation(
        self,
        state_surface: StateSurface
    ):
        """Test that states are isolated by tenant."""
        execution_id = "exec_shared"
        tenant1 = "tenant_1"
        tenant2 = "tenant_2"
        
        state1 = {"tenant": "tenant_1", "value": 1}
        state2 = {"tenant": "tenant_2", "value": 2}
        
        # Set states for different tenants
        await state_surface.set_execution_state(execution_id, tenant1, state1)
        await state_surface.set_execution_state(execution_id, tenant2, state2)
        
        # Verify isolation
        retrieved1 = await state_surface.get_execution_state(execution_id, tenant1)
        retrieved2 = await state_surface.get_execution_state(execution_id, tenant2)
        
        assert retrieved1["tenant"] == "tenant_1", "Tenant1 state should be isolated"
        assert retrieved2["tenant"] == "tenant_2", "Tenant2 state should be isolated"
        assert retrieved1["value"] == 1, "Tenant1 value should match"
        assert retrieved2["value"] == 2, "Tenant2 value should match"
    
    @pytest.mark.asyncio
    async def test_update_execution_state(
        self,
        state_surface: StateSurface
    ):
        """Test updating execution state."""
        execution_id = "exec_update"
        tenant_id = "tenant_1"
        
        # Set initial state
        initial_state = {"status": "running", "step": 1}
        await state_surface.set_execution_state(execution_id, tenant_id, initial_state)
        
        # Update state
        updated_state = {"status": "completed", "step": 2, "result": "success"}
        success = await state_surface.set_execution_state(execution_id, tenant_id, updated_state)
        assert success, "State update should succeed"
        
        # Verify update
        retrieved = await state_surface.get_execution_state(execution_id, tenant_id)
        assert retrieved["status"] == "completed", "Status should be updated"
        assert retrieved["step"] == 2, "Step should be updated"
        assert retrieved["result"] == "success", "New field should be added"
    
    @pytest.mark.asyncio
    async def test_store_file_reference(
        self,
        state_surface: StateSurface
    ):
        """Test storing file reference in state."""
        session_id = "session_file_ref"
        tenant_id = "tenant_1"
        file_reference = "file:tenant_1:session_file_ref:file_123"
        storage_location = "gs://bucket/file.txt"
        filename = "test_file.txt"
        metadata = {
            "size": 1024,
            "content_type": "text/plain"
        }
        
        # Store file reference
        stored_ref = await state_surface.store_file_reference(
            session_id,
            tenant_id,
            file_reference,
            storage_location,
            filename,
            metadata=metadata
        )
        assert stored_ref == file_reference, "File reference should be stored"
        
        # Retrieve file metadata (via get_file_metadata)
        file_metadata = await state_surface.get_file_metadata(file_reference)
        assert file_metadata is not None, "File metadata should be retrievable"
        assert file_metadata["storage_location"] == storage_location, "Storage location should match"
        assert file_metadata["filename"] == filename, "Filename should match"
    
    @pytest.mark.asyncio
    async def test_multiple_executions(
        self,
        state_surface: StateSurface
    ):
        """Test managing multiple executions for a tenant."""
        tenant_id = "tenant_multiple"
        
        # Create multiple executions
        execution_states = {}
        for i in range(3):
            execution_id = f"exec_multiple_{i}"
            state = {"execution_number": i, "status": "running"}
            await state_surface.set_execution_state(execution_id, tenant_id, state)
            execution_states[execution_id] = state
        
        # Verify all executions can be retrieved
        for execution_id, expected_state in execution_states.items():
            retrieved = await state_surface.get_execution_state(execution_id, tenant_id)
            assert retrieved is not None, f"Execution {execution_id} should be retrievable"
            assert retrieved["execution_number"] == expected_state["execution_number"], f"Execution {execution_id} data should match"
    
    @pytest.mark.asyncio
    async def test_state_overwrite(
        self,
        state_surface: StateSurface
    ):
        """Test that setting state overwrites existing state."""
        execution_id = "exec_overwrite"
        tenant_id = "tenant_1"
        
        # Set initial state
        initial_state = {"status": "running", "step": 1}
        await state_surface.set_execution_state(execution_id, tenant_id, initial_state)
        
        # Overwrite with new state
        new_state = {"status": "completed", "step": 2, "result": "success"}
        success = await state_surface.set_execution_state(execution_id, tenant_id, new_state)
        assert success, "State overwrite should succeed"
        
        # Verify new state
        retrieved = await state_surface.get_execution_state(execution_id, tenant_id)
        assert retrieved["status"] == "completed", "State should be overwritten"
        assert retrieved["step"] == 2, "State should be overwritten"
        assert "result" in retrieved, "New fields should be present"
    
    @pytest.mark.asyncio
    async def test_error_handling_missing_state(
        self,
        state_surface: StateSurface
    ):
        """Test error handling for missing state."""
        # Try to get non-existent execution state
        retrieved = await state_surface.get_execution_state("non_existent", "tenant_1")
        assert retrieved is None, "Should return None for non-existent state"
        
        # Try to get non-existent session state
        session = await state_surface.get_session_state("non_existent", "tenant_1")
        assert session is None, "Should return None for non-existent session"
