"""
Insights Realm Manager - Lifecycle and Registration

WHAT (Insights Realm): I manage Insights Realm lifecycle
HOW (Manager): I register capabilities with Curator and bind to Runtime
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from symphainy_platform.foundations.curator.models.capability_definition import CapabilityDefinition


class InsightsRealmManager:
    """
    Insights Realm Manager - Lifecycle and Registration.
    
    Manages Insights Realm lifecycle:
    - Registers capabilities with Curator
    - Binds realm to Runtime lifecycle
    - Coordinates realm initialization
    """
    
    def __init__(
        self,
        curator: Any,
        data_mash_orchestrator: Any,
        runtime_service: Optional[Any] = None
    ):
        """
        Initialize Insights Realm Manager.
        
        Args:
            curator: Curator Foundation Service
            data_mash_orchestrator: Data Mash Orchestrator instance
            runtime_service: Optional Runtime Service (for future integration)
        """
        self.curator = curator
        self.data_mash_orchestrator = data_mash_orchestrator
        self.runtime_service = runtime_service
        self.logger = get_logger(self.__class__.__name__)
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize and register Insights Realm capabilities.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            self.logger.warning("Insights Realm Manager already initialized")
            return True
        
        try:
            self.logger.info("Initializing Insights Realm Manager...")
            
            # Register capabilities with Curator
            await self._register_capabilities()
            
            self._initialized = True
            self.logger.info("✅ Insights Realm Manager initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Insights Realm Manager: {e}", exc_info=True)
            return False
    
    async def _register_capabilities(self) -> None:
        """Register Insights Realm capabilities with Curator."""
        try:
            # Register data_mash.create capability
            data_mash_capability = CapabilityDefinition(
                capability_name="data_mash_create",
                service_name="insights_realm",
                protocol_name="DataMashOrchestrator",
                description="Create a new data mash for semantic interpretation",
                realm="insights",
                contracts={
                    "soa_api": {
                        "api_name": "data_mash_create",
                        "endpoint": "/api/v1/data-mash/create",
                        "method": "POST",
                        "handler": "DataMashOrchestrator.create_mash"
                    }
                },
                semantic_mapping={
                    "domain_capability": "data_mash.create",
                    "user_journey": "create_data_mash_for_interpretation"
                },
                inputs={
                    "content_refs": "List[str]",
                    "options": "Dict[str, Any]",
                    "tenant_id": "str",
                    "session_id": "str"
                },
                outputs={
                    "mash_id": "str",
                    "mash_result": "Dict[str, Any]"
                },
                determinism="non-deterministic"  # Uses agents for reasoning
            )
            
            await self.curator.capability_registry.register_capability(data_mash_capability)
            self.logger.info("✅ Registered data_mash.create capability")
            
        except Exception as e:
            self.logger.error(f"Failed to register capabilities: {e}", exc_info=True)
            raise
    
    async def shutdown(self) -> bool:
        """
        Shutdown Insights Realm Manager.
        
        Returns:
            bool: True if shutdown successful
        """
        try:
            self.logger.info("Shutting down Insights Realm Manager...")
            self._initialized = False
            self.logger.info("✅ Insights Realm Manager shut down successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to shutdown Insights Realm Manager: {e}", exc_info=True)
            return False
    
    def is_initialized(self) -> bool:
        """Check if manager is initialized."""
        return self._initialized
