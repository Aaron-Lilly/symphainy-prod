"""
Solution Composition Journey Orchestrator

Composes guided solution creation:
1. get_solution_templates - Get available templates
2. compose_solution - Create solution from template
3. get_composition_guide - Get guided composition help

WHAT (Journey Role): I orchestrate solution composition
HOW (Journey Implementation): I compose template, composition, and guidance intents
"""

import sys
from pathlib import Path


def _find_project_root() -> Path:
    """Find project root by searching for pyproject.toml."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback for when running from different locations
    return Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) > 3 else Path.cwd()


project_root = _find_project_root()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class SolutionCompositionJourney:
    """
    Solution Composition Journey Orchestrator.
    
    Enables guided solution creation:
    - Browse solution templates
    - Create solutions from templates
    - Get composition guidance
    
    MCP Tools:
    - tower_get_templates: Get solution templates
    - tower_compose_solution: Create solution from template
    - tower_get_composition_guide: Get composition guidance
    """
    
    JOURNEY_ID = "solution_composition"
    JOURNEY_NAME = "Solution Composition"
    
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
        """Compose solution composition journey."""
        journey_params = journey_params or {}
        action = journey_params.get("action", "templates")
        journey_execution_id = generate_event_id()
        
        self.logger.info(f"Composing journey: {self.journey_name}, action: {action}")
        
        try:
            if action == "templates":
                return await self._get_templates(context, journey_params, journey_execution_id)
            elif action == "compose":
                return await self._compose_solution(context, journey_params, journey_execution_id)
            elif action == "guide":
                return await self._get_composition_guide(context, journey_params, journey_execution_id)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    async def _get_templates(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Get available solution templates."""
        category = params.get("category")
        
        templates = [
            {
                "template_id": "content_processing",
                "name": "Content Processing Solution",
                "description": "Solution for file upload, parsing, and embedding",
                "category": "data",
                "journeys_included": ["file_upload", "file_parsing", "embedding"],
                "complexity": "medium"
            },
            {
                "template_id": "business_intelligence",
                "name": "Business Intelligence Solution",
                "description": "Solution for data analysis and insights generation",
                "category": "analytics",
                "journeys_included": ["data_analysis", "quality_assessment", "reporting"],
                "complexity": "high"
            },
            {
                "template_id": "workflow_automation",
                "name": "Workflow Automation Solution",
                "description": "Solution for workflow and SOP management",
                "category": "automation",
                "journeys_included": ["sop_creation", "workflow_management", "coexistence_analysis"],
                "complexity": "medium"
            },
            {
                "template_id": "minimal_solution",
                "name": "Minimal Solution",
                "description": "Bare-bones solution template for custom implementations",
                "category": "custom",
                "journeys_included": [],
                "complexity": "low"
            }
        ]
        
        if category:
            templates = [t for t in templates if t["category"] == category]
        
        semantic_payload = {"resource_type": "templates", "template_count": len(templates), "journey_execution_id": journey_execution_id}
        artifact = create_structured_artifact(result_type="solution_templates", semantic_payload=semantic_payload, renderings={"templates": templates})
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"templates": artifact},
            "events": [{"type": "templates_retrieved", "count": len(templates)}]
        }
    
    async def _compose_solution(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Create solution from template."""
        template_id = params.get("template_id")
        solution_name = params.get("solution_name")
        configuration = params.get("configuration", {})
        
        if not template_id:
            raise ValueError("template_id is required")
        if not solution_name:
            raise ValueError("solution_name is required")
        
        # Generate solution ID
        solution_id = solution_name.lower().replace(" ", "_") + "_solution"
        
        composition_result = {
            "solution_id": solution_id,
            "solution_name": solution_name,
            "template_id": template_id,
            "status": "created",
            "configuration": configuration,
            "journeys_created": [],
            "mcp_server_created": True,
            "created_at": self.clock.now_utc().isoformat(),
            "next_steps": [
                "Configure domain bindings",
                "Register supported intents",
                "Deploy solution"
            ]
        }
        
        semantic_payload = {"solution_id": solution_id, "template_id": template_id, "status": "created", "journey_execution_id": journey_execution_id}
        artifact = create_structured_artifact(result_type="composition_result", semantic_payload=semantic_payload, renderings={"result": composition_result})
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "solution_id": solution_id,
            "artifacts": {"composition_result": artifact},
            "events": [{"type": "solution_composed", "solution_id": solution_id, "template_id": template_id}]
        }
    
    async def _get_composition_guide(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Get composition guidance."""
        step = params.get("step", "overview")
        
        guide = {
            "current_step": step,
            "steps": [
                {"step": 1, "title": "Select Template", "description": "Choose a solution template that matches your use case", "status": "not_started"},
                {"step": 2, "title": "Configure Solution", "description": "Set solution name, goals, and constraints", "status": "not_started"},
                {"step": 3, "title": "Select Journeys", "description": "Choose which journeys to include", "status": "not_started"},
                {"step": 4, "title": "Configure Integrations", "description": "Set up domain bindings and external systems", "status": "not_started"},
                {"step": 5, "title": "Review & Deploy", "description": "Review configuration and deploy solution", "status": "not_started"}
            ],
            "tips": [
                "Start with a template that closely matches your use case",
                "You can always add more journeys later",
                "Use the validation tool to check your solution before deployment"
            ]
        }
        
        semantic_payload = {"guide_type": "composition", "current_step": step, "journey_execution_id": journey_execution_id}
        artifact = create_structured_artifact(result_type="composition_guide", semantic_payload=semantic_payload, renderings={"guide": guide})
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"guide": artifact},
            "events": [{"type": "guide_retrieved", "step": step}]
        }
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        return {
            "get_templates": {
                "handler": self._handle_templates,
                "input_schema": {
                    "type": "object",
                    "properties": {"category": {"type": "string", "enum": ["data", "analytics", "automation", "custom"]}, "user_context": {"type": "object"}}
                },
                "description": "Get available solution templates"
            },
            "compose_solution": {
                "handler": self._handle_compose,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "template_id": {"type": "string"},
                        "solution_name": {"type": "string"},
                        "configuration": {"type": "object"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["template_id", "solution_name"]
                },
                "description": "Create a new solution from template"
            },
            "get_composition_guide": {
                "handler": self._handle_guide,
                "input_schema": {
                    "type": "object",
                    "properties": {"step": {"type": "string"}, "user_context": {"type": "object"}}
                },
                "description": "Get guided composition help"
            }
        }
    
    async def _handle_templates(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "templates", "category": kwargs.get("category")})
    
    async def _handle_compose(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {
            "action": "compose",
            "template_id": kwargs.get("template_id"),
            "solution_name": kwargs.get("solution_name"),
            "configuration": kwargs.get("configuration", {})
        })
    
    async def _handle_guide(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "guide", "step": kwargs.get("step", "overview")})
    
    def _create_context(self, kwargs: Dict) -> ExecutionContext:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="control_tower"
        )
        context.state_surface = self.state_surface
        return context
