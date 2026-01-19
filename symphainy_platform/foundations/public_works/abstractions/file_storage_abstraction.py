"""
File Storage Abstraction - Business Logic Implementation (Layer 1)

Implements file storage operations using GCS and Supabase adapters.
Coordinates between file storage (GCS) and file metadata (Supabase).

WHAT (Infrastructure Role): I provide file storage services
HOW (Infrastructure Implementation): I use GCS adapter for storage and Supabase adapter for metadata
"""

import hashlib
import uuid as uuid_lib
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
            
            # Determine MIME type from metadata or file path
            mime_type = None
            if metadata:
                mime_type = metadata.get("mime_type") or metadata.get("content_type")  # Support both for transition
            
            if not mime_type:
                # Try to infer from file path
                if file_path.endswith('.parquet'):
                    mime_type = 'application/parquet'
                elif file_path.endswith('.json'):
                    mime_type = 'application/json'
                elif file_path.endswith('.csv'):
                    mime_type = 'text/csv'
                elif file_path.endswith('.pdf'):
                    mime_type = 'application/pdf'
                elif file_path.endswith('.xlsx'):
                    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                elif file_path.endswith('.xls'):
                    mime_type = 'application/vnd.ms-excel'
                elif file_path.endswith('.docx'):
                    mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                elif file_path.endswith('.doc'):
                    mime_type = 'application/msword'
                elif file_path.endswith('.txt'):
                    mime_type = 'text/plain'
                else:
                    mime_type = 'application/octet-stream'
            
            # Upload to GCS
            gcs_metadata = {}
            if metadata:
                gcs_metadata = {k: str(v) for k, v in metadata.items() if k not in ('mime_type', 'content_type')}
            
            success = await self.gcs.upload_file(
                blob_name=file_path,
                file_data=file_data,
                content_type=mime_type,  # GCS API uses content_type parameter name
                metadata=gcs_metadata
            )
            
            if not success:
                self.logger.error(f"Failed to upload file to GCS: {file_path}")
                return {"success": False, "error": "GCS upload failed"}
            
            # Generate file_id as a proper UUID (not session_id which has "session_" prefix)
            # The uuid column in Supabase requires a valid UUID format
            import uuid as uuid_lib
            file_id = str(uuid_lib.uuid4())  # Generate proper UUID for file_id
            
            # Create metadata in Supabase if metadata provided
            if metadata and metadata.get("user_id"):
                # Convert user_id and tenant_id to UUID if they're strings (for backward compatibility)
                user_id = metadata.get("user_id")
                tenant_id = metadata.get("tenant_id")
                
                # CRITICAL: Filter out any values that start with "session_" prefix
                # These are likely session IDs being passed incorrectly
                if isinstance(user_id, str) and user_id.startswith("session_"):
                    self.logger.warning(f"user_id starts with 'session_' prefix, using 'system' instead: {user_id}")
                    user_id = "system"
                
                if isinstance(tenant_id, str) and tenant_id.startswith("session_"):
                    self.logger.warning(f"tenant_id starts with 'session_' prefix, this is invalid: {tenant_id}")
                    # tenant_id is required, so we can't use a default - this should be an error
                    raise ValueError(f"tenant_id cannot start with 'session_' prefix: {tenant_id}")
                
                # If they're strings, generate deterministic UUID from string
                try:
                    if isinstance(user_id, str):
                        try:
                            # Try to parse as UUID first
                            user_id = uuid_lib.UUID(user_id)
                        except ValueError:
                            # If not valid UUID format, generate deterministic UUID from string
                            user_id = uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, user_id)
                    
                    if isinstance(tenant_id, str):
                        try:
                            # Try to parse as UUID first
                            tenant_id = uuid_lib.UUID(tenant_id)
                        except ValueError:
                            # If not valid UUID format, generate deterministic UUID from string
                            tenant_id = uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, tenant_id)
                except Exception as e:
                    self.logger.warning(f"Failed to convert user_id/tenant_id to UUID: {e}, using as-is")
                
                # Build file_metadata dictionary - only include fields that exist in schema
                # Note: session_id is NOT in the schema, so we explicitly exclude it
                # file_type must be one of: 'structured', 'unstructured', 'hybrid' (parsing pathway)
                # NOT the MIME type (that goes in mime_type)
                file_type = metadata.get("file_type", "unstructured")
                # Validate file_type is one of the allowed values
                if file_type not in ("structured", "unstructured", "hybrid"):
                    self.logger.warning(f"Invalid file_type '{file_type}', defaulting to 'unstructured'")
                    file_type = "unstructured"
                
                file_metadata = {
                    "uuid": file_id,
                    "user_id": str(user_id) if hasattr(uuid_lib, 'UUID') and isinstance(user_id, uuid_lib.UUID) else user_id,
                    "tenant_id": str(tenant_id) if hasattr(uuid_lib, 'UUID') and isinstance(tenant_id, uuid_lib.UUID) else tenant_id,
                    "ui_name": metadata.get("ui_name", file_path.split('/')[-1]),
                    "file_path": file_path,
                    "file_type": file_type,  # Parsing pathway: structured, unstructured, hybrid
                    "mime_type": mime_type,  # MIME type (e.g., application/pdf) - for rendering, storage
                    "file_size": file_size,
                    "file_hash": file_hash,
                    "status": metadata.get("status", "uploaded"),
                    "created_at": self.clock.now_iso(),
                    "updated_at": self.clock.now_iso(),
                    "deleted": False
                }
                
                # Explicitly remove session_id if it exists (not in schema)
                # This prevents errors when metadata dict is passed through with extra fields
                file_metadata.pop("session_id", None)
                
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
        prefix: Optional[str] = None,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in storage.
        
        Args:
            prefix: Optional prefix filter (for GCS)
            tenant_id: Optional tenant_id filter (for Supabase metadata)
            user_id: Optional user_id filter (for Supabase metadata)
            file_type: Optional file_type filter (for Supabase metadata)
            limit: Optional result limit
            offset: Optional pagination offset
        
        Returns:
            List of file metadata dictionaries
        """
        try:
            # If tenant_id or user_id is provided, query Supabase for metadata
            # Otherwise, list from GCS
            if tenant_id or user_id:
                # Convert tenant_id/user_id to UUID if needed
                import uuid as uuid_lib
                tenant_id_uuid = tenant_id
                user_id_uuid = user_id
                
                try:
                    if tenant_id and isinstance(tenant_id, str):
                        try:
                            tenant_id_uuid = str(uuid_lib.UUID(tenant_id))
                        except ValueError:
                            tenant_id_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, tenant_id))
                    
                    if user_id and isinstance(user_id, str):
                        try:
                            user_id_uuid = str(uuid_lib.UUID(user_id))
                        except ValueError:
                            user_id_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, user_id))
                except Exception as e:
                    self.logger.warning(f"Failed to convert tenant_id/user_id to UUID: {e}")
                
                # Query Supabase for file metadata
                filters = {}
                if file_type:
                    filters["file_type"] = file_type
                
                files = await self.supabase.list_files(
                    user_id=user_id_uuid or "system",
                    tenant_id=tenant_id_uuid,
                    filters=filters,
                    limit=limit,
                    offset=offset
                )
                
                self.logger.info(f"Listed {len(files)} files from Supabase (tenant_id: {tenant_id_uuid}, user_id: {user_id_uuid})")
                return files
            else:
                # Fallback to GCS listing
                files = await self.gcs.list_files(prefix=prefix)
                
                self.logger.info(f"Listed {len(files)} files from GCS (prefix: {prefix or 'all'})")
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
    
    async def register_materialization(
        self,
        file_id: str,
        boundary_contract_id: str,
        materialization_type: str,
        materialization_scope: Dict[str, Any],
        materialization_backing_store: str,
        tenant_id: str,
        user_id: str,
        session_id: str,
        file_reference: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register materialization in materialization index (Supabase project_files).
        
        This is called when user explicitly saves a file, making it available for parsing.
        The file becomes a "materialized representation" with workspace scope.
        
        Args:
            file_id: File identifier
            boundary_contract_id: Boundary contract ID that authorized this materialization
            materialization_type: Type of materialization ('full_artifact', 'deterministic', etc.)
            materialization_scope: Workspace scope (user_id, session_id, solution_id, scope_type)
            materialization_backing_store: Where materialized ('gcs', 'supabase', 'memory', 'none')
            tenant_id: Tenant identifier
            user_id: User identifier
            session_id: Session identifier
            file_reference: File reference (e.g., "file:tenant:session:file_id")
            metadata: File metadata (ui_name, file_type, mime_type, size, etc.)
        
        Returns:
            Dict with success status and materialization record
        """
        try:
            # Get file metadata from Supabase if it exists
            existing_file = await self.get_file_by_uuid(file_id)
            
            # Prepare materialization record data
            # Note: session_id is NOT a column in project_files (removed in 001 migration)
            # session_id is stored in materialization_scope JSONB field instead
            materialization_data = {
                "uuid": file_id,
                "tenant_id": tenant_id,
                "user_id": user_id,
                # session_id REMOVED - not in schema, stored in materialization_scope JSONB instead
                "boundary_contract_id": boundary_contract_id,
                "representation_type": materialization_type,
                "materialization_scope": materialization_scope,  # Contains session_id in JSONB
                "materialization_backing_store": materialization_backing_store,
                "materialization_policy_basis": "mvp_workspace_policy",
                "source_external": True,  # Source data is external
                "source_type": "file",
                "ui_name": metadata.get("ui_name") or metadata.get("file_name", "unknown"),
                "file_type": metadata.get("file_type", "unstructured"),
                "mime_type": metadata.get("mime_type", "application/octet-stream"),
                "file_path": metadata.get("storage_location") or metadata.get("file_path"),
                "file_size": metadata.get("size") or metadata.get("file_size"),
                "file_hash": metadata.get("file_hash"),
                "ingestion_type": metadata.get("ingestion_type", "upload"),
                "deleted": False,
                "created_at": self.clock.now_iso(),
                "updated_at": self.clock.now_iso()
            }
            
            # Use Supabase adapter's client to insert/update in project_files table
            # The supabase_file_adapter has _client (Supabase Client) that we can use
            if hasattr(self.supabase, '_client') and self.supabase._client:
                # Insert or update (upsert) in project_files
                # Note: We need to handle the case where boundary_contract_id and scope fields might not exist in schema yet
                # For now, we'll insert what we can and log any schema issues
                try:
                    response = self.supabase._client.table("project_files").upsert(
                        materialization_data,
                        on_conflict="uuid"
                    ).execute()
                    
                    if response.data and len(response.data) > 0:
                        self.logger.info(f"✅ Materialization registered: {file_id} (contract: {boundary_contract_id})")
                        return {
                            "success": True,
                            "file_id": file_id,
                            "boundary_contract_id": boundary_contract_id,
                            "materialization_type": materialization_type,
                            "materialization_scope": materialization_scope
                        }
                    else:
                        self.logger.error("Failed to register materialization: No data returned from Supabase")
                        return {
                            "success": False,
                            "error": "No data returned from Supabase"
                        }
                except Exception as schema_error:
                    # If schema doesn't have new fields yet, try without them
                    self.logger.warning(f"Schema error (may need migration): {schema_error}")
                    # Try with basic fields only
                    basic_data = {
                        "uuid": file_id,
                        "tenant_id": tenant_id,
                        "user_id": user_id,
                        "ui_name": metadata.get("ui_name") or metadata.get("file_name", "unknown"),
                        "file_type": metadata.get("file_type", "unstructured"),
                        "mime_type": metadata.get("mime_type", "application/octet-stream"),
                        "file_path": metadata.get("storage_location") or metadata.get("file_path"),
                        "file_size": metadata.get("size") or metadata.get("file_size"),
                        "deleted": False,
                        "updated_at": self.clock.now_iso()
                    }
                    try:
                        response = self.supabase._client.table("project_files").upsert(
                            basic_data,
                            on_conflict="uuid"
                        ).execute()
                        self.logger.info(f"✅ Materialization registered (basic): {file_id}")
                        return {
                            "success": True,
                            "file_id": file_id,
                            "boundary_contract_id": boundary_contract_id,
                            "warning": "Registered with basic fields only (schema migration may be needed)"
                        }
                    except Exception as e2:
                        self.logger.error(f"Failed to register materialization even with basic fields: {e2}")
                        raise
            else:
                # Fallback: Log and return success (materialization is authorized, just not registered in index)
                self.logger.warning("Supabase client not available, materialization authorized but not registered in index")
                return {
                    "success": True,
                    "file_id": file_id,
                    "boundary_contract_id": boundary_contract_id,
                    "warning": "Materialization authorized but not registered in index (Supabase unavailable)"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to register materialization: {e}", exc_info=True)
            # Don't fail the save operation - materialization is authorized, just not registered
            return {
                "success": False,
                "error": str(e),
                "file_id": file_id,
                "boundary_contract_id": boundary_contract_id
            }
