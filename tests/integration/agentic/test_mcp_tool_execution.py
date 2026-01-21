"""
MCP Tool Execution Tests

Tests MCP tool execution across all realms.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import asyncio
from symphainy_platform.realms.content.mcp_server.content_mcp_server import ContentRealmMCPServer
from symphainy_platform.realms.insights.mcp_server.insights_mcp_server import InsightsRealmMCPServer
from symphainy_platform.realms.journey.mcp_server.journey_mcp_server import JourneyRealmMCPServer
from symphainy_platform.realms.outcomes.mcp_server.outcomes_mcp_server import OutcomesRealmMCPServer
from symphainy_platform.realms.content.orchestrators.content_orchestrator import ContentOrchestrator
from symphainy_platform.realms.insights.orchestrators.insights_orchestrator import InsightsOrchestrator
from symphainy_platform.realms.journey.orchestrators.journey_orchestrator import JourneyOrchestrator
from symphainy_platform.realms.outcomes.orchestrators.outcomes_orchestrator import OutcomesOrchestrator
from symphainy_platform.civic_systems.agentic.mcp_client_manager import MCPClientManager


@pytest.mark.asyncio
async def test_content_mcp_server_initialization():
    """Test Content MCP Server initialization."""
    orchestrator = ContentOrchestrator()
    mcp_server = ContentRealmMCPServer(orchestrator)
    
    result = await mcp_server.initialize()
    assert result is True
    
    tools = mcp_server.get_tool_list()
    assert len(tools) == 3
    assert "content_ingest_file" in tools
    assert "content_parse_content" in tools
    assert "content_extract_embeddings" in tools


@pytest.mark.asyncio
async def test_insights_mcp_server_initialization():
    """Test Insights MCP Server initialization."""
    orchestrator = InsightsOrchestrator()
    mcp_server = InsightsRealmMCPServer(orchestrator)
    
    result = await mcp_server.initialize()
    assert result is True
    
    tools = mcp_server.get_tool_list()
    assert len(tools) == 3
    assert "insights_extract_structured_data" in tools
    assert "insights_discover_extraction_pattern" in tools
    assert "insights_create_extraction_config" in tools


@pytest.mark.asyncio
async def test_journey_mcp_server_initialization():
    """Test Journey MCP Server initialization."""
    orchestrator = JourneyOrchestrator()
    mcp_server = JourneyRealmMCPServer(orchestrator)
    
    result = await mcp_server.initialize()
    assert result is True
    
    tools = mcp_server.get_tool_list()
    assert len(tools) == 3
    assert "journey_optimize_process" in tools
    assert "journey_generate_sop" in tools
    assert "journey_create_workflow" in tools


@pytest.mark.asyncio
async def test_outcomes_mcp_server_initialization():
    """Test Outcomes MCP Server initialization."""
    orchestrator = OutcomesOrchestrator()
    mcp_server = OutcomesRealmMCPServer(orchestrator)
    
    result = await mcp_server.initialize()
    assert result is True
    
    tools = mcp_server.get_tool_list()
    assert len(tools) == 3
    assert "outcomes_synthesize_outcome" in tools
    assert "outcomes_generate_roadmap" in tools
    assert "outcomes_create_poc" in tools


@pytest.mark.asyncio
async def test_mcp_client_manager_discovery():
    """Test MCP Client Manager tool discovery."""
    client_manager = MCPClientManager()
    
    # Register MCP servers
    content_orch = ContentOrchestrator()
    content_mcp = ContentRealmMCPServer(content_orch)
    await content_mcp.initialize()
    await client_manager.register_server("content_mcp", content_mcp)
    
    insights_orch = InsightsOrchestrator()
    insights_mcp = InsightsRealmMCPServer(insights_orch)
    await insights_mcp.initialize()
    await client_manager.register_server("insights_mcp", insights_mcp)
    
    # Discover tools
    all_tools = await client_manager.list_all_tools()
    assert len(all_tools) >= 6  # At least 3 from content + 3 from insights
    
    # Check tool names
    tool_names = [tool["name"] for tool in all_tools]
    assert "content_ingest_file" in tool_names
    assert "insights_extract_structured_data" in tool_names


@pytest.mark.asyncio
async def test_mcp_tool_execution_schema_validation():
    """Test MCP tool execution with schema validation."""
    client_manager = MCPClientManager()
    
    # Register Content MCP server
    content_orch = ContentOrchestrator()
    content_mcp = ContentRealmMCPServer(content_orch)
    await content_mcp.initialize()
    await client_manager.register_server("content_mcp", content_mcp)
    
    # Try to execute tool with invalid parameters (should fail validation or return error)
    try:
        result = await client_manager.execute_tool(
            server_name="content_mcp",
            tool_name="content_ingest_file",
            parameters={},  # Missing required parameters
            user_context={"tenant_id": "test"}
        )
        # If validation doesn't happen at MCP level, the orchestrator will fail
        # Either way, we should get an error response
        if isinstance(result, dict):
            # Check if result indicates failure
            assert result.get("success") is False or "error" in result or "file_data" in str(result).lower()
        else:
            # If exception was raised, that's also acceptable
            assert False, "Expected error response or exception"
    except Exception as e:
        # Expected - validation should catch missing parameters
        error_str = str(e).lower()
        assert "required" in error_str or "missing" in error_str or "file_data" in error_str or "validation" in error_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
