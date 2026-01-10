"""
Public Works Foundation Service

Orchestrates all infrastructure adapters and abstractions.
This is Layer 4 of the 5-layer architecture.

WHAT (Foundation Role): I provide infrastructure capabilities to all platform components
HOW (Foundation Implementation): I use 5-layer architecture with dependency injection

Rules:
- Foundations never call realms
- Foundations never reason
- Foundations are deterministic
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from .adapters.redis_adapter import RedisAdapter
from .adapters.consul_adapter import ConsulAdapter
from .abstractions.state_abstraction import StateManagementAbstraction
from .abstractions.service_discovery_abstraction import ServiceDiscoveryAbstraction
from .protocols.state_protocol import StateManagementProtocol
from .protocols.service_discovery_protocol import ServiceDiscoveryProtocol


class PublicWorksFoundationService:
    """
    Public Works Foundation Service - 5-Layer Architecture
    
    This service implements the 5-layer architecture pattern,
    providing infrastructure capabilities to all platform components.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Public Works Foundation Service.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = get_logger(self.__class__.__name__)
        
        # Layer 0: Infrastructure Adapters
        self.redis_adapter: Optional[RedisAdapter] = None
        self.consul_adapter: Optional[ConsulAdapter] = None
        # ArangoDB adapter will be added when needed
        
        # Layer 1: Infrastructure Abstractions
        self.state_abstraction: Optional[StateManagementAbstraction] = None
        self.service_discovery_abstraction: Optional[ServiceDiscoveryAbstraction] = None
        
        # Initialization flag
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize all infrastructure components.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            self.logger.warning("Public Works Foundation already initialized")
            return True
        
        try:
            self.logger.info("Initializing Public Works Foundation...")
            
            # Layer 0: Create adapters
            await self._create_adapters()
            
            # Layer 1: Create abstractions
            await self._create_abstractions()
            
            self._initialized = True
            self.logger.info("Public Works Foundation initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Public Works Foundation: {e}", exc_info=True)
            return False
    
    async def _create_adapters(self):
        """Create all infrastructure adapters (Layer 0)."""
        self.logger.info("Creating infrastructure adapters...")
        
        # Redis adapter
        redis_config = self.config.get("redis", {})
        if redis_config:
            self.redis_adapter = RedisAdapter(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                db=redis_config.get("db", 0),
                password=redis_config.get("password")
            )
            await self.redis_adapter.connect()
            self.logger.info("Redis adapter created")
        else:
            self.logger.warning("Redis configuration not provided, Redis adapter not created")
        
        # Consul adapter
        consul_config = self.config.get("consul", {})
        if consul_config:
            self.consul_adapter = ConsulAdapter(
                host=consul_config.get("host", "localhost"),
                port=consul_config.get("port", 8500),
                token=consul_config.get("token")
            )
            if self.consul_adapter.connect():
                self.logger.info("Consul adapter created")
            else:
                self.logger.warning("Consul adapter connection failed")
        else:
            self.logger.warning("Consul configuration not provided, Consul adapter not created")
        
        # ArangoDB adapter will be added when needed
    
    async def _create_abstractions(self):
        """Create all infrastructure abstractions (Layer 1)."""
        self.logger.info("Creating infrastructure abstractions...")
        
        # State management abstraction
        self.state_abstraction = StateManagementAbstraction(
            redis_adapter=self.redis_adapter,
            arango_adapter=None  # Will be added when ArangoDB adapter is ready
        )
        self.logger.info("State management abstraction created")
        
        # Service discovery abstraction
        self.service_discovery_abstraction = ServiceDiscoveryAbstraction(
            consul_adapter=self.consul_adapter
        )
        self.logger.info("Service discovery abstraction created")
    
    async def shutdown(self):
        """Shutdown all infrastructure components."""
        self.logger.info("Shutting down Public Works Foundation...")
        
        if self.redis_adapter:
            await self.redis_adapter.disconnect()
        
        if self.consul_adapter:
            self.consul_adapter.disconnect()
        
        self._initialized = False
        self.logger.info("Public Works Foundation shut down")
    
    # ============================================================================
    # Abstraction Access Methods
    # ============================================================================
    
    def get_state_abstraction(self) -> Optional[StateManagementProtocol]:
        """
        Get state management abstraction.
        
        Returns:
            Optional[StateManagementProtocol]: State management abstraction or None
        """
        return self.state_abstraction
    
    def get_service_discovery_abstraction(self) -> Optional[ServiceDiscoveryProtocol]:
        """
        Get service discovery abstraction.
        
        Returns:
            Optional[ServiceDiscoveryProtocol]: Service discovery abstraction or None
        """
        return self.service_discovery_abstraction
    
    def is_initialized(self) -> bool:
        """Check if foundation is initialized."""
        return self._initialized
