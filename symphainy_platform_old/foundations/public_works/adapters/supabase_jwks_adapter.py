"""
Supabase JWKS Adapter - JWKS Fetcher and Cache (Layer 0)

Fetches and caches Supabase's JWKS (JSON Web Key Set) for local JWT verification.
This is the raw technology layer for JWKS operations.

WHAT (Infrastructure Role): I provide JWKS fetching and caching
HOW (Infrastructure Implementation): I fetch from Supabase's JWKS endpoint and cache public keys
"""

import asyncio
import httpx
from typing import Dict, Any, Optional
from utilities import get_logger, get_clock


class SupabaseJWKSAdapter:
    """
    JWKS adapter for Supabase - fetches and caches public keys.
    
    Supabase provides JWKS at: https://<project>.supabase.co/auth/v1/.well-known/jwks.json
    This allows local JWT verification without network calls to Supabase API.
    """
    
    def __init__(self, supabase_url: Optional[str] = None, jwks_url: Optional[str] = None, cache_ttl: int = 600):
        """
        Initialize JWKS adapter.
        
        Args:
            supabase_url: Supabase project URL (used to construct JWKS URL if jwks_url not provided)
            jwks_url: Direct JWKS URL (takes precedence)
            cache_ttl: Cache TTL in seconds (default 10 minutes, Supabase caches for 10 min)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        # Use SUPABASE_JWKS_URL if provided (recommended), otherwise construct from supabase_url
        if jwks_url:
            # Normalize JWKS URL - ensure it has .well-known (not well-known)
            self.jwks_url = jwks_url.replace("/well-known/", "/.well-known/")
        elif supabase_url:
            # Normalize URL - remove trailing slashes
            self.supabase_url = supabase_url.rstrip('/') if supabase_url else supabase_url
            self.jwks_url = f"{self.supabase_url}/auth/v1/.well-known/jwks.json"
        else:
            raise ValueError(
                "Either jwks_url or supabase_url must be provided. "
                "Example: SupabaseJWKSAdapter(supabase_url=url) or SupabaseJWKSAdapter(jwks_url=url)"
            )
        
        self.cache_ttl = cache_ttl
        
        # Cache for JWKS
        self._jwks_cache: Optional[Dict[str, Any]] = None
        self._jwks_cache_time: Optional[str] = None
        self._jwks_lock = asyncio.Lock()
        
        self.logger.info(f"Supabase JWKS adapter initialized for: {self.jwks_url}")
    
    async def get_jwks(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get JWKS (cached or fresh).
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            JWKS dictionary with keys
        """
        async with self._jwks_lock:
            # Check if cache is valid
            if not force_refresh and self._jwks_cache and self._jwks_cache_time:
                cache_time = self.clock.parse_iso(self._jwks_cache_time)
                age = (self.clock.now() - cache_time).total_seconds()
                if age < self.cache_ttl:
                    self.logger.debug(f"Using cached JWKS (age: {age:.1f}s)")
                    return self._jwks_cache
            
            # Fetch fresh JWKS
            try:
                self.logger.info(f"Fetching JWKS from: {self.jwks_url}")
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(self.jwks_url)
                    response.raise_for_status()
                    
                    jwks = response.json()
                    
                    # Validate JWKS structure
                    if not isinstance(jwks, dict) or "keys" not in jwks:
                        raise ValueError("Invalid JWKS structure: missing 'keys'")
                    
                    # Cache JWKS
                    self._jwks_cache = jwks
                    self._jwks_cache_time = self.clock.now_iso()
                    
                    self.logger.info(f"JWKS fetched and cached ({len(jwks.get('keys', []))} keys)")
                    return jwks
                    
            except httpx.TimeoutException:
                self.logger.error(f"JWKS fetch timeout: {self.jwks_url}")
                # Return cached JWKS if available (even if expired)
                if self._jwks_cache:
                    self.logger.warning("Using expired JWKS cache due to timeout")
                    return self._jwks_cache
                raise
            except Exception as e:
                self.logger.error(f"Failed to fetch JWKS: {e}", exc_info=True)
                # Return cached JWKS if available (even if expired)
                if self._jwks_cache:
                    self.logger.warning("Using expired JWKS cache due to error")
                    return self._jwks_cache
                raise
    
    def get_key_by_kid(self, kid: str, jwks: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get public key by key ID (kid) from JWKS.
        
        Args:
            kid: Key ID from JWT header
            jwks: JWKS dictionary (if None, uses cached JWKS)
            
        Returns:
            Public key dictionary or None if not found
        """
        if jwks is None:
            jwks = self._jwks_cache
        
        if not jwks or "keys" not in jwks:
            return None
        
        # Find key with matching kid
        for key in jwks["keys"]:
            if key.get("kid") == kid:
                return key
        
        return None
    
    async def refresh_jwks(self) -> Dict[str, Any]:
        """Force refresh JWKS cache."""
        return await self.get_jwks(force_refresh=True)
