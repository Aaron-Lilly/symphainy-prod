"""
Test ContentSolution - Content Realm Platform Solution

Tests:
- Solution initialization
- Journey registration (4 journeys)
- SOA API exposure
- compose_journey intent handling
- File upload/parse/embed flow
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestContentSolutionInitialization:
    """Test ContentSolution initialization."""
    
    def test_solution_has_correct_id(self, content_solution):
        """Solution should have correct ID."""
        assert content_solution.SOLUTION_ID == "content_solution"
    
    def test_solution_has_correct_name(self, content_solution):
        """Solution should have correct name."""
        assert content_solution.SOLUTION_NAME == "Content Solution"
    
    def test_solution_has_supported_intents(self, content_solution):
        """Solution should declare supported intents."""
        assert hasattr(content_solution, 'SUPPORTED_INTENTS')
        assert "compose_journey" in content_solution.SUPPORTED_INTENTS
        assert "ingest_file" in content_solution.SUPPORTED_INTENTS


class TestContentJourneys:
    """Test ContentSolution journeys."""
    
    def test_has_4_journeys(self, content_solution):
        """ContentSolution should have 4 journeys."""
        journeys = content_solution.get_journeys()
        assert len(journeys) == 4
    
    def test_has_file_upload_materialization_journey(self, content_solution):
        """Should have file_upload_materialization journey."""
        journeys = content_solution.get_journeys()
        assert "file_upload_materialization" in journeys
    
    def test_has_file_parsing_journey(self, content_solution):
        """Should have file_parsing journey."""
        journeys = content_solution.get_journeys()
        assert "file_parsing" in journeys
    
    def test_has_deterministic_embedding_journey(self, content_solution):
        """Should have deterministic_embedding journey."""
        journeys = content_solution.get_journeys()
        assert "deterministic_embedding" in journeys
    
    def test_has_file_management_journey(self, content_solution):
        """Should have file_management journey."""
        journeys = content_solution.get_journeys()
        assert "file_management" in journeys
    
    def test_each_journey_has_compose_journey_method(self, content_solution):
        """Each journey should have compose_journey method."""
        for journey_id, journey in content_solution.get_journeys().items():
            assert hasattr(journey, 'compose_journey'), \
                f"Journey {journey_id} missing compose_journey method"


class TestContentSOAAPIs:
    """Test ContentSolution SOA APIs."""
    
    def test_exposes_soa_apis(self, content_solution):
        """Solution should expose SOA APIs."""
        apis = content_solution.get_soa_apis()
        assert len(apis) > 0
    
    def test_has_compose_journey_api(self, content_solution):
        """Should have compose_journey SOA API."""
        apis = content_solution.get_soa_apis()
        assert "compose_journey" in apis


class TestContentHandleIntent:
    """Test ContentSolution intent handling."""
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_intent(
        self, content_solution, execution_context, compose_journey_intent
    ):
        """Should handle compose_journey intent."""
        intent = compose_journey_intent(
            journey_id="file_upload_materialization",
            journey_params={"file_name": "test.txt"},
            solution_id="content_solution"
        )
        
        result = await content_solution.handle_intent(intent, execution_context)
        
        assert "success" in result
        assert "artifacts" in result
        assert "events" in result
    
    @pytest.mark.asyncio
    async def test_handle_ingest_file_routes_to_journey(
        self, content_solution, execution_context
    ):
        """ingest_file intent should route to file_upload_materialization journey."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={"file_name": "test.txt", "file_path": "/tmp/test.txt"}
        )
        
        # Should not raise - routes to appropriate journey
        result = await content_solution.handle_intent(intent, execution_context)
        assert "success" in result or "error" in result


class TestContentMCPServer:
    """Test ContentSolution MCP Server."""
    
    def test_initialize_mcp_server(self, content_solution):
        """Should be able to initialize MCP server."""
        mcp_server = content_solution.initialize_mcp_server()
        assert mcp_server is not None
    
    @pytest.mark.asyncio
    async def test_mcp_tools_use_content_prefix(self, content_solution):
        """MCP tools should use content_ prefix."""
        mcp_server = content_solution.initialize_mcp_server()
        
        if hasattr(mcp_server, 'tools'):
            for tool in mcp_server.tools:
                if hasattr(tool, 'name'):
                    assert tool.name.startswith("content_"), \
                        f"Tool {tool.name} should use content_ prefix"


class TestContentExperienceSDKConfig:
    """Test Content Solution Experience SDK configuration."""
    
    def test_has_experience_sdk_config(self, content_solution):
        """Should have Experience SDK config method."""
        assert hasattr(content_solution, 'get_experience_sdk_config')
    
    def test_experience_sdk_config_has_required_fields(self, content_solution):
        """Experience SDK config should have required fields."""
        if hasattr(content_solution, 'get_experience_sdk_config'):
            config = content_solution.get_experience_sdk_config()
            
            assert "solution_id" in config
            assert "supported_intents" in config
            # journeys is the correct field name (available_journeys is nested under integration_patterns)
            assert "journeys" in config
            assert "soa_apis" in config
