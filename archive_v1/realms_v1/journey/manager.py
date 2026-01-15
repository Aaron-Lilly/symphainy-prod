"""
Journey Realm Manager - Lifecycle and Registration

WHAT (Journey Realm): I manage Journey Realm lifecycle
HOW (Manager): I register capabilities with Curator and bind to Runtime
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from symphainy_platform.foundations.curator.models.capability_definition import CapabilityDefinition


class JourneyRealmManager:
    """
    Journey Realm Manager - Lifecycle and Registration.
    
    Manages Journey Realm lifecycle:
    - Registers capabilities with Curator
    - Binds realm to Runtime lifecycle
    - Coordinates realm initialization
    - Registers agents with Agent Foundation Service
    """
    
    def __init__(
        self,
        curator: Any,
        journey_orchestrator: Any,
        agent_foundation: Optional[Any] = None,
        runtime_service: Optional[Any] = None
    ):
        """
        Initialize Journey Realm Manager.
        
        Args:
            curator: Curator Foundation Service
            journey_orchestrator: Journey Orchestrator instance
            agent_foundation: Agent Foundation Service (for agent registration)
            runtime_service: Optional Runtime Service (for future integration)
        """
        self.curator = curator
        self.journey_orchestrator = journey_orchestrator
        self.agent_foundation = agent_foundation
        self.runtime_service = runtime_service
        self.logger = get_logger(self.__class__.__name__)
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize and register Journey Realm capabilities.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            self.logger.warning("Journey Realm Manager already initialized")
            return True
        
        try:
            self.logger.info("Initializing Journey Realm Manager...")
            
            # Register capabilities with Curator
            await self._register_capabilities()
            
            self._initialized = True
            self.logger.info("✅ Journey Realm Manager initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Journey Realm Manager: {e}", exc_info=True)
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
        """Register Journey Realm capabilities with Curator."""
        try:
            # Register journey.create_sop_from_workflow capability
            sop_from_workflow_capability = CapabilityDefinition(
                capability_name="journey_create_sop_from_workflow",
                service_name="journey_realm",
                protocol_name="JourneyOrchestrator",
                description="Create SOP from workflow",
                realm="journey",
                contracts={
                    "soa_api": {
                        "api_name": "journey_create_sop_from_workflow",
                        "endpoint": "/api/v1/journey/sop/from-workflow",
                        "method": "POST",
                        "handler": "JourneyOrchestrator.create_sop_from_workflow"
                    }
                },
                semantic_mapping={
                    "domain_capability": "journey.create_sop_from_workflow",
                    "user_journey": "convert_workflow_to_sop"
                },
                inputs={
                    "workflow_reference": "str",
                    "session_id": "str",
                    "tenant_id": "str",
                    "options": "Optional[Dict[str, Any]]"
                },
                outputs={
                    "sop_reference": "str",
                    "sop_metadata": "Dict[str, Any]"
                },
                determinism="deterministic"
            )
            
            await self.curator.capability_registry.register_capability(sop_from_workflow_capability)
            self.logger.info("✅ Registered journey.create_sop_from_workflow capability")
            
            # Register journey.create_workflow_from_sop capability
            workflow_from_sop_capability = CapabilityDefinition(
                capability_name="journey_create_workflow_from_sop",
                service_name="journey_realm",
                protocol_name="JourneyOrchestrator",
                description="Create workflow from SOP",
                realm="journey",
                contracts={
                    "soa_api": {
                        "api_name": "journey_create_workflow_from_sop",
                        "endpoint": "/api/v1/journey/workflow/from-sop",
                        "method": "POST",
                        "handler": "JourneyOrchestrator.create_workflow_from_sop"
                    }
                },
                semantic_mapping={
                    "domain_capability": "journey.create_workflow_from_sop",
                    "user_journey": "convert_sop_to_workflow"
                },
                inputs={
                    "sop_reference": "str",
                    "session_id": "str",
                    "tenant_id": "str",
                    "options": "Optional[Dict[str, Any]]"
                },
                outputs={
                    "workflow_reference": "str",
                    "workflow_metadata": "Dict[str, Any]"
                },
                determinism="deterministic"
            )
            
            await self.curator.capability_registry.register_capability(workflow_from_sop_capability)
            self.logger.info("✅ Registered journey.create_workflow_from_sop capability")
            
            # Register journey.start_sop_wizard capability
            start_wizard_capability = CapabilityDefinition(
                capability_name="journey_start_sop_wizard",
                service_name="journey_realm",
                protocol_name="JourneyOrchestrator",
                description="Start SOP creation wizard",
                realm="journey",
                contracts={
                    "soa_api": {
                        "api_name": "journey_start_sop_wizard",
                        "endpoint": "/api/v1/journey/sop/wizard/start",
                        "method": "POST",
                        "handler": "JourneyOrchestrator.start_sop_wizard"
                    }
                },
                semantic_mapping={
                    "domain_capability": "journey.start_sop_wizard",
                    "user_journey": "start_sop_creation_wizard"
                },
                inputs={
                    "session_id": "str",
                    "tenant_id": "str",
                    "initial_description": "Optional[str]"
                },
                outputs={
                    "wizard_session_token": "str",
                    "wizard_state": "Dict[str, Any]"
                },
                determinism="deterministic"
            )
            
            await self.curator.capability_registry.register_capability(start_wizard_capability)
            self.logger.info("✅ Registered journey.start_sop_wizard capability")
            
            # Register journey.analyze_coexistence capability
            analyze_coexistence_capability = CapabilityDefinition(
                capability_name="journey_analyze_coexistence",
                service_name="journey_realm",
                protocol_name="JourneyOrchestrator",
                description="Analyze coexistence opportunities",
                realm="journey",
                contracts={
                    "soa_api": {
                        "api_name": "journey_analyze_coexistence",
                        "endpoint": "/api/v1/journey/coexistence/analyze",
                        "method": "POST",
                        "handler": "JourneyOrchestrator.analyze_coexistence"
                    }
                },
                semantic_mapping={
                    "domain_capability": "journey.analyze_coexistence",
                    "user_journey": "analyze_human_ai_coexistence"
                },
                inputs={
                    "session_id": "str",
                    "tenant_id": "str",
                    "workflow_reference": "Optional[str]",
                    "sop_reference": "Optional[str]",
                    "options": "Optional[Dict[str, Any]]"
                },
                outputs={
                    "analysis_reference": "str",
                    "analysis_metadata": "Dict[str, Any]"
                },
                determinism="non-deterministic"  # Uses agent reasoning
            )
            
            await self.curator.capability_registry.register_capability(analyze_coexistence_capability)
            self.logger.info("✅ Registered journey.analyze_coexistence capability")
            
            # Register journey.generate_blueprint capability
            generate_blueprint_capability = CapabilityDefinition(
                capability_name="journey_generate_blueprint",
                service_name="journey_realm",
                protocol_name="JourneyOrchestrator",
                description="Generate coexistence blueprint",
                realm="journey",
                contracts={
                    "soa_api": {
                        "api_name": "journey_generate_blueprint",
                        "endpoint": "/api/v1/journey/blueprint/generate",
                        "method": "POST",
                        "handler": "JourneyOrchestrator.generate_coexistence_blueprint"
                    }
                },
                semantic_mapping={
                    "domain_capability": "journey.generate_blueprint",
                    "user_journey": "generate_coexistence_blueprint"
                },
                inputs={
                    "analysis_reference": "str",
                    "session_id": "str",
                    "tenant_id": "str",
                    "options": "Optional[Dict[str, Any]]"
                },
                outputs={
                    "blueprint_reference": "str",
                    "blueprint_metadata": "Dict[str, Any]"
                },
                determinism="non-deterministic"  # Uses agent reasoning
            )
            
            await self.curator.capability_registry.register_capability(generate_blueprint_capability)
            self.logger.info("✅ Registered journey.generate_blueprint capability")
            
            # Register journey.create_platform_journey capability
            create_journey_capability = CapabilityDefinition(
                capability_name="journey_create_platform_journey",
                service_name="journey_realm",
                protocol_name="JourneyOrchestrator",
                description="Create platform journey from blueprint",
                realm="journey",
                contracts={
                    "soa_api": {
                        "api_name": "journey_create_platform_journey",
                        "endpoint": "/api/v1/journey/platform-journey/create",
                        "method": "POST",
                        "handler": "JourneyOrchestrator.create_platform_journey"
                    }
                },
                semantic_mapping={
                    "domain_capability": "journey.create_platform_journey",
                    "user_journey": "create_platform_journey"
                },
                inputs={
                    "blueprint_reference": "str",
                    "session_id": "str",
                    "tenant_id": "str",
                    "options": "Optional[Dict[str, Any]]"
                },
                outputs={
                    "journey_reference": "str",
                    "journey_metadata": "Dict[str, Any]"
                },
                determinism="non-deterministic"  # Uses agent reasoning
            )
            
            await self.curator.capability_registry.register_capability(create_journey_capability)
            self.logger.info("✅ Registered journey.create_platform_journey capability")
            
        except Exception as e:
            self.logger.error(f"Failed to register capabilities: {e}", exc_info=True)
            raise
    
    async def shutdown(self) -> bool:
        """
        Shutdown Journey Realm Manager.
        
        Returns:
            bool: True if shutdown successful
        """
        try:
            self.logger.info("Shutting down Journey Realm Manager...")
            self._initialized = False
            self.logger.info("✅ Journey Realm Manager shut down successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to shutdown Journey Realm Manager: {e}", exc_info=True)
            return False
    
    def is_initialized(self) -> bool:
        """Check if manager is initialized."""
        return self._initialized
