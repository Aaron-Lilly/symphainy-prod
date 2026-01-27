"""
Authentication Middleware for Experience Service

Protects all API endpoints except public ones (auth, health).
"""
import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional
from utilities import get_logger

logger = get_logger("ExperienceAPI.AuthMiddleware")


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API request authentication.
    
    Protects all endpoints except:
    - /health
    - /api/auth/*
    - /docs, /openapi.json, /redoc (FastAPI docs)
    """
    
    def __init__(self, app, excluded_paths: Optional[List[str]] = None):
        super().__init__(app)
        
        # Default excluded paths (public endpoints)
        self.excluded_paths = excluded_paths or [
            "/health",
            "/api/auth/login",
            "/api/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if the path should be excluded from authentication."""
        # Check exact matches
        if path in self.excluded_paths:
            return True
        
        # Check if path starts with excluded prefix
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        
        return False
    
    def _extract_token_from_header(self, authorization: Optional[str]) -> Optional[str]:
        """Extract Bearer token from Authorization header."""
        if not authorization:
            return None
        
        # Check if it's a Bearer token
        if not authorization.startswith("Bearer "):
            return None
        
        # Extract the token part
        token = authorization[7:]  # Remove "Bearer " prefix
        return token.strip() if token else None
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and validate authentication if required.
        """
        path = request.url.path
        method = request.method
        
        # Skip authentication for excluded paths
        if self._is_excluded_path(path):
            logger.debug(f"Skipping auth for excluded path: {method} {path}")
            return await call_next(request)
        
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        token = self._extract_token_from_header(authorization)
        
        if not token:
            logger.warning(f"Missing or invalid Authorization header for: {method} {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "unauthorized",
                    "message": "Missing or invalid Authorization header",
                    "details": "Please provide a valid Bearer token"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate token via Security Guard SDK
        try:
            if not hasattr(request.app.state, "security_guard_sdk"):
                logger.error("Security Guard SDK not initialized in app state")
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={
                        "error": "service_unavailable",
                        "message": "Authentication service not available"
                    }
                )
            
            security_guard = request.app.state.security_guard_sdk
            auth_result = await security_guard.validate_token(token)
            
            if not auth_result:
                logger.warning(f"Invalid token for: {method} {path}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": "unauthorized",
                        "message": "Invalid or expired token",
                        "details": "Please login again to get a valid token"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Add user information to request state
            request.state.user_id = auth_result.user_id
            request.state.tenant_id = auth_result.tenant_id
            request.state.token = token
            request.state.roles = auth_result.roles or []
            request.state.permissions = auth_result.permissions or []
            
            logger.debug(f"Authentication successful for user: {auth_result.user_id}")
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Authentication error for {method} {path}: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "authentication_error",
                    "message": "An error occurred during authentication",
                    "details": "Please try again later"
                }
            )
        
        # Continue with the request
        response = await call_next(request)
        return response
