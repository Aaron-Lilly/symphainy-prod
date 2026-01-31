"""
Materialization Policy Store - Database-backed policy store.

Stores materialization policies in Supabase with tenant-scoped support and platform defaults.
Implements "capability by design, implementation by policy" - real infrastructure with permissive MVP policies.
"""

import sys
from pathlib import Path

# MaterializationPolicyStore is at: symphainy_platform/civic_systems/smart_city/stores/materialization_policy_store.py
# Project root is 5 levels up
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from utilities import get_logger, get_clock
import uuid


class MaterializationPolicyStore:
    """
    Materialization Policy Store - Database-backed policy store.
    
    Supports:
    - Tenant-scoped policies (override platform defaults)
    - Platform-level default policies
    - Solution-specific policies (override tenant policies)
    - Policy versioning
    """
    
    def __init__(self, supabase_adapter: Optional[Any] = None):
        """
        Initialize Materialization Policy Store.
        
        Args:
            supabase_adapter: Supabase adapter for database operations
        """
        self.supabase_adapter = supabase_adapter
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self._policy_cache: Dict[str, Dict[str, Any]] = {}  # Cache for policy lookups
    
    async def get_policy(
        self,
        tenant_id: Optional[str] = None,
        solution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get materialization policy for tenant/solution.
        
        Policy resolution order:
        1. Solution-specific policy (if solution_id provided)
        2. Tenant-specific policy (if tenant_id provided)
        3. Platform default policy
        
        Args:
            tenant_id: Optional tenant identifier
            solution_id: Optional solution identifier
        
        Returns:
            Dict with policy configuration:
            {
                "allow_all_types": bool,
                "allowed_types": List[str],
                "default_ttl_days": int,
                "default_backing_store": str,
                "no_restrictions": bool,
                "policy_version": str
            }
        """
        # Build cache key
        cache_key = f"{tenant_id or 'platform'}:{solution_id or 'default'}"
        
        # Check cache
        if cache_key in self._policy_cache:
            return self._policy_cache[cache_key]
        
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot get materialization policy. Platform contract §8A."
            )
        
        try:
            policy = None
            
            # 1. Try solution-specific policy
            if solution_id:
                policy = await self._get_solution_policy(solution_id)
                if policy:
                    self.logger.info(f"Using solution-specific policy for solution: {solution_id}")
            
            # 2. Try tenant-specific policy
            if not policy and tenant_id:
                policy = await self._get_tenant_policy(tenant_id)
                if policy:
                    self.logger.info(f"Using tenant-specific policy for tenant: {tenant_id}")
            
            # 3. Fall back to platform default
            if not policy:
                policy = await self._get_platform_default_policy()
                if policy:
                    self.logger.info("Using platform default policy")
            
            # If still no policy, use MVP permissive
            if not policy:
                self.logger.warning("No policy found in database, using MVP permissive policy")
                policy = self._get_mvp_permissive_policy()
            
            # Cache policy
            self._policy_cache[cache_key] = policy
            
            return policy
            
        except Exception as e:
            self.logger.error(f"Failed to get materialization policy: {e}", exc_info=True)
            # Fallback to MVP permissive policy
            return self._get_mvp_permissive_policy()
    
    async def _get_solution_policy(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """Get solution-specific policy."""
        try:
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID."""
                if not value:
                    return None
                try:
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                    return str(uuid.uuid5(namespace, str(value)))
            
            response = self.supabase_adapter.service_client.table("materialization_policies").select(
                "*"
            ).eq("solution_id", to_uuid(solution_id)).eq(
                "is_active", True
            ).order("policy_version", desc=True).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get("policy_rules", {})
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get solution policy: {e}", exc_info=True)
            return None
    
    async def _get_tenant_policy(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant-specific policy."""
        try:
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID."""
                if not value:
                    return None
                try:
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                    return str(uuid.uuid5(namespace, str(value)))
            
            response = self.supabase_adapter.service_client.table("materialization_policies").select(
                "*"
            ).eq("tenant_id", to_uuid(tenant_id)).is_(
                "solution_id", "null"
            ).eq(
                "is_active", True
            ).order("policy_version", desc=True).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get("policy_rules", {})
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get tenant policy: {e}", exc_info=True)
            return None
    
    async def _get_platform_default_policy(self) -> Optional[Dict[str, Any]]:
        """Get platform default policy."""
        try:
            response = self.supabase_adapter.service_client.table("materialization_policies").select(
                "*"
            ).is_(
                "tenant_id", "null"
            ).eq(
                "is_platform_default", True
            ).eq(
                "is_active", True
            ).order("policy_version", desc=True).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0].get("policy_rules", {})
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get platform default policy: {e}", exc_info=True)
            return None
    
    def _get_mvp_permissive_policy(self) -> Dict[str, Any]:
        """
        Get MVP permissive policy (fallback when database is not available).
        
        This is the "capability by design, implementation by policy" approach:
        - Real infrastructure exists (database-backed policy store)
        - But MVP uses permissive policies
        - Production can tighten policies without code changes
        """
        return {
            "allow_all_types": True,
            "allowed_types": [
                "reference",
                "partial_extraction",
                "deterministic",
                "semantic_embedding",
                "full_artifact"
            ],
            "default_ttl_days": 30,
            "default_backing_store": "gcs",
            "no_restrictions": True,
            "policy_version": "mvp_1.0"
        }
    
    async def evaluate_policy(
        self,
        artifact_type: str,
        tenant_id: Optional[str] = None,
        solution_id: Optional[str] = None,
        requested_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate materialization policy for artifact type.
        
        Args:
            artifact_type: Type of artifact (e.g., "file", "roadmap", "poc")
            tenant_id: Optional tenant identifier
            solution_id: Optional solution identifier
            requested_type: Optional requested materialization type
        
        Returns:
            Dict with materialization decision:
            {
                "materialization_type": str,  # "reference", "partial_extraction", "deterministic", "semantic_embedding", "full_artifact"
                "backing_store": str,  # "gcs", "supabase", "none"
                "ttl_days": int,  # TTL in days (None for permanent)
                "allowed": bool,  # Whether materialization is allowed
                "policy_basis": str  # Policy that authorized this
            }
        """
        try:
            # Get policy
            policy = await self.get_policy(tenant_id=tenant_id, solution_id=solution_id)
            
            # Check if all types are allowed
            if policy.get("allow_all_types", False):
                # MVP permissive: Allow all types
                materialization_type = requested_type or "full_artifact"
                backing_store = policy.get("default_backing_store", "gcs")
                ttl_days = policy.get("default_ttl_days", 30)
                
                return {
                    "materialization_type": materialization_type,
                    "backing_store": backing_store,
                    "ttl_days": ttl_days,
                    "allowed": True,
                    "policy_basis": f"mvp_permissive_policy_{policy.get('policy_version', '1.0')}"
                }
            
            # Check if requested type is in allowed types
            allowed_types = policy.get("allowed_types", [])
            if requested_type and requested_type in allowed_types:
                materialization_type = requested_type
                backing_store = policy.get("default_backing_store", "gcs")
                ttl_days = policy.get("default_ttl_days", 30)
                
                return {
                    "materialization_type": materialization_type,
                    "backing_store": backing_store,
                    "ttl_days": ttl_days,
                    "allowed": True,
                    "policy_basis": f"policy_{policy.get('policy_version', '1.0')}"
                }
            
            # Requested type not allowed
            return {
                "materialization_type": None,
                "backing_store": None,
                "ttl_days": None,
                "allowed": False,
                "policy_basis": f"policy_{policy.get('policy_version', '1.0')}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate materialization policy: {e}", exc_info=True)
            # Fail secure: Deny materialization if policy evaluation fails
            return {
                "materialization_type": None,
                "backing_store": None,
                "ttl_days": None,
                "allowed": False,
                "policy_basis": "policy_evaluation_failed"
            }
    
    async def create_tenant_policy(
        self,
        tenant_id: str,
        policy_rules: Dict[str, Any],
        policy_name: str = "Tenant Materialization Policy",
        description: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a tenant-specific materialization policy.
        
        Args:
            tenant_id: Tenant identifier
            policy_rules: Policy rules dictionary
            policy_name: Human-readable policy name
            description: Optional policy description
        
        Returns:
            Policy ID (UUID string) or None if creation failed
        """
        if not self.supabase_adapter:
            raise RuntimeError(
                "Supabase adapter not wired; cannot create tenant policy. Platform contract §8A."
            )
        
        try:
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID."""
                if not value:
                    return None
                try:
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                    return str(uuid.uuid5(namespace, str(value)))
            
            policy_data = {
                "tenant_id": to_uuid(tenant_id),
                "solution_id": None,
                "policy_name": policy_name,
                "policy_version": 1,
                "policy_rules": policy_rules,
                "is_platform_default": False,
                "is_active": True,
                "description": description,
                "created_by": "system"
            }
            
            response = self.supabase_adapter.service_client.table("materialization_policies").insert(
                policy_data
            ).execute()
            
            if response.data and len(response.data) > 0:
                policy_id = response.data[0].get("policy_id")
                self.logger.info(f"Created tenant materialization policy: {policy_id}")
                # Clear cache for this tenant
                self._policy_cache.pop(f"{tenant_id}:default", None)
                return str(policy_id)
            else:
                self.logger.error("Failed to create tenant policy: No data returned")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to create tenant policy: {e}", exc_info=True)
            return None
