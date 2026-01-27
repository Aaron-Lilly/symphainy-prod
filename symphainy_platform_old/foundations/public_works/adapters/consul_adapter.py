"""
Consul Service Discovery Adapter - Raw Technology Client (Layer 0)

Raw Consul client wrapper with no business logic.
This is the raw technology layer for Consul operations.

WHAT (Infrastructure Role): I provide raw Consul client operations
HOW (Infrastructure Implementation): I use real Consul client with no business logic
"""

import json
import logging
from typing import Dict, Any, Optional, List
from consul import Consul
from consul.base import ConsulException

from utilities import get_logger


class ConsulAdapter:
    """
    Raw Consul client wrapper - no business logic.
    
    This adapter provides direct access to Consul operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self, host: str = "localhost", port: int = 8500, token: Optional[str] = None):
        """
        Initialize Consul adapter with real connection.
        
        Args:
            host: Consul host
            port: Consul port
            token: Optional Consul ACL token
        """
        self.host = host
        self.port = port
        self.token = token
        self._client: Optional[Consul] = None
        self.logger = get_logger(self.__class__.__name__)
    
    def connect(self) -> bool:
        """Connect to Consul."""
        try:
            self._client = Consul(host=self.host, port=self.port, token=self.token)
            # Test connection
            self._client.agent.self()
            self.logger.info(f"Consul adapter connected: {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Consul: {e}", exc_info=True)
            return False
    
    def disconnect(self):
        """Disconnect from Consul."""
        # Consul client doesn't have explicit disconnect
        self._client = None
    
    # ============================================================================
    # RAW SERVICE REGISTRATION OPERATIONS
    # ============================================================================
    
    def register_service(
        self,
        service_name: str,
        service_id: str,
        address: str,
        port: int,
        tags: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None,
        check: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Raw Consul service registration - no business logic.
        
        Args:
            service_name: Name of the service
            service_id: Unique service identifier
            address: Service address
            port: Service port
            tags: Optional service tags
            meta: Optional service metadata
            check: Optional health check configuration
        
        Returns:
            bool: True if registration successful
        """
        if not self._client:
            return False
        
        try:
            # Convert meta dict to tags (python-consul limitation)
            enriched_tags = tags.copy() if tags else []
            if meta:
                for k, v in meta.items():
                    if isinstance(v, (str, int, float, bool)):
                        enriched_tags.append(f"{k}:{v}")
                    elif isinstance(v, (list, tuple)):
                        enriched_tags.append(f"{k}:{','.join(str(item) for item in v)}")
                    elif isinstance(v, dict):
                        enriched_tags.append(f"{k}:{json.dumps(v)}")
            
            # Register service
            self._client.agent.service.register(
                name=service_name,
                service_id=service_id,
                address=address,
                port=port,
                tags=enriched_tags,
                check=check
            )
            
            self.logger.debug(f"Service registered with Consul: {service_name} ({service_id})")
            return True
        except ConsulException as e:
            self.logger.error(f"Consul service registration error: {e}")
            return False
    
    def deregister_service(self, service_id: str) -> bool:
        """
        Raw Consul service deregistration - no business logic.
        
        Args:
            service_id: Service identifier
        
        Returns:
            bool: True if deregistration successful
        """
        if not self._client:
            return False
        
        try:
            self._client.agent.service.deregister(service_id)
            self.logger.debug(f"Service deregistered from Consul: {service_id}")
            return True
        except ConsulException as e:
            self.logger.error(f"Consul service deregistration error: {e}")
            return False
    
    # ============================================================================
    # RAW SERVICE DISCOVERY OPERATIONS
    # ============================================================================
    
    def discover_service(self, service_name: str) -> List[Dict[str, Any]]:
        """
        Raw Consul service discovery - no business logic.
        
        Args:
            service_name: Name of the service to discover
        
        Returns:
            List[Dict[str, Any]]: List of service instances
        """
        if not self._client:
            return []
        
        try:
            # Get healthy services
            _, services = self._client.health.service(service_name, passing=True)
            
            result = []
            for service in services:
                service_info = service.get("Service", {})
                checks = service.get("Checks", [])
                
                # Determine health status
                health_status = "passing"
                for check in checks:
                    if check.get("Status") != "passing":
                        health_status = check.get("Status", "unknown")
                        break
                
                # Parse tags back to meta (reverse of registration)
                meta = {}
                tags = service_info.get("Tags", [])
                for tag in tags:
                    if ":" in tag:
                        key, value = tag.split(":", 1)
                        # Try to parse JSON values
                        try:
                            meta[key] = json.loads(value)
                        except json.JSONDecodeError:
                            meta[key] = value
                
                result.append({
                    "service_id": service_info.get("ID"),
                    "service_name": service_info.get("Service"),
                    "address": service_info.get("Address"),
                    "port": service_info.get("Port"),
                    "tags": tags,
                    "meta": meta,
                    "health_status": health_status
                })
            
            return result
        except ConsulException as e:
            self.logger.error(f"Consul service discovery error: {e}")
            return []
    
    def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Raw Consul service health check - no business logic.
        
        Args:
            service_name: Name of the service
        
        Returns:
            Dict[str, Any]: Health status information
        """
        if not self._client:
            return {}
        
        try:
            _, services = self._client.health.service(service_name)
            
            health_info = {
                "service_name": service_name,
                "instances": [],
                "total_instances": len(services),
                "passing": 0,
                "warning": 0,
                "critical": 0
            }
            
            for service in services:
                checks = service.get("Checks", [])
                status = "passing"
                for check in checks:
                    check_status = check.get("Status", "unknown")
                    if check_status == "critical":
                        status = "critical"
                        health_info["critical"] += 1
                        break
                    elif check_status == "warning":
                        status = "warning"
                        health_info["warning"] += 1
                    else:
                        health_info["passing"] += 1
                
                health_info["instances"].append({
                    "service_id": service.get("Service", {}).get("ID"),
                    "status": status,
                    "checks": checks
                })
            
            return health_info
        except ConsulException as e:
            self.logger.error(f"Consul service health check error: {e}")
            return {}
