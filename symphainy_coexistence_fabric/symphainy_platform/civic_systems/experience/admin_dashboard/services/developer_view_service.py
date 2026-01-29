"""
Developer View Service - Platform SDK Documentation & Developer Tools

Provides developer-focused capabilities: documentation, playground, feature submission.

WHAT (Developer View Role): I provide developer tools and documentation
HOW (Developer View Implementation): I expose Platform SDK documentation and playground
"""

import sys
from pathlib import Path

# Add project root to path
# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger
from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder
from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry


class DeveloperViewService:
    """
    Developer View Service - Developer tools and documentation.
    
    Provides:
    - Platform SDK documentation
    - Code examples
    - Patterns & best practices
    - Solution Builder Playground (gated)
    - Feature submission (gated - "Coming Soon" for MVP)
    """
    
    def __init__(
        self,
        solution_registry: Optional[SolutionRegistry] = None,
        public_works: Optional[Any] = None
    ):
        """
        Initialize Developer View Service.
        
        Args:
            solution_registry: Solution registry for playground
            public_works: Public Works Foundation Service
        """
        self.logger = get_logger(self.__class__.__name__)
        self.solution_registry = solution_registry or SolutionRegistry()
        self.public_works = public_works
    
    async def get_documentation(self, section: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Platform SDK documentation.
        
        Args:
            section: Optional documentation section
        
        Returns:
            Dict with documentation content
        """
        # For MVP: Return structure
        # In Phase 2: Load from markdown files or generate from code
        
        docs = {
            "sections": {
                "architecture": {
                    "title": "Architecture Overview",
                    "content": "Platform architecture: Runtime, Civic Systems, Solutions, Foundations"
                },
                "solution_pattern": {
                    "title": "Solution Pattern",
                    "content": "How to build solutions using BaseSolution: compose journeys, expose SOA APIs, integrate with MCP server"
                },
                "journey_orchestrators": {
                    "title": "Journey Orchestrators",
                    "content": "How to implement journey orchestrators that handle specific workflows and return standardized results"
                },
                "smart_city_sdk": {
                    "title": "Smart City SDK",
                    "content": "Smart City SDK: Security Guard, Traffic Cop, Post Office - infrastructure abstractions"
                },
                "agentic_sdk": {
                    "title": "Agentic SDK",
                    "content": "How to implement agents using AgentBase and collaboration patterns"
                },
                "public_works": {
                    "title": "Public Works",
                    "content": "Public Works pattern: Adapters, Abstractions, Protocols for infrastructure access"
                },
                "mcp_integration": {
                    "title": "MCP Integration",
                    "content": "How to expose solution journeys as MCP tools for AI agent consumption"
                }
            }
        }
        
        if section:
            return docs["sections"].get(section, {})
        
        return docs
    
    async def get_code_examples(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get code examples.
        
        Args:
            category: Optional example category
        
        Returns:
            Dict with code examples
        """
        examples = {
            "creating_solution": {
                "title": "Creating a Solution",
                "language": "python",
                "code": """
from typing import Dict, Any, List
from symphainy_platform.bases.solution_base import BaseSolution
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext

class MySolution(BaseSolution):
    '''My custom solution following the Solution Pattern.'''
    
    SOLUTION_ID = "my_solution"
    SOLUTION_NAME = "My Solution"
    
    # Declare all intents this solution handles
    SUPPORTED_INTENTS = [
        "compose_journey",
        "my_custom_intent",
    ]
    
    def __init__(self, public_works=None, state_surface=None):
        super().__init__(public_works, state_surface)
        self._journeys = {}
        self._initialize_journeys()
    
    def _initialize_journeys(self):
        '''Initialize journey orchestrators.'''
        # from .journeys.my_journey import MyJourney
        # self._journeys["my_journey"] = MyJourney(...)
        pass
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        '''Handle intent by routing to appropriate journey.'''
        intent_type = intent.intent_type
        
        if intent_type == "compose_journey":
            return await self._handle_compose_journey(intent, context)
        
        # Route to journey
        journey = self._find_journey_for_intent(intent_type)
        if journey:
            return await journey.compose_journey(context, intent.parameters)
        
        raise ValueError(f"Unknown intent: {intent_type}")
"""
            },
            "building_solution": {
                "title": "Building a Solution with SolutionBuilder",
                "language": "python",
                "code": """
from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder

solution = SolutionBuilder(solution_id="my_solution") \\
    .with_context(
        goals=["Provide domain capabilities"],
        constraints=["All operations via intents", "Artifacts in State Surface"]
    ) \\
    .add_domain_binding(
        domain="content",
        system_name="file_storage",
        adapter_type="gcs_adapter"
    ) \\
    .register_intents(["compose_journey", "ingest_file", "parse_content"]) \\
    .with_metadata({"version": "1.0.0"}) \\
    .build()
"""
            },
            "creating_journey": {
                "title": "Creating a Journey Orchestrator",
                "language": "python",
                "code": """
from typing import Dict, Any
from symphainy_platform.bases.orchestrator_base import OrchestratorBase
from symphainy_platform.runtime.execution_context import ExecutionContext

class MyJourney(OrchestratorBase):
    '''Journey orchestrator for a specific workflow.'''
    
    JOURNEY_ID = "my_journey"
    JOURNEY_NAME = "My Journey"
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        '''Execute the journey workflow.'''
        action = params.get("action", "default")
        
        if action == "process":
            return await self._handle_process(context, params)
        
        return self.build_journey_result(
            success=True,
            data={"message": "Journey completed"},
            artifacts={},
            events=[]
        )
    
    def get_soa_apis(self) -> Dict[str, Any]:
        '''Return SOA API definitions for MCP server.'''
        return {
            "process": {
                "handler": self._handle_process_soa,
                "input_schema": {"type": "object", "properties": {...}},
                "description": "Process something"
            }
        }
"""
            }
        }
        
        if category:
            return examples.get(category, {})
        
        return {"examples": examples}
    
    async def get_patterns(self) -> Dict[str, Any]:
        """
        Get patterns and best practices.
        
        Returns:
            Dict with patterns
        """
        return {
            "patterns": {
                "solution_pattern": {
                    "title": "Solution Pattern",
                    "description": "How to implement solutions using BaseSolution, composing journeys and exposing SOA APIs"
                },
                "journey_orchestration": {
                    "title": "Journey Orchestration Pattern",
                    "description": "How to implement journey orchestrators that handle specific workflows with standardized results"
                },
                "solution_composition": {
                    "title": "Solution Composition Pattern",
                    "description": "How to compose solutions from journey orchestrators and expose them via MCP server"
                },
                "agent_collaboration": {
                    "title": "Agent Collaboration Pattern",
                    "description": "How agents collaborate via Runtime intents, not direct invocation"
                },
                "public_works_pattern": {
                    "title": "Public Works Pattern",
                    "description": "How to create adapters, abstractions, and protocols for infrastructure access"
                },
                "mcp_server_pattern": {
                    "title": "MCP Server Pattern",
                    "description": "How to expose solution journeys as MCP tools for AI agent consumption"
                }
            }
        }
    
    async def validate_solution(
        self,
        solution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a solution configuration (Solution Builder Playground).
        
        Args:
            solution_config: Solution configuration dictionary
        
        Returns:
            Dict with validation result
        """
        try:
            # Build solution from config
            builder = SolutionBuilder.from_config(solution_config)
            solution = builder.build()
            
            return {
                "valid": True,
                "solution": solution.to_dict(),
                "message": "Solution is valid"
            }
        except ValueError as e:
            return {
                "valid": False,
                "error": str(e),
                "message": "Solution validation failed"
            }
        except Exception as e:
            self.logger.error(f"Solution validation error: {e}", exc_info=True)
            return {
                "valid": False,
                "error": str(e),
                "message": "Internal error during validation"
            }
    
    async def preview_solution(
        self,
        solution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Preview a solution structure (Solution Builder Playground).
        
        Args:
            solution_config: Solution configuration dictionary
        
        Returns:
            Dict with solution preview
        """
        try:
            builder = SolutionBuilder.from_config(solution_config)
            solution = builder.build()
            
            return {
                "solution_id": solution.solution_id,
                "context": solution.solution_context.to_dict(),
                "domain_bindings": [b.to_dict() for b in solution.domain_service_bindings],
                "sync_strategies": [s.to_dict() for s in solution.sync_strategies],
                "supported_intents": solution.supported_intents,
                "metadata": solution.metadata
            }
        except Exception as e:
            self.logger.error(f"Solution preview error: {e}", exc_info=True)
            return {
                "error": str(e),
                "message": "Failed to generate preview"
            }
    
    async def submit_feature_request(
        self,
        feature_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit a feature request (gated - "Coming Soon" for MVP).
        
        Args:
            feature_request: Feature request data
        
        Returns:
            Dict with submission result
        """
        # For MVP: Return "Coming Soon" message
        # In Phase 2: Store feature request and trigger governance workflow
        
        return {
            "status": "coming_soon",
            "message": "Feature submission is coming soon! This will enable developers to submit feature proposals for platform team review.",
            "feature_request": feature_request  # Echo back for demo purposes
        }
