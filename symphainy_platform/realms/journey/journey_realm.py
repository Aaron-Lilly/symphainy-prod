"""
Journey Realm - Realm Service Implementation

Implements Runtime Participation Contract for journey/coexistence operations.

WHAT (Journey Realm Role): I handle journey-related intents (coexistence workflows, blueprints)
HOW (Journey Realm Implementation): I coordinate JourneyOrchestrator to process intents
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional

from utilities import get_logger
from symphainy_platform.civic_systems.platform_sdk.realm_sdk import RealmBase
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from .orchestrators.journey_orchestrator import JourneyOrchestrator


class JourneyRealm(RealmBase):
    """
    Journey Realm - Domain service for journey/coexistence operations.
    
    Handles:
    - Workflow optimization
    - SOP generation
    - Coexistence analysis
    - Blueprint creation
    - Journey creation from blueprints
    """
    
    def __init__(
        self,
        realm_name: str = "journey",
        public_works: Optional[Any] = None
    ):
        """
        Initialize Journey Realm.
        
        Args:
            realm_name: Realm name (default: "journey")
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        super().__init__(realm_name)
        
        self.public_works = public_works
        
        # Initialize orchestrator with Public Works
        self.orchestrator = JourneyOrchestrator(public_works=public_works)
        
        self.logger.info(f"Journey Realm initialized: {realm_name}")
    
    def declare_intents(self) -> List[str]:
        """
        Declare which intents this realm supports.
        
        Returns:
            List of supported intent types
        """
        return [
            "optimize_process",
            "generate_sop",  # Supports both workflow-based and chat-based generation
            "generate_sop_from_chat",  # Explicit chat-based SOP generation
            "sop_chat_message",  # Process chat messages in SOP generation session
            "create_workflow",
            "analyze_coexistence",
            "create_blueprint"
        ]
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent (Runtime Participation Contract).
        
        Args:
            intent: The intent to handle
            context: Runtime execution context
        
        Returns:
            Dict with "artifacts" and "events" keys
        """
        # Validate intent is supported
        is_valid, error = self.validate_intent(intent)
        if not is_valid:
            raise ValueError(error)
        
        self.logger.info(f"Handling intent: {intent.intent_type} ({intent.intent_id})")
        
        # Delegate to orchestrator
        result = await self.orchestrator.handle_intent(intent, context)
        
        # Ensure result follows contract
        if "artifacts" not in result:
            result["artifacts"] = {}
        if "events" not in result:
            result["events"] = []
        
        return result
