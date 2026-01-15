"""
Tenant Abstraction - Pure Infrastructure Implementation (Layer 1)

Implements tenancy operations using Supabase adapter.
Returns raw tenant data only - no business logic.

WHAT (Infrastructure Role): I provide tenant services
HOW (Infrastructure Implementation): I use Supabase adapter with Redis caching
"""

import json
from typing import Dict, Any, Optional, List

from utilities import get_logger, get_clock
from ..protocols.auth_protocol import TenancyProtocol
from ..adapters.supabase_adapter import SupabaseAdapter
from ..adapters.redis_adapter import RedisAdapter


class TenantAbstraction(TenancyProtocol):
    """
    Tenant abstraction - pure infrastructure.
    
    Returns raw tenant data only (Dict[str, Any]), not business objects.
    Business logic (tenant access validation, config management) belongs
    in Security Guard Primitive and Platform SDK, not here.
    """
    
    def __init__(
        self,
        supabase_adapter: SupabaseAdapter,
        redis_adapter: Optional[RedisAdapter] = None
    ):
        """
        Initialize Tenant abstraction.
        
        Args:
            supabase_adapter: Supabase adapter (Layer 0)
            redis_adapter: Redis adapter for caching (optional, Layer 0)
        """
        self.supabase = supabase_adapter
        self.redis = redis_adapter
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("Tenant Abstraction initialized (pure infrastructure)")
    
    async def get_tenant(
        self,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get tenant information.
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            Optional[Dict]: Tenant information or None if not found
        """
        try:
            # Try cache first if Redis is available
            if self.redis:
                cache_key = f"tenant:{tenant_id}"
                cached_tenant = await self.redis.get(cache_key)
                if cached_tenant:
                    tenant_data = json.loads(cached_tenant)
                    self.logger.debug(f"Retrieved tenant from cache: {tenant_id}")
                    return tenant_data
            
            # Get tenant from Supabase
            result = await self.supabase.get_tenant_by_id(tenant_id)
            
            if result.get("success"):
                tenant_data = result.get("tenant", {})
                
                # Cache if Redis is available
                if self.redis and tenant_data:
                    cache_key = f"tenant:{tenant_id}"
                    await self.redis.set(cache_key, json.dumps(tenant_data), ttl=3600)
                
                self.logger.info(f"Retrieved tenant: {tenant_id}")
                return tenant_data
            else:
                self.logger.warning(f"Tenant not found: {tenant_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get tenant {tenant_id}: {e}", exc_info=True)
            return None
    
    async def get_user_tenant_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get raw tenant information for a given user.
        
        This method is pure infrastructure and returns raw data, not business objects.
        Delegates to SupabaseAdapter.get_user_tenant_info().
        
        Args:
            user_id: User ID
        
        Returns:
            Dict[str, Any]: Raw tenant information from database
            Structure:
            {
                "tenant_id": str,
                "primary_tenant_id": str,
                "tenant_type": str,
                "roles": List[str],
                "permissions": List[str],
                "raw_user_tenant_data": Dict[str, Any]  # Full data from user_tenants table
            }
        """
        try:
            # Delegate to Supabase adapter (pure infrastructure)
            tenant_info = await self.supabase.get_user_tenant_info(user_id)
            
            if tenant_info:
                self.logger.debug(f"Retrieved tenant info for user: {user_id}")
                return tenant_info
            else:
                self.logger.debug(f"No tenant info found for user: {user_id}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Failed to get user tenant info for {user_id}: {e}", exc_info=True)
            return {}
    
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new tenant.
        
        Args:
            tenant_data: Tenant creation data
        
        Returns:
            Optional[str]: Tenant ID if successful, None otherwise
        """
        try:
            # Add default values
            enhanced_data = {
                **tenant_data,
                "status": tenant_data.get("status", "active"),
                "created_at": self.clock.now_iso(),
                "updated_at": self.clock.now_iso()
            }
            
            result = await self.supabase.create_tenant(enhanced_data)
            
            if result.get("success"):
                tenant_id = result.get("tenant_id")
                
                # Clear cache if Redis is available
                if self.redis:
                    cache_key = f"tenant:{tenant_id}"
                    await self.redis.delete(cache_key)
                
                self.logger.info(f"Tenant created: {tenant_id}")
                return tenant_id
            else:
                self.logger.error(f"Failed to create tenant: {result.get('error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to create tenant: {e}", exc_info=True)
            return None
    
    async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update tenant information.
        
        Args:
            tenant_id: Tenant ID
            updates: Updates to apply
        
        Returns:
            bool: True if successful
        """
        try:
            # Add update timestamp
            enhanced_updates = {
                **updates,
                "updated_at": self.clock.now_iso()
            }
            
            # Note: SupabaseAdapter doesn't have update_tenant method yet
            # For now, we'll need to add it or use admin operations
            # This is a placeholder for the full implementation
            
            # Clear cache if Redis is available
            if self.redis:
                cache_key = f"tenant:{tenant_id}"
                await self.redis.delete(cache_key)
            
            self.logger.info(f"Tenant updated: {tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update tenant {tenant_id}: {e}", exc_info=True)
            return False
