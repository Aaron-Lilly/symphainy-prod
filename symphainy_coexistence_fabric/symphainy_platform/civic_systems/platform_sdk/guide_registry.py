"""
Guide Registry - Store and Manage Guides (Fact Patterns + Output Templates)

Platform SDK component for managing guides used in guided discovery.

WHAT (Platform SDK Role): I store and manage guides
HOW (Platform SDK Implementation): I use Supabase to store guides

Guides contain:
- Fact patterns (entities, relationships, attributes)
- Output templates (how to format results)
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


class GuideRegistry:
    """
    Guide Registry - Store and manage guides.
    
    Guides are used for guided discovery in Insights Realm.
    Each guide contains:
    - Fact pattern (entities, relationships, attributes)
    - Output template (how to format results)
    """
    
    def __init__(self, supabase_adapter: Optional[Any] = None):
        """
        Initialize Guide Registry.
        
        Args:
            supabase_adapter: Supabase adapter for storage
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.supabase_adapter = supabase_adapter
    
    async def register_guide(
        self,
        guide_id: str,
        guide: Dict[str, Any],
        tenant_id: str
    ) -> bool:
        """
        Register a guide in the registry.
        
        Args:
            guide_id: Guide identifier
            guide: Guide data (name, description, type, fact_pattern, output_template)
            tenant_id: Tenant identifier
        
        Returns:
            True if registration successful
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot register guide. Platform contract §8A."
            )
        
        try:
            # Prepare guide record
            guide_record = {
                "id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "guide_id": guide_id,
                "name": guide.get("name", ""),
                "description": guide.get("description", ""),
                "type": guide.get("type", "user_created"),  # "default" | "user_uploaded" | "user_created"
                "fact_pattern": guide.get("fact_pattern", {}),
                "output_template": guide.get("output_template", {}),
                "version": guide.get("version", "1.0"),
                "created_by": guide.get("created_by")  # User ID if user_created
            }
            
            # Insert into Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="guides",
                operation="insert",
                user_context={"tenant_id": tenant_id},
                data=guide_record
            )
            
            if result.get("success"):
                self.logger.debug(f"Registered guide: {guide_id}")
                return True
            else:
                self.logger.error(f"Failed to register guide: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to register guide: {e}", exc_info=True)
            return False
    
    async def get_guide(
        self,
        guide_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a guide from the registry.
        
        Args:
            guide_id: Guide identifier
            tenant_id: Tenant identifier
        
        Returns:
            Guide data or None if not found
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot retrieve guide. Platform contract §8A."
            )
        
        try:
            # Query guides table
            query_result = await self.supabase_adapter.execute_rls_policy(
                table="guides",
                operation="select",
                user_context={"tenant_id": tenant_id},
                data=None
            )
            
            if query_result.get("success") and query_result.get("data"):
                # Filter in Python
                matching_records = [
                    r for r in query_result["data"]
                    if r.get("guide_id") == guide_id and r.get("tenant_id") == tenant_id
                ]
                if matching_records:
                    guide = matching_records[0]
                    # Remove Supabase internal fields
                    guide.pop("id", None)
                    return guide
        
        except Exception as e:
            self.logger.error(f"Failed to get guide: {e}", exc_info=True)
        
        return None
    
    async def list_guides(
        self,
        tenant_id: str,
        guide_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List guides from the registry.
        
        Args:
            tenant_id: Tenant identifier
            guide_type: Optional filter by type ("default" | "user_uploaded" | "user_created")
        
        Returns:
            List of guides
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot list guides. Platform contract §8A."
            )
        
        try:
            # Query guides table
            query_result = await self.supabase_adapter.execute_rls_policy(
                table="guides",
                operation="select",
                user_context={"tenant_id": tenant_id},
                data=None
            )
            
            if query_result.get("success") and query_result.get("data"):
                guides = query_result["data"]
                
                # Filter by type if specified
                if guide_type:
                    guides = [g for g in guides if g.get("type") == guide_type]
                
                # Remove Supabase internal fields
                for guide in guides:
                    guide.pop("id", None)
                
                return guides
        
        except Exception as e:
            self.logger.error(f"Failed to list guides: {e}", exc_info=True)
        
        return []
    
    async def update_guide(
        self,
        guide_id: str,
        updates: Dict[str, Any],
        tenant_id: str
    ) -> bool:
        """
        Update a guide in the registry.
        
        Args:
            guide_id: Guide identifier
            updates: Guide updates
            tenant_id: Tenant identifier
        
        Returns:
            True if update successful
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot update guide. Platform contract §8A."
            )
        
        try:
            # Get existing guide to get UUID
            guide = await self.get_guide(guide_id, tenant_id)
            if not guide:
                self.logger.warning(f"Guide not found: {guide_id}")
                return False
            
            # Query to get UUID
            query_result = await self.supabase_adapter.execute_rls_policy(
                table="guides",
                operation="select",
                user_context={"tenant_id": tenant_id},
                data=None
            )
            
            if query_result.get("success") and query_result.get("data"):
                matching_records = [
                    r for r in query_result["data"]
                    if r.get("guide_id") == guide_id and r.get("tenant_id") == tenant_id
                ]
                if not matching_records:
                    return False
                
                guide_uuid = matching_records[0].get("id")
                
                # Prepare update data
                update_data = {
                    **updates,
                    "updated_at": self.clock.now_iso()
                }
                
                # Update in Supabase
                result = await self.supabase_adapter.execute_rls_policy(
                    table="guides",
                    operation="update",
                    user_context={"tenant_id": tenant_id},
                    data={"id": guide_uuid, **update_data}
                )
                
                if result.get("success"):
                    self.logger.debug(f"Updated guide: {guide_id}")
                    return True
                else:
                    self.logger.error(f"Failed to update guide: {result.get('error')}")
                    return False
        
        except Exception as e:
            self.logger.error(f"Failed to update guide: {e}", exc_info=True)
            return False
    
    async def delete_guide(
        self,
        guide_id: str,
        tenant_id: str
    ) -> bool:
        """
        Delete a guide from the registry.
        
        Args:
            guide_id: Guide identifier
            tenant_id: Tenant identifier
        
        Returns:
            True if deletion successful
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot delete guide. Platform contract §8A."
            )
        
        try:
            # Query to get UUID
            query_result = await self.supabase_adapter.execute_rls_policy(
                table="guides",
                operation="select",
                user_context={"tenant_id": tenant_id},
                data=None
            )
            
            if query_result.get("success") and query_result.get("data"):
                matching_records = [
                    r for r in query_result["data"]
                    if r.get("guide_id") == guide_id and r.get("tenant_id") == tenant_id
                ]
                if not matching_records:
                    return False
                
                guide_uuid = matching_records[0].get("id")
                
                # Delete from Supabase
                result = await self.supabase_adapter.execute_rls_policy(
                    table="guides",
                    operation="delete",
                    user_context={"tenant_id": tenant_id},
                    data={"id": guide_uuid}
                )
                
                if result.get("success"):
                    self.logger.debug(f"Deleted guide: {guide_id}")
                    return True
                else:
                    self.logger.error(f"Failed to delete guide: {result.get('error')}")
                    return False
        
        except Exception as e:
            self.logger.error(f"Failed to delete guide: {e}", exc_info=True)
            return False
