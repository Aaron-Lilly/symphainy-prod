"""
Service Registry

Manages service instance registration and discovery.

WHAT (Service Role): I manage service instance registration and discovery
HOW (Service Implementation): I maintain a service registry with Consul integration
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utilities import get_logger, get_clock

from ..models.capability_definition import CapabilityDefinition


class ServiceRegistry:
    """
    Service Registry - Central service registration and discovery.
    
    Manages service instance registration, metadata, and integration with Consul.
    """
    
    def __init__(self, service_discovery_abstraction: Optional[Any] = None):
        """
        Initialize Service Registry.
        
        Args:
            service_discovery_abstraction: Optional service discovery abstraction (from Public Works)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.service_discovery = service_discovery_abstraction
        
        # Service registry
        # Key: service_name, Value: Dict with service_instance, metadata, service_id, etc.
        self.registered_services: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("Service Registry initialized")
    
    async def register_service(
        self,
        service_instance: Any,
        service_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register a service instance.
        
        Registers with:
        1. Consul (via Public Works service discovery abstraction)
        2. Local cache (for fast lookups)
        
        Args:
            service_instance: The service instance to register
            service_metadata: Service metadata including:
                - service_name (required)
                - service_type (required)
                - address (required)
                - port (required)
                - capabilities (optional)
                - tags (optional)
                - realm (optional)
                - health_check_endpoint (optional)
        
        Returns:
            Dict with registration result
        """
        try:
            service_name = service_metadata.get("service_name")
            if not service_name:
                self.logger.error("Service name is required")
                return {"success": False, "error": "Service name is required"}
            
            # Check if already registered
            if service_name in self.registered_services:
                self.logger.info(f"Service {service_name} already registered, updating...")
                return await self.update_service(service_name, service_metadata)
            
            # Register with Consul (via Public Works service discovery abstraction)
            service_id = None
            if self.service_discovery:
                try:
                    service_info = {
                        "service_name": service_name,
                        "service_type": service_metadata.get("service_type", "unknown"),
                        "address": service_metadata.get("address", "localhost"),
                        "port": service_metadata.get("port", 8000),
                        "tags": service_metadata.get("tags", []),
                        "meta": {
                            "capabilities": ",".join(service_metadata.get("capabilities", [])),
                            "endpoints": ",".join(service_metadata.get("endpoints", [])),
                            "realm": service_metadata.get("realm", "unknown"),
                            "registered_at": self.clock.now_iso()
                        },
                        "health_check_endpoint": service_metadata.get("health_check_endpoint")
                    }
                    
                    registration = await self.service_discovery.register_service(service_info)
                    if registration and registration.success:
                        service_id = registration.service_id
                        self.logger.info(f"Service {service_name} registered with Consul: {service_id}")
                    else:
                        self.logger.warning(f"Consul registration failed for {service_name}, continuing with local cache only")
                except Exception as e:
                    self.logger.warning(f"Error registering with Consul: {e}, continuing with local cache only")
            else:
                self.logger.warning("Service discovery not available, using local cache only")
            
            # Register in local cache
            self.registered_services[service_name] = {
                "service_instance": service_instance,
                "metadata": service_metadata,
                "service_id": service_id,
                "registered_at": self.clock.now_iso(),
                "status": "active"
            }
            
            self.logger.info(f"Service registered: {service_name}")
            return {
                "success": True,
                "service_name": service_name,
                "service_id": service_id,
                "message": "Service registered successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to register service: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get service by name.
        
        Args:
            service_name: Name of the service
        
        Returns:
            Optional[Dict[str, Any]]: Service registration or None if not found
        """
        return self.registered_services.get(service_name)
    
    async def list_services(self, realm: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List services with optional filters.
        
        Args:
            realm: Optional realm filter
        
        Returns:
            List[Dict[str, Any]]: List of service registrations
        """
        services = list(self.registered_services.values())
        
        if realm:
            services = [
                s for s in services
                if s.get("metadata", {}).get("realm") == realm
            ]
        
        return services
    
    async def update_service(
        self,
        service_name: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update service metadata.
        
        Args:
            service_name: Name of the service
            updates: Updates to apply
        
        Returns:
            Dict with update result
        """
        try:
            if service_name not in self.registered_services:
                return {"success": False, "error": "Service not found"}
            
            # Merge updates
            current_metadata = self.registered_services[service_name]["metadata"]
            updated_metadata = {**current_metadata, **updates}
            self.registered_services[service_name]["metadata"] = updated_metadata
            self.registered_services[service_name]["updated_at"] = self.clock.now_iso()
            
            # Update in Consul if service discovery available
            if self.service_discovery:
                service_id = self.registered_services[service_name].get("service_id")
                if service_id:
                    # Re-register with updated metadata
                    service_info = {
                        "service_id": service_id,
                        "service_name": service_name,
                        "service_type": updated_metadata.get("service_type", "unknown"),
                        "address": updated_metadata.get("address", "localhost"),
                        "port": updated_metadata.get("port", 8000),
                        "tags": updated_metadata.get("tags", []),
                        "meta": {
                            "capabilities": ",".join(updated_metadata.get("capabilities", [])),
                            "endpoints": ",".join(updated_metadata.get("endpoints", [])),
                            "realm": updated_metadata.get("realm", "unknown"),
                            "updated_at": self.clock.now_iso()
                        }
                    }
                    await self.service_discovery.register_service(service_info)
            
            self.logger.info(f"Service updated: {service_name}")
            return {"success": True, "message": "Service updated successfully"}
            
        except Exception as e:
            self.logger.error(f"Failed to update service: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def deregister_service(self, service_name: str) -> bool:
        """
        Deregister a service.
        
        Args:
            service_name: Name of the service to deregister
        
        Returns:
            bool: True if deregistration successful
        """
        try:
            if service_name not in self.registered_services:
                self.logger.warning(f"Service not found: {service_name}")
                return False
            
            # Deregister from Consul
            service_id = self.registered_services[service_name].get("service_id")
            if self.service_discovery and service_id:
                await self.service_discovery.deregister_service(service_id)
            
            # Remove from local cache
            del self.registered_services[service_name]
            
            self.logger.info(f"Service deregistered: {service_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deregister service: {e}", exc_info=True)
            return False
