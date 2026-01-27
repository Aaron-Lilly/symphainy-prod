"""
GCS File Adapter - Raw Technology Client (Layer 0)

Raw Google Cloud Storage client wrapper for file operations.
This is the raw technology layer for GCS operations.

WHAT (Infrastructure Role): I provide raw GCS operations for file storage
HOW (Infrastructure Implementation): I use real GCS client with no business logic
"""

import json
from typing import Dict, Any, Optional, List, BinaryIO
from datetime import timedelta

try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound, GoogleCloudError
except ImportError:
    # Mock classes for when GCS is not available
    class MockBlob:
        def __init__(self, name):
            self.name = name
            self.content_type = None
            self.metadata = {}
        def upload_from_string(self, data, content_type=None):
            pass
        def upload_from_filename(self, filename, content_type=None):
            pass
        def upload_from_file(self, file_stream, content_type=None):
            pass
        def download_as_bytes(self):
            return b"mock data"
        def download_as_string(self):
            return "mock data"
        def exists(self):
            return True
        def delete(self):
            pass
        def reload(self):
            pass
        def patch(self):
            pass
    
    class MockBucket:
        def __init__(self, name):
            self.name = name
            self.location = "mock-location"
            self.storage_class = "STANDARD"
            self.time_created = None
            self.updated = None
            self.versioning_enabled = False
            self.labels = {}
        def blob(self, name):
            return MockBlob(name)
        def list_blobs(self, prefix=None, delimiter=None):
            return []
        def copy_blob(self, source, dest_bucket, dest_name):
            pass
        def reload(self):
            pass
    
    class storage:
        class Client:
            def __init__(self, project=None, credentials=None, *args, **kwargs):
                self.project = project
            def bucket(self, name):
                return MockBucket(name)
            def delete_blobs(self, blobs):
                pass
        class Blob:
            def __init__(self): pass
    class NotFound(Exception): pass
    class GoogleCloudError(Exception): pass

from utilities import get_logger, get_clock


