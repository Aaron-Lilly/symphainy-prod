"""
Security Guard Primitive - Policy-aware authentication and authorization.

Pure primitive that makes policy decisions about:
- Authentication validation
- Authorization checks
- Permission validation
- Zero-trust enforcement
- Tenant isolation

Called ONLY by Runtime (via SDK).
No side effects, no infrastructure calls.

Phase 1: Scaffold structure
Phase 5: Full implementation
"""

from typing import Dict, Any, Optional, List
from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext
from utilities import get_logger


class SecurityGuardPrimitive:
    """
    Security Guard Primitive - Policy-aware authentication and authorization.
    
    Pure primitive that makes policy decisions.
    Called ONLY by Runtime (via SDK).
    No side effects, no infrastructure calls.
    """
    
    def __init__(self):
        """
        Initialize Security Guard Primitive.
        
        Note: No dependencies on infrastructure or registries.
        Policy rules come from Runtime context (prepared by SDK).
        """
        self.logger = get_logger(self.__class__.__name__)
    
    async def evaluate_auth(
        self,
        security_context: SecurityContext,
        action: str,
        resource: Optional[str] = None,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate authentication policy.
        
        Policy Logic Only:
        - Is user authenticated?
        - Does security context permit action?
        - Are policy rules satisfied?
        
        Args:
            security_context: Security context
            action: Action being performed
            resource: Optional resource identifier
            policy_rules: Policy rules from Policy Registry (prepared by SDK)
        
        Returns:
            Dict[str, Any]: Policy decision
            Structure:
            {
                "allowed": bool,
                "requires_mfa": bool,
                "zero_trust_enabled": bool,
                "reason": str,
                "policy_source": str
            }
        """
        # Policy Decision 1: Check if user is authenticated
        if not security_context or not security_context.user_id:
            return {
                "allowed": False,
                "requires_mfa": False,
                "zero_trust_enabled": False,
                "reason": "User not authenticated",
                "policy_source": "security_guard_primitive"
            }
        
        # Policy Decision 2: Check policy rules (from Policy Registry)
        if policy_rules:
            # Extract policy configuration from policy_rules
            zero_trust_enabled = policy_rules.get("zero_trust_enabled", False)
            require_mfa = policy_rules.get("require_mfa", False)
            allowed_actions = policy_rules.get("allowed_actions", [])
            denied_actions = policy_rules.get("denied_actions", [])
            
            # Check if action is explicitly denied
            if denied_actions and action in denied_actions:
                return {
                    "allowed": False,
                    "requires_mfa": False,
                    "zero_trust_enabled": zero_trust_enabled,
                    "reason": f"Action '{action}' is explicitly denied by policy",
                    "policy_source": "policy_registry"
                }
            
            # Check if action is explicitly allowed (if list is non-empty)
            if allowed_actions and action not in allowed_actions:
                return {
                    "allowed": False,
                    "requires_mfa": False,
                    "zero_trust_enabled": zero_trust_enabled,
                    "reason": f"Action '{action}' is not in allowed actions list",
                    "policy_source": "policy_registry"
                }
            
            # Policy Decision 3: Zero-trust check
            if zero_trust_enabled:
                # Zero-trust policy: Always verify
                return {
                    "allowed": True,  # Will be verified by Runtime
                    "requires_mfa": require_mfa,
                    "zero_trust_enabled": True,
                    "reason": "Zero-trust policy requires continuous verification",
                    "policy_source": "policy_registry"
                }
            
            # Policy Decision 4: MFA requirement
            if require_mfa:
                return {
                    "allowed": True,
                    "requires_mfa": True,
                    "zero_trust_enabled": False,
                    "reason": "MFA required by policy",
                    "policy_source": "policy_registry"
                }
        
        # Default: Allow authenticated users (MVP open policy)
        return {
            "allowed": True,
            "requires_mfa": False,
            "zero_trust_enabled": False,
            "reason": "Authenticated user allowed (default policy)",
            "policy_source": "security_guard_primitive"
        }
    
    async def validate_tenant_access(
        self,
        tenant_id: str,
        user_tenant_id: str,
        resource_tenant_id: Optional[str] = None,
        isolation_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate tenant access.
        
        Policy Logic Only:
        - Does user tenant match resource tenant?
        - Are isolation rules satisfied?
        - Is cross-tenant access allowed?
        
        Args:
            tenant_id: Tenant ID (user's tenant)
            user_tenant_id: User's tenant ID (should match tenant_id)
            resource_tenant_id: Optional resource tenant ID
            isolation_rules: Tenant isolation rules from Policy Registry (prepared by SDK)
        
        Returns:
            Dict[str, Any]: Policy decision
            Structure:
            {
                "allowed": bool,
                "isolation_level": str,
                "allow_admin_override": bool,
                "reason": str,
                "policy_source": str
            }
        """
        # Policy Decision 1: Check if user tenant matches
        if user_tenant_id != tenant_id:
            return {
                "allowed": False,
                "isolation_level": "strict",
                "allow_admin_override": False,
                "reason": f"User tenant '{user_tenant_id}' does not match requested tenant '{tenant_id}'",
                "policy_source": "security_guard_primitive"
            }
        
        # Policy Decision 2: Check resource tenant isolation
        if resource_tenant_id:
            # Same tenant = always allowed
            if resource_tenant_id == tenant_id:
                return {
                    "allowed": True,
                    "isolation_level": "strict",
                    "allow_admin_override": False,
                    "reason": "Resource belongs to same tenant",
                    "policy_source": "security_guard_primitive"
                }
            
            # Different tenant = check isolation rules
            if isolation_rules:
                isolation_level = isolation_rules.get("isolation_level", "strict")
                allow_admin_override = isolation_rules.get("allow_admin_override", False)
                allowed_cross_tenant_actions = isolation_rules.get("allowed_cross_tenant_actions", [])
                
                # Strict isolation: deny cross-tenant access
                if isolation_level == "strict":
                    return {
                        "allowed": False,
                        "isolation_level": "strict",
                        "allow_admin_override": allow_admin_override,
                        "reason": f"Strict isolation: cannot access resource from tenant '{resource_tenant_id}'",
                        "policy_source": "policy_registry"
                    }
                
                # Moderate isolation: allow with restrictions
                if isolation_level == "moderate":
                    # TODO: Check allowed_cross_tenant_actions
                    return {
                        "allowed": True,
                        "isolation_level": "moderate",
                        "allow_admin_override": allow_admin_override,
                        "reason": "Moderate isolation: cross-tenant access allowed with restrictions",
                        "policy_source": "policy_registry"
                    }
                
                # Permissive isolation: allow cross-tenant access
                if isolation_level == "permissive":
                    return {
                        "allowed": True,
                        "isolation_level": "permissive",
                        "allow_admin_override": allow_admin_override,
                        "reason": "Permissive isolation: cross-tenant access allowed",
                        "policy_source": "policy_registry"
                    }
            
            # Default: strict isolation if no rules
            return {
                "allowed": False,
                "isolation_level": "strict",
                "allow_admin_override": False,
                "reason": f"Default strict isolation: cannot access resource from tenant '{resource_tenant_id}'",
                "policy_source": "security_guard_primitive"
            }
        
        # No resource tenant specified = allow (user accessing their own tenant)
        return {
            "allowed": True,
            "isolation_level": "strict",
            "allow_admin_override": False,
            "reason": "User accessing own tenant",
            "policy_source": "security_guard_primitive"
        }
    
    async def check_permission(
        self,
        security_context: SecurityContext,
        permission: str,
        resource: Optional[str] = None,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check permission policy.
        
        Policy Logic Only:
        - Does user have explicit permission?
        - Does user have role that grants permission?
        - Does admin role grant all permissions?
        
        Args:
            security_context: Security context
            permission: Permission to check
            resource: Optional resource identifier
            policy_rules: Policy rules from Policy Registry (prepared by SDK)
        
        Returns:
            Dict[str, Any]: Policy decision
            Structure:
            {
                "allowed": bool,
                "permission_source": str,
                "reason": str,
                "policy_source": str
            }
        """
        # Policy Decision 1: Admin override
        if security_context.roles and "admin" in security_context.roles:
            return {
                "allowed": True,
                "permission_source": "admin_role",
                "reason": "Admin role grants all permissions",
                "policy_source": "security_guard_primitive"
            }
        
        # Policy Decision 2: Explicit permission
        if security_context.permissions and permission in security_context.permissions:
            return {
                "allowed": True,
                "permission_source": "explicit",
                "reason": "User has explicit permission",
                "policy_source": "security_guard_primitive"
            }
        
        # Policy Decision 3: Role-based permission (would check role → permission mapping)
        # For now, deny if not explicit
        # TODO: Implement role → permission mapping from Policy Registry
        return {
            "allowed": False,
            "permission_source": "none",
            "reason": f"User does not have required permission '{permission}'",
            "policy_source": "security_guard_primitive"
        }
    
    async def enforce_zero_trust(
        self,
        security_context: SecurityContext,
        action: str,
        resource: str,
        policy_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enforce zero-trust policy.
        
        Policy Logic Only:
        - Never trust, always verify
        - Continuous validation
        - Adaptive access control
        
        Args:
            security_context: Security context
            action: Action being performed
            resource: Resource identifier
            policy_rules: Policy rules from Policy Registry (prepared by SDK)
        
        Returns:
            Dict[str, Any]: Policy decision
            Structure:
            {
                "allowed": bool,
                "verification_required": List[str],
                "reason": str,
                "policy_source": str
            }
        """
        # Policy Decision 1: Check if zero-trust is enabled
        zero_trust_enabled = False
        if policy_rules:
            zero_trust_enabled = policy_rules.get("zero_trust_enabled", False)
        
        if not zero_trust_enabled:
            return {
                "allowed": True,
                "verification_required": [],
                "reason": "Zero-trust not enabled",
                "policy_source": "security_guard_primitive"
            }
        
        # Policy Decision 2: Zero-trust policy - always verify
        verification_required = []
        
        # Check if action requires additional verification
        if action in ["admin", "delete", "modify"]:
            verification_required.append("mfa")
        
        if resource.startswith("/api/admin/"):
            verification_required.append("device")
        
        # High-risk actions require additional verification
        high_risk_actions = ["delete", "modify", "admin", "export"]
        if action in high_risk_actions:
            verification_required.append("mfa")
            verification_required.append("device")
        
        return {
            "allowed": True,  # Will be verified by Runtime
            "verification_required": verification_required,
            "reason": "Zero-trust policy requires continuous verification",
            "policy_source": "policy_registry" if policy_rules else "security_guard_primitive"
        }
