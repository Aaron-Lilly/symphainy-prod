"""
Introduction Journey Orchestrator

Composes platform introduction operations:
1. introduce_platform - Welcome and onboarding
2. show_solution_catalog - Browse available solutions
3. explain_coexistence - Educational content about coexistence

WHAT (Journey Role): I orchestrate platform introduction
HOW (Journey Implementation): I compose introduction intents for onboarding
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


class IntroductionJourney:
    """
    Introduction Journey Orchestrator.
    
    Handles platform onboarding:
    - Welcome new users
    - Show available solutions
    - Explain coexistence concepts
    
    MCP Tools:
    - coexist_introduce_platform: Welcome message
    - coexist_show_catalog: Solution catalog
    - coexist_explain: Coexistence explanation
    """
    
    JOURNEY_ID = "introduction"
    JOURNEY_NAME = "Platform Introduction"
    
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
        """Compose introduction journey."""
        journey_params = journey_params or {}
        action = journey_params.get("action", "introduce")
        journey_execution_id = generate_event_id()
        
        self.logger.info(f"Composing journey: {self.journey_name}, action: {action}")
        
        try:
            if action == "introduce":
                return await self._introduce_platform(context, journey_params, journey_execution_id)
            elif action == "catalog":
                return await self._show_solution_catalog(context, journey_params, journey_execution_id)
            elif action == "explain":
                return await self._explain_coexistence(context, journey_params, journey_execution_id)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    async def _introduce_platform(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Introduce the platform to a new user."""
        user_name = params.get("user_name", "User")
        user_goals = params.get("user_goals")
        
        welcome_message = f"Welcome to Symphainy, {user_name}! Let's build your coexistence future together."
        if user_goals:
            welcome_message += f" I see you're interested in: {user_goals}"
        
        introduction = {
            "welcome_message": welcome_message,
            "platform_tagline": "Coordinate boundary-crossing work across systems",
            "value_propositions": [
                "Enable legacy and modern systems to work together",
                "AI-powered guidance through your transformation journey",
                "Governed, secure coordination of cross-boundary workflows"
            ],
            "next_steps": [
                {"action": "catalog", "label": "Explore Solutions"},
                {"action": "goals", "label": "Share Your Goals"},
                {"action": "start", "label": "Start Your Journey"}
            ],
            "key_concepts": {
                "coexistence": "Systems working together without replacement",
                "boundary_crossing": "Workflows spanning multiple systems and teams",
                "guided_journey": "AI-assisted path through platform capabilities"
            }
        }
        
        semantic_payload = {
            "intro_type": "platform_introduction",
            "user_name": user_name,
            "has_goals": user_goals is not None,
            "journey_execution_id": journey_execution_id
        }
        
        artifact = create_structured_artifact(
            result_type="platform_introduction",
            semantic_payload=semantic_payload,
            renderings=introduction
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"introduction": artifact},
            "events": [{"type": "platform_introduction_presented", "user_name": user_name}]
        }
    
    async def _show_solution_catalog(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Show the solution catalog."""
        category = params.get("category")
        
        solutions_by_category = {
            "data": [
                {"solution_id": "content_solution", "name": "Content Solution", "description": "File processing and content management", "journeys": 4}
            ],
            "analytics": [
                {"solution_id": "insights_solution", "name": "Insights Solution", "description": "Business analysis and data quality", "journeys": 2}
            ],
            "automation": [
                {"solution_id": "journey_solution", "name": "Journey Solution", "description": "Workflow and SOP management", "journeys": 2}
            ],
            "outcomes": [
                {"solution_id": "outcomes_solution", "name": "Outcomes Solution", "description": "POC creation and roadmap generation", "journeys": 2}
            ],
            "governance": [
                {"solution_id": "control_tower", "name": "Control Tower", "description": "Platform monitoring and management", "journeys": 4}
            ]
        }
        
        if category:
            solutions_by_category = {category: solutions_by_category.get(category, [])}
        
        featured = [
            {"solution_id": "content_solution", "name": "Content Solution", "reason": "Start by uploading content"}
        ]
        
        catalog = {
            "featured_solutions": featured,
            "solutions_by_category": solutions_by_category,
            "total_solutions": 5,
            "categories": ["data", "analytics", "automation", "outcomes", "governance"]
        }
        
        semantic_payload = {
            "catalog_type": "solution_catalog",
            "category_filter": category,
            "journey_execution_id": journey_execution_id
        }
        
        artifact = create_structured_artifact(
            result_type="solution_catalog",
            semantic_payload=semantic_payload,
            renderings=catalog
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"catalog": artifact},
            "events": [{"type": "solution_catalog_displayed", "solution_count": 5}]
        }
    
    async def _explain_coexistence(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Explain coexistence concepts."""
        depth = params.get("depth", "overview")
        
        explanation = {
            "headline": "What is Coexistence?",
            "tagline": "Systems working together, not replacing each other",
            "core_definition": "The Coexistence Fabric is Symphainy's approach to coordinating work that spans multiple systems, tools, and people. Instead of replacing existing systems, the platform enables them to coexist and work together seamlessly.",
            "key_concepts": [
                {
                    "concept": "Boundary-Crossing",
                    "icon": "link",
                    "description": "Workflows that span legacy systems, modern tools, and human teams require coordination across boundaries."
                },
                {
                    "concept": "Coordination",
                    "icon": "git-branch",
                    "description": "The platform orchestrates work across systems, translating between formats, validating operations, and ensuring consistency."
                },
                {
                    "concept": "Governance",
                    "icon": "shield",
                    "description": "Policy enforcement, data boundaries, and compliance are managed centrally while respecting system autonomy."
                }
            ],
            "real_world_example": {
                "title": "SOP ↔ Workflow Coexistence",
                "description": "A Standard Operating Procedure (SOP) defines how work should be done. A workflow defines how work is done in practice. The platform analyzes how these coexist, identifying gaps, overlaps, and opportunities for alignment."
            },
            "benefits": [
                "Preserve investments in existing systems",
                "Gradual modernization without disruption",
                "Unified governance across heterogeneous systems",
                "AI-powered optimization of cross-boundary workflows"
            ]
        }
        
        semantic_payload = {
            "explanation_type": "coexistence",
            "depth": depth,
            "journey_execution_id": journey_execution_id
        }
        
        artifact = create_structured_artifact(
            result_type="coexistence_explanation",
            semantic_payload=semantic_payload,
            renderings=explanation
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"explanation": artifact},
            "events": [{"type": "coexistence_explained", "depth": depth}]
        }
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA API definitions for MCP tool registration."""
        return {
            "introduce_platform": {
                "handler": self._handle_introduce,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_name": {"type": "string"},
                        "user_goals": {"type": "string"},
                        "user_context": {"type": "object"}
                    }
                },
                "description": "Welcome new users to the platform"
            },
            "show_catalog": {
                "handler": self._handle_catalog,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "user_context": {"type": "object"}
                    }
                },
                "description": "Show available solutions catalog"
            },
            "explain_coexistence": {
                "handler": self._handle_explain,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "depth": {"type": "string", "enum": ["overview", "detailed", "technical"]},
                        "user_context": {"type": "object"}
                    }
                },
                "description": "Explain coexistence concepts"
            }
        }
    
    async def _handle_introduce(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "introduce", **kwargs})
    
    async def _handle_catalog(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "catalog", **kwargs})
    
    async def _handle_explain(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "explain", **kwargs})
    
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
