"""
Load Pre-Configured Extraction Configs

Utility script to load and register pre-configured extraction configs.
"""

import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List
from symphainy_platform.realms.insights.models.extraction_config import ExtractionConfig
from symphainy_platform.civic_systems.agentic.extraction_config_registry import ExtractionConfigRegistry


def load_config_from_json(file_path: Path) -> ExtractionConfig:
    """
    Load extraction config from JSON file.
    
    Args:
        file_path: Path to JSON config file
    
    Returns:
        ExtractionConfig instance
    """
    with open(file_path, 'r') as f:
        config_data = json.load(f)
    
    return ExtractionConfig.from_dict(config_data)


async def register_preconfigured_configs(
    registry: ExtractionConfigRegistry,
    tenant_id: str
) -> Dict[str, bool]:
    """
    Register all pre-configured extraction configs.
    
    Args:
        registry: ExtractionConfigRegistry instance
        tenant_id: Tenant identifier
    
    Returns:
        Dict mapping config_id to registration success status
    """
    config_dir = Path(__file__).parent
    results = {}
    
    # List of pre-configured config files
    config_files = [
        "variable_life_policy_rules_config.json",
        "after_action_review_config.json",
        "permit_semantic_object_config.json"
    ]
    
    for config_file in config_files:
        config_path = config_dir / config_file
        if not config_path.exists():
            results[config_file] = False
            continue
        
        try:
            config = load_config_from_json(config_path)
            success = await registry.register_config(config, tenant_id)
            results[config.config_id] = success
            
            if success:
                print(f"✅ Registered config: {config.config_id}")
            else:
                print(f"❌ Failed to register config: {config.config_id}")
                
        except Exception as e:
            print(f"❌ Error loading config {config_file}: {e}")
            results[config_file] = False
    
    return results


if __name__ == "__main__":
    # Example usage (requires Supabase adapter)
    import asyncio
    
    async def main():
        # This would be called with actual registry instance
        # registry = ExtractionConfigRegistry(supabase_adapter=supabase_adapter)
        # results = await register_preconfigured_configs(registry, tenant_id="default")
        # print(results)
        print("Use register_preconfigured_configs() with a registry instance")
    
    asyncio.run(main())
