"""
Authorization Abstraction - Pure Infrastructure Implementation (Layer 1)

Implements authorization operations using Supabase adapter.
Returns raw permission data only - no business logic.

WHAT (Infrastructure Role): I provide authorization services
HOW (Infrastructure Implementation): I use Supabase adapter with Redis caching
"""

import json
from typing import Dict, Any, Optional, List

from utilities import get_logger
from ..protocols.auth_protocol import AuthorizationProtocol
from ..adapters.supabase_adapter import SupabaseAdapter
from ..adapters.redis_adapter import RedisAdapter


class AuthorizationAbstraction(AuthorizationProtocol):
    """
    Authorization abstraction - pure infrastructure.
    
    Returns raw permission data only (Dict[str, Any], List[str]), not business objects.
    Business logic (permission checking, role hierarchy) belongs in Security Guard Primitive, not here.
    """
    
    def __init__(
        self,
        supabase_adapter: SupabaseAdapter,
        redis_adapter: Optional[RedisAdapter] = None
    ):
        """
        Initialize Authorization abstraction.
        
        Args:
            supabase_adapter: Supabase adapter (Layer 0)
            redis_adapter: Redis adapter for caching (optional, Layer 0)
        """
        self.supabase = supabase_adapter
        self.redis = redis_adapter
        self.logger = get_logger(self.__class__.__name__)
        
        self.logger.info("Authorization Abstraction initialized (pure infrastructure)")
    
    async def check_permission(
        self,
        user_id: str,
        permission: str,
        resource: Optional[str] = None
    ) -> bool:
        """
        Check if user has permission (raw infrastructure check).
        
        This is pure infrastructure - queries database/cache for permission data.
        Business logic (policy decisions, role hierarchy) belongs in Security Guard Primitive.
        
        Args:
            user_id: User ID
            permission: Permission to check
            resource: Optional resource identifier
        
        Returns:
            bool: True if user has permission in database/cache (raw check only)
        """
        try:
            # Get user permissions (raw data)
            permissions = await self.get_user_permissions(user_id)
            
            # Simple infrastructure check: is permission in list?
            # Business logic (role hierarchy, policy rules) is in Security Guard Primitive
            return permission in permissions
            
        except Exception as e:
            self.logger.error(f"Failed to check permission for {user_id}: {e}", exc_info=True)
            return False
    
    async def get_user_permissions(
        self,
        user_id: str
    ) -> List[str]:
        """
        Get all permissions for a user (raw infrastructure data).
        
        Returns raw permission data from database/cache.
        No business logic - just infrastructure data access.
        
        Args:
            user_id: User ID
        
        Returns:
            List[str]: List of permission strings (raw data)
        """
        try:
            # Try cache first if Redis is available
            if self.redis:
                cache_key = f"user_permissions:{user_id}"
                cached_permissions = await self.redis.get(cache_key)
                if cached_permissions:
                    permissions = json.loads(cached_permissions)
                    self.logger.debug(f"Retrieved permissions from cache for user: {user_id}")
                    return permissions
            
            # Get permissions from Supabase (raw data)
            # Query user_metadata or user_tenants table
            result = await self.supabase.admin_get_user(user_id)
            
            if result.get("success"):
                user_data = result.get("user", {})
                # Extract permissions from user_metadata (raw data)
                permissions = user_data.get("user_metadata", {}).get("permissions", [])
                
                # Cache if Redis is available
                if self.redis and permissions:
                    cache_key = f"user_permissions:{user_id}"
                    await self.redis.set(cache_key, json.dumps(permissions), ttl=1800)
                
                self.logger.debug(f"Retrieved permissions from Supabase for user: {user_id}")
                return permissions
            else:
                self.logger.warning(f"User not found: {user_id}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to get user permissions for {user_id}: {e}", exc_info=True)
            return []
