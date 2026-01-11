"""
Content Realm Foundation Service

Initializes and wires up all Content Realm services and orchestrators.

WHAT (Content Realm): I coordinate Content Realm services
HOW (Foundation): I initialize and register all parsing services
"""

import logging
from typing import Dict, Any, Optional

from utilities import get_logger

from ..services.structured_parsing_service import StructuredParsingService
from ..services.unstructured_parsing_service import UnstructuredParsingService
from ..services.hybrid_parsing_service import HybridParsingService
from ..services.workflow_sop_parsing_service import WorkflowSOPParsingService
from ..orchestrators.content_orchestrator import ContentOrchestrator

logger = get_logger(__name__)


class ContentRealmFoundationService:
    """
    Content Realm Foundation Service.
    
    Initializes and wires up all Content Realm services:
    - Structured Parsing Service
    - Unstructured Parsing Service
    - Hybrid Parsing Service
    - Workflow/SOP Parsing Service
    - Content Orchestrator
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Any,
        curator: Optional[Any] = None
    ):
        """
        Initialize Content Realm Foundation Service.
        
        Args:
            state_surface: State Surface instance
            platform_gateway: Platform Gateway instance
            curator: Curator Foundation Service (for service registration)
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.curator = curator
        self.logger = logger
        
        # Services
        self.structured_service: Optional[StructuredParsingService] = None
        self.unstructured_service: Optional[UnstructuredParsingService] = None
        self.hybrid_service: Optional[HybridParsingService] = None
        self.workflow_sop_service: Optional[WorkflowSOPParsingService] = None
        
        # Orchestrator
        self.content_orchestrator: Optional[ContentOrchestrator] = None
        
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize all Content Realm services.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            self.logger.warning("Content Realm Foundation already initialized")
            return True
        
        try:
            self.logger.info("Initializing Content Realm Foundation...")
            
            # Initialize parsing services
            self.structured_service = StructuredParsingService(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
            
            self.unstructured_service = UnstructuredParsingService(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
            
            self.hybrid_service = HybridParsingService(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway,
                use_kreuzberg=True  # Use Kreuzberg if available
            )
            
            self.workflow_sop_service = WorkflowSOPParsingService(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
            
            self.logger.info("✅ Parsing services initialized")
            
            # Initialize Content Orchestrator
            self.content_orchestrator = ContentOrchestrator(
                structured_service=self.structured_service,
                unstructured_service=self.unstructured_service,
                hybrid_service=self.hybrid_service,
                workflow_sop_service=self.workflow_sop_service,
                state_surface=self.state_surface
            )
            
            self.logger.info("✅ Content Orchestrator initialized")
            
            # Register services with Curator
            if self.curator and hasattr(self.curator, 'service_registry'):
                await self._register_services()
            
            self._initialized = True
            self.logger.info("✅ Content Realm Foundation initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Content Realm Foundation: {e}", exc_info=True)
            return False
    
    async def _register_services(self):
        """Register parsing services with Curator."""
        try:
            # Register Structured Parsing Service
            await self.curator.service_registry.register_service(
                service_instance=self.structured_service,
                service_metadata={
                    "service_name": "structured_parsing_service",
                    "realm": "content",
                    "capabilities": ["parse_excel", "parse_csv", "parse_json", "parse_binary"]
                }
            )
            
            # Register Unstructured Parsing Service
            await self.curator.service_registry.register_service(
                service_instance=self.unstructured_service,
                service_metadata={
                    "service_name": "unstructured_parsing_service",
                    "realm": "content",
                    "capabilities": ["parse_pdf", "parse_word", "parse_text", "parse_image"]
                }
            )
            
            # Register Hybrid Parsing Service
            await self.curator.service_registry.register_service(
                service_instance=self.hybrid_service,
                service_metadata={
                    "service_name": "hybrid_parsing_service",
                    "realm": "content",
                    "capabilities": ["parse_hybrid"]
                }
            )
            
            # Register Workflow/SOP Parsing Service
            await self.curator.service_registry.register_service(
                service_instance=self.workflow_sop_service,
                service_metadata={
                    "service_name": "workflow_sop_parsing_service",
                    "realm": "content",
                    "capabilities": ["parse_workflow", "parse_sop"]
                }
            )
            
            self.logger.info("✅ Parsing services registered with Curator")
        
        except Exception as e:
            self.logger.error(f"Failed to register services with Curator: {e}", exc_info=True)
    
    def get_content_orchestrator(self) -> Optional[ContentOrchestrator]:
        """Get Content Orchestrator."""
        return self.content_orchestrator
    
    def get_structured_service(self) -> Optional[StructuredParsingService]:
        """Get Structured Parsing Service."""
        return self.structured_service
    
    def get_unstructured_service(self) -> Optional[UnstructuredParsingService]:
        """Get Unstructured Parsing Service."""
        return self.unstructured_service
    
    def get_hybrid_service(self) -> Optional[HybridParsingService]:
        """Get Hybrid Parsing Service."""
        return self.hybrid_service
    
    def get_workflow_sop_service(self) -> Optional[WorkflowSOPParsingService]:
        """Get Workflow/SOP Parsing Service."""
        return self.workflow_sop_service
    
    def is_initialized(self) -> bool:
        """Check if foundation is initialized."""
        return self._initialized
