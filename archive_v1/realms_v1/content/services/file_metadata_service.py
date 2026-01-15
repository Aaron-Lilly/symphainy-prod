"""
File Metadata Service

Manages file metadata and lineage tracking across uploaded, parsed, and embedded files.
Preserves user-friendly names (ui_name) and maintains lineage links.

WHAT (Content Realm): I manage file metadata and lineage
HOW (Service): I use SupabaseFileAdapter to store metadata in Supabase tables
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger, get_clock, generate_file_id
from symphainy_platform.foundations.public_works.adapters.supabase_file_adapter import SupabaseFileAdapter


class FileMetadataService:
    """
    File Metadata Service.
    
    Manages file metadata and lineage tracking:
    - Original uploaded files (project_files table)
    - Parsed files (parsed_data_files table)
    - Embedded files (embedding_files table)
    
    Preserves user-friendly names (ui_name) and maintains lineage links.
    """
    
    def __init__(self, supabase_file_adapter: SupabaseFileAdapter):
        """
        Initialize File Metadata Service.
        
        Args:
            supabase_file_adapter: SupabaseFileAdapter instance for database operations
        """
        self.supabase_adapter = supabase_file_adapter
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        if not self.supabase_adapter:
            self.logger.warning("SupabaseFileAdapter not provided - file metadata operations may fail")
    
    async def create_file_metadata(
        self,
        file_id: str,
        ui_name: str,
        original_filename: str,
        file_type: str,
        tenant_id: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create file metadata for original uploaded file.
        
        Args:
            file_id: File UUID (from FileStorageAbstraction)
            ui_name: User-friendly display name (e.g., "Balances")
            original_filename: Full original filename
            file_type: File type (e.g., "xlsx", "pdf")
            tenant_id: Tenant identifier
            user_id: User identifier
            metadata: Optional additional metadata
        
        Returns:
            Dict with created file metadata
        """
        if not self.supabase_adapter:
            raise RuntimeError("SupabaseFileAdapter not available")
        
        try:
            file_data = {
                "uuid": file_id,
                "ui_name": ui_name,
                "original_filename": original_filename,
                "file_type": file_type,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "status": "uploaded",
                "created_at": self.clock.now_iso(),
                "updated_at": self.clock.now_iso(),
                "deleted": False
            }
            
            if metadata:
                file_data.update(metadata)
            
            result = await self.supabase_adapter.create_file(file_data)
            self.logger.info(f"✅ Created file metadata: {file_id} (ui_name: {ui_name})")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create file metadata: {e}", exc_info=True)
            raise
    
    async def create_parsed_file_metadata(
        self,
        parsed_file_id: str,
        file_id: str,
        ui_name: str,
        tenant_id: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create parsed file metadata with lineage link to original.
        
        Args:
            parsed_file_id: Parsed file UUID
            file_id: Original file UUID (lineage link)
            ui_name: User-friendly display name (e.g., "parsed_Balances")
            tenant_id: Tenant identifier
            user_id: User identifier
            metadata: Optional additional metadata
        
        Returns:
            Dict with created parsed file metadata
        """
        if not self.supabase_adapter:
            raise RuntimeError("SupabaseFileAdapter not available")
        
        try:
            parsed_file_data = {
                "parsed_file_id": parsed_file_id,
                "file_id": file_id,  # Lineage link to original
                "ui_name": ui_name,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "status": "parsed",
                "parsed_at": self.clock.now_iso(),
                "created_at": self.clock.now_iso(),
                "updated_at": self.clock.now_iso()
            }
            
            if metadata:
                parsed_file_data.update(metadata)
            
            result = await self.supabase_adapter.create_parsed_file(parsed_file_data)
            self.logger.info(f"✅ Created parsed file metadata: {parsed_file_id} (ui_name: {ui_name}, parent: {file_id})")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create parsed file metadata: {e}", exc_info=True)
            raise
    
    async def create_embedding_file_metadata(
        self,
        embedding_id: str,
        parsed_file_id: str,
        file_id: str,
        ui_name: str,
        tenant_id: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create embedding file metadata with lineage links to parsed and original.
        
        Args:
            embedding_id: Embedding UUID
            parsed_file_id: Parsed file UUID (lineage link)
            file_id: Original file UUID (lineage link)
            ui_name: User-friendly display name (e.g., "embedded_Balances")
            tenant_id: Tenant identifier
            user_id: User identifier
            metadata: Optional additional metadata
        
        Returns:
            Dict with created embedding file metadata
        """
        if not self.supabase_adapter:
            raise RuntimeError("SupabaseFileAdapter not available")
        
        try:
            embedding_file_data = {
                "uuid": embedding_id,
                "parsed_file_id": parsed_file_id,  # Lineage link to parsed file
                "file_id": file_id,  # Lineage link to original file
                "ui_name": ui_name,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "status": "embedded",
                "created_at": self.clock.now_iso(),
                "updated_at": self.clock.now_iso()
            }
            
            if metadata:
                embedding_file_data.update(metadata)
            
            result = await self.supabase_adapter.create_embedding_file(embedding_file_data)
            self.logger.info(f"✅ Created embedding file metadata: {embedding_id} (ui_name: {ui_name}, parsed: {parsed_file_id}, original: {file_id})")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create embedding file metadata: {e}", exc_info=True)
            raise
    
    async def get_file_lineage(
        self,
        file_id: Optional[str] = None,
        ui_name: Optional[str] = None,
        user_id: str = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get complete file lineage: original → parsed → embedded.
        
        Args:
            file_id: File UUID (optional, if ui_name not provided)
            ui_name: User-friendly name (optional, if file_id not provided)
            user_id: User identifier (required if using ui_name)
            tenant_id: Tenant identifier (optional)
        
        Returns:
            Dict with original_file, parsed_files, embedded_files
        """
        if not self.supabase_adapter:
            raise RuntimeError("SupabaseFileAdapter not available")
        
        try:
            # If ui_name provided, get file_id first
            if ui_name and not file_id:
                if not user_id:
                    raise ValueError("user_id required when querying by ui_name")
                
                # Try to find in project_files first
                files = await self.supabase_adapter.list_files(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    filters={"ui_name": ui_name}
                )
                if files:
                    file_id = files[0].get("uuid")
                else:
                    # Try parsed_data_files
                    parsed_file = await self.supabase_adapter.get_parsed_file_by_ui_name(
                        ui_name=ui_name,
                        user_id=user_id,
                        tenant_id=tenant_id
                    )
                    if parsed_file:
                        file_id = parsed_file.get("file_id")
                    else:
                        # Try embedding_files
                        embedding_file = await self.supabase_adapter.get_embedding_file_by_ui_name(
                            ui_name=ui_name,
                            user_id=user_id,
                            tenant_id=tenant_id
                        )
                        if embedding_file:
                            file_id = embedding_file.get("file_id")
            
            if not file_id:
                return {"original_file": None, "parsed_files": [], "embedded_files": []}
            
            # Get lineage using adapter method
            lineage = await self.supabase_adapter.get_file_lineage(
                file_id=file_id,
                user_id=user_id or "",
                tenant_id=tenant_id
            )
            
            return lineage
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get file lineage: {e}", exc_info=True)
            return {"original_file": None, "parsed_files": [], "embedded_files": []}
    
    async def get_file_by_ui_name(
        self,
        ui_name: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        file_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get file metadata by ui_name (supports uploaded, parsed, embedded).
        
        Args:
            ui_name: User-friendly name
            user_id: User identifier
            tenant_id: Tenant identifier (optional)
            file_type: File type filter ("uploaded", "parsed", "embedded") (optional)
        
        Returns:
            File metadata dict or None if not found
        """
        if not self.supabase_adapter:
            raise RuntimeError("SupabaseFileAdapter not available")
        
        try:
            # Try project_files first (uploaded files)
            if not file_type or file_type == "uploaded":
                files = await self.supabase_adapter.list_files(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    filters={"ui_name": ui_name}
                )
                if files:
                    return {"file_type": "uploaded", **files[0]}
            
            # Try parsed_data_files
            if not file_type or file_type == "parsed":
                parsed_file = await self.supabase_adapter.get_parsed_file_by_ui_name(
                    ui_name=ui_name,
                    user_id=user_id,
                    tenant_id=tenant_id
                )
                if parsed_file:
                    return {"file_type": "parsed", **parsed_file}
            
            # Try embedding_files
            if not file_type or file_type == "embedded":
                embedding_file = await self.supabase_adapter.get_embedding_file_by_ui_name(
                    ui_name=ui_name,
                    user_id=user_id,
                    tenant_id=tenant_id
                )
                if embedding_file:
                    return {"file_type": "embedded", **embedding_file}
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get file by ui_name {ui_name}: {e}", exc_info=True)
            return None
    
    def sanitize_ui_name(self, filename: str) -> str:
        """
        Sanitize filename to create user-friendly ui_name.
        
        Removes extension and special characters, keeps it readable.
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized ui_name
        """
        # Remove extension
        if '.' in filename:
            ui_name = filename.rsplit('.', 1)[0]
        else:
            ui_name = filename
        
        # Remove special characters, keep alphanumeric, spaces, hyphens, underscores
        import re
        ui_name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', ui_name)
        
        # Trim whitespace
        ui_name = ui_name.strip()
        
        # If empty after sanitization, use a default
        if not ui_name:
            ui_name = "file"
        
        return ui_name
    
    def generate_parsed_ui_name(self, original_ui_name: str) -> str:
        """
        Generate parsed file ui_name from original.
        
        Pattern: "parsed_{original_ui_name}"
        
        Args:
            original_ui_name: Original file ui_name
        
        Returns:
            Parsed file ui_name
        """
        return f"parsed_{original_ui_name}"
    
    def generate_embedded_ui_name(self, original_ui_name: str) -> str:
        """
        Generate embedded file ui_name from original.
        
        Pattern: "embedded_{original_ui_name}"
        
        Args:
            original_ui_name: Original file ui_name
        
        Returns:
            Embedded file ui_name
        """
        return f"embedded_{original_ui_name}"
