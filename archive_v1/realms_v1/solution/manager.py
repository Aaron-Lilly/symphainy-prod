"""
Solution Realm Manager - Lifecycle and Registration

WHAT (Solution Realm): I manage Solution Realm lifecycle
HOW (Manager): I register capabilities with Curator and bind to Runtime
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from symphainy_platform.foundations.curator.models.capability_definition import CapabilityDefinition


class SolutionRealmManager:
    """
    Solution Realm Manager - Lifecycle and Registration.
    
    Manages Solution Realm lifecycle:
    - Registers capabilities with Curator
    - Binds realm to Runtime lifecycle
    - Coordinates realm initialization
    - Registers agents with Agent Foundation Service
    """
    
    def __init__(
        self,
        curator: Any,
        solution_orchestrator: Any,
        agent_foundation: Optional[Any] = None,
        runtime_service: Optional[Any] = None
    ):
        """
        Initialize Solution Realm Manager.
        
        Args:
            curator: Curator Foundation Service
            solution_orchestrator: Solution Orchestrator instance
            agent_foundation: Agent Foundation Service (for agent registration)
            runtime_service: Optional Runtime Service (for future integration)
        """
        self.curator = curator
        self.solution_orchestrator = solution_orchestrator
        self.agent_foundation = agent_foundation
        self.runtime_service = runtime_service
        self.logger = get_logger(self.__class__.__name__)
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize and register Solution Realm capabilities.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            self.logger.warning("Solution Realm Manager already initialized")
            return True
        
        try:
            self.logger.info("Initializing Solution Realm Manager...")
            
            # Register capabilities with Curator
            await self._register_capabilities()
            
            self._initialized = True
            self.logger.info("✅ Solution Realm Manager initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Solution Realm Manager: {e}", exc_info=True)
            return False
    
    async def register_agent(self, agent: Any) -> bool:
        """
        Register an agent with Agent Foundation Service.
        
        Args:
            agent: Agent instance to register
        
        Returns:
            bool: True if registration successful, False otherwise
        """
        if not self.agent_foundation:
            self.logger.warning("Agent Foundation Service not available, skipping agent registration")
            return False
        
        try:
            success = await self.agent_foundation.register_agent(agent)
            if success:
                self.logger.info(f"✅ Registered agent: {agent.agent_name}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_name}: {e}", exc_info=True)
            return False
    
    async def _register_capabilities(self) -> None:
        """Register Solution Realm capabilities with Curator."""
        try:
            # Register solution.generate_summary_visual capability
            summary_visual_capability = CapabilityDefinition(
                capability_name="solution_generate_summary_visual",
                service_name="solution_realm",
                protocol_name="SolutionOrchestrator",
                description="Generate summary visual from realm outputs",
                realm="solution",
                contracts={
                    "soa_api": {
                        "api_name": "solution_generate_summary_visual",
                        "endpoint": "/api/v1/solution/visual/summary",
                        "method": "POST",
                        "handler": "SolutionOrchestrator.generate_summary_visual"
                    }
                },
                semantic_mapping={
                    "domain_capability": "solution.generate_summary_visual",
                    "user_journey": "generate_realm_summary_visual"
                },
                inputs={
                    "realm_outputs": "Dict[str, Any]",
                    "visualization_type": "str"
                },
                outputs={
                    "visual_reference": "str",
                    "visual_metadata": "Dict[str, Any]"
                },
                determinism="deterministic"
            )
            
            await self.curator.capability_registry.register_capability(summary_visual_capability)
            self.logger.info("✅ Registered solution.generate_summary_visual capability")
            
            # Register solution.generate_roadmap capability
            generate_roadmap_capability = CapabilityDefinition(
                capability_name="solution_generate_roadmap",
                service_name="solution_realm",
                protocol_name="SolutionOrchestrator",
                description="Generate strategic roadmap from realm outputs",
                realm="solution",
                contracts={
                    "soa_api": {
                        "api_name": "solution_generate_roadmap",
                        "endpoint": "/api/v1/solution/roadmap/generate",
                        "method": "POST",
                        "handler": "SolutionOrchestrator.generate_roadmap"
                    }
                },
                semantic_mapping={
                    "domain_capability": "solution.generate_roadmap",
                    "user_journey": "generate_strategic_roadmap"
                },
                inputs={
                    "realm_outputs": "Dict[str, Any]",
                    "business_context": "Dict[str, Any]",
                    "options": "Optional[Dict[str, Any]]"
                },
                outputs={
                    "roadmap_reference": "str",
                    "roadmap_metadata": "Dict[str, Any]"
                },
                determinism="non-deterministic"  # Uses agent reasoning
            )
            
            await self.curator.capability_registry.register_capability(generate_roadmap_capability)
            self.logger.info("✅ Registered solution.generate_roadmap capability")
            
            # Register solution.generate_poc_proposal capability
            generate_poc_capability = CapabilityDefinition(
                capability_name="solution_generate_poc_proposal",
                service_name="solution_realm",
                protocol_name="SolutionOrchestrator",
                description="Generate POC proposal from realm outputs",
                realm="solution",
                contracts={
                    "soa_api": {
                        "api_name": "solution_generate_poc_proposal",
                        "endpoint": "/api/v1/solution/poc/generate",
                        "method": "POST",
                        "handler": "SolutionOrchestrator.generate_poc_proposal"
                    }
                },
                semantic_mapping={
                    "domain_capability": "solution.generate_poc_proposal",
                    "user_journey": "generate_poc_proposal"
                },
                inputs={
                    "realm_outputs": "Dict[str, Any]",
                    "business_context": "Dict[str, Any]",
                    "poc_type": "str",
                    "options": "Optional[Dict[str, Any]]"
                },
                outputs={
                    "poc_reference": "str",
                    "poc_metadata": "Dict[str, Any]"
                },
                determinism="non-deterministic"  # Uses agent reasoning
            )
            
            await self.curator.capability_registry.register_capability(generate_poc_capability)
            self.logger.info("✅ Registered solution.generate_poc_proposal capability")
            
            # Register solution.create_platform_solution capability
            create_solution_capability = CapabilityDefinition(
                capability_name="solution_create_platform_solution",
                service_name="solution_realm",
                protocol_name="SolutionOrchestrator",
                description="Create platform solution from roadmap/POC",
                realm="solution",
                contracts={
                    "soa_api": {
                        "api_name": "solution_create_platform_solution",
                        "endpoint": "/api/v1/solution/solution/create",
                        "method": "POST",
                        "handler": "SolutionOrchestrator.create_platform_solution"
                    }
                },
                semantic_mapping={
                    "domain_capability": "solution.create_platform_solution",
                    "user_journey": "create_platform_solution"
                },
                inputs={
                    "roadmap_reference": "Optional[str]",
                    "poc_reference": "Optional[str]",
                    "options": "Optional[Dict[str, Any]]"
                },
                outputs={
                    "solution_reference": "str",
                    "solution_metadata": "Dict[str, Any]"
                },
                determinism="non-deterministic"  # Uses agent reasoning
            )
            
            await self.curator.capability_registry.register_capability(create_solution_capability)
            self.logger.info("✅ Registered solution.create_platform_solution capability")
            
        except Exception as e:
            self.logger.error(f"Failed to register capabilities: {e}", exc_info=True)
            raise
    
    async def shutdown(self) -> bool:
        """
        Shutdown Solution Realm Manager.
        
        Returns:
            bool: True if shutdown successful
        """
        try:
            self.logger.info("Shutting down Solution Realm Manager...")
            self._initialized = False
            self.logger.info("✅ Solution Realm Manager shut down successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to shutdown Solution Realm Manager: {e}", exc_info=True)
            return False
    
    def is_initialized(self) -> bool:
        """Check if manager is initialized."""
        return self._initialized
