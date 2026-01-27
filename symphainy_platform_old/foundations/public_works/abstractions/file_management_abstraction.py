"""
File Management Abstraction - Pure Infrastructure (Layer 1)

Implements file management operations using GCS and Supabase adapters.
Coordinates between file storage (GCS) and file metadata (Supabase).

WHAT (Infrastructure Role): I provide file storage services
HOW (Infrastructure Implementation): I use GCS adapter for storage and Supabase adapter for metadata

NOTE: This is PURE INFRASTRUCTURE - no business logic.
Business logic (UUID generation, validation, metadata enhancement) belongs in Platform SDK.
"""

from typing import Dict, Any, Optional, List

from utilities import get_logger
from ..protocols.file_management_protocol import FileManagementProtocol
from ..adapters.gcs_adapter import GCSAdapter
from ..adapters.supabase_file_adapter import SupabaseFileAdapter


class FileManagementAbstraction(FileManagementProtocol):
    """
    File management abstraction - pure infrastructure.
    
    Coordinates between GCS (file storage) and Supabase (file metadata).
    Returns raw data only (Dict[str, Any]), not business objects.
    Business logic (UUID generation, validation, metadata enhancement) belongs in Platform SDK.
    """
    
    def __init__(
        self,
        gcs_adapter: GCSAdapter,
        supabase_adapter: SupabaseFileAdapter
    ):
        """
        Initialize File Management abstraction.
        
        Args:
            gcs_adapter: GCS adapter for file storage (Layer 0)
            supabase_adapter: Supabase adapter for file metadata (Layer 0)
        """
        self.gcs = gcs_adapter
        self.supabase = supabase_adapter
        self.logger = get_logger(self.__class__.__name__)
        
        self.logger.info("File Management Abstraction initialized (pure infrastructure)")
    
    async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create file - pure infrastructure only.
        
        Stores file in GCS and metadata in Supabase.
        Returns raw data from adapters.
        
        Args:
            file_data: File data dict with:
                - file_content: bytes (required for GCS upload)
                - user_id: str (required)
                - ui_name: str (required)
                - file_type: str (required)
                - tenant_id: Optional[str]
                - mime_type: Optional[str]
                - metadata: Optional[Dict[str, Any]]
                - uuid: Optional[str] (if not provided, Platform SDK should generate)
                - All other fields passed through to Supabase
        
        Returns:
            Raw data from Supabase adapter (includes uuid, ui_name, file_type, etc.)
        """
        try:
            # Extract file content for GCS upload
            file_content = file_data.get("file_content")
            if not file_content:
                raise ValueError("file_content is required for file creation")
            
            # Extract GCS blob name (use uuid if provided, otherwise generate path)
            uuid = file_data.get("uuid")
            if not uuid:
                # Platform SDK should provide uuid, but if not, use a path-based approach
                # This is infrastructure fallback, not business logic
                blob_name = file_data.get("original_path") or f"files/{file_data.get('ui_name', 'file')}"
            else:
                blob_name = f"files/{uuid}"
            
            # Upload to GCS (pure infrastructure)
            # Use mime_type if provided, otherwise use content_type, otherwise default
            content_type = (
                file_data.get("mime_type") or
                file_data.get("content_type") or
                "application/octet-stream"
            )
            
            # Extract metadata for GCS (exclude file_content and other non-GCS fields)
            gcs_metadata = {}
            if file_data.get("metadata"):
                gcs_metadata = {k: str(v) for k, v in file_data["metadata"].items()}
            
            gcs_success = await self.gcs.upload_file(
                blob_name=blob_name,
                file_data=file_content,
                content_type=content_type,
                metadata=gcs_metadata
            )
            
            if not gcs_success:
                raise Exception(f"Failed to upload file to GCS: {blob_name}")
            
            # Prepare metadata for Supabase (pass through all fields, no business logic)
            supabase_metadata = {
                **file_data,  # Pass through all fields
                "original_path": blob_name,  # Store GCS path
                "service_context": {
                    "gcs_blob_name": blob_name,
                    "gcs_bucket": getattr(self.gcs, 'bucket_name', None),
                    "storage_type": "gcs"
                }
            }
            
            # Remove file_content from Supabase metadata (it's in GCS, not Supabase)
            supabase_metadata.pop("file_content", None)
            
            # Store file metadata in Supabase (pure infrastructure)
            result = await self.supabase.create_file(supabase_metadata)
            
            self.logger.info(f"File created: {result.get('uuid')} - {result.get('ui_name')} (GCS: {blob_name})")
            
            # Return raw data from Supabase
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create file: {e}", exc_info=True)
            raise
    
    async def get_file(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get file - pure infrastructure only.
        
        Retrieves file metadata from Supabase and file content from GCS.
        Returns raw data from adapters.
        
        Args:
            file_uuid: File UUID
        
        Returns:
            Raw file data dict with:
                - All Supabase metadata fields
                - file_content: bytes (from GCS) if available
        """
        try:
            # Get file metadata from Supabase
            result = await self.supabase.get_file(file_uuid)
            
            if not result:
                return None
            
            # Get file content from GCS if available
            service_context = result.get("service_context", {})
            if isinstance(service_context, dict):
                gcs_blob_name = service_context.get("gcs_blob_name") or result.get("original_path")
            else:
                gcs_blob_name = result.get("original_path")
            
            if gcs_blob_name:
                file_content = await self.gcs.download_file(blob_name=gcs_blob_name)
                if file_content:
                    result["file_content"] = file_content
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get file {file_uuid}: {e}", exc_info=True)
            raise
    
    async def update_file(self, file_uuid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update file - pure infrastructure only.
        
        Updates file metadata in Supabase.
        Returns raw data from adapter.
        
        Args:
            file_uuid: File UUID
            updates: Dictionary of fields to update
        
        Returns:
            Raw updated file data from Supabase
        """
        try:
            # Update file metadata in Supabase (pure infrastructure)
            result = await self.supabase.update_file(file_uuid, updates)
            
            self.logger.info(f"File updated: {file_uuid}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update file {file_uuid}: {e}", exc_info=True)
            raise
    
    async def delete_file(self, file_uuid: str) -> bool:
        """
        Delete file - pure infrastructure only.
        
        Deletes file from GCS and metadata from Supabase.
        Returns raw success status.
        
        Args:
            file_uuid: File UUID
        
        Returns:
            bool: True if successful
        """
        try:
            # Get file info first to get GCS blob name
            file_info = await self.supabase.get_file(file_uuid)
            
            if not file_info:
                self.logger.warning(f"File not found for deletion: {file_uuid}")
                return False
            
            # Delete file from GCS
            service_context = file_info.get("service_context", {})
            if isinstance(service_context, dict):
                gcs_blob_name = service_context.get("gcs_blob_name") or file_info.get("original_path")
            else:
                gcs_blob_name = file_info.get("original_path")
            
            if gcs_blob_name:
                try:
                    await self.gcs.delete_file(blob_name=gcs_blob_name)
                except Exception as gcs_error:
                    self.logger.warning(f"Error deleting from GCS: {gcs_error}")
            
            # Delete file metadata from Supabase
            result = await self.supabase.delete_file(file_uuid)
            
            if result:
                self.logger.info(f"File deleted: {file_uuid}")
            else:
                self.logger.error(f"Failed to delete file: {file_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_uuid}: {e}", exc_info=True)
            raise
    
    async def list_files(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List files - pure infrastructure only.
        
        Lists file metadata from Supabase.
        Returns raw data from adapter.
        
        Args:
            user_id: User ID
            tenant_id: Optional tenant ID
            filters: Optional filters dict
            limit: Optional limit
            offset: Optional offset
        
        Returns:
            List of raw file metadata dicts from Supabase
        """
        try:
            # List files from Supabase (pure infrastructure)
            result = await self.supabase.list_files(
                user_id=user_id,
                tenant_id=tenant_id,
                filters=filters or {},
                limit=limit,
                offset=offset
            )
            
            self.logger.debug(f"Listed {len(result)} files for user {user_id}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}", exc_info=True)
            raise
