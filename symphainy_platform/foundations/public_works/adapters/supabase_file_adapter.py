"""
Supabase File Management Adapter - Raw Technology Client (Layer 0)

Raw Supabase client wrapper for file management operations.
This is the raw technology layer for Supabase file metadata operations.

WHAT (Infrastructure Role): I provide raw Supabase operations for file management
HOW (Infrastructure Implementation): I use real Supabase client with no business logic
"""

from typing import Dict, Any, Optional, List
from supabase import create_client, Client

from utilities import get_logger, get_clock


class SupabaseFileAdapter:
    """Raw Supabase client wrapper for file management operations - no business logic."""
    
    def __init__(self, url: str, service_key: str):
        """
        Initialize Supabase file management adapter with real credentials.
        
        Args:
            url: Supabase project URL
            service_key: Supabase service role key
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        # Normalize URL - remove trailing slashes
        self.url = url.rstrip('/') if url else url
        self.service_key = service_key
        
        # Create Supabase client (private - use wrapper methods instead)
        self._client: Client = create_client(self.url, service_key)
        # Keep client as alias for backward compatibility
        self.client = self._client
        
        self.logger.info(f"Supabase File Management adapter initialized with URL: {self.url}")
    
    async def connect(self) -> bool:
        """Connect to Supabase (already connected in __init__)."""
        try:
            # Test connection
            result = self._client.table("project_files").select("uuid").limit(1).execute()
            self.logger.info("Supabase File Management adapter connected")
            return True
        except Exception as e:
            self.logger.error(f"Supabase File Management adapter connection failed: {e}")
            return False
    
    # ============================================================================
    # RAW FILE OPERATIONS
    # ============================================================================
    
    async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw file creation - no business logic."""
        try:
            result = self._client.table("project_files").insert(file_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            self.logger.error(f"Failed to create file: {e}")
            raise
    
    async def get_file(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """Raw file retrieval - no business logic."""
        try:
            result = self._client.table("project_files").select("*").eq("uuid", file_uuid).eq("deleted", False).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Failed to get file {file_uuid}: {e}")
            return None
    
    async def update_file(self, file_uuid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Raw file update - no business logic."""
        try:
            # Add updated_at timestamp
            updates["updated_at"] = self.clock.now_iso()
            
            result = self._client.table("project_files").update(updates).eq("uuid", file_uuid).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            self.logger.error(f"Failed to update file {file_uuid}: {e}")
            raise
    
    async def delete_file(self, file_uuid: str) -> bool:
        """Raw file deletion (soft delete) - no business logic."""
        try:
            result = self._client.table("project_files").update({
                "deleted": True,
                "updated_at": self.clock.now_iso()
            }).eq("uuid", file_uuid).execute()
            return len(result.data) > 0
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_uuid}: {e}")
            return False
    
    async def list_files(self, user_id: str, tenant_id: Optional[str] = None, 
                        filters: Optional[Dict[str, Any]] = None, 
                        limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Raw file listing - no business logic."""
        try:
            query = self._client.table("project_files").select("*").eq("user_id", user_id).eq("deleted", False)
            
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.range(offset, offset + (limit or 10) - 1)
            
            result = query.order("created_at", desc=True).execute()
            return result.data
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return []
    
    # ============================================================================
    # RAW FILE LINKING OPERATIONS
    # ============================================================================
    
    async def create_file_link(self, parent_uuid: str, child_uuid: str, link_type: str, 
                              generation_gap: int = 1, relationship_strength: str = "direct") -> Dict[str, Any]:
        """Raw file link creation - no business logic."""
        try:
            link_data = {
                "parent_uuid": parent_uuid,
                "child_uuid": child_uuid,
                "link_type": link_type,
                "generation_gap": generation_gap,
                "relationship_strength": relationship_strength
            }
            
            result = self._client.table("file_links").insert(link_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            self.logger.error(f"Failed to create file link: {e}")
            raise
    
    async def get_file_links(self, file_uuid: str, direction: str = "both") -> List[Dict[str, Any]]:
        """Raw file link retrieval - no business logic."""
        try:
            links = []
            
            if direction in ("parent", "both"):
                parent_result = self._client.table("file_links").select("*").eq("child_uuid", file_uuid).execute()
                links.extend(parent_result.data)
            
            if direction in ("child", "both"):
                child_result = self._client.table("file_links").select("*").eq("parent_uuid", file_uuid).execute()
                links.extend(child_result.data)
            
            return links
            
        except Exception as e:
            self.logger.error(f"Failed to get file links for {file_uuid}: {e}")
            return []
    
    async def delete_file_link(self, link_id: str) -> bool:
        """Raw file link deletion - no business logic."""
        try:
            result = self._client.table("file_links").delete().eq("id", link_id).execute()
            return len(result.data) > 0
        except Exception as e:
            self.logger.error(f"Failed to delete file link {link_id}: {e}")
            return False
    
    # ============================================================================
    # RAW LINEAGE OPERATIONS
    # ============================================================================
    
    async def get_lineage_tree(self, root_uuid: str) -> List[Dict[str, Any]]:
        """Raw lineage tree retrieval using SQL function - no business logic."""
        try:
            result = self._client.rpc("get_file_lineage_tree", {"root_uuid": root_uuid}).execute()
            return result.data
        except Exception as e:
            self.logger.error(f"Failed to get lineage tree for {root_uuid}: {e}")
            return []
    
    async def get_file_descendants(self, root_uuid: str) -> List[Dict[str, Any]]:
        """Raw descendants retrieval using SQL function - no business logic."""
        try:
            result = self._client.rpc("get_file_descendants", {"root_uuid": root_uuid}).execute()
            return result.data
        except Exception as e:
            self.logger.error(f"Failed to get descendants for {root_uuid}: {e}")
            return []
    
    # ============================================================================
    # RAW SEARCH OPERATIONS
    # ============================================================================
    
    async def search_files(self, user_id: str, search_term: str, 
                          content_type: Optional[str] = None,
                          file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Raw file search - no business logic."""
        try:
            query = self._client.table("project_files").select("*").eq("user_id", user_id).eq("deleted", False)
            
            # Text search on ui_name
            query = query.ilike("ui_name", f"%{search_term}%")
            
            if content_type:
                query = query.eq("content_type", content_type)
            
            if file_type:
                query = query.eq("file_type", file_type)
            
            result = query.order("created_at", desc=True).execute()
            return result.data
            
        except Exception as e:
            self.logger.error(f"Failed to search files: {e}")
            return []
    
    # ============================================================================
    # RAW STATISTICS OPERATIONS
    # ============================================================================
    
    async def get_file_statistics(self, user_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Raw file statistics - no business logic."""
        try:
            query = self._client.table("project_files").select("content_type, file_type, status").eq("user_id", user_id).eq("deleted", False)
            
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            
            result = query.execute()
            files = result.data
            
            # Calculate statistics
            total_files = len(files)
            content_types = {}
            file_types = {}
            statuses = {}
            
            for file in files:
                content_type = file.get("content_type", "unknown")
                file_type = file.get("file_type", "unknown")
                status = file.get("status", "unknown")
                
                content_types[content_type] = content_types.get(content_type, 0) + 1
                file_types[file_type] = file_types.get(file_type, 0) + 1
                statuses[status] = statuses.get(status, 0) + 1
            
            return {
                "total_files": total_files,
                "content_types": content_types,
                "file_types": file_types,
                "statuses": statuses,
                "timestamp": self.clock.now_iso()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file statistics: {e}")
            return {"total_files": 0, "content_types": {}, "file_types": {}, "statuses": {}}
    
    # ============================================================================
    # RAW HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Raw health check - no business logic."""
        try:
            # Test basic connection
            result = self._client.table("project_files").select("uuid").limit(1).execute()
            
            return {
                "status": "healthy",
                "message": "Supabase File Management adapter is operational",
                "timestamp": self.clock.now_iso()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Supabase File Management adapter error: {e}",
                "timestamp": self.clock.now_iso()
            }
    
    # ============================================================================
    # RAW PARSED FILE OPERATIONS
    # ============================================================================
    
    async def create_parsed_file(self, parsed_file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw parsed file creation - no business logic."""
        try:
            result = self._client.table("parsed_data_files").insert(parsed_file_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            self.logger.error(f"Failed to create parsed file: {e}")
            raise
    
    async def get_parsed_file(self, parsed_file_id: str) -> Optional[Dict[str, Any]]:
        """Raw parsed file retrieval - no business logic."""
        try:
            result = self._client.table("parsed_data_files").select("*").eq("parsed_file_id", parsed_file_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Failed to get parsed file {parsed_file_id}: {e}")
            return None
    
    async def list_parsed_files(self, user_id: str, tenant_id: Optional[str] = None,
                               file_id: Optional[str] = None,
                               filters: Optional[Dict[str, Any]] = None,
                               limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Raw parsed file listing - no business logic."""
        try:
            query = self._client.table("parsed_data_files").select("*").eq("user_id", user_id)
            
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            
            if file_id:
                query = query.eq("file_id", file_id)
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.range(offset, offset + (limit or 10) - 1)
            
            result = query.order("parsed_at", desc=True).execute()
            return result.data
            
        except Exception as e:
            self.logger.error(f"Failed to list parsed files: {e}")
            return []
    
    async def get_parsed_file_by_ui_name(self, ui_name: str, user_id: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Raw parsed file retrieval by ui_name - no business logic."""
        try:
            query = self._client.table("parsed_data_files").select("*").eq("ui_name", ui_name).eq("user_id", user_id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Failed to get parsed file by ui_name {ui_name}: {e}")
            return None
    
    # ============================================================================
    # RAW EMBEDDING FILE OPERATIONS
    # ============================================================================
    
    async def create_embedding_file(self, embedding_file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw embedding file creation - no business logic."""
        try:
            result = self._client.table("embedding_files").insert(embedding_file_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            self.logger.error(f"Failed to create embedding file: {e}")
            raise
    
    async def get_embedding_file(self, embedding_id: str) -> Optional[Dict[str, Any]]:
        """Raw embedding file retrieval - no business logic."""
        try:
            result = self._client.table("embedding_files").select("*").eq("uuid", embedding_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Failed to get embedding file {embedding_id}: {e}")
            return None
    
    async def list_embedding_files(self, user_id: str, tenant_id: Optional[str] = None,
                                  parsed_file_id: Optional[str] = None,
                                  file_id: Optional[str] = None,
                                  filters: Optional[Dict[str, Any]] = None,
                                  limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Raw embedding file listing - no business logic."""
        try:
            query = self._client.table("embedding_files").select("*").eq("user_id", user_id)
            
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            
            if parsed_file_id:
                query = query.eq("parsed_file_id", parsed_file_id)
            
            if file_id:
                query = query.eq("file_id", file_id)
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.range(offset, offset + (limit or 10) - 1)
            
            result = query.order("created_at", desc=True).execute()
            return result.data
            
        except Exception as e:
            self.logger.error(f"Failed to list embedding files: {e}")
            return []
    
    async def get_embedding_file_by_ui_name(self, ui_name: str, user_id: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Raw embedding file retrieval by ui_name - no business logic."""
        try:
            query = self._client.table("embedding_files").select("*").eq("ui_name", ui_name).eq("user_id", user_id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Failed to get embedding file by ui_name {ui_name}: {e}")
            return None
    
    # ============================================================================
    # RAW LINEAGE QUERIES
    # ============================================================================
    
    async def get_file_lineage(self, file_id: str, user_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Raw lineage retrieval - no business logic.
        
        Returns complete lineage: original → parsed → embedded
        """
        try:
            # Get original file
            original_file = await self.get_file(file_id)
            if not original_file:
                return {"original_file": None, "parsed_files": [], "embedded_files": []}
            
            # Get parsed files linked to original
            parsed_files = await self.list_parsed_files(
                user_id=user_id,
                tenant_id=tenant_id,
                file_id=file_id
            )
            
            # Get embedded files linked to original and parsed files
            embedded_files = []
            for parsed_file in parsed_files:
                parsed_file_id = parsed_file.get("parsed_file_id")
                if parsed_file_id:
                    embeddings = await self.list_embedding_files(
                        user_id=user_id,
                        tenant_id=tenant_id,
                        parsed_file_id=parsed_file_id,
                        file_id=file_id
                    )
                    embedded_files.extend(embeddings)
            
            return {
                "original_file": original_file,
                "parsed_files": parsed_files,
                "embedded_files": embedded_files
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file lineage for {file_id}: {e}")
            return {"original_file": None, "parsed_files": [], "embedded_files": []}
