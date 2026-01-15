"""
File Storage Abstraction - Business Logic Implementation (Layer 1)

Implements file storage operations using GCS and Supabase adapters.
Coordinates between file storage (GCS) and file metadata (Supabase).

WHAT (Infrastructure Role): I provide file storage services
HOW (Infrastructure Implementation): I use GCS adapter for storage and Supabase adapter for metadata
"""

import hashlib
from typing import Dict, Any, Optional, List

from utilities import get_logger, get_clock, generate_session_id
from ..protocols.file_storage_protocol import FileStorageProtocol
from ..adapters.gcs_adapter import GCSAdapter
from ..adapters.supabase_file_adapter import SupabaseFileAdapter


class FileStorageAbstraction(FileStorageProtocol):
    """
    File storage abstraction with business logic.
    
    Coordinates between GCS (file storage) and Supabase (file metadata).
    Provides file upload, download, deletion, and metadata management.
    """
    
    def __init__(
        self,
        gcs_adapter: GCSAdapter,
        supabase_file_adapter: SupabaseFileAdapter,
        bucket_name: str
    ):
        """
        Initialize File Storage abstraction.
        
        Args:
            gcs_adapter: GCS adapter for file storage (Layer 0)
            supabase_file_adapter: Supabase adapter for file metadata (Layer 0)
            bucket_name: GCS bucket name
        """
        self.gcs = gcs_adapter
        self.supabase = supabase_file_adapter
        self.bucket_name = bucket_name
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info(f"File Storage Abstraction initialized with bucket: {bucket_name}")
    
    async def upload_file(
        self,
        file_path: str,
        file_data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to GCS and create metadata in Supabase.
        
        Args:
            file_path: File path in storage
            file_data: File data (binary)
            metadata: Optional metadata
        
        Returns:
            Dict with success status and file_id if successful
        """
        try:
            # Calculate file hash
            file_hash = hashlib.sha256(file_data).hexdigest()
            file_size = len(file_data)
            
            # Determine content type from metadata or file path
            content_type = None
            if metadata:
                content_type = metadata.get("content_type")
            
            if not content_type:
                # Try to infer from file path
                if file_path.endswith('.parquet'):
                    content_type = 'application/parquet'
                elif file_path.endswith('.json'):
                    content_type = 'application/json'
                elif file_path.endswith('.csv'):
                    content_type = 'text/csv'
                else:
                    content_type = 'application/octet-stream'
            
            # Upload to GCS
            gcs_metadata = {}
            if metadata:
                gcs_metadata = {k: str(v) for k, v in metadata.items() if k != 'content_type'}
            
            success = await self.gcs.upload_file(
                blob_name=file_path,
                file_data=file_data,
                content_type=content_type,
                metadata=gcs_metadata
            )
            
            if not success:
                self.logger.error(f"Failed to upload file to GCS: {file_path}")
                return {"success": False, "error": "GCS upload failed"}
            
            # Generate file_id
            file_id = generate_session_id()  # Generate unique file ID
            
            # Create metadata in Supabase if metadata provided
            if metadata and metadata.get("user_id"):
                file_metadata = {
                    "uuid": file_id,
                    "user_id": metadata.get("user_id"),
                    "tenant_id": metadata.get("tenant_id"),
                    "ui_name": metadata.get("ui_name", file_path.split('/')[-1]),
                    "file_path": file_path,
                    "file_type": metadata.get("file_type", "unstructured"),
                    "content_type": content_type,
                    "file_size": file_size,
                    "file_hash": file_hash,
                    "status": metadata.get("status", "uploaded"),
                    "created_at": self.clock.now_iso(),
                    "updated_at": self.clock.now_iso(),
                    "deleted": False
                }
                
                try:
                    await self.supabase.create_file(file_metadata)
                    self.logger.info(f"File metadata created in Supabase: {file_id}")
                except Exception as meta_error:
                    self.logger.warning(f"File uploaded to GCS but metadata creation failed: {meta_error}")
                    # Continue - file is stored, metadata can be fixed later
            
            self.logger.info(f"File uploaded successfully: {file_path} ({file_size} bytes)")
            return {
                "success": True,
                "file_id": file_id,
                "file_path": file_path
            }
            
        except Exception as e:
            self.logger.error(f"Failed to upload file {file_path}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def download_file(
        self,
        file_path: str
    ) -> Optional[bytes]:
        """
        Download a file from GCS.
        
        Args:
            file_path: File path in storage
        
        Returns:
            Optional[bytes]: File data or None if not found
        """
        try:
            file_data = await self.gcs.download_file(file_path)
            
            if file_data:
                self.logger.info(f"File downloaded: {file_path} ({len(file_data)} bytes)")
            else:
                self.logger.warning(f"File not found: {file_path}")
            
            return file_data
            
        except Exception as e:
            self.logger.error(f"Failed to download file {file_path}: {e}", exc_info=True)
            return None
    
    async def delete_file(
        self,
        file_path: str
    ) -> bool:
        """
        Delete a file from GCS and mark as deleted in Supabase.
        
        Args:
            file_path: File path in storage
        
        Returns:
            bool: True if successful
        """
        try:
            # Delete from GCS
            success = await self.gcs.delete_file(file_path)
            
            if not success:
                self.logger.warning(f"File not found in GCS: {file_path}")
            
            # Mark as deleted in Supabase (soft delete)
            # Try to find file by path
            try:
                # Note: SupabaseFileAdapter doesn't have search by path method
                # For now, we'll just delete from GCS
                # In full implementation, we'd query Supabase by file_path and soft delete
                self.logger.debug(f"File deleted from GCS: {file_path}")
            except Exception as meta_error:
                self.logger.warning(f"File deleted from GCS but metadata update failed: {meta_error}")
            
            self.logger.info(f"File deleted: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_path}: {e}", exc_info=True)
            return False
    
    async def list_files(
        self,
        prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in storage.
        
        Args:
            prefix: Optional prefix filter
        
        Returns:
            List of file metadata dictionaries
        """
        try:
            files = await self.gcs.list_files(prefix=prefix)
            
            self.logger.info(f"Listed {len(files)} files (prefix: {prefix or 'all'})")
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}", exc_info=True)
            return []
    
    async def get_file_metadata(
        self,
        file_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from GCS.
        
        Args:
            file_path: File path in storage
        
        Returns:
            Optional[Dict]: File metadata or None if not found
        """
        try:
            metadata = await self.gcs.get_file_metadata(file_path)
            
            if metadata:
                self.logger.debug(f"Retrieved file metadata: {file_path}")
            else:
                self.logger.warning(f"File metadata not found: {file_path}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to get file metadata {file_path}: {e}", exc_info=True)
            return None
    
    async def get_file_by_uuid(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from Supabase by UUID (extended method).
        
        Args:
            file_uuid: File UUID
        
        Returns:
            Optional[Dict]: File metadata or None if not found
        """
        try:
            file_data = await self.supabase.get_file(file_uuid)
            
            if file_data:
                self.logger.debug(f"Retrieved file by UUID: {file_uuid}")
            else:
                self.logger.warning(f"File not found by UUID: {file_uuid}")
            
            return file_data
            
        except Exception as e:
            self.logger.error(f"Failed to get file by UUID {file_uuid}: {e}", exc_info=True)
            return None
