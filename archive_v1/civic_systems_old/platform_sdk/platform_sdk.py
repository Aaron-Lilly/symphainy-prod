"""
Platform SDK - Translation and Coordination Layer

Translates raw infrastructure data into runtime-ready objects.
Coordinates Smart City governance decisions with Runtime needs.
"""

import uuid
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
from utilities import get_logger, get_clock

from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext
from symphainy_platform.foundations.public_works.protocols.auth_protocol import AuthenticationProtocol, TenancyProtocol, AuthorizationProtocol
from symphainy_platform.foundations.public_works.protocols.file_management_protocol import FileManagementProtocol
from symphainy_platform.foundations.public_works.protocols.content_metadata_protocol import ContentMetadataProtocol
from symphainy_platform.foundations.public_works.protocols.knowledge_governance_protocol import KnowledgeGovernanceProtocol, PolicyType
from civic_systems.smart_city.registries.policy_registry import PolicyRegistry


class PlatformSDK:
    """
    Platform SDK - Boundary Zone for Translation and Coordination.
    
    This SDK:
    - Translates raw infrastructure data (from abstractions) into runtime-ready objects (SecurityContext, etc.)
    - Coordinates Smart City governance decisions with Runtime needs
    - Houses business logic translation from old abstractions/services
    """
    
    def __init__(
        self,
        auth_abstraction: Optional[AuthenticationProtocol] = None,
        tenant_abstraction: Optional[TenancyProtocol] = None,
        authorization_abstraction: Optional[AuthorizationProtocol] = None,
        file_management_abstraction: Optional[FileManagementProtocol] = None,
        policy_registry: Optional[PolicyRegistry] = None
    ):
        """
        Initialize Platform SDK.
        
        Args:
            auth_abstraction: Authentication abstraction (for raw auth data)
            tenant_abstraction: Tenancy abstraction (for raw tenant data)
            authorization_abstraction: Authorization abstraction (for raw permission data)
            file_management_abstraction: File Management abstraction (for raw file data)
            policy_registry: Policy Registry (for policy rules)
        """
        self.auth_abstraction = auth_abstraction
        self.tenant_abstraction = tenant_abstraction
        self.authorization_abstraction = authorization_abstraction
        self.file_management_abstraction = file_management_abstraction
        self.content_metadata_abstraction = None  # Will be set if needed
        self.knowledge_governance_abstraction = None  # Will be set if needed
        self.policy_registry = policy_registry
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("Platform SDK initialized")
    
    async def resolve_security_context(
        self,
        raw_auth_data: Dict[str, Any]
    ) -> Optional[SecurityContext]:
        """
        Translate raw authentication data into SecurityContext.
        
        This is translation logic (not policy logic).
        Policy logic (what is allowed) is in Smart City roles.
        This logic (how to create SecurityContext) is in SDK.
        
        Args:
            raw_auth_data: Raw authentication data from AuthAbstraction
        
        Returns:
            Optional[SecurityContext]: SecurityContext or None if invalid
        """
        if not raw_auth_data or not raw_auth_data.get("success"):
            return None
        
        user_id = raw_auth_data.get("user_id")
        email = raw_auth_data.get("email", "")
        access_token = raw_auth_data.get("access_token")
        
        # Resolve tenant (translation logic - was in AuthAbstraction)
        tenant_id = await self._resolve_tenant_from_auth_data(raw_auth_data)
        
        # Resolve roles/permissions (translation logic - was in AuthAbstraction)
        roles, permissions = await self._resolve_roles_permissions_from_auth_data(
            raw_auth_data,
            tenant_id
        )
        
        # Create SecurityContext (translation logic - was in AuthAbstraction)
        return SecurityContext(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            roles=roles,
            permissions=permissions,
            origin="platform_sdk"
        )
    
    async def _resolve_tenant_from_auth_data(
        self,
        raw_auth_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Resolve tenant ID from raw auth data.
        
        Translation logic - was in AuthAbstraction.
        """
        # Try tenant info from database first (via tenant_abstraction if available)
        user_id = raw_auth_data.get("user_id")
        if user_id and self.tenant_abstraction:
            try:
                tenant_info = await self.tenant_abstraction.get_user_tenant_info(user_id)
                if tenant_info and tenant_info.get("tenant_id"):
                    return tenant_info.get("tenant_id")
            except Exception as e:
                self.logger.warning(f"Failed to get tenant info from abstraction: {e}")
        
        # Fallback to user metadata
        raw_user_metadata = raw_auth_data.get("raw_user_metadata", {})
        tenant_id = raw_user_metadata.get("tenant_id")
        
        if tenant_id:
            return tenant_id
        
        # Fallback to raw user data
        raw_user_data = raw_auth_data.get("raw_user_data", {})
        tenant_id = raw_user_data.get("tenant_id") or raw_user_data.get("user_metadata", {}).get("tenant_id")
        
        return tenant_id
    
    async def _resolve_roles_permissions_from_auth_data(
        self,
        raw_auth_data: Dict[str, Any],
        tenant_id: Optional[str]
    ) -> tuple[List[str], List[str]]:
        """
        Resolve roles and permissions from raw auth data.
        
        Translation logic - was in AuthAbstraction.
        """
        # Try tenant info from database first (via tenant_abstraction if available)
        user_id = raw_auth_data.get("user_id")
        if user_id and tenant_id and self.tenant_abstraction:
            try:
                # Check if tenant_abstraction has get_user_tenant_info method
                if hasattr(self.tenant_abstraction, 'get_user_tenant_info'):
                    tenant_info = await self.tenant_abstraction.get_user_tenant_info(user_id)
                    if tenant_info and tenant_info.get("tenant_id") == tenant_id:
                        roles = tenant_info.get("roles", [])
                        permissions = tenant_info.get("permissions", [])
                        if roles or permissions:
                            return (
                                roles if isinstance(roles, list) else [roles] if roles else [],
                                permissions if isinstance(permissions, list) else [permissions] if permissions else []
                            )
            except Exception as e:
                self.logger.warning(f"Failed to get tenant info for roles/permissions: {e}")
        
        # Fallback to user metadata
        raw_user_metadata = raw_auth_data.get("raw_user_metadata", {})
        roles = raw_user_metadata.get("roles", [])
        permissions = raw_user_metadata.get("permissions", [])
        
        if roles or permissions:
            return (
                roles if isinstance(roles, list) else [roles] if roles else [],
                permissions if isinstance(permissions, list) else [permissions] if permissions else []
            )
        
        # Fallback to raw user data
        raw_user_data = raw_auth_data.get("raw_user_data", {})
        roles = raw_user_data.get("roles", [])
        permissions = raw_user_data.get("permissions", [])
        
        return (
            roles if isinstance(roles, list) else [roles] if roles else [],
            permissions if isinstance(permissions, list) else [permissions] if permissions else []
        )
    
    async def authenticate_and_resolve_context(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[SecurityContext]:
        """
        Authenticate user and resolve SecurityContext.
        
        This is a convenience method that:
        1. Calls AuthAbstraction.authenticate() (gets raw data)
        2. Translates raw data to SecurityContext (via resolve_security_context)
        
        Args:
            credentials: Authentication credentials
        
        Returns:
            Optional[SecurityContext]: SecurityContext or None if failed
        """
        if not self.auth_abstraction:
            self.logger.error("Auth abstraction not available")
            return None
        
        # Get raw auth data from abstraction
        raw_auth_data = await self.auth_abstraction.authenticate(credentials)
        
        if not raw_auth_data:
            return None
        
        # Translate to SecurityContext
        return await self.resolve_security_context(raw_auth_data)
    
    async def validate_token_and_resolve_context(
        self,
        token: str
    ) -> Optional[SecurityContext]:
        """
        Validate token and resolve SecurityContext.
        
        Args:
            token: Authentication token
        
        Returns:
            Optional[SecurityContext]: SecurityContext or None if invalid
        """
        if not self.auth_abstraction:
            self.logger.error("Auth abstraction not available")
            return None
        
        # Get raw validation data from abstraction
        raw_auth_data = await self.auth_abstraction.validate_token(token)
        
        if not raw_auth_data:
            return None
        
        # Translate to SecurityContext
        return await self.resolve_security_context(raw_auth_data)
    
    # ============================================================================
    # Security Guard Methods (Boundary Zone for Realms)
    # ============================================================================
    
    async def ensure_user_can(
        self,
        action: str,
        tenant_id: str,
        user_id: str,
        resource: Optional[str] = None,
        security_context: Optional[SecurityContext] = None
    ) -> Dict[str, Any]:
        """
        Ensure user can perform action (Security Guard boundary method).
        
        This is the boundary zone for Realms - translates Realm intent → runtime contract shape.
        - Queries Policy Registry for policy rules
        - Gets user context (via abstractions)
        - Prepares runtime contract shape
        - Does NOT call primitives directly (that's Runtime's job)
        
        Args:
            action: Action being performed (e.g., "content.parse")
            tenant_id: Tenant ID
            user_id: User ID
            resource: Optional resource identifier
            security_context: Optional security context (if already resolved)
        
        Returns:
            Dict[str, Any]: Runtime contract shape (ready for Runtime)
            Structure:
            {
                "action": str,
                "resource": Optional[str],
                "user_id": str,
                "tenant_id": str,
                "security_context": SecurityContext,
                "policy_rules": Dict[str, Any],
                "ready_for_runtime": bool
            }
        """
        try:
            # Get security context if not provided
            if not security_context:
                # TODO: Resolve security context from user_id
                # For now, create minimal context
                security_context = SecurityContext(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    origin="platform_sdk"
                )
            
            # Query Policy Registry for policy rules
            policy_rules = {}
            if self.policy_registry:
                policy_rules = await self.policy_registry.get_policy_rules(
                    action=action,
                    tenant_id=tenant_id,
                    resource=resource
                )
            
            # Prepare runtime contract shape
            return {
                "action": action,
                "resource": resource,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "security_context": security_context,
                "policy_rules": policy_rules,
                "ready_for_runtime": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to ensure user can perform action: {e}", exc_info=True)
            return {
                "action": action,
                "resource": resource,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "security_context": security_context,
                "policy_rules": {},
                "ready_for_runtime": False,
                "error": str(e)
            }
    
    async def validate_tenant_access(
        self,
        tenant_id: str,
        user_id: str,
        resource_tenant_id: Optional[str] = None,
        security_context: Optional[SecurityContext] = None
    ) -> Dict[str, Any]:
        """
        Validate tenant access (Security Guard boundary method).
        
        This is the boundary zone for Realms - translates Realm intent → runtime contract shape.
        - Queries Policy Registry for tenant isolation rules
        - Gets tenant info (via abstractions)
        - Prepares runtime contract shape
        - Does NOT call primitives directly (that's Runtime's job)
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            resource_tenant_id: Optional resource tenant ID
            security_context: Optional security context (if already resolved)
        
        Returns:
            Dict[str, Any]: Runtime contract shape (ready for Runtime)
            Structure:
            {
                "tenant_id": str,
                "user_id": str,
                "resource_tenant_id": Optional[str],
                "isolation_rules": Dict[str, Any],
                "tenant_info": Dict[str, Any],
                "ready_for_runtime": bool
            }
        """
        try:
            # Get security context if not provided
            if not security_context:
                # TODO: Resolve security context from user_id
                # For now, create minimal context
                security_context = SecurityContext(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    origin="platform_sdk"
                )
            
            # Query Policy Registry for tenant isolation rules
            isolation_rules = {}
            if self.policy_registry:
                isolation_rules = await self.policy_registry.get_tenant_isolation_rules(
                    tenant_id=tenant_id
                )
            
            # Get tenant info (raw data from abstraction)
            tenant_info = {}
            if self.tenant_abstraction:
                tenant_info_raw = await self.tenant_abstraction.get_tenant(tenant_id)
                if tenant_info_raw:
                    tenant_info = tenant_info_raw
            
            # Prepare runtime contract shape
            return {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "resource_tenant_id": resource_tenant_id,
                "security_context": security_context,
                "isolation_rules": isolation_rules,
                "tenant_info": tenant_info,
                "ready_for_runtime": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate tenant access: {e}", exc_info=True)
            return {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "resource_tenant_id": resource_tenant_id,
                "security_context": security_context,
                "isolation_rules": {},
                "tenant_info": {},
                "ready_for_runtime": False,
                "error": str(e)
            }
    
    # ============================================================================
    # Data Steward Methods (Boundary Zone for Realms)
    # ============================================================================
    
    async def resolve_file_metadata(
        self,
        raw_file_data: Dict[str, Any],
        raw_gcs_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Translate raw file data from GCS + Supabase into FileMetadata business object.
        
        This is the harvested business logic from FileManagementAbstraction:
        - UUID generation (if not provided)
        - File hash calculation
        - Content type inference
        - Metadata enhancement (timestamps, status, etc.)
        
        Args:
            raw_file_data: Raw file data dict (from Supabase adapter)
            raw_gcs_result: Optional raw GCS upload result
        
        Returns:
            Dict with enhanced file metadata (business object)
        """
        if not raw_file_data:
            return {}
        
        # Generate UUID if not present (harvested from FileManagementAbstraction)
        file_uuid = raw_file_data.get("uuid")
        if not file_uuid:
            file_uuid = str(uuid.uuid4())
            raw_file_data["uuid"] = file_uuid
        
        # Calculate file hash if file_content is present (harvested from FileStorageAbstraction)
        file_content = raw_file_data.get("file_content")
        if file_content and not raw_file_data.get("file_hash"):
            if isinstance(file_content, str):
                file_content_bytes = file_content.encode('utf-8')
            else:
                file_content_bytes = file_content
            raw_file_data["file_hash"] = hashlib.sha256(file_content_bytes).hexdigest()
            raw_file_data["file_size"] = len(file_content_bytes)
        
        # Infer content type if not present (harvested from FileStorageAbstraction)
        if not raw_file_data.get("mime_type") and not raw_file_data.get("content_type"):
            file_type = raw_file_data.get("file_type", "")
            if file_type:
                # Simple extension to MIME type mapping (harvested business logic)
                mime_map = {
                    "txt": "text/plain",
                    "pdf": "application/pdf",
                    "html": "text/html",
                    "json": "application/json",
                    "xml": "application/xml",
                    "csv": "text/csv",
                    "bin": "application/octet-stream",
                    "cpy": "text/plain",  # COBOL copybook
                    "parquet": "application/parquet"
                }
                content_type = mime_map.get(file_type.lower(), "application/octet-stream")
                raw_file_data["mime_type"] = content_type
                raw_file_data["content_type"] = content_type
        
        # Add business metadata (harvested from FileManagementAbstraction)
        if "created_at" not in raw_file_data:
            raw_file_data["created_at"] = self.clock.now_iso()
        if "updated_at" not in raw_file_data:
            raw_file_data["updated_at"] = self.clock.now_iso()
        if "status" not in raw_file_data:
            raw_file_data["status"] = "uploaded"
        if "deleted" not in raw_file_data:
            raw_file_data["deleted"] = False
        if "pillar_origin" not in raw_file_data:
            raw_file_data["pillar_origin"] = "content_pillar"
        if "upload_source" not in raw_file_data:
            raw_file_data["upload_source"] = "api"
        
        return raw_file_data
    
    async def resolve_content_metadata(
        self,
        raw_content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Translate raw content metadata from ArangoDB into ContentMetadata business object.
        
        This is the harvested business logic from ContentMetadataAbstraction:
        - Content ID generation (if not provided)
        - Metadata enhancement (timestamps, status, version, etc.)
        
        Args:
            raw_content_data: Raw content metadata dict (from ArangoDB adapter)
        
        Returns:
            Dict with enhanced content metadata (business object)
        """
        if not raw_content_data:
            return {}
        
        # Generate content ID if not present (harvested from ContentMetadataAbstraction)
        content_id = raw_content_data.get("content_id")
        if not content_id:
            content_id = str(uuid.uuid4())
            raw_content_data["content_id"] = content_id
        
        # Add business metadata (harvested from ContentMetadataAbstraction)
        if "created_at" not in raw_content_data:
            raw_content_data["created_at"] = self.clock.now_iso()
        if "updated_at" not in raw_content_data:
            raw_content_data["updated_at"] = self.clock.now_iso()
        if "status" not in raw_content_data:
            raw_content_data["status"] = "active"
        if "version" not in raw_content_data:
            raw_content_data["version"] = 1
        if "analysis_status" not in raw_content_data:
            raw_content_data["analysis_status"] = "pending"
        
        return raw_content_data
    
    async def check_content_relationships_before_deletion(
        self,
        content_id: str
    ) -> Dict[str, Any]:
        """
        Check content relationships before deletion (governance rule).
        
        This is the harvested business logic from ContentMetadataAbstraction.delete_content_metadata.
        Business rule: Cannot delete content metadata with relationships.
        
        Args:
            content_id: Content ID to check
        
        Returns:
            Dict with:
            {
                "can_delete": bool,
                "relationships": List[Dict[str, Any]],
                "reason": str
            }
        """
        if not self.content_metadata_abstraction:
            self.logger.warning("Content metadata abstraction not available, allowing deletion")
            return {
                "can_delete": True,
                "relationships": [],
                "reason": "Content metadata abstraction not available"
            }
        
        try:
            # Get relationships (harvested business logic)
            relationships = await self.content_metadata_abstraction.get_content_relationships(
                content_id,
                direction="both"
            )
            
            if relationships:
                return {
                    "can_delete": False,
                    "relationships": relationships,
                    "reason": f"Content metadata has {len(relationships)} relationships"
                }
            else:
                return {
                    "can_delete": True,
                    "relationships": [],
                    "reason": "No relationships found"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to check content relationships: {e}", exc_info=True)
            # On error, allow deletion (fail open for now)
            return {
                "can_delete": True,
                "relationships": [],
                "reason": f"Error checking relationships: {str(e)}"
            }
    
    async def resolve_lineage(
        self,
        raw_lineage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Translate raw lineage data from ArangoDB into LineageGraph business object.
        
        This is the harvested business logic from StateManagementAbstraction (for lineage).
        Lineage graph construction is in Data Steward service layer (not abstraction), so this
        just enhances the raw lineage data with business metadata.
        
        Args:
            raw_lineage_data: Raw lineage data dict (from State Management Abstraction)
        
        Returns:
            Dict with enhanced lineage data (business object)
        """
        if not raw_lineage_data:
            return {}
        
        # Generate lineage ID if not present
        lineage_id = raw_lineage_data.get("lineage_id")
        if not lineage_id:
            lineage_id = str(uuid.uuid4())
            raw_lineage_data["lineage_id"] = lineage_id
        
        # Add business metadata
        if "created_at" not in raw_lineage_data:
            raw_lineage_data["created_at"] = self.clock.now_iso()
        if "status" not in raw_lineage_data:
            raw_lineage_data["status"] = "active"
        
        return raw_lineage_data
    
    async def ensure_data_access(
        self,
        action: str,
        user_id: str,
        tenant_id: str,
        resource: str,
        security_context: Optional[SecurityContext] = None
    ) -> Dict[str, Any]:
        """
        Ensure user can access data (Data Steward boundary method).
        
        This is the boundary zone for Realms - translates Realm intent → runtime contract shape.
        - Queries Policy Registry for data access policies
        - Gets user context (via abstractions)
        - Prepares runtime contract shape
        - Does NOT call primitives directly (that's Runtime's job)
        
        Args:
            action: Action being performed (e.g., "file.read", "content.write")
            user_id: User ID
            tenant_id: Tenant ID
            resource: Resource identifier (e.g., file_uuid, content_id)
            security_context: Optional SecurityContext (if already resolved)
        
        Returns:
            Dict with runtime contract shape ready for Runtime → Data Steward Primitive
        """
        try:
            if not self.policy_registry:
                self.logger.warning("Policy Registry not available, using default policy")
                policy_rules = {}
            else:
                # Query Policy Registry for data access policies
                policy_rules = await self.policy_registry.get_policy_rules(
                    action=action,
                    resource=resource,
                    tenant_id=tenant_id
                )
            
            # Prepare runtime contract shape
            return {
                "action": action,
                "resource": resource,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "security_context": security_context.to_dict() if security_context else None,
                "policy_rules": policy_rules,
                "ready_for_runtime": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to ensure data access: {e}", exc_info=True)
            return {
                "action": action,
                "resource": resource,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "security_context": security_context.to_dict() if security_context else None,
                "policy_rules": {},
                "ready_for_runtime": False,
                "error": str(e)
            }

    # ============================================================================
    # Librarian Methods (Translation Logic)
    # ============================================================================
    
    async def ensure_search_access(
        self,
        action: str,
        user_id: str,
        tenant_id: str,
        query: Optional[str] = None,
        security_context: Optional[SecurityContext] = None
    ) -> Dict[str, Any]:
        """
        Ensure user can perform search operations (Librarian boundary method).
        
        Translates Realm intent → runtime contract shape for Librarian Primitive.
        - Queries Policy Registry for search access policies
        - Prepares runtime contract shape
        
        Args:
            action: Action being performed (e.g., "search_knowledge", "semantic_search")
            user_id: User ID
            tenant_id: Tenant ID
            query: Optional search query (for query-based restrictions)
            security_context: Optional SecurityContext (if already resolved)
        
        Returns:
            Dict with runtime contract shape ready for Runtime → Librarian Primitive
        """
        try:
            if not security_context:
                # Resolve security context if not provided
                # This would typically come from a previous auth call
                security_context = SecurityContext(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    origin="platform_sdk_search_access"
                )
            
            # Retrieve policy rules from Policy Registry
            policy_rules = {}
            if self.policy_registry:
                policy_rules = await self.policy_registry.get_policy_rules(
                    action=action,
                    resource="search",
                    tenant_id=tenant_id
                )
            
            return {
                "action": action,
                "resource": "search",
                "user_id": user_id,
                "tenant_id": tenant_id,
                "query": query,
                "security_context": security_context,
                "policy_rules": policy_rules,
                "ready_for_runtime": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to ensure search access: {e}", exc_info=True)
            return {
                "action": action,
                "resource": "search",
                "user_id": user_id,
                "tenant_id": tenant_id,
                "query": query,
                "security_context": security_context.to_dict() if security_context else None,
                "policy_rules": {},
                "ready_for_runtime": False,
                "error": str(e)
            }
    
    async def ensure_knowledge_access(
        self,
        action: str,
        user_id: str,
        tenant_id: str,
        resource: Optional[str] = None,
        security_context: Optional[SecurityContext] = None
    ) -> Dict[str, Any]:
        """
        Ensure user can access knowledge assets (Librarian boundary method).
        
        Translates Realm intent → runtime contract shape for Librarian Primitive.
        - Queries Policy Registry for knowledge access policies
        - Prepares runtime contract shape
        
        Args:
            action: Action being performed (e.g., "read_embeddings", "read_semantic_graph")
            user_id: User ID
            tenant_id: Tenant ID
            resource: Optional resource identifier (e.g., content_id, file_id)
            security_context: Optional SecurityContext (if already resolved)
        
        Returns:
            Dict with runtime contract shape ready for Runtime → Librarian Primitive
        """
        try:
            if not security_context:
                security_context = SecurityContext(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    origin="platform_sdk_knowledge_access"
                )
            
            # Retrieve policy rules from Policy Registry
            policy_rules = {}
            if self.policy_registry:
                policy_rules = await self.policy_registry.get_policy_rules(
                    action=action,
                    resource=resource,
                    tenant_id=tenant_id
                )
            
            return {
                "action": action,
                "resource": resource,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "security_context": security_context,
                "policy_rules": policy_rules,
                "ready_for_runtime": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to ensure knowledge access: {e}", exc_info=True)
            return {
                "action": action,
                "resource": resource,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "security_context": security_context.to_dict() if security_context else None,
                "policy_rules": {},
                "ready_for_runtime": False,
                "error": str(e)
            }
    
    async def apply_tenant_filter(
        self,
        filter_conditions: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Apply tenant filtering to search/query filters (translation logic).
        
        This is translation logic - adds tenant_id to filter conditions.
        Harvested from SemanticDataAbstraction and KnowledgeDiscoveryAbstraction.
        
        Args:
            filter_conditions: Existing filter conditions
            tenant_id: Tenant ID to add
        
        Returns:
            Filter conditions with tenant_id added
        """
        return {
            **filter_conditions,
            "tenant_id": tenant_id
        }
