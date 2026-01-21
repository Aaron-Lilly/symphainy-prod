"""
Integration Tests: Structured Extraction Framework

Tests the complete structured extraction framework including:
- ExtractionConfig models
- ExtractionConfigRegistry
- StructuredExtractionService
- StructuredExtractionAgent
- MCP Server integration
- Pre-configured patterns
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import json
from typing import Dict, Any
from symphainy_platform.realms.insights.models.extraction_config import (
    ExtractionConfig,
    ExtractionCategory
)
from symphainy_platform.civic_systems.agentic.extraction_config_registry import (
    ExtractionConfigRegistry
)
from symphainy_platform.realms.insights.enabling_services.structured_extraction_service import (
    StructuredExtractionService
)
from symphainy_platform.civic_systems.agentic.agents.structured_extraction_agent import (
    StructuredExtractionAgent
)
from symphainy_platform.realms.insights.mcp_server.insights_mcp_server import (
    InsightsRealmMCPServer
)
from symphainy_platform.realms.insights.configs.load_preconfigured_configs import (
    load_config_from_json
)


class TestExtractionConfigModels:
    """Test ExtractionConfig models."""
    
    def test_create_extraction_category(self):
        """Test creating ExtractionCategory."""
        category = ExtractionCategory(
            name="test_category",
            extraction_type="llm",
            description="Test category",
            prompt_template="Extract test data",
            required=True
        )
        
        assert category.name == "test_category"
        assert category.extraction_type == "llm"
        assert category.required is True
    
    def test_create_extraction_config(self):
        """Test creating ExtractionConfig."""
        category = ExtractionCategory(
            name="test_category",
            extraction_type="llm"
        )
        
        config = ExtractionConfig(
            config_id="test_config",
            name="Test Config",
            domain="custom",
            categories=[category]
        )
        
        assert config.config_id == "test_config"
        assert len(config.categories) == 1
    
    def test_config_validation(self):
        """Test config validation."""
        category = ExtractionCategory(
            name="test_category",
            extraction_type="llm"
        )
        
        config = ExtractionConfig(
            config_id="test_config",
            name="Test Config",
            domain="custom",
            categories=[category]
        )
        
        # Should validate successfully
        is_valid, error = config.validate()
        # Note: Will fail if jsonschema not installed, but that's expected
        if error and "jsonschema" in error.lower():
            pytest.skip("jsonschema library not installed")
        
        assert is_valid, f"Validation failed: {error}"
    
    def test_config_json_serialization(self):
        """Test JSON serialization."""
        category = ExtractionCategory(
            name="test_category",
            extraction_type="llm"
        )
        
        config = ExtractionConfig(
            config_id="test_config",
            name="Test Config",
            domain="custom",
            categories=[category]
        )
        
        json_str = config.to_json()
        assert isinstance(json_str, str)
        
        # Parse back
        config_restored = ExtractionConfig.from_json(json_str)
        assert config_restored.config_id == config.config_id


class TestExtractionConfigRegistry:
    """Test ExtractionConfigRegistry."""
    
    @pytest.mark.asyncio
    async def test_registry_initialization(self):
        """Test registry initialization."""
        registry = ExtractionConfigRegistry(supabase_adapter=None)
        assert registry.supabase_adapter is None
    
    @pytest.mark.asyncio
    async def test_register_config_without_supabase(self):
        """Test registering config without Supabase (should handle gracefully)."""
        registry = ExtractionConfigRegistry(supabase_adapter=None)
        
        category = ExtractionCategory(
            name="test_category",
            extraction_type="llm"
        )
        
        config = ExtractionConfig(
            config_id="test_config",
            name="Test Config",
            domain="custom",
            categories=[category]
        )
        
        # Should return False (no Supabase adapter)
        result = await registry.register_config(config, tenant_id="test_tenant")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_config_without_supabase(self):
        """Test getting config without Supabase."""
        registry = ExtractionConfigRegistry(supabase_adapter=None)
        
        result = await registry.get_config("test_config", "test_tenant")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_list_configs_without_supabase(self):
        """Test listing configs without Supabase."""
        registry = ExtractionConfigRegistry(supabase_adapter=None)
        
        result = await registry.list_configs("test_tenant")
        assert result == []


class TestStructuredExtractionService:
    """Test StructuredExtractionService."""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initialization."""
        service = StructuredExtractionService(public_works=None)
        
        assert service.config_registry is not None
        assert service.extraction_agent is not None
    
    @pytest.mark.asyncio
    async def test_extract_without_config(self):
        """Test extraction without pre-configured pattern (should fail gracefully)."""
        service = StructuredExtractionService(public_works=None)
        
        result = await service.extract_structured_data(
            pattern="nonexistent_pattern",
            data_source={"parsed_file_id": "test_file"},
            tenant_id="test_tenant"
        )
        
        # Should return error result
        assert "error" in result or result.get("extraction_id") is None


class TestPreConfiguredPatterns:
    """Test pre-configured extraction patterns."""
    
    def test_load_variable_life_policy_rules_config(self):
        """Test loading variable_life_policy_rules config."""
        # Find config file relative to project root
        project_root = Path(__file__).resolve().parents[3]
        config_path = project_root / "symphainy_platform" / "realms" / "insights" / "configs" / "variable_life_policy_rules_config.json"
        
        if not config_path.exists():
            pytest.skip(f"Config file not found: {config_path}")
        
        config = load_config_from_json(config_path)
        
        assert config.config_id == "variable_life_policy_rules"
        assert config.domain == "variable_life_policy_rules"
        assert len(config.categories) == 5
        assert any(cat.name == "investment_rules" for cat in config.categories)
        assert any(cat.name == "cash_value_rules" for cat in config.categories)
        assert any(cat.name == "compliance_rules" for cat in config.categories)
    
    def test_load_after_action_review_config(self):
        """Test loading after_action_review config."""
        project_root = Path(__file__).resolve().parents[3]
        config_path = project_root / "symphainy_platform" / "realms" / "insights" / "configs" / "after_action_review_config.json"
        
        if not config_path.exists():
            pytest.skip(f"Config file not found: {config_path}")
        
        config = load_config_from_json(config_path)
        
        assert config.config_id == "after_action_review"
        assert config.domain == "aar"
        assert len(config.categories) == 4
        assert any(cat.name == "lessons_learned" for cat in config.categories)
        assert any(cat.name == "risks" for cat in config.categories)
        assert any(cat.name == "recommendations" for cat in config.categories)
    
    def test_load_permit_semantic_object_config(self):
        """Test loading permit_semantic_object config."""
        project_root = Path(__file__).resolve().parents[3]
        config_path = project_root / "symphainy_platform" / "realms" / "insights" / "configs" / "permit_semantic_object_config.json"
        
        if not config_path.exists():
            pytest.skip(f"Config file not found: {config_path}")
        
        config = load_config_from_json(config_path)
        
        assert config.config_id == "permit_semantic_object"
        assert config.domain == "pso"
        assert len(config.categories) == 3
        assert any(cat.name == "permit_metadata" for cat in config.categories)
        assert any(cat.name == "obligations" for cat in config.categories)


class TestMCPServerIntegration:
    """Test MCP Server integration."""
    
    @pytest.mark.asyncio
    async def test_mcp_server_initialization(self):
        """Test MCP server initialization."""
        # Create mock orchestrator
        class MockOrchestrator:
            def _define_soa_api_handlers(self):
                return {
                    "test_api": {
                        "handler": self._test_handler,
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "test_param": {"type": "string"}
                            }
                        },
                        "description": "Test API"
                    }
                }
            
            async def _test_handler(self, **kwargs):
                return {"result": "success"}
        
        orchestrator = MockOrchestrator()
        mcp_server = InsightsRealmMCPServer(orchestrator)
        
        # Initialize MCP server
        result = await mcp_server.initialize()
        
        assert result is True
        assert len(mcp_server.get_tool_list()) > 0
        assert "insights_test_api" in mcp_server.get_tool_list()
    
    @pytest.mark.asyncio
    async def test_mcp_server_tool_execution(self):
        """Test MCP server tool execution."""
        class MockOrchestrator:
            def _define_soa_api_handlers(self):
                return {
                    "test_api": {
                        "handler": self._test_handler,
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "test_param": {"type": "string"}
                            }
                        },
                        "description": "Test API"
                    }
                }
            
            async def _test_handler(self, **kwargs):
                return {"result": "success", "param": kwargs.get("test_param")}
        
        orchestrator = MockOrchestrator()
        mcp_server = InsightsRealmMCPServer(orchestrator)
        await mcp_server.initialize()
        
        # Execute tool
        result = await mcp_server.execute_tool(
            tool_name="insights_test_api",
            parameters={"test_param": "test_value"},
            user_context={"tenant_id": "test_tenant"}
        )
        
        assert result["result"] == "success"
        assert result["param"] == "test_value"
    
    @pytest.mark.asyncio
    async def test_insights_orchestrator_soa_apis(self):
        """Test Insights Orchestrator SOA API definitions."""
        from symphainy_platform.realms.insights.orchestrators.insights_orchestrator import (
            InsightsOrchestrator
        )
        
        orchestrator = InsightsOrchestrator(public_works=None)
        
        # Check if _define_soa_api_handlers exists (as method, not attribute)
        assert hasattr(orchestrator, '_define_soa_api_handlers'), "SOA API handler method not found"
        
        # Get SOA APIs
        soa_apis = orchestrator._define_soa_api_handlers()
        
        assert isinstance(soa_apis, dict), "SOA APIs should be a dictionary"
        assert "extract_structured_data" in soa_apis, "extract_structured_data API not found"
        assert "discover_extraction_pattern" in soa_apis, "discover_extraction_pattern API not found"
        assert "create_extraction_config" in soa_apis, "create_extraction_config API not found"
        
        # Check each API has required fields
        for api_name, api_def in soa_apis.items():
            assert "handler" in api_def, f"API '{api_name}' missing handler"
            assert "input_schema" in api_def, f"API '{api_name}' missing input_schema"
            assert "description" in api_def, f"API '{api_name}' missing description"
            assert callable(api_def["handler"]), f"API '{api_name}' handler is not callable"


class TestEndToEndExtraction:
    """Test end-to-end extraction flow."""
    
    @pytest.mark.asyncio
    async def test_extraction_flow_without_llm(self):
        """Test extraction flow without LLM (should handle gracefully)."""
        service = StructuredExtractionService(public_works=None)
        
        # Try to extract with a pattern (will fail without config registry or LLM)
        result = await service.extract_structured_data(
            pattern="variable_life_policy_rules",
            data_source={"parsed_file_id": "test_file"},
            tenant_id="test_tenant"
        )
        
        # Should return error or empty result (graceful failure)
        assert isinstance(result, dict)
        # Either has error or empty extraction_id
        assert "error" in result or result.get("extraction_id") is None or result.get("extraction_id") == "unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
