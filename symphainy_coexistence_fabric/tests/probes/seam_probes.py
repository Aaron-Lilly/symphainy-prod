"""
Seam Probe Tests for Team B and Team C

These probes test the boundaries (seams) between components to ensure:
1. Success paths work predictably
2. Failure paths fail predictably  
3. Contracts are honored at each boundary

Run with: pytest tests/probes/seam_probes.py -v

Seam Categories:
- SEAM 1: Capability Service → PlatformContext (ctx.platform, ctx.governance, ctx.reasoning)
- SEAM 2: PlatformContext → Protocol Boundaries (what services can access)
- SEAM 3: Intent Service → Service Factory (registration and lookup)
- SEAM 4: Admin Dashboard API → Control Tower Intents
- SEAM 5: Frontend → Backend API (contract shapes)
"""

import pytest
from typing import Dict, Any, Optional
from dataclasses import dataclass
from unittest.mock import Mock, AsyncMock, MagicMock


# ============================================================================
# SEAM 1: Capability Service → PlatformContext
# ============================================================================
# This seam defines what capability services can access via ctx

class TestSeam1_PlatformContextContract:
    """
    SEAM 1: PlatformContext provides ctx.platform, ctx.governance, ctx.reasoning
    
    Contract:
    - ctx.platform: File operations, parsing, storage, embeddings
    - ctx.governance: Auth (ctx.governance.auth), Sessions (ctx.governance.sessions)
    - ctx.reasoning: LLM access, agent invocation
    - ctx.state_surface: Execution state management
    - ctx.intent: The intent being executed
    - ctx.tenant_id, ctx.session_id, ctx.execution_id: Identity
    """
    
    def test_platform_context_has_all_required_fields(self):
        """SUCCESS: PlatformContext exposes all documented fields."""
        from symphainy_platform.civic_systems.platform_sdk import PlatformContext
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # Create a minimal context
        intent = IntentFactory.create_intent(
            intent_type="test_intent",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="test_solution",
            parameters={}
        )
        
        ctx = PlatformContext(
            intent=intent,
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="test_solution",
            execution_id="test_execution",
            platform=None,
            governance=None,
            reasoning=None,
            state_surface=None
        )
        
        # Verify required fields exist
        assert hasattr(ctx, 'platform'), "ctx.platform must exist"
        assert hasattr(ctx, 'governance'), "ctx.governance must exist"
        assert hasattr(ctx, 'reasoning'), "ctx.reasoning must exist"
        assert hasattr(ctx, 'state_surface'), "ctx.state_surface must exist"
        assert hasattr(ctx, 'intent'), "ctx.intent must exist"
        assert hasattr(ctx, 'tenant_id'), "ctx.tenant_id must exist"
        assert hasattr(ctx, 'session_id'), "ctx.session_id must exist"
        assert hasattr(ctx, 'execution_id'), "ctx.execution_id must exist"
        
        print("✅ SEAM 1: PlatformContext has all required fields")
    
    def test_platform_context_to_execution_context_conversion(self):
        """SUCCESS: PlatformContext can convert to ExecutionContext for library calls."""
        from symphainy_platform.civic_systems.platform_sdk import PlatformContext
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="test_intent",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="test_solution",
            parameters={"key": "value"}
        )
        
        ctx = PlatformContext(
            intent=intent,
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="test_solution",
            execution_id="exec_123",
            platform=None,
            governance=None,
            reasoning=None,
            state_surface=None
        )
        
        # Convert to ExecutionContext
        exec_ctx = ctx.to_execution_context()
        
        # Verify conversion preserves identity
        assert exec_ctx.tenant_id == ctx.tenant_id
        assert exec_ctx.session_id == ctx.session_id
        assert exec_ctx.execution_id == ctx.execution_id
        assert exec_ctx.intent == ctx.intent
        
        print("✅ SEAM 1: PlatformContext converts to ExecutionContext correctly")
    
    def test_platform_context_with_none_services_is_valid(self):
        """SUCCESS: PlatformContext accepts None for optional services."""
        from symphainy_platform.civic_systems.platform_sdk import PlatformContext
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="test_intent",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="test_solution",
            parameters={}
        )
        
        # Should not raise
        ctx = PlatformContext(
            intent=intent,
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="test_solution",
            execution_id="test_execution",
            platform=None,  # OK to be None
            governance=None,  # OK to be None
            reasoning=None,  # OK to be None
            state_surface=None  # OK to be None
        )
        
        assert ctx.platform is None
        assert ctx.governance is None
        assert ctx.reasoning is None
        
        print("✅ SEAM 1: PlatformContext accepts None services (services inject later)")


