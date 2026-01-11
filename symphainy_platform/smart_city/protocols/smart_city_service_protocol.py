"""
Smart City Service Protocol

Protocol for all Smart City services.

Smart City services:
- Register with Runtime as observers
- Observe execution
- Enforce policy
- Emit telemetry
- Can use agents for policy reasoning
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class SmartCityServiceProtocol(ABC):
    """
    Protocol for Smart City services.
    
    All Smart City services:
    - Register with Runtime as observers
    - Observe execution events
    - Enforce policy
    - Emit telemetry
    - Can use agents for policy reasoning
    """
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize service and register with Runtime/Curator.
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def observe_execution(self, execution_id: str, event: dict) -> None:
        """
        Observe Runtime execution events.
        
        This method is called by Runtime when execution events occur.
        Smart City services can observe and enforce policy based on events.
        
        Args:
            execution_id: Execution identifier
            event: Execution event dict with event_type, payload, etc.
        """
        pass
    
    @abstractmethod
    async def enforce_policy(
        self,
        execution_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enforce policy for execution context.
        
        This method is called to enforce policy before/during execution.
        Can use agents for policy reasoning.
        
        Args:
            execution_id: Execution identifier
            context: Execution context (user, tenant, action, etc.)
        
        Returns:
            Dict containing policy enforcement result:
            {
                "allowed": bool,
                "reason": str,
                "policy_applied": str,
                "metadata": {...}
            }
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Gracefully shutdown service."""
        pass
