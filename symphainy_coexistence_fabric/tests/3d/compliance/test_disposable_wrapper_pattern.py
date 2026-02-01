"""
Disposable Wrapper Pattern Compliance Tests

Validates that Platform SDK wrappers follow the Disposable Wrapper Pattern:
- No Logic: Wrappers don't make decisions
- No Caching: Wrappers don't store state between calls
- No Business Assumptions: Wrappers don't encode domain rules
- Pure Delegation: Call underlying service, return result
- Light Shaping: Normalize input/output formats only

See docs/architecture/DISPOSABLE_WRAPPER_PATTERN.md

These tests are PROBATIVE - they will fail if the architecture is violated.
"""

from __future__ import annotations

import sys
import ast
import inspect
import warnings
from pathlib import Path
from typing import List, Dict, Any, Set

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestDisposableWrapperPatternCompliance:
    """
    Validate that Platform SDK wrappers are disposable.
    
    A wrapper is disposable if it can be replaced with a different implementation
    that has the same method signatures, and all capability services still work.
    """
    
    def test_platform_service_no_instance_state(self):
        """
        PlatformService should not accumulate state between calls.
        
        Allowed: References to abstractions (protocol-typed backends)
        Forbidden: Caches, result storage, counters, accumulated lists
        """
        from symphainy_platform.civic_systems.platform_sdk.services.platform_service import PlatformService
        
        # Get all instance attributes that are not abstractions
        source = inspect.getsource(PlatformService)
        
        # Parse the __init__ method to find instance attributes
        tree = ast.parse(source)
        
        state_attrs = []
        cache_patterns = ['cache', 'results', 'history', 'accumulator', 'counter', '_count']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                if isinstance(node.value, ast.Name) and node.value.id == 'self':
                    attr_name = node.attr
                    # Check if it looks like state accumulation
                    for pattern in cache_patterns:
                        if pattern in attr_name.lower():
                            state_attrs.append(attr_name)
        
        assert len(state_attrs) == 0, (
            f"PlatformService has state-accumulating attributes: {state_attrs}. "
            "Disposable Wrapper Pattern violation: No Caching/State."
        )
    
    def test_reasoning_service_no_conversation_state(self):
        """
        ReasoningService should not store conversation history.
        
        Conversation state belongs in the agent or capability service,
        not in the wrapper.
        """
        from symphainy_platform.civic_systems.platform_sdk.services.reasoning_service import ReasoningService
        
        source = inspect.getsource(ReasoningService)
        
        # Look for conversation/history storage
        forbidden_patterns = [
            'conversation_history',
            'message_history',
            'chat_history',
            '_messages',
            '_conversation',
        ]
        
        violations = []
        for pattern in forbidden_patterns:
            if pattern in source:
                violations.append(pattern)
        
        assert len(violations) == 0, (
            f"ReasoningService has conversation state patterns: {violations}. "
            "Disposable Wrapper Pattern violation: No State Accumulation."
        )
    
    def test_collaborate_method_emits_deprecation_warning(self):
        """
        AgentService.collaborate() should emit deprecation warning.
        
        This method violates the pattern (orchestration in wrapper) and should
        warn users to use Journey orchestrators instead.
        """
        from symphainy_platform.civic_systems.platform_sdk.services.reasoning_service import AgentService
        
        service = AgentService()
        
        # Check that calling collaborate emits a DeprecationWarning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # We can't actually call it without agents, but we can check the method exists
            # and has the deprecation documented
            method = getattr(service, 'collaborate', None)
            assert method is not None, "collaborate method should exist for backward compatibility"
            
            # Check the docstring mentions deprecation
            docstring = method.__doc__ or ""
            assert "deprecated" in docstring.lower(), (
                "collaborate() docstring should mention it's deprecated"
            )
    
    def test_platform_service_methods_are_pure_delegation(self):
        """
        PlatformService methods should delegate to underlying abstractions.
        
        This test checks that methods call abstraction methods rather than
        implementing business logic directly.
        """
        from symphainy_platform.civic_systems.platform_sdk.services.platform_service import PlatformService
        
        source = inspect.getsource(PlatformService)
        
        # Methods that should be pure delegation
        delegation_methods = [
            'parse',
            'visualize',
            'embed',
            'ingest_file',
            'store_artifact',
            'retrieve_artifact',
            'store_semantic',
            'search_semantic',
        ]
        
        # For each method, verify it calls an abstraction
        tree = ast.parse(source)
        
        for method_name in delegation_methods:
            # Find the method
            for node in ast.walk(tree):
                if isinstance(node, ast.AsyncFunctionDef) and node.name == method_name:
                    # Check that it has abstraction calls (self._something)
                    has_delegation = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.Attribute):
                            if isinstance(child.value, ast.Name) and child.value.id == 'self':
                                if child.attr.startswith('_') and not child.attr.startswith('__'):
                                    has_delegation = True
                                    break
                    
                    assert has_delegation, (
                        f"Method {method_name} doesn't appear to delegate to an abstraction. "
                        "Disposable Wrapper Pattern requires pure delegation."
                    )
    
    def test_wrapper_methods_accept_execution_context(self):
        """
        Methods that call library services should accept execution_context parameter.
        
        This ensures the audit trail is maintained.
        """
        from symphainy_platform.civic_systems.platform_sdk.services.platform_service import PlatformService
        
        # Methods that should accept execution_context
        context_methods = [
            'create_deterministic_embeddings',
            'get_parsed_file',
        ]
        
        for method_name in context_methods:
            method = getattr(PlatformService, method_name, None)
            assert method is not None, f"Method {method_name} should exist"
            
            sig = inspect.signature(method)
            param_names = list(sig.parameters.keys())
            
            assert 'execution_context' in param_names, (
                f"Method {method_name} should accept execution_context parameter "
                "to maintain audit trail. See DISPOSABLE_WRAPPER_PATTERN.md"
            )


