"""
Registry Abstraction - Pure Infrastructure (Layer 1)

Implements registry operations using Supabase adapter with RLS policy enforcement.
Returns raw data only - no business logic.

WHAT (Infrastructure Role): I provide registry storage services with governance
HOW (Infrastructure Implementation): I use Supabase adapter with RLS policy execution

NOTE: This is PURE INFRASTRUCTURE - no business logic.
Business logic (UUID generation, validation, metadata enhancement) belongs in Platform SDK.
RLS policies provide governance at the database level.
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger
from ..adapters.supabase_adapter import SupabaseAdapter


class RegistryAbstraction:
    """
    Registry Abstraction - Pure infrastructure.
    
    Provides governed access to Supabase for registry operations (lineage, metadata, etc.).
    Uses RLS policies for governance at the database level.
    
    ARCHITECTURAL PRINCIPLE: This is the correct way to perform registry CRUD operations.
    - Goes through governance (RLS policies)
    - Uses Supabase adapter (Layer 0)
    - Returns raw data only
    """
    
    def __init__(self, supabase_adapter: SupabaseAdapter):
        """
        Initialize Registry abstraction.
        
        Args:
            supabase_adapter: Supabase adapter (Layer 0)
        """
        self.supabase = supabase_adapter
        self.logger = get_logger(self.__class__.__name__)
        
        self.logger.info("Registry Abstraction initialized (pure infrastructure)")
    
    async def insert_record(
        self,
        table: str,
        data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert record into registry table (governed by RLS).
        
        ARCHITECTURAL PRINCIPLE: This is the correct way to perform registry inserts.
        - Goes through RLS policy (governance)
        - Uses Supabase adapter (Layer 0)
        - Returns raw data only
        
        Args:
            table: Table name
            data: Record data
            user_context: User context (tenant_id, access_token, etc.)
        
        Returns:
            Dict with success status and result data
        """
        try:
            result = await self.supabase.execute_rls_policy(
                table=table,
                operation="insert",
                user_context=user_context,
                data=data
            )
            return result
        except Exception as e:
            self.logger.error(f"Registry insert failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "insert_failed"
            }
    
    async def query_records(
        self,
        table: str,
        user_context: Dict[str, Any],
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query records from registry table (governed by RLS).
        
        Args:
            table: Table name
            user_context: User context (tenant_id, access_token, etc.)
            filter_conditions: Optional filter conditions
        
        Returns:
            List of records
        """
        try:
            result = await self.supabase.execute_rls_policy(
                table=table,
                operation="select",
                user_context=user_context,
                data=filter_conditions
            )
            
            if result.get("success"):
                return result.get("data", [])
            else:
                self.logger.warning(f"Registry query failed: {result.get('error')}")
                return []
        except Exception as e:
            self.logger.error(f"Registry query failed: {e}", exc_info=True)
            return []
    
    async def update_record(
        self,
        table: str,
        data: Dict[str, Any],
        user_context: Dict[str, Any],
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update record in registry table (governed by RLS).
        
        Args:
            table: Table name
            data: Update data
            user_context: User context (tenant_id, access_token, etc.)
            filter_conditions: Optional filter conditions for WHERE clause
        
        Returns:
            Dict with success status and result data
        """
        try:
            # Combine data and filter_conditions for update
            update_data = {**data}
            if filter_conditions:
                update_data["_filter"] = filter_conditions
            
            result = await self.supabase.execute_rls_policy(
                table=table,
                operation="update",
                user_context=user_context,
                data=update_data
            )
            return result
        except Exception as e:
            self.logger.error(f"Registry update failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "update_failed"
            }
    
    async def delete_record(
        self,
        table: str,
        user_context: Dict[str, Any],
        filter_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Delete record from registry table (governed by RLS).
        
        Args:
            table: Table name
            user_context: User context (tenant_id, access_token, etc.)
            filter_conditions: Filter conditions for WHERE clause
        
        Returns:
            Dict with success status
        """
        try:
            result = await self.supabase.execute_rls_policy(
                table=table,
                operation="delete",
                user_context=user_context,
                data=filter_conditions
            )
            return result
        except Exception as e:
            self.logger.error(f"Registry delete failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "delete_failed"
            }
