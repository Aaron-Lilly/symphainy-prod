"""
Intent Registry - Track Intent Handlers

Tracks which domain services support which intents.

WHAT (Runtime Role): I track intent-to-handler mappings
HOW (Runtime Implementation): I maintain a registry of intent handlers

Key Principle: Domain services register the intents they support.
Runtime uses this registry to route intents to the correct handlers.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field

from utilities import get_logger
from .intent_model import Intent


@dataclass
class IntentHandler:
    """Intent handler registration."""
    intent_type: str
    handler_name: str  # Domain service name
    handler_function: Optional[Callable] = None  # Optional: direct function reference
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntentRegistry:
    """
    Registry for intent handlers.
    
    Tracks which domain services support which intents.
    """
    
    def __init__(self):
        """Initialize intent registry."""
        self._handlers: Dict[str, List[IntentHandler]] = {}
        self.logger = get_logger(self.__class__.__name__)
    
    def register_intent(
        self,
        intent_type: str,
        handler_name: str,
        handler_function: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register an intent handler.
        
        Args:
            intent_type: Type of intent (e.g., "ingest_file")
            handler_name: Name of the handler (domain service name)
            handler_function: Optional direct function reference
            metadata: Optional handler metadata
        
        Returns:
            True if registration successful
        """
        if not intent_type:
            self.logger.error("Cannot register intent: intent_type is required")
            return False
        
        if not handler_name:
            self.logger.error("Cannot register intent: handler_name is required")
            return False
        
        handler = IntentHandler(
            intent_type=intent_type,
            handler_name=handler_name,
            handler_function=handler_function,
            metadata=metadata or {}
        )
        
        if intent_type not in self._handlers:
            self._handlers[intent_type] = []
        
        # Check if handler already registered
        existing = [h for h in self._handlers[intent_type] if h.handler_name == handler_name]
        if existing:
            self.logger.warning(
                f"Handler {handler_name} already registered for intent {intent_type}, "
                "updating registration"
            )
            # Update existing handler
            existing[0].handler_function = handler_function
            existing[0].metadata = metadata or {}
        else:
            self._handlers[intent_type].append(handler)
        
        self.logger.info(f"Registered intent handler: {intent_type} -> {handler_name}")
        return True
    
    def get_intent_handlers(self, intent_type: str) -> List[IntentHandler]:
        """
        Get handlers for an intent type.
        
        Args:
            intent_type: Type of intent
        
        Returns:
            List of intent handlers
        """
        return self._handlers.get(intent_type, [])
    
    def get_handler(self, intent_type: str, handler_name: str) -> Optional[IntentHandler]:
        """
        Get a specific handler.
        
        Args:
            intent_type: Type of intent
            handler_name: Name of the handler
        
        Returns:
            Intent handler or None if not found
        """
        handlers = self.get_intent_handlers(intent_type)
        for handler in handlers:
            if handler.handler_name == handler_name:
                return handler
        return None
    
    def list_supported_intents(self) -> List[str]:
        """
        List all supported intent types.
        
        Returns:
            List of intent types
        """
        return list(self._handlers.keys())
    
    def unregister_intent(self, intent_type: str, handler_name: str) -> bool:
        """
        Unregister an intent handler.
        
        Args:
            intent_type: Type of intent
            handler_name: Name of the handler
        
        Returns:
            True if unregistration successful
        """
        if intent_type not in self._handlers:
            return False
        
        handlers = self._handlers[intent_type]
        original_count = len(handlers)
        self._handlers[intent_type] = [
            h for h in handlers if h.handler_name != handler_name
        ]
        
        if len(self._handlers[intent_type]) < original_count:
            self.logger.info(f"Unregistered intent handler: {intent_type} -> {handler_name}")
            return True
        
        return False
    
    def has_handler(self, intent_type: str, handler_name: Optional[str] = None) -> bool:
        """
        Check if a handler exists.
        
        Args:
            intent_type: Type of intent
            handler_name: Optional handler name (checks specific handler if provided)
        
        Returns:
            True if handler exists
        """
        if intent_type not in self._handlers:
            return False
        
        if handler_name:
            return any(h.handler_name == handler_name for h in self._handlers[intent_type])
        
        return len(self._handlers[intent_type]) > 0
