"""
Unit tests for State Surface.
"""

import pytest
from symphainy_platform.runtime.state_surface import StateSurface


@pytest.mark.unit
@pytest.mark.runtime
class TestStateSurface:
    """Test State Surface."""
    
    @pytest.mark.asyncio
    async def test_set_get_execution_state_memory(self):
        """Test setting and getting execution state (in-memory)."""
        state_surface = StateSurface(use_memory=True)
        
        execution_id = "exec_123"
        tenant_id = "tenant_123"
        state = {"status": "running", "data": "test"}
        
        # Set state
        result = await state_surface.set_execution_state(execution_id, tenant_id, state)
        assert result is True
        
        # Get state
        retrieved = await state_surface.get_execution_state(execution_id, tenant_id)
        assert retrieved is not None
        assert retrieved["status"] == "running"
        assert retrieved["data"] == "test"
        assert "updated_at" in retrieved
    
    @pytest.mark.asyncio
    async def test_set_get_session_state_memory(self):
        """Test setting and getting session state (in-memory)."""
        state_surface = StateSurface(use_memory=True)
        
        session_id = "session_123"
        tenant_id = "tenant_123"
        state = {"user_id": "user_123", "context": {}}
        
        # Set state
        result = await state_surface.set_session_state(session_id, tenant_id, state)
        assert result is True
        
        # Get state
        retrieved = await state_surface.get_session_state(session_id, tenant_id)
        assert retrieved is not None
        assert retrieved["user_id"] == "user_123"
        assert "updated_at" in retrieved
    
    @pytest.mark.asyncio
    async def test_delete_state_memory(self):
        """Test deleting state (in-memory)."""
        state_surface = StateSurface(use_memory=True)
        
        execution_id = "exec_123"
        tenant_id = "tenant_123"
        state = {"status": "running"}
        
        # Set state
        await state_surface.set_execution_state(execution_id, tenant_id, state)
        
        # Delete state
        result = await state_surface.delete_state("execution", tenant_id, execution_id)
        assert result is True
        
        # Verify deleted
        retrieved = await state_surface.get_execution_state(execution_id, tenant_id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_list_executions_memory(self):
        """Test listing executions (in-memory)."""
        state_surface = StateSurface(use_memory=True)
        
        tenant_id = "tenant_123"
        
        # Create multiple executions
        for i in range(5):
            await state_surface.set_execution_state(
                f"exec_{i}",
                tenant_id,
                {"status": "running"}
            )
        
        # List executions
        executions = await state_surface.list_executions(tenant_id)
        assert len(executions) == 5
        assert "exec_0" in executions
        assert "exec_4" in executions
