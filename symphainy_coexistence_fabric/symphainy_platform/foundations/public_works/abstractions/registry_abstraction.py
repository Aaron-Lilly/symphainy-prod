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
    
    async def list_artifacts(
        self,
        tenant_id: str,
        artifact_type: Optional[str] = None,
        lifecycle_state: Optional[str] = None,
        eligible_for: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List artifacts from artifact_index (discovery/exploration).
        
        This queries artifact_index for UI dropdowns and exploration.
        For actual artifact content, use State Surface resolve_artifact().
        
        Args:
            tenant_id: Tenant identifier
            artifact_type: Filter by artifact type
            lifecycle_state: Filter by lifecycle state (default: READY)
            eligible_for: Filter artifacts eligible for next intent
            limit: Pagination limit
            offset: Pagination offset
        
        Returns:
            Dict with 'artifacts' list and 'total' count
        """
        try:
            # Build query using Supabase client directly (for complex filtering)
            # We'll use the adapter's client for direct PostgREST queries
            # SupabaseAdapter exposes client as self.client
            client = self.supabase.client
            
            query = client.table("artifact_index").select("*")
            query = query.eq("tenant_id", tenant_id)
            
            # Default to READY/ARCHIVED if lifecycle_state not specified
            if lifecycle_state:
                query = query.eq("lifecycle_state", lifecycle_state)
            else:
                query = query.in_("lifecycle_state", ["READY", "ARCHIVED"])
            
            if artifact_type:
                query = query.eq("artifact_type", artifact_type)
            
            # Eligibility filtering (MVP: hard-coded mapping)
            if eligible_for:
                eligible_types = self._get_eligible_artifact_types(eligible_for)
                if eligible_types:
                    query = query.in_("artifact_type", eligible_types)
            
            # Get total count (execute query without pagination)
            count_result = query.execute()
            total = len(count_result.data) if count_result.data else 0
            
            # Apply pagination
            query = query.order("created_at", desc=True).limit(limit).offset(offset)
            result = query.execute()
            
            return {
                "artifacts": result.data or [],
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list artifacts: {e}", exc_info=True)
            return {
                "artifacts": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
    
    def _get_eligible_artifact_types(self, intent_type: str) -> List[str]:
        """
        Get artifact types eligible for a given intent.
        
        MVP: Hard-coded mapping
        Future: Dynamic eligibility rules
        
        Args:
            intent_type: Intent type (e.g., "parse_content", "extract_embeddings")
        
        Returns:
            List of eligible artifact types
        """
        eligibility_map = {
            "parse_content": ["file"],
            "extract_embeddings": ["parsed_content"],
            "create_deterministic_embeddings": ["parsed_content"],
            "hydrate_semantic_profile": ["parsed_content"],
            "save_materialization": ["file", "parsed_content", "embeddings"]
        }
        return eligibility_map.get(intent_type, [])
    
    async def create_pending_intent(
        self,
        intent_id: str,
        intent_type: str,
        target_artifact_id: str,
        context: Dict[str, Any],
        tenant_id: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create pending intent in intent_executions table.
        
        This is where ingestion_profile and other intent context lives.
        Intents are durable and resumable across sessions.
        
        Args:
            intent_id: Unique intent identifier
            intent_type: Type of intent (e.g., "parse_content")
            target_artifact_id: Artifact this intent operates on
            context: Intent context (ingestion_profile, parse_options, etc.)
            tenant_id: Tenant identifier
            user_id: Optional user identifier
            session_id: Optional session identifier
        
        Returns:
            Dict with success status and result data
        """
        try:
            intent_record = {
                "intent_id": intent_id,
                "intent_type": intent_type,
                "status": "pending",
                "target_artifact_id": target_artifact_id,
                "context": context,
                "tenant_id": tenant_id,
                "created_by": user_id,
                "session_id": session_id
            }
            
            result = await self.insert_record(
                table="intent_executions",
                data=intent_record,
                user_context={"tenant_id": tenant_id}
            )
            
            if result.get("success"):
                self.logger.info(f"Pending intent created: {intent_id} ({intent_type}) for artifact {target_artifact_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create pending intent: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "create_pending_intent_failed"
            }
    
    async def get_pending_intents(
        self,
        tenant_id: str,
        target_artifact_id: Optional[str] = None,
        intent_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get pending intents.
        
        Used for UI queries like "show me files with pending parse intents".
        
        Args:
            tenant_id: Tenant identifier
            target_artifact_id: Optional filter by target artifact
            intent_type: Optional filter by intent type
        
        Returns:
            List of pending intent records
        """
        try:
            filter_conditions = {
                "tenant_id": tenant_id,
                "status": "pending"
            }
            
            if target_artifact_id:
                filter_conditions["target_artifact_id"] = target_artifact_id
            
            if intent_type:
                filter_conditions["intent_type"] = intent_type
            
            records = await self.query_records(
                table="intent_executions",
                user_context={"tenant_id": tenant_id},
                filter_conditions=filter_conditions
            )
            
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to get pending intents: {e}", exc_info=True)
            return []
    
    async def update_intent_status(
        self,
        intent_id: str,
        status: str,
        tenant_id: str,
        execution_id: Optional[str] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update intent execution status.
        
        Args:
            intent_id: Intent identifier
            status: New status (pending, in_progress, completed, failed, cancelled)
            tenant_id: Tenant identifier
            execution_id: Optional execution ID if executed
            error: Optional error message if failed
        
        Returns:
            Dict with success status
        """
        try:
            from datetime import datetime
            
            updates = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if execution_id:
                updates["execution_id"] = execution_id
            
            if status == "completed":
                updates["completed_at"] = datetime.utcnow().isoformat()
            
            if error:
                updates["error"] = error
            
            result = await self.update_record(
                table="intent_executions",
                data=updates,
                user_context={"tenant_id": tenant_id},
                filter_conditions={"intent_id": intent_id}
            )
            
            if result.get("success"):
                self.logger.info(f"Intent status updated: {intent_id} -> {status}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update intent status: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "update_intent_status_failed"
            }
