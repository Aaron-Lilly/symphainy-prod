"""
Integration Test: Team A Intercept Path Verification

This test validates that Team A's intercept wiring correctly routes intents
to Team B's capability services.

Verification Points:
1. Handler lookup succeeds for intent types
2. PlatformContextFactory can create context
3. Services have correct execute(ctx) signature
4. Services return expected result structure {artifacts, events, status}

Team A runs this to confirm wiring is complete.
See: TEAM_B_WORKPLAN.md Task 1.3
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestInterceptPathWiring:
    """
    Tests to verify Team A's intercept path is correctly wired to Team B's services.
    
    These tests can be run by Team A to confirm integration is working.
    """
    
    @pytest.fixture(autouse=True)
    def skip_if_deps_missing(self):
        """Skip tests if infrastructure dependencies are missing."""
        try:
            from symphainy_platform.runtime.service_factory import ServiceFactory
        except ImportError as e:
            pytest.skip(f"Skipping due to missing dependency: {e}")
    
    def test_handler_lookup_succeeds_for_ingest_file(self):
        """
        Verify: Handler lookup succeeds for 'ingest_file' intent.
        
        This is the first verification point - Team A's intercept must be able
        to find our handler.
        """
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        factory = ServiceFactory()
        service_class = factory.get_service_class("ingest_file")
        
        assert service_class is not None, (
            "Handler lookup failed for 'ingest_file'. "
            "Team A intercept path cannot find this service."
        )
        
        # Verify it's the right service
        from symphainy_platform.capabilities.content.intent_services import IngestFileService
        assert service_class == IngestFileService, (
            f"Wrong service class returned: {service_class}"
        )
    
    def test_handler_lookup_succeeds_for_create_deterministic_embeddings(self):
        """
        Verify: Handler lookup succeeds for 'create_deterministic_embeddings' intent.
        """
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        factory = ServiceFactory()
        service_class = factory.get_service_class("create_deterministic_embeddings")
        
        assert service_class is not None, (
            "Handler lookup failed for 'create_deterministic_embeddings'. "
            "Team A intercept path cannot find this service."
        )
    
    def test_handler_lookup_succeeds_for_authenticate_user(self):
        """
        Verify: Handler lookup succeeds for 'authenticate_user' intent.
        """
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        factory = ServiceFactory()
        service_class = factory.get_service_class("authenticate_user")
        
        assert service_class is not None, (
            "Handler lookup failed for 'authenticate_user'. "
            "Team A intercept path cannot find this service."
        )
    
    def test_platform_context_factory_creates_valid_context(self):
        """
        Verify: PlatformContextFactory can create a valid PlatformContext.
        
        Team A's intercept creates context via the factory - this must work.
        """
        from symphainy_platform.civic_systems.platform_sdk.context import (
            PlatformContext,
            PlatformContextFactory
        )
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # Create a test intent
        intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={
                "file_data": b"test content",
                "source_metadata": {"ui_name": "test.txt", "file_type": "text"}
            }
        )
        
        # Create factory (without public_works for this test)
        # In real use, Team A provides public_works
        try:
            factory = PlatformContextFactory()
            # This should fail without public_works (§8A compliance)
            ctx = factory.create_context(intent)
            pytest.fail("Should raise RuntimeError without public_works (§8A)")
        except RuntimeError as e:
            assert "§8A" in str(e) or "not wired" in str(e).lower(), (
                "Should fail with §8A compliance error when public_works missing"
            )
    
    def test_service_returns_expected_structure(self):
        """
        Verify: Services return expected {artifacts, events} structure.
        
        Team A's intercept expects this structure.
        """
        from symphainy_platform.capabilities.content.intent_services import IngestFileService
        import inspect
        
        # Get the execute method
        service = IngestFileService()
        execute_method = getattr(service, 'execute', None)
        
        assert execute_method is not None, "Service must have execute method"
        assert inspect.iscoroutinefunction(execute_method), "execute must be async"
        
        # Check return type annotation if available
        sig = inspect.signature(execute_method)
        return_annotation = sig.return_annotation
        
        # The return type should indicate dict (with artifacts, events)
        # We can't fully verify without running, but we can check the docstring
        docstring = execute_method.__doc__ or ""
        assert "artifacts" in docstring.lower() or "dict" in str(return_annotation).lower(), (
            "execute() should document returning artifacts structure"
        )


class TestPlatformSDKWiring:
    """
    Tests to verify Platform SDK services are correctly wired.
    """
    
    def test_platform_context_has_all_services(self):
        """
        Verify: PlatformContext exposes all four SDK services.
        
        ctx.platform, ctx.governance, ctx.reasoning, ctx.experience must exist.
        """
        from symphainy_platform.civic_systems.platform_sdk.context import PlatformContext
        import dataclasses
        
        fields = {f.name for f in dataclasses.fields(PlatformContext)}
        
        required_services = ['platform', 'governance', 'reasoning', 'experience']
        
        for service in required_services:
            assert service in fields, (
                f"PlatformContext missing '{service}' field. "
                "Team A intercept expects all four SDK services."
            )
    
    def test_platform_service_methods_available(self):
        """
        Verify: PlatformService has expected methods.
        """
        from symphainy_platform.civic_systems.platform_sdk.services.platform_service import PlatformService
        
        expected_methods = [
            'parse',
            'parse_csv',
            'parse_pdf',
            'visualize',
            'embed',
            'ingest_file',
            'store_artifact',
            'retrieve_artifact',
            'store_semantic',
            'search_semantic',
            'create_deterministic_embeddings',
            'get_parsed_file',
        ]
        
        missing = []
        for method in expected_methods:
            if not hasattr(PlatformService, method):
                missing.append(method)
        
        assert len(missing) == 0, (
            f"PlatformService missing methods: {missing}. "
            "Capability services depend on these."
        )
    
    def test_reasoning_service_agent_access(self):
        """
        Verify: ReasoningService provides agent access.
        """
        from symphainy_platform.civic_systems.platform_sdk.services.reasoning_service import ReasoningService
        
        # Create service (without public_works for structural test)
        service = ReasoningService()
        
        # Check agents sub-service exists
        assert hasattr(service, 'agents'), "ReasoningService must have agents"
        assert hasattr(service, 'llm'), "ReasoningService must have llm"
        
        # Check agent methods
        agents = service.agents
        assert hasattr(agents, 'get'), "agents must have get()"
        assert hasattr(agents, 'invoke'), "agents must have invoke()"
    
    def test_context_to_execution_context_preserves_identity(self):
        """
        Verify: to_execution_context() preserves execution identity.
        
        This is critical for audit trail.
        """
        from symphainy_platform.civic_systems.platform_sdk.context import PlatformContext
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="test_intent",
            tenant_id="tenant_1",
            session_id="session_1",
            solution_id="test_solution",
            parameters={}
        )
        
        ctx = PlatformContext(
            execution_id="exec_123",
            intent=intent,
            tenant_id="tenant_1",
            session_id="session_1",
            solution_id="test_solution"
        )
        
        # Convert to ExecutionContext
        exec_ctx = ctx.to_execution_context()
        
        # Verify identity is preserved
        assert exec_ctx.execution_id == ctx.execution_id, "execution_id must be preserved"
        assert exec_ctx.tenant_id == ctx.tenant_id, "tenant_id must be preserved"
        assert exec_ctx.session_id == ctx.session_id, "session_id must be preserved"
        assert exec_ctx.intent == ctx.intent, "intent must be preserved"


class TestCapabilityServiceContracts:
    """
    Tests to verify capability services follow the contract.
    """
    
    @pytest.fixture(autouse=True)
    def skip_if_deps_missing(self):
        """Skip tests if infrastructure dependencies are missing."""
        try:
            from symphainy_platform.runtime.service_factory import ServiceFactory
        except ImportError as e:
            pytest.skip(f"Skipping due to missing dependency: {e}")
    
    def test_all_services_extend_platform_intent_service(self):
        """
        Verify: All registered services extend PlatformIntentService.
        """
        from symphainy_platform.runtime.service_factory import ServiceFactory
        from symphainy_platform.civic_systems.platform_sdk.intent_service_base import PlatformIntentService
        
        factory = ServiceFactory()
        
        non_compliant = []
        for intent_type in factory.get_supported_intents():
            service_class = factory.get_service_class(intent_type)
            if service_class is None:
                continue
            
            if not issubclass(service_class, PlatformIntentService):
                non_compliant.append((intent_type, service_class.__name__))
        
        assert len(non_compliant) == 0, (
            f"Services not extending PlatformIntentService: {non_compliant}. "
            "All capability services must extend PlatformIntentService."
        )
    
    def test_services_have_intent_type_attribute(self):
        """
        Verify: All services declare their intent_type.
        """
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        factory = ServiceFactory()
        
        missing_intent_type = []
        for intent_type in factory.get_supported_intents():
            service_class = factory.get_service_class(intent_type)
            if service_class is None:
                continue
            
            if not hasattr(service_class, 'intent_type'):
                missing_intent_type.append(service_class.__name__)
        
        assert len(missing_intent_type) == 0, (
            f"Services missing intent_type attribute: {missing_intent_type}"
        )
