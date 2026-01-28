"""
Test SecuritySolution - Security Realm Platform Solution (FOUNDATIONAL)

CRITICAL: Security tests are foundational - they must pass first.

Tests:
- Solution initialization
- Journey registration (3 journeys)
- Authentication, Registration, Session management
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestSecuritySolutionInitialization:
    """Test SecuritySolution initialization."""
    
    def test_solution_has_correct_id(self, security_solution):
        """Solution should have correct ID."""
        assert security_solution.SOLUTION_ID == "security_solution"
    
    def test_solution_has_supported_intents(self, security_solution):
        """Solution should declare supported intents."""
        assert hasattr(security_solution, 'SUPPORTED_INTENTS')
        assert "compose_journey" in security_solution.SUPPORTED_INTENTS


class TestSecurityJourneys:
    """Test SecuritySolution journeys."""
    
    def test_has_3_journeys(self, security_solution):
        """SecuritySolution should have 3 journeys."""
        journeys = security_solution._journeys
        assert len(journeys) == 3
    
    def test_has_authentication_journey(self, security_solution):
        """Should have authentication journey."""
        journeys = security_solution._journeys
        assert "authentication" in journeys
    
    def test_has_registration_journey(self, security_solution):
        """Should have registration journey."""
        journeys = security_solution._journeys
        assert "registration" in journeys
    
    def test_has_session_management_journey(self, security_solution):
        """Should have session_management journey."""
        journeys = security_solution._journeys
        assert "session_management" in journeys
    
    def test_each_journey_has_compose_journey(self, security_solution):
        """Each journey should have compose_journey method."""
        for journey_id, journey in security_solution._journeys.items():
            assert hasattr(journey, 'compose_journey')


class TestSecurityHandleIntent:
    """Test SecuritySolution intent handling."""
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_authentication(
        self, security_solution, execution_context, compose_journey_intent
    ):
        """Should handle authentication journey."""
        intent = compose_journey_intent(
            journey_id="authentication",
            journey_params={
                "email": "test@example.com",
                "password": "TestPassword123!"
            },
            solution_id="security_solution"
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_registration(
        self, security_solution, execution_context, compose_journey_intent
    ):
        """Should handle registration journey."""
        intent = compose_journey_intent(
            journey_id="registration",
            journey_params={
                "email": "newuser@example.com",
                "password": "NewPassword123!",
                "display_name": "Test User"
            },
            solution_id="security_solution"
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        assert "success" in result


class TestSecurityMCPServer:
    """Test SecuritySolution MCP Server."""
    
    def test_initialize_mcp_server(self, security_solution):
        """Should initialize MCP server."""
        mcp_server = security_solution.initialize_mcp_server()
        assert mcp_server is not None
    
    @pytest.mark.asyncio
    async def test_mcp_tools_use_security_prefix(self, security_solution):
        """MCP tools should use security_ prefix."""
        mcp_server = security_solution.initialize_mcp_server()
        
        if hasattr(mcp_server, 'tools'):
            for tool in mcp_server.tools:
                if hasattr(tool, 'name'):
                    assert tool.name.startswith("security_")


class TestSecurityIsFoundational:
    """Test that Security is treated as foundational."""
    
    def test_security_solution_exists(self, security_solution):
        """SecuritySolution must exist."""
        assert security_solution is not None
    
    def test_security_journeys_are_complete(self, security_solution):
        """All security journeys must be complete."""
        journeys = security_solution._journeys
        
        for journey_id, journey in journeys.items():
            assert hasattr(journey, 'compose_journey'), \
                f"Security journey {journey_id} incomplete"
            assert hasattr(journey, 'get_soa_apis'), \
                f"Security journey {journey_id} missing get_soa_apis"
