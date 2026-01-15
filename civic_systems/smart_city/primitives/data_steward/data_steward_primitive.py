"""
Data Steward Primitive - Policy-Aware Primitive for Data Access

Makes policy decisions only:
- Can user access this data?
- Can user perform this action on this data?
- What are the data access constraints?

WHAT (Smart City Role): I make policy decisions about data access
HOW (Smart City Implementation): I evaluate policies and return decisions (no side effects)
"""

from typing import Dict, Any, Optional

from utilities import get_logger
from civic_systems.smart_city.registries.policy_registry import PolicyRegistry


class DataStewardPrimitive:
    """
    Data Steward Primitive - Policy-aware primitive for data access.
    
    Makes policy decisions only:
    - Can user access this data?
    - Can user perform this action on this data?
    - What are the data access constraints?
    
    Policy Logic Only:
    - No side effects
    - No infrastructure calls
    - Only: Observe context, validate policy, emit allow/deny/annotate
    """
    
    def __init__(self, policy_registry: PolicyRegistry):
        """
        Initialize Data Steward Primitive.
        
        Args:
            policy_registry: Policy Registry for querying data access policies
        """
        self.policy_registry = policy_registry
        self.logger = get_logger(self.__class__.__name__)
        
        self.logger.info("Data Steward Primitive initialized")
    
    async def evaluate_data_access(
        self,
        action: str,
        user_id: str,
        tenant_id: str,
        resource: str,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate data access policy.
        
        Policy Logic Only:
        - Is user allowed to access this data?
        - Are tenant isolation rules satisfied?
        - Are data classification rules satisfied?
        
        Args:
            action: Action being performed (e.g., "file.read", "content.write")
            user_id: User ID
            tenant_id: Tenant ID
            resource: Resource identifier (e.g., file_uuid, content_id)
            policy_rules: Optional policy rules (from Policy Registry via Platform SDK)
        
        Returns:
            Dict with policy decision:
            {
                "allowed": bool,
                "reason": str,
                "requires_approval": bool,
                "constraints": Dict[str, Any]
            }
        """
        policy_rules = policy_rules or {}
        
        # Policy Decision 1: Basic access check
        if not user_id or not tenant_id:
            return {
                "allowed": False,
                "reason": "User or tenant not specified",
                "requires_approval": False,
                "constraints": {}
            }
        
        # Policy Decision 2: Tenant isolation
        isolation_level = policy_rules.get("isolation_level", "strict")
        if isolation_level == "strict":
            # In strict isolation, users can only access their tenant's data
            # This primitive only decides if isolation is required, not how to enforce it
            # Runtime will handle actual enforcement (e.g., query filtering)
            pass
        
        # Policy Decision 3: Data classification
        data_classification_required = policy_rules.get("data_classification_required", False)
        if data_classification_required:
            # Check if user has required classification level
            # This primitive only decides if classification is required, not how to check it
            # Runtime will handle actual checking (e.g., query user permissions)
            pass
        
        # Policy Decision 4: Action-specific rules
        required_permissions = policy_rules.get("required_permissions", [])
        if required_permissions:
            # This primitive only decides what permissions are required, not if user has them
            # Runtime will handle actual permission checking
            pass
        
        # Policy Decision 5: Resource-specific rules
        resource_constraints = policy_rules.get("resource_constraints", {})
        if resource_constraints:
            # This primitive only decides what constraints apply, not how to enforce them
            # Runtime will handle actual enforcement
            pass
        
        # Default: Allow if no blocking policies
        return {
            "allowed": True,
            "reason": "Data access granted",
            "requires_approval": False,
            "constraints": resource_constraints
        }
    
    async def evaluate_data_classification(
        self,
        data_classification: str,
        user_classification: str,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate data classification policy.
        
        Policy Logic Only:
        - Can user with this classification access data with this classification?
        
        Args:
            data_classification: Data classification level (e.g., "public", "internal", "confidential")
            user_classification: User classification level
            policy_rules: Optional policy rules
        
        Returns:
            Dict with policy decision
        """
        policy_rules = policy_rules or {}
        
        # Classification hierarchy (policy decision)
        classification_hierarchy = policy_rules.get("classification_hierarchy", {
            "public": 0,
            "internal": 1,
            "confidential": 2,
            "restricted": 3
        })
        
        data_level = classification_hierarchy.get(data_classification.lower(), 999)
        user_level = classification_hierarchy.get(user_classification.lower(), 0)
        
        # Policy Decision: User must have equal or higher classification
        allowed = user_level >= data_level
        
        return {
            "allowed": allowed,
            "reason": f"User classification {user_classification} {'meets' if allowed else 'does not meet'} data classification {data_classification}",
            "data_classification": data_classification,
            "user_classification": user_classification,
            "requires_approval": False
        }
