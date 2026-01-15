"""
Smart City Foundation Service - Phase 4

Orchestrates all Smart City services and provides unified access.

WHAT: I provide platform governance and infrastructure capabilities
HOW: I orchestrate Smart City services that observe Runtime and enforce policy

Smart City is BOTH:
- Plane: Governance/Control Plane (observes Runtime, enforces policy)
- Realm: Platform Realm (special realm that's always present)
"""

from typing import Dict, Any, Optional, List
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService
from symphainy_platform.runtime.runtime_service import RuntimeService
from symphainy_platform.agentic.foundation_service import AgentFoundationService
from utilities import get_logger, LogLevel, LogCategory

# Import Smart City services
from .services.security_guard.security_guard_service import SecurityGuardService
from .services.nurse.nurse_service import NurseService
from .services.city_manager.city_manager_service import CityManagerService
from .services.traffic_cop.traffic_cop_service import TrafficCopService
from .services.post_office.post_office_service import PostOfficeService
from .services.conductor.conductor_service import ConductorService
from .services.librarian.librarian_service import LibrarianService
from .services.data_steward.data_steward_service import DataStewardService


class SmartCityFoundationService:
    """
    Smart City Foundation Service
    
    Orchestrates all Smart City services and provides unified access.
    
    Responsibilities:
    - Initialize all Smart City services
    - Register services with Runtime as observers
    - Register services with Curator
    - Provide unified access to services
    - Coordinate service lifecycle
    """
    
    def __init__(
        self,
        public_works_foundation: PublicWorksFoundationService,
        curator_foundation: CuratorFoundationService,
        runtime_service: RuntimeService,
        agent_foundation: Optional[AgentFoundationService] = None
    ):
        """
        Initialize Smart City Foundation Service.
        
        Args:
            public_works_foundation: Public Works Foundation
            curator_foundation: Curator Foundation
            runtime_service: Runtime Service (for observer registration)
            agent_foundation: Optional Agent Foundation (for policy reasoning agents)
        """
        self.public_works = public_works_foundation
        self.curator = curator_foundation
        self.runtime_service = runtime_service
        self.agent_foundation = agent_foundation
        self.logger = get_logger("smart_city_foundation", LogLevel.INFO, LogCategory.PLATFORM)
        
        # Smart City services
        self.services: Dict[str, Any] = {}
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all Smart City services."""
        try:
            self.logger.info("Initializing Smart City Foundation")
            
            # Initialize all services
            # Note: Order matters - City Manager should be first (bootstrap)
            # Then Security Guard (governance), then others
            
            # 1. City Manager (bootstrap)
            self.services["city_manager"] = CityManagerService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime_service,
                agent_foundation=self.agent_foundation
            )
            
            # 2. Security Guard (governance)
            self.services["security_guard"] = SecurityGuardService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime_service,
                agent_foundation=self.agent_foundation
            )
            
            # 3. Traffic Cop (session semantics)
            self.services["traffic_cop"] = TrafficCopService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime_service,
                agent_foundation=self.agent_foundation
            )
            
            # 4. Post Office (event routing)
            self.services["post_office"] = PostOfficeService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime_service,
                agent_foundation=self.agent_foundation
            )
            
            # 5. Conductor (workflow orchestration)
            self.services["conductor"] = ConductorService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime_service,
                agent_foundation=self.agent_foundation
            )
            
            # 6. Librarian (knowledge governance)
            self.services["librarian"] = LibrarianService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime_service,
                agent_foundation=self.agent_foundation
            )
            
            # 7. Data Steward (lifecycle & policy hooks)
            self.services["data_steward"] = DataStewardService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime_service,
                agent_foundation=self.agent_foundation
            )
            
            # 8. Nurse (telemetry, tracing, health)
            self.services["nurse"] = NurseService(
                public_works_foundation=self.public_works,
                curator_foundation=self.curator,
                runtime_service=self.runtime_service,
                agent_foundation=self.agent_foundation
            )
            
            # Initialize all services
            for service_name, service in self.services.items():
                success = await service.initialize()
                if not success:
                    self.logger.error(f"Failed to initialize {service_name}")
                    return False
            
            self.is_initialized = True
            self.logger.info("Smart City Foundation initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Smart City Foundation: {e}", exc_info=e)
            return False
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """
        Get Smart City service by name.
        
        Args:
            service_name: Name of the service (e.g., "security_guard")
        
        Returns:
            Service instance or None if not found
        """
        return self.services.get(service_name)
    
    def list_services(self) -> List[str]:
        """
        List all Smart City service names.
        
        Returns:
            List of service names
        """
        return list(self.services.keys())
    
    async def shutdown(self) -> None:
        """Shutdown all Smart City services."""
        self.logger.info("Shutting down Smart City Foundation")
        
        for service_name, service in self.services.items():
            try:
                await service.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down {service_name}: {e}")
        
        self.is_initialized = False