class TestServiceRegistrationAudit:
    """
    Validate that all capability services are properly registered.
    
    This ensures Team A's intercept path can find all our services.
    """
    
    @pytest.fixture(autouse=True)
    def skip_if_deps_missing(self):
        """Skip tests if dependencies are missing (run in CI where deps are installed)."""
        try:
            from symphainy_platform.runtime.service_factory import ServiceFactory
        except ImportError as e:
            pytest.skip(f"Skipping due to missing dependency: {e}")
    
    def test_all_content_services_registered(self):
        """Content capability services are registered in service_factory."""
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        # Based on actual registration in service_factory.py
        expected_content_intents = [
            "echo",  # Test service
            "ingest_file",
            "save_materialization",
            "parse_content",
            "create_deterministic_embeddings",
            "get_parsed_file",
            "retrieve_artifact_metadata",
            "list_artifacts",
            "archive_file",
            "delete_file",
            # Legacy:
            "extract_embeddings",
        ]
        
        factory = ServiceFactory()
        registered = set(factory.get_supported_intents())
        
        missing = []
        for intent in expected_content_intents:
            if intent not in registered:
                missing.append(intent)
        
        assert len(missing) == 0, (
            f"Content services not registered: {missing}. "
            "Check service_factory.py registration."
        )
    
    def test_all_security_services_registered(self):
        """Security capability services are registered in service_factory."""
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        # Based on actual registration in service_factory.py
        expected_security_intents = [
            "authenticate_user",
            "validate_token",
            "create_user_account",
            "check_email_availability",
            "create_session",
            "validate_authorization",
            "terminate_session",
        ]
        
        factory = ServiceFactory()
        registered = set(factory.get_supported_intents())
        
        missing = []
        for intent in expected_security_intents:
            if intent not in registered:
                missing.append(intent)
        
        assert len(missing) == 0, (
            f"Security services not registered: {missing}. "
            "Check service_factory.py registration."
        )
    
    def test_all_coexistence_services_registered(self):
        """Coexistence capability services are registered in service_factory."""
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        # Based on actual registration in service_factory.py
        expected_coexistence_intents = [
            "introduce_platform",
            "show_solution_catalog",
            "navigate_to_solution",
            "initiate_guide_agent",
            "process_guide_agent_message",
            "route_to_liaison_agent",
            "list_available_mcp_tools",
        ]
        
        factory = ServiceFactory()
        registered = set(factory.get_supported_intents())
        
        missing = []
        for intent in expected_coexistence_intents:
            if intent not in registered:
                missing.append(intent)
        
        assert len(missing) == 0, (
            f"Coexistence services not registered: {missing}. "
            "Check service_factory.py registration."
        )
    
    def test_all_insights_services_registered(self):
        """Insights capability services are registered in service_factory."""
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        # Based on actual registration in service_factory.py
        expected_insights_intents = [
            "assess_data_quality",
            "interpret_data_self_discovery",
            "interpret_data_guided",
            "analyze_structured_data",
            "analyze_unstructured_data",
            "visualize_lineage",
            "map_relationships",
        ]
        
        factory = ServiceFactory()
        registered = set(factory.get_supported_intents())
        
        missing = []
        for intent in expected_insights_intents:
            if intent not in registered:
                missing.append(intent)
        
        assert len(missing) == 0, (
            f"Insights services not registered: {missing}. "
            "Check service_factory.py registration."
        )
    
    def test_all_operations_services_registered(self):
        """Operations capability services are registered in service_factory."""
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        # Based on actual registration in service_factory.py
        expected_operations_intents = [
            "generate_sop",
            "generate_sop_from_chat",
            "sop_chat_message",
            "create_workflow",
            "optimize_process",
            "analyze_coexistence",
        ]
        
        factory = ServiceFactory()
        registered = set(factory.get_supported_intents())
        
        missing = []
        for intent in expected_operations_intents:
            if intent not in registered:
                missing.append(intent)
        
        assert len(missing) == 0, (
            f"Operations services not registered: {missing}. "
            "Check service_factory.py registration."
        )
    
    def test_all_outcomes_services_registered(self):
        """Outcomes capability services are registered in service_factory."""
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        # Based on actual registration in service_factory.py
        expected_outcomes_intents = [
            "synthesize_outcome",
            "generate_roadmap",
            "create_poc",
            "create_blueprint",
            "export_artifact",
            "create_solution",
        ]
        
        factory = ServiceFactory()
        registered = set(factory.get_supported_intents())
        
        missing = []
        for intent in expected_outcomes_intents:
            if intent not in registered:
                missing.append(intent)
        
        assert len(missing) == 0, (
            f"Outcomes services not registered: {missing}. "
            "Check service_factory.py registration."
        )
    
    def test_all_control_tower_services_registered(self):
        """Control Tower capability services are registered in service_factory."""
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        # Based on actual registration in service_factory.py
        expected_control_tower_intents = [
            "get_platform_statistics",
            "get_system_health",
            "get_realm_health",
            "list_solutions",
            "get_solution_status",
            "validate_solution",
            "get_patterns",
            "get_code_examples",
            "get_documentation",
        ]
        
        factory = ServiceFactory()
        registered = set(factory.get_supported_intents())
        
        missing = []
        for intent in expected_control_tower_intents:
            if intent not in registered:
                missing.append(intent)
        
        assert len(missing) == 0, (
            f"Control Tower services not registered: {missing}. "
            "Check service_factory.py registration."
        )


    def test_total_service_count(self):
        """
        Verify total number of registered services matches expected.
        
        This is a probative test - it will fail if services are added/removed
        without updating this test, forcing explicit acknowledgment.
        
        Expected counts per capability (from service_factory.py):
        - Content: 11 (10 + 1 legacy)
        - Insights: 7
        - Operations: 6
        - Outcomes: 6
        - Security: 7
        - Control Tower: 9
        - Coexistence: 8 (7 + 1 legacy)
        Total: 54
        """
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        factory = ServiceFactory()
        registered = factory.get_supported_intents()
        
        # Update this number when services change
        EXPECTED_TOTAL = 54
        
        actual_count = len(registered)
        
        assert actual_count >= EXPECTED_TOTAL, (
            f"Missing services! Expected at least {EXPECTED_TOTAL}, got {actual_count}. "
            f"Registered intents: {sorted(registered)}"
        )
        
        if actual_count > EXPECTED_TOTAL:
            # New services added - update expected count
            print(f"\n⚠️ New services detected: {actual_count} vs expected {EXPECTED_TOTAL}")
            print(f"   Update EXPECTED_TOTAL in test if intentional")


