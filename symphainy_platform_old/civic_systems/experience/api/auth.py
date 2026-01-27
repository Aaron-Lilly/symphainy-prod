"""
Authentication API Endpoints

Follows Security Guard SDK pattern for authentication.
"""
import sys
from pathlib import Path

# Add project root to path
# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Dict, Any, Optional
import re

from utilities import get_logger
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK
from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK
from ..middleware.rate_limiter import rate_limit_login, rate_limit_register
from ..sdk.runtime_client import RuntimeClient
from datetime import datetime


router = APIRouter(prefix="/api/auth", tags=["authentication"])
logger = get_logger("ExperienceAPI.Auth")


def get_security_guard_sdk(request: Request) -> SecurityGuardSDK:
    """Dependency to get Security Guard SDK."""
    if not hasattr(request.app.state, "security_guard_sdk"):
        raise RuntimeError("Security Guard SDK not initialized. Check Experience service startup.")
    return request.app.state.security_guard_sdk


def get_traffic_cop_sdk(request: Request) -> TrafficCopSDK:
    """Dependency to get Traffic Cop SDK."""
    if not hasattr(request.app.state, "traffic_cop_sdk"):
        raise RuntimeError("Traffic Cop SDK not initialized. Check Experience service startup.")
    return request.app.state.traffic_cop_sdk


def get_runtime_client() -> RuntimeClient:
    """Dependency to get Runtime client."""
    return RuntimeClient(runtime_url="http://runtime:8000")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Password must be 8-128 characters")
    
    @validator('email')
    def validate_email_length(cls, v):
        if len(v) > 254:  # RFC 5321 limit
            raise ValueError('Email address too long (max 254 characters)')
        return v


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name must be 1-100 characters")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Password must be 8-128 characters")
    
    @validator('email')
    def validate_email_length(cls, v):
        if len(v) > 254:  # RFC 5321 limit
            raise ValueError('Email address too long (max 254 characters)')
        return v
    
    @validator('name')
    def sanitize_name(cls, v):
        """Sanitize name to remove potentially dangerous characters."""
        # Remove HTML/script tags and special characters
        sanitized = re.sub(r'[<>"\']', '', v)
        # Remove leading/trailing whitespace
        sanitized = sanitized.strip()
        if not sanitized:
            raise ValueError('Name cannot be empty after sanitization')
        return sanitized


class AuthResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    session_id: Optional[str] = None  # Separate session_id (not the same as access_token)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    roles: Optional[list] = None
    permissions: Optional[list] = None
    message: Optional[str] = None
    error: Optional[str] = None


@router.post("/login", response_model=AuthResponse)
async def login(
    http_request: Request,
    request: LoginRequest,
    security_guard: SecurityGuardSDK = Depends(get_security_guard_sdk),
    traffic_cop: TrafficCopSDK = Depends(get_traffic_cop_sdk),
    runtime_client: RuntimeClient = Depends(get_runtime_client),
    _rate_limit: None = Depends(rate_limit_login)  # FastAPI dependency for rate limiting
):
    """
    Login user and auto-create session.
    
    Uses Security Guard SDK to authenticate user, then automatically creates a session.
    Returns both access_token (for authentication) and session_id (for session state).
    """
    try:
        # Use auth_abstraction directly to get both validation and tokens in one call
        auth_abstraction = security_guard.auth_abstraction
        auth_data = await auth_abstraction.authenticate({
            "email": request.email,
            "password": request.password
        })
        
        # Check if authentication failed
        if not auth_data or not auth_data.get("success") or not auth_data.get("access_token"):
            # Authentication failed - return 401 directly
            logger.warning(f"Authentication failed for {request.email}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "authentication_failed",
                    "message": "Invalid email or password",
                    "details": "Please check your credentials and try again"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Authentication succeeded - get user context via Security Guard SDK
        try:
            auth_result = await security_guard.authenticate({
                "email": request.email,
                "password": request.password
            })
        except Exception as e:
            # If Security Guard SDK call fails, use data from auth_abstraction
            logger.warning(f"Security Guard SDK authentication failed, using auth_abstraction data: {e}")
            auth_result = None
        
        access_token = auth_data.get("access_token")
        refresh_token = auth_data.get("refresh_token")
        user_id = auth_result.user_id if auth_result else auth_data.get("user_id")
        tenant_id = auth_result.tenant_id if auth_result else auth_data.get("tenant_id")
        
        # Auto-create session after successful authentication
        session_id = None
        try:
            # Create session intent via Traffic Cop SDK
            session_intent = await traffic_cop.create_session_intent(
                tenant_id=tenant_id,
                user_id=user_id,
                metadata={"authenticated_at": datetime.now().isoformat()}
            )
            
            # Create session in Runtime (will validate via Traffic Cop Primitives)
            session_result = await runtime_client.create_session({
                "intent_type": "create_session",
                "tenant_id": session_intent.tenant_id,
                "user_id": session_intent.user_id,
                "session_id": session_intent.session_id,
                "execution_contract": session_intent.execution_contract,
                "metadata": {}
            })
            
            session_id = session_result.get("session_id") or session_intent.session_id
            logger.info(f"Session created automatically on login: {session_id} for user {user_id}")
            
        except Exception as session_error:
            # Log but don't fail login if session creation fails
            logger.error(f"Failed to create session on login: {session_error}", exc_info=True)
            # Continue without session_id - frontend can create session separately if needed
        
        return AuthResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
            session_id=session_id,  # Separate session_id (not the same as access_token)
            user_id=user_id,
            tenant_id=tenant_id,
            roles=auth_result.roles if auth_result else [],
            permissions=auth_result.permissions if auth_result else []
        )
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions (like our 401) - don't log as error
        raise
    except Exception as e:
        # Check if it's an authentication error (invalid credentials)
        error_str = str(e).lower()
        if "invalid" in error_str or "authentication" in error_str or "credentials" in error_str or "password" in error_str:
            logger.warning(f"Authentication failed: {e}")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "authentication_failed",
                    "message": "Invalid email or password",
                    "details": "Please check your credentials and try again"
                }
            )
        # Other errors are server errors
        logger.error(f"Login failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", response_model=AuthResponse)