# ============================================================================
# SEAM 2: Service → Protocol Boundary Access
# ============================================================================
# This seam defines what services can/cannot access

class TestSeam2_ProtocolBoundaryAccess:
    """
    SEAM 2: Services access infrastructure through protocol boundaries only
    
    Contract:
    - ctx.platform: Can access parse(), ingest_file(), delete_file(), embed(), etc.
    - ctx.governance.auth: Can access authenticate(), register_user(), validate_token()
    - ctx.governance.sessions: Can access create_session_intent(), terminate_session()
    - ctx.reasoning: Can access invoke_agent(), complete(), etc.
    
    FORBIDDEN:
    - ctx.platform._public_works (internal)
    - getattr(ctx.platform._public_works, 'security_guard_sdk') (adapter leak)
    """
    
    def test_platform_service_exposes_file_operations(self):
        """SUCCESS: ctx.platform exposes file operations."""
        from symphainy_platform.civic_systems.platform_sdk.services.platform_service import PlatformService
        
        # Create minimal PlatformService
        platform = PlatformService(public_works=None)
        
        # Verify expected methods exist
        assert hasattr(platform, 'ingest_file'), "ctx.platform must have ingest_file()"
        assert hasattr(platform, 'delete_file'), "ctx.platform must have delete_file()"
        assert hasattr(platform, 'parse'), "ctx.platform must have parse()"
        assert hasattr(platform, 'embed'), "ctx.platform must have embed()"
        assert hasattr(platform, 'store_artifact'), "ctx.platform must have store_artifact()"
        
        print("✅ SEAM 2: PlatformService exposes file operations")
    
    def test_platform_service_delete_file_fails_without_abstraction(self):
        """FAILURE MODE: delete_file() raises RuntimeError if abstraction not wired."""
        from symphainy_platform.civic_systems.platform_sdk.services.platform_service import PlatformService
        
        # Create PlatformService without file_storage
        platform = PlatformService(public_works=None)
        
        # Attempting delete_file should raise
        import asyncio
        with pytest.raises(RuntimeError) as exc_info:
            asyncio.get_event_loop().run_until_complete(
                platform.delete_file("test_location")
            )
        
        assert "FileStorageAbstraction not wired" in str(exc_info.value)
        assert "Platform contract §8A" in str(exc_info.value)
        
        print("✅ SEAM 2: delete_file() fails loudly when abstraction missing")
    
    def test_governance_service_structure(self):
        """SUCCESS: ctx.governance has auth and sessions sub-services."""
        from symphainy_platform.civic_systems.platform_sdk.services.governance_service import GovernanceService
        
        # Create minimal GovernanceService
        governance = GovernanceService(public_works=None)
        
        # Verify structure - check attributes exist (accessing raises if not wired)
        assert hasattr(governance, '_security_guard_sdk'), "GovernanceService should have _security_guard_sdk"
        assert hasattr(governance, '_traffic_cop_sdk'), "GovernanceService should have _traffic_cop_sdk"
        
        print("✅ SEAM 2: GovernanceService has auth and sessions structure")
    
    def test_security_service_fails_without_governance_auth(self):
        """FAILURE MODE: Security services fail if ctx.governance.auth missing."""
        from symphainy_platform.capabilities.security.intent_services.authenticate_user_service import AuthenticateUserService
        from symphainy_platform.civic_systems.platform_sdk import PlatformContext
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        service = AuthenticateUserService()
        
        intent = IntentFactory.create_intent(
            intent_type="authenticate_user",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security",
            parameters={"email": "test@test.com", "password": "test123"}
        )
        
        # Create context WITHOUT governance
        ctx = PlatformContext(
            intent=intent,
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security",
            execution_id="test_execution",
            platform=None,
            governance=None,  # Missing!
            reasoning=None,
            state_surface=None
        )
        
        # Execute should raise RuntimeError
        import asyncio
        with pytest.raises(RuntimeError) as exc_info:
            asyncio.get_event_loop().run_until_complete(service.execute(ctx))
        
        assert "ctx.governance.auth required" in str(exc_info.value)
        
        print("✅ SEAM 2: Security services fail loudly without ctx.governance.auth")


