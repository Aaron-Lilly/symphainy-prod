"""
Authentication, Authorization, and Tenancy Protocol - Abstraction Contract (Layer 2)

Defines the interface for authentication, authorization, and tenancy operations.
Enables swappability between Supabase, Auth0, AWS Cognito, etc.

WHAT (Infrastructure Role): I define the contract for auth operations
HOW (Infrastructure Implementation): I specify the interface for auth, authz, and tenancy
"""

from typing import Protocol, Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SecurityContext:
    """Security context data structure - no technology dependencies."""
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    email: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    origin: Optional[str] = None


class AuthenticationProtocol(Protocol):
    """Protocol for authentication operations."""
    
    async def authenticate(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[SecurityContext]:
        """
        Authenticate user.
        
        Args:
            credentials: Authentication credentials
        
        Returns:
            Optional[SecurityContext]: User session or None if failed
        """
        ...
    
    async def validate_token(
        self,
        token: str
    ) -> Optional[SecurityContext]:
        """
        Validate token.
        
        Args:
            token: Authentication token
        
        Returns:
            Optional[SecurityContext]: User context or None if invalid
        """
        ...
    
    async def refresh_token(
        self,
        refresh_token: str
    ) -> Optional[SecurityContext]:
        """
        Refresh token.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Optional[SecurityContext]: New user session or None if failed
        """
        ...


class AuthorizationProtocol(Protocol):
    """Protocol for authorization operations."""
    
    async def check_permission(
        self,
        user_id: str,
        permission: str,
        resource: Optional[str] = None
    ) -> bool:
        """
        Check if user has permission.
        
        Args:
            user_id: User ID
            permission: Permission to check
            resource: Optional resource identifier
        
        Returns:
            bool: True if user has permission
        """
        ...
    
    async def get_user_permissions(
        self,
        user_id: str
    ) -> List[str]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            List of permission strings
        """
        ...


class TenancyProtocol(Protocol):
    """Protocol for tenancy operations."""
    
    async def get_tenant(
        self,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get tenant information.
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            Optional[Dict]: Tenant information or None if not found
        """
        ...
    
    async def validate_tenant_access(
        self,
        user_tenant_id: str,
        resource_tenant_id: str
    ) -> bool:
        """
        Validate tenant access.
        
        Args:
            user_tenant_id: User's tenant ID
            resource_tenant_id: Resource's tenant ID
        
        Returns:
            bool: True if access is allowed
        """
        ...
