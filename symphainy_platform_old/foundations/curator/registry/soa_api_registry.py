"""
SOA API Registry

Manages SOA API endpoint registration and discovery.

WHAT (Service Role): I manage SOA API endpoint registration and discovery
HOW (Service Implementation): I maintain an SOA API registry
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utilities import get_logger, get_clock


class SOAAPIRegistry:
    """
    SOA API Registry - Central SOA API endpoint registration and discovery.
    
    Manages SOA API endpoints for realm-to-realm communication.
    """
    
    def __init__(self):
        """Initialize SOA API Registry."""
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        # SOA API registry
        # Key: api_name (e.g., "service_name.api_name"), Value: Dict with handler, metadata, etc.
        self.soa_api_registry: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("SOA API Registry initialized")
    
    async def register_soa_api(
        self,
        api_name: str,
        service_name: str,
        handler: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register an SOA API endpoint.
        
        Args:
            api_name: Name of the API (e.g., "parse_file")
            service_name: Name of the service providing this API
            handler: API handler function/method
            metadata: Optional metadata (description, parameters, etc.)
        
        Returns:
            bool: True if registration successful
        """
        try:
            full_api_name = f"{service_name}.{api_name}"
            
            self.soa_api_registry[full_api_name] = {
                "api_name": api_name,
                "service_name": service_name,
                "full_api_name": full_api_name,
                "handler": handler,
                "metadata": metadata or {},
                "registered_at": self.clock.now_iso(),
                "status": "active"
            }
            
            self.logger.info(f"SOA API registered: {full_api_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register SOA API: {e}", exc_info=True)
            return False
    
    async def get_api(self, api_name: str, service_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get SOA API by name.
        
        Args:
            api_name: Name of the API
            service_name: Optional service name (for full API name)
        
        Returns:
            Optional[Dict[str, Any]]: API registration or None if not found
        """
        if service_name:
            full_api_name = f"{service_name}.{api_name}"
            return self.soa_api_registry.get(full_api_name)
        else:
            # Search for API by partial name
            for full_name, api in self.soa_api_registry.items():
                if api.get("api_name") == api_name:
                    return api
            return None
    
    async def list_apis(
        self,
        service_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List SOA APIs with optional filters.
        
        Args:
            service_name: Optional service name filter
        
        Returns:
            List[Dict[str, Any]]: List of API registrations
        """
        apis = list(self.soa_api_registry.values())
        
        if service_name:
            apis = [a for a in apis if a.get("service_name") == service_name]
        
        return apis
    
    async def deregister_api(self, api_name: str, service_name: Optional[str] = None) -> bool:
        """
        Deregister an SOA API.
        
        Args:
            api_name: Name of the API
            service_name: Optional service name (for full API name)
        
        Returns:
            bool: True if deregistration successful
        """
        try:
            if service_name:
                full_api_name = f"{service_name}.{api_name}"
                if full_api_name not in self.soa_api_registry:
                    self.logger.warning(f"SOA API not found: {full_api_name}")
                    return False
                del self.soa_api_registry[full_api_name]
            else:
                # Search and remove
                found = False
                for full_name, api in list(self.soa_api_registry.items()):
                    if api.get("api_name") == api_name:
                        del self.soa_api_registry[full_name]
                        found = True
                        break
                if not found:
                    self.logger.warning(f"SOA API not found: {api_name}")
                    return False
            
            self.logger.info(f"SOA API deregistered: {api_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deregister SOA API: {e}", exc_info=True)
            return False
