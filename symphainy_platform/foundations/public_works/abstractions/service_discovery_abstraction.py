"""
Service Discovery Abstraction - Business Logic Implementation (Layer 1)

Implements service discovery operations across different backends.
Coordinates between Consul, Istio, Linkerd adapters.

WHAT (Infrastructure Role): I manage service registration and discovery
HOW (Infrastructure Implementation): I coordinate between service discovery adapters
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from utilities import get_logger, get_clock

from ..protocols.service_discovery_protocol import (
    ServiceDiscoveryProtocol,
    ServiceRegistration,
    ServiceInfo
)
from ..adapters.consul_adapter import ConsulAdapter


class ServiceDiscoveryAbstraction(ServiceDiscoveryProtocol):
    """
    Service discovery abstraction with business logic.
    
    Coordinates between Consul (current) and future service mesh technologies.
    For Phase 2, we start with Consul only. Other adapters will be added when needed.
    """
    
    def __init__(self, consul_adapter: Optional[ConsulAdapter] = None):
        """
        Initialize service discovery abstraction.
        
        Args:
            consul_adapter: Consul adapter for service discovery
        """
        self.consul_adapter = consul_adapter
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("Service Discovery Abstraction initialized")
    
    async def register_service(self, service_info: Dict[str, Any]) -> Optional[ServiceRegistration]:
        """
        Register a service with business logic validation.
        
        Args:
            service_info: Service information including:
                - service_name (required)
                - service_type (required)
                - address (required)
                - port (required)
                - tags (optional)
                - meta (optional)
                - health_check_endpoint (optional)
        
        Returns:
            ServiceRegistration: Registration result or None if failed
        """
        try:
            # Validate required fields
            required_fields = ["service_name", "service_type", "address", "port"]
            for field in required_fields:
                if field not in service_info:
                    self.logger.error(f"Missing required field '{field}' in service_info")
                    return None
            
            service_name = service_info["service_name"]
            
            # Generate service ID (unique per instance)
            service_id = service_info.get("service_id")
            if not service_id:
                service_id = f"{service_name}-{service_info['address']}-{service_info['port']}"
            
            # Prepare health check if specified
            check = None
            if service_info.get("health_check_endpoint"):
                check = {
                    "http": f"http://{service_info['address']}:{service_info['port']}{service_info['health_check_endpoint']}",
                    "interval": "10s",
                    "timeout": "5s"
                }
            
            # Register with Consul
            if self.consul_adapter:
                success = self.consul_adapter.register_service(
                    service_name=service_name,
                    service_id=service_id,
                    address=service_info["address"],
                    port=service_info["port"],
                    tags=service_info.get("tags", []),
                    meta=service_info.get("meta", {}),
                    check=check
                )
                
                if success:
                    self.logger.info(f"Service registered: {service_name} ({service_id})")
                    return ServiceRegistration(
                        service_id=service_id,
                        service_name=service_name,
                        address=service_info["address"],
                        port=service_info["port"],
                        success=True
                    )
                else:
                    self.logger.error(f"Failed to register service: {service_name}")
                    return ServiceRegistration(
                        service_id=service_id,
                        service_name=service_name,
                        address=service_info["address"],
                        port=service_info["port"],
                        success=False,
                        error="Consul registration failed"
                    )
            else:
                self.logger.error("Consul adapter not available")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to register service: {e}", exc_info=True)
            return None
    
    async def discover_service(self, service_name: str) -> List[ServiceInfo]:
        """
        Discover service instances by name.
        
        Args:
            service_name: Name of the service to discover
        
        Returns:
            List[ServiceInfo]: List of service instances
        """
        try:
            if not self.consul_adapter:
                return []
            
            services = self.consul_adapter.discover_service(service_name)
            
            result = []
            for service in services:
                result.append(ServiceInfo(
                    service_id=service["service_id"],
                    service_name=service["service_name"],
                    address=service["address"],
                    port=service["port"],
                    tags=service["tags"],
                    meta=service["meta"],
                    health_status=service["health_status"]
                ))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to discover service {service_name}: {e}", exc_info=True)
            return []
    
    async def deregister_service(self, service_id: str) -> bool:
        """
        Deregister a service by service ID.
        
        Args:
            service_id: Service identifier
        
        Returns:
            bool: True if deregistration successful
        """
        try:
            if not self.consul_adapter:
                return False
            
            success = self.consul_adapter.deregister_service(service_id)
            if success:
                self.logger.info(f"Service deregistered: {service_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to deregister service {service_id}: {e}", exc_info=True)
            return False
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Get health status for a service.
        
        Args:
            service_name: Name of the service
        
        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            if not self.consul_adapter:
                return {}
            
            return self.consul_adapter.get_service_health(service_name)
            
        except Exception as e:
            self.logger.error(f"Failed to get service health for {service_name}: {e}", exc_info=True)
            return {}
