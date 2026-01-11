"""
Platform Gateway

Provides unified access to abstractions and services across the platform.

WHAT (Runtime): I provide unified access to platform capabilities
HOW (Gateway): I route requests to appropriate foundations and services
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PlatformGateway:
    """
    Platform Gateway for accessing abstractions and services.
    
    Provides unified interface for:
    - Getting abstractions from Public Works Foundation
    - Getting services from Curator
    """
    
    def __init__(
        self,
        public_works_foundation: Optional[Any] = None,
        curator: Optional[Any] = None
    ):
        """
        Initialize Platform Gateway.
        
        Args:
            public_works_foundation: Public Works Foundation Service instance
            curator: Curator Foundation Service instance
        """
        self.public_works = public_works_foundation
        self.curator = curator
        self._abstraction_cache: Dict[str, Any] = {}
        self._service_cache: Dict[str, Any] = {}
        self.logger = logger
        
        self.logger.info("✅ Platform Gateway initialized")
    
    async def get_abstraction(self, abstraction_name: str) -> Optional[Any]:
        """
        Get abstraction by name.
        
        Args:
            abstraction_name: Name of abstraction (e.g., "pdf_processing_abstraction")
        
        Returns:
            Abstraction instance or None
        """
        # Check cache
        if abstraction_name in self._abstraction_cache:
            return self._abstraction_cache[abstraction_name]
        
        # Get from Public Works Foundation
        if self.public_works:
            # Try getter method first
            method_name = f"get_{abstraction_name}"
            if hasattr(self.public_works, method_name):
                abstraction = getattr(self.public_works, method_name)()
                if abstraction:
                    self._abstraction_cache[abstraction_name] = abstraction
                    return abstraction
            
            # Try direct attribute access
            if hasattr(self.public_works, abstraction_name):
                abstraction = getattr(self.public_works, abstraction_name)
                if abstraction:
                    self._abstraction_cache[abstraction_name] = abstraction
                    return abstraction
        
        self.logger.warning(f"Abstraction not found: {abstraction_name}")
        return None
    
    async def get_service(self, service_name: str) -> Optional[Any]:
        """
        Get service by name.
        
        Args:
            service_name: Name of service (e.g., "structured_parsing_service")
        
        Returns:
            Service instance or None
        """
        # Check cache
        if service_name in self._service_cache:
            return self._service_cache[service_name]
        
        # Get from Curator service registry
        if self.curator and hasattr(self.curator, 'service_registry'):
            service_info = self.curator.service_registry.get_service(service_name)
            if service_info:
                service_instance = service_info.get("service_instance")
                if service_instance:
                    self._service_cache[service_name] = service_instance
                    return service_instance
        
        self.logger.warning(f"Service not found: {service_name}")
        return None
    
    def clear_cache(self):
        """Clear abstraction and service caches."""
        self._abstraction_cache.clear()
        self._service_cache.clear()
        self.logger.debug("Platform Gateway cache cleared")
