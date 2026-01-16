"""
Realm SDK - SDK for Creating Domain Services

Enforces Runtime Participation Contract for domain services.

WHAT (Platform SDK Role): I provide SDK for creating domain services
HOW (Platform SDK Implementation): I enforce Runtime Participation Contract

Key Principle: Domain services must follow Runtime Participation Contract:
- Declare which intents they support
- Accept runtime execution context
- Return artifacts and events, not side effects
- Never bypass Runtime
"""

from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod

from utilities import get_logger
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext


class RealmBase(ABC):
    """
    Base class for domain services (realms).
    
    Enforces Runtime Participation Contract.
    All domain services must inherit from this class.
    """
    
    def __init__(self, realm_name: str):
        """
        Initialize realm.
        
        Args:
            realm_name: Name of the realm (e.g., "content", "insights")
        """
        self.realm_name = realm_name
        self.logger = get_logger(f"{self.__class__.__name__}")
        self._intent_handlers: Dict[str, Callable] = {}
    
    @abstractmethod
    def declare_intents(self) -> List[str]:
        """
        Declare which intents this realm supports.
        
        Must be implemented by realm.
        
        Returns:
            List of supported intent types
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement declare_intents()")
    
    @abstractmethod
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent (Runtime Participation Contract).
        
        Must be implemented by realm.
        
        Args:
            intent: The intent to handle
            context: Runtime execution context
        
        Returns:
            Dict with "artifacts" and "events" keys:
            {
                "artifacts": {...},  # Artifacts produced
                "events": [...]      # Events generated
            }
        
        Raises:
            ValueError: If intent is not supported
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement handle_intent()")
    
    def register_intent_handler(
        self,
        intent_type: str,
        handler: Callable[[Intent, ExecutionContext], Dict[str, Any]]
    ):
        """
        Register an intent handler (decorator helper).
        
        Args:
            intent_type: Intent type
            handler: Handler function
        """
        self._intent_handlers[intent_type] = handler
        self.logger.info(f"Registered intent handler: {intent_type}")
    
    def get_intent_handler(self, intent_type: str) -> Optional[Callable]:
        """Get intent handler for intent type."""
        return self._intent_handlers.get(intent_type)
    
    def validate_intent(self, intent: Intent) -> tuple[bool, Optional[str]]:
        """
        Validate that intent is supported by this realm.
        
        Args:
            intent: Intent to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        supported_intents = self.declare_intents()
        if intent.intent_type not in supported_intents:
            return False, f"Intent type {intent.intent_type} not supported by realm {self.realm_name}"
        return True, None


def intent_handler(intent_type: str):
    """
    Decorator for registering intent handlers.
    
    Usage:
        @intent_handler("ingest_file")
        async def handle_ingest_file(intent: Intent, context: ExecutionContext) -> Dict[str, Any]:
            return {"artifacts": {...}, "events": [...]}
    """
    def decorator(func: Callable):
        # Store intent type in function metadata
        func._intent_type = intent_type
        return func
    return decorator


