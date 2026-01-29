"""
Realm Registry - Registers Realms with Runtime

Tracks registered realm names and metadata.

WHAT (Runtime Role): I track registered realm names
HOW (Runtime Implementation): I maintain a registry of realm names and metadata

NOTE: RealmBase has been removed from the platform. 
Realms are now natively implemented as: solution + orchestrators + intent services.
See SOLUTION_PATTERN.md and BaseSolution for the correct pattern.
"""

from typing import Dict, List, Optional, Any
from utilities import get_logger

from .intent_registry import IntentRegistry


# Known realm names in the platform
# These correspond to solutions: content, insights, operations, outcomes, security, coexistence, control_tower
KNOWN_REALM_NAMES = [
    "content",
    "insights", 
    "operations",
    "outcomes",
    "security",
    "coexistence",
    "control_tower",
    "journey"  # Legacy name, maps to operations
]


class RealmRegistry:
    """
    Registry for realm name registration and discovery.
    
    NOTE: This registry no longer holds RealmBase instances.
    Realms are now natively implemented as solutions.
    This registry only tracks realm names and optional metadata.
    
    For intent registration, use SolutionRegistry and the solution's
    SUPPORTED_INTENTS directly.
    """
    
    def __init__(self, intent_registry: Optional[IntentRegistry] = None):
        """
        Initialize realm registry.
        
        Args:
            intent_registry: Intent registry (optional, kept for backward compatibility)
        """
        self._realms: Dict[str, Dict[str, Any]] = {}  # realm_name -> metadata
        self.intent_registry = intent_registry
        self.logger = get_logger(self.__class__.__name__)
        
        # Pre-populate with known realm names
        for realm_name in KNOWN_REALM_NAMES:
            self._realms[realm_name] = {"name": realm_name, "registered": True}
    
    def register_realm(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a realm name with optional metadata.
        
        NOTE: This no longer accepts RealmBase instances.
        Realm registration is now name-based only.
        
        Args:
            name: Realm name to register
            metadata: Optional metadata dict
        
        Returns:
            True if registered successfully
        """
        try:
            self._realms[name] = {
                "name": name,
                "registered": True,
                **(metadata or {})
            }
            self.logger.info(f"Realm name registered: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register realm name: {e}", exc_info=True)
            return False
    
    def get_realm(self, realm_name: str) -> Optional[Dict[str, Any]]:
        """
        Get realm metadata by name.
        
        NOTE: This no longer returns RealmBase instances.
        Returns a metadata dict or None.
        
        Args:
            realm_name: Realm name
        
        Returns:
            Realm metadata dict, or None if not found
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
        Unregister a realm name.
        
        Args:
            realm_name: Realm name
        
        Returns:
            True if unregistered successfully
        """
        if realm_name not in self._realms:
            return False
        
        del self._realms[realm_name]
        self.logger.info(f"Realm name unregistered: {realm_name}")
        return True
    
    def get_realm_metadata(self, realm_name: str) -> Optional[Dict[str, Any]]:
        """
        Get realm metadata.
        
        Args:
            realm_name: Realm name
        
        Returns:
            Metadata dict or None
        """
        realm = self._realms.get(realm_name)
        return realm if realm else None
