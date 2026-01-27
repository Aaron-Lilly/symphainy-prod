"""
Operations Realm - Realm Service Implementation

Implements Runtime Participation Contract for operations.

WHAT (Operations Realm Role): I handle operations-related intents
HOW (Operations Realm Implementation): I coordinate OperationsOrchestrator to process intents
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
from .orchestrators.operations_orchestrator import OperationsOrchestrator


class OperationsRealm(RealmBase):
    """
    Operations Realm - Domain service for operations.
    
    Handles:
    - Workflow optimization
    - SOP generation
    - Coexistence analysis
    - Blueprint creation
    """
    
    def __init__(
        self,
        realm_name: str = "operations",
        public_works: Optional[Any] = None
    ):
        """
        Initialize Operations Realm.
        
        Args:
            realm_name: Realm name (default: "operations")
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        super().__init__(realm_name)
        
        self.public_works = public_works
        
        # Initialize orchestrator with Public Works
        self.orchestrator = OperationsOrchestrator(public_works=public_works)
        
        self.logger.info(f"Operations Realm initialized: {realm_name}")
    
    def declare_intents(self) -> List[str]:
        """
        Declare which intents this realm supports.
        
        Returns:
            List of supported intent types
        """
        return [
            "optimize_process",
            "generate_sop",
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