class GCSAdapter:
    """
    Raw GCS client wrapper for file operations - no business logic.
    
    CREDENTIALS ARCHITECTURE (Supabase Pattern):
    - credentials_json: Service account credentials as JSON string (from GCS_CREDENTIALS_JSON)
      Used ONLY for bucket operations (application data).
    - If credentials_json is None: Uses Application Default Credentials
      (compute service account on GCP VM, or GOOGLE_APPLICATION_CREDENTIALS
      if set - but we never modify GOOGLE_APPLICATION_CREDENTIALS).
    
    CRITICAL SEPARATION:
    - GOOGLE_APPLICATION_CREDENTIALS = SSH/VM access (infrastructure) - NEVER modified
    - GCS_CREDENTIALS_JSON = Bucket access (application data) - JSON string, no file paths!
    """
    
    def __init__(self, project_id: str, bucket_name: str, credentials_json: Optional[str] = None):
        """
        Initialize GCS file adapter with real connection.
        
        CREDENTIALS PATTERN (Supabase-style):
        - credentials_json: Service account credentials as JSON string (Supabase pattern)
        - If not provided, use Application Default Credentials
        - NO FILE PATHS - eliminates path resolution complexity and SSH/GCE concerns
        
        Args:
            project_id: GCP project ID
            bucket_name: GCS bucket name
            credentials_json: Service account credentials as JSON string (from GCS_CREDENTIALS_JSON)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.project_id = project_id
        self.bucket_name = bucket_name
        
        # CRITICAL: We do NOT modify GOOGLE_APPLICATION_CREDENTIALS globally
        # This would break SSH access and other GCP tools
        # Instead, we pass credentials directly to the client
        
        # Use JSON credentials (Supabase pattern - no file paths!)
        if credentials_json:
            try:
                from google.oauth2 import service_account
                
                # Strip quotes if present (env files may wrap JSON in quotes)
                json_str = str(credentials_json).strip("'\"")
                
                # Parse JSON string to dict
                creds_dict = json.loads(json_str)
                
                # Create credentials object from dict
                credentials = service_account.Credentials.from_service_account_info(
                    creds_dict
                )
                
                # Create client with credentials object
                self._client = storage.Client(
                    project=project_id,
                    credentials=credentials
                )
                self.logger.info("GCS client initialized with JSON credentials (Supabase pattern)")
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                self.logger.error(f"Failed to parse GCS credentials JSON: {e}")
                raise ValueError(f"Invalid GCS credentials JSON: {e}")
            except ImportError:
                self.logger.error("google.oauth2 not available - cannot use JSON credentials")
                raise ImportError("google.oauth2.service_account required for JSON credentials")
        else:
            # No explicit credentials - use Application Default Credentials
            # (reads from GOOGLE_APPLICATION_CREDENTIALS if set,
            # or uses compute service account if on GCP VM)
            self._client = storage.Client(project=project_id)
            self.logger.info("GCS client initialized with Application Default Credentials")
        
        # Create bucket (private - use wrapper methods instead)
        self._bucket = self._client.bucket(bucket_name)
        # Keep client and bucket as aliases for backward compatibility
        self.client = self._client
        self.bucket = self._bucket
        self.logger.info(f"GCS File adapter initialized with bucket: {bucket_name}, project: {project_id}")
    
    # ============================================================================
    # RAW FILE UPLOAD OPERATIONS
    # ============================================================================
    
    async def upload_file(self, blob_name: str, file_data: bytes, 
                         content_type: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> bool:
        """Raw file upload - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            
            # Prepare metadata first (before upload)
            if metadata:
                # Filter out file_type from metadata to avoid Content-Type mismatch
                # GCS uses content_type for the actual Content-Type header
                # file_type is a business logic concept, not a GCS metadata field
                filtered_metadata = {k: v for k, v in metadata.items() 
                                   if k not in ['file_type', 'content_type']}
                if filtered_metadata:
                    blob.metadata = filtered_metadata
            
            # Validate parquet bytes before upload (if it's a parquet file)
            if content_type and "parquet" in content_type.lower() and isinstance(file_data, bytes):
                if len(file_data) >= 4:
                    magic_bytes = file_data[:4]
                    footer_magic = file_data[-4:] if len(file_data) >= 4 else None
                    if magic_bytes == b'PAR1' and footer_magic == b'PAR1':
                        self.logger.debug(f"Parquet bytes validated: {len(file_data)} bytes, header={magic_bytes}, footer={footer_magic}")
                    else:
                        self.logger.error(f"Invalid parquet bytes: header={magic_bytes}, footer={footer_magic}, length={len(file_data)}")
                        raise ValueError(f"Invalid parquet bytes before upload: header={magic_bytes}, footer={footer_magic}")
            
            # Upload with explicit content_type to prevent auto-detection conflicts
            if content_type:
                blob.content_type = content_type
                blob.upload_from_string(file_data, content_type=content_type)
            else:
                blob.upload_from_string(file_data)
            
            self.logger.info(f"Successfully uploaded file {blob_name} to GCS (content_type: {content_type or 'auto-detected'}, size: {len(file_data)} bytes)")
            return True
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            self.logger.error(f"Failed to upload file {blob_name}")
            self.logger.error(f"   Error Type: {error_type}")
            self.logger.error(f"   Error Message: {error_msg}")
            self.logger.error(f"   Bucket: {self.bucket_name}")
            self.logger.error(f"   Project: {self.project_id}")
            import traceback
            self.logger.error(f"   Full Traceback:\n{traceback.format_exc()}")
            return False
    
    async def upload_file_from_path(self, blob_name: str, file_path: str,
                                   content_type: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> bool:
        """Raw file upload from path - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            
            if metadata:
                blob.metadata = metadata
            
            if content_type:
                blob.content_type = content_type
                blob.upload_from_filename(file_path, content_type=content_type)
            else:
                blob.upload_from_filename(file_path)
            
            return True
        except GoogleCloudError as e:
            self.logger.error(f"Failed to upload file from path {blob_name}: {e}")
            return False
    
    async def upload_file_from_stream(self, blob_name: str, file_stream: BinaryIO,
                                     content_type: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> bool:
        """Raw file upload from stream - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            
            if metadata:
                blob.metadata = metadata
            
            if content_type:
                blob.content_type = content_type
                blob.upload_from_file(file_stream, content_type=content_type)
            else:
                blob.upload_from_file(file_stream)
            
            return True
        except GoogleCloudError as e:
            self.logger.error(f"Failed to upload file from stream {blob_name}: {e}")
            return False
    
    # ============================================================================
    # RAW FILE DOWNLOAD OPERATIONS
    # ============================================================================
    
    async def download_file(self, blob_name: str) -> Optional[bytes]:
        """Raw file download - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            if not blob.exists():
                self.logger.warning(f"Blob does not exist: {blob_name}")
                return None
            
            file_data = blob.download_as_bytes()
            
            # Validate parquet bytes after download (if it's a parquet file)
            if file_data and len(file_data) >= 4:
                magic_bytes = file_data[:4]
                footer_magic = file_data[-4:] if len(file_data) >= 4 else None
                if magic_bytes == b'PAR1' and footer_magic == b'PAR1':
                    self.logger.debug(f"Parquet bytes validated: {len(file_data)} bytes, header={magic_bytes}, footer={footer_magic}")
                elif magic_bytes == b'PAR1':
                    # Header is valid but footer might be missing (could be truncated)
                    self.logger.warning(f"Parquet header valid but footer missing: header={magic_bytes}, footer={footer_magic}, length={len(file_data)}")
                else:
                    # Not a parquet file or corrupted
                    self.logger.debug(f"Non-parquet file: header={magic_bytes}, length={len(file_data)}")
            
            return file_data
        except GoogleCloudError as e:
            self.logger.error(f"Failed to download file {blob_name}: {e}")
            return None
    
    async def download_file_to_path(self, blob_name: str, file_path: str) -> bool:
        """Raw file download to path - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            if not blob.exists():
                return False
            blob.download_to_filename(file_path)
            return True
        except GoogleCloudError as e:
            self.logger.error(f"Failed to download file to path {blob_name}: {e}")
            return False
    
    async def download_file_to_stream(self, blob_name: str, file_stream: BinaryIO) -> bool:
        """Raw file download to stream - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            if not blob.exists():
                return False
            blob.download_to_file(file_stream)
            return True
        except GoogleCloudError as e:
            self.logger.error(f"Failed to download file to stream {blob_name}: {e}")
            return False
    
    # ============================================================================
    # RAW FILE METADATA OPERATIONS
    # ============================================================================
    
    async def get_file_metadata(self, blob_name: str) -> Optional[Dict[str, Any]]:
        """Raw file metadata retrieval - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            if not blob.exists():
                return None
            
            blob.reload()
            return {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "time_created": blob.time_created.isoformat() if blob.time_created else None,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "etag": blob.etag,
                "md5_hash": blob.md5_hash,
                "crc32c": blob.crc32c,
                "metadata": blob.metadata or {}
            }
        except GoogleCloudError as e:
            self.logger.error(f"Failed to get file metadata {blob_name}: {e}")
            return None
    
    async def update_file_metadata(self, blob_name: str, metadata: Dict[str, str]) -> bool:
        """Raw file metadata update - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            if not blob.exists():
                return False
            blob.metadata = metadata
            blob.patch()
            return True
        except GoogleCloudError as e:
            self.logger.error(f"Failed to update file metadata {blob_name}: {e}")
            return False
    
    # ============================================================================
    # RAW FILE LISTING OPERATIONS
    # ============================================================================
    
    async def list_files(self, prefix: Optional[str] = None, delimiter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Raw file listing - no business logic."""
        try:
            blobs = self._bucket.list_blobs(prefix=prefix, delimiter=delimiter)
            files = []
            for blob in blobs:
                files.append({
                    "name": blob.name,
                    "size": blob.size,
                    "content_type": blob.content_type,
                    "time_created": blob.time_created.isoformat() if blob.time_created else None,
                    "updated": blob.updated.isoformat() if blob.updated else None,
                    "etag": blob.etag
                })
            return files
        except GoogleCloudError as e:
            self.logger.error(f"Failed to list files: {e}")
            return []
    
    async def file_exists(self, blob_name: str) -> bool:
        """Raw file existence check - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            return blob.exists()
        except GoogleCloudError as e:
            self.logger.error(f"Failed to check file existence {blob_name}: {e}")
            return False
    
    # ============================================================================
    # RAW FILE DELETION OPERATIONS
    # ============================================================================
    
    async def delete_file(self, blob_name: str) -> bool:
        """Raw file deletion - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            if not blob.exists():
                return False
            blob.delete()
            return True
        except GoogleCloudError as e:
            self.logger.error(f"Failed to delete file {blob_name}: {e}")
            return False
    
    async def delete_files(self, blob_names: List[str]) -> int:
        """Raw multiple file deletion - no business logic."""
        try:
            blobs = [self._bucket.blob(name) for name in blob_names]
            self._client.delete_blobs(blobs)
            return len(blob_names)
        except GoogleCloudError as e:
            self.logger.error(f"Failed to delete files: {e}")
            return 0
    
    # ============================================================================
    # RAW FILE COPY OPERATIONS
    # ============================================================================
    
    async def copy_file(self, source_blob_name: str, destination_blob_name: str) -> bool:
        """Raw file copy - no business logic."""
        try:
            source_blob = self._bucket.blob(source_blob_name)
            if not source_blob.exists():
                return False
            self._bucket.copy_blob(source_blob, self._bucket, destination_blob_name)
            return True
        except GoogleCloudError as e:
            self.logger.error(f"Failed to copy file {source_blob_name}: {e}")
            return False
    
    async def move_file(self, source_blob_name: str, destination_blob_name: str) -> bool:
        """Raw file move - no business logic."""
        try:
            copy_success = await self.copy_file(source_blob_name, destination_blob_name)
            if not copy_success:
                return False
            delete_success = await self.delete_file(source_blob_name)
            if not delete_success:
                await self.delete_file(destination_blob_name)
                return False
            return True
        except GoogleCloudError as e:
            self.logger.error(f"Failed to move file {source_blob_name}: {e}")
            return False
    
    # ============================================================================
    # RAW URL OPERATIONS
    # ============================================================================
    
    async def generate_signed_url(self, blob_name: str, expiration: int = 3600,
                                 method: str = "GET") -> Optional[str]:
        """Raw signed URL generation - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            if not blob.exists():
                return None
            return blob.generate_signed_url(
                expiration=self.clock.now() + timedelta(seconds=expiration),
                method=method
            )
        except GoogleCloudError as e:
            self.logger.error(f"Failed to generate signed URL {blob_name}: {e}")
            return None
    
    async def get_public_url(self, blob_name: str) -> Optional[str]:
        """Raw public URL generation - no business logic."""
        try:
            blob = self._bucket.blob(blob_name)
            if not blob.exists():
                return None
            return blob.public_url
        except GoogleCloudError as e:
            self.logger.error(f"Failed to get public URL {blob_name}: {e}")
            return None
    
    # ============================================================================
    # RAW BUCKET OPERATIONS
    # ============================================================================
    
    async def get_bucket_info(self) -> Dict[str, Any]:
        """Raw bucket info - no business logic."""
        try:
            return {
                "name": self._bucket.name,
                "location": self._bucket.location,
                "storage_class": self._bucket.storage_class,
                "time_created": self._bucket.time_created.isoformat() if self._bucket.time_created else None,
                "updated": self._bucket.updated.isoformat() if self._bucket.updated else None,
                "versioning_enabled": self._bucket.versioning_enabled,
                "labels": self._bucket.labels or {}
            }
        except GoogleCloudError as e:
            self.logger.error(f"Failed to get bucket info: {e}")
            return {}
    
    async def test_connection(self) -> bool:
        """Raw connection test - no business logic."""
        try:
            self._bucket.reload()
            return True
        except GoogleCloudError as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
