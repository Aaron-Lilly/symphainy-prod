"""
Journey Realm Foundation Service

Initializes and wires up all Journey Realm services, orchestrators, and agents.

WHAT (Journey Realm): I coordinate Journey Realm services
HOW (Foundation): I initialize and register all Journey services, orchestrators, and agents
"""

import logging
from typing import Dict, Any, Optional

from utilities import get_logger

from .orchestrators.journey_orchestrator import JourneyOrchestrator
from .manager import JourneyRealmManager
from .services.sop_builder_service.sop_builder_service import SOPBuilderService
from .services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService
from .services.coexistence_analysis_service.coexistence_analysis_service import CoexistenceAnalysisService

logger = get_logger(__name__)


class JourneyRealmFoundationService:
    """
    Journey Realm Foundation Service.
    
    Initializes and wires up all Journey Realm components:
    - Services (SOP Builder, Workflow Conversion, Coexistence Analysis)
    - Journey Orchestrator
    - Agents (Liaison, SOP Builder Wizard, Workflow Generator, Coexistence Analyzer)
    - Journey Realm Manager
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Any,
        curator: Optional[Any] = None,
        agent_foundation: Optional[Any] = None,
        runtime_service: Optional[Any] = None
    ):
        """
        Initialize Journey Realm Foundation Service.
        
        Args:
            state_surface: State Surface instance
            platform_gateway: Platform Gateway instance
            curator: Curator Foundation Service (for capability registration)
            agent_foundation: Agent Foundation Service (for agent registration)
            runtime_service: Runtime Service (for future integration)
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.curator = curator
        self.agent_foundation = agent_foundation
        self.runtime_service = runtime_service
        self.logger = logger
        
        # Services (will be initialized in Phase 2)
        self.sop_builder_service: Optional[Any] = None
        self.workflow_conversion_service: Optional[Any] = None
        self.coexistence_analysis_service: Optional[Any] = None
        
        # Orchestrator
        self.journey_orchestrator: Optional[JourneyOrchestrator] = None
        
        # Agents (will be initialized in Phase 6)
        self.journey_liaison_agent: Optional[Any] = None
        self.sop_builder_wizard_agent: Optional[Any] = None
        self.workflow_generator_agent: Optional[Any] = None
        self.coexistence_analyzer_agent: Optional[Any] = None
        
        # Manager
        self.manager: Optional[JourneyRealmManager] = None
        
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize all Journey Realm components.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            self.logger.warning("Journey Realm Foundation already initialized")
            return True
        
        try:
            self.logger.info("Initializing Journey Realm Foundation...")
            
            # Initialize Journey Realm Services
            file_storage = self.platform_gateway.get_file_storage_abstraction() if hasattr(self.platform_gateway, 'get_file_storage_abstraction') else None
            
            if file_storage:
                # SOP Builder Service
                self.sop_builder_service = SOPBuilderService(
                    state_surface=self.state_surface,
                    file_storage_abstraction=file_storage,
                    platform_gateway=self.platform_gateway
                )
                self.logger.info("✅ SOP Builder Service initialized")
                
                # Workflow Conversion Service
                self.workflow_conversion_service = WorkflowConversionService(
                    state_surface=self.state_surface,
                    file_storage_abstraction=file_storage,
                    platform_gateway=self.platform_gateway
                )
                self.logger.info("✅ Workflow Conversion Service initialized")
                
                # Coexistence Analysis Service
                self.coexistence_analysis_service = CoexistenceAnalysisService(
                    state_surface=self.state_surface,
                    file_storage_abstraction=file_storage,
                    platform_gateway=self.platform_gateway
                )
                self.logger.info("✅ Coexistence Analysis Service initialized")
            else:
                self.logger.warning("File Storage Abstraction not available, services not initialized")
            
            # Initialize Journey Orchestrator
            self.journey_orchestrator = JourneyOrchestrator(
                sop_builder_service=self.sop_builder_service,
                workflow_conversion_service=self.workflow_conversion_service,
                coexistence_analysis_service=self.coexistence_analysis_service,
                state_surface=self.state_surface,
                file_storage_abstraction=file_storage,
                agent_foundation=self.agent_foundation
            )
            
            self.logger.info("✅ Journey Orchestrator initialized")
            
            # Note: Agents will be initialized in Phase 6
            # For now, we create placeholder references
            self.logger.info("⚠️  Agents will be initialized in Phase 6")
            
            # Initialize Journey Realm Manager
            if self.curator:
                self.manager = JourneyRealmManager(
                    curator=self.curator,
                    journey_orchestrator=self.journey_orchestrator,
                    agent_foundation=self.agent_foundation,
                    runtime_service=self.runtime_service
                )
                await self.manager.initialize()
                self.logger.info("✅ Journey Realm Manager initialized")
            else:
                self.logger.warning("Curator not available, skipping Manager initialization")
            
            self._initialized = True
            self.logger.info("✅ Journey Realm Foundation initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Journey Realm Foundation: {e}", exc_info=True)
            return False
    
    async def register_agents(self) -> bool:
        """
        Register all Journey Realm agents with Agent Foundation Service.
        
        This will be called after agents are initialized in Phase 6.
        
        Returns:
            bool: True if all agents registered successfully
        """
        if not self.agent_foundation:
            self.logger.warning("Agent Foundation Service not available, skipping agent registration")
            return False
        
        if not self.manager:
            self.logger.warning("Manager not initialized, skipping agent registration")
            return False
        
        success = True
        
        # Register Journey Liaison Agent
        if self.journey_liaison_agent:
            if not await self.manager.register_agent(self.journey_liaison_agent):
                success = False
        
        # Register SOP Builder Wizard Agent
        if self.sop_builder_wizard_agent:
            if not await self.manager.register_agent(self.sop_builder_wizard_agent):
                success = False
        
        # Register Workflow Generator Agent
        if self.workflow_generator_agent:
            if not await self.manager.register_agent(self.workflow_generator_agent):
                success = False
        
        # Register Coexistence Analyzer Agent
        if self.coexistence_analyzer_agent:
            if not await self.manager.register_agent(self.coexistence_analyzer_agent):
                success = False
        
        if success:
            self.logger.info("✅ All Journey Realm agents registered")
        else:
            self.logger.warning("⚠️  Some Journey Realm agents failed to register")
        
        return success
    
    def get_journey_orchestrator(self) -> Optional[JourneyOrchestrator]:
        """Get Journey Orchestrator."""
        return self.journey_orchestrator
    
    def get_sop_builder_service(self) -> Optional[Any]:
        """Get SOP Builder Service."""
        return self.sop_builder_service
    
    def get_workflow_conversion_service(self) -> Optional[Any]:
        """Get Workflow Conversion Service."""
        return self.workflow_conversion_service
    
    def get_coexistence_analysis_service(self) -> Optional[Any]:
        """Get Coexistence Analysis Service."""
        return self.coexistence_analysis_service
    
    def get_journey_liaison_agent(self) -> Optional[Any]:
        """Get Journey Liaison Agent."""
        return self.journey_liaison_agent
    
    def get_sop_builder_wizard_agent(self) -> Optional[Any]:
        """Get SOP Builder Wizard Agent."""
        return self.sop_builder_wizard_agent
    
    def get_workflow_generator_agent(self) -> Optional[Any]:
        """Get Workflow Generator Agent."""
        return self.workflow_generator_agent
    
    def get_coexistence_analyzer_agent(self) -> Optional[Any]:
        """Get Coexistence Analyzer Agent."""
        return self.coexistence_analyzer_agent
    
    def is_initialized(self) -> bool:
        """Check if foundation is initialized."""
        return self._initialized
