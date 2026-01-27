"""
Artifact Storage Abstraction - Business Logic Implementation (Layer 1)

Implements artifact storage operations using GCS and Supabase adapters.
Coordinates between artifact storage (GCS) and artifact metadata (Supabase).

WHAT (Infrastructure Role): I provide artifact storage services
HOW (Infrastructure Implementation): I use GCS adapter for storage and Supabase adapter for metadata
"""

import json
import base64
import uuid as uuid_lib
from typing import Dict, Any, Optional, List

from utilities import get_logger, get_clock, generate_event_id
from ..protocols.artifact_storage_protocol import ArtifactStorageProtocol
from ..adapters.gcs_adapter import GCSAdapter
from ..adapters.supabase_file_adapter import SupabaseFileAdapter


class ArtifactStorageAbstraction(ArtifactStorageProtocol):
    """
    Artifact storage abstraction with business logic.
    
    Coordinates between GCS (artifact storage) and Supabase (artifact metadata).
    Handles both simple and composite artifacts.
    """
    
    def __init__(
        self,
        gcs_adapter: GCSAdapter,
        supabase_file_adapter: SupabaseFileAdapter,
        bucket_name: str
    ):
        """
        Initialize Artifact Storage abstraction.
        
        Args:
            gcs_adapter: GCS adapter for artifact storage (Layer 0)
            supabase_file_adapter: Supabase adapter for artifact metadata (Layer 0)
            bucket_name: GCS bucket name
        """
        self.gcs = gcs_adapter
        self.supabase = supabase_file_adapter
        self.bucket_name = bucket_name
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info(f"Artifact Storage Abstraction initialized with bucket: {bucket_name}")
    
    async def store_artifact(
        self,
        artifact_type: str,
        artifact_data: Dict[str, Any],
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store artifact in GCS and metadata in Supabase.
        
        Handles:
        - Simple artifacts (single JSON file)
        - Composite artifacts (embedded components)
        - Visual artifacts (stored separately)
        """
        try:
            # 1. Generate artifact_id
            artifact_id = generate_event_id()
            
            # 2. Extract visuals (store separately)
            visuals = {}
            artifact_json_data = artifact_data.copy()
            
            for key, value in artifact_data.items():
                if key.endswith("_visual") and isinstance(value, dict):
                    if "image_base64" in value:
                        # Store visual separately
                        visual_path = f"artifacts/{artifact_type}/{tenant_id}/{artifact_id}/{key}.png"
                        try:
                            image_bytes = base64.b64decode(value["image_base64"])
                            
                            upload_result = await self.gcs.upload_file(
                                blob_name=visual_path,
                                file_data=image_bytes,
                                content_type="image/png",
                                metadata={
                                    "artifact_id": artifact_id,
                                    "artifact_type": artifact_type,
                                    "tenant_id": tenant_id,
                                    "visual_type": key
                                }
                            )
                            
                            if upload_result:
                                # Replace with reference
                                visuals[key] = {
                                    "storage_path": visual_path,
                                    "format": "png"
                                }
                                artifact_json_data[key] = visuals[key]
                                self.logger.info(f"Visual stored separately: {visual_path}")
                            else:
                                self.logger.warning(f"Failed to store visual: {visual_path}")
                        except Exception as e:
                            self.logger.warning(f"Failed to decode/store visual {key}: {e}")
                            # Continue - visual will remain in artifact JSON
            
            # 3. Serialize artifact to JSON
            artifact_json = json.dumps(artifact_json_data, indent=2, default=str)
            artifact_bytes = artifact_json.encode('utf-8')
            
            # 4. Store in GCS
            artifact_path = f"artifacts/{artifact_type}/{tenant_id}/{artifact_id}.json"
            upload_result = await self.gcs.upload_file(
                blob_name=artifact_path,
                file_data=artifact_bytes,
                content_type="application/json",
                metadata={
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type,
                    "tenant_id": tenant_id
                }
            )
            
            if not upload_result:
                self.logger.error(f"Failed to upload artifact to GCS: {artifact_path}")
                return {"success": False, "error": "GCS upload failed"}
            
            # 5. Store metadata in Supabase (using project_files table with artifact_type)
            # Convert IDs to UUID format for Supabase schema requirements
            # Extract UUID from artifact_id (remove "event_" prefix if present)
            artifact_uuid = artifact_id
            if artifact_id.startswith("event_"):
                artifact_uuid = artifact_id.replace("event_", "", 1)
            # Validate it's a valid UUID
            try:
                artifact_uuid = str(uuid_lib.UUID(artifact_uuid))
            except ValueError:
                # If not valid UUID, generate deterministic UUID from artifact_id
                artifact_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, artifact_id))
            
            # Convert tenant_id to UUID
            tenant_id_uuid = tenant_id
            if isinstance(tenant_id, str):
                try:
                    tenant_id_uuid = str(uuid_lib.UUID(tenant_id))
                except ValueError:
                    # Generate deterministic UUID from tenant_id string
                    tenant_id_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, tenant_id))
            
            # Convert user_id to UUID if provided
            user_id_uuid = None
            user_id_raw = metadata.get("user_id") if metadata else None
            if user_id_raw:
                if isinstance(user_id_raw, str):
                    try:
                        user_id_uuid = str(uuid_lib.UUID(user_id_raw))
                    except ValueError:
                        # Generate deterministic UUID from user_id string
                        user_id_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, user_id_raw))
                else:
                    user_id_uuid = str(user_id_raw)

            else:
                # Default to system user UUID (deterministic, consistent)
                user_id_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, "system"))
            
            artifact_metadata = {
                "uuid": artifact_uuid,
                "user_id": user_id_uuid,
                "tenant_id": tenant_id_uuid,
                "ui_name": metadata.get("ui_name") or f"{artifact_type}_{artifact_id}",
                "file_path": artifact_path,
                "artifact_type": artifact_type,  # NEW field - distinguishes artifacts from files
                "file_type": "structured",  # Artifacts are structured JSON; use artifact_type to distinguish  # Distinguish from regular files
                "mime_type": "application/json",
                "file_size": len(artifact_bytes),
                "status": metadata.get("status", "active"),
                "created_at": self.clock.now_iso(),
                "updated_at": self.clock.now_iso(),
                "deleted": False,
                # Store artifact-specific metadata in metadata JSONB field
                "metadata": {
                    "execution_id": metadata.get("execution_id"),
                    "session_id": metadata.get("session_id"),
                    "component_count": len(artifact_data.get("components", {})),
                    "has_visuals": len(visuals) > 0,
                    "visual_paths": list(visuals.keys()) if visuals else []
                }
            }
            
            try:
                await self.supabase.create_file(artifact_metadata)
                self.logger.info(f"Artifact metadata created in Supabase: {artifact_id}")
            except Exception as meta_error:
                self.logger.warning(f"Artifact stored in GCS but metadata creation failed: {meta_error}")
                # Continue - artifact is stored, metadata can be fixed later
            
            self.logger.info(f"Artifact stored successfully: {artifact_path} ({len(artifact_bytes)} bytes)")
            return {
                "success": True,
                "artifact_id": artifact_id,
                "storage_path": artifact_path,
                "visual_paths": visuals
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store artifact {artifact_type}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def get_artifact(
        self,
        artifact_id: str,
        tenant_id: str,
        include_visuals: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve artifact from GCS.
        
        For composite artifacts, retrieves all components.
        For artifacts with visuals, retrieves visual references (or full images if include_visuals=True).
        
        Args:
            artifact_id: Artifact ID
            tenant_id: Tenant ID (for security)
            include_visuals: If True, retrieve full visual images (base64). If False, only references.
        
        Returns:
            Optional[Dict]: Artifact data or None if not found
        """
        try:
            # 1. Get metadata from Supabase
            # Extract UUID from artifact_id (remove "event_" prefix if present)
            artifact_uuid_for_lookup = artifact_id
            if artifact_id.startswith("event_"):
                artifact_uuid_for_lookup = artifact_id.replace("event_", "", 1)
            # Validate it's a valid UUID
            try:
                artifact_uuid_for_lookup = str(uuid_lib.UUID(artifact_uuid_for_lookup))
            except ValueError:
                # If not valid UUID, generate deterministic UUID from artifact_id
                artifact_uuid_for_lookup = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, artifact_id))
            
            artifact_metadata = await self.supabase.get_file(artifact_uuid_for_lookup)
            
            if not artifact_metadata:
                self.logger.warning(f"Artifact metadata not found in Supabase: {artifact_id}, trying GCS fallback")
                # Fallback: Try to retrieve directly from GCS using common artifact type patterns
                # Artifacts are stored at: artifacts/{artifact_type}/{tenant_id}/{artifact_id}.json
                common_artifact_types = ["workflow", "solution", "blueprint", "sop", "roadmap", "poc", "visual"]
                
                for artifact_type in common_artifact_types:
                    storage_path = f"artifacts/{artifact_type}/{tenant_id}/{artifact_id}.json"
                    artifact_bytes = await self.gcs.download_file(storage_path)
                    if artifact_bytes:
                        self.logger.info(f"Retrieved artifact {artifact_id} from GCS fallback (path: {storage_path})")
                        artifact = json.loads(artifact_bytes.decode('utf-8'))
                        return artifact
                
                self.logger.warning(f"Artifact not found in GCS fallback: {artifact_id}")
                return None
            
            # Verify tenant_id matches
            # Convert tenant_id to UUID for comparison (stored as UUID in Supabase)
            tenant_id_for_comparison = tenant_id
            if isinstance(tenant_id, str):
                try:
                    tenant_id_for_comparison = str(uuid_lib.UUID(tenant_id))
                except ValueError:
                    tenant_id_for_comparison = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, tenant_id))
            
            if artifact_metadata.get("tenant_id") != tenant_id_for_comparison:
                self.logger.warning(f"Artifact {artifact_id} does not belong to tenant {tenant_id}")
                return None
            
            # Verify it's an artifact (not a regular file)
            if not artifact_metadata.get("artifact_type"):  # Check artifact_type instead of file_type
                self.logger.warning(f"Record {artifact_id} is not an artifact (artifact_type: {artifact_metadata.get('file_type')})")
                return None
            
            # 2. Get artifact from GCS
            storage_path = artifact_metadata.get("file_path")
            if not storage_path:
                self.logger.warning(f"Artifact {artifact_id} has no storage_path")
                return None
            
            artifact_bytes = await self.gcs.download_file(storage_path)
            if not artifact_bytes:
                self.logger.warning(f"Artifact not found in GCS: {storage_path}")
                return None
            
            # 3. Deserialize artifact
            artifact = json.loads(artifact_bytes.decode('utf-8'))
            
            # 4. Retrieve visuals if requested
            if include_visuals:
                metadata_obj = artifact_metadata.get("metadata", {})
                visual_paths = metadata_obj.get("visual_paths", [])
                
                # Handle structured artifacts (with renderings)
                if "renderings" in artifact:
                    renderings = artifact["renderings"]
                    for visual_key in visual_paths:
                        if visual_key in renderings and isinstance(renderings[visual_key], dict):
                            visual_ref = renderings[visual_key]
                            if "storage_path" in visual_ref:
                                visual_bytes = await self.gcs.download_file(visual_ref["storage_path"])
                                if visual_bytes:
                                    visual_base64 = base64.b64encode(visual_bytes).decode()
                                    renderings[visual_key]["image_base64"] = visual_base64
                                    self.logger.debug(f"Retrieved visual {visual_key} for artifact {artifact_id}")
                else:
                    # Handle legacy format (visuals at top level)
                    for visual_key in visual_paths:
                        if visual_key in artifact and isinstance(artifact[visual_key], dict):
                            visual_ref = artifact[visual_key]
                            if "storage_path" in visual_ref:
                                visual_bytes = await self.gcs.download_file(visual_ref["storage_path"])
                                if visual_bytes:
                                    visual_base64 = base64.b64encode(visual_bytes).decode()
                                    artifact[visual_key]["image_base64"] = visual_base64
                                    self.logger.debug(f"Retrieved visual {visual_key} for artifact {artifact_id}")
            
            self.logger.info(f"Artifact retrieved successfully: {artifact_id}")
            return artifact
            
        except Exception as e:
            self.logger.error(f"Failed to get artifact {artifact_id}: {e}", exc_info=True)
            return None
    
    
    async def get_visual(
        self,
        visual_path: str,
        tenant_id: str
    ) -> Optional[bytes]:
        """
        Retrieve visual image from GCS by storage path.
        
        Args:
            visual_path: GCS storage path of the visual (e.g., "artifacts/workflow/tenant_123/artifact_456/workflow_visual.png")
            tenant_id: Tenant ID (for security validation)
        
        Returns:
            Optional[bytes]: Visual image bytes (PNG format) or None if not found
        """
        try:
            # Validate tenant_id is in path (security check)
            if tenant_id not in visual_path:
                self.logger.warning(f"Visual path {visual_path} does not match tenant {tenant_id}")
                return None
            
            # Download visual from GCS
            visual_bytes = await self.gcs.download_file(visual_path)
            
            if visual_bytes:
                self.logger.info(f"Visual retrieved successfully: {visual_path}")
                return visual_bytes
            else:
                self.logger.warning(f"Visual not found in GCS: {visual_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get visual {visual_path}: {e}", exc_info=True)
            return None
    
    async def get_visual_base64(
        self,
        visual_path: str,
        tenant_id: str
    ) -> Optional[str]:
        """
        Retrieve visual image from GCS and return as base64 string.
        
        Args:
            visual_path: GCS storage path of the visual
            tenant_id: Tenant ID (for security validation)
        
        Returns:
            Optional[str]: Base64-encoded image string or None if not found
        """
        visual_bytes = await self.get_visual(visual_path, tenant_id)
        if visual_bytes:
            return base64.b64encode(visual_bytes).decode()
        return None

    async def list_artifacts(
        self,
        artifact_type: str,
        tenant_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List artifacts by type and tenant."""
        try:
            # Query Supabase for artifacts
            # Note: SupabaseFileAdapter.list_files requires user_id, but we want to list by tenant
            # We'll query directly using the Supabase client for artifact queries
            
            # Build query for artifacts
            # Access the Supabase client through the adapter
            client = self.supabase.client if hasattr(self.supabase, 'client') else self.supabase._client
            query = client.table("project_files").select("*").eq("tenant_id", tenant_id).eq("deleted", False)
            
            # Filter by artifact_type and file_type
            query = query.eq("artifact_type", artifact_type)
            query = query.is_("artifact_type", "not.null")  # Artifacts have artifact_type set
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.range(offset, offset + (limit or 10) - 1)
            
            result = query.order("created_at", desc=True).execute()
            artifacts = result.data if result.data else []
            
            self.logger.info(f"Listed {len(artifacts)} artifacts of type {artifact_type} for tenant {tenant_id}")
            return artifacts
            
        except Exception as e:
            self.logger.error(f"Failed to list artifacts {artifact_type}: {e}", exc_info=True)
            return []
    
    async def delete_artifact(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> bool:
        """Delete artifact from GCS and metadata from Supabase."""
        try:
            # 1. Get metadata
            # Extract UUID from artifact_id (remove "event_" prefix if present)
            artifact_uuid_for_lookup = artifact_id
            if artifact_id.startswith("event_"):
                artifact_uuid_for_lookup = artifact_id.replace("event_", "", 1)
            # Validate it's a valid UUID
            try:
                artifact_uuid_for_lookup = str(uuid_lib.UUID(artifact_uuid_for_lookup))
            except ValueError:
                # If not valid UUID, generate deterministic UUID from artifact_id
                artifact_uuid_for_lookup = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, artifact_id))
            
            # 1. Get metadata from Supabase
            artifact_metadata = await self.supabase.get_file(artifact_uuid_for_lookup)
            if not artifact_metadata:
                self.logger.warning(f"Artifact metadata not found: {artifact_id}")
                return False
            
            # Verify tenant_id
            if artifact_metadata.get("tenant_id") != tenant_id_for_comparison:
                self.logger.warning(f"Artifact {artifact_id} does not belong to tenant {tenant_id}")
                return False
            
            # 2. Delete from GCS
            storage_path = artifact_metadata.get("file_path")
            if storage_path:
                delete_result = await self.gcs.delete_file(storage_path)
                if not delete_result:
                    self.logger.warning(f"Failed to delete artifact from GCS: {storage_path}")
            
            # 3. Delete visuals if any
            # Visual paths are stored in artifact JSON, so we'd need to retrieve artifact first
            # For now, we'll rely on GCS lifecycle policies or manual cleanup
            # TODO: Implement visual deletion if needed
            
            # 4. Soft delete in Supabase
            try:
                await self.supabase.update_file(artifact_id, {"deleted": True})
            except Exception as e:
                self.logger.warning(f"Failed to soft delete artifact metadata: {e}")
            
            self.logger.info(f"Artifact deleted: {artifact_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete artifact {artifact_id}: {e}", exc_info=True)
            return False
    
    async def store_composite_artifact(
        self,
        artifact_type: str,
        artifact_data: Dict[str, Any],
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store composite artifact with embedded components.
        
        This is the same as store_artifact but with explicit handling
        for multi-component artifacts (blueprints, roadmaps, etc.).
        Components are embedded in artifact_data JSON.
        """
        # For now, use same implementation as store_artifact
        # Components are embedded in artifact_data JSON
        # Large binary components (visuals) are stored separately
        return await self.store_artifact(artifact_type, artifact_data, tenant_id, metadata)