class RealmSDK:
    """
    SDK for creating domain services.
    
    Provides utilities and helpers for building realms that comply with
    Runtime Participation Contract.
    """
    
    @staticmethod
    def create_realm(realm_name: str, realm_class: type) -> RealmBase:
        """
        Create a realm instance.
        
        Args:
            realm_name: Name of the realm
            realm_class: Realm class (must inherit from RealmBase)
        
        Returns:
            Realm instance
        """
        if not issubclass(realm_class, RealmBase):
            raise ValueError(f"Realm class must inherit from RealmBase: {realm_class}")
        
        realm = realm_class(realm_name)
        
        # Auto-register intent handlers from decorators
        for attr_name in dir(realm):
            attr = getattr(realm, attr_name)
            if callable(attr) and hasattr(attr, '_intent_type'):
                intent_type = attr._intent_type
                realm.register_intent_handler(intent_type, attr)
        
        return realm
    
    @staticmethod
    def validate_realm_contract(realm: RealmBase) -> tuple[bool, Optional[str]]:
        """
        Validate that realm follows Runtime Participation Contract.
        
        Args:
            realm: Realm instance to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check that realm declares intents
        try:
            intents = realm.declare_intents()
            if not intents:
                return False, "Realm must declare at least one supported intent"
        except NotImplementedError:
            return False, "Realm must implement declare_intents()"
        
        # Check that realm implements handle_intent
        try:
            # Check if handle_intent is implemented (not the abstract method)
            import inspect
            # Get the method from the instance's class
            handle_intent_method = getattr(realm.__class__, 'handle_intent', None)
            if handle_intent_method is None:
                return False, "Realm must implement handle_intent()"
            
            # Check if it's the abstract method from RealmBase
            # If the method's qualname includes RealmBase, it's likely the abstract one
            # Better: check if calling it would raise NotImplementedError
            try:
                # Try to get the method's implementation
                if hasattr(handle_intent_method, '__isabstractmethod__') and handle_intent_method.__isabstractmethod__:
                    return False, "Realm must implement handle_intent()"
            except:
                pass
            
            # More reliable: check if the method is actually implemented
            # by checking if it's bound to the instance's class (not RealmBase)
            if hasattr(RealmBase, 'handle_intent'):
                base_method = getattr(RealmBase, 'handle_intent')
                if handle_intent_method is base_method:
                    return False, "Realm must implement handle_intent()"
        except Exception as e:
            # If we can't check, assume it's implemented (fail open for now)
            pass
        
        return True, None
    
    @staticmethod
    def create_realm_from_template(
        realm_name: str,
        template_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Create realm template structure.
        
        Args:
            realm_name: Name of the realm
            template_type: Template type ("basic", "with_orchestrator", "with_agents")
        
        Returns:
            Template structure dictionary
        """
        templates = {
            "basic": {
                "realm_name": realm_name,
                "structure": {
                    "enabling_services": [],
                    "orchestrators": [],
                    "agents": []
                },
                "intent_handlers": []
            },
            "with_orchestrator": {
                "realm_name": realm_name,
                "structure": {
                    "enabling_services": [],
                    "orchestrators": [f"{realm_name}_orchestrator"],
                    "agents": []
                },
                "intent_handlers": []
            },
            "with_agents": {
                "realm_name": realm_name,
                "structure": {
                    "enabling_services": [],
                    "orchestrators": [f"{realm_name}_orchestrator"],
                    "agents": [f"{realm_name}_agent"]
                },
                "intent_handlers": []
            }
        }
        
        return templates.get(template_type, templates["basic"])
    
    @staticmethod
    def register_realm_with_runtime(
        realm: RealmBase,
        intent_registry: Any  # IntentRegistry instance
    ) -> bool:
        """
        Register realm with Runtime's intent registry.
        
        Args:
            realm: Realm instance
            intent_registry: Intent registry from Runtime
        
        Returns:
            True if registration successful
        """
        try:
            # Validate realm contract
            is_valid, error = RealmSDK.validate_realm_contract(realm)
            if not is_valid:
                logger = get_logger("RealmSDK")
                logger.error(f"Realm contract validation failed: {error}")
                return False
            
            # Get supported intents
            supported_intents = realm.declare_intents()
            
            # Register each intent with the registry
            for intent_type in supported_intents:
                # Create intent handler wrapper
                async def intent_handler_wrapper(intent: Any, context: Any) -> Dict[str, Any]:
                    return await realm.handle_intent(intent, context)
                
                # Register with intent registry
                intent_registry.register_handler(
                    intent_type=intent_type,
                    handler=intent_handler_wrapper,
                    realm_name=realm.realm_name
                )
            
            logger = get_logger("RealmSDK")
            logger.info(f"Realm registered with Runtime: {realm.realm_name}")
            return True
            
        except Exception as e:
            logger = get_logger("RealmSDK")
            logger.error(f"Failed to register realm with Runtime: {e}", exc_info=True)
            return False