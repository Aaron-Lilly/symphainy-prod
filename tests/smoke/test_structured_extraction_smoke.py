"""
Smoke Test: Structured Extraction Framework

Quick validation of base framework components.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from symphainy_platform.realms.insights.models.extraction_config import (
    ExtractionConfig,
    ExtractionCategory,
    EXTRACTION_CONFIG_SCHEMA
)
from symphainy_platform.civic_systems.agentic.extraction_config_registry import (
    ExtractionConfigRegistry
)


class TestExtractionConfigModels:
    """Test ExtractionConfig models."""
    
    def test_extraction_category_creation(self):
        """Test creating ExtractionCategory."""
        category = ExtractionCategory(
            name="investment_rules",
            extraction_type="llm",
            description="Investment allocation rules",
            prompt_template="Extract investment rules",
            required=True
        )
        
        assert category.name == "investment_rules"
        assert category.extraction_type == "llm"
        assert category.required is True
    
    def test_extraction_config_creation(self):
        """Test creating ExtractionConfig."""
        category = ExtractionCategory(
            name="investment_rules",
            extraction_type="llm",
            description="Investment allocation rules"
        )
        
        config = ExtractionConfig(
            config_id="test_config",
            name="Test Config",
            domain="variable_life_policy_rules",
            categories=[category]
        )
        
        assert config.config_id == "test_config"
        assert config.domain == "variable_life_policy_rules"
        assert len(config.categories) == 1
        assert config.categories[0].name == "investment_rules"
    
    def test_extraction_config_to_dict(self):
        """Test converting ExtractionConfig to dictionary."""
        category = ExtractionCategory(
            name="investment_rules",
            extraction_type="llm"
        )
        
        config = ExtractionConfig(
            config_id="test_config",
            name="Test Config",
            domain="variable_life_policy_rules",
            categories=[category]
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["config_id"] == "test_config"
        assert config_dict["name"] == "Test Config"
        assert config_dict["domain"] == "variable_life_policy_rules"
        assert len(config_dict["categories"]) == 1
        assert config_dict["categories"][0]["name"] == "investment_rules"
    
    def test_extraction_config_from_dict(self):
        """Test creating ExtractionConfig from dictionary."""
        config_dict = {
            "config_id": "test_config",
            "name": "Test Config",
            "domain": "variable_life_policy_rules",
            "categories": [
                {
                    "name": "investment_rules",
                    "extraction_type": "llm",
                    "description": "Investment rules"
                }
            ]
        }
        
        config = ExtractionConfig.from_dict(config_dict)
        
        assert config.config_id == "test_config"
        assert config.name == "Test Config"
        assert len(config.categories) == 1
        assert config.categories[0].name == "investment_rules"
    
    def test_extraction_config_json_serialization(self):
        """Test JSON serialization."""
        category = ExtractionCategory(
            name="investment_rules",
            extraction_type="llm"
        )
        
        config = ExtractionConfig(
            config_id="test_config",
            name="Test Config",
            domain="variable_life_policy_rules",
            categories=[category]
        )
        
        json_str = config.to_json()
        assert isinstance(json_str, str)
        
        # Parse back
        config_restored = ExtractionConfig.from_json(json_str)
        assert config_restored.config_id == config.config_id
        assert config_restored.name == config.name


class TestExtractionConfigRegistry:
    """Test ExtractionConfigRegistry."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = ExtractionConfigRegistry(supabase_adapter=None)
        
        assert registry.supabase_adapter is None
        assert registry.logger is not None
    
    @pytest.mark.asyncio
    async def test_registry_without_supabase(self):
        """Test registry operations without Supabase (should handle gracefully)."""
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
        
        # Should return None/empty (no Supabase adapter)
        retrieved = await registry.get_config("test_config", "test_tenant")
        assert retrieved is None
        
        listed = await registry.list_configs("test_tenant")
        assert listed == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
