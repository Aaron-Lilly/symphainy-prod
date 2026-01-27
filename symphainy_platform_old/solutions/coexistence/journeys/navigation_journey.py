"""
Navigation Journey Orchestrator

Composes solution navigation operations:
1. navigate_to_solution - Route to a specific solution
2. get_solution_context - Retrieve current context
3. establish_solution_context - Set up solution context

WHAT (Journey Role): I orchestrate solution navigation
HOW (Journey Implementation): I compose navigation intents for routing
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class NavigationJourney:
    """
    Navigation Journey Orchestrator.
    
    Handles solution navigation:
    - Navigate to solutions
    - Manage solution context
    - Track navigation state
    
    MCP Tools:
    - coexist_navigate: Navigate to solution
    - coexist_get_context: Get current context
    - coexist_establish_context: Set solution context
    """
    
    JOURNEY_ID = "navigation"
    JOURNEY_NAME = "Solution Navigation"
    
    # Route mappings for solutions
    SOLUTION_ROUTES = {
        "content_solution": "/pillars/content",
        "insights_solution": "/pillars/insights",
        "journey_solution": "/pillars/journey",
        "outcomes_solution": "/pillars/business-outcomes",
        "control_tower": "/admin",
        "coexistence": "/"
    }
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        solution_registry: Optional[Any] = None
    ):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.solution_registry = solution_registry
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compose navigation journey."""
        journey_params = journey_params or {}
        action = journey_params.get("action", "navigate")
        journey_execution_id = generate_event_id()
        
        self.logger.info(f"Composing journey: {self.journey_name}, action: {action}")
        
        try:
            if action == "navigate":
                return await self._navigate_to_solution(context, journey_params, journey_execution_id)
            elif action == "get_context":
                return await self._get_solution_context(context, journey_params, journey_execution_id)
            elif action == "establish_context":
                return await self._establish_solution_context(context, journey_params, journey_execution_id)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    async def _navigate_to_solution(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Navigate to a specific solution."""
        solution_id = params.get("solution_id")
        pillar_name = params.get("pillar_name")
        
        if not solution_id:
            raise ValueError("solution_id is required")
        
        route = self.SOLUTION_ROUTES.get(solution_id, "/")
        if pillar_name:
            route = f"/pillars/{pillar_name}"
        
        solution_name = solution_id.replace("_", " ").title()
        
        navigation = {
            "route": route,
            "solution_id": solution_id,
            "solution_name": solution_name,
            "pillar_name": pillar_name or solution_id.replace("_solution", ""),
            "navigation_metadata": {
                "from_solution": "coexistence",
                "to_solution": solution_id,
                "context_preserved": True
            },
            "initial_state": {
                "welcome_message": f"Welcome to {solution_name}!",
                "suggested_actions": ["start_journey", "view_artifacts"]
            },
            "breadcrumbs": [
                {"label": "Home", "route": "/"},
                {"label": solution_name, "route": route}
            ]
        }
        
        semantic_payload = {
            "navigation_type": "solution_switch",
            "target_solution": solution_id,
            "journey_execution_id": journey_execution_id
        }
        
        artifact = create_structured_artifact(
            result_type="navigation_result",
            semantic_payload=semantic_payload,
            renderings=navigation
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"navigation": artifact},
            "events": [{"type": "navigation_initiated", "to_solution": solution_id}]
        }
    
    async def _get_solution_context(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Get current solution context."""
        include_artifacts = params.get("include_artifacts", True)
        include_progress = params.get("include_progress", True)
        
        # Build context from session state
        solution_context = {
            "current_solution": None,
            "user_context": {
                "user_name": "User",
                "user_goals": None,
                "goals_analyzed": False
            },
            "journey_progress": None,
            "artifacts_summary": [],
            "available_actions": [
                {"action": "start_journey", "label": "Start Your Journey"},
                {"action": "view_catalog", "label": "Browse Solutions"}
            ],
            "session_metadata": {
                "session_start": self.clock.now_utc().isoformat(),
                "last_activity": self.clock.now_utc().isoformat()
            }
        }
        
        # Try to get real context from state surface
        if self.state_surface:
            try:
                session_state = await self.state_surface.get_session_state(context.session_id)
                if session_state:
                    solution_context.update(session_state)
            except Exception as e:
                self.logger.debug(f"Could not get session state: {e}")
        
        semantic_payload = {
            "context_type": "solution_context",
            "has_active_solution": solution_context.get("current_solution") is not None,
            "journey_execution_id": journey_execution_id
        }
        
        artifact = create_structured_artifact(
            result_type="solution_context",
            semantic_payload=semantic_payload,
            renderings=solution_context
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"context": artifact},
            "events": [{"type": "solution_context_retrieved"}]
        }
    
    async def _establish_solution_context(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Establish solution context for session."""
        solution_structure = params.get("solution_structure", {})
        user_goals = params.get("user_goals")
        pillar_preferences = params.get("pillar_preferences", [])
        reasoning = params.get("reasoning", {})
        
        solution_id = solution_structure.get("solution_id", "content_solution")
        
        # Build pillar configuration
        pillar_config = pillar_preferences or [
            {"pillar_name": "content", "enabled": True, "navigation_order": 1},
            {"pillar_name": "insights", "enabled": True, "navigation_order": 2},
            {"pillar_name": "journey", "enabled": True, "navigation_order": 3},
            {"pillar_name": "outcomes", "enabled": True, "navigation_order": 4}
        ]
        
        # Find first enabled pillar
        enabled_pillars = [p for p in pillar_config if p.get("enabled", True)]
        first_pillar = enabled_pillars[0] if enabled_pillars else pillar_config[0]
        
        established_context = {
            "solution": {
                "solution_id": solution_id,
                "solution_name": solution_id.replace("_", " ").title(),
                "strategic_focus": solution_structure.get("strategic_focus", "general")
            },
            "user_profile": {
                "user_goals": user_goals,
                "goals_analyzed": user_goals is not None
            },
            "pillar_configuration": pillar_config,
            "initial_journey": {
                "journey_id": "file_upload_materialization",
                "journey_name": "File Upload & Materialization",
                "first_intent": "ingest_file"
            },
            "agent_guidance": {
                "initial_message": f"Welcome! Based on your goals, I recommend starting with the {first_pillar['pillar_name'].title()} pillar.",
                "confidence": reasoning.get("confidence", 0.8)
            },
            "navigation": {
                "start_route": f"/pillars/{first_pillar['pillar_name']}",
                "breadcrumbs": [
                    {"label": "Home", "route": "/"},
                    {"label": first_pillar['pillar_name'].title(), "route": f"/pillars/{first_pillar['pillar_name']}"}
                ]
            }
        }
        
        # Persist context if state surface available
        if self.state_surface:
            try:
                await self.state_surface.set_session_state(context.session_id, established_context)
            except Exception as e:
                self.logger.debug(f"Could not persist session state: {e}")
        
        semantic_payload = {
            "context_type": "established",
            "solution_id": solution_id,
            "pillars_enabled": len(enabled_pillars),
            "journey_execution_id": journey_execution_id
        }
        
        artifact = create_structured_artifact(
            result_type="solution_context_established",
            semantic_payload=semantic_payload,
            renderings=established_context
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"established_context": artifact},
            "events": [{"type": "solution_context_established", "solution_id": solution_id}]
        }
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA API definitions for MCP tool registration."""
        return {
            "navigate_to_solution": {
                "handler": self._handle_navigate,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "solution_id": {"type": "string"},
                        "pillar_name": {"type": "string"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["solution_id"]
                },
                "description": "Navigate to a specific solution"
            },
            "get_solution_context": {
                "handler": self._handle_get_context,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "include_artifacts": {"type": "boolean"},
                        "include_progress": {"type": "boolean"},
                        "user_context": {"type": "object"}
                    }
                },
                "description": "Get current solution context"
            },
            "establish_solution_context": {
                "handler": self._handle_establish,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "solution_structure": {"type": "object"},
                        "user_goals": {"type": "string"},
                        "pillar_preferences": {"type": "array"},
                        "user_context": {"type": "object"}
                    }
                },
                "description": "Establish solution context for session"
            }
        }
    
    async def _handle_navigate(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "navigate", **kwargs})
    
    async def _handle_get_context(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "get_context", **kwargs})
    
    async def _handle_establish(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "establish_context", **kwargs})
    
    def _create_context(self, kwargs: Dict) -> ExecutionContext:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="coexistence"
        )
        context.state_surface = self.state_surface
        return context
