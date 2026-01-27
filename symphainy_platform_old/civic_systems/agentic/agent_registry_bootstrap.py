"""
Agent Registry Bootstrap

Bootstrap agent definitions and postures into registries.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Optional, Any
from utilities import get_logger
from symphainy_platform.civic_systems.agentic.agent_definition_registry import AgentDefinitionRegistry
from symphainy_platform.civic_systems.agentic.agent_posture_registry import AgentPostureRegistry
from symphainy_platform.civic_systems.agentic.agent_definitions import (
    STRUCTURED_EXTRACTION_AGENT_DEFINITION,
    GUIDE_AGENT_DEFINITION,
    JOURNEY_LIAISON_AGENT_DEFINITION,
    STATELESS_AGENT_DEFINITION
)
from symphainy_platform.civic_systems.agentic.agent_postures import (
    DEFAULT_POSTURE,
    CONSERVATIVE_POSTURE,
    EXPLORATORY_POSTURE,
    PRODUCTION_POSTURE
)


class AgentRegistryBootstrap:
    """
    Bootstrap agent definitions and postures into registries.
    
    Used for initial setup and migration.
    """
    
    def __init__(self, supabase_adapter: Optional[Any] = None):
        """
        Initialize bootstrap.
        
        Args:
            supabase_adapter: Supabase adapter for storage
        """
        self.logger = get_logger(self.__class__.__name__)
        self.definition_registry = AgentDefinitionRegistry(supabase_adapter=supabase_adapter)
        self.posture_registry = AgentPostureRegistry(supabase_adapter=supabase_adapter)
    
    async def bootstrap_definitions(self) -> bool:
        """
        Bootstrap agent definitions.
        
        Returns:
            True if successful
        """
        try:
            definitions = [
                STRUCTURED_EXTRACTION_AGENT_DEFINITION,
                GUIDE_AGENT_DEFINITION,
                JOURNEY_LIAISON_AGENT_DEFINITION,
                STATELESS_AGENT_DEFINITION
            ]
            
            registered_count = 0
            for definition in definitions:
                try:
                    # Check if already exists
                    existing = await self.definition_registry.get_definition(definition.agent_id)
                    if existing:
                        self.logger.info(f"Agent definition already exists: {definition.agent_id}")
                        continue
                    
                    # Register definition
                    success = await self.definition_registry.register_definition(definition)
                    if success:
                        registered_count += 1
                        self.logger.info(f"✅ Registered agent definition: {definition.agent_id}")
                    else:
                        self.logger.warning(f"Failed to register agent definition: {definition.agent_id}")
                except Exception as e:
                    self.logger.error(f"Exception registering agent definition {definition.agent_id}: {e}", exc_info=True)
            
            self.logger.info(f"✅ Bootstrapped {registered_count} agent definitions")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception bootstrapping agent definitions: {e}", exc_info=True)
            return False
    
    async def bootstrap_postures(self) -> bool:
        """
        Bootstrap agent postures.
        
        Returns:
            True if successful
        """
        try:
            postures = [
                DEFAULT_POSTURE,
                CONSERVATIVE_POSTURE,
                EXPLORATORY_POSTURE,
                PRODUCTION_POSTURE
            ]
            
            registered_count = 0
            for posture in postures:
                try:
                    # Register posture (platform default)
                    success = await self.posture_registry.register_posture(posture)
                    if success:
                        registered_count += 1
                        self.logger.info(f"✅ Registered agent posture: {posture.agent_id} (platform default)")
                    else:
                        self.logger.warning(f"Failed to register agent posture: {posture.agent_id}")
                except Exception as e:
                    self.logger.error(f"Exception registering agent posture {posture.agent_id}: {e}", exc_info=True)
            
            self.logger.info(f"✅ Bootstrapped {registered_count} agent postures")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception bootstrapping agent postures: {e}", exc_info=True)
            return False
    
    async def bootstrap_all(self) -> bool:
        """
        Bootstrap all definitions and postures.
        
        Returns:
            True if successful
        """
        self.logger.info("🚀 Bootstrapping agent definitions and postures...")
        
        definitions_ok = await self.bootstrap_definitions()
        postures_ok = await self.bootstrap_postures()
        
        if definitions_ok and postures_ok:
            self.logger.info("✅ Agent registry bootstrap complete")
            return True
        else:
            self.logger.warning("⚠️ Agent registry bootstrap completed with errors")
            return False
