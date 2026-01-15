"""
Content Realm Manager - Lifecycle and Registration

WHAT (Content Realm): I manage Content Realm lifecycle
HOW (Manager): I register capabilities with Curator and bind to Runtime
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from symphainy_platform.foundations.curator.models.capability_definition import CapabilityDefinition


class ContentRealmManager:
    """
    Content Realm Manager - Lifecycle and Registration.
    
    Manages Content Realm lifecycle:
    - Registers capabilities with Curator
    - Binds realm to Runtime lifecycle
    - Coordinates realm initialization
    """
    
    def __init__(
        self,
        curator: Any,
        content_orchestrator: Any,
        runtime_service: Optional[Any] = None
    ):
        """
        Initialize Content Realm Manager.
        
        Args:
            curator: Curator Foundation Service
            content_orchestrator: Content Orchestrator instance
            runtime_service: Optional Runtime Service (for future integration)
        """
        self.curator = curator
        self.content_orchestrator = content_orchestrator
        self.runtime_service = runtime_service
        self.logger = get_logger(self.__class__.__name__)
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize and register Content Realm capabilities.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            self.logger.warning("Content Realm Manager already initialized")
            return True
        
        try:
            self.logger.info("Initializing Content Realm Manager...")
            
            # Register capabilities with Curator
            await self._register_capabilities()
            
            self._initialized = True
            self.logger.info("✅ Content Realm Manager initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Content Realm Manager: {e}", exc_info=True)
            return False
    
    async def _register_capabilities(self) -> None:
        """Register Content Realm capabilities with Curator."""
        try:
            # Register content.upload capability
            upload_capability = CapabilityDefinition(
                capability_name="content_upload",
                service_name="content_realm",
                protocol_name="ContentOrchestrator",
                description="Upload and parse files",
                realm="content",
                contracts={
                    "soa_api": {
                        "api_name": "content_upload",
                        "endpoint": "/api/v1/content/upload",
                        "method": "POST",
                        "handler": "ContentOrchestrator.handle_upload_intent"
                    }
                },
                semantic_mapping={
                    "domain_capability": "content.upload",
                    "user_journey": "upload_file_for_processing"
                },
                inputs={
                    "file_data": "bytes",
                    "filename": "str",
                    "tenant_id": "str",
                    "session_id": "str"
                },
                outputs={
                    "file_id": "str",
                    "file_reference": "str",
                    "parse_result": "ParsingResult"
                },
                determinism="deterministic"
            )
            
            await self.curator.capability_registry.register_capability(upload_capability)
            self.logger.info("✅ Registered content.upload capability")
            
            # Register content.parse capability
            parse_capability = CapabilityDefinition(
                capability_name="content_parse",
                service_name="content_realm",
                protocol_name="ContentOrchestrator",
                description="Parse files",
                realm="content",
                contracts={
                    "soa_api": {
                        "api_name": "content_parse",
                        "endpoint": "/api/v1/content/parse",
                        "method": "POST",
                        "handler": "ContentOrchestrator.parse_file"
                    }
                },
                semantic_mapping={
                    "domain_capability": "content.parse",
                    "user_journey": "parse_uploaded_file"
                },
                inputs={
                    "file_reference": "str",
                    "filename": "str",
                    "parsing_type": "Optional[str]",
                    "options": "Optional[Dict[str, Any]]"
                },
                outputs={
                    "parse_result": "ParsingResult"
                },
                determinism="deterministic"
            )
            
            await self.curator.capability_registry.register_capability(parse_capability)
            self.logger.info("✅ Registered content.parse capability")
            
        except Exception as e:
            self.logger.error(f"Failed to register capabilities: {e}", exc_info=True)
            raise
    
    async def shutdown(self) -> bool:
        """
        Shutdown Content Realm Manager.
        
        Returns:
            bool: True if shutdown successful
        """
        try:
            self.logger.info("Shutting down Content Realm Manager...")
            self._initialized = False
            self.logger.info("✅ Content Realm Manager shut down successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to shutdown Content Realm Manager: {e}", exc_info=True)
            return False
    
    def is_initialized(self) -> bool:
        """Check if manager is initialized."""
        return self._initialized
