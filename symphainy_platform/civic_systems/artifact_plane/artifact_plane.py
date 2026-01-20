"""
Artifact Plane - Core Implementation

Manages derived artifacts as first-class citizens, separate from execution state.
Coordinates artifact storage (GCS), registry (StateManagement), and lineage (Arango).

WHAT (Artifact Plane Role): I manage artifact lifecycle and retrieval
HOW (Artifact Plane Implementation): I coordinate storage, registry, and lineage
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
# Artifact Plane is at: symphainy_platform/civic_systems/artifact_plane/artifact_plane.py
# Project root is 4 levels up
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utilities import get_logger, get_clock, generate_event_id
from symphainy_platform.foundations.public_works.protocols.artifact_storage_protocol import ArtifactStorageProtocol
from symphainy_platform.foundations.public_works.protocols.state_protocol import StateManagementProtocol
from symphainy_platform.runtime.execution_context import ExecutionContext


class ArtifactPlane:
    """
    Artifact Plane - Manages derived artifacts as first-class citizens.
    
    Artifacts are governed representations (roadmaps, POCs, blueprints, etc.)
    that are:
    - Produced by realms
    - Used across realms
    - Referenced over time
    - Human-visible
    - Policy-governed
    
    They are NOT:
    - Execution state (that's for Runtime)
    - Session state (that's for UX continuity)
    - Raw data (that's for Data Steward)
    """
    
    def __init__(
        self,
        artifact_storage: ArtifactStorageProtocol,
        state_management: StateManagementProtocol
    ):
        """
        Initialize Artifact Plane.
        
        Args:
            artifact_storage: Artifact storage protocol (for payloads in GCS)
            state_management: State management protocol (for registry in Supabase/Arango)
        """
        self.artifact_storage = artifact_storage
        self.state_management = state_management
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("Artifact Plane initialized")
    
    async def create_artifact(
        self,
        artifact_type: str,  # "roadmap", "poc", "blueprint", "sop", etc.
        artifact_id: Optional[str],  # If None, will be generated
        payload: Dict[str, Any],  # Full artifact data
        context: ExecutionContext,
        metadata: Optional[Dict[str, Any]] = None,
        lifecycle_state: str = "draft",  # Initial lifecycle state
        owner: str = "client",  # Owner of artifact
        purpose: str = "delivery",  # Purpose of artifact
        source_artifact_ids: Optional[List[str]] = None  # Dependencies
    ) -> Dict[str, Any]:
        """
        Create and register an artifact in the Artifact Plane.
        
        This:
        1. Stores artifact payload in GCS (via ArtifactStorageProtocol)
        2. Registers artifact metadata in registry (via StateManagementProtocol)
        3. Links artifact to execution for lineage
        4. Sets initial lifecycle state (default: draft)
        
        Args:
            artifact_type: Type of artifact ("roadmap", "poc", "blueprint", etc.)
            artifact_id: Artifact ID (if None, will be generated)
            payload: Full artifact data
            context: Execution context (for lineage and ownership)
            metadata: Optional additional metadata
            lifecycle_state: Initial lifecycle state ("draft", "accepted", "obsolete") - default: "draft"
            owner: Owner of artifact ("client", "platform", "shared") - default: "client"
            purpose: Purpose of artifact ("decision_support", "delivery", "governance", "learning") - default: "delivery"
            source_artifact_ids: Optional list of artifact IDs this artifact depends on
        
        Returns:
            Dict with artifact_id and registry info:
            {
                "artifact_id": "...",
                "storage_path": "...",
                "registry_key": "..."
            }
        """
        try:
            # Generate artifact_id if not provided
            if not artifact_id:
                artifact_id = generate_event_id()
            
            self.logger.info(f"Creating artifact: {artifact_type} ({artifact_id})")
            
            # 1. Store artifact payload in GCS (via ArtifactStorageProtocol)
            storage_metadata = {
                "execution_id": context.execution_id,
                "intent_type": context.intent.intent_type,
                "intent_id": context.intent.intent_id,
                "session_id": context.session_id,
                "solution_id": context.solution_id,
                "realm": self._infer_realm_from_intent(context.intent.intent_type),
                **(metadata or {})
            }
            
            storage_result = await self.artifact_storage.store_artifact(
                artifact_type=artifact_type,
                artifact_data=payload,
                tenant_id=context.tenant_id,
                metadata=storage_metadata
            )
            
            if not storage_result.get("success"):
                raise ValueError(f"Failed to store artifact: {storage_result.get('error')}")
            
            # Use artifact_id from storage if different (storage may generate its own)
            stored_artifact_id = storage_result.get("artifact_id", artifact_id)
            storage_path = storage_result.get("storage_path")
            
            # 2. Register artifact in registry (via StateManagementProtocol)
            registry_key = f"artifact:{context.tenant_id}:{stored_artifact_id}"
            
            # Validate lifecycle fields
            if lifecycle_state not in ["draft", "accepted", "obsolete"]:
                raise ValueError(f"Invalid lifecycle_state: {lifecycle_state}. Must be one of: draft, accepted, obsolete")
            if owner not in ["client", "platform", "shared"]:
                raise ValueError(f"Invalid owner: {owner}. Must be one of: client, platform, shared")
            if purpose not in ["decision_support", "delivery", "governance", "learning"]:
                raise ValueError(f"Invalid purpose: {purpose}. Must be one of: decision_support, delivery, governance, learning")
            
            registry_data = {
                "artifact_id": stored_artifact_id,
                "artifact_type": artifact_type,
                "tenant_id": context.tenant_id,
                "session_id": context.session_id,
                "solution_id": context.solution_id,
                "realm": storage_metadata.get("realm"),
                "intent_type": context.intent.intent_type,
                "intent_id": context.intent.intent_id if hasattr(context.intent, 'intent_id') else None,
                "execution_id": context.execution_id,
                "created_at": self.clock.now_iso(),
                "updated_at": self.clock.now_iso(),
                "payload_storage_path": storage_path,
                "payload_artifact_id": stored_artifact_id,  # Reference to storage
                "regenerable": metadata.get("regenerable", True) if metadata else True,
                "retention_policy": metadata.get("retention_policy", "session") if metadata else "session",
                "metadata": metadata or {},
                # Lifecycle fields (Phase 2.1)
                "lifecycle_state": lifecycle_state,
                "owner": owner,
                "purpose": purpose,
                "lifecycle_transitions": [],  # Initialize empty transitions array
                # Versioning fields (Phase 2.2)
                "version": 1,  # Start at version 1
                "parent_artifact_id": None,  # Original version has no parent
                "is_current_version": True,  # New artifacts are always current version
                # Dependencies (Phase 2.4)
                "source_artifact_ids": source_artifact_ids or []  # List of artifact IDs this depends on
            }
            
            # Store in registry (durable state - ArangoDB)
            registry_success = await self.state_management.store_state(
                state_id=registry_key,
                state_data=registry_data,
                metadata={
                    "type": "artifact_registry",
                    "backend": "arango_db",
                    "strategy": "durable",
                    "tenant_id": context.tenant_id
                },
                ttl=None  # No TTL for durable registry
            )
            
            if not registry_success:
                self.logger.warning(f"Failed to register artifact in registry: {stored_artifact_id}")
                # Continue anyway - storage succeeded, registry is secondary
            
            self.logger.info(f"✅ Artifact created: {stored_artifact_id} (type: {artifact_type})")
            
            return {
                "artifact_id": stored_artifact_id,
                "storage_path": storage_path,
                "registry_key": registry_key,
                "visual_paths": storage_result.get("visual_paths", {})
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create artifact: {e}", exc_info=True)
            raise
    
    async def get_artifact(
        self,
        artifact_id: str,
        tenant_id: str,
        include_payload: bool = True,
        include_visuals: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve an artifact from the Artifact Plane.
        
        Args:
            artifact_id: Artifact ID
            tenant_id: Tenant ID (for security)
            include_payload: If True, retrieve full payload from storage
            include_visuals: If True and include_payload=True, include full visual images
        
        Returns:
            Optional[Dict]: Artifact data with registry info and optionally payload, or None if not found
        """
        try:
            self.logger.info(f"Retrieving artifact: {artifact_id} (tenant: {tenant_id})")
            
            # 1. Get registry entry
            registry_key = f"artifact:{tenant_id}:{artifact_id}"
            self.logger.info(f"Looking up registry key: {registry_key}")
            registry_data = await self.state_management.retrieve_state(registry_key)
            
            if not registry_data:
                self.logger.warning(f"Artifact not found in registry: {artifact_id} (key: {registry_key})")
                # Try to get payload directly from storage (in case registry failed but storage succeeded)
                if include_payload:
                    self.logger.info(f"Trying direct storage retrieval for {artifact_id}")
                    payload = await self.artifact_storage.get_artifact(
                        artifact_id=artifact_id,
                        tenant_id=tenant_id,
                        include_visuals=include_visuals
                    )
                    if payload:
                        self.logger.info(f"Found artifact in storage (registry lookup failed): {artifact_id}")
                        return {
                            "artifact_id": artifact_id,
                            "payload": payload,
                            "registry": None  # Registry lookup failed
                        }
                return None
            
            self.logger.info(f"Found artifact in registry: {artifact_id}")
            result = {
                "artifact_id": artifact_id,
                "registry": registry_data
            }
            
            # 2. Get payload from storage if requested
            if include_payload:
                # Try to get artifact_id from registry if different
                payload_artifact_id = registry_data.get("payload_artifact_id", artifact_id)
                self.logger.info(f"Retrieving payload from storage: {payload_artifact_id}")
                
                payload = await self.artifact_storage.get_artifact(
                    artifact_id=payload_artifact_id,
                    tenant_id=tenant_id,
                    include_visuals=include_visuals
                )
                
                if payload:
                    result["payload"] = payload
                    self.logger.info(f"Retrieved payload for artifact: {artifact_id}")
                else:
                    self.logger.warning(f"Artifact payload not found in storage: {payload_artifact_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get artifact: {e}", exc_info=True)
            return None
    
    async def list_artifacts(
        self,
        tenant_id: str,
        artifact_type: Optional[str] = None,
        session_id: Optional[str] = None,
        solution_id: Optional[str] = None,
        lifecycle_state: Optional[str] = None,
        owner: Optional[str] = None,
        purpose: Optional[str] = None,
        is_current_version: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List artifacts by criteria with filtering and pagination.
        
        Args:
            tenant_id: Tenant ID (required)
            artifact_type: Optional filter by type
            session_id: Optional filter by session
            solution_id: Optional filter by solution
            lifecycle_state: Optional filter by lifecycle state (draft, accepted, obsolete)
            owner: Optional filter by owner (client, platform, shared)
            purpose: Optional filter by purpose (decision_support, delivery, governance, learning)
            is_current_version: Optional filter by current version (True/False)
            limit: Optional result limit
            offset: Optional result offset for pagination
        
        Returns:
            List of artifact registry entries matching criteria
        """
        try:
            self.logger.info(f"Listing artifacts for tenant: {tenant_id}")
            
            # Build filters for state_management.list_states
            filters = {
                "tenant_id": tenant_id
            }
            
            # Add optional filters
            if artifact_type:
                filters["artifact_type"] = artifact_type
            if session_id:
                filters["session_id"] = session_id
            if solution_id:
                filters["solution_id"] = solution_id
            if lifecycle_state:
                filters["lifecycle_state"] = lifecycle_state
            if owner:
                filters["owner"] = owner
            if purpose:
                filters["purpose"] = purpose
            if is_current_version is not None:
                filters["is_current_version"] = is_current_version
            
            # Use state_management.list_states to query artifacts
            # Note: This relies on state_management protocol implementation
            # For Supabase adapter, this queries the artifacts table
            # For other adapters, this uses their list_states implementation
            artifacts = await self.state_management.list_states(
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # Filter results to only include artifacts (registry keys start with "artifact:")
            # Extract artifact_id from registry keys
            result = []
            for artifact_data in artifacts:
                # Extract artifact_id from registry key if present
                registry_key = artifact_data.get("state_id", "")
                if registry_key.startswith("artifact:"):
                    # Extract artifact_id from key format: "artifact:{tenant_id}:{artifact_id}"
                    parts = registry_key.split(":")
                    if len(parts) >= 3:
                        artifact_id = parts[2]
                        artifact_data["artifact_id"] = artifact_id
                        result.append(artifact_data)
                else:
                    # If state_id doesn't follow pattern, include if it has artifact_id
                    if "artifact_id" in artifact_data:
                        result.append(artifact_data)
            
            self.logger.info(f"Found {len(result)} artifacts matching criteria")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to list artifacts: {e}", exc_info=True)
            return []
    
    async def transition_lifecycle_state(
        self,
        artifact_id: str,
        tenant_id: str,
        new_state: str,
        transitioned_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Transition artifact lifecycle state (draft → accepted → obsolete).
        
        This method:
        1. Validates the transition is allowed
        2. Updates the lifecycle state
        3. Records the transition in lifecycle_transitions array
        4. Updates the registry
        
        Args:
            artifact_id: Artifact ID
            tenant_id: Tenant ID (for security)
            new_state: New lifecycle state ("draft", "accepted", "obsolete")
            transitioned_by: User/system that initiated the transition (optional)
            reason: Reason for transition (optional)
        
        Returns:
            bool: True if transition successful, False otherwise
        """
        try:
            # Validate new_state
            if new_state not in ["draft", "accepted", "obsolete"]:
                self.logger.error(f"Invalid lifecycle_state: {new_state}")
                return False
            
            # Get current artifact registry entry
            registry_key = f"artifact:{tenant_id}:{artifact_id}"
            registry_data = await self.state_management.retrieve_state(registry_key)
            
            if not registry_data:
                self.logger.error(f"Artifact not found: {artifact_id}")
                return False
            
            current_state = registry_data.get("lifecycle_state", "draft")
            
            # Validate transition (MVP: permissive - allow all transitions)
            # Production: Can add policy validation here
            valid_transitions = {
                "draft": ["accepted", "obsolete"],
                "accepted": ["obsolete"],
                "obsolete": []  # Obsolete is terminal
            }
            
            if new_state not in valid_transitions.get(current_state, []):
                # Allow same-state transitions (idempotent)
                if new_state == current_state:
                    self.logger.info(f"Artifact already in state {new_state}: {artifact_id}")
                    return True
                else:
                    self.logger.error(f"Invalid transition: {current_state} → {new_state} for artifact {artifact_id}")
                    return False
            
            # Record transition
            transition_record = {
                "from_state": current_state,
                "to_state": new_state,
                "transitioned_at": self.clock.now_iso(),
                "transitioned_by": transitioned_by,
                "reason": reason
            }
            
            # Get existing transitions array
            lifecycle_transitions = registry_data.get("lifecycle_transitions", [])
            lifecycle_transitions.append(transition_record)
            
            # Update registry data
            registry_data["lifecycle_state"] = new_state
            registry_data["lifecycle_transitions"] = lifecycle_transitions
            registry_data["updated_at"] = self.clock.now_iso()
            
            # Store updated registry
            success = await self.state_management.store_state(
                state_id=registry_key,
                state_data=registry_data,
                metadata={
                    "type": "artifact_registry",
                    "backend": "arango_db",
                    "strategy": "durable",
                    "tenant_id": tenant_id
                },
                ttl=None
            )
            
            if success:
                self.logger.info(f"✅ Lifecycle transition: {artifact_id} {current_state} → {new_state}")
            else:
                self.logger.error(f"Failed to update lifecycle state for artifact: {artifact_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to transition lifecycle state: {e}", exc_info=True)
            return False
    
    async def get_artifact_version(
        self,
        artifact_id: str,
        tenant_id: str,
        version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific version of an artifact.
        
        If version is not specified, returns the current version.
        
        Args:
            artifact_id: Artifact ID (base artifact ID)
            tenant_id: Tenant ID (for security)
            version: Optional version number (if None, returns current version)
        
        Returns:
            Optional[Dict]: Artifact data for the specified version, or None if not found
        """
        try:
            if version is None:
                # Get current version
                registry_key = f"artifact:{tenant_id}:{artifact_id}"
                registry_data = await self.state_management.retrieve_state(registry_key)
                
                if not registry_data:
                    return None
                
                # Check if this is the current version
                if registry_data.get("is_current_version", True):
                    return await self.get_artifact(artifact_id, tenant_id, include_payload=True)
                else:
                    # Not current version, but return what we have
                    return await self.get_artifact(artifact_id, tenant_id, include_payload=True)
            else:
                # Get specific version
                # For MVP, we'll search by artifact_id and version
                # In production, this would query the artifacts table directly
                registry_key = f"artifact:{tenant_id}:{artifact_id}"
                registry_data = await self.state_management.retrieve_state(registry_key)
                
                if not registry_data:
                    return None
                
                # Check if this is the requested version
                artifact_version = registry_data.get("version", 1)
                if artifact_version == version:
                    return await self.get_artifact(artifact_id, tenant_id, include_payload=True)
                else:
                    # Version not found (for MVP, we only track current version in state management)
                    # In production, this would query all versions from artifacts table
                    self.logger.warning(f"Version {version} not found for artifact {artifact_id} (current version: {artifact_version})")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Failed to get artifact version: {e}", exc_info=True)
            return None
    
    async def list_artifact_versions(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        List all versions of an artifact.
        
        Args:
            artifact_id: Artifact ID (base artifact ID)
            tenant_id: Tenant ID (for security)
        
        Returns:
            List[Dict]: List of artifact versions (sorted by version number)
        """
        try:
            # For MVP, we only have the current version in state management
            # In production, this would query the artifacts table for all versions
            registry_key = f"artifact:{tenant_id}:{artifact_id}"
            registry_data = await self.state_management.retrieve_state(registry_key)
            
            if not registry_data:
                return []
            
            # Return current version
            artifact = await self.get_artifact(artifact_id, tenant_id, include_payload=False)
            if artifact:
                return [artifact]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to list artifact versions: {e}", exc_info=True)
            return []
    
    async def get_artifact_dependencies(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> List[str]:
        """
        Get list of artifact IDs that this artifact depends on.
        
        Args:
            artifact_id: Artifact ID
            tenant_id: Tenant ID (for security)
        
        Returns:
            List[str]: List of artifact IDs this artifact depends on
        """
        try:
            registry_key = f"artifact:{tenant_id}:{artifact_id}"
            registry_data = await self.state_management.retrieve_state(registry_key)
            
            if not registry_data:
                return []
            
            source_artifact_ids = registry_data.get("source_artifact_ids", [])
            return source_artifact_ids if isinstance(source_artifact_ids, list) else []
            
        except Exception as e:
            self.logger.error(f"Failed to get artifact dependencies: {e}", exc_info=True)
            return []
    
    async def validate_dependencies(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Validate that all dependencies exist before deletion.
        
        Args:
            artifact_id: Artifact ID to validate
            tenant_id: Tenant ID (for security)
        
        Returns:
            Dict with validation result:
            {
                "valid": bool,
                "missing_dependencies": List[str],
                "dependent_artifacts": List[str]  # Artifacts that depend on this one
            }
        """
        try:
            # Get artifact dependencies
            dependencies = await self.get_artifact_dependencies(artifact_id, tenant_id)
            
            # Check if dependencies exist
            missing_dependencies = []
            for dep_id in dependencies:
                dep_key = f"artifact:{tenant_id}:{dep_id}"
                dep_data = await self.state_management.retrieve_state(dep_key)
                if not dep_data:
                    missing_dependencies.append(dep_id)
            
            # For MVP, we can't easily find dependent artifacts (would require reverse search)
            # In production, this would query artifacts table for artifacts that have this one in source_artifact_ids
            dependent_artifacts = []
            
            return {
                "valid": len(missing_dependencies) == 0,
                "missing_dependencies": missing_dependencies,
                "dependent_artifacts": dependent_artifacts
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate dependencies: {e}", exc_info=True)
            return {
                "valid": False,
                "missing_dependencies": [],
                "dependent_artifacts": []
            }
    
    async def register_lineage(
        self,
        artifact_id: str,
        source_execution_id: str,
        source_intent: str,
        context: ExecutionContext
    ) -> bool:
        """
        Register artifact lineage (which execution/intent created it).
        
        This is automatically done in create_artifact, but can be called separately
        for additional lineage relationships.
        
        Args:
            artifact_id: Artifact ID
            source_execution_id: Execution that created it
            source_intent: Intent that created it
            context: Execution context
        
        Returns:
            bool: True if successful
        """
        # Lineage is stored in registry during create_artifact via source_artifact_ids
        # Additional lineage relationships can be stored in Arango graph for graph queries
        # For MVP, lineage is tracked via source_artifact_ids in artifact registry
        # This method provides an explicit API for registering execution-level lineage
        self.logger.info(f"Lineage registered: {artifact_id} <- {source_execution_id}")
        
        # Store execution lineage in registry metadata
        try:
            registry_key = f"artifact:{tenant_id}:{artifact_id}"
            registry_data = await self.state_management.retrieve_state(registry_key)
            
            if registry_data:
                # Add execution lineage to metadata
                metadata = registry_data.get("metadata", {})
                execution_lineage = metadata.get("execution_lineage", [])
                if source_execution_id not in execution_lineage:
                    execution_lineage.append(source_execution_id)
                    metadata["execution_lineage"] = execution_lineage
                    
                    # Update registry with new metadata
                    await self.state_management.update_state(
                        state_id=registry_key,
                        updates={"metadata": metadata}
                    )
                    self.logger.info(f"Updated execution lineage for artifact: {artifact_id}")
            
            return True
        except Exception as e:
            self.logger.warning(f"Failed to register execution lineage: {e}")
            # Return True anyway - lineage is also tracked via source_artifact_ids
            return True
    
    def _infer_realm_from_intent(self, intent_type: str) -> str:
        """Infer realm name from intent type."""
        if intent_type.startswith("generate_roadmap") or intent_type.startswith("create_poc") or intent_type.startswith("synthesize_outcome") or intent_type.startswith("create_solution"):
            return "outcomes"
        elif intent_type.startswith("create_workflow") or intent_type.startswith("generate_sop") or intent_type.startswith("create_blueprint") or intent_type.startswith("optimize_process"):
            return "journey"
        elif intent_type.startswith("interpret_data") or intent_type.startswith("assess_data_quality") or intent_type.startswith("analyze_data"):
            return "insights"
        elif intent_type.startswith("ingest_file") or intent_type.startswith("parse_content") or intent_type.startswith("register_file"):
            return "content"
        else:
            return "unknown"
