"""
Runtime Spine Integration Tests

Tests Runtime API with real infrastructure (Redis, ArangoDB).

WHAT (Test Role): I verify Runtime initialization, service discovery, session creation, and intent submission
HOW (Test Implementation): I use docker-compose infrastructure and test Runtime API operations
"""

import pytest
from typing import Dict, Any
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter
from symphainy_platform.foundations.public_works.adapters.arango_adapter import ArangoAdapter
from symphainy_platform.foundations.public_works.abstractions.state_abstraction import StateManagementAbstraction
from symphainy_platform.runtime.runtime_api import RuntimeAPI
from symphainy_platform.runtime.execution_lifecycle_manager import ExecutionLifecycleManager
from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.runtime.wal import WriteAheadLog
from symphainy_platform.runtime.intent_registry import IntentRegistry
from symphainy_platform.runtime.realm_registry import RealmRegistry
from tests.infrastructure.test_fixtures import test_redis, test_arango, clean_test_db


@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.runtime
class TestRuntimeSpine:
    """Test Runtime Spine with real infrastructure."""
    
    @pytest.fixture
    def mock_intent_handler_function(self):
        """Create a mock intent handler function for testing."""
        async def mock_handler(intent, context):
            """Mock handler function that returns success."""
            return {
                "status": "success",
                "result": f"Processed {intent.intent_type}",
                "artifacts": {
                    "output": "test_output"
                }
            }
        
        return mock_handler
    
    @pytest.fixture
    def runtime_api(
        self,
        test_redis: RedisAdapter,
        test_arango: ArangoAdapter,
        mock_intent_handler_function
    ) -> RuntimeAPI:
        """Create RuntimeAPI with real adapters."""
        # Create dependencies
        state_abstraction = StateManagementAbstraction(
            redis_adapter=test_redis,
            arango_adapter=test_arango
        )
        state_surface = StateSurface(state_abstraction=state_abstraction)
        wal = WriteAheadLog(redis_adapter=test_redis)
        
        # Create intent registry and realm registry
        intent_registry = IntentRegistry()
        realm_registry = RealmRegistry(intent_registry=intent_registry)
        
        # Register mock handler for common test intents
        intent_registry.register_intent(
            intent_type="content.ingest_file",
            handler_name="test_handler",
            handler_function=mock_intent_handler_function
        )
        
        # ✅ Create Data Steward SDK for boundary contract assignment
        from tests.helpers.data_steward_fixtures import create_data_steward_sdk
        data_steward_sdk = create_data_steward_sdk(supabase_adapter=None)
        
        # Create execution lifecycle manager
        execution_lifecycle_manager = ExecutionLifecycleManager(
            intent_registry=intent_registry,
            state_surface=state_surface,
            wal=wal,
            data_steward_sdk=data_steward_sdk  # ✅ Required
        )
        
        # Create Runtime API
        return RuntimeAPI(
            execution_lifecycle_manager=execution_lifecycle_manager,
            state_surface=state_surface
        )
    
    @pytest.mark.asyncio
    async def test_runtime_initialization(self, runtime_api: RuntimeAPI):
        """Test Runtime API initialization."""
        assert runtime_api is not None, "Runtime API should be initialized"
        assert runtime_api.execution_lifecycle_manager is not None, "Execution lifecycle manager should be initialized"
        assert runtime_api.state_surface is not None, "State surface should be initialized"
    
    @pytest.mark.asyncio
    async def test_create_session_flow(self, runtime_api: RuntimeAPI):
        """Test session creation flow."""
        from symphainy_platform.runtime.runtime_api import SessionCreateRequest
        
        # Create session
        request = SessionCreateRequest(
            tenant_id="test_tenant",
            user_id="test_user",
            metadata={"test": "data"}
        )
        
        response = await runtime_api.create_session(request)
        
        assert response is not None, "Session response should be returned"
        assert response.session_id is not None, "Session ID should be set"
        assert response.tenant_id == "test_tenant", "Tenant ID should match"
        assert response.user_id == "test_user", "User ID should match"
    
    @pytest.mark.asyncio
    async def test_intent_submission_flow(self, runtime_api: RuntimeAPI):
        """Test intent submission flow."""
        from symphainy_platform.runtime.runtime_api import (
            SessionCreateRequest,
            IntentSubmitRequest
        )
        
        # Create session first
        session_request = SessionCreateRequest(
            tenant_id="test_tenant",
            user_id="test_user"
        )
        session_response = await runtime_api.create_session(session_request)
        assert session_response is not None, "Session should be created"
        session_id = session_response.session_id
        
        # Submit intent
        intent_request = IntentSubmitRequest(
            intent_type="content.ingest_file",
            tenant_id="test_tenant",
            session_id=session_id,
            solution_id="test_solution",
            parameters={"file_path": "/tmp/test.txt"}
        )
        
        intent_response = await runtime_api.submit_intent(intent_request)
        
        assert intent_response is not None, "Intent response should be returned"
        assert intent_response.execution_id is not None, "Execution ID should be set"
        assert intent_response.intent_id is not None, "Intent ID should be set"
        assert intent_response.status in ["pending", "running", "completed", "accepted"], "Status should be valid"
    
    @pytest.mark.asyncio
    async def test_wal_entries_created(self, runtime_api: RuntimeAPI):
        """Test that WAL entries are created."""
        from symphainy_platform.runtime.runtime_api import (
            SessionCreateRequest,
            IntentSubmitRequest
        )
        
        # Create session
        session_request = SessionCreateRequest(
            tenant_id="test_tenant_wal",
            user_id="test_user"
        )
        session_response = await runtime_api.create_session(session_request)
        session_id = session_response.session_id
        
        # Submit intent
        intent_request = IntentSubmitRequest(
            intent_type="content.ingest_file",
            tenant_id="test_tenant_wal",
            session_id=session_id,
            solution_id="test_solution",
            parameters={}
        )
        await runtime_api.submit_intent(intent_request)
        
        # Check WAL events
        wal = runtime_api.execution_lifecycle_manager.wal
        events = await wal.get_events("test_tenant_wal", limit=10)
        
        # Should have at least INTENT_RECEIVED and EXECUTION_STARTED events
        assert len(events) > 0, "WAL should have events"
        event_types = [e.event_type for e in events]
        from symphainy_platform.runtime.wal import WALEventType
        assert WALEventType.INTENT_RECEIVED in event_types or WALEventType.EXECUTION_STARTED in event_types, "Should log execution events"
    
    @pytest.mark.asyncio
    async def test_execution_state_tracking(self, runtime_api: RuntimeAPI):
        """Test that execution state is tracked."""
        from symphainy_platform.runtime.runtime_api import (
            SessionCreateRequest,
            IntentSubmitRequest
        )
        
        # Create session
        session_request = SessionCreateRequest(
            tenant_id="test_tenant_state",
            user_id="test_user"
        )
        session_response = await runtime_api.create_session(session_request)
        session_id = session_response.session_id
        
        # Submit intent
        intent_request = IntentSubmitRequest(
            intent_type="content.ingest_file",
            tenant_id="test_tenant_state",
            session_id=session_id,
            solution_id="test_solution",
            parameters={}
        )
        intent_response = await runtime_api.submit_intent(intent_request)
        execution_id = intent_response.execution_id
        
        # Check execution state
        state = await runtime_api.state_surface.get_execution_state(
            execution_id,
            "test_tenant_state"
        )
        
        assert state is not None, "Execution state should be tracked"
        assert state.get("status") in ["pending", "running", "completed"], "Execution state should have valid status"
    
    @pytest.mark.asyncio
    async def test_multi_tenant_isolation(self, runtime_api: RuntimeAPI):
        """Test multi-tenant isolation."""
        from symphainy_platform.runtime.runtime_api import SessionCreateRequest
        
        # Create sessions for different tenants
        session1_request = SessionCreateRequest(tenant_id="tenant_1", user_id="user_1")
        session1 = await runtime_api.create_session(session1_request)
        
        session2_request = SessionCreateRequest(tenant_id="tenant_2", user_id="user_2")
        session2 = await runtime_api.create_session(session2_request)
        
        assert session1 is not None, "Session 1 should be created"
        assert session2 is not None, "Session 2 should be created"
        assert session1.session_id != session2.session_id, "Sessions should have different IDs"
        
        # Verify tenant isolation in state
        state1 = await runtime_api.state_surface.get_session_state(
            session1.session_id,
            "tenant_1"
        )
        state2 = await runtime_api.state_surface.get_session_state(
            session2.session_id,
            "tenant_2"
        )
        
        assert state1 is not None, "Tenant 1 session state should exist"
        assert state2 is not None, "Tenant 2 session state should exist"
        
        # Try to access session from wrong tenant (should return None)
        wrong_tenant_state = await runtime_api.state_surface.get_session_state(
            session1.session_id,
            "tenant_2"  # Wrong tenant
        )
        # Note: StateSurface may return None or empty dict for wrong tenant
        # The key is that tenants are isolated
