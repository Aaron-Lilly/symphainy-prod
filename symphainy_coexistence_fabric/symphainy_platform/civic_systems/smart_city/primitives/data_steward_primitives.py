"""
Data Steward Primitives - Policy Decisions for Data Governance

Primitives for Data Steward policy decisions (used by Runtime only).
"""

from __future__ import annotations  # Enable postponed evaluation of annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
import hashlib

from utilities import get_logger, get_clock

if TYPE_CHECKING:
    # Forward reference for type hints
    pass


@dataclass
class DataPermissionCheck:
    """Data permission check result."""
    is_allowed: bool
    data_id: str
    reason: Optional[str] = None


@dataclass
class ProvenanceChainValidation:
    """Provenance chain validation result."""
    is_valid: bool
    chain: list[Dict[str, Any]]  # Using list instead of List for Python 3.9+ compatibility
    reason: Optional[str] = None


@dataclass
class DataAccessRequest:
    """Data access request result."""
    access_granted: bool
    contract_id: Optional[str] = None
    access_reason: Optional[str] = None
    access_conditions: Optional[Dict[str, Any]] = None


@dataclass
class MaterializationAuthorization:
    """Materialization authorization result."""
    materialization_allowed: bool
    materialization_type: Optional[str] = None  # 'reference', 'partial_extraction', 'deterministic', 'semantic_embedding', 'full_artifact'
    materialization_scope: Optional[Dict[str, Any]] = None
    materialization_ttl: Optional[timedelta] = None
    materialization_backing_store: Optional[str] = None  # 'gcs', 'supabase', 'memory', 'none'
    policy_basis: Optional[str] = None
    reason: Optional[str] = None


