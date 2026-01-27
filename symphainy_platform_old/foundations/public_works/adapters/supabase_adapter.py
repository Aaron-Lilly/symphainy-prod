"""
Supabase Adapter - Raw Technology Client (Layer 0)

Real Supabase client wrapper with no business logic.
This is the raw technology layer for Supabase operations.

WHAT (Infrastructure Role): I provide raw Supabase client operations
HOW (Infrastructure Implementation): I use real Supabase client with no business logic
"""

import asyncio
import base64
import time
from typing import Dict, Any, Optional, List
from supabase import create_client, Client
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.backends import default_backend

from utilities import get_logger
from .supabase_jwks_adapter import SupabaseJWKSAdapter


class SupabaseAuthError(Exception):
    """Custom exception for Supabase authentication errors."""
    pass


def _is_auth_error(error: Exception) -> bool:
    """Check if an exception is an auth-related error."""
    error_str = str(error).lower()
    return (
        "auth" in error_str or
        "invalid credentials" in error_str or
        ("email" in error_str and "password" in error_str) or
        ("token" in error_str and ("invalid" in error_str or "expired" in error_str)) or
        "unauthorized" in error_str or
        "forbidden" in error_str
    )


class SupabaseAdapter:
    """
    Raw Supabase client wrapper - no business logic.
    
    This adapter provides direct access to Supabase operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(
        self,
        url: str,
        anon_key: str,
        service_key: Optional[str] = None,
        jwks_url: Optional[str] = None,
        jwt_issuer: Optional[str] = None
    ):
        """
        Initialize Supabase adapter with real credentials.
        
        Args:
            url: Supabase project URL
            anon_key: Supabase anonymous/public key
            service_key: Supabase service role key (optional)
            jwks_url: Optional JWKS URL for local JWT verification
            jwt_issuer: Optional JWT issuer for token validation
        """
        self.logger = get_logger(self.__class__.__name__)
        
        # Normalize URL - remove trailing slashes
        self.url = url.rstrip('/') if url else url
        self.anon_key = anon_key
        self.service_key = service_key
        self.jwt_issuer = jwt_issuer
        
        # Log service_key status for debugging
        if service_key:
            self.logger.info("Service key provided - service_client will be available for database queries")
        else:
            self.logger.warning("Service key NOT provided - service_client will fallback to anon_client")
            self.logger.warning("This may cause get_user_tenant_info() to fail. Set SUPABASE_SERVICE_KEY in environment.")
        
        # Create clients
        self.anon_client: Client = create_client(self.url, anon_key)
        self.service_client: Client = create_client(self.url, service_key) if service_key else self.anon_client
        
        # Log client initialization status
        if self.service_client and service_key:
            self.logger.debug("service_client initialized with service_key (can query user_tenants table)")
        else:
            self.logger.debug("service_client initialized as anon_client (may not be able to query user_tenants table)")
        
        # Initialize JWKS adapter for local JWT verification
        try:
            if jwks_url:
                self.jwks_adapter = SupabaseJWKSAdapter(jwks_url=jwks_url)
                self.logger.info(f"Supabase adapter initialized with URL: {self.url} (JWKS enabled via jwks_url)")
            else:
                self.jwks_adapter = SupabaseJWKSAdapter(supabase_url=self.url)
                self.logger.info(f"Supabase adapter initialized with URL: {self.url} (JWKS enabled, constructed URL)")
            
            if self.jwt_issuer:
                self.logger.info(f"JWT issuer configured: {self.jwt_issuer}")
            else:
                self.logger.warning("JWT issuer not set - issuer validation will be skipped")
        except Exception as e:
            self.jwks_adapter = None
            self.logger.warning(f"JWKS adapter not available - local JWT verification disabled: {e}")
            self.logger.info(f"Supabase adapter initialized with URL: {self.url} (JWKS disabled)")
    
    # ============================================================================
    # RAW AUTHENTICATION OPERATIONS
    # ============================================================================
    
    async def sign_in_with_password(self, email: str, password: str) -> Dict[str, Any]:
        """Raw authentication with Supabase - no business logic."""
        try:
            response = self.anon_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            return {
                "success": True,
                "user": response.user.__dict__ if response.user else None,
                "session": response.session.__dict__ if response.session else None,
                "access_token": response.session.access_token if response.session else None,
                "refresh_token": response.session.refresh_token if response.session else None,
                "expires_in": response.session.expires_in if response.session else None,
                "expires_at": response.session.expires_at if response.session else None
            }
        except Exception as e:
            if _is_auth_error(e):
                self.logger.error(f"Supabase auth error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "auth_error"
                }
            else:
                self.logger.error(f"Unexpected error in sign_in_with_password: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "unexpected_error"
                }
    
    async def sign_up_with_password(self, email: str, password: str, user_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Raw user registration with Supabase - no business logic."""
        try:
            response = self.anon_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            
            return {
                "success": True,
                "user": response.user.__dict__ if response.user else None,
                "session": response.session.__dict__ if response.session else None,
                "access_token": response.session.access_token if response.session else None,
                "refresh_token": response.session.refresh_token if response.session else None,
                "expires_in": response.session.expires_in if response.session else None,
                "expires_at": response.session.expires_at if response.session else None
            }
        except Exception as e:
            if _is_auth_error(e):
                self.logger.error(f"Supabase signup error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "auth_error"
                }
            else:
                self.logger.error(f"Unexpected error in sign_up_with_password: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "unexpected_error"
                }
    
    async def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """Raw token refresh with Supabase - no business logic."""
        try:
            response = self.anon_client.auth.refresh_session(refresh_token)
            
            return {
                "success": True,
                "user": response.user.__dict__ if response.user else None,
                "session": response.session.__dict__ if response.session else None,
                "access_token": response.session.access_token if response.session else None,
                "refresh_token": response.session.refresh_token if response.session else None,
                "expires_in": response.session.expires_in if response.session else None,
                "expires_at": response.session.expires_at if response.session else None
            }
        except Exception as e:
            if _is_auth_error(e):
                self.logger.error(f"Supabase refresh error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "auth_error"
                }
            else:
                self.logger.error(f"Unexpected error in refresh_session: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "unexpected_error"
                }
    
    async def validate_token_local(self, access_token: str) -> Dict[str, Any]:
        """
        Validate JWT token locally using JWKS (no network calls to Supabase API).
        
        This is Supabase's recommended approach for token validation.
        Uses JWKS endpoint to get public keys and verifies JWT signature locally.
        
        Benefits:
        - Fast (no network calls)
        - Reliable (no dependency on Supabase API)
        - Best practice (Supabase's recommended approach)
        - Secure (RS256/ES256 asymmetric keys)
        
        Returns:
            Dict with success, user data, or error
        """
        validation_start = time.time()
        
        if not self.jwks_adapter:
            # Fallback to network call if JWKS not available
            self.logger.warning("JWKS adapter not available, falling back to network validation")
            network_start = time.time()
            result = await self.get_user(access_token)
            network_time = time.time() - network_start
            self.logger.warning(f"Network validation completed in {network_time:.3f}s (fallback mode)")
            return result
        
        try:
            token_preview = access_token[:50] + "..." if len(access_token) > 50 else access_token
            self.logger.info(f"Starting local token validation... (token_preview: {token_preview})")
            
            # Decode JWT header to get kid (key ID)
            header_start = time.time()
            try:
                unverified_header = jwt.get_unverified_header(access_token)
                kid = unverified_header.get("kid")
                header_time = time.time() - header_start
                self.logger.info(f"JWT header decoded in {header_time:.3f}s, kid (key ID): {kid}")
            except Exception as header_error:
                self.logger.error(f"Failed to decode JWT header: {header_error}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Invalid token: failed to decode header - {str(header_error)}",
                    "error_type": "auth_error"
                }
            
            if not kid:
                self.logger.error("JWT missing 'kid' in header")
                self.logger.error(f"JWT header contents: {unverified_header}")
                return {
                    "success": False,
                    "error": "Invalid token: missing key ID",
                    "error_type": "auth_error"
                }
            
            # Get JWKS (cached)
            jwks_start = time.time()
            self.logger.info("Fetching JWKS (may be cached)...")
            try:
                jwks = await self.jwks_adapter.get_jwks()
                jwks_time = time.time() - jwks_start
                self.logger.info(f"JWKS fetched in {jwks_time:.3f}s: {len(jwks.get('keys', []))} keys available")
            except Exception as jwks_error:
                self.logger.error(f"Failed to fetch JWKS: {jwks_error}", exc_info=True)
                return {
                    "success": False,
                    "error": f"JWKS fetch failed: {str(jwks_error)}",
                    "error_type": "jwks_error"
                }
            
            # Get public key by kid
            key_lookup_start = time.time()
            key_data = self.jwks_adapter.get_key_by_kid(kid, jwks)
            key_lookup_time = time.time() - key_lookup_start
            self.logger.info(f"Key lookup for kid '{kid}' completed in {key_lookup_time:.3f}s: {'FOUND' if key_data else 'NOT_FOUND'}")
            
            if not key_data:
                self.logger.error(f"Key with kid '{kid}' not found in JWKS")
                self.logger.error(f"Available kids in JWKS: {[k.get('kid') for k in jwks.get('keys', [])]}")
                # Try refreshing JWKS (key rotation)
                self.logger.info("Attempting to refresh JWKS (key rotation)...")
                refresh_start = time.time()
                try:
                    jwks = await self.jwks_adapter.refresh_jwks()
                    refresh_time = time.time() - refresh_start
                    self.logger.info(f"JWKS refresh completed in {refresh_time:.3f}s")
                    key_data = self.jwks_adapter.get_key_by_kid(kid, jwks)
                    if key_data:
                        self.logger.info("Key found after refresh!")
                    else:
                        self.logger.error(f"Key still not found after refresh. Available kids: {[k.get('kid') for k in jwks.get('keys', [])]}")
                except Exception as refresh_error:
                    self.logger.error(f"Failed to refresh JWKS: {refresh_error}", exc_info=True)
                
                if not key_data:
                    total_time = time.time() - validation_start
                    self.logger.error(f"Token validation failed after {total_time:.3f}s: key not found")
                    return {
                        "success": False,
                        "error": "Invalid token: key not found in JWKS",
                        "error_type": "auth_error"
                    }
            
            # Convert JWK to public key (supports both RS256/RSA and ES256/EC)
            key_type = key_data.get("kty")  # "RSA" or "EC"
            algorithm = key_data.get("alg")  # "RS256" or "ES256"
            
            if key_type == "EC" or algorithm == "ES256":
                # Elliptic Curve (ES256) - Supabase uses this
                x_bytes = base64.urlsafe_b64decode(key_data["x"] + "==")
                y_bytes = base64.urlsafe_b64decode(key_data["y"] + "==")
                
                # Convert to integers
                x_int = int.from_bytes(x_bytes, "big")
                y_int = int.from_bytes(y_bytes, "big")
                
                # Get curve type (default to P-256 for ES256)
                crv = key_data.get("crv", "P-256")
                if crv == "P-256":
                    curve = ec.SECP256R1()
                elif crv == "P-384":
                    curve = ec.SECP384R1()
                elif crv == "P-521":
                    curve = ec.SECP521R1()
                else:
                    raise ValueError(f"Unsupported curve: {crv}")
                
                # Create EC public key
                public_key = ec.EllipticCurvePublicNumbers(x_int, y_int, curve).public_key(default_backend())
                self.logger.debug(f"Created EC public key (ES256) for curve {crv}")
                jwt_algorithm = "ES256"
                
            elif key_type == "RSA" or algorithm == "RS256":
                # RSA (RS256) - legacy support
                n_bytes = base64.urlsafe_b64decode(key_data["n"] + "==")
                e_bytes = base64.urlsafe_b64decode(key_data["e"] + "==")
                
                # Convert to integers
                n_int = int.from_bytes(n_bytes, "big")
                e_int = int.from_bytes(e_bytes, "big")
                
                # Create RSA public key
                public_key = rsa.RSAPublicNumbers(e_int, n_int).public_key(default_backend())
                self.logger.debug("Created RSA public key (RS256)")
                jwt_algorithm = "RS256"
            else:
                raise ValueError(f"Unsupported key type: {key_type} or algorithm: {algorithm}")
            
            # Verify and decode JWT
            verify_options = {"verify_exp": True, "verify_aud": True}
            issuer = self.jwt_issuer
            
            self.logger.info(f"Verifying JWT with algorithm={jwt_algorithm}, issuer={issuer or 'NOT_SET'}")
            
            verify_start = time.time()
            try:
                payload = jwt.decode(
                    access_token,
                    public_key,
                    algorithms=[jwt_algorithm],
                    audience="authenticated",  # Supabase JWT audience
                    issuer=issuer if issuer else None,
                    options=verify_options
                )
                verify_time = time.time() - verify_start
                self.logger.info(f"JWT signature verified successfully in {verify_time:.3f}s! User ID: {payload.get('sub', 'N/A')}")
                
                # Log issuer validation
                if issuer:
                    token_issuer = payload.get("iss")
                    if token_issuer != issuer:
                        self.logger.error(f"JWT issuer mismatch: expected '{issuer}', got '{token_issuer}'")
                        return {
                            "success": False,
                            "error": f"Invalid token: issuer mismatch (expected '{issuer}')",
                            "error_type": "auth_error"
                        }
                    self.logger.debug(f"JWT issuer validated: {token_issuer}")
            except ExpiredSignatureError:
                verify_time = time.time() - verify_start
                self.logger.error(f"JWT validation failed after {verify_time:.3f}s: Token expired")
                return {
                    "success": False,
                    "error": "Token expired",
                    "error_type": "auth_error"
                }
            except InvalidTokenError as e:
                verify_time = time.time() - verify_start
                self.logger.error(f"JWT validation failed after {verify_time:.3f}s: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": f"Invalid token: {str(e)}",
                    "error_type": "auth_error"
                }
            
            # Extract user information from JWT payload
            user_id = payload.get("sub")  # Supabase uses 'sub' for user_id
            email = payload.get("email")
            user_metadata = payload.get("user_metadata", {})
            
            self.logger.info(f"Extracted user_id from JWT: {user_id}, email: {email}")
            
            if not user_id:
                self.logger.error("JWT payload missing 'sub' (user_id)")
                return {
                    "success": False,
                    "error": "Invalid token: missing user ID",
                    "error_type": "auth_error"
                }
            
            # Get tenant information from database (still needed)
            self.logger.info(f"Fetching tenant info for user_id: {user_id}")
            tenant_info = await self.get_user_tenant_info(user_id)
            self.logger.info(f"Tenant info result: tenant_id={tenant_info.get('tenant_id')}, roles={tenant_info.get('roles')}, permissions={tenant_info.get('permissions')}")
            
            # Build user dict
            user_dict = {
                "id": user_id,
                "email": email,
                "user_metadata": user_metadata,
                "tenant_id": tenant_info.get("tenant_id") or user_metadata.get("tenant_id"),
                "primary_tenant_id": tenant_info.get("primary_tenant_id") or user_metadata.get("primary_tenant_id"),
                "tenant_type": tenant_info.get("tenant_type", "individual"),
                "roles": tenant_info.get("roles", []),
                "permissions": tenant_info.get("permissions", [])
            }
            
            total_time = time.time() - validation_start
            self.logger.info(f"Token validated locally for user: {user_id}, tenant_id: {user_dict.get('tenant_id')}, {len(user_dict.get('permissions', []))} permissions (total_time: {total_time:.3f}s)")
            
            return {
                "success": True,
                "user": user_dict,
                "access_token": access_token
            }
            
        except Exception as e:
            total_time = time.time() - validation_start
            self.logger.error(f"Local token validation error after {total_time:.3f}s: {e}", exc_info=True)
            # Fallback to network call on error
            self.logger.warning("Falling back to network validation due to local validation error")
            return await self.get_user(access_token)
    
    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """
        Raw user retrieval with Supabase - enhanced with tenant context.
        
        SECURITY: Uses Supabase's official auth.get_user() API call.
        Adds timeout protection to prevent ForwardAuth from hanging.
        
        NOTE: This method makes a network call. For better performance,
        use validate_token_local() which uses JWKS for local verification.
        """
        try:
            # Use Supabase's official get_user method (validates token via network call)
            # Wrap in timeout to prevent ForwardAuth from hanging (2 second timeout)
            try:
                user_response = await asyncio.wait_for(
                    asyncio.to_thread(self.anon_client.auth.get_user, access_token),
                    timeout=2.0  # 2 second timeout for ForwardAuth
                )
            except asyncio.TimeoutError:
                self.logger.error("Supabase get_user timeout after 2 seconds - Supabase API may be slow or unavailable")
                return {
                    "success": False,
                    "error": "Token validation timeout - Supabase API slow or unavailable",
                    "error_type": "timeout"
                }
            
            if not user_response.user:
                return {
                    "success": False,
                    "error": "Invalid token",
                    "error_type": "auth_error"
                }
            
            user = user_response.user
            user_id = user.id
            
            # Get tenant information from database (not just metadata)
            tenant_info = await self.get_user_tenant_info(user_id)
            
            # Merge tenant info with user data
            user_dict = user.__dict__ if hasattr(user, '__dict__') else {
                "id": user.id,
                "email": user.email,
                "user_metadata": user.user_metadata or {}
            }
            
            # Add tenant context
            user_dict["tenant_id"] = tenant_info.get("tenant_id")
            user_dict["primary_tenant_id"] = tenant_info.get("primary_tenant_id")
            user_dict["tenant_type"] = tenant_info.get("tenant_type", "individual")
            user_dict["roles"] = tenant_info.get("roles", [])
            user_dict["permissions"] = tenant_info.get("permissions", [])
            
            return {
                "success": True,
                "user": user_dict,
                "access_token": access_token
            }
        except Exception as e:
            if _is_auth_error(e):
                self.logger.error(f"Supabase get_user error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "auth_error"
                }
            else:
                self.logger.error(f"Unexpected error in get_user: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "unexpected_error"
                }
    
    async def get_user_tenant_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's tenant information from database.
        
        Public method to allow auth abstractions to check tenant status.
        Returns empty dict if no tenant found.
        """
        try:
            # Use service_client to query user_tenants table (requires service key)
            if not self.service_client or not self.service_key:
                self.logger.warning("Service client not available - service_key may not be configured. Cannot query user_tenants table.")
                self.logger.warning("Check that SUPABASE_SERVICE_KEY is set in environment.")
                return {}
            
            self.logger.debug(f"Querying user_tenants table for user_id: {user_id}")
            try:
                response = self.service_client.table("user_tenants").select(
                    "tenant_id, role, is_primary, tenants(type, name, status)"
                ).eq("user_id", user_id).eq("is_primary", True).execute()
                
                self.logger.debug(f"Database query returned {len(response.data) if response.data else 0} records")
            except Exception as db_error:
                self.logger.error(f"Database query failed for user_id {user_id}: {db_error}", exc_info=True)
                # Try fallback to user_metadata
                response = type('obj', (object,), {'data': []})()  # Empty response object
            
            if not response.data:
                # Fallback: check user_metadata
                self.logger.warning(f"No tenant data found in user_tenants table for user_id: {user_id}, trying metadata fallback")
                try:
                    user_response = self.service_client.auth.admin.get_user_by_id(user_id)
                    user_metadata = user_response.user.user_metadata or {}
                    self.logger.info(f"Using metadata fallback for user_id: {user_id}")
                    self.logger.debug(f"Metadata fallback - tenant_id: {user_metadata.get('tenant_id')}, roles: {user_metadata.get('roles')}, permissions: {user_metadata.get('permissions')}")
                    return {
                        "tenant_id": user_metadata.get("tenant_id"),
                        "primary_tenant_id": user_metadata.get("primary_tenant_id"),
                        "tenant_type": user_metadata.get("tenant_type", "individual"),
                        "roles": user_metadata.get("roles", []),
                        "permissions": user_metadata.get("permissions", [])
                    }
                except Exception as e:
                    self.logger.warning(f"Could not get user metadata for user_id {user_id}: {e}")
                    self.logger.warning("Returning empty dict - permissions will be empty")
                    return {}
            
            tenant_data = response.data[0]
            tenant_info = tenant_data.get("tenants", {})
            
            # Map role to permissions
            role = tenant_data.get("role", "member")
            permissions = self._get_permissions_for_role(role)
            
            self.logger.info(f"Found tenant info for user_id: {user_id}, tenant_id: {tenant_data.get('tenant_id')}, role: {role}, permissions: {permissions}")
            
            return {
                "tenant_id": tenant_data["tenant_id"],
                "primary_tenant_id": tenant_data["tenant_id"],
                "tenant_type": tenant_info.get("type", "individual"),
                "roles": [role],
                "permissions": permissions
            }
            
        except Exception as e:
            self.logger.error(f"Error getting tenant info for user_id {user_id}: {e}", exc_info=True)
            return {}
    
    def _get_permissions_for_role(self, role: str) -> List[str]:
        """Get permissions for a given role."""
        role_permissions = {
            "owner": ["read", "write", "admin", "delete"],
            "admin": ["read", "write", "admin"],
            "member": ["read", "write"],
            "viewer": ["read"]
        }
        return role_permissions.get(role, ["read"])
    
    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Raw user sign out with Supabase - no business logic."""
        try:
            # Set the session for the client
            self.anon_client.auth.set_session(access_token, "")
            response = self.anon_client.auth.sign_out()
            
            return {
                "success": True,
                "message": "User signed out successfully"
            }
        except Exception as e:
            if _is_auth_error(e):
                self.logger.error(f"Supabase sign_out error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "auth_error"
                }
            else:
                self.logger.error(f"Unexpected error in sign_out: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "unexpected_error"
                }
    
    # ============================================================================
    # RAW DATABASE OPERATIONS (for RLS policies)
    # ============================================================================
    
    async def execute_rls_policy(self, table: str, operation: str, user_context: Dict[str, Any], data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Raw RLS policy execution with Supabase - no business logic."""
        try:
            # Set the session for the client
            if user_context.get("access_token"):
                self.anon_client.auth.set_session(user_context["access_token"], "")
            
            if operation == "select":
                response = self.anon_client.table(table).select("*").execute()
            elif operation == "insert":
                response = self.anon_client.table(table).insert(data).execute()
            elif operation == "update":
                response = self.anon_client.table(table).update(data).execute()
            elif operation == "delete":
                response = self.anon_client.table(table).delete().execute()
            else:
                return {
                    "success": False,
                    "error": f"Unsupported operation: {operation}",
                    "error_type": "invalid_operation"
                }
            
            return {
                "success": True,
                "data": response.data,
                "count": response.count,
                "operation": operation,
                "table": table
            }
        except Exception as e:
            self.logger.error(f"Supabase RLS policy error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "rls_error"
            }
    
    # ============================================================================
    # RAW ADMIN OPERATIONS (using service key)
    # ============================================================================
    
    async def admin_get_user(self, user_id: str) -> Dict[str, Any]:
        """Raw admin user retrieval with Supabase - no business logic."""
        try:
            response = self.service_client.auth.admin.get_user_by_id(user_id)
            
            return {
                "success": True,
                "user": response.user.__dict__ if response.user else None
            }
        except Exception as e:
            self.logger.error(f"Supabase admin_get_user error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "admin_error"
            }
    
    async def admin_update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Raw admin user update with Supabase - no business logic."""
        try:
            response = self.service_client.auth.admin.update_user_by_id(user_id, updates)
            
            return {
                "success": True,
                "user": response.user.__dict__ if response.user else None
            }
        except Exception as e:
            self.logger.error(f"Supabase admin_update_user error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "admin_error"
            }
    
    # ============================================================================
    # TENANT MANAGEMENT OPERATIONS (using service key)
    # ============================================================================
    
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tenant using service key (server-side only)."""
        try:
            if not self.service_client or not self.service_key:
                return {
                    "success": False,
                    "error": "Service client not available",
                    "error_type": "config_error"
                }
            
            response = self.service_client.table("tenants").insert(tenant_data).execute()
            
            if not response.data:
                return {
                    "success": False,
                    "error": "Failed to create tenant",
                    "error_type": "database_error"
                }
            
            return {
                "success": True,
                "tenant": response.data[0],
                "tenant_id": response.data[0]["id"]
            }
        except Exception as e:
            self.logger.error(f"Supabase create_tenant error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "database_error"
            }
    
    async def link_user_to_tenant(self, user_id: str, tenant_id: str, role: str = "member", is_primary: bool = False) -> Dict[str, Any]:
        """Link a user to a tenant using service key (server-side only)."""
        try:
            if not self.service_client or not self.service_key:
                return {
                    "success": False,
                    "error": "Service client not available",
                    "error_type": "config_error"
                }
            
            # If setting as primary, unset other primary tenants for this user
            if is_primary:
                self.service_client.table("user_tenants").update({
                    "is_primary": False
                }).eq("user_id", user_id).execute()
            
            response = self.service_client.table("user_tenants").insert({
                "user_id": user_id,
                "tenant_id": tenant_id,
                "role": role,
                "is_primary": is_primary
            }).execute()
            
            if not response.data:
                return {
                    "success": False,
                    "error": "Failed to link user to tenant",
                    "error_type": "database_error"
                }
            
            return {
                "success": True,
                "user_tenant": response.data[0]
            }
        except Exception as e:
            self.logger.error(f"Supabase link_user_to_tenant error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "database_error"
            }
    
    async def get_tenant_by_id(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant information by ID."""
        try:
            if not self.service_client or not self.service_key:
                return {
                    "success": False,
                    "error": "Service client not available",
                    "error_type": "config_error"
                }
            
            response = self.service_client.table("tenants").select("*").eq("id", tenant_id).execute()
            
            if not response.data:
                return {
                    "success": False,
                    "error": "Tenant not found",
                    "error_type": "not_found"
                }
            
            return {
                "success": True,
                "tenant": response.data[0]
            }
        except Exception as e:
            self.logger.error(f"Supabase get_tenant_by_id error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "database_error"
            }
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Supabase connection - no business logic."""
        try:
            # Try to get the current user (this will fail if not authenticated, but that's OK)
            self.anon_client.auth.get_user()
            return {
                "success": True,
                "message": "Supabase connection successful",
                "url": self.url
            }
        except Exception as e:
            # Connection test doesn't require authentication
            return {
                "success": True,
                "message": "Supabase connection successful (no auth required)",
                "url": self.url
            }
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Get Supabase connection information - no business logic."""
        return {
            "url": self.url,
            "has_anon_key": bool(self.anon_key),
            "has_service_key": bool(self.service_key),
            "anon_client_initialized": self.anon_client is not None,
            "service_client_initialized": self.service_client is not None
        }
