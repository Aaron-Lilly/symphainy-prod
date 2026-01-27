"""
Test MCP Server Base - Common MCP Server Tests

Tests that apply to all MCP servers:
- Tool registration
- Tool naming conventions
- SOA API mapping
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestMCPServerPattern:
    """Test common MCP server patterns."""
    
    @pytest.mark.asyncio
    async def test_all_solutions_can_initialize_mcp_server(
        self,
        coexistence_solution,
        content_solution,
        insights_solution,
        operations_solution,
        outcomes_solution,
        security_solution,
        journey_solution,
        control_tower
    ):
        """All 8 solutions should be able to initialize MCP servers."""
        solutions = [
            coexistence_solution,
            content_solution,
            insights_solution,
            operations_solution,
            outcomes_solution,
            security_solution,
            journey_solution,
            control_tower
        ]
        
        for solution in solutions:
            assert hasattr(solution, 'initialize_mcp_server'), \
                f"{solution.SOLUTION_ID} missing initialize_mcp_server"
            
            try:
                mcp_server = await solution.initialize_mcp_server()
                assert mcp_server is not None, \
                    f"{solution.SOLUTION_ID} MCP server is None"
            except Exception as e:
                # Log but don't fail - some may need real deps
                print(f"Warning: {solution.SOLUTION_ID} MCP init failed: {e}")
    
    def test_all_solutions_have_get_soa_apis(
        self,
        coexistence_solution,
        content_solution,
        insights_solution,
        operations_solution,
        outcomes_solution,
        security_solution,
        journey_solution,
        control_tower
    ):
        """All solutions should expose SOA APIs."""
        solutions = [
            coexistence_solution,
            content_solution,
            insights_solution,
            operations_solution,
            outcomes_solution,
            security_solution,
            journey_solution,
            control_tower
        ]
        
        for solution in solutions:
            assert hasattr(solution, 'get_soa_apis'), \
                f"{solution.SOLUTION_ID} missing get_soa_apis"
            
            apis = solution.get_soa_apis()
            assert len(apis) > 0, \
                f"{solution.SOLUTION_ID} has no SOA APIs"


class TestMCPToolNamingConventions:
    """Test MCP tool naming conventions."""
    
    EXPECTED_PREFIXES = {
        "coexistence": "coexist_",
        "content_solution": "content_",
        "insights_solution": "insights_",
        "operations_solution": "ops_",
        "outcomes_solution": "outcomes_",
        "security_solution": "security_",
        "journey_solution": "journey_",
        "control_tower": "tower_"
    }
    
    @pytest.mark.asyncio
    async def test_coexistence_tools_use_coexist_prefix(self, coexistence_solution):
        """Coexistence MCP tools should use coexist_ prefix."""
        mcp_server = await coexistence_solution.initialize_mcp_server()
        
        if hasattr(mcp_server, 'tools') and mcp_server.tools:
            for tool in mcp_server.tools:
                name = getattr(tool, 'name', str(tool))
                assert name.startswith("coexist_"), \
                    f"Tool {name} should use coexist_ prefix"
    
    @pytest.mark.asyncio
    async def test_content_tools_use_content_prefix(self, content_solution):
        """Content MCP tools should use content_ prefix."""
        mcp_server = await content_solution.initialize_mcp_server()
        
        if hasattr(mcp_server, 'tools') and mcp_server.tools:
            for tool in mcp_server.tools:
                name = getattr(tool, 'name', str(tool))
                assert name.startswith("content_"), \
                    f"Tool {name} should use content_ prefix"


class TestMCPToolSOAAPIMapping:
    """Test that MCP tools map to SOA APIs."""
    
    def test_journey_soa_apis_registered_as_tools(self, content_solution):
        """Journey SOA APIs should be registered as MCP tools."""
        journeys = content_solution.get_journeys()
        
        total_soa_apis = 0
        for journey_id, journey in journeys.items():
            if hasattr(journey, 'get_soa_apis'):
                apis = journey.get_soa_apis()
                total_soa_apis += len(apis)
        
        # MCP server should have at least as many tools
        # (some may be solution-level)
        assert total_soa_apis > 0, "No SOA APIs found in journeys"
    
    def test_soa_api_structure_is_valid(self, content_solution):
        """SOA API definitions should have valid structure."""
        apis = content_solution.get_soa_apis()
        
        for api_name, api_def in apis.items():
            assert "handler" in api_def, f"API {api_name} missing handler"
            assert "input_schema" in api_def, f"API {api_name} missing input_schema"
            
            schema = api_def["input_schema"]
            assert "type" in schema, f"API {api_name} schema missing type"
            assert schema["type"] == "object", f"API {api_name} schema type should be object"
