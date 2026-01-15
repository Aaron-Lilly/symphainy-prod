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
    """
    Protocol for authentication operations.
    
    Returns raw data (Dict[str, Any]) - no business objects.
    Platform SDK translates raw data to SecurityContext.
    """
    
    async def authenticate(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user.
        
        Returns raw data only - no business logic, no SecurityContext.
        Platform SDK will translate this to SecurityContext.
        
        Args:
            credentials: Authentication credentials
        
        Returns:
            Optional[Dict[str, Any]]: Raw authentication data or None if failed
            Structure:
            {
                "success": bool,
                "user_id": str,
                "email": str,
                "access_token": str,
                "refresh_token": str,
                "expires_in": int,
                "expires_at": int,
                "raw_user_data": Dict[str, Any],
                "raw_session_data": Dict[str, Any],
                "raw_user_metadata": Dict[str, Any],
                "raw_app_metadata": Dict[str, Any],
                "raw_provider_data": Dict[str, Any],
                "error": Optional[str]
            }
        """
        ...
    
    async def validate_token(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Validate token.
        
        Returns raw data only - no business logic, no SecurityContext.
        Platform SDK will translate this to SecurityContext.
        
        Args:
            token: Authentication token
        
        Returns:
            Optional[Dict[str, Any]]: Raw validation data or None if invalid
        """
        ...
    
    async def refresh_token(
        self,
        refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Refresh token.
        
        Returns raw data only - no business logic, no SecurityContext.
        Platform SDK will translate this to SecurityContext.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Optional[Dict[str, Any]]: Raw refresh data or None if failed
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
        
        Returns raw tenant data only - no business logic.
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            Optional[Dict[str, Any]]: Raw tenant information or None if not found
        """
        ...
    
    async def get_user_tenant_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get raw tenant information for a specific user.
        
        Returns raw data from user_tenants table and user metadata.
        No business logic - just infrastructure data access.
        
        Args:
            user_id: User ID
        
        Returns:
            Dict[str, Any]: Raw tenant information
            Structure:
            {
                "tenant_id": str,
                "primary_tenant_id": str,
                "tenant_type": str,
                "roles": List[str],
                "permissions": List[str],
                "raw_user_tenant_data": Dict[str, Any]
            }
        """
        ...
