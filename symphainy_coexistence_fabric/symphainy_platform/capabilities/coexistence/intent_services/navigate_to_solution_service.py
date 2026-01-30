"""
Navigate to Solution Service (Platform SDK)

Routes the user to a specific solution.

Contract: docs/intent_contracts/coexistence/intent_navigate_to_solution.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class NavigateToSolutionService(PlatformIntentService):
    """
    Navigate to Solution Service using Platform SDK.
    
    Handles the `navigate_to_solution` intent:
    - Validates solution exists
    - Returns solution context and entry point
    """
    
    # Available solutions
    SOLUTIONS = {
        "content_solution": {
            "name": "Content Solution",
            "entry_point": "/content",
            "default_journey": "FileIngestionJourney",
            "liaison_agent": "content_liaison_agent"
        },
        "insights_solution": {
            "name": "Insights Solution",
            "entry_point": "/insights",
            "default_journey": "DataQualityJourney",
            "liaison_agent": "insights_liaison_agent"
        },
        "operations_solution": {
            "name": "Operations Solution",
            "entry_point": "/operations",
            "default_journey": "SOPGenerationJourney",
            "liaison_agent": "operations_liaison_agent"
        },
        "outcomes_solution": {
            "name": "Outcomes Solution",
            "entry_point": "/outcomes",
            "default_journey": "OutcomeSynthesisJourney",
            "liaison_agent": "outcomes_liaison_agent"
        },
        "coexistence_solution": {
            "name": "Coexistence Solution",
            "entry_point": "/coexistence",
            "default_journey": "GuidedNavigationJourney",
            "liaison_agent": "guide_agent"
        }
    }
    
    def __init__(self, service_id: str = "navigate_to_solution_service"):
        """Initialize Navigate to Solution Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute navigate_to_solution intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with navigation context
        """
        self.logger.info(f"Executing navigate_to_solution: {ctx.execution_id}")
        
        solution_id = ctx.intent.parameters.get("solution_id")
        
        if not solution_id:
            raise ValueError("solution_id is required")
        
        if solution_id not in self.SOLUTIONS:
            raise ValueError(f"Unknown solution: {solution_id}. Available: {list(self.SOLUTIONS.keys())}")
        
        solution = self.SOLUTIONS[solution_id]
        
        # Build navigation context
        navigation = {
            "solution_id": solution_id,
            "solution_name": solution["name"],
            "entry_point": solution["entry_point"],
            "default_journey": solution["default_journey"],
            "liaison_agent": solution["liaison_agent"],
            "navigated_at": datetime.utcnow().isoformat(),
            "context": {
                "tenant_id": ctx.tenant_id,
                "session_id": ctx.session_id,
                "source": "navigate_to_solution"
            }
        }
        
        # Store navigation in session state
        if ctx.state_surface:
            try:
                await ctx.state_surface.set_state(
                    key=f"current_solution:{ctx.session_id}",
                    value={
                        "solution_id": solution_id,
                        "navigated_at": navigation["navigated_at"]
                    },
                    tenant_id=ctx.tenant_id
                )
            except Exception as e:
                self.logger.warning(f"Could not persist navigation state: {e}")
        
        self.logger.info(f"✅ Navigated to {solution_id}")
        
        return {
            "artifacts": {
                "navigation": navigation
            },
            "events": [{
                "type": "navigated_to_solution",
                "event_id": generate_event_id(),
                "solution_id": solution_id
            }]
        }
