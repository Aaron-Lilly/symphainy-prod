"""
Extraction Config Registry - Store and Manage Extraction Configs

Platform SDK component for managing extraction configurations.
Follows GuideRegistry pattern for consistency.

WHAT (Platform SDK Role): I store and manage extraction configs
HOW (Platform SDK Implementation): I use Supabase to store configs (JSON Schema format)
"""

import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
import uuid

from utilities import get_logger, get_clock
from symphainy_platform.realms.insights.models.extraction_config import (
    ExtractionConfig,
    EXTRACTION_CONFIG_SCHEMA
)


class ExtractionConfigRegistry:
    """
    Extraction Config Registry - Store and manage extraction configs.
    
    Configs are stored in Supabase and follow JSON Schema format.
    Each config defines how to extract structured data from unstructured sources.
    """
    
    def __init__(self, supabase_adapter: Optional[Any] = None):
        """
        Initialize Extraction Config Registry.
        
        Args:
            supabase_adapter: Supabase adapter for storage
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.supabase_adapter = supabase_adapter
    
    async def register_config(
        self,
        config: ExtractionConfig,
        tenant_id: str
    ) -> bool:
        """
        Register an extraction config in the registry.
        
        Args:
            config: ExtractionConfig instance
            tenant_id: Tenant identifier
        
        Returns:
            True if registration successful
        """
        if not self.supabase_adapter:
            self.logger.warning("Supabase adapter not available, cannot register config")
            return False
        
        # Validate config before registration
        is_valid, error = config.validate()
        if not is_valid:
            self.logger.error(f"Config validation failed: {error}")
            return False
        
        try:
            # Prepare config record
            config_dict = config.to_dict()
            config_record = {
                "id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "config_id": config.config_id,
                "name": config.name,
                "description": config.description,
                "domain": config.domain,
                "config_data": config_dict,  # Store full config as JSON
                "version": config.version,
                "created_by": config.created_by,
                "created_at": self.clock.now().isoformat() if self.clock else None
            }
            
            # Insert into Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="extraction_configs",
                operation="insert",
                user_context={"tenant_id": tenant_id},
                data=config_record
            )
            
            if result.get("success"):
                self.logger.info(f"✅ Registered extraction config: {config.config_id}")
                return True
            else:
                self.logger.error(f"Failed to register config: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to register extraction config: {e}", exc_info=True)
            return False
    
    async def get_config(
        self,
        config_id: str,
        tenant_id: str
    ) -> Optional[ExtractionConfig]:
        """
        Get an extraction config from the registry.
        
        Args:
            config_id: Config identifier
            tenant_id: Tenant identifier
        
        Returns:
            ExtractionConfig instance, or None if not found
        """
        if not self.supabase_adapter:
            return None
        
        try:
            # Query extraction_configs table
            query_result = await self.supabase_adapter.execute_rls_policy(
                table="extraction_configs",
                operation="select",
                user_context={"tenant_id": tenant_id},
                data=None
            )
            
            if query_result.get("success") and query_result.get("data"):
                # Filter in Python
                matching_records = [
                    r for r in query_result["data"]
                    if r.get("config_id") == config_id and r.get("tenant_id") == tenant_id
                ]
                if matching_records:
                    record = matching_records[0]
                    config_data = record.get("config_data", {})
                    
                    # Reconstruct ExtractionConfig from stored data
                    return ExtractionConfig.from_dict(config_data)
        
        except Exception as e:
            self.logger.error(f"Failed to get extraction config: {e}", exc_info=True)
        
        return None
    
    async def list_configs(
        self,
        tenant_id: str,
        domain: Optional[str] = None
    ) -> List[ExtractionConfig]:
        """
        List extraction configs (optionally filtered by domain).
        
        Args:
            tenant_id: Tenant identifier
            domain: Optional domain filter
        
        Returns:
            List of ExtractionConfig instances
        """
        if not self.supabase_adapter:
            return []
        
        try:
            # Query extraction_configs table
            query_result = await self.supabase_adapter.execute_rls_policy(
                table="extraction_configs",
                operation="select",
                user_context={"tenant_id": tenant_id},
                data=None
            )
            
            configs = []
            if query_result.get("success") and query_result.get("data"):
                for record in query_result["data"]:
                    if record.get("tenant_id") == tenant_id:
                        # Apply domain filter if specified
                        if domain and record.get("domain") != domain:
                            continue
                        
                        config_data = record.get("config_data", {})
                        try:
                            config = ExtractionConfig.from_dict(config_data)
                            configs.append(config)
                        except Exception as e:
                            self.logger.warning(f"Failed to parse config {record.get('config_id')}: {e}")
                            continue
            
            return configs
        
        except Exception as e:
            self.logger.error(f"Failed to list extraction configs: {e}", exc_info=True)
            return []
    
    async def update_config(
        self,
        config: ExtractionConfig,
        tenant_id: str
    ) -> bool:
        """
        Update an existing extraction config.
        
        Args:
            config: Updated ExtractionConfig instance
            tenant_id: Tenant identifier
        
        Returns:
            True if update successful
        """
        if not self.supabase_adapter:
            self.logger.warning("Supabase adapter not available, cannot update config")
            return False
        
        # Validate config before update
        is_valid, error = config.validate()
        if not is_valid:
            self.logger.error(f"Config validation failed: {error}")
            return False
        
        try:
            # Prepare update record
            config_dict = config.to_dict()
            update_record = {
                "name": config.name,
                "description": config.description,
                "domain": config.domain,
                "config_data": config_dict,
                "version": config.version,
                "updated_at": self.clock.now().isoformat() if self.clock else None
            }
            
            # Update in Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="extraction_configs",
                operation="update",
                user_context={"tenant_id": tenant_id},
                data=update_record,
                filters={"config_id": config.config_id, "tenant_id": tenant_id}
            )
            
            if result.get("success"):
                self.logger.info(f"✅ Updated extraction config: {config.config_id}")
                return True
            else:
                self.logger.error(f"Failed to update config: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update extraction config: {e}", exc_info=True)
            return False
    
    async def delete_config(
        self,
        config_id: str,
        tenant_id: str
    ) -> bool:
        """
        Delete an extraction config from the registry.
        
        Args:
            config_id: Config identifier
            tenant_id: Tenant identifier
        
        Returns:
            True if deletion successful
        """
        if not self.supabase_adapter:
            self.logger.warning("Supabase adapter not available, cannot delete config")
            return False
        
        try:
            result = await self.supabase_adapter.execute_rls_policy(
                table="extraction_configs",
                operation="delete",
                user_context={"tenant_id": tenant_id},
                data=None,
                filters={"config_id": config_id, "tenant_id": tenant_id}
            )
            
            if result.get("success"):
                self.logger.info(f"✅ Deleted extraction config: {config_id}")
                return True
            else:
                self.logger.error(f"Failed to delete config: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete extraction config: {e}", exc_info=True)
            return False