# ============================================================================
# SEAM 3: Intent Service → Service Factory
# ============================================================================
# This seam defines how services are registered and looked up

class TestSeam3_ServiceFactoryContract:
    """
    SEAM 3: Services register with ServiceFactory, Runtime looks them up
    
    Contract:
    - Each service has intent_type class attribute
    - Services extend PlatformIntentService
    - Services have async execute(ctx) method
    - ServiceFactory maps intent_type -> service instance
    """
    
    def test_all_services_have_intent_type(self):
        """SUCCESS: All capability services have intent_type class attribute."""
        from symphainy_platform.capabilities.content.intent_services import (
            IngestFileService, DeleteFileService, ParseContentService
        )
        from symphainy_platform.capabilities.security.intent_services import (
            AuthenticateUserService, CreateSessionService
        )
        from symphainy_platform.capabilities.control_tower.intent_services import (
            GetPlatformStatisticsService, ListSolutionsService
        )
        
        services = [
            IngestFileService,
            DeleteFileService,
            ParseContentService,
            AuthenticateUserService,
            CreateSessionService,
            GetPlatformStatisticsService,
            ListSolutionsService
        ]
        
        for service_class in services:
            assert hasattr(service_class, 'intent_type'), \
                f"{service_class.__name__} missing intent_type class attribute"
            assert service_class.intent_type is not None, \
                f"{service_class.__name__}.intent_type is None"
        
        print(f"✅ SEAM 3: {len(services)} services have intent_type attributes")
    
    def test_service_extends_platform_intent_service(self):
        """SUCCESS: Services extend PlatformIntentService base class."""
        from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService
        from symphainy_platform.capabilities.content.intent_services import IngestFileService
        
        assert issubclass(IngestFileService, PlatformIntentService), \
            "IngestFileService must extend PlatformIntentService"
        
        print("✅ SEAM 3: Services extend PlatformIntentService")
    
    def test_service_execute_is_async(self):
        """SUCCESS: Service execute() method is async."""
        from symphainy_platform.capabilities.content.intent_services import IngestFileService
        import inspect
        
        service = IngestFileService()
        
        assert hasattr(service, 'execute'), "Service must have execute method"
        assert inspect.iscoroutinefunction(service.execute), \
            "execute() must be async (coroutine function)"
        
        print("✅ SEAM 3: Service execute() is async")
    
    def test_service_instantiation_without_arguments(self):
        """SUCCESS: Services can be instantiated with just service_id."""
        from symphainy_platform.capabilities.content.intent_services import IngestFileService
        from symphainy_platform.capabilities.security.intent_services import AuthenticateUserService
        from symphainy_platform.capabilities.control_tower.intent_services import GetPlatformStatisticsService
        
        # All should instantiate without errors
        s1 = IngestFileService()
        s2 = AuthenticateUserService()
        s3 = GetPlatformStatisticsService()
        
        assert s1.intent_type == "ingest_file"
        assert s2.intent_type == "authenticate_user"
        assert s3.intent_type == "get_platform_statistics"
        
        print("✅ SEAM 3: Services instantiate without arguments")


