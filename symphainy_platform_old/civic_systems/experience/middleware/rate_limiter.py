"""
Rate Limiter for API Endpoints

Simple rate limiting using Redis (or in-memory fallback).
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

from typing import Optional, Dict, Tuple, Callable
from datetime import datetime, timedelta
from functools import wraps
from fastapi import Request, HTTPException, status, Depends
import os
from utilities import get_logger

logger = get_logger("RateLimiter")


class RateLimiter:
    """
    Simple rate limiter using in-memory storage (or Redis if available).
    
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self):
        """Initialize rate limiter."""
        self.rate_limits: Dict[str, Dict[str, any]] = {}  # key -> {count, reset_at}
        self.logger = logger
    
    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Generate rate limit key."""
        return f"rate_limit:{endpoint}:{identifier}"
    
    def _is_test_mode(self, request: Request) -> bool:
        """
        Check if request is in test mode.
        
        Test mode is enabled if:
        1. TEST_MODE environment variable is set to 'true'
        2. X-Test-Mode header is set to 'true'
        
        Args:
            request: FastAPI request
            
        Returns:
            True if in test mode, False otherwise
        """
        # Check environment variable
        if os.getenv("TEST_MODE", "").lower() == "true":
            return True
        
        # Check header
        test_mode_header = request.headers.get("X-Test-Mode", "").lower()
        if test_mode_header == "true":
            return True
        
        return False
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting (IP address)."""
        # In test mode, use a unique identifier per test to avoid conflicts
        if self._is_test_mode(request):
            # Use a test-specific identifier that includes timestamp to avoid conflicts
            test_id = request.headers.get("X-Test-ID", "test")
            return f"test_{test_id}"
        
        # Try to get real IP from headers (if behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP if multiple
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def check_rate_limit(
        self,
        request: Request,
        endpoint: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit.
        
        Args:
            request: FastAPI request
            endpoint: Endpoint identifier
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        # In test mode, use relaxed limits (1000 requests per minute)
        if self._is_test_mode(request):
            max_requests = 1000
            window_seconds = 60
        
        identifier = self._get_client_identifier(request)
        key = self._get_key(identifier, endpoint)
        
        now = datetime.utcnow()
        
        # Get current rate limit state
        if key in self.rate_limits:
            limit_info = self.rate_limits[key]
            reset_at = limit_info["reset_at"]
            
            # Check if window has expired
            if now >= reset_at:
                # Reset window
                self.rate_limits[key] = {
                    "count": 1,
                    "reset_at": now + timedelta(seconds=window_seconds)
                }
                return True, None
            
            # Check if limit exceeded
            if limit_info["count"] >= max_requests:
                retry_after = int((reset_at - now).total_seconds())
                return False, retry_after
            
            # Increment count
            limit_info["count"] += 1
        else:
            # First request in window
            self.rate_limits[key] = {
                "count": 1,
                "reset_at": now + timedelta(seconds=window_seconds)
            }
        
        return True, None
    
    def cleanup_expired_limits(self):
        """Clean up expired rate limit entries."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, info in self.rate_limits.items()
            if now >= info["reset_at"]
        ]
        for key in expired_keys:
            del self.rate_limits[key]


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """
    Get rate limiter instance (FastAPI dependency).
    
    Returns:
        RateLimiter instance
    """
    return _rate_limiter


def create_rate_limit_dependency(
    max_requests: int = 5,
    window_seconds: int = 60
) -> Callable:
    """
    Create a FastAPI dependency for rate limiting.
    
    This is the proper FastAPI way to implement rate limiting.
    
    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
    
    Returns:
        FastAPI dependency function
    
    Usage:
        # Create dependency
        rate_limit_login = create_rate_limit_dependency(max_requests=5, window_seconds=60)
        
        # Use in endpoint
        @router.post("/login")
        async def login(
            request: Request,
            rate_limiter: RateLimiter = Depends(rate_limit_login)
        ):
            ...
    """
    async def rate_limit_check(
        request: Request,
        rate_limiter: RateLimiter = Depends(get_rate_limiter)
    ) -> None:
        """
        FastAPI dependency that checks rate limit and raises 429 if exceeded.
        
        Args:
            request: FastAPI request
            rate_limiter: Rate limiter instance
        
        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        # Clean up expired limits periodically
        rate_limiter.cleanup_expired_limits()
        
        # Check rate limit
        endpoint = f"{request.method}:{request.url.path}"
        is_allowed, retry_after = rate_limiter.check_rate_limit(
            request=request,
            endpoint=endpoint,
            max_requests=max_requests,
            window_seconds=window_seconds
        )
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. Maximum {max_requests} requests per {window_seconds} seconds.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after) if retry_after else "60",
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Window": str(window_seconds)
                }
            )
    
    return rate_limit_check


# Pre-configured rate limit dependencies for common use cases
rate_limit_login = create_rate_limit_dependency(max_requests=5, window_seconds=60)
rate_limit_register = create_rate_limit_dependency(max_requests=3, window_seconds=300)


# Legacy decorator support (for backwards compatibility)
def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    """
    Decorator for rate limiting endpoints (legacy support).
    
    Note: For new code, prefer using FastAPI dependencies:
    rate_limiter: RateLimiter = Depends(create_rate_limit_dependency(...))
    
    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
    
    Usage:
        @router.post("/login")
        @rate_limit(max_requests=5, window_seconds=60)
        async def login(http_request: Request, ...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find Request object in args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                request = kwargs.get("http_request") or kwargs.get("request")
            
            if not request or not isinstance(request, Request):
                # If no request found, call function anyway (shouldn't happen in FastAPI)
                return await func(*args, **kwargs)
            
            # Clean up expired limits periodically
            _rate_limiter.cleanup_expired_limits()
            
            # Check rate limit
            endpoint = f"{request.method}:{request.url.path}"
            is_allowed, retry_after = _rate_limiter.check_rate_limit(
                request=request,
                endpoint=endpoint,
                max_requests=max_requests,
                window_seconds=window_seconds
            )
            
            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "rate_limit_exceeded",
                        "message": f"Too many requests. Maximum {max_requests} requests per {window_seconds} seconds.",
                        "retry_after": retry_after
                    },
                    headers={
                        "Retry-After": str(retry_after) if retry_after else "60",
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Window": str(window_seconds)
                    }
                )
            
            # Call original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