async def register(
    http_request: Request,
    request: RegisterRequest,
    security_guard: SecurityGuardSDK = Depends(get_security_guard_sdk),
    _rate_limit: None = Depends(rate_limit_register)  # FastAPI dependency for rate limiting
):
    """
    Register new user.
    
    Uses Security Guard SDK (via auth_abstraction) to register user.
    """
    try:
        # Use auth_abstraction directly to get both registration and tokens in one call
        auth_abstraction = security_guard.auth_abstraction
        auth_data = await auth_abstraction.register_user({
            "email": request.email,
            "password": request.password,
            "user_metadata": {
                "name": request.name,
                "full_name": request.name
            }
        })
        
        if not auth_data or not auth_data.get("access_token"):
            # Check if user already exists - try login instead
            error_msg = auth_data.get("error", "") if auth_data else ""
            if "already registered" in error_msg.lower() or "user already" in error_msg.lower():
                logger.info(f"User {request.email} already exists, attempting login instead")
                try:
                    # Try to authenticate the existing user
                    login_data = await auth_abstraction.authenticate({
                        "email": request.email,
                        "password": request.password
                    })
                    
                    if login_data and login_data.get("access_token"):
                        # Login succeeded - get user context
                        try:
                            auth_result = await security_guard.authenticate({
                                "email": request.email,
                                "password": request.password
                            })
                        except Exception:
                            auth_result = None
                        
                        return AuthResponse(
                            success=True,
                            access_token=login_data.get("access_token"),
                            refresh_token=login_data.get("refresh_token"),
                            user_id=auth_result.user_id if auth_result else login_data.get("user_id"),
                            tenant_id=auth_result.tenant_id if auth_result else login_data.get("tenant_id"),
                            roles=auth_result.roles if auth_result else [],
                            permissions=auth_result.permissions if auth_result else [],
                            message="User already exists, logged in successfully"
                        )
                except Exception as login_error:
                    logger.warning(f"Login attempt failed for existing user: {login_error}")
                    # Fall through to return registration error
            
            # Registration failed for other reasons
            return AuthResponse(
                success=False,
                error=auth_data.get("error", "Registration failed") if auth_data else "Registration failed"
            )
        
        # Registration succeeded - get user context via Security Guard SDK for roles/permissions
        auth_result = await security_guard.register_user({
            "email": request.email,
            "password": request.password,
            "user_metadata": {
                "name": request.name,
                "full_name": request.name
            }
        })
        
        access_token = auth_data.get("access_token")
        refresh_token = auth_data.get("refresh_token")
        
        return AuthResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=auth_result.user_id if auth_result else auth_data.get("user_id"),
            tenant_id=auth_result.tenant_id if auth_result else auth_data.get("tenant_id"),
            roles=auth_result.roles if auth_result else [],
            permissions=auth_result.permissions if auth_result else []
        )
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
