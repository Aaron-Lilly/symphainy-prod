"""
Security Guard Primitives - Policy Validation and Permission Checks

Primitives for Security Guard policy decisions (used by Runtime only).

WHAT (Smart City Role): I validate policies and check permissions
HOW (Primitive Implementation): I provide pure functions, no side effects, deterministic

⚠️ CRITICAL: Primitives are used by Runtime only.
SDKs prepare execution contracts. Primitives validate them.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from utilities import get_logger


class PolicyStore:
    """
    Policy store interface (abstract).
    
    In MVP: Simple in-memory or Redis-based policy store
    In full: ArangoDB graph-based policy store with caching
    """
    
    async def get_policies(
        self,
        tenant_id: str,
        action: Optional[str] = None,
        resource: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get policies for tenant, action, resource.
        
        Args:
            tenant_id: Tenant identifier
            action: Optional action filter
            resource: Optional resource filter
        
        Returns:
            List of policy dictionaries
        """
        # MVP: Return empty list (no policies in MVP)
        # Full: Query ArangoDB graph for policies
        return []
    
    async def evaluate_policy(
        self,
        policy: Dict[str, Any],
        user_id: str,
        tenant_id: str,
        action: str,
        resource: Optional[str] = None
    ) -> bool:
        """
        Evaluate a single policy.
        
        Args:
            policy: Policy dictionary
            user_id: User identifier
            tenant_id: Tenant identifier
            action: Action to check
            resource: Optional resource identifier
        
        Returns:
            True if policy allows, False otherwise
        """
        # MVP: Simple allow-all (for MVP showcase)
        # Full: Sophisticated policy evaluation engine
        return True


class SecurityGuardPrimitives:
    """
    Security Guard Primitives - Policy Validation
    
    Pure functions for policy validation and permission checks.
    Used by Runtime only.
    """
    
    def __init__(self, policy_store: Optional[PolicyStore] = None):
        """
        Initialize Security Guard Primitives.
        
        Args:
            policy_store: Optional policy store (for MVP, can be None)
        """
        self.policy_store = policy_store or PolicyStore()
        self.logger = get_logger(self.__class__.__name__)
    
    @staticmethod
    async def check_permission(
        user_id: str,
        tenant_id: str,
        action: str,
        resource: Optional[str],
        policy_store: PolicyStore,
        execution_contract: Dict[str, Any]
    ) -> bool:
        """
        Check if user has permission (Primitive - pure function, no side effects).
        
        This is called by Runtime to validate the execution contract
        prepared by Security Guard SDK.
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            action: Action to check
            resource: Optional resource identifier
            policy_store: Policy store instance
            execution_contract: Execution contract prepared by SDK
        
        Returns:
            True if permission granted, False otherwise
        """
        try:
            # 1. Load policies (from cache or store)
            policies = await policy_store.get_policies(tenant_id, action, resource)
            
            # If SDK prepared policies in execution contract, use those
            if execution_contract.get("policies"):
                policies = execution_contract.get("policies")
            
            # 2. Evaluate policies (deterministic)
            for policy in policies:
                allowed = await policy_store.evaluate_policy(
                    policy, user_id, tenant_id, action, resource
                )
                if not allowed:
                    return False
            
            # MVP: If no policies, allow (for MVP showcase)
            # Full: Default deny if no policies
            return True
            
        except Exception as e:
            # Log error but return False (fail secure)
            logger = get_logger("SecurityGuardPrimitives")
            logger.error(f"Permission check failed: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def validate_tenant_access(
        user_id: str,
        tenant_id: str,
        policy_store: PolicyStore,
        execution_contract: Dict[str, Any]
    ) -> bool:
        """
        Validate tenant access (Primitive - pure function, no side effects).
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            policy_store: Policy store instance
            execution_contract: Execution contract prepared by SDK
        
        Returns:
            True if tenant access granted, False otherwise
        """
        try:
            # 1. Check if user belongs to tenant
            # (This would typically check user_tenants table)
            # For MVP: Allow if execution contract has tenant_id
            if execution_contract.get("tenant_id") == tenant_id:
                return True
            
            # 2. Check tenant-level policies
            policies = await policy_store.get_policies(tenant_id)
            
            # Evaluate tenant access policies
            for policy in policies:
                if policy.get("type") == "tenant_access":
                    allowed = await policy_store.evaluate_policy(
                        policy, user_id, tenant_id, "access_tenant", None
                    )
                    if not allowed:
                        return False
            
            # MVP: Default allow (for MVP showcase)
            return True
            
        except Exception as e:
            logger = get_logger("SecurityGuardPrimitives")
            logger.error(f"Tenant access validation failed: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def validate_authentication(
        execution_contract: Dict[str, Any],
        policy_store: PolicyStore
    ) -> bool:
        """
        Validate authentication execution contract (Primitive).
        
        Args:
            execution_contract: Execution contract prepared by SDK
            policy_store: Policy store instance
        
        Returns:
            True if authentication is valid, False otherwise
        """
        try:
            # 1. Check required fields
            required_fields = ["action", "tenant_id", "user_id", "email"]
            for field in required_fields:
                if field not in execution_contract:
                    return False
            
            # 2. Validate action
            if execution_contract.get("action") != "authenticate":
                return False
            
            # 3. Check authentication policies (if any)
            tenant_id = execution_contract.get("tenant_id")
            policies = await policy_store.get_policies(tenant_id, "authenticate")
            
            for policy in policies:
                allowed = await policy_store.evaluate_policy(
                    policy,
                    execution_contract.get("user_id"),
                    tenant_id,
                    "authenticate",
                    None
                )
                if not allowed:
                    return False
            
            # MVP: Default allow (for MVP showcase)
            return True
            
        except Exception as e:
            logger = get_logger("SecurityGuardPrimitives")
            logger.error(f"Authentication validation failed: {e}", exc_info=True)
            return False
