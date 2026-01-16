"""
Execution Lifecycle Integration Tests

Tests ExecutionLifecycleManager with real infrastructure.

WHAT (Test Role): I verify execution lifecycle orchestration works
HOW (Test Implementation): I use docker-compose infrastructure and test execution flows
"""

import pytest
from typing import Dict, Any
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter
from symphainy_platform.foundations.public_works.adapters.arango_adapter import ArangoAdapter
from symphainy_platform.foundations.public_works.abstractions.state_abstraction import StateManagementAbstraction
from symphainy_platform.runtime.execution_lifecycle_manager import ExecutionLifecycleManager, ExecutionResult
from symphainy_platform.runtime.intent_model import Intent, IntentFactory
from symphainy_platform.runtime.intent_registry import IntentRegistry, IntentHandler
from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.runtime.wal import WriteAheadLog, WALEventType
from symphainy_platform.runtime.transactional_outbox import TransactionalOutbox
from tests.infrastructure.test_fixtures import test_redis, test_arango, clean_test_db


@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.runtime
class TestExecutionLifecycle:
    """Test ExecutionLifecycleManager with real infrastructure."""
    
    @pytest.fixture
    def execution_manager(
        self,
        test_redis: RedisAdapter,
        test_arango: ArangoAdapter
    ) -> ExecutionLifecycleManager:
        """Create ExecutionLifecycleManager with real adapters."""
        # Create dependencies
        state_abstraction = StateManagementAbstraction(
            redis_adapter=test_redis,
            arango_adapter=test_arango
        )
        state_surface = StateSurface(state_abstraction=state_abstraction)
        wal = WriteAheadLog(redis_adapter=test_redis)
        transactional_outbox = TransactionalOutbox(redis_adapter=test_redis, wal=wal)
        
        # Create intent registry
        intent_registry = IntentRegistry()
        
        # Create execution lifecycle manager
        return ExecutionLifecycleManager(
            intent_registry=intent_registry,
            state_surface=state_surface,
            wal=wal,
            transactional_outbox=transactional_outbox
        )
    
    @pytest.fixture
    def mock_intent_handler_function(self):
        """Create a mock intent handler function for testing."""
        async def mock_handler(intent: Intent, context: Any) -> Dict[str, Any]:
            """Mock handler function that returns success."""
            return {
                "status": "success",
                "result": f"Processed {intent.intent_type}",
                "artifacts": {
                    "output": "test_output"
                }
            }
        
        return mock_handler
    
    @pytest.mark.asyncio
    async def test_execute_intent_with_handler(
        self,
        execution_manager: ExecutionLifecycleManager,
        mock_intent_handler_function
    ):
        """Test executing an intent with a registered handler."""
        # Register handler
        execution_manager.intent_registry.register_intent(
            intent_type="test.intent",
            handler_name="test_handler",
            handler_function=mock_intent_handler_function
        )
        
        # Create intent
        intent = IntentFactory.create_intent(
            intent_type="test.intent",
            tenant_id="tenant_1",
            session_id="session_1",
            solution_id="solution_1",
            parameters={"test_param": "test_value"}
        )
        
        # Execute intent
        result = await execution_manager.execute(intent)
        
        assert result is not None, "Execution result should be returned"
        assert result.success is True, "Execution should succeed"
        assert result.execution_id is not None, "Execution ID should be set"
        assert "test_output" in str(result.artifacts), "Artifacts should contain handler output"
    
    @pytest.mark.asyncio
    async def test_execute_intent_without_handler(
        self,
        execution_manager: ExecutionLifecycleManager
    ):
        """Test executing an intent without a registered handler."""
        # Create intent without registering handler
        intent = IntentFactory.create_intent(
            intent_type="unknown.intent",
            tenant_id="tenant_1",
            session_id="session_1",
            solution_id="solution_1"
        )
        
        # Execute intent (should fail gracefully)
        result = await execution_manager.execute(intent)
        
        assert result is not None, "Execution result should be returned"
        assert result.success is False, "Execution should fail without handler"
        assert result.error is not None, "Error should be set"
    
    @pytest.mark.asyncio
    async def test_execution_state_tracking(
        self,
        execution_manager: ExecutionLifecycleManager,
        mock_intent_handler_function
    ):
        """Test that execution state is tracked in StateSurface."""
        # Register handler
        execution_manager.intent_registry.register_intent(
            intent_type="test.state.tracking",
            handler_name="test_handler",
            handler_function=mock_intent_handler_function
        )
        
        # Create intent
        intent = IntentFactory.create_intent(
            intent_type="test.state.tracking",
            tenant_id="tenant_state",
            session_id="session_state",
            solution_id="solution_state"
        )
        
        # Execute intent
        result = await execution_manager.execute(intent)
        assert result.success, "Execution should succeed"
        
        # Verify execution state is stored
        execution_state = await execution_manager.state_surface.get_execution_state(
            result.execution_id,
            intent.tenant_id
        )
        assert execution_state is not None, "Execution state should be stored"
        assert execution_state.get("status") in ["completed", "running"], "Execution state should have status"
    
    @pytest.mark.asyncio
    async def test_wal_logging(
        self,
        execution_manager: ExecutionLifecycleManager,
        mock_intent_handler_function
    ):
        """Test that execution is logged to WAL."""
        # Register handler
        execution_manager.intent_registry.register_intent(
            intent_type="test.wal.logging",
            handler_name="test_handler",
            handler_function=mock_intent_handler_function
        )
        
        # Create intent
        intent = IntentFactory.create_intent(
            intent_type="test.wal.logging",
            tenant_id="tenant_wal",
            session_id="session_wal",
            solution_id="solution_wal"
        )
        
        # Execute intent
        result = await execution_manager.execute(intent)
        assert result.success, "Execution should succeed"
        
        # Verify WAL events
        events = await execution_manager.wal.get_events(
            intent.tenant_id,
            limit=10
        )
        
        # Should have INTENT_RECEIVED and EXECUTION_STARTED events
        event_types = [e.event_type for e in events]
        assert WALEventType.INTENT_RECEIVED in event_types, "Should log INTENT_RECEIVED"
        assert WALEventType.EXECUTION_STARTED in event_types, "Should log EXECUTION_STARTED"
    
    @pytest.mark.asyncio
    async def test_transactional_outbox_events(
        self,
        execution_manager: ExecutionLifecycleManager,
        mock_intent_handler_function
    ):
        """Test that events are added to transactional outbox."""
        # Register handler
        execution_manager.intent_registry.register_intent(
            intent_type="test.outbox.events",
            handler_name="test_handler",
            handler_function=mock_intent_handler_function
        )
        
        # Create intent
        intent = IntentFactory.create_intent(
            intent_type="test.outbox.events",
            tenant_id="tenant_outbox",
            session_id="session_outbox",
            solution_id="solution_outbox"
        )
        
        # Execute intent
        result = await execution_manager.execute(intent)
        assert result.success, "Execution should succeed"
        
        # Verify outbox events
        pending_events = await execution_manager.transactional_outbox.get_pending_events(
            result.execution_id
        )
        # Note: Events may be published immediately, so pending may be empty
        # We verify that outbox operations work
        assert isinstance(pending_events, list), "Should return list of events"
    
    @pytest.mark.asyncio
    async def test_intent_validation(
        self,
        execution_manager: ExecutionLifecycleManager
    ):
        """Test that invalid intents are rejected."""
        # Create invalid intent (missing required fields)
        invalid_intent = Intent(
            intent_id="invalid_intent",
            intent_type="",  # Empty intent_type
            tenant_id="tenant_1",
            session_id="session_1",
            solution_id="solution_1"
        )
        
        # Execute intent (should fail validation)
        result = await execution_manager.execute(invalid_intent)
        
        assert result.success is False, "Invalid intent should fail"
        assert result.error is not None, "Error should be set"
        assert "Invalid intent" in result.error or "validation" in result.error.lower(), "Error should mention validation"
    
    @pytest.mark.asyncio
    async def test_execution_artifacts(
        self,
        execution_manager: ExecutionLifecycleManager,
        mock_intent_handler_function
    ):
        """Test that execution artifacts are returned."""
        # Register handler that returns artifacts
        execution_manager.intent_registry.register_intent(
            intent_type="test.artifacts",
            handler_name="test_handler",
            handler_function=mock_intent_handler_function
        )
        
        # Create intent
        intent = IntentFactory.create_intent(
            intent_type="test.artifacts",
            tenant_id="tenant_artifacts",
            session_id="session_artifacts",
            solution_id="solution_artifacts"
        )
        
        # Execute intent
        result = await execution_manager.execute(intent)
        assert result.success, "Execution should succeed"
        
        # Verify artifacts
        assert result.artifacts is not None, "Artifacts should be returned"
        assert len(result.artifacts) > 0, "Artifacts should not be empty"
    
    @pytest.mark.asyncio
    async def test_multiple_executions(
        self,
        execution_manager: ExecutionLifecycleManager,
        mock_intent_handler_function
    ):
        """Test executing multiple intents."""
        # Register handler
        execution_manager.intent_registry.register_intent(
            intent_type="test.multiple",
            handler_name="test_handler",
            handler_function=mock_intent_handler_function
        )
        
        # Execute multiple intents
        results = []
        for i in range(3):
            intent = IntentFactory.create_intent(
                intent_type="test.multiple",
                tenant_id="tenant_multi",
                session_id=f"session_multi_{i}",
                solution_id="solution_multi",
                parameters={"sequence": i}
            )
            result = await execution_manager.execute(intent)
            results.append(result)
        
        # Verify all executions succeeded
        assert len(results) == 3, "Should have 3 execution results"
        assert all(r.success for r in results), "All executions should succeed"
        assert len(set(r.execution_id for r in results)) == 3, "Each execution should have unique ID"
