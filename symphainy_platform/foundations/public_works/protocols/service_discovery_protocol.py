"""
Service Discovery Protocol - Abstraction Contract

Defines the contract for service discovery operations across different backends.
This protocol enables swappability between Consul, Istio, Linkerd, etc.

WHAT (Infrastructure Role): I define how services should be discovered and registered
HOW (Infrastructure Implementation): I provide the interface for service discovery logic
"""

from typing import Protocol, Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ServiceRegistration:
    """Service registration result."""
    service_id: str
    service_name: str
    address: str
    port: int
    success: bool
    error: Optional[str] = None


@dataclass
class ServiceInfo:
    """Service information for discovery."""
    service_id: str
    service_name: str
    address: str
    port: int
    tags: List[str]
    meta: Dict[str, Any]
    health_status: str  # "passing", "warning", "critical"


class ServiceDiscoveryProtocol(Protocol):
    """
    Protocol for service discovery operations.
    
    This protocol defines how services should be registered, discovered,
    and managed across different service mesh technologies.
    """
    
    async def register_service(self, service_info: Dict[str, Any]) -> Optional[ServiceRegistration]:
        """
        Register a service with the service discovery backend.
        
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
        ...
    
    async def discover_service(self, service_name: str) -> List[ServiceInfo]:
        """
        Discover service instances by name.
        
        Args:
            service_name: Name of the service to discover
        
        Returns:
            List[ServiceInfo]: List of service instances
        """
        ...
    
    async def deregister_service(self, service_id: str) -> bool:
        """
        Deregister a service by service ID.
        
        Args:
            service_id: Service identifier
        
        Returns:
            bool: True if deregistration successful
        """
        ...
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Get health status for a service.
        
        Args:
            service_name: Name of the service
        
        Returns:
            Dict[str, Any]: Health status information
        """
        ...