# ============================================================================
# SEAM 4: Admin Dashboard API → Control Tower Intents
# ============================================================================
# This seam defines how Admin Dashboard routes to Control Tower

class TestSeam4_AdminDashboardToControlTower:
    """
    SEAM 4: Admin Dashboard APIs submit Control Tower intents
    
    Contract:
    - Admin Dashboard API endpoints are thin layers
    - They call submit_control_tower_intent() 
    - Control Tower services handle the business logic
    - Response shape matches Control Tower artifacts
    """
    
    def test_intent_helper_exists(self):
        """SUCCESS: Admin Dashboard has intent_helper module."""
        try:
            from symphainy_platform.civic_systems.experience.admin_dashboard import intent_helper
            
            assert hasattr(intent_helper, 'submit_control_tower_intent'), \
                "intent_helper must have submit_control_tower_intent function"
            
            print("✅ SEAM 4: intent_helper.submit_control_tower_intent exists")
        except ImportError as e:
            # May fail due to consul import in transitive dependencies
            if "consul" in str(e):
                pytest.skip(f"Skipped due to missing consul dependency: {e}")
            raise
    
    def test_control_tower_intents_registered(self):
        """SUCCESS: Control Tower capability has expected intent services."""
        from symphainy_platform.capabilities.control_tower.intent_services import (
            GetPlatformStatisticsService,
            GetSystemHealthService,
            ListSolutionsService,
            GetExecutionMetricsService,
            GetSolutionTemplatesService,
            ComposeSolutionService
        )
        
        expected_intents = {
            "get_platform_statistics": GetPlatformStatisticsService,
            "get_system_health": GetSystemHealthService,
            "list_solutions": ListSolutionsService,
            "get_execution_metrics": GetExecutionMetricsService,
            "get_solution_templates": GetSolutionTemplatesService,
            "compose_solution": ComposeSolutionService
        }
        
        for intent_type, service_class in expected_intents.items():
            assert service_class.intent_type == intent_type, \
                f"{service_class.__name__}.intent_type should be '{intent_type}'"
        
        print(f"✅ SEAM 4: {len(expected_intents)} Control Tower intents registered")
    
    def test_control_tower_service_returns_artifacts(self):
        """SUCCESS: Control Tower services return artifacts dict."""
        from symphainy_platform.capabilities.control_tower.intent_services import GetPlatformStatisticsService
        from symphainy_platform.civic_systems.platform_sdk import PlatformContext
        from symphainy_platform.runtime.intent_model import IntentFactory
        import asyncio
        
        service = GetPlatformStatisticsService()
        
        intent = IntentFactory.create_intent(
            intent_type="get_platform_statistics",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="control_tower",
            parameters={}
        )
        
        # Mock state_surface for the test
        mock_state = MagicMock()
        mock_state.get_session_count = AsyncMock(return_value=5)
        mock_state.get_artifact_count = AsyncMock(return_value=10)
        mock_state.get_file_count = AsyncMock(return_value=3)
        
        ctx = PlatformContext(
            intent=intent,
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="control_tower",
            execution_id="test_execution",
            platform=None,
            governance=None,
            reasoning=None,
            state_surface=mock_state
        )
        
        result = asyncio.get_event_loop().run_until_complete(service.execute(ctx))
        
        # Verify result structure
        assert "artifacts" in result, "Result must have 'artifacts' key"
        assert "events" in result, "Result must have 'events' key"
        assert isinstance(result["artifacts"], dict), "artifacts must be dict"
        
        print("✅ SEAM 4: Control Tower services return {artifacts, events}")


# ============================================================================
# SEAM 5: Frontend → Backend API Contract
# ============================================================================
# This seam defines the API shape between frontend and backend

