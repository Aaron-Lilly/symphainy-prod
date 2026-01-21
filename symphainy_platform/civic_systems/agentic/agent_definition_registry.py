"""
Agent Definition Registry - Store and Manage Agent Definitions

Platform SDK component for managing agent definitions (Layer 1: Platform DNA).
Follows ExtractionConfigRegistry pattern for consistency.

WHAT (Platform SDK Role): I store and manage agent definitions
HOW (Platform SDK Implementation): I use Supabase to store definitions (JSON Schema format)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
import uuid

from utilities import get_logger, get_clock
from symphainy_platform.civic_systems.agentic.models.agent_definition import (
    AgentDefinition,
    AGENT_DEFINITION_SCHEMA
)


class AgentDefinitionRegistry:
    """
    Agent Definition Registry - Store and manage agent definitions.
    
    Definitions are stored in Supabase and follow JSON Schema format.
    Each definition represents the stable, platform-owned identity of an agent.
    """
    
    def __init__(self, supabase_adapter: Optional[Any] = None):
        """
        Initialize Agent Definition Registry.
        
        Args:
            supabase_adapter: Supabase adapter for storage
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.supabase_adapter = supabase_adapter
    
    async def register_definition(
        self,
        definition: AgentDefinition
    ) -> bool:
        """
        Register an agent definition in the registry.
        
        Args:
            definition: AgentDefinition instance
        
        Returns:
            True if registration successful
        """
        if not self.supabase_adapter:
            self.logger.warning("Supabase adapter not available, cannot register definition")
            return False
        
        # Validate definition before registration
        is_valid, error = definition.validate()
        if not is_valid:
            self.logger.error(f"Definition validation failed: {error}")
            return False
        
        try:
            # Prepare definition record
            definition_dict = definition.to_dict()
            definition_record = {
                "id": str(uuid.uuid4()),
                "agent_id": definition.agent_id,
                "agent_type": definition.agent_type,
                "definition_data": definition_dict,  # Store full definition as JSON
                "version": definition.version,
                "created_by": definition.created_by,
                "created_at": self.clock.now().isoformat() if self.clock else None
            }
            
            # Insert into Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_definition_registry",
                operation="insert",
                user_context={},  # Platform-owned, no tenant isolation
                data=definition_record
            )
            
            if result.get("success"):
                self.logger.info(f"✅ Registered agent definition: {definition.agent_id}")
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Failed to register definition: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception registering definition: {e}", exc_info=True)
            return False
    
    async def get_definition(
        self,
        agent_id: str
    ) -> Optional[AgentDefinition]:
        """
        Get agent definition by agent_id.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            AgentDefinition instance, or None if not found
        """
        if not self.supabase_adapter:
            self.logger.warning("Supabase adapter not available, cannot retrieve definition")
            return None
        
        try:
            # Query Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_definition_registry",
                operation="select",
                user_context={},  # Platform-owned
                filters={"agent_id": agent_id},
                limit=1
            )
            
            if result.get("success") and result.get("data"):
                records = result["data"]
                if records:
                    record = records[0]
                    definition_data = record.get("definition_data", {})
                    return AgentDefinition.from_dict(definition_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Exception retrieving definition: {e}", exc_info=True)
            return None
    
    async def list_definitions(
        self,
        agent_type: Optional[str] = None
    ) -> List[AgentDefinition]:
        """
        List all agent definitions, optionally filtered by type.
        
        Args:
            agent_type: Optional agent type filter
        
        Returns:
            List of AgentDefinition instances
        """
        if not self.supabase_adapter:
            self.logger.warning("Supabase adapter not available, cannot list definitions")
            return []
        
        try:
            # Query Supabase
            filters = {}
            if agent_type:
                filters["agent_type"] = agent_type
            
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_definition_registry",
                operation="select",
                user_context={},  # Platform-owned
                filters=filters
            )
            
            if result.get("success") and result.get("data"):
                records = result["data"]
                definitions = []
                for record in records:
                    definition_data = record.get("definition_data", {})
                    definitions.append(AgentDefinition.from_dict(definition_data))
                return definitions
            
            return []
            
        except Exception as e:
            self.logger.error(f"Exception listing definitions: {e}", exc_info=True)
            return []
    
    async def update_definition(
        self,
        definition: AgentDefinition
    ) -> bool:
        """
        Update an existing agent definition.
        
        Args:
            definition: AgentDefinition instance with updated data
        
        Returns:
            True if update successful
        """
        if not self.supabase_adapter:
            self.logger.warning("Supabase adapter not available, cannot update definition")
            return False
        
        # Validate definition before update
        is_valid, error = definition.validate()
        if not is_valid:
            self.logger.error(f"Definition validation failed: {error}")
            return False
        
        try:
            # Prepare definition record
            definition_dict = definition.to_dict()
            definition_record = {
                "agent_type": definition.agent_type,
                "definition_data": definition_dict,
                "version": definition.version,
                "updated_at": self.clock.now().isoformat() if self.clock else None
            }
            
            # Update in Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_definition_registry",
                operation="update",
                user_context={},  # Platform-owned
                filters={"agent_id": definition.agent_id},
                data=definition_record
            )
            
            if result.get("success"):
                self.logger.info(f"✅ Updated agent definition: {definition.agent_id}")
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Failed to update definition: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception updating definition: {e}", exc_info=True)
            return False
    
    async def delete_definition(
        self,
        agent_id: str
    ) -> bool:
        """
        Delete an agent definition.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            True if deletion successful
        """
        if not self.supabase_adapter:
            self.logger.warning("Supabase adapter not available, cannot delete definition")
            return False
        
        try:
            # Delete from Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_definition_registry",
                operation="delete",
                user_context={},  # Platform-owned
                filters={"agent_id": agent_id}
            )
            
            if result.get("success"):
                self.logger.info(f"✅ Deleted agent definition: {agent_id}")
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Failed to delete definition: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception deleting definition: {e}", exc_info=True)
            return False
