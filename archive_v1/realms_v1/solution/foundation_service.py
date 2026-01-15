"""
Solution Realm Foundation Service

Initializes and wires up all Solution Realm services, orchestrators, and agents.

WHAT (Solution Realm): I coordinate Solution Realm services
HOW (Foundation): I initialize and register all Solution services, orchestrators, and agents
"""

import logging
from typing import Dict, Any, Optional

from utilities import get_logger

from .orchestrators.solution_orchestrator import SolutionOrchestrator
from .manager import SolutionRealmManager

logger = get_logger(__name__)


class SolutionRealmFoundationService:
    """
    Solution Realm Foundation Service.
    
    Initializes and wires up all Solution Realm components:
    - Services (Roadmap Generation, POC Generation, Report Generator)
    - Solution Orchestrator
    - Agents (Liaison, Roadmap, POC Proposal)
    - Solution Realm Manager
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
        Initialize Solution Realm Foundation Service.
        
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
        
        # Services (will be initialized in Phase 3)
        self.roadmap_generation_service: Optional[Any] = None
        self.poc_generation_service: Optional[Any] = None
        self.report_generator_service: Optional[Any] = None
        
        # Orchestrator
        self.solution_orchestrator: Optional[SolutionOrchestrator] = None
        
        # Agents (will be initialized in Phase 6)
        self.solution_liaison_agent: Optional[Any] = None
        self.roadmap_agent: Optional[Any] = None
        self.poc_proposal_agent: Optional[Any] = None
        
        # Manager
        self.manager: Optional[SolutionRealmManager] = None
        
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize all Solution Realm components.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            self.logger.warning("Solution Realm Foundation already initialized")
            return True
        
        try:
            self.logger.info("Initializing Solution Realm Foundation...")
            
            # Note: Services will be initialized in Phase 3
            # For now, we create placeholder references
            self.logger.info("⚠️  Services will be initialized in Phase 3")
            
            # Initialize Solution Orchestrator (placeholder - will be fully implemented in Phase 5)
            # For now, create with None services (will be updated in Phase 5)
            self.solution_orchestrator = SolutionOrchestrator(
                roadmap_generation_service=self.roadmap_generation_service,
                poc_generation_service=self.poc_generation_service,
                report_generator_service=self.report_generator_service,
                state_surface=self.state_surface,
                file_storage_abstraction=self.platform_gateway.get_file_storage_abstraction() if hasattr(self.platform_gateway, 'get_file_storage_abstraction') else None,
                agent_foundation=self.agent_foundation
            )
            
            self.logger.info("✅ Solution Orchestrator initialized (placeholder)")
            
            # Note: Agents will be initialized in Phase 6
            # For now, we create placeholder references
            self.logger.info("⚠️  Agents will be initialized in Phase 6")
            
            # Initialize Solution Realm Manager
            if self.curator:
                self.manager = SolutionRealmManager(
                    curator=self.curator,
                    solution_orchestrator=self.solution_orchestrator,
                    agent_foundation=self.agent_foundation,
                    runtime_service=self.runtime_service
                )
                await self.manager.initialize()
                self.logger.info("✅ Solution Realm Manager initialized")
            else:
                self.logger.warning("Curator not available, skipping Manager initialization")
            
            self._initialized = True
            self.logger.info("✅ Solution Realm Foundation initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Solution Realm Foundation: {e}", exc_info=True)
            return False
    
    async def register_agents(self) -> bool:
        """
        Register all Solution Realm agents with Agent Foundation Service.
        
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
        
        # Register Solution Liaison Agent
        if self.solution_liaison_agent:
            if not await self.manager.register_agent(self.solution_liaison_agent):
                success = False
        
        # Register Roadmap Agent
        if self.roadmap_agent:
            if not await self.manager.register_agent(self.roadmap_agent):
                success = False
        
        # Register POC Proposal Agent
        if self.poc_proposal_agent:
            if not await self.manager.register_agent(self.poc_proposal_agent):
                success = False
        
        if success:
            self.logger.info("✅ All Solution Realm agents registered")
        else:
            self.logger.warning("⚠️  Some Solution Realm agents failed to register")
        
        return success
    
    def get_solution_orchestrator(self) -> Optional[SolutionOrchestrator]:
        """Get Solution Orchestrator."""
        return self.solution_orchestrator
    
    def get_roadmap_generation_service(self) -> Optional[Any]:
        """Get Roadmap Generation Service."""
        return self.roadmap_generation_service
    
    def get_poc_generation_service(self) -> Optional[Any]:
        """Get POC Generation Service."""
        return self.poc_generation_service
    
    def get_report_generator_service(self) -> Optional[Any]:
        """Get Report Generator Service."""
        return self.report_generator_service
    
    def get_solution_liaison_agent(self) -> Optional[Any]:
        """Get Solution Liaison Agent."""
        return self.solution_liaison_agent
    
    def get_roadmap_agent(self) -> Optional[Any]:
        """Get Roadmap Agent."""
        return self.roadmap_agent
    
    def get_poc_proposal_agent(self) -> Optional[Any]:
        """Get POC Proposal Agent."""
        return self.poc_proposal_agent
    
    def is_initialized(self) -> bool:
        """Check if foundation is initialized."""
        return self._initialized