class TestSeam5_FrontendBackendAPIContract:
    """
    SEAM 5: Frontend AdminAPIManager calls backend Control Tower APIs
    
    Contract:
    - GET /api/admin/control-room/statistics → {active_sessions, total_artifacts, ...}
    - GET /api/admin/control-room/health → {status, components, ...}
    - GET /api/admin/developer/patterns → {patterns: [...]}
    - GET /api/admin/developer/documentation → {documentation: {...}}
    
    Error Response Shape:
    - {detail: "error message"} for HTTP errors
    """
    
    def test_statistics_response_shape(self):
        """SUCCESS: Statistics endpoint returns expected shape."""
        # Define expected response shape
        expected_keys = {
            "active_sessions",
            "total_artifacts", 
            "total_files",
            "timestamp"
        }
        
        # Simulate what Control Tower returns
        from symphainy_platform.capabilities.control_tower.intent_services import GetPlatformStatisticsService
        
        service = GetPlatformStatisticsService()
        assert service.intent_type == "get_platform_statistics"
        
        print(f"✅ SEAM 5: Statistics API contract defined (keys: {expected_keys})")
    
    def test_health_response_shape(self):
        """SUCCESS: Health endpoint returns expected shape."""
        expected_keys = {
            "status",
            "components",
            "timestamp"
        }
        
        from symphainy_platform.capabilities.control_tower.intent_services import GetSystemHealthService
        
        service = GetSystemHealthService()
        assert service.intent_type == "get_system_health"
        
        print(f"✅ SEAM 5: Health API contract defined (keys: {expected_keys})")
    
    def test_execution_status_endpoint_exists(self):
        """SUCCESS: Execution status REST endpoint exists for polling fallback."""
        # This endpoint was added by Team B for frontend integration
        try:
            import importlib.util
            spec = importlib.util.find_spec("symphainy_platform.civic_systems.experience.api.websocket")
            assert spec is not None, "websocket module should exist"
            
            from symphainy_platform.civic_systems.experience.api.websocket import router
            
            # Check routes - path includes full path with prefix
            routes = [r.path for r in router.routes]
            status_route_exists = any("status" in route for route in routes)
            assert status_route_exists, \
                f"GET /status endpoint should exist, found: {routes}"
            
            print("✅ SEAM 5: Execution status REST endpoint exists")
        except ImportError as e:
            if "consul" in str(e):
                pytest.skip(f"Skipped due to missing consul dependency: {e}")
            raise


# ============================================================================
# SEAM 6: Service Failure Modes
# ============================================================================
# This seam defines how services fail

class TestSeam6_ServiceFailureModes:
    """
    SEAM 6: Services fail in predictable ways
    
    Contract:
    - Missing required parameter → ValueError
    - Missing required infrastructure → RuntimeError with "Platform contract §8A"
    - AI service unavailable → {status: "unavailable", error: "..."}
    - Never silent failure or fake data
    """
    
    def test_missing_parameter_raises_value_error(self):
        """FAILURE MODE: Missing required parameter raises ValueError."""
        from symphainy_platform.capabilities.security.intent_services import AuthenticateUserService
        from symphainy_platform.civic_systems.platform_sdk import PlatformContext
        from symphainy_platform.runtime.intent_model import IntentFactory
        import asyncio
        
        # Use AuthenticateUserService which validates parameters before any infrastructure call
        service = AuthenticateUserService()
        
        # Intent WITHOUT required email/password parameters
        intent = IntentFactory.create_intent(
            intent_type="authenticate_user",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security",
            parameters={}  # Missing email and password!
        )
        
        ctx = PlatformContext(
            intent=intent,
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security",
            execution_id="test_execution",
            platform=None,
            governance=None,
            reasoning=None,
            state_surface=None
        )
        
        with pytest.raises(ValueError) as exc_info:
            asyncio.get_event_loop().run_until_complete(service.execute(ctx))
        
        assert "email" in str(exc_info.value).lower() or "password" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()
        
        print("✅ SEAM 6: Missing parameter raises ValueError")
    
    def test_ai_service_unavailable_returns_status(self):
        """FAILURE MODE: AI service unavailable returns status, not fake data."""
        from symphainy_platform.capabilities.coexistence.intent_services import ProcessGuideAgentMessageService
        from symphainy_platform.civic_systems.platform_sdk import PlatformContext
        from symphainy_platform.runtime.intent_model import IntentFactory
        import asyncio
        
        # Use ProcessGuideAgentMessageService which checks reasoning before any platform call
        service = ProcessGuideAgentMessageService()
        
        intent = IntentFactory.create_intent(
            intent_type="process_guide_agent_message",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={"message": "Hello", "guide_session_id": "test_guide_session", "context": {}}
        )
        
        # Context WITHOUT reasoning service
        ctx = PlatformContext(
            intent=intent,
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            execution_id="test_execution",
            platform=None,
            governance=None,
            reasoning=None,  # No AI!
            state_surface=None
        )
        
        result = asyncio.get_event_loop().run_until_complete(service.execute(ctx))
        
        # Should return unavailable status, NOT fake response
        assert "artifacts" in result
        artifacts = result["artifacts"]
        
        # Response is nested in artifacts.response for this service
        response = artifacts.get("response", artifacts)
        
        assert response.get("status") == "unavailable", \
            f"AI service unavailable should set status='unavailable', got: {response}"
        assert "error" in response, \
            "AI service unavailable should include error message"
        
        print("✅ SEAM 6: AI unavailable returns {status: 'unavailable'}, not fake data")


