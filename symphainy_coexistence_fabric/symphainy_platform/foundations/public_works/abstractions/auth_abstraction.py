"""
Auth Abstraction - Pure Infrastructure Implementation (Layer 1)

Implements authentication operations using Supabase adapter.
Returns raw data only - no business logic, no business objects.

WHAT (Infrastructure Role): I provide authentication services
HOW (Infrastructure Implementation): I use Supabase adapter and return raw data
"""

from typing import Dict, Any, Optional

from utilities import get_logger, get_clock
from utilities.errors import DomainError
from ..protocols.auth_protocol import AuthenticationProtocol
from ..adapters.supabase_adapter import SupabaseAdapter


class AuthenticationError(DomainError):
    """Authentication error exception."""
    pass


class AuthAbstraction(AuthenticationProtocol):
    """
    Authentication abstraction - pure infrastructure.
    
    Returns raw data only (Dict[str, Any]), not business objects.
    Business logic (SecurityContext creation, tenant creation, role extraction)
    belongs in Platform SDK, not here.
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
        
        self.logger.info("Auth Abstraction initialized (pure infrastructure)")
    
    async def authenticate(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user using Supabase adapter.
        
        Returns raw data only - no business logic, no SecurityContext.
        Platform SDK will translate this to SecurityContext.
        
        Args:
            credentials: Authentication credentials (email, password)
        
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
                "raw_user_data": Dict[str, Any],  # Full user data from Supabase
                "raw_session_data": Dict[str, Any],  # Full session data from Supabase
                "raw_user_metadata": Dict[str, Any],  # User metadata
                "raw_app_metadata": Dict[str, Any],  # App metadata
                "raw_provider_data": Dict[str, Any],  # Provider data
                "error": Optional[str]  # Error message if failed
            }
        """
        try:
            email = credentials.get("email")
            password = credentials.get("password")
            
            if not email or not password:
                raise AuthenticationError("Email and password are required")
            
            # Use Supabase adapter - pure infrastructure call
            result = await self.supabase.sign_in_with_password(email, password)
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Authentication failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": result.get("error_type", "auth_error")
                }
            
            # Extract raw data from Supabase response
            user_data = result.get("user", {})
            session_data = result.get("session", {})
            
            # Return raw data only - no business logic
            return {
                "success": True,
                "user_id": user_data.get("id"),
                "email": user_data.get("email", ""),
                "access_token": session_data.get("access_token"),
                "refresh_token": session_data.get("refresh_token"),
                "expires_in": session_data.get("expires_in"),
                "expires_at": session_data.get("expires_at"),
                "raw_user_data": user_data,  # Full user data
                "raw_session_data": session_data,  # Full session data
                "raw_user_metadata": user_data.get("user_metadata", {}),
                "raw_app_metadata": user_data.get("app_metadata", {}),
                "raw_provider_data": result.get("provider_data", {})
            }
            
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "unexpected_error"
            }
    
    async def validate_token(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Validate token using Supabase adapter.
        
        Returns raw data only - no business logic, no SecurityContext.
        Platform SDK will translate this to SecurityContext.
        
        Args:
            token: Authentication token
        
        Returns:
            Optional[Dict[str, Any]]: Raw validation data or None if invalid
            Structure:
            {
                "success": bool,
                "user_id": str,
                "email": str,
                "access_token": str,
                "raw_user_data": Dict[str, Any],
                "raw_user_metadata": Dict[str, Any],
                "raw_app_metadata": Dict[str, Any],
                "error": Optional[str]
            }
        """
        try:
            # Use Supabase adapter for token validation
            if hasattr(self.supabase, 'validate_token_local'):
                # Prefer local JWKS validation (faster)
                result = await self.supabase.validate_token_local(token)
            else:
                # Fallback to network validation
                result = await self.supabase.get_user(token)
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Token validation failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": result.get("error_type", "validation_error")
                }
            
            # Extract raw data
            user_data = result.get("user", {})
            
            # Return raw data only - no business logic
            return {
                "success": True,
                "user_id": user_data.get("id"),
                "email": user_data.get("email", ""),
                "access_token": token,  # Return the validated token
                "raw_user_data": user_data,
                "raw_user_metadata": user_data.get("user_metadata", {}),
                "raw_app_metadata": user_data.get("app_metadata", {}),
                "raw_provider_data": result.get("provider_data", {})
            }
            
        except Exception as e:
            self.logger.error(f"Token validation error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "validation_error"
            }
    
    async def refresh_token(
        self,
        refresh_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Refresh token using Supabase adapter.
        
        Returns raw data only - no business logic, no SecurityContext.
        Platform SDK will translate this to SecurityContext.
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Optional[Dict[str, Any]]: Raw refresh data or None if failed
        """
        try:
            # Use Supabase adapter
            result = await self.supabase.refresh_session(refresh_token)
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Token refresh failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "refresh_error"
                }
            
            # Extract raw data
            user_data = result.get("user", {})
            session_data = result.get("session", {})
            
            # Return raw data only
            return {
                "success": True,
                "user_id": user_data.get("id"),
                "email": user_data.get("email", ""),
                "access_token": session_data.get("access_token"),
                "refresh_token": session_data.get("refresh_token"),
                "expires_in": session_data.get("expires_in"),
                "expires_at": session_data.get("expires_at"),
                "raw_user_data": user_data,
                "raw_session_data": session_data,
                "raw_user_metadata": user_data.get("user_metadata", {}),
                "raw_app_metadata": user_data.get("app_metadata", {}),
                "raw_provider_data": result.get("provider_data", {})
            }
            
        except Exception as e:
            self.logger.error(f"Token refresh error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "refresh_error"
            }
    
    async def register_user(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Register new user using Supabase adapter.
        
        Returns raw data only - no business logic, no tenant creation, no SecurityContext.
        Platform SDK will handle tenant creation and SecurityContext creation.
        
        Args:
            credentials: Registration credentials (email, password, user_metadata, etc.)
        
        Returns:
            Optional[Dict[str, Any]]: Raw registration data or None if failed
        """
        try:
            email = credentials.get("email")
            password = credentials.get("password")
            user_metadata = credentials.get("user_metadata", {})
            
            if not email or not password:
                raise AuthenticationError("Email and password are required")
            
            # Use Supabase adapter - pure infrastructure call
            result = await self.supabase.sign_up_with_password(
                email=email,
                password=password,
                user_metadata=user_metadata
            )
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Registration failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": result.get("error_type", "registration_error")
                }
            
            # Extract raw data
            user_data = result.get("user", {})
            session_data = result.get("session", {})
            
            # Return raw data only - no business logic
            return {
                "success": True,
                "user_id": user_data.get("id"),
                "email": user_data.get("email", ""),
                "access_token": session_data.get("access_token") if session_data else None,
                "refresh_token": session_data.get("refresh_token") if session_data else None,
                "expires_in": session_data.get("expires_in") if session_data else None,
                "expires_at": session_data.get("expires_at") if session_data else None,
                "raw_user_data": user_data,
                "raw_session_data": session_data,
                "raw_user_metadata": user_data.get("user_metadata", {}),
                "raw_app_metadata": user_data.get("app_metadata", {}),
                "raw_provider_data": result.get("provider_data", {})
            }
            
        except Exception as e:
            self.logger.error(f"Registration error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": "registration_error"
            }
    
    async def logout_user(self, token: str) -> bool:
        """
        Logout user using Supabase adapter.
        
        Args:
            token: Authentication token
        
        Returns:
            bool: True if logout successful
        """
        try:
            result = await self.supabase.sign_out(token)
            return result.get("success", False)
        except Exception as e:
            self.logger.error(f"Logout error: {str(e)}", exc_info=True)
            return False
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information using Supabase adapter.
        
        Returns raw data only - no business logic.
        
        Args:
            user_id: User ID
        
        Returns:
            Optional[Dict[str, Any]]: Raw user data or None if not found
        """
        try:
            result = await self.supabase.admin_get_user(user_id)
            
            if not result.get("success"):
                self.logger.warning(f"Failed to get user info: {result.get('error')}")
                return None
            
            user_data = result.get("user", {})
            
            # Return raw data only
            return {
                "user_id": user_data.get("id"),
                "email": user_data.get("email"),
                "raw_user_data": user_data,
                "raw_user_metadata": user_data.get("user_metadata", {}),
                "raw_app_metadata": user_data.get("app_metadata", {}),
                "created_at": user_data.get("created_at"),
                "last_sign_in": user_data.get("last_sign_in_at")
            }
            
        except Exception as e:
            self.logger.error(f"Get user info error: {str(e)}", exc_info=True)
            return None
