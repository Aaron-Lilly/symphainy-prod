"""
Agent Posture Registry - Store and Manage Agent Postures

Platform SDK component for managing agent postures (Layer 2: Tenant/Solution scoped).
Follows ExtractionConfigRegistry pattern for consistency.

WHAT (Platform SDK Role): I store and manage agent postures
HOW (Platform SDK Implementation): I use Supabase to store postures (JSON Schema format)

Key Feature: Fallback hierarchy (solution → tenant → platform default)
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
from symphainy_platform.civic_systems.agentic.models.agent_posture import (
    AgentPosture,
    AGENT_POSTURE_SCHEMA
)


class AgentPostureRegistry:
    """
    Agent Posture Registry - Store and manage agent postures.
    
    Postures are stored in Supabase and follow JSON Schema format.
    Each posture represents behavioral tuning for a specific tenant or solution.
    
    Fallback hierarchy:
    1. Solution-specific posture (agent_id, tenant_id, solution_id)
    2. Tenant-specific posture (agent_id, tenant_id, NULL)
    3. Platform default posture (agent_id, NULL, NULL)
    """
    
    def __init__(self, supabase_adapter: Optional[Any] = None):
        """
        Initialize Agent Posture Registry.
        
        Args:
            supabase_adapter: Supabase adapter for storage
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.supabase_adapter = supabase_adapter
    
    async def register_posture(
        self,
        posture: AgentPosture,
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Register an agent posture in the registry.
        
        Args:
            posture: AgentPosture instance
            tenant_id: Tenant identifier (for RLS, uses posture.tenant_id if not provided)
        
        Returns:
            True if registration successful
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot register posture. Platform contract §8A."
            )
        
        # Validate posture before registration
        is_valid, error = posture.validate()
        if not is_valid:
            self.logger.error(f"Posture validation failed: {error}")
            return False
        
        try:
            # Prepare posture record
            posture_dict = posture.to_dict()
            posture_record = {
                "id": str(uuid.uuid4()),
                "agent_id": posture.agent_id,
                "tenant_id": posture.tenant_id,
                "solution_id": posture.solution_id,
                "posture_data": posture_dict,  # Store full posture as JSON
                "version": posture.version,
                "created_by": posture.created_by,
                "created_at": self.clock.now().isoformat() if self.clock else None
            }
            
            # Use tenant_id from posture or parameter
            rls_tenant_id = posture.tenant_id or tenant_id or "platform"
            
            # Insert into Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_posture_registry",
                operation="insert",
                user_context={"tenant_id": rls_tenant_id},
                data=posture_record
            )
            
            if result.get("success"):
                self.logger.info(
                    f"✅ Registered agent posture: {posture.agent_id} "
                    f"(tenant={posture.tenant_id}, solution={posture.solution_id})"
                )
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Failed to register posture: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception registering posture: {e}", exc_info=True)
            return False
    
    async def get_posture(
        self,
        agent_id: str,
        tenant_id: Optional[str] = None,
        solution_id: Optional[str] = None
    ) -> Optional[AgentPosture]:
        """
        Get agent posture with fallback hierarchy.
        
        Fallback order:
        1. Solution-specific (agent_id, tenant_id, solution_id)
        2. Tenant-specific (agent_id, tenant_id, NULL)
        3. Platform default (agent_id, NULL, NULL)
        
        Args:
            agent_id: Agent identifier
            tenant_id: Optional tenant identifier
            solution_id: Optional solution identifier
        
        Returns:
            AgentPosture instance, or None if not found
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot retrieve posture. Platform contract §8A."
            )
        
        try:
            # Try solution-specific first
            if tenant_id and solution_id:
                posture = await self._get_posture_direct(agent_id, tenant_id, solution_id)
                if posture:
                    return posture
            
            # Try tenant-specific
            if tenant_id:
                posture = await self._get_posture_direct(agent_id, tenant_id, None)
                if posture:
                    return posture
            
            # Try platform default
            posture = await self._get_posture_direct(agent_id, None, None)
            if posture:
                return posture
            
            return None
            
        except Exception as e:
            self.logger.error(f"Exception retrieving posture: {e}", exc_info=True)
            return None
    
    async def _get_posture_direct(
        self,
        agent_id: str,
        tenant_id: Optional[str],
        solution_id: Optional[str]
    ) -> Optional[AgentPosture]:
        """Get posture directly (no fallback)."""
        try:
            # Query Supabase
            filters = {"agent_id": agent_id}
            if tenant_id is not None:
                filters["tenant_id"] = tenant_id
            else:
                filters["tenant_id"] = None
            if solution_id is not None:
                filters["solution_id"] = solution_id
            else:
                filters["solution_id"] = None
            
            rls_tenant_id = tenant_id or "platform"
            
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_posture_registry",
                operation="select",
                user_context={"tenant_id": rls_tenant_id},
                filters=filters,
                limit=1
            )
            
            if result.get("success") and result.get("data"):
                records = result["data"]
                if records:
                    record = records[0]
                    posture_data = record.get("posture_data", {})
                    return AgentPosture.from_dict(posture_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Exception retrieving posture directly: {e}", exc_info=True)
            return None
    
    async def list_postures(
        self,
        agent_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> List[AgentPosture]:
        """
        List agent postures, optionally filtered.
        
        Args:
            agent_id: Optional agent identifier filter
            tenant_id: Optional tenant identifier filter
        
        Returns:
            List of AgentPosture instances
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot list postures. Platform contract §8A."
            )
        
        try:
            # Query Supabase
            filters = {}
            if agent_id:
                filters["agent_id"] = agent_id
            if tenant_id:
                filters["tenant_id"] = tenant_id
            
            rls_tenant_id = tenant_id or "platform"
            
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_posture_registry",
                operation="select",
                user_context={"tenant_id": rls_tenant_id},
                filters=filters
            )
            
            if result.get("success") and result.get("data"):
                records = result["data"]
                postures = []
                for record in records:
                    posture_data = record.get("posture_data", {})
                    postures.append(AgentPosture.from_dict(posture_data))
                return postures
            
            return []
            
        except Exception as e:
            self.logger.error(f"Exception listing postures: {e}", exc_info=True)
            return []
    
    async def update_posture(
        self,
        posture: AgentPosture,
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Update an existing agent posture.
        
        Args:
            posture: AgentPosture instance with updated data
            tenant_id: Tenant identifier (for RLS)
        
        Returns:
            True if update successful
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot update posture. Platform contract §8A."
            )
        
        # Validate posture before update
        is_valid, error = posture.validate()
        if not is_valid:
            self.logger.error(f"Posture validation failed: {error}")
            return False
        
        try:
            # Prepare posture record
            posture_dict = posture.to_dict()
            posture_record = {
                "posture_data": posture_dict,
                "version": posture.version,
                "updated_at": self.clock.now().isoformat() if self.clock else None
            }
            
            # Update filters
            filters = {"agent_id": posture.agent_id}
            if posture.tenant_id is not None:
                filters["tenant_id"] = posture.tenant_id
            else:
                filters["tenant_id"] = None
            if posture.solution_id is not None:
                filters["solution_id"] = posture.solution_id
            else:
                filters["solution_id"] = None
            
            rls_tenant_id = posture.tenant_id or tenant_id or "platform"
            
            # Update in Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_posture_registry",
                operation="update",
                user_context={"tenant_id": rls_tenant_id},
                filters=filters,
                data=posture_record
            )
            
            if result.get("success"):
                self.logger.info(f"✅ Updated agent posture: {posture.agent_id}")
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Failed to update posture: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception updating posture: {e}", exc_info=True)
            return False
    
    async def delete_posture(
        self,
        agent_id: str,
        tenant_id: Optional[str] = None,
        solution_id: Optional[str] = None
    ) -> bool:
        """
        Delete an agent posture.
        
        Args:
            agent_id: Agent identifier
            tenant_id: Optional tenant identifier
            solution_id: Optional solution identifier
        
        Returns:
            True if deletion successful
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot delete posture. Platform contract §8A."
            )
        
        try:
            # Delete filters
            filters = {"agent_id": agent_id}
            if tenant_id is not None:
                filters["tenant_id"] = tenant_id
            else:
                filters["tenant_id"] = None
            if solution_id is not None:
                filters["solution_id"] = solution_id
            else:
                filters["solution_id"] = None
            
            rls_tenant_id = tenant_id or "platform"
            
            # Delete from Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_posture_registry",
                operation="delete",
                user_context={"tenant_id": rls_tenant_id},
                filters=filters
            )
            
            if result.get("success"):
                self.logger.info(f"✅ Deleted agent posture: {agent_id}")
                return True
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Failed to delete posture: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception deleting posture: {e}", exc_info=True)
            return False