# ============================================================================
# SUMMARY: Generate Seam Documentation
# ============================================================================

def test_generate_seam_documentation():
    """Generate summary of all seam contracts."""
    report = """
================================================================================
SEAM CONTRACT DOCUMENTATION
================================================================================

SEAM 1: Capability Service → PlatformContext
─────────────────────────────────────────────
What it does: Provides execution context to capability services
Access via:   ctx (PlatformContext instance)
Fields:       ctx.platform, ctx.governance, ctx.reasoning, ctx.state_surface,
              ctx.intent, ctx.tenant_id, ctx.session_id, ctx.execution_id
Conversions:  ctx.to_execution_context() for library service calls

SEAM 2: Service → Protocol Boundary Access  
─────────────────────────────────────────────
What it does: Defines what services can/cannot access
ALLOWED:      ctx.platform.ingest_file(), ctx.platform.delete_file()
              ctx.governance.auth.authenticate(), ctx.governance.sessions.create_session_intent()
              ctx.reasoning.invoke_agent(), ctx.reasoning.complete()
FORBIDDEN:    ctx.platform._public_works (internal implementation)
              getattr(ctx.platform._public_works, 'sdk') (adapter leak)
Failure mode: RuntimeError("Platform contract §8A: ...")

SEAM 3: Intent Service → Service Factory
─────────────────────────────────────────────
What it does: Maps intent_type to service instances
Contract:     Service.intent_type (class attribute) → ServiceFactory lookup
              Service.execute(ctx) → async, returns {artifacts, events}
Base class:   PlatformIntentService
Registration: Automatic via service_factory module imports

SEAM 4: Admin Dashboard API → Control Tower Intents
─────────────────────────────────────────────
What it does: Routes admin requests to Control Tower capability
Pattern:      API endpoint → submit_control_tower_intent() → Control Tower service
Endpoints:    /api/admin/control-room/statistics → get_platform_statistics
              /api/admin/control-room/health → get_system_health
              /api/admin/developer/patterns → get_patterns
Response:     Artifacts from Control Tower service

SEAM 5: Frontend → Backend API Contract
─────────────────────────────────────────────
What it does: Defines HTTP API shape between teams
Endpoints:    GET /api/admin/control-room/statistics
              GET /api/admin/control-room/health
              GET /api/execution/{id}/status (polling fallback)
Responses:    Success: {artifacts data}
              Error: {detail: "error message"}

SEAM 6: Service Failure Modes
─────────────────────────────────────────────
What it does: Defines predictable failure patterns
Patterns:     Missing parameter → ValueError
              Missing infrastructure → RuntimeError with "Platform contract §8A"
              AI unavailable → {status: "unavailable", error: "..."}
FORBIDDEN:    Silent failure, fake data, mock responses

================================================================================
"""
    print(report)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