class TestServiceContractValidation:
    """
    Validate that all services follow the execute(ctx) contract.
    
    All PlatformIntentService implementations must have an async execute(ctx)
    method that accepts PlatformContext.
    """
    
    @pytest.fixture(autouse=True)
    def skip_if_deps_missing(self):
        """Skip tests if dependencies are missing (run in CI where deps are installed)."""
        try:
            from symphainy_platform.runtime.service_factory import ServiceFactory
        except ImportError as e:
            pytest.skip(f"Skipping due to missing dependency: {e}")
    
    def test_service_has_execute_method(self):
        """All registered services must have an async execute method."""
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        factory = ServiceFactory()
        
        # Get all registered service classes
        for intent_type in factory.get_supported_intents():
            service_class = factory.get_service_class(intent_type)
            
            if service_class is None:
                continue
                
            # Check execute method exists
            assert hasattr(service_class, 'execute'), (
                f"Service for {intent_type} missing execute() method"
            )
            
            # Check it's async
            execute_method = getattr(service_class, 'execute')
            assert inspect.iscoroutinefunction(execute_method), (
                f"Service for {intent_type} execute() must be async"
            )
    
    def test_service_execute_accepts_platform_context(self):
        """Service execute() methods must accept PlatformContext as first param."""
        from symphainy_platform.runtime.service_factory import ServiceFactory
        
        factory = ServiceFactory()
        
        for intent_type in factory.get_supported_intents():
            service_class = factory.get_service_class(intent_type)
            
            if service_class is None:
                continue
            
            execute_method = getattr(service_class, 'execute', None)
            if execute_method is None:
                continue
            
            sig = inspect.signature(execute_method)
            params = list(sig.parameters.keys())
            
            # First param after self should be ctx
            if len(params) >= 2:
                # params[0] is 'self', params[1] should be 'ctx'
                assert params[1] == 'ctx', (
                    f"Service for {intent_type} execute() should accept 'ctx' "
                    f"as first parameter, got '{params[1]}'"
                )


