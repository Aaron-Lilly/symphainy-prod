"""
Artifact Storage Protocol - Abstraction Contract (Layer 2)

Defines the interface for artifact storage operations.
Enables swappability between storage backends (GCS, S3, Azure Blob, etc.).

WHAT (Infrastructure Role): I define the contract for artifact storage operations
HOW (Infrastructure Implementation): I specify the interface for artifact storage
"""

from typing import Protocol, Optional, Dict, Any, List


class ArtifactStorageProtocol(Protocol):
    """Protocol for artifact storage operations."""
    
    async def store_artifact(
        self,
        artifact_type: str,
        artifact_data: Dict[str, Any],
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store artifact in storage and metadata in database.
        
        Args:
            artifact_type: Type of artifact ('workflow', 'sop', 'blueprint', 'solution', 'roadmap', 'poc', 'hybrid_embeddings')
            artifact_data: Artifact data (will be serialized to JSON)
            tenant_id: Tenant ID
            metadata: Optional metadata (execution_id, session_id, user_id, etc.)
        
        Returns:
            Dict with success status and artifact_id if successful:
            {"success": True, "artifact_id": "...", "storage_path": "...", "visual_paths": {...}}
            or {"success": False, "error": "..."}
        """
        ...
    
    async def get_artifact(
        self,
        artifact_id: str,
        tenant_id: str,
        include_visuals: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve artifact from storage.
        
        For composite artifacts, retrieves all components.
        For artifacts with visuals, retrieves visual references (or full images if requested).
        
        Args:
            artifact_id: Artifact ID
            tenant_id: Tenant ID (for security)
            include_visuals: If True, retrieve full visual images (base64). If False, only references.
        
        Returns:
            Optional[Dict]: Artifact data or None if not found
        """
        ...
    
    async def get_visual(
        self,
        visual_path: str,
        tenant_id: str
    ) -> Optional[bytes]:
        """
        Retrieve visual image from storage by storage path.
        
        Args:
            visual_path: Storage path of the visual
            tenant_id: Tenant ID (for security validation)
        
        Returns:
            Optional[bytes]: Visual image bytes (PNG format) or None if not found
        """
        ...
    
    async def get_visual_base64(
        self,
        visual_path: str,
        tenant_id: str
    ) -> Optional[str]:
        """
        Retrieve visual image from storage and return as base64 string.
        
        Args:
            visual_path: Storage path of the visual
            tenant_id: Tenant ID (for security validation)
        
        Returns:
            Optional[str]: Base64-encoded image string or None if not found
        """
        ...
    
    async def list_artifacts(
        self,
        artifact_type: str,
        tenant_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List artifacts by type and tenant.
        
        Args:
            artifact_type: Type of artifact to list
            tenant_id: Tenant ID
            limit: Optional result limit
            offset: Optional pagination offset
        
        Returns:
            List of artifact metadata dictionaries
        """
        ...
    
    async def delete_artifact(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> bool:
        """
        Delete artifact from storage and metadata from database.
        
        Args:
            artifact_id: Artifact ID
            tenant_id: Tenant ID (for security)
        
        Returns:
            bool: True if successful
        """
        ...
    
    async def store_composite_artifact(
        self,
        artifact_type: str,
        artifact_data: Dict[str, Any],
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store composite artifact with embedded components.
        
        Large binary components (visuals) are stored separately with references.
        All other components are embedded in the main artifact JSON.
        
        Args:
            artifact_type: Type of artifact
            artifact_data: Artifact data with embedded components
            tenant_id: Tenant ID
            metadata: Optional metadata
        
        Returns:
            Dict with success status, artifact_id, storage_path, and visual_paths:
            {"success": True, "artifact_id": "...", "storage_path": "...", "visual_paths": {...}}
        """
        ...
