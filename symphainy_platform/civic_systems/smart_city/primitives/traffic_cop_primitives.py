"""
Traffic Cop Primitives - Session Validation and Rate Limiting

Primitives for Traffic Cop policy decisions (used by Runtime only).

WHAT (Smart City Role): I validate sessions and check rate limits
HOW (Primitive Implementation): I provide pure functions, no side effects, deterministic

⚠️ CRITICAL: Primitives are used by Runtime only.
SDKs prepare execution contracts. Primitives validate them.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger


class RateLimitStore:
    """
    Rate limit store interface (abstract).
    
    In MVP: Simple in-memory or Redis-based rate limit tracking
    In full: Sophisticated rate limiting with sliding windows
    """
    
    async def check_rate_limit(
        self,
        tenant_id: Optional[str],  # Optional for anonymous sessions
        user_id: Optional[str],
        action: str,
        limit: int,
        window_seconds: int
    ) -> bool:
        """
        Check if rate limit is exceeded.
        
        Args:
            tenant_id: Tenant identifier
            user_id: Optional user identifier
            resource: Resource identifier (e.g., "create_session")
            limit: Maximum number of requests
            window_seconds: Time window in seconds
        
        Returns:
            True if within limit, False if exceeded
        """
        # MVP: Always allow (for MVP showcase)
        # Full: Implement sliding window rate limiting
        return True
    
    async def record_request(
        self,
        tenant_id: Optional[str],  # Optional for anonymous sessions
        user_id: Optional[str],
        action: str
    ) -> None:
        """
        Record a request for rate limiting.
        
        Args:
            tenant_id: Tenant identifier
            user_id: Optional user identifier
            action: Action identifier
        """
        # MVP: No-op (for MVP showcase)
        # Full: Record request in Redis with TTL
        pass


class TrafficCopPrimitives:
    """
    Traffic Cop Primitives - Policy Validation
    
    Pure functions for session validation and rate limiting.
    Used by Runtime only.
    """
    
    def __init__(self, rate_limit_store: Optional[RateLimitStore] = None):
        """
        Initialize Traffic Cop Primitives.
        
        Args:
            rate_limit_store: Optional rate limit store (for MVP, can be None)
        """
        self.rate_limit_store = rate_limit_store or RateLimitStore()
        self.logger = get_logger(self.__class__.__name__)
    
    @staticmethod
    async def validate_session(
        session_id: str,
        tenant_id: str,
        execution_contract: Dict[str, Any],
        rate_limit_store: RateLimitStore
    ) -> bool:
        """
        Validate session (Primitive - pure function, no side effects).
        
        This is called by Runtime to validate the execution contract
        prepared by Traffic Cop SDK.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
            execution_contract: Execution contract prepared by SDK
            rate_limit_store: Rate limit store instance
        
        Returns:
            True if session is valid, False otherwise
        """
        try:
            # 1. Check required fields
            if execution_contract.get("action") not in ["create_session", "get_session", "validate_session"]:
                return False
            
            # 2. Check rate limiting (if creating session)
            if execution_contract.get("action") == "create_session":
                user_id = execution_contract.get("user_id")
                within_limit = await rate_limit_store.check_rate_limit(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    action="create_session",
                    limit=10,  # MVP: 10 sessions per minute
                    window_seconds=60
                )
                if not within_limit:
                    return False
            
            # 3. Validate session access policies (if any)
            access_policies = execution_contract.get("access_policies", [])
            for policy in access_policies:
                # MVP: Simple allow-all (for MVP showcase)
                # Full: Evaluate policy rules
                pass
            
            # MVP: Default allow (for MVP showcase)
            return True
            
        except Exception as e:
            logger = get_logger("TrafficCopPrimitives")
            logger.error(f"Session validation failed: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def check_rate_limit(
        tenant_id: str,
        user_id: Optional[str],
        action: str,
        rate_limit_store: RateLimitStore,
        execution_contract: Dict[str, Any]
    ) -> bool:
        """
        Check rate limit (Primitive - pure function, no side effects).
        
        Args:
            tenant_id: Tenant identifier
            user_id: Optional user identifier
            action: Action to check
            rate_limit_store: Rate limit store instance
            execution_contract: Execution contract prepared by SDK
        
        Returns:
            True if within rate limit, False otherwise
        """
        try:
            # Get rate limit policies from execution contract
            rate_limit_policies = execution_contract.get("rate_limit_policies", [])
            
            # If no policies, use defaults
            if not rate_limit_policies:
                # MVP: Default limits (for MVP showcase)
                limit = 100  # 100 requests per minute
                window_seconds = 60
            else:
                # Full: Use policy-defined limits
                # For MVP: Use first policy's limits
                policy = rate_limit_policies[0] if rate_limit_policies else {}
                limit = policy.get("limit", 100)
                window_seconds = policy.get("window_seconds", 60)
            
            # Check rate limit
            within_limit = await rate_limit_store.check_rate_limit(
                tenant_id=tenant_id,
                user_id=user_id,
                action=action,
                limit=limit,
                window_seconds=window_seconds
            )
            
            # Record request if within limit
            if within_limit:
                await rate_limit_store.record_request(tenant_id, user_id, action)
            
            return within_limit
            
        except Exception as e:
            logger = get_logger("TrafficCopPrimitives")
            logger.error(f"Rate limit check failed: {e}", exc_info=True)
            return False  # Fail secure: deny if check fails
    
    @staticmethod
    async def validate_session_creation(
        execution_contract: Dict[str, Any],
        rate_limit_store: RateLimitStore
    ) -> bool:
        """
        Validate session creation execution contract (Primitive).
        
        Supports both anonymous sessions (tenant_id=None, user_id=None) and authenticated sessions.
        
        Args:
            execution_contract: Execution contract prepared by SDK
            rate_limit_store: Rate limit store instance
        
        Returns:
            True if session creation is valid, False otherwise
        """
        try:
            # 1. Check required fields
            required_fields = ["action", "session_id"]
            for field in required_fields:
                if field not in execution_contract:
                    return False
            
            # 2. Validate action
            if execution_contract.get("action") != "create_session":
                return False
            
            # 3. Check if anonymous session (tenant_id and user_id can be None)
            is_anonymous = (
                execution_contract.get("session_type") == "anonymous" or
                execution_contract.get("tenant_id") is None or
                execution_contract.get("user_id") is None
            )
            
            # 4. Check rate limiting (skip for anonymous sessions in MVP)
            if not is_anonymous:
                tenant_id = execution_contract.get("tenant_id")
                user_id = execution_contract.get("user_id")
                within_limit = await TrafficCopPrimitives.check_rate_limit(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    action="create_session",
                    rate_limit_store=rate_limit_store,
                    execution_contract=execution_contract
                )
                
                if not within_limit:
                    return False
            
            # MVP: Default allow (for MVP showcase)
            # Anonymous sessions always allowed (no rate limiting in MVP)
            return True
            
        except Exception as e:
            logger = get_logger("TrafficCopPrimitives")
            logger.error(f"Session creation validation failed: {e}", exc_info=True)
            return False
