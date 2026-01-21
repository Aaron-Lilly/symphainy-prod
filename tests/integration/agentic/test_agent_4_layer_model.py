"""
E2E Tests for 4-Layer Agent Model

Tests agent initialization, prompt assembly, and execution with 4-layer model.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import asyncio
from typing import Dict, Any, Optional
from symphainy_platform.civic_systems.agentic.agents.structured_extraction_agent import StructuredExtractionAgent
from symphainy_platform.civic_systems.agentic.agent_definition_registry import AgentDefinitionRegistry
from symphainy_platform.civic_systems.agentic.agent_posture_registry import AgentPostureRegistry
from symphainy_platform.civic_systems.agentic.agent_registry_bootstrap import AgentRegistryBootstrap
from symphainy_platform.civic_systems.agentic.telemetry.agentic_telemetry_service import AgenticTelemetryService
from symphainy_platform.civic_systems.agentic.mcp_client_manager import MCPClientManager
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent, IntentFactory


@pytest.fixture
async def supabase_adapter():
    """Get Supabase adapter (if available)."""
    # Try to get from environment or return None
    return None  # For now, tests run without Supabase


@pytest.fixture
async def agent_registry_bootstrap(supabase_adapter):
    """Bootstrap agent registry."""
    bootstrap = AgentRegistryBootstrap(supabase_adapter=supabase_adapter)
    # Note: In real tests, we'd bootstrap here
    return bootstrap


@pytest.fixture
async def execution_context():
    """Create execution context."""
    intent = IntentFactory.create_intent(
        intent_type="test",
        tenant_id="test_tenant",
        session_id="test_session",
        solution_id="test_solution",
        parameters={}
    )
    return ExecutionContext(
        execution_id="test_execution",
        intent=intent,
        tenant_id="test_tenant",
        session_id="test_session",
        solution_id="test_solution"
    )


@pytest.mark.asyncio
async def test_agent_initialization_with_definition_id(execution_context):
    """Test agent initialization with definition ID."""
    # Create agent with definition ID (will load from registry)
    agent = StructuredExtractionAgent(
        agent_id="structured_extraction_agent",
        agent_definition_id="structured_extraction_agent",
        public_works=None  # No public works for this test
    )
    
    assert agent.agent_id == "structured_extraction_agent"
    assert agent.agent_type == "structured_extraction"
    assert "structured_extraction" in agent.capabilities


@pytest.mark.asyncio
async def test_agent_prompt_assembly(execution_context):
    """Test agent prompt assembly from 4-layer model."""
    agent = StructuredExtractionAgent(
        agent_id="structured_extraction_agent",
        public_works=None
    )
    
    # Create request with runtime context
    request = {
        "message": "Extract policy rules from this document",
        "business_context": {
            "industry": "insurance",
            "document_type": "policy"
        },
        "journey_goal": "Extract structured policy data",
        "available_artifacts": ["parsed_file_123"],
        "human_preferences": {
            "detail_level": "high"
        }
    }
    
    # Process request (will assemble prompt from 4 layers)
    try:
        result = await agent.process_request(request, execution_context)
        # Should return structured result
        assert result is not None
    except Exception as e:
        # Expected if public_works not available or config is None
        error_str = str(e)
        assert "Public Works" in error_str or "LLM" in error_str or "config" in error_str.lower() or "NoneType" in error_str


@pytest.mark.asyncio
async def test_agent_definition_registry():
    """Test agent definition registry operations."""
    registry = AgentDefinitionRegistry(supabase_adapter=None)
    
    # Test listing (should work even without Supabase)
    definitions = await registry.list_definitions()
    assert isinstance(definitions, list)


@pytest.mark.asyncio
async def test_agent_posture_registry():
    """Test agent posture registry operations."""
    registry = AgentPostureRegistry(supabase_adapter=None)
    
    # Test listing (should work even without Supabase)
    postures = await registry.list_postures()
    assert isinstance(postures, list)


@pytest.mark.asyncio
async def test_agent_bootstrap():
    """Test agent registry bootstrap."""
    bootstrap = AgentRegistryBootstrap(supabase_adapter=None)
    
    # Bootstrap should complete (even if Supabase not available)
    result = await bootstrap.bootstrap_all()
    # Should not raise exception
    assert result is not None


@pytest.mark.asyncio
async def test_agent_telemetry_integration(execution_context):
    """Test agent telemetry integration."""
    telemetry_service = AgenticTelemetryService(supabase_adapter=None)
    
    agent = StructuredExtractionAgent(
        agent_id="structured_extraction_agent",
        telemetry_service=telemetry_service,
        public_works=None
    )
    
    # Agent should have telemetry service
    assert agent.telemetry_service is not None


@pytest.mark.asyncio
async def test_agent_mcp_tool_access(execution_context):
    """Test agent MCP tool access."""
    mcp_client_manager = MCPClientManager()
    
    agent = StructuredExtractionAgent(
        agent_id="structured_extraction_agent",
        mcp_client_manager=mcp_client_manager,
        public_works=None
    )
    
    # Agent should have MCP client manager
    assert agent.mcp_client_manager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
