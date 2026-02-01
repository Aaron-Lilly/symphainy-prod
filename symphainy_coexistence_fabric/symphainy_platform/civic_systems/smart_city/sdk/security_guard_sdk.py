"""
Security Guard SDK - Authentication, Authorization, and Tenant Context Coordination

SDK for Security Guard coordination (used by Experience, Solution, Realms).

WHAT (Smart City Role): I coordinate authentication, authorization, and tenant context
HOW (SDK Implementation): I use Public Works abstractions to prepare execution contracts

⚠️ CRITICAL: NO Runtime dependency.
SDKs prepare execution contracts. Runtime validates and executes them.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from utilities import get_logger, get_clock
from symphainy_platform.foundations.public_works.protocols.auth_protocol import (
    AuthenticationProtocol,
    TenancyProtocol,
    SecurityContext
)


@dataclass
class AuthenticationResult:
    """Authentication result with execution contract."""
    user_id: str
    tenant_id: str
    email: str
    permissions: List[str]
    roles: List[str]
    execution_contract: Dict[str, Any]  # Prepared for Runtime validation


@dataclass
class TenantContext:
    """Tenant context with execution contract."""
    tenant_id: str
    tenant_type: str
    permissions: List[str]
    roles: List[str]
    execution_contract: Dict[str, Any]  # Prepared for Runtime validation


class SecurityGuardSDK:
    """
    Security Guard SDK - Coordination Logic
    
    Coordinates authentication, authorization, and tenant context.
    Prepares execution contracts for Runtime validation.
    
    ⚠️ NO Runtime dependency - SDKs prepare, Runtime executes.
    """
    
    def __init__(
        self,
        auth_abstraction: AuthenticationProtocol,
        tenant_abstraction: TenancyProtocol,
        policy_resolver: Optional[Any] = None  # Policy library (optional for MVP)
    ):
        """
        Initialize Security Guard SDK.
        
        Args:
            auth_abstraction: Authentication abstraction (from Public Works)
            tenant_abstraction: Tenant abstraction (from Public Works)
            policy_resolver: Optional policy resolver (for policy preparation)
        """
        self.auth_abstraction = auth_abstraction
        self.tenant_abstraction = tenant_abstraction
        self.policy_resolver = policy_resolver
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("Security Guard SDK initialized (NO Runtime dependency)")
    
    async def authenticate(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[AuthenticationResult]:
        """
        Coordinate authentication (SDK - prepares execution contract).
        
        Returns execution-ready contract that Runtime will validate via primitives.
        
        Args:
            credentials: Authentication credentials (email, password)
        
        Returns:
            AuthenticationResult with execution contract, or None if failed
        """
        try:
            # 1. Call auth abstraction (pure infrastructure)
            auth_data = await self.auth_abstraction.authenticate(credentials)
            
            if not auth_data or not auth_data.get("success"):
                self.logger.warning(f"Authentication failed: {auth_data.get('error', 'Unknown error')}")
                return None
            
            user_id = auth_data.get("user_id")
            email = auth_data.get("email", "")
            
            # 2. Get tenant context (pure infrastructure)
            tenant_info = await self.tenant_abstraction.get_user_tenant_info(user_id)
            
            if not tenant_info:
                self.logger.warning(f"No tenant info found for user {user_id}")
                return None
            
            tenant_id = tenant_info.get("tenant_id") or tenant_info.get("primary_tenant_id")
            roles = tenant_info.get("roles", [])
            permissions = tenant_info.get("permissions", [])
            
            # 3. Resolve policies (preparation, not validation)
            policies = []
            if self.policy_resolver:
                try:
                    policies = await self.policy_resolver.get_policies(tenant_id)
                except Exception as e:
                    self.logger.warning(f"Policy resolution failed (non-fatal): {e}")
            
            # 4. Prepare execution contract (for Runtime validation)
            execution_contract = {
                "action": "authenticate",
                "tenant_id": tenant_id,
                "user_id": user_id,
                "email": email,
                "roles": roles,
                "permissions": permissions,
                "policies": policies,  # Prepared for Runtime validation
                "timestamp": self.clock.now_iso()
            }
            
            return AuthenticationResult(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                permissions=permissions,
                roles=roles,
                execution_contract=execution_contract
            )
            
        except Exception as e:
            self.logger.error(f"Authentication coordination failed: {e}", exc_info=True)
            return None
    
    async def register_user(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[AuthenticationResult]:
        """
        Coordinate user registration (SDK - prepares execution contract).
        
        Returns execution-ready contract that Runtime will validate via primitives.
        
        Args:
            credentials: Registration credentials (email, password, name, etc.)
        
        Returns:
            AuthenticationResult with execution contract, or None if failed
        """
        try:
            # 1. Call auth abstraction (pure infrastructure)
            auth_data = await self.auth_abstraction.register_user(credentials)
            
            if not auth_data or not auth_data.get("success"):
                self.logger.warning(f"Registration failed: {auth_data.get('error', 'Unknown error')}")
                return None
            
            user_id = auth_data.get("user_id")
            email = auth_data.get("email", "")
            
            # 2. Get tenant context (pure infrastructure)
            # For new users, tenant may not exist yet - try to get it
            tenant_info = await self.tenant_abstraction.get_user_tenant_info(user_id)
            
            if not tenant_info:
                # For new users, create default tenant context
                # In production, tenant creation would be handled by Runtime
                tenant_id = f"tenant_{user_id}"  # Default tenant
                roles = ["user"]
                permissions = ["read", "write"]
                self.logger.info(f"New user {user_id} - using default tenant context")
            else:
                tenant_id = tenant_info.get("tenant_id") or tenant_info.get("primary_tenant_id")
                roles = tenant_info.get("roles", ["user"])
                permissions = tenant_info.get("permissions", ["read", "write"])
            
            # 3. Resolve policies (preparation, not validation)
            policies = []
            if self.policy_resolver:
                try:
                    policies = await self.policy_resolver.get_policies(tenant_id)
                except Exception as e:
                    self.logger.warning(f"Policy resolution failed (non-fatal): {e}")
            
            # 4. Prepare execution contract (for Runtime validation)
            execution_contract = {
                "action": "register_user",
                "tenant_id": tenant_id,
                "user_id": user_id,
                "email": email,
                "roles": roles,
                "permissions": permissions,
                "policies": policies,  # Prepared for Runtime validation
                "timestamp": self.clock.now_iso()
            }
            
            return AuthenticationResult(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                permissions=permissions,
                roles=roles,
                execution_contract=execution_contract
            )
            
        except Exception as e:
            self.logger.error(f"Registration coordination failed: {e}", exc_info=True)
            return None
    
    async def validate_token(
        self,
        token: str
    ) -> Optional[AuthenticationResult]:
        """
        Coordinate token validation (SDK - prepares execution contract).
        
        Args:
            token: Authentication token
        
        Returns:
            AuthenticationResult with execution contract, or None if invalid
        """
        try:
            # 1. Validate token (pure infrastructure)
            validation_data = await self.auth_abstraction.validate_token(token)
            
            if not validation_data or not validation_data.get("success"):
                self.logger.warning("Token validation failed")
                return None
            
            user_id = validation_data.get("user_id")
            email = validation_data.get("email", "")
            
            # 2. Get tenant context
            tenant_info = await self.tenant_abstraction.get_user_tenant_info(user_id)
            
            if not tenant_info:
                return None
            
            tenant_id = tenant_info.get("tenant_id") or tenant_info.get("primary_tenant_id")
            roles = tenant_info.get("roles", [])
            permissions = tenant_info.get("permissions", [])
            
            # 3. Prepare execution contract
            execution_contract = {
                "action": "validate_token",
                "tenant_id": tenant_id,
                "user_id": user_id,
                "email": email,
                "roles": roles,
                "permissions": permissions,
                "timestamp": self.clock.now_iso()
            }
            
            return AuthenticationResult(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                permissions=permissions,
                roles=roles,
                execution_contract=execution_contract
            )
            
        except Exception as e:
            self.logger.error(f"Token validation coordination failed: {e}", exc_info=True)
            return None
    
    async def get_tenant_context(
        self,
        tenant_id: str
    ) -> Optional[TenantContext]:
        """
        Get tenant context (SDK - prepares execution contract).
        
        Args:
            tenant_id: Tenant identifier
        
        Returns:
            TenantContext with execution contract, or None if not found
        """
        try:
            # 1. Get tenant (pure infrastructure)
            tenant_data = await self.tenant_abstraction.get_tenant(tenant_id)
            
            if not tenant_data:
                return None
            
            tenant_type = tenant_data.get("tenant_type", "standard")
            
            # 2. Resolve policies (preparation)
            policies = []
            if self.policy_resolver:
                try:
                    policies = await self.policy_resolver.get_policies(tenant_id)
                except Exception as e:
                    self.logger.warning(f"Policy resolution failed (non-fatal): {e}")
            
            # 3. Prepare execution contract
            execution_contract = {
                "action": "get_tenant_context",
                "tenant_id": tenant_id,
                "tenant_type": tenant_type,
                "policies": policies,
                "timestamp": self.clock.now_iso()
            }
            
            return TenantContext(
                tenant_id=tenant_id,
                tenant_type=tenant_type,
                permissions=[],  # Tenant-level permissions (if needed)
                roles=[],  # Tenant-level roles (if needed)
                execution_contract=execution_contract
            )
            
        except Exception as e:
            self.logger.error(f"Tenant context coordination failed: {e}", exc_info=True)
            return None
    
    async def authorize(
        self,
        user_id: str,
        tenant_id: str,
        action: str,
        resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Coordinate authorization (SDK - prepares execution contract).
        
        This prepares the authorization request for Runtime validation.
        Runtime will use Security Guard Primitives to validate.
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            action: Action to authorize
            resource: Optional resource identifier
        
        Returns:
            Dict with authorization preparation (not validation result)
        """
        # 1. Get tenant context
        tenant_context = await self.get_tenant_context(tenant_id)
        
        if not tenant_context:
            return {
                "prepared": False,
                "error": "Tenant not found"
            }
        
        # 2. Resolve policies (preparation)
        policies = []
        if self.policy_resolver:
            try:
                policies = await self.policy_resolver.get_policies(tenant_id, action, resource)
            except Exception as e:
                self.logger.warning(f"Policy resolution failed (non-fatal): {e}")
        
        # 3. Prepare execution contract (for Runtime validation)
        execution_contract = {
            "action": "authorize",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "requested_action": action,
            "resource": resource,
            "policies": policies,  # Prepared for Runtime validation
            "timestamp": self.clock.now_iso()
        }
        
        return {
            "prepared": True,
            "execution_contract": execution_contract
        }

    async def check_email_availability(self, email: str) -> Optional[Dict[str, Any]]:
        """Delegate to auth_abstraction if it has check_email_availability."""
        if self.auth_abstraction and hasattr(self.auth_abstraction, "check_email_availability"):
            return await self.auth_abstraction.check_email_availability(email)
        return None

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Delegate to auth_abstraction if it has check_permission."""
        if self.auth_abstraction and hasattr(self.auth_abstraction, "check_permission"):
            result = await self.auth_abstraction.check_permission(user_id, action, resource)
            return {"authorized": result, "reason": None} if isinstance(result, bool) else result
        return None
