"""
Librarian Primitive - Policy-aware knowledge access.

Pure primitive that makes policy decisions about:
- Search access validation
- Knowledge access validation

Called ONLY by Runtime (via SDK).
No side effects, no infrastructure calls.
"""

from typing import Dict, Any, Optional
from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext
from utilities import get_logger


class LibrarianPrimitive:
    """
    Librarian Primitive - Policy-aware knowledge access.
    
    Pure primitive that makes policy decisions about:
    - Search access validation
    - Knowledge access validation
    
    Called ONLY by Runtime (via SDK).
    No side effects, no infrastructure calls.
    """
    
    def __init__(self):
        """
        Initialize Librarian Primitive.
        
        Note: No dependencies on infrastructure or registries.
        Policy rules come from Runtime context (prepared by SDK).
        """
        self.logger = get_logger(self.__class__.__name__)
    
    async def evaluate_search_access(
        self,
        security_context: SecurityContext,
        action: str,
        tenant_id: str,
        query: Optional[str] = None,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate search access policy.
        
        Policy Logic Only:
        - Is user authorized for this search action?
        - Are policy rules satisfied?
        - Are there query restrictions?
        
        Args:
            security_context: Security context
            action: Action being performed (e.g., "search_knowledge", "semantic_search")
            tenant_id: Tenant ID of the user
            query: Optional search query (for query-based restrictions)
            policy_rules: Policy rules from Policy Registry (prepared by SDK)
        
        Returns:
            Dict[str, Any]: Policy decision
            Structure:
            {
                "allowed": bool,
                "reason": str,
                "policy_source": str,
                "required_roles": List[str],
                "required_permissions": List[str],
                "query_restrictions": Optional[List[str]]
            }
        """
        # Policy Decision 1: Basic authentication check
        if not security_context or not security_context.user_id:
            return {
                "allowed": False,
                "reason": "User not authenticated",
                "policy_source": "librarian_primitive",
                "required_roles": [],
                "required_permissions": []
            }
        
        policy_rules = policy_rules or {}
        
        # Policy Decision 2: Check required roles
        required_roles = policy_rules.get("required_roles", [])
        if required_roles and not any(role in security_context.roles for role in required_roles):
            return {
                "allowed": False,
                "reason": f"Missing required roles: {', '.join(required_roles)}",
                "policy_source": "policy_registry",
                "required_roles": required_roles,
                "required_permissions": []
            }
        
        # Policy Decision 3: Check required permissions
        required_permissions = policy_rules.get("required_permissions", [])
        if required_permissions and not all(perm in security_context.permissions for perm in required_permissions):
            return {
                "allowed": False,
                "reason": f"Missing required permissions: {', '.join(required_permissions)}",
                "policy_source": "policy_registry",
                "required_roles": required_roles,
                "required_permissions": required_permissions
            }
        
        # Policy Decision 4: Query-based restrictions (if query provided)
        if query:
            restricted_queries = policy_rules.get("restricted_queries", [])
            if restricted_queries and any(restricted in query.lower() for restricted in restricted_queries):
                return {
                    "allowed": False,
                    "reason": "Query contains restricted terms",
                    "policy_source": "policy_registry",
                    "required_roles": required_roles,
                    "required_permissions": required_permissions,
                    "query_restrictions": restricted_queries
                }
        
        return {
            "allowed": True,
            "reason": "Search access granted",
            "policy_source": "librarian_primitive",
            "required_roles": required_roles,
            "required_permissions": required_permissions,
            "query_restrictions": policy_rules.get("restricted_queries", [])
        }
    
    async def evaluate_knowledge_access(
        self,
        security_context: SecurityContext,
        action: str,
        tenant_id: str,
        resource: Optional[str] = None,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate knowledge access policy.
        
        Policy Logic Only:
        - Is user authorized for this knowledge action?
        - Are policy rules satisfied?
        - Are there resource restrictions?
        
        Args:
            security_context: Security context
            action: Action being performed (e.g., "read_embeddings", "read_semantic_graph")
            tenant_id: Tenant ID of the user
            resource: Optional resource identifier (e.g., content_id, file_id)
            policy_rules: Policy rules from Policy Registry (prepared by SDK)
        
        Returns:
            Dict[str, Any]: Policy decision
            Structure:
            {
                "allowed": bool,
                "reason": str,
                "policy_source": str,
                "required_roles": List[str],
                "required_permissions": List[str],
                "resource_restrictions": Optional[List[str]]
            }
        """
        # Policy Decision 1: Basic authentication check
        if not security_context or not security_context.user_id:
            return {
                "allowed": False,
                "reason": "User not authenticated",
                "policy_source": "librarian_primitive",
                "required_roles": [],
                "required_permissions": []
            }
        
        policy_rules = policy_rules or {}
        
        # Policy Decision 2: Check required roles
        required_roles = policy_rules.get("required_roles", [])
        if required_roles and not any(role in security_context.roles for role in required_roles):
            return {
                "allowed": False,
                "reason": f"Missing required roles: {', '.join(required_roles)}",
                "policy_source": "policy_registry",
                "required_roles": required_roles,
                "required_permissions": []
            }
        
        # Policy Decision 3: Check required permissions
        required_permissions = policy_rules.get("required_permissions", [])
        if required_permissions and not all(perm in security_context.permissions for perm in required_permissions):
            return {
                "allowed": False,
                "reason": f"Missing required permissions: {', '.join(required_permissions)}",
                "policy_source": "policy_registry",
                "required_roles": required_roles,
                "required_permissions": required_permissions
            }
        
        # Policy Decision 4: Resource-based restrictions (if resource provided)
        if resource:
            restricted_resources = policy_rules.get("restricted_resources", [])
            if restricted_resources and resource in restricted_resources:
                return {
                    "allowed": False,
                    "reason": f"Access denied to resource: {resource}",
                    "policy_source": "policy_registry",
                    "required_roles": required_roles,
                    "required_permissions": required_permissions,
                    "resource_restrictions": restricted_resources
                }
        
        return {
            "allowed": True,
            "reason": "Knowledge access granted",
            "policy_source": "librarian_primitive",
            "required_roles": required_roles,
            "required_permissions": required_permissions,
            "resource_restrictions": policy_rules.get("restricted_resources", [])
        }
