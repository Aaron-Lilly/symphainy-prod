"""
Integration tests for Runtime Spine (Week 1.5).

Tests end-to-end flow:
- Session creation → Intent submission → Saga registration → State recording
"""

import pytest
from symphainy_platform.runtime import (
    StateSurface,
    WriteAheadLog,
    SagaCoordinator,
    RuntimeService
)


@pytest.mark.integration
@pytest.mark.runtime
class TestRuntimeSpine:
    """Test Runtime Spine end-to-end."""
    
    @pytest.fixture
    async def runtime_service(self):
        """Create runtime service with in-memory storage."""
        state_surface = StateSurface(use_memory=True)
        wal = WriteAheadLog(use_memory=True)
        saga_coordinator = SagaCoordinator(state_surface=state_surface)
        
        return RuntimeService(
            state_surface=state_surface,
            wal=wal,
            saga_coordinator=saga_coordinator
        )
    
    @pytest.mark.asyncio
    async def test_create_session_flow(self, runtime_service):
        """Test session creation flow."""
        from symphainy_platform.runtime.runtime_service import CreateSessionRequest
        
        # Create session
        request = CreateSessionRequest(
            tenant_id="test_tenant",
            user_id="test_user",
            context={"test": "data"}
        )
        
        response = await runtime_service.create_session(request)
        
        assert response.success is True
        assert response.session is not None
        assert response.session["tenant_id"] == "test_tenant"
        assert response.session["user_id"] == "test_user"
        assert response.session["context"] == {"test": "data"}
        assert response.session["session_id"] is not None
    
    @pytest.mark.asyncio
    async def test_intent_submission_flow(self, runtime_service):
        """Test intent submission flow."""
        from symphainy_platform.runtime.runtime_service import (
            CreateSessionRequest,
            SubmitIntentRequest
        )
        
        # Create session first
        session_request = CreateSessionRequest(
            tenant_id="test_tenant",
            user_id="test_user"
        )
        session_response = await runtime_service.create_session(session_request)
        assert session_response.success is True
        session_id = session_response.session["session_id"]
        
        # Submit intent
        intent_request = SubmitIntentRequest(
            intent_type="content.upload",
            realm="content",
            session_id=session_id,
            tenant_id="test_tenant",
            payload={"file_path": "/tmp/test.txt"}
        )
        
        intent_response = await runtime_service.submit_intent(intent_request)
        
        assert intent_response.success is True
        assert intent_response.execution_id is not None
    
    @pytest.mark.asyncio
    async def test_wal_entries_created(self, runtime_service):
        """Test that WAL entries are created."""
        from symphainy_platform.runtime.runtime_service import (
            CreateSessionRequest,
            SubmitIntentRequest
        )
        
        # Create session
        session_request = CreateSessionRequest(
            tenant_id="test_tenant",
            user_id="test_user"
        )
        session_response = await runtime_service.create_session(session_request)
        session_id = session_response.session["session_id"]
        
        # Submit intent
        intent_request = SubmitIntentRequest(
            intent_type="content.upload",
            realm="content",
            session_id=session_id,
            tenant_id="test_tenant",
            payload={}
        )
        await runtime_service.submit_intent(intent_request)
        
        # Check WAL events
        events = await runtime_service.wal.get_events("test_tenant")
        assert len(events) >= 3  # SESSION_CREATED, INTENT_RECEIVED, SAGA_STARTED
        
        event_types = [e.event_type.value for e in events]
        assert "session_created" in event_types
        assert "intent_received" in event_types
        assert "saga_started" in event_types
    
    @pytest.mark.asyncio
    async def test_saga_registration(self, runtime_service):
        """Test that sagas are registered."""
        from symphainy_platform.runtime.runtime_service import (
            CreateSessionRequest,
            SubmitIntentRequest
        )
        
        # Create session
        session_request = CreateSessionRequest(
            tenant_id="test_tenant",
            user_id="test_user"
        )
        session_response = await runtime_service.create_session(session_request)
        session_id = session_response.session["session_id"]
        
        # Submit intent
        intent_request = SubmitIntentRequest(
            intent_type="content.upload",
            realm="content",
            session_id=session_id,
            tenant_id="test_tenant",
            payload={}
        )
        intent_response = await runtime_service.submit_intent(intent_request)
        execution_id = intent_response.execution_id
        
        # Check execution state
        state = await runtime_service.state_surface.get_execution_state(
            execution_id,
            "test_tenant"
        )
        
        assert state is not None
        assert state["status"] == "pending"
        assert "saga_id" in state
    
    @pytest.mark.asyncio
    async def test_multi_tenant_isolation(self, runtime_service):
        """Test multi-tenant isolation."""
        from symphainy_platform.runtime.runtime_service import CreateSessionRequest
        
        # Create sessions for different tenants
        session1 = await runtime_service.create_session(
            CreateSessionRequest(tenant_id="tenant_1", user_id="user_1")
        )
        session2 = await runtime_service.create_session(
            CreateSessionRequest(tenant_id="tenant_2", user_id="user_2")
        )
        
        assert session1.success is True
        assert session2.success is True
        
        # Try to access session from wrong tenant
        response = await runtime_service.get_session(
            session1.session["session_id"],
            "tenant_2"  # Wrong tenant
        )
        
        # Should not find session (tenant isolation)
        assert response.success is False
        assert "not found" in response.error.lower()
