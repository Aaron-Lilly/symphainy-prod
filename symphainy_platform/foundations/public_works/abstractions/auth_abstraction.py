"""
Auth Abstraction - Business Logic Implementation (Layer 1)

Implements authentication operations using Supabase adapter.
Provides user authentication, token validation, and user management.

WHAT (Infrastructure Role): I provide authentication services
HOW (Infrastructure Implementation): I use Supabase adapter with business logic
"""

from typing import Dict, Any, Optional

from utilities import get_logger, get_clock, generate_session_id
from utilities.errors import DomainError
from ..protocols.auth_protocol import AuthenticationProtocol, SecurityContext
from ..adapters.supabase_adapter import SupabaseAdapter


class AuthenticationError(DomainError):
    """Authentication error exception."""
    pass


class AuthAbstraction(AuthenticationProtocol):
    """
    Authentication abstraction with business logic.
    
    Implements authentication operations using Supabase adapter.
    Provides user authentication, token validation, and user management.
    """
    
    def __init__(self, supabase_adapter: SupabaseAdapter):
        """
        Initialize Auth abstraction with Supabase adapter.
        
        Args:
            supabase_adapter: Supabase adapter (Layer 0)
        """
        self.supabase = supabase_adapter
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("Auth Abstraction initialized")
    
    async def authenticate(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[SecurityContext]:
        """
        Authenticate user using Supabase adapter.
        
        Args:
            credentials: Authentication credentials (email, password)
        
        Returns:
            Optional[SecurityContext]: User session or None if failed
        """
        try:
            email = credentials.get("email")
            password = credentials.get("password")
            
            if not email or not password:
                raise AuthenticationError("Email and password are required")
            
            # Use Supabase adapter
            result = await self.supabase.sign_in_with_password(email, password)
            
            if not result.get("success"):
                raise AuthenticationError(f"Authentication failed: {result.get('error')}")
            
            user_data = result.get("user", {})
            session_data = result.get("session", {})
            
            # Extract user information
            user_id = user_data.get("id")
            email = user_data.get("email", "")
            
            # Check tenant status - query user_tenants table first
            tenant_info = await self.supabase.get_user_tenant_info(user_id)
            tenant_id = tenant_info.get("tenant_id")
            
            # If no tenant_id from database, check user_metadata as fallback
            if not tenant_id:
                tenant_id = user_data.get("user_metadata", {}).get("tenant_id")
            
            # If still no tenant, create one automatically
            if not tenant_id:
                self.logger.warning(f"User {user_id} has no tenant - creating default tenant")
                try:
                    tenant_result = await self._create_tenant_for_user(
                        user_id=user_id,
                        tenant_type="individual",
                        tenant_name=f"Tenant for {email or user_id}",
                        email=email
                    )
                    
                    if tenant_result.get("success"):
                        tenant_id = tenant_result.get("tenant_id")
                        # Link user to tenant with owner role
                        link_result = await self.supabase.link_user_to_tenant(
                            user_id=user_id,
                            tenant_id=tenant_id,
                            role="owner",
                            is_primary=True
                        )
                        if link_result.get("success"):
                            self.logger.info(f"Created and linked tenant {tenant_id} for user {user_id}")
                            # Re-fetch tenant info to get permissions
                            tenant_info = await self.supabase.get_user_tenant_info(user_id)
                        else:
                            self.logger.warning(f"Tenant created but linking failed: {link_result.get('error')}")
                    else:
                        self.logger.error(f"Failed to create tenant for user {user_id}: {tenant_result.get('error')}")
                except Exception as tenant_error:
                    self.logger.error(f"Error creating tenant for user {user_id}: {tenant_error}", exc_info=True)
                    # Continue without tenant - graceful degradation
            
            # Get roles and permissions from tenant info (if available)
            if tenant_info and tenant_info.get("tenant_id"):
                roles = tenant_info.get("roles", [])
                permissions = tenant_info.get("permissions", [])
            else:
                # Fallback to user_metadata if tenant_info not available
                roles = user_data.get("user_metadata", {}).get("roles", [])
                permissions = user_data.get("user_metadata", {}).get("permissions", [])
            
            # Create security context
            context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                roles=roles if isinstance(roles, list) else [roles] if roles else [],
                permissions=permissions if isinstance(permissions, list) else [permissions] if permissions else [],
                origin="supabase_auth"
            )
            
            self.logger.info(f"User authenticated: {user_id}, tenant: {tenant_id}, permissions: {len(context.permissions)}")
            
            return context
            
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}", exc_info=True)
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    async def validate_token(
        self,
        token: str
    ) -> Optional[SecurityContext]:
        """
        Validate token using Supabase JWKS local verification (fast, no network calls).
        
        Falls back to network validation if JWKS is unavailable.
        
        Args:
            token: Authentication token
        
        Returns:
            Optional[SecurityContext]: User context or None if invalid
        """
        try:
            self.logger.info("Starting token validation (JWKS)...")
            
            # Use local JWT verification via JWKS (fast, no network calls)
            if hasattr(self.supabase, 'validate_token_local'):
                self.logger.info("Using local JWKS validation...")
                result = await self.supabase.validate_token_local(token)
            else:
                # Fallback to network call if local verification not available
                self.logger.warning("Local token validation not available, using network call")
                result = await self.supabase.get_user(token)
            
            if not result.get("success"):
                error_message = result.get("error", "Unknown error")
                self.logger.error(f"Token validation failed: {error_message}")
                raise AuthenticationError(f"Token validation failed: {error_message}")
            
            self.logger.info("Token validation succeeded (JWKS)")
            
            user_data = result.get("user", {})
            
            # Extract user information
            user_id = user_data.get("id")
            email = user_data.get("email", "")
            
            # Check tenant status - query user_tenants table first
            tenant_info = await self.supabase.get_user_tenant_info(user_id)
            tenant_id = tenant_info.get("tenant_id")
            
            # If no tenant_id from database, check user_data/user_metadata as fallback
            if not tenant_id:
                tenant_id = user_data.get("tenant_id") or user_data.get("user_metadata", {}).get("tenant_id")
            
            # If still no tenant, create one automatically
            if not tenant_id:
                self.logger.warning(f"User {user_id} has no tenant - creating default tenant")
                try:
                    tenant_result = await self._create_tenant_for_user(
                        user_id=user_id,
                        tenant_type="individual",
                        tenant_name=f"Tenant for {email or user_id}",
                        email=email
                    )
                    
                    if tenant_result.get("success"):
                        tenant_id = tenant_result.get("tenant_id")
                        # Link user to tenant with owner role
                        link_result = await self.supabase.link_user_to_tenant(
                            user_id=user_id,
                            tenant_id=tenant_id,
                            role="owner",
                            is_primary=True
                        )
                        if link_result.get("success"):
                            self.logger.info(f"Created and linked tenant {tenant_id} for user {user_id}")
                            # Re-fetch tenant info to get permissions
                            tenant_info = await self.supabase.get_user_tenant_info(user_id)
                        else:
                            self.logger.warning(f"Tenant created but linking failed: {link_result.get('error')}")
                    else:
                        self.logger.error(f"Failed to create tenant for user {user_id}: {tenant_result.get('error')}")
                except Exception as tenant_error:
                    self.logger.error(f"Error creating tenant for user {user_id}: {tenant_error}", exc_info=True)
                    # Continue without tenant - graceful degradation
            
            # Get roles and permissions from tenant info (if available)
            if tenant_info and tenant_info.get("tenant_id"):
                roles = tenant_info.get("roles", [])
                permissions = tenant_info.get("permissions", [])
            else:
                # Fallback to user_data if tenant_info not available
                roles = user_data.get("roles", [])
                permissions = user_data.get("permissions", [])
            
            if not permissions:
                self.logger.warning(f"No permissions found for user_id: {user_id}")
            
            # Create security context
            context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                roles=roles if isinstance(roles, list) else [roles] if roles else [],
                permissions=permissions if isinstance(permissions, list) else [permissions] if permissions else [],
                origin="supabase_validation"
            )
            
            self.logger.info(f"Token validated for user: {user_id}, tenant: {tenant_id}, permissions: {len(context.permissions)}")
            
            return context
            
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Token validation error: {str(e)}", exc_info=True)
            raise AuthenticationError(f"Token validation failed: {str(e)}")
    
    async def refresh_token(
        self,
        refresh_token: str
    ) -> Optional[SecurityContext]:
        """
        Refresh token using Supabase adapter.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Optional[SecurityContext]: New user session or None if failed
        """
        try:
            # Use Supabase adapter to refresh token
            result = await self.supabase.refresh_session(refresh_token)
            
            if not result.get("success"):
                raise AuthenticationError(f"Token refresh failed: {result.get('error')}")
            
            user_data = result.get("user", {})
            session_data = result.get("session", {})
            
            # Extract user information
            user_id = user_data.get("id")
            tenant_id = user_data.get("user_metadata", {}).get("tenant_id")
            roles = user_data.get("user_metadata", {}).get("roles", [])
            permissions = user_data.get("user_metadata", {}).get("permissions", [])
            
            # Create security context
            context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                email=user_data.get("email"),
                roles=roles if isinstance(roles, list) else [roles] if roles else [],
                permissions=permissions if isinstance(permissions, list) else [permissions] if permissions else [],
                origin="supabase_refresh"
            )
            
            self.logger.info(f"Token refreshed for user: {user_id}")
            
            return context
            
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Token refresh error: {str(e)}", exc_info=True)
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    async def get_user_context(self, token: str) -> SecurityContext:
        """
        Get user/tenant context via Supabase API.
        
        Use case: ForwardAuth endpoint (needs user context in headers)
        
        Args:
            token: Authentication token
        
        Returns:
            SecurityContext: User context
        """
        try:
            self.logger.info("Getting user context (Supabase API)...")
            
            # Infrastructure logic: Supabase API call
            result = await self.supabase.get_user(token)
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"User context failed: {error_msg}")
                raise AuthenticationError(f"User context failed: {error_msg}")
            
            self.logger.info("User context retrieved (Supabase API)")
            
            # Infrastructure logic: Extract user info
            user_data = result.get("user", {})
            user_id = user_data.get("id")
            email = user_data.get("email") or ""
            user_metadata = user_data.get("user_metadata", {})
            
            # Infrastructure logic: Extract tenant info
            tenant_id = (
                user_data.get("tenant_id") or
                user_metadata.get("tenant_id") or
                None
            )
            
            # Infrastructure logic: Extract roles/permissions
            roles = user_data.get("roles", [])
            permissions = user_data.get("permissions", [])
            
            # Fallback to user_metadata if database query didn't return tenant info
            if not tenant_id:
                tenant_id = user_metadata.get("tenant_id")
            if not roles:
                roles = user_metadata.get("roles", [])
            if not permissions:
                permissions = user_metadata.get("permissions", [])
            
            # Return clean SecurityContext
            context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                roles=roles if isinstance(roles, list) else [roles] if roles else [],
                permissions=permissions if isinstance(permissions, list) else [permissions] if permissions else [],
                origin="supabase_user_context"
            )
            
            self.logger.info(f"User context retrieved: user={user_id}, tenant={tenant_id}")
            return context
            
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"User context error: {e}", exc_info=True)
            raise AuthenticationError(f"Failed to get user context: {str(e)}")
    
    async def logout_user(self, token: str) -> bool:
        """Logout user using Supabase adapter."""
        try:
            result = await self.supabase.sign_out(token)
            
            if not result.get("success"):
                self.logger.warning(f"Logout failed: {result.get('error')}")
            
            self.logger.info("User logged out successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Logout error: {str(e)}", exc_info=True)
            raise AuthenticationError(f"Logout failed: {str(e)}")
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information using Supabase adapter."""
        try:
            result = await self.supabase.admin_get_user(user_id)
            
            if not result.get("success"):
                raise AuthenticationError(f"Failed to get user info: {result.get('error')}")
            
            user_data = result.get("user", {})
            
            return {
                "user_id": user_data.get("id"),
                "email": user_data.get("email"),
                "tenant_id": user_data.get("user_metadata", {}).get("tenant_id"),
                "roles": user_data.get("user_metadata", {}).get("roles", []),
                "permissions": user_data.get("user_metadata", {}).get("permissions", []),
                "created_at": user_data.get("created_at"),
                "last_sign_in": user_data.get("last_sign_in_at")
            }
            
        except Exception as e:
            self.logger.error(f"Get user info error: {str(e)}", exc_info=True)
            raise AuthenticationError(f"Failed to get user info: {str(e)}")
    
    async def update_user_metadata(self, user_id: str, metadata: Dict[str, Any]) -> bool:
        """Update user metadata using Supabase adapter."""
        try:
            result = await self.supabase.admin_update_user(user_id, {"user_metadata": metadata})
            
            if not result.get("success"):
                self.logger.warning(f"Failed to update user metadata: {result.get('error')}")
            
            self.logger.info(f"User metadata updated for user: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Update user metadata error: {str(e)}", exc_info=True)
            raise AuthenticationError(f"Failed to update user metadata: {str(e)}")
    
    async def register_user(self, credentials: Dict[str, Any]) -> SecurityContext:
        """
        Register new user and create/assign tenant (server-side).
        
        Creates tenant server-side during registration instead of
        relying on client-side tenant ID generation.
        """
        try:
            email = credentials.get("email")
            password = credentials.get("password")
            tenant_type = credentials.get("tenant_type", "individual")
            tenant_name = credentials.get("tenant_name", f"Tenant for {email}")
            user_metadata = credentials.get("user_metadata", {})
            
            if not email or not password:
                raise AuthenticationError("Email and password are required")
            
            # Step 1: Create user in Supabase Auth
            result = await self.supabase.sign_up_with_password(
                email=email,
                password=password,
                user_metadata={
                    **user_metadata,
                    "full_name": credentials.get("name", ""),
                    "tenant_type": tenant_type
                }
            )
            
            if not result.get("success"):
                raise AuthenticationError(f"Registration failed: {result.get('error')}")
            
            user_data = result.get("user", {})
            user_id = user_data.get("id")
            
            if not user_id:
                raise AuthenticationError("User created but no user ID returned")
            
            # Step 2: Create tenant (server-side, using service key)
            tenant_result = await self._create_tenant_for_user(
                user_id=user_id,
                tenant_type=tenant_type,
                tenant_name=tenant_name,
                email=email
            )
            
            if not tenant_result.get("success"):
                self.logger.error(f"Failed to create tenant for user {user_id}")
                raise AuthenticationError("Registration succeeded but tenant creation failed")
            
            tenant_id = tenant_result.get("tenant_id")
            
            # Step 3: Link user to tenant
            link_result = await self.supabase.link_user_to_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
                role="owner",
                is_primary=True
            )
            
            if not link_result.get("success"):
                self.logger.warning(f"Failed to link user {user_id} to tenant {tenant_id}")
            
            # Step 4: Update user metadata with tenant_id
            update_result = await self.supabase.admin_update_user(user_id, {
                "user_metadata": {
                    **user_metadata,
                    "tenant_id": tenant_id,
                    "primary_tenant_id": tenant_id,
                    "tenant_type": tenant_type,
                    "full_name": credentials.get("name", "")
                }
            })
            
            if not update_result.get("success"):
                self.logger.warning(f"Failed to update user metadata for {user_id}")
            
            # Step 5: Create security context
            context = SecurityContext(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                roles=["owner"],
                permissions=["read", "write", "admin", "delete"],
                origin="supabase_registration"
            )
            
            self.logger.info(f"User registered with tenant: {user_id} -> {tenant_id}")
            
            return context
            
        except AuthenticationError:
            raise
        except Exception as e:
            self.logger.error(f"Registration error: {str(e)}", exc_info=True)
            raise AuthenticationError(f"Registration failed: {str(e)}")
    
    async def _create_tenant_for_user(self, user_id: str, tenant_type: str, tenant_name: str, email: str) -> Dict[str, Any]:
        """Create tenant for a new user (server-side only)."""
        try:
            # Generate unique slug using session ID generator
            slug = f"tenant-{user_id[:8]}-{generate_session_id()[:8]}"
            
            tenant_data = {
                "name": tenant_name,
                "slug": slug,
                "type": tenant_type,
                "owner_id": user_id,
                "status": "active",
                "metadata": {
                    "created_by": user_id,
                    "created_for": email
                }
            }
            
            result = await self.supabase.create_tenant(tenant_data)
            
            if not result.get("success"):
                self.logger.error(f"Tenant creation failed: {result.get('error')}")
                return result
            
            self.logger.info(f"Tenant created: {result.get('tenant_id')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating tenant: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "tenant_creation_error"
            }
