"""
Realm Registry - Registers Realms with Runtime

Tracks registered realms and their intent handlers.

WHAT (Runtime Role): I track registered realms
HOW (Runtime Implementation): I maintain a registry of realm instances and their intents
"""

from typing import Dict, List, Optional
from utilities import get_logger

from symphainy_platform.civic_systems.platform_sdk.realm_sdk import RealmBase
from .intent_registry import IntentRegistry


class RealmRegistry:
    """
    Registry for realm registration and discovery.
    
    Maintains a registry of all registered realms.
    """
    
    def __init__(self, intent_registry: IntentRegistry):
        """
        Initialize realm registry.
        
        Args:
            intent_registry: Intent registry for registering intent handlers
        """
        self._realms: Dict[str, RealmBase] = {}  # realm_name -> Realm
        self.intent_registry = intent_registry
        self.logger = get_logger(self.__class__.__name__)
    
    def register_realm(self, realm: RealmBase) -> bool:
        """
        Register a realm with Runtime.
        
        Args:
            realm: Realm instance to register
        
        Returns:
            True if registered successfully
        """
        try:
            # Validate realm contract
            from symphainy_platform.civic_systems.platform_sdk.realm_sdk import RealmSDK
            is_valid, error = RealmSDK.validate_realm_contract(realm)
            if not is_valid:
                self.logger.error(f"Realm contract validation failed: {error}")
                return False
            
            # Register realm
            self._realms[realm.realm_name] = realm
            self.logger.info(f"Realm registered: {realm.realm_name}")
            
            # Auto-register intents
            for intent_type in realm.declare_intents():
                self.intent_registry.register_intent(
                    intent_type=intent_type,
                    handler_name=realm.realm_name,
                    handler_function=realm.handle_intent
                )
                self.logger.info(f"Intent registered: {intent_type} -> {realm.realm_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register realm: {e}", exc_info=True)
            return False
    
    def get_realm(self, realm_name: str) -> Optional[RealmBase]:
        """
        Get realm by name.
        
        Args:
            realm_name: Realm name
        
        Returns:
            Realm instance, or None if not found
        """
        return self._realms.get(realm_name)
    
    def list_realms(self) -> List[str]:
        """
        List all registered realm names.
        
        Returns:
            List of realm names
        """
        return list(self._realms.keys())
    
    def unregister_realm(self, realm_name: str) -> bool:
        """
        Unregister a realm.
        
        Args:
            realm_name: Realm name
        
        Returns:
            True if unregistered successfully
        """
        if realm_name not in self._realms:
            return False
        
        realm = self._realms[realm_name]
        
        # Unregister intents
        for intent_type in realm.declare_intents():
            # Note: IntentRegistry doesn't have unregister method yet
            # For MVP, we'll just remove from our registry
            pass
        
        del self._realms[realm_name]
        self.logger.info(f"Realm unregistered: {realm_name}")
        return True
