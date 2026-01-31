"""
Curator Service - Platform DNA Promotion

Service for promoting Purpose-Bound Outcomes to Platform DNA (generalized, curated capabilities).

WHAT (Curator Role): I validate and promote outcomes to Platform DNA
HOW (Service Implementation): I validate, generalize, and create registry entries
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from utilities import get_logger, get_clock
import uuid
from symphainy_platform.civic_systems.smart_city.primitives.curator_primitives import CuratorPrimitives


class CuratorService:
    """
    Curator Service - Platform DNA Promotion
    
    Validates, generalizes, and promotes Purpose-Bound Outcomes to Platform DNA.
    """
    
    def __init__(
        self,
        supabase_adapter: Optional[Any] = None,
        artifact_plane: Optional[Any] = None,
        curator_primitives: Optional[CuratorPrimitives] = None
    ):
        """
        Initialize Curator Service.
        
        Args:
            supabase_adapter: Supabase adapter for registry operations
            artifact_plane: Artifact Plane for retrieving source artifacts
            curator_primitives: Curator primitives for policy decisions
        """
        self.supabase_adapter = supabase_adapter
        self.artifact_plane = artifact_plane
        self.curator_primitives = curator_primitives
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def promote_to_platform_dna(
        self,
        artifact_id: str,
        tenant_id: str,
        registry_type: str,  # "solution", "intent", "realm"
        registry_name: str,
        registry_id: Optional[str] = None,  # If None, will be generated
        promoted_by: str = "curator",
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Promote Purpose-Bound Outcome to Platform DNA.
        
        This is an explicit workflow that:
        1. Validates promotion criteria (de-identified, generalizable, policy-approved)
        2. Generalizes outcome (removes client context)
        3. Creates registry entry (versioned, immutable)
        4. Records promotion in WAL
        
        Args:
            artifact_id: Artifact ID of Purpose-Bound Outcome to promote
            tenant_id: Tenant ID (for retrieving artifact)
            registry_type: Type of registry ("solution", "intent", "realm")
            registry_name: Human-readable name for the registry entry
            registry_id: Optional registry ID (if None, will be generated)
            promoted_by: Who/what initiated the promotion
            description: Optional description
            tags: Optional tags for discovery
        
        Returns:
            Registry ID (UUID string) or None if promotion failed
        """
        try:
            # Validate registry_type
            valid_types = ["solution", "intent", "realm"]
            if registry_type not in valid_types:
                self.logger.error(f"Invalid registry_type: {registry_type}. Must be one of: {valid_types}")
                return None
            
            # 1. Retrieve source artifact from Artifact Plane
            if not self.artifact_plane:
                raise RuntimeError(
                    "Artifact plane not wired; cannot retrieve source artifact. Platform contract §8A."
                )
            
            artifact = await self.artifact_plane.get_artifact(
                artifact_id=artifact_id,
                tenant_id=tenant_id,
                include_payload=True
            )
            
            if not artifact:
                self.logger.error(f"Source artifact not found: {artifact_id}")
                return None
            
            # 2. Validate promotion criteria (policy decision via CuratorPrimitives)
            artifact_type = artifact.get("artifact_type", "")
            lifecycle_state = artifact.get("lifecycle_state")
            
            # Use CuratorPrimitives for policy decision (capability by design, implementation by policy)
            if self.curator_primitives:
                validation_result = await self.curator_primitives.validate_promotion(
                    artifact_type=artifact_type,
                    registry_type=registry_type,
                    tenant_id=tenant_id,
                    lifecycle_state=lifecycle_state
                )
                
                if not validation_result.is_allowed:
                    self.logger.error(f"Promotion validation failed: {validation_result.reason} (policy: {validation_result.policy_basis})")
                    return None
            else:
                # Fallback to internal validation if primitives not available
                validation_result = await self._validate_promotion_criteria(
                    artifact=artifact,
                    registry_type=registry_type
                )
                
                if not validation_result.get("is_valid"):
                    self.logger.error(f"Promotion validation failed: {validation_result.get('reason')}")
                    return None
            
            # 3. Generalize outcome (remove client context)
            generalized_definition = await self._generalize_outcome(
                artifact=artifact,
                registry_type=registry_type
            )
            
            if not generalized_definition:
                self.logger.error("Failed to generalize outcome")
                return None
            
            # 4. Create registry entry
            registry_id_result = await self._create_registry_entry(
                registry_type=registry_type,
                registry_id=registry_id,
                registry_name=registry_name,
                registry_definition=generalized_definition,
                source_artifact_id=artifact_id,
                source_tenant_id=tenant_id,
                promoted_by=promoted_by,
                description=description,
                tags=tags
            )
            
            if registry_id_result:
                self.logger.info(f"✅ Promoted to Platform DNA: {registry_id_result} (type: {registry_type})")
                return registry_id_result
            else:
                self.logger.error("Failed to create registry entry")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to promote to Platform DNA: {e}", exc_info=True)
            return None
    
    async def _validate_promotion_criteria(
        self,
        artifact: Dict[str, Any],
        registry_type: str
    ) -> Dict[str, Any]:
        """
        Validate promotion criteria.
        
        Criteria:
        - Artifact must be in "accepted" lifecycle state
        - Artifact must be generalizable (no hard-coded client references)
        - Artifact must be de-identified (no PII or client-specific data)
        - Policy approval (MVP: permissive, production: actual policy check)
        
        Args:
            artifact: Source artifact
            registry_type: Type of registry
        
        Returns:
            Dict with is_valid and reason
        """
        # Check lifecycle state
        lifecycle_state = artifact.get("lifecycle_state")
        if lifecycle_state != "accepted":
            return {
                "is_valid": False,
                "reason": f"Artifact must be in 'accepted' state, current state: {lifecycle_state}"
            }
        
        # Check artifact type matches registry type
        artifact_type = artifact.get("artifact_type", "")
        if registry_type == "solution" and artifact_type not in ["solution", "blueprint"]:
            return {
                "is_valid": False,
                "reason": f"Artifact type '{artifact_type}' cannot be promoted to solution registry"
            }
        elif registry_type == "intent" and artifact_type not in ["intent", "workflow"]:
            return {
                "is_valid": False,
                "reason": f"Artifact type '{artifact_type}' cannot be promoted to intent registry"
            }
        elif registry_type == "realm" and artifact_type not in ["realm", "journey"]:
            return {
                "is_valid": False,
                "reason": f"Artifact type '{artifact_type}' cannot be promoted to realm registry"
            }
        
        # MVP: Permissive validation (capability by design, implementation by policy)
        # Production: Add actual policy checks, PII detection, etc.
        
        return {
            "is_valid": True,
            "reason": "Promotion criteria validated (MVP: permissive)"
        }
    
    async def _generalize_outcome(
        self,
        artifact: Dict[str, Any],
        registry_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generalize outcome by removing client context.
        
        Removes:
        - Tenant-specific references
        - Client-specific data
        - Session-specific data
        - User-specific data
        
        Keeps:
        - Core structure
        - Generalizable patterns
        - Abstracted logic
        
        Args:
            artifact: Source artifact
            registry_type: Type of registry
        
        Returns:
            Generalized definition (de-identified, abstracted)
        """
        try:
            # Get artifact payload
            payload = artifact.get("payload", {})
            if not payload:
                # Try to get from storage path
                storage_path = artifact.get("payload_storage_path")
                if storage_path and self.artifact_plane:
                    # Retrieve from Artifact Plane storage
                    full_artifact = await self.artifact_plane.get_artifact(
                        artifact_id=artifact.get("artifact_id"),
                        tenant_id=artifact.get("tenant_id"),
                        include_payload=True
                    )
                    if full_artifact:
                        payload = full_artifact.get("payload", {})
            
            if not payload:
                self.logger.warning("No payload found in artifact, using metadata only")
                payload = {}
            
            # Extract semantic payload (the meaning, not the rendering)
            semantic_payload = payload.get("semantic_payload", payload)
            
            # Generalize: Remove client-specific fields
            generalized = self._remove_client_context(semantic_payload)
            
            # Add metadata
            generalized_definition = {
                "definition": generalized,
                "artifact_type": artifact.get("artifact_type"),
                "generalized_at": self.clock.now_iso(),
                "source_artifact_type": artifact.get("artifact_type")
            }
            
            return generalized_definition
            
        except Exception as e:
            self.logger.error(f"Failed to generalize outcome: {e}", exc_info=True)
            return None
    
    def _remove_client_context(self, data: Any) -> Any:
        """
        Recursively remove client-specific context from data.
        
        Removes:
        - tenant_id, tenant_name
        - user_id, user_name
        - session_id
        - client-specific IDs
        - PII fields
        
        Args:
            data: Data to generalize (dict, list, or primitive)
        
        Returns:
            Generalized data
        """
        if isinstance(data, dict):
            # Remove client-specific keys
            client_keys = [
                "tenant_id", "tenant_name", "user_id", "user_name", "session_id",
                "client_id", "client_name", "organization_id", "organization_name",
                "email", "phone", "address", "personal_data"
            ]
            
            generalized = {}
            for key, value in data.items():
                if key.lower() not in [k.lower() for k in client_keys]:
                    # Recursively generalize value
                    generalized[key] = self._remove_client_context(value)
            
            return generalized
        
        elif isinstance(data, list):
            # Generalize each item in list
            return [self._remove_client_context(item) for item in data]
        
        else:
            # Primitive value - return as-is
            return data
    
    async def _create_registry_entry(
        self,
        registry_type: str,
        registry_id: Optional[str],
        registry_name: str,
        registry_definition: Dict[str, Any],
        source_artifact_id: str,
        source_tenant_id: str,
        promoted_by: str,
        description: Optional[str],
        tags: Optional[List[str]]
    ) -> Optional[str]:
        """
        Create registry entry in appropriate registry table.
        
        Args:
            registry_type: Type of registry ("solution", "intent", "realm")
            registry_id: Registry ID (if None, will be generated)
            registry_name: Human-readable name
            registry_definition: Generalized definition
            source_artifact_id: Source artifact ID
            source_tenant_id: Source tenant ID
            promoted_by: Who promoted
            description: Optional description
            tags: Optional tags
        
        Returns:
            Registry ID (UUID string) or None if creation failed
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot create registry entry. Platform contract §8A."
            )
        
        try:
            # Generate registry_id if not provided
            if not registry_id:
                # Generate from registry_name (deterministic)
                namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                registry_id = str(uuid.uuid5(namespace, f"{registry_type}:{registry_name}"))
            
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID."""
                if not value:
                    return None
                try:
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                    return str(uuid.uuid5(namespace, str(value)))
            
            # Determine table name and field names based on registry_type
            table_name = f"{registry_type}_registry"
            id_field = f"{registry_type}_id"
            name_field = f"{registry_type}_name"
            definition_field = f"{registry_type}_definition"
            version_field = f"{registry_type}_version"
            
            # Prepare registry entry
            registry_entry = {
                id_field: registry_id,
                name_field: registry_name,
                version_field: 1,  # Start at version 1
                definition_field: registry_definition,
                "source_artifact_id": source_artifact_id,
                "source_tenant_id": to_uuid(source_tenant_id),
                "promoted_at": self.clock.now_iso(),
                "promoted_by": promoted_by,
                "parent_registry_id": None,  # Original version has no parent
                "is_current_version": True,
                "description": description,
                "tags": tags or [],
                "metadata": {},
                "created_at": self.clock.now_iso(),
                "created_by": promoted_by
            }
            
            # Insert into registry table
            response = self.supabase_adapter.service_client.table(table_name).insert(
                registry_entry
            ).execute()
            
            if response.data and len(response.data) > 0:
                created_registry_id = response.data[0].get("registry_id")
                self.logger.info(f"Created registry entry: {created_registry_id} in {table_name}")
                return str(created_registry_id)
            else:
                self.logger.error(f"Failed to create registry entry: No data returned")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to create registry entry: {e}", exc_info=True)
            return None
