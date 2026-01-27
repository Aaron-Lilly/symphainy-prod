"""
Curator Foundation Service

Orchestrates all platform registries: services, agents, tools, SOA APIs, and capabilities.

WHAT (Foundation Role): I provide platform-wide registry services to the platform
HOW (Foundation Implementation): I maintain central registries for services, agents, tools, SOA APIs, and capabilities

Curator is NOT execution - it's the platform's capability ontology.
Runtime executes the capability, Curator just registers/looks up.
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger

from .registry.capability_registry import CapabilityRegistry
from .registry.service_registry import ServiceRegistry
from .registry.agent_registry import AgentRegistry
from .registry.tool_registry import ToolRegistry
from .registry.soa_api_registry import SOAAPIRegistry
from .models.capability_definition import CapabilityDefinition


class CuratorFoundationService:
    """
    Curator Foundation Service - Platform Registry Coordinator
    
    Manages all platform registries:
    - Service Registry (service instances)
    - Capability Registry (what services can do)
    - Agent Registry (agent capabilities)
    - Tool Registry (MCP tools)
    - SOA API Registry (realm-to-realm APIs)
    """
    
    def __init__(self, public_works_foundation: Optional[Any] = None):
        """
        Initialize Curator Foundation Service.
        
        Args:
            public_works_foundation: Optional Public Works Foundation (for service discovery)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works_foundation
        
        # Get service discovery abstraction from Public Works
        service_discovery = None
        if self.public_works:
            service_discovery = self.public_works.get_service_discovery_abstraction()
        
        # Initialize all registries
        self.service_registry = ServiceRegistry(service_discovery_abstraction=service_discovery)
        self.capability_registry = CapabilityRegistry()
        self.agent_registry = AgentRegistry()
        self.tool_registry = ToolRegistry()
        self.soa_api_registry = SOAAPIRegistry()
        
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize Curator Foundation Service.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            self.logger.warning("Curator Foundation already initialized")
            return True
        
        try:
            self.logger.info("Initializing Curator Foundation...")
            self._initialized = True
            self.logger.info("Curator Foundation initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Curator Foundation: {e}", exc_info=True)
            return False
    
    # ============================================================================
    # Service Registration
    # ============================================================================
    
    async def register_service(
        self,
        service_instance: Any,
        service_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register a service instance.
        
        Registers with:
        1. Service Registry (for Consul + local cache)
        2. Capability Registry (if capabilities provided)
        3. SOA API Registry (if SOA APIs provided)
        4. Tool Registry (if MCP tools provided)
        
        Args:
            service_instance: The service instance to register
            service_metadata: Service metadata including:
                - service_name (required)
                - service_type (required)
                - address (required)
                - port (required)
                - capabilities (optional)
                - soa_apis (optional)
                - mcp_tools (optional)
                - tags (optional)
                - realm (optional)
        
        Returns:
            Dict with registration result
        """
        return await self.service_registry.register_service(service_instance, service_metadata)
    
    async def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service by name."""
        return await self.service_registry.get_service(service_name)
    
    async def list_services(self, realm: Optional[str] = None) -> List[Dict[str, Any]]:
        """List services with optional filters."""
        return await self.service_registry.list_services(realm=realm)
    
    async def deregister_service(self, service_name: str) -> bool:
        """Deregister a service."""
        return await self.service_registry.deregister_service(service_name)
    
    # ============================================================================
    # Capability Registration
    # ============================================================================
    
    async def register_capability(self, capability: CapabilityDefinition) -> bool:
        """Register a capability."""
        return await self.capability_registry.register_capability(capability)
    
    async def get_capability(self, capability_name: str) -> Optional[CapabilityDefinition]:
        """Get capability by name."""
        return await self.capability_registry.get_capability(capability_name)
    
    async def lookup_capability_by_intent(self, intent: str) -> List[CapabilityDefinition]:
        """
        Lookup capabilities by intent.
        
        This is the core function: intent → capability lookup.
        """
        return await self.capability_registry.lookup_capability_by_intent(intent)
    
    async def list_capabilities(
        self,
        realm: Optional[str] = None,
        service_name: Optional[str] = None
    ) -> List[CapabilityDefinition]:
        """List capabilities with optional filters."""
        return await self.capability_registry.list_capabilities(realm=realm, service_name=service_name)
    
    async def unregister_capability(self, capability_name: str) -> bool:
        """Unregister a capability."""
        return await self.capability_registry.unregister_capability(capability_name)
    
    # ============================================================================
    # Agent Registration
    # ============================================================================
    
    async def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        characteristics: Dict[str, Any],
        contracts: Dict[str, Any]
    ) -> bool:
        """Register an agent."""
        return await self.agent_registry.register_agent(agent_id, agent_name, characteristics, contracts)
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID."""
        return await self.agent_registry.get_agent(agent_id)
    
    async def get_agent_by_name(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent by name."""
        return await self.agent_registry.get_agent_by_name(agent_name)
    
    async def list_agents(
        self,
        realm: Optional[str] = None,
        capability: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List agents with optional filters."""
        return await self.agent_registry.list_agents(realm=realm, capability=capability)
    
    async def deregister_agent(self, agent_id: str) -> bool:
        """Deregister an agent."""
        return await self.agent_registry.deregister_agent(agent_id)
    
    # ============================================================================
    # Tool Registration
    # ============================================================================
    
    async def register_mcp_tool(
        self,
        tool_name: str,
        tool_definition: Dict[str, Any],
        server_name: Optional[str] = None,
        realm: Optional[str] = None
    ) -> bool:
        """Register an MCP tool."""
        return await self.tool_registry.register_mcp_tool(tool_name, tool_definition, server_name, realm)
    
    async def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool by name."""
        return await self.tool_registry.get_tool(tool_name)
    
    async def list_tools(
        self,
        realm: Optional[str] = None,
        server_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List tools with optional filters."""
        return await self.tool_registry.list_tools(realm=realm, server_name=server_name)
    
    async def register_mcp_server(
        self,
        server_name: str,
        server_instance: Any,
        tools: List[str],
        realm: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register an MCP server."""
        return await self.tool_registry.register_mcp_server(server_name, server_instance, tools, realm, metadata)
    
    async def get_server(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get MCP server by name."""
        return await self.tool_registry.get_server(server_name)
    
    async def deregister_tool(self, tool_name: str) -> bool:
        """Deregister an MCP tool."""
        return await self.tool_registry.deregister_tool(tool_name)
    
    async def deregister_server(self, server_name: str) -> bool:
        """Deregister an MCP server."""
        return await self.tool_registry.deregister_server(server_name)
    
    # ============================================================================
    # SOA API Registration
    # ============================================================================
    
    async def register_soa_api(
        self,
        api_name: str,
        service_name: str,
        handler: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register an SOA API endpoint."""
        return await self.soa_api_registry.register_soa_api(api_name, service_name, handler, metadata)
    
    async def get_api(self, api_name: str, service_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get SOA API by name."""
        return await self.soa_api_registry.get_api(api_name, service_name)
    
    async def list_apis(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List SOA APIs with optional filters."""
        return await self.soa_api_registry.list_apis(service_name=service_name)
    
    async def deregister_api(self, api_name: str, service_name: Optional[str] = None) -> bool:
        """Deregister an SOA API."""
        return await self.soa_api_registry.deregister_api(api_name, service_name)
    
    def is_initialized(self) -> bool:
        """Check if foundation is initialized."""
        return self._initialized
