"""
Navigate to Solution Intent Service

Implements the navigate_to_solution intent for the Coexistence Realm.

Purpose: Navigate a user to a specific solution, establishing
context and providing guidance on how to use it.

WHAT (Intent Service Role): I navigate users to solutions
HOW (Intent Service Implementation): I establish solution context
    and return navigation guidance
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class NavigateToSolutionService(BaseIntentService):
    """
    Intent service for solution navigation.
    
    Provides:
    - Solution context establishment
    - Available actions in the solution
    - Suggested next steps
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize NavigateToSolutionService."""
        super().__init__(
            service_id="navigate_to_solution_service",
            intent_type="navigate_to_solution",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the navigate_to_solution intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            solution_id = intent_params.get("solution_id")
            if not solution_id:
                raise ValueError("solution_id is required")
            
            user_goal = intent_params.get("user_goal")  # Optional context
            
            # Navigate to solution
            navigation = await self._navigate_to_solution(solution_id, user_goal)
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success", "solution": solution_id},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "navigation": navigation,
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "navigated_to_solution",
                        "timestamp": datetime.utcnow().isoformat(),
                        "solution_id": solution_id
                    }
                ]
            }
            
        except ValueError as e:
            return {"success": False, "error": str(e), "error_code": "INVALID_SOLUTION"}
        except Exception as e:
            self.logger.error(f"Failed to navigate: {e}")
            return {"success": False, "error": str(e)}
    
    async def _navigate_to_solution(self, solution_id: str, user_goal: Optional[str]) -> Dict[str, Any]:
        """Navigate to a solution and establish context."""
        solutions = {
            "content_solution": {
                "name": "Content Solution",
                "context_established": True,
                "available_actions": [
                    {"action": "ingest_file", "description": "Upload a file"},
                    {"action": "parse_content", "description": "Parse uploaded content"},
                    {"action": "create_embeddings", "description": "Create semantic embeddings"},
                    {"action": "list_artifacts", "description": "View your files"}
                ],
                "suggested_journey": "FileIngestionJourney",
                "suggested_prompt": "Upload a file to get started",
                "liaison_agent": "ContentLiaisonAgent"
            },
            "insights_solution": {
                "name": "Insights Solution",
                "context_established": True,
                "available_actions": [
                    {"action": "assess_data_quality", "description": "Evaluate data quality"},
                    {"action": "interpret_data", "description": "Get AI interpretation"},
                    {"action": "visualize_lineage", "description": "See data lineage"},
                    {"action": "map_relationships", "description": "Map entity relationships"}
                ],
                "suggested_journey": "DataQualityJourney",
                "suggested_prompt": "Select an artifact to analyze",
                "liaison_agent": "InsightsLiaisonAgent"
            },
            "operations_solution": {
                "name": "Operations Solution",
                "context_established": True,
                "available_actions": [
                    {"action": "generate_sop", "description": "Generate an SOP"},
                    {"action": "create_workflow", "description": "Create a workflow"},
                    {"action": "optimize_process", "description": "Optimize a process"},
                    {"action": "analyze_coexistence", "description": "Analyze coexistence"}
                ],
                "suggested_journey": "SOPGenerationJourney",
                "suggested_prompt": "Describe the process you want to document",
                "liaison_agent": "OperationsLiaisonAgent"
            },
            "outcomes_solution": {
                "name": "Outcomes Solution",
                "context_established": True,
                "available_actions": [
                    {"action": "synthesize_outcome", "description": "Synthesize outcomes"},
                    {"action": "generate_roadmap", "description": "Create a roadmap"},
                    {"action": "create_poc", "description": "Generate a POC"},
                    {"action": "create_blueprint", "description": "Create a blueprint"}
                ],
                "suggested_journey": "OutcomeSynthesisJourney",
                "suggested_prompt": "What outcome would you like to create?",
                "liaison_agent": "OutcomesLiaisonAgent"
            },
            "coexistence_solution": {
                "name": "Coexistence Solution",
                "context_established": True,
                "available_actions": [
                    {"action": "introduce_platform", "description": "Learn about the platform"},
                    {"action": "show_catalog", "description": "See all solutions"},
                    {"action": "start_guide", "description": "Start guided session"},
                    {"action": "get_help", "description": "Get help"}
                ],
                "suggested_journey": "GuideAgentJourney",
                "suggested_prompt": "How can I help you today?",
                "liaison_agent": None  # Guide Agent handles this realm
            }
        }
        
        if solution_id not in solutions:
            raise ValueError(f"Unknown solution: {solution_id}")
        
        navigation = solutions[solution_id]
        
        # Add personalized suggestion if user_goal provided
        if user_goal:
            navigation["personalized_suggestion"] = f"Based on your goal '{user_goal}', I suggest starting with the {navigation['suggested_journey']}"
        
        return navigation
