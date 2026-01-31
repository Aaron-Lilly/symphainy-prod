"""
List Artifacts Service (Platform SDK)

Lists artifacts (files) for a tenant/session.

Uses ctx.platform for registry queries.

Contract: docs/intent_contracts/journey_content_file_management/intent_list_artifacts.md
"""

from typing import Dict, Any, Optional, List

from utilities import get_logger

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class ListArtifactsService(PlatformIntentService):
    """
    List Artifacts Service using Platform SDK.
    
    Handles the `list_artifacts` intent:
    - Lists artifacts for tenant/session with optional filtering
    - Supports pagination (limit, offset)
    - Returns structured artifact with file list
    """
    
    def __init__(self, service_id: str = "list_artifacts_service"):
        """Initialize List Artifacts Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute list_artifacts intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with artifacts containing file list
        """
        self.logger.info(f"Executing list_artifacts: {ctx.execution_id}")
        
        # Extract parameters with defaults
        tenant_id = ctx.intent.parameters.get("tenant_id", ctx.tenant_id)
        session_id = ctx.intent.parameters.get("session_id", ctx.session_id)
        file_type = ctx.intent.parameters.get("file_type")
        artifact_type = ctx.intent.parameters.get("artifact_type")
        limit = ctx.intent.parameters.get("limit", 100)
        offset = ctx.intent.parameters.get("offset", 0)
        
        # Get user_id from context for workspace-scoped filtering
        user_id = ctx.metadata.get("user_id")
        if not user_id:
            user_id = ctx.intent.metadata.get("user_id", "system")
        
        # List files via ctx.platform registry
        files = await self._list_files(
            ctx=ctx,
            tenant_id=tenant_id,
            session_id=session_id,
            file_type=file_type or artifact_type,
            limit=limit,
            offset=offset,
            user_id=user_id
        )
        
        # Transform to semantic payload
        file_list_semantic = []
        for file in files:
            file_semantic = {
                "artifact_id": file.get("uuid") or file.get("file_id"),
                "artifact_name": file.get("ui_name") or file.get("file_name"),
                "artifact_type": file.get("file_type"),
                "mime_type": file.get("mime_type") or file.get("content_type"),
                "file_size": file.get("file_size"),
                "content_fingerprint": file.get("file_hash"),
                "storage_location": file.get("gcs_blob_path") or file.get("file_path"),
                "created_at": file.get("created_at"),
                "updated_at": file.get("updated_at")
            }
            file_list_semantic.append(file_semantic)
        
        semantic_payload = {
            "artifacts": file_list_semantic,
            "count": len(files),
            "tenant_id": tenant_id,
            "session_id": session_id,
            "limit": limit,
            "offset": offset,
            "artifact_type_filter": file_type or artifact_type
        }
        
        self.logger.info(f"✅ Listed {len(files)} artifacts")
        
        return {
            "artifacts": {
                "artifact_list": {
                    "result_type": "artifact_list",
                    "semantic_payload": semantic_payload
                }
            },
            "events": []
        }
    
    async def _list_files(
        self,
        ctx: PlatformContext,
        tenant_id: str,
        session_id: str,
        file_type: Optional[str],
        limit: int,
        offset: int,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        List files from registry via ctx.platform.
        """
        # Access registry through ctx.platform
        registry = ctx.platform.registry
        if not registry:
            self.logger.warning("Registry not available, returning empty list")
            return []
        
        try:
            files = await registry.list_files(
                tenant_id=tenant_id,
                session_id=session_id,
                file_type=file_type,
                limit=limit,
                offset=offset,
                user_id=user_id
            )
            return files or []
        except Exception as e:
            self.logger.error(f"Failed to list files from registry: {e}")
            return []
