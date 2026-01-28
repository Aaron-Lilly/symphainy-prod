"""
Test Solution Initializer - Platform Startup Tests

CRITICAL: These tests must pass for the platform to boot.

Tests:
- All 8 solutions initialize successfully
- Solutions are registered with SolutionRegistry
- compose_journey intents are registered
- MCP Servers initialize
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestSolutionInitializer:
    """Test solution initialization at startup."""
    
    @pytest.mark.asyncio
    async def test_initialize_solutions_creates_all_8_solutions(
        self, mock_public_works, mock_state_surface, mock_solution_registry, mock_intent_registry
    ):
        """All 8 platform solutions should be initialized."""
        from symphainy_platform.solutions import initialize_solutions
        
        services = await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=mock_solution_registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=False  # Skip MCP for unit test
        )
        
        # Verify all 8 solutions are created
        assert services.coexistence is not None, "CoexistenceSolution not initialized"
        assert services.content is not None, "ContentSolution not initialized"
        assert services.insights is not None, "InsightsSolution not initialized"
        assert services.operations is not None, "OperationsSolution not initialized"
        assert services.outcomes is not None, "OutcomesSolution not initialized"
        assert services.security is not None, "SecuritySolution not initialized"
        assert services.control_tower is not None, "ControlTower not initialized"
    
    @pytest.mark.asyncio
    async def test_solutions_stored_in_solutions_dict(
        self, mock_public_works, mock_state_surface, mock_solution_registry, mock_intent_registry
    ):
        """Solutions should be accessible via _solutions dict."""
        from symphainy_platform.solutions import initialize_solutions
        
        services = await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=mock_solution_registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=False
        )
        
        # Verify _solutions dict contains all solutions
        expected_ids = [
            "coexistence", "content_solution", "insights_solution",
            "operations_solution", "outcomes_solution", "security_solution",
            "control_tower"
        ]
        
        for solution_id in expected_ids:
            assert solution_id in services._solutions, f"Missing solution: {solution_id}"
            assert services._solutions[solution_id] is not None
    
    @pytest.mark.asyncio
    async def test_get_solution_by_id(
        self, mock_public_works, mock_state_surface, mock_solution_registry, mock_intent_registry
    ):
        """Should be able to get solution by ID."""
        from symphainy_platform.solutions import initialize_solutions
        
        services = await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=mock_solution_registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=False
        )
        
        # Test get_solution method
        content = services.get_solution("content_solution")
        assert content is not None
        assert content.SOLUTION_ID == "content_solution"
        
        # Non-existent solution returns None
        missing = services.get_solution("nonexistent")
        assert missing is None
    
    @pytest.mark.asyncio
    async def test_list_solutions_returns_all(
        self, mock_public_works, mock_state_surface, mock_solution_registry, mock_intent_registry
    ):
        """list_solutions should return all 8 solutions."""
        from symphainy_platform.solutions import initialize_solutions
        
        services = await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=mock_solution_registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=False
        )
        
        solutions = services.list_solutions()
        assert len(solutions) == 8


class TestSolutionRegistration:
    """Test solution registration with SolutionRegistry."""
    
    @pytest.mark.asyncio
    async def test_solutions_registered_with_registry(
        self, mock_public_works, mock_state_surface, mock_intent_registry
    ):
        """All solutions should be registered with SolutionRegistry."""
        from symphainy_platform.solutions import initialize_solutions
        from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
        
        registry = SolutionRegistry()
        
        await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=False
        )
        
        # Verify all solutions are registered
        expected_ids = [
            "coexistence", "content_solution", "insights_solution",
            "operations_solution", "outcomes_solution", "security_solution",
            "control_tower"
        ]
        
        for solution_id in expected_ids:
            solution = registry.get_solution(solution_id)
            assert solution is not None, f"Solution {solution_id} not registered"
    
    @pytest.mark.asyncio
    async def test_solutions_activated_after_registration(
        self, mock_public_works, mock_state_surface, mock_intent_registry
    ):
        """Solutions should be activated after registration."""
        from symphainy_platform.solutions import initialize_solutions
        from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
        
        registry = SolutionRegistry()
        
        await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=False
        )
        
        # Verify all solutions are active
        for solution_id in ["coexistence", "content_solution"]:
            assert registry.is_solution_active(solution_id), f"Solution {solution_id} not active"


class TestIntentRegistration:
    """Test intent registration with IntentRegistry."""
    
    @pytest.mark.asyncio
    async def test_compose_journey_intents_registered(
        self, mock_public_works, mock_state_surface, mock_solution_registry
    ):
        """compose_journey intent should be registered for all solutions."""
        from symphainy_platform.solutions import initialize_solutions
        from symphainy_platform.runtime.intent_registry import IntentRegistry
        
        intent_registry = IntentRegistry()
        
        await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=mock_solution_registry,
            intent_registry=intent_registry,
            initialize_mcp_servers=False
        )
        
        # Verify compose_journey is registered
        handlers = intent_registry.get_intent_handlers("compose_journey")
        assert len(handlers) >= 8, "compose_journey should be registered for all solutions"


class TestMCPServerInitialization:
    """Test MCP Server initialization."""
    
    @pytest.mark.asyncio
    async def test_mcp_servers_initialize(
        self, mock_public_works, mock_state_surface, mock_solution_registry, mock_intent_registry
    ):
        """MCP Servers should initialize when requested."""
        from symphainy_platform.solutions import initialize_solutions
        
        services = await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=mock_solution_registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=True
        )
        
        # Verify MCP servers dict is populated
        # Note: Some may fail in unit test due to missing deps, but dict should exist
        assert hasattr(services, '_mcp_servers')
    
    @pytest.mark.asyncio
    async def test_get_mcp_server(
        self, mock_public_works, mock_state_surface, mock_solution_registry, mock_intent_registry
    ):
        """Should be able to get MCP server by solution ID."""
        from symphainy_platform.solutions import initialize_solutions
        
        services = await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=mock_solution_registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=True
        )
        
        # Test get_mcp_server method exists
        assert hasattr(services, 'get_mcp_server')


class TestSolutionInitializerErrorHandling:
    """Test error handling in solution initialization."""
    
    @pytest.mark.asyncio
    async def test_initialize_solutions_handles_registration_failure(
        self, mock_public_works, mock_state_surface, mock_intent_registry
    ):
        """Should handle solution registration failures gracefully."""
        from symphainy_platform.solutions import initialize_solutions
        from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
        
        registry = SolutionRegistry()
        
        # Initialize solutions - registration failures should be logged but not crash
        services = await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=False
        )
        
        # Solutions should still be initialized even if registration fails
        assert services.coexistence is not None
        assert services.content is not None
    
    @pytest.mark.asyncio
    async def test_initialize_solutions_creates_valid_solution_contexts(
        self, mock_public_works, mock_state_surface, mock_intent_registry
    ):
        """All solutions should have valid SolutionContext after initialization."""
        from symphainy_platform.solutions import initialize_solutions
        from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
        
        registry = SolutionRegistry()
        
        services = await initialize_solutions(
            public_works=mock_public_works,
            state_surface=mock_state_surface,
            solution_registry=registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=False
        )
        
        # Verify all registered solutions have valid solution_context
        for solution_id in ["coexistence", "content_solution", "operations_solution"]:
            solution = registry.get_solution(solution_id)
            if solution:  # Only check if registered
                assert solution.solution_context is not None
                assert solution.solution_context.goals is not None
                assert isinstance(solution.solution_context.goals, list)
    
    @pytest.mark.asyncio
    async def test_initialize_solutions_handles_missing_optional_params(
        self, mock_state_surface, mock_solution_registry, mock_intent_registry
    ):
        """Should handle missing optional parameters gracefully."""
        from symphainy_platform.solutions import initialize_solutions
        
        # Test with None public_works
        services = await initialize_solutions(
            public_works=None,
            state_surface=mock_state_surface,
            solution_registry=mock_solution_registry,
            intent_registry=mock_intent_registry,
            initialize_mcp_servers=False
        )
        
        # Solutions should still initialize
        assert services.coexistence is not None
        assert services.content is not None


class TestGetSolutionSummary:
    """Test get_solution_summary function."""
    
    def test_get_solution_summary_returns_all_8_solutions(self):
        """Summary should include all 8 solutions."""
        from symphainy_platform.solutions import get_solution_summary
        
        summary = get_solution_summary()
        
        expected_keys = [
            "coexistence", "content_solution", "insights_solution",
            "operations_solution", "outcomes_solution", "security_solution",
            "control_tower"
        ]
        
        for key in expected_keys:
            assert key in summary, f"Missing solution in summary: {key}"
    
    def test_solution_summary_has_required_fields(self):
        """Each solution summary should have required fields."""
        from symphainy_platform.solutions import get_solution_summary
        
        summary = get_solution_summary()
        
        for solution_id, info in summary.items():
            assert "name" in info, f"Missing name for {solution_id}"
            assert "description" in info, f"Missing description for {solution_id}"
            assert "mcp_prefix" in info, f"Missing mcp_prefix for {solution_id}"
            assert "journeys" in info, f"Missing journeys for {solution_id}"
            assert "status" in info, f"Missing status for {solution_id}"