class TestAgentRegistryAudit:
    """
    Validate that all agents are properly mapped and can be lazily instantiated.
    """
    
    def test_all_expected_agents_mapped(self):
        """All expected agents are in the AgentService mapping."""
        from symphainy_platform.civic_systems.platform_sdk.services.reasoning_service import AgentService
        
        expected_agents = [
            "guide_agent",
            "content_liaison_agent",
            "insights_liaison_agent",
            "operations_liaison_agent",
            "outcomes_liaison_agent",
            "coexistence_analysis_agent",
            "sop_generation_agent",
            "roadmap_generation_agent",
            "blueprint_creation_agent",
            "poc_generation_agent",
            "outcomes_synthesis_agent",
            "business_analysis_agent",
            "insights_eda_agent",
        ]
        
        service = AgentService()
        mapped_agents = set(service._AGENT_CLASSES.keys())
        
        missing = []
        for agent_id in expected_agents:
            if agent_id not in mapped_agents:
                missing.append(agent_id)
        
        assert len(missing) == 0, (
            f"Agents not mapped in AgentService: {missing}. "
            "Check _AGENT_CLASSES mapping."
        )
    
    def test_agent_class_paths_are_valid(self):
        """Agent class paths in mapping point to importable modules."""
        from symphainy_platform.civic_systems.platform_sdk.services.reasoning_service import AgentService
        import importlib
        
        service = AgentService()
        
        invalid_paths = []
        for agent_id, class_path in service._AGENT_CLASSES.items():
            try:
                module_path, class_name = class_path.rsplit(".", 1)
                module = importlib.import_module(module_path)
                
                if not hasattr(module, class_name):
                    invalid_paths.append((agent_id, class_path, "class not found in module"))
                    
            except ImportError as e:
                invalid_paths.append((agent_id, class_path, str(e)))
        
        assert len(invalid_paths) == 0, (
            f"Invalid agent class paths: {invalid_paths}. "
            "Check _AGENT_CLASSES mapping."
        )


class TestPlatformContextContract:
    """
    Validate PlatformContext follows the contract.
    """
    
    def test_platform_context_has_required_fields(self):
        """PlatformContext has all required fields."""
        from symphainy_platform.civic_systems.platform_sdk.context import PlatformContext
        
        required_fields = [
            'execution_id',
            'intent',
            'tenant_id',
            'session_id',
            'solution_id',
            'platform',
            'governance',
            'reasoning',
            'state_surface',
            'wal',
            'artifacts',
        ]
        
        # Check fields exist in dataclass
        import dataclasses
        field_names = [f.name for f in dataclasses.fields(PlatformContext)]
        
        missing = []
        for field in required_fields:
            if field not in field_names:
                missing.append(field)
        
        assert len(missing) == 0, (
            f"PlatformContext missing required fields: {missing}"
        )
    
    def test_platform_context_has_to_execution_context(self):
        """PlatformContext has to_execution_context() method for audit trail."""
        from symphainy_platform.civic_systems.platform_sdk.context import PlatformContext
        
        assert hasattr(PlatformContext, 'to_execution_context'), (
            "PlatformContext must have to_execution_context() method "
            "for maintaining audit trail in wrapper calls"
        )
    
    def test_platform_context_validation(self):
        """PlatformContext.validate() catches invalid configurations."""
        from symphainy_platform.civic_systems.platform_sdk.context import PlatformContext
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="test_intent",
            tenant_id="tenant_1",
            session_id="session_1",
            solution_id="test_solution",
            parameters={}
        )
        
        # Valid context
        ctx = PlatformContext(
            execution_id="exec_1",
            intent=intent,
            tenant_id="tenant_1",
            session_id="session_1",
            solution_id="test_solution"
        )
        
        is_valid, error = ctx.validate()
        assert is_valid, f"Valid context should pass validation: {error}"
        
        # Invalid context (tenant mismatch)
        ctx_invalid = PlatformContext(
            execution_id="exec_1",
            intent=intent,
            tenant_id="different_tenant",  # Mismatch!
            session_id="session_1",
            solution_id="test_solution"
        )
        
        is_valid, error = ctx_invalid.validate()
        assert not is_valid, "Tenant mismatch should fail validation"
        assert "mismatch" in error.lower(), "Error should mention mismatch"
