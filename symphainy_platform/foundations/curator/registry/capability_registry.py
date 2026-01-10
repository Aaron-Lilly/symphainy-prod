"""
Capability Registry

Manages capability registration and intent → capability lookup.

WHAT (Service Role): I manage service capability registration and discovery
HOW (Service Implementation): I maintain a central capability registry
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger

from ..models.capability_definition import CapabilityDefinition


class CapabilityRegistry:
    """
    Capability Registry - Central capability registration and discovery.
    
    Manages service capability registration, validation, and intent → capability lookup.
    """
    
    def __init__(self):
        """Initialize Capability Registry."""
        self.logger = get_logger(self.__class__.__name__)
        
        # Central capability registry
        # Key: capability_name, Value: CapabilityDefinition
        self.capability_registry: Dict[str, CapabilityDefinition] = {}
        
        # Intent → capability mapping
        # Key: intent (e.g., "content.upload_file"), Value: List[CapabilityDefinition]
        self.intent_mapping: Dict[str, List[CapabilityDefinition]] = {}
        
        self.logger.info("Capability Registry initialized")
    
    async def register_capability(self, capability: CapabilityDefinition) -> bool:
        """
        Register a capability.
        
        Args:
            capability: CapabilityDefinition to register
        
        Returns:
            bool: True if registration successful
        """
        try:
            # Validate capability
            if not capability.capability_name:
                self.logger.error("Capability missing capability_name")
                return False
            
            # Register capability
            self.capability_registry[capability.capability_name] = capability
            
            # Register intent mappings (if semantic mapping provided)
            if capability.semantic_mapping:
                domain_capability = capability.semantic_mapping.get("domain_capability")
                if domain_capability:
                    if domain_capability not in self.intent_mapping:
                        self.intent_mapping[domain_capability] = []
                    self.intent_mapping[domain_capability].append(capability)
            
            self.logger.info(f"Capability registered: {capability.capability_name} (service: {capability.service_name}, realm: {capability.realm})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register capability: {e}", exc_info=True)
            return False
    
    async def get_capability(self, capability_name: str) -> Optional[CapabilityDefinition]:
        """
        Get capability by name.
        
        Args:
            capability_name: Name of the capability
        
        Returns:
            Optional[CapabilityDefinition]: Capability if found, None otherwise
        """
        return self.capability_registry.get(capability_name)
    
    async def lookup_capability_by_intent(self, intent: str) -> List[CapabilityDefinition]:
        """
        Lookup capabilities by intent.
        
        Args:
            intent: Intent string (e.g., "content.upload_file")
        
        Returns:
            List[CapabilityDefinition]: List of matching capabilities
        """
        return self.intent_mapping.get(intent, [])
    
    async def list_capabilities(
        self,
        realm: Optional[str] = None,
        service_name: Optional[str] = None
    ) -> List[CapabilityDefinition]:
        """
        List capabilities with optional filters.
        
        Args:
            realm: Optional realm filter
            service_name: Optional service name filter
        
        Returns:
            List[CapabilityDefinition]: List of matching capabilities
        """
        capabilities = list(self.capability_registry.values())
        
        if realm:
            capabilities = [c for c in capabilities if c.realm == realm]
        
        if service_name:
            capabilities = [c for c in capabilities if c.service_name == service_name]
        
        return capabilities
    
    async def unregister_capability(self, capability_name: str) -> bool:
        """
        Unregister a capability.
        
        Args:
            capability_name: Name of the capability to unregister
        
        Returns:
            bool: True if unregistration successful
        """
        try:
            if capability_name not in self.capability_registry:
                self.logger.warning(f"Capability not found: {capability_name}")
                return False
            
            capability = self.capability_registry[capability_name]
            
            # Remove from registry
            del self.capability_registry[capability_name]
            
            # Remove from intent mappings
            if capability.semantic_mapping:
                domain_capability = capability.semantic_mapping.get("domain_capability")
                if domain_capability and domain_capability in self.intent_mapping:
                    self.intent_mapping[domain_capability] = [
                        c for c in self.intent_mapping[domain_capability]
                        if c.capability_name != capability_name
                    ]
                    if not self.intent_mapping[domain_capability]:
                        del self.intent_mapping[domain_capability]
            
            self.logger.info(f"Capability unregistered: {capability_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister capability: {e}", exc_info=True)
            return False