class DataStewardPrimitives:
    """
    Data Steward Primitives - Policy Decisions
    
    Makes policy decisions for data governance.
    """
    
    def __init__(
        self, 
        policy_store: Optional[Any] = None,  # Legacy - kept for backward compatibility
        boundary_contract_store: Optional[Any] = None,  # BoundaryContractStore (defined later in file)
        materialization_policy_store: Optional[Any] = None  # MaterializationPolicyStore for configurable policy
    ):
        self.policy_store = policy_store  # Legacy
        self.boundary_contract_store = boundary_contract_store  # BoundaryContractStore instance
        self.materialization_policy_store = materialization_policy_store  # ✅ MaterializationPolicyStore for policy decisions
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def check_data_permission(
        self,
        data_id: str,
        user_id: str,
        tenant_id: str,
        action: str
    ) -> DataPermissionCheck:
        """Check data permission (policy decision)."""
        # MVP: Basic validation
        if not data_id:
            return DataPermissionCheck(
                is_allowed=False,
                data_id=data_id,
                reason="Data ID is required"
            )
        
        return DataPermissionCheck(
            is_allowed=True,
            data_id=data_id
        )
    
    async def validate_provenance_chain(
        self,
        provenance_chain: list[Dict[str, Any]],  # Using list instead of List for Python 3.9+ compatibility
        tenant_id: str
    ) -> ProvenanceChainValidation:
        """Validate provenance chain (policy decision)."""
        # MVP: Basic validation
        if not provenance_chain:
            return ProvenanceChainValidation(
                is_valid=False,
                chain=provenance_chain,
                reason="Provenance chain is required"
            )
        
        return ProvenanceChainValidation(
            is_valid=True,
            chain=provenance_chain
        )
    
    async def request_data_access(
        self,
        intent: Dict[str, Any],
        context: Dict[str, Any],
        external_source_type: str,
        external_source_identifier: str,
        external_source_metadata: Optional[Dict[str, Any]] = None
    ) -> DataAccessRequest:
        """
        Request data access - negotiate boundary contract.
        
        This is the FIRST step before any data materialization.
        Answers: Can we read the external data?
        
        Args:
            intent: Intent that triggered the request
            context: Execution context (tenant_id, user_id, etc.)
            external_source_type: Type of external source ('file', 'api', 'database', etc.)
            external_source_identifier: Identifier for external source (file path, API endpoint, etc.)
            external_source_metadata: Additional source metadata
        
        Returns:
            DataAccessRequest with access_granted and contract_id
        """
        tenant_id = context.get("tenant_id")
        user_id = context.get("user_id")
        intent_id = intent.get("intent_id")
        
        if not tenant_id or not user_id:
            return DataAccessRequest(
                access_granted=False,
                access_reason="tenant_id and user_id are required"
            )
        
        # Check if contract already exists for this source
        existing_contract = None
        if self.boundary_contract_store:
            try:
                existing_contract = await self.boundary_contract_store.get_boundary_contract(
                    tenant_id=tenant_id,
                    external_source_type=external_source_type,
                    external_source_identifier=external_source_identifier
                )
            except Exception as e:
                self.logger.debug(f"Error checking existing contract: {e}")
        
        # If contract exists and is active, reuse it
        if existing_contract and existing_contract.get("contract_status") == "active":
            return DataAccessRequest(
                access_granted=existing_contract.get("access_granted", False),
                contract_id=existing_contract.get("contract_id"),
                access_reason=existing_contract.get("access_reason"),
                access_conditions=existing_contract.get("access_conditions")
            )
        
        # ✅ Get policy from MaterializationPolicyStore (configurable, not hardcoded)
        policy = None
        solution_id = context.get("solution_id")
        
        if self.materialization_policy_store:
            try:
                policy = await self.materialization_policy_store.get_policy(
                    tenant_id=tenant_id,
                    solution_id=solution_id
                )
                self.logger.debug(f"Retrieved policy from MaterializationPolicyStore for tenant: {tenant_id}")
            except Exception as e:
                self.logger.warning(f"Failed to get policy from MaterializationPolicyStore: {e}, using store default")
                # Policy store has built-in fallback to MVP permissive policy
        
        # ✅ Use policy store's built-in default if no policy found
        if not policy and self.materialization_policy_store:
            policy = self.materialization_policy_store._get_mvp_permissive_policy()
            self.logger.debug("Using MaterializationPolicyStore default MVP permissive policy")
        
        # ✅ Make policy decision (policy decision in Civic Systems, not Runtime)
        # MVP: Always grant access (policy decision)
        access_granted = True
        access_reason = policy.get("policy_version", "mvp_1.0") if policy else "mvp_default_policy"
        access_conditions = {
            "policy_basis": policy.get("policy_version", "mvp_1.0") if policy else "mvp_default",
            "materialization_pending": True  # Will be authorized in authorize_materialization()
        }
        
        # Create boundary contract
        contract_id = None
        if self.boundary_contract_store:
            try:
                # Convert string IDs to UUIDs (database expects UUIDs)
                def to_uuid(value: Optional[str]) -> Optional[str]:
                    """Convert string to UUID, generating deterministic UUID if not valid UUID format."""
                    if not value:
                        return None
                    try:
                        # Try to parse as UUID
                        return str(uuid.UUID(value))
                    except (ValueError, AttributeError):
                        # Generate deterministic UUID from string (for test values like "test_tenant")
                        # Use namespace UUID v5 for deterministic generation
                        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
                        return str(uuid.uuid5(namespace, str(value)))
                
                # ✅ Include policy information in contract
                contract_data = {
                    "tenant_id": to_uuid(tenant_id),
                    "user_id": to_uuid(user_id),
                    "intent_id": to_uuid(intent_id),
                    "external_source_type": external_source_type,
                    "external_source_identifier": external_source_identifier,
                    "external_source_metadata": external_source_metadata or {},
                    "access_granted": access_granted,
                    "access_granted_at": self.clock.now_iso(),
                    "access_granted_by": "data_steward_primitives",  # ✅ Policy assigned by Civic Systems
                    "access_reason": access_reason,
                    "access_conditions": access_conditions,
                    "contract_status": "pending",  # Will be activated after materialization decision
                    "created_by": to_uuid(user_id),
                    "contract_terms": {
                        "intent_type": intent.get("intent_type"),
                        "requested_at": self.clock.now_iso(),
                        "policy_basis": policy.get("policy_version", "mvp_1.0") if policy else "mvp_default"
                    }
                }
                contract_id = await self.boundary_contract_store.create_boundary_contract(contract_data)
            except Exception as e:
                self.logger.error(f"Failed to create boundary contract: {e}", exc_info=True)
        
        return DataAccessRequest(
            access_granted=access_granted,
            contract_id=contract_id,
            access_reason=access_reason,
            access_conditions=access_conditions
        )
    
    async def authorize_materialization(
        self,
        contract_id: str,
        tenant_id: str,
        requested_type: Optional[str] = None,  # Requested materialization type
        materialization_policy: Optional[Any] = None,  # MaterializationPolicyStore
        context: Optional[Dict[str, Any]] = None  # Execution context with user_id, session_id, solution_id
    ) -> MaterializationAuthorization:
        """
        Authorize materialization - decide what form and where.
        
        This is the SECOND step after access is granted.
        Answers: Can we persist it? In what form? For how long? Where? Who can access it?
        
        Args:
            contract_id: Boundary contract ID from request_data_access()
            tenant_id: Tenant identifier
            requested_type: Requested materialization type (optional)
            materialization_policy: MaterializationPolicyStore for policy decisions
            context: Execution context with user_id, session_id, solution_id (for workspace scoping)
        
        Returns:
            MaterializationAuthorization with materialization decision including scope
        """
        if not contract_id:
            return MaterializationAuthorization(
                materialization_allowed=False,
                reason="contract_id is required"
            )
        
        # Get boundary contract
        contract = None
        if self.boundary_contract_store:
            try:
                contract = await self.boundary_contract_store.get_boundary_contract_by_id(
                    contract_id=contract_id,
                    tenant_id=tenant_id
                )
            except Exception as e:
                self.logger.error(f"Failed to get boundary contract: {e}", exc_info=True)
        
        if not contract:
            return MaterializationAuthorization(
                materialization_allowed=False,
                reason="Boundary contract not found"
            )
        
        # Check if access was granted
        if not contract.get("access_granted"):
            return MaterializationAuthorization(
                materialization_allowed=False,
                reason="Access not granted in boundary contract"
            )
        
        # Determine materialization type from policy
        # Use database-backed policy store (capability by design, implementation by policy)
        materialization_type = requested_type or "full_artifact"  # Default fallback
        materialization_backing_store = "gcs"  # Default fallback
        materialization_ttl = None  # Default: Permanent
        policy_basis = "mvp_default_policy"  # Default fallback
        
        # Get artifact type from contract metadata or use default
        artifact_type = contract.get("external_source_metadata", {}).get("artifact_type", "file")
        solution_id = context.get("solution_id") if context else None
        
        # ✅ Use database-backed policy store if available (preferred)
        # This is the configurable policy store (not hardcoded)
        if self.materialization_policy_store:
            try:
                decision = await self.materialization_policy_store.evaluate_policy(
                    artifact_type=artifact_type,
                    tenant_id=tenant_id,
                    solution_id=solution_id,
                    requested_type=requested_type
                )
                
                if decision.get("allowed", False):
                    materialization_type = decision.get("materialization_type", requested_type or "full_artifact")
                    materialization_backing_store = decision.get("backing_store", "gcs")
                    ttl_days = decision.get("ttl_days")
                    if ttl_days:
                        materialization_ttl = timedelta(days=ttl_days)
                    policy_basis = decision.get("policy_basis", "materialization_policy")
                else:
                    # Policy denied materialization
                    return MaterializationAuthorization(
                        materialization_allowed=False,
                        reason=f"Materialization not allowed by policy for artifact type: {artifact_type}"
                    )
                    
            except Exception as e:
                self.logger.warning(f"Error evaluating materialization policy: {e}")
                # Fall through to legacy policy evaluation or defaults
        
        # Fallback to legacy materialization_policy if provided (for backward compatibility)
        elif materialization_policy:
            try:
                decision = await materialization_policy.evaluate_policy(
                    artifact_type=artifact_type,
                    tenant_id=tenant_id
                )
                if decision == "persist":
                    materialization_type = "full_artifact"
                    materialization_backing_store = "gcs"
                    policy_basis = "materialization_policy_persist"
                elif decision == "cache":
                    materialization_type = "deterministic"  # Cache as deterministic representation
                    materialization_backing_store = "supabase"
                    materialization_ttl = timedelta(hours=24)  # Default cache TTL
                    policy_basis = "materialization_policy_cache"
                elif decision == "discard":
                    materialization_type = "reference"  # Reference only, no materialization
                    materialization_backing_store = "none"
                    policy_basis = "materialization_policy_discard"
            except Exception as e:
                self.logger.warning(f"Error evaluating materialization policy: {e}")
        
        # Calculate expiration time if TTL is set
        materialization_expires_at = None
        if materialization_ttl:
            materialization_expires_at = (datetime.now() + materialization_ttl).isoformat()
        
        # Set materialization_scope and reference_scope from context (for MVP: workspace-scoped)
        materialization_scope = {}
        reference_scope = {}
        
        if context:
            user_id = context.get("user_id") or "system"
            session_id = context.get("session_id")
            solution_id = context.get("solution_id")
            
            # Convert user_id to UUID for consistency (materialization_scope should store UUID for filtering)
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID, generating deterministic UUID if not valid UUID format."""
                if not value:
                    return None
                try:
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                    return str(uuid.uuid5(namespace, str(value)))
            
            # Set materialization scope (where this materialization is scoped to)
            # Store user_id as UUID for consistent filtering
            materialization_scope = {
                "user_id": to_uuid(user_id),  # Store as UUID for consistent filtering
                "session_id": session_id,
                "solution_id": solution_id,
                "scope_type": "workspace"  # MVP default: workspace-scoped
            }
            
            # Set reference scope (who can reference/access this materialization)
            reference_scope = {
                "users": [user_id] if user_id else [],
                "scope_type": "workspace"
            }
        
        # Update contract with materialization decision including scope
        if self.boundary_contract_store:
            try:
                # Convert timedelta to PostgreSQL INTERVAL format
                ttl_interval = None
                if materialization_ttl:
                    ttl_interval = f"{int(materialization_ttl.total_seconds())} seconds"
                
                await self.boundary_contract_store.update_boundary_contract(
                    contract_id=contract_id,
                    tenant_id=tenant_id,
                    updates={
                        "materialization_allowed": True,
                        "materialization_type": materialization_type,
                        "materialization_scope": materialization_scope,  # ADD: Workspace scope
                        "reference_scope": reference_scope,  # ADD: Who can access
                        "materialization_backing_store": materialization_backing_store,
                        "materialization_ttl": ttl_interval,  # PostgreSQL INTERVAL format
                        "materialization_expires_at": materialization_expires_at,
                        "materialization_policy_basis": policy_basis,
                        "contract_status": "active",
                        "activated_at": self.clock.now_iso()
                    }
                )
            except Exception as e:
                self.logger.error(f"Failed to update boundary contract: {e}", exc_info=True)
        
        return MaterializationAuthorization(
            materialization_allowed=True,
            materialization_type=materialization_type,
            materialization_scope=materialization_scope,  # ADD: Return scope
            materialization_backing_store=materialization_backing_store,
            materialization_ttl=materialization_ttl,
            policy_basis=policy_basis,
            reason=f"Materialization authorized: {materialization_type} (workspace-scoped)"
        )


class BoundaryContractStore:
    """
    Boundary Contract Store - Interface for boundary contract persistence.
    
    In MVP: Uses Supabase adapter for database operations
    In full: Could use ArangoDB graph-based contract store
    """
    
    def __init__(self, supabase_adapter: Optional[Any] = None):
        """
        Initialize Boundary Contract Store.
        
        Args:
            supabase_adapter: Supabase adapter for database operations
        """
        self.supabase_adapter = supabase_adapter
        self.logger = get_logger(self.__class__.__name__)
    
    async def create_boundary_contract(self, contract_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new boundary contract in Supabase.
        
        Args:
            contract_data: Contract data dictionary
        
        Returns:
            Contract ID (UUID string) or None if creation failed
        """
        if not self.supabase_adapter:
            self.logger.warning("Supabase adapter not available, cannot create boundary contract")
            return None
        
        try:
            # Generate contract_id if not provided
            if "contract_id" not in contract_data:
                contract_data["contract_id"] = str(uuid.uuid4())
            
            # Insert into data_boundary_contracts table
            response = self.supabase_adapter.service_client.table("data_boundary_contracts").insert(
                contract_data
            ).execute()
            
            if response.data and len(response.data) > 0:
                contract_id = response.data[0].get("contract_id")
                self.logger.info(f"Created boundary contract: {contract_id}")
                return contract_id
            else:
                self.logger.error("Failed to create boundary contract: No data returned")
                return None
        except Exception as e:
            self.logger.error(f"Failed to create boundary contract: {e}", exc_info=True)
            return None
    
    async def get_boundary_contract(
        self,
        tenant_id: str,
        external_source_type: str,
        external_source_identifier: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get boundary contract by external source.
        
        Args:
            tenant_id: Tenant identifier
            external_source_type: Type of external source
            external_source_identifier: Identifier for external source
        
        Returns:
            Contract dictionary or None if not found
        """
        if not self.supabase_adapter:
            return None
        
        try:
            # Convert string IDs to UUIDs (database expects UUIDs)
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID, generating deterministic UUID if not valid UUID format."""
                if not value:
                    return None
                try:
                    # Try to parse as UUID
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    # Generate deterministic UUID from string (for test values like "test_tenant")
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
                    return str(uuid.uuid5(namespace, str(value)))
            
            response = self.supabase_adapter.service_client.table("data_boundary_contracts").select(
                "*"
            ).eq("tenant_id", to_uuid(tenant_id)).eq(
                "external_source_type", external_source_type
            ).eq(
                "external_source_identifier", external_source_identifier
            ).eq(
                "contract_status", "active"
            ).order("created_at", desc=True).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            self.logger.error(f"Failed to get boundary contract: {e}", exc_info=True)
            return None
    
    async def get_boundary_contract_by_id(
        self,
        contract_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get boundary contract by contract ID.
        
        Args:
            contract_id: Contract identifier
            tenant_id: Tenant identifier
        
        Returns:
            Contract dictionary or None if not found
        """
        if not self.supabase_adapter:
            return None
        
        try:
            # Convert string IDs to UUIDs (database expects UUIDs)
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID, generating deterministic UUID if not valid UUID format."""
                if not value:
                    return None
                try:
                    # Try to parse as UUID
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    # Generate deterministic UUID from string (for test values like "test_tenant")
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
                    return str(uuid.uuid5(namespace, str(value)))
            
            response = self.supabase_adapter.service_client.table("data_boundary_contracts").select(
                "*"
            ).eq("contract_id", to_uuid(contract_id)).eq("tenant_id", to_uuid(tenant_id)).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            self.logger.error(f"Failed to get boundary contract by ID: {e}", exc_info=True)
            return None
    
    async def update_boundary_contract(
        self,
        contract_id: str,
        tenant_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update boundary contract.
        
        Args:
            contract_id: Contract identifier
            tenant_id: Tenant identifier
            updates: Dictionary of fields to update
        
        Returns:
            True if update successful, False otherwise
        """
        if not self.supabase_adapter:
            return False
        
        try:
            # Convert string IDs to UUIDs (database expects UUIDs)
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID, generating deterministic UUID if not valid UUID format."""
                if not value:
                    return None
                try:
                    # Try to parse as UUID
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    # Generate deterministic UUID from string (for test values like "test_tenant")
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
                    return str(uuid.uuid5(namespace, str(value)))
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now().isoformat()
            
            response = self.supabase_adapter.service_client.table("data_boundary_contracts").update(
                updates
            ).eq("contract_id", to_uuid(contract_id)).eq("tenant_id", to_uuid(tenant_id)).execute()
            
            if response.data:
                self.logger.debug(f"Updated boundary contract: {contract_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to update boundary contract: {e}", exc_info=True)
            return False