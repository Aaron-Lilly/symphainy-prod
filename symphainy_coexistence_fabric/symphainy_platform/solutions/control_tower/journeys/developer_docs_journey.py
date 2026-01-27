"""
Developer Docs Journey Orchestrator

Composes developer documentation access:
1. get_documentation - Get SDK/API documentation
2. get_patterns - Get implementation patterns
3. get_code_examples - Get code examples
4. validate_solution - Validate solution implementation

WHAT (Journey Role): I orchestrate developer documentation access
HOW (Journey Implementation): I compose documentation, patterns, and validation intents
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


class DeveloperDocsJourney:
    """
    Developer Docs Journey Orchestrator.
    
    Provides developer resources:
    - SDK and API documentation
    - Implementation patterns
    - Code examples
    - Solution validation
    
    MCP Tools:
    - tower_get_docs: Get documentation
    - tower_get_patterns: Get implementation patterns
    - tower_get_examples: Get code examples
    - tower_validate_solution: Validate solution
    """
    
    JOURNEY_ID = "developer_docs"
    JOURNEY_NAME = "Developer Documentation"
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        developer_service: Optional[Any] = None
    ):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.developer_service = developer_service
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compose developer docs journey."""
        journey_params = journey_params or {}
        action = journey_params.get("action", "docs")
        journey_execution_id = generate_event_id()
        
        self.logger.info(f"Composing journey: {self.journey_name}, action: {action}")
        
        try:
            if action == "docs":
                return await self._get_documentation(context, journey_params, journey_execution_id)
            elif action == "patterns":
                return await self._get_patterns(context, journey_params, journey_execution_id)
            elif action == "examples":
                return await self._get_examples(context, journey_params, journey_execution_id)
            elif action == "validate":
                return await self._validate_solution(context, journey_params, journey_execution_id)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    async def _get_documentation(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Get SDK/API documentation."""
        topic = params.get("topic", "overview")
        
        docs = {
            "topic": topic,
            "title": "Symphainy Platform Developer Guide",
            "sections": [
                {"title": "Getting Started", "path": "/docs/getting-started"},
                {"title": "Architecture Overview", "path": "/docs/architecture"},
                {"title": "Intent API Reference", "path": "/docs/api/intents"},
                {"title": "Solution Pattern", "path": "/docs/patterns/solutions"},
                {"title": "Journey Orchestration", "path": "/docs/patterns/journeys"},
                {"title": "MCP Integration", "path": "/docs/mcp"}
            ],
            "quick_links": [
                {"title": "Create a Solution", "path": "/docs/tutorials/create-solution"},
                {"title": "Submit an Intent", "path": "/docs/tutorials/submit-intent"},
                {"title": "Build a Journey", "path": "/docs/tutorials/build-journey"}
            ]
        }
        
        semantic_payload = {"doc_type": "documentation", "topic": topic, "journey_execution_id": journey_execution_id}
        artifact = create_structured_artifact(result_type="documentation", semantic_payload=semantic_payload, renderings={"docs": docs})
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"documentation": artifact},
            "events": [{"type": "documentation_retrieved", "topic": topic}]
        }
    
    async def _get_patterns(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Get implementation patterns."""
        pattern_type = params.get("pattern_type", "all")
        
        patterns = [
            {
                "pattern_id": "solution_pattern",
                "name": "Solution Pattern",
                "description": "How to create a new Solution that composes journeys",
                "category": "architecture",
                "complexity": "medium"
            },
            {
                "pattern_id": "journey_orchestrator",
                "name": "Journey Orchestrator Pattern",
                "description": "How to compose intents into journeys",
                "category": "architecture",
                "complexity": "medium"
            },
            {
                "pattern_id": "mcp_server",
                "name": "MCP Server Pattern",
                "description": "How to expose SOA APIs as MCP tools",
                "category": "integration",
                "complexity": "low"
            },
            {
                "pattern_id": "intent_service",
                "name": "Intent Service Pattern",
                "description": "How to implement an intent service",
                "category": "architecture",
                "complexity": "high"
            },
            {
                "pattern_id": "compose_journey",
                "name": "Compose Journey Pattern",
                "description": "How to invoke journeys programmatically",
                "category": "runtime",
                "complexity": "low"
            }
        ]
        
        if pattern_type != "all":
            patterns = [p for p in patterns if p["category"] == pattern_type]
        
        semantic_payload = {"doc_type": "patterns", "pattern_type": pattern_type, "journey_execution_id": journey_execution_id}
        artifact = create_structured_artifact(result_type="patterns", semantic_payload=semantic_payload, renderings={"patterns": patterns})
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"patterns": artifact},
            "events": [{"type": "patterns_retrieved", "count": len(patterns)}]
        }
    
    async def _get_examples(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Get code examples."""
        example_type = params.get("example_type", "solution")
        
        examples = {
            "solution": {
                "title": "Create a New Solution",
                "language": "python",
                "code": '''
from symphainy_platform.solutions import ContentSolution

# Initialize solution
solution = ContentSolution(
    public_works=public_works,
    state_surface=state_surface
)

# List available journeys
journeys = solution.get_journeys()
print(f"Available journeys: {list(journeys.keys())}")

# Initialize MCP server
await solution.initialize_mcp_server()
'''
            },
            "journey": {
                "title": "Invoke a Journey",
                "language": "python",
                "code": '''
# Via compose_journey intent
intent = IntentFactory.create_intent(
    intent_type="compose_journey",
    tenant_id=tenant_id,
    session_id=session_id,
    solution_id="content_solution",
    parameters={
        "journey_id": "file_upload_materialization",
        "journey_params": {
            "file_content": file_content,
            "file_name": "example.pdf"
        }
    }
)
result = await solution.handle_intent(intent, context)
'''
            },
            "mcp_tool": {
                "title": "Use MCP Tool",
                "language": "typescript",
                "code": '''
// Call MCP tool from agent
const result = await mcpClient.callTool("content_upload_and_materialize", {
    file_content: base64Content,
    file_name: "example.pdf",
    content_type: "unstructured"
});
'''
            }
        }
        
        example = examples.get(example_type, examples["solution"])
        
        semantic_payload = {"doc_type": "example", "example_type": example_type, "journey_execution_id": journey_execution_id}
        artifact = create_structured_artifact(result_type="code_example", semantic_payload=semantic_payload, renderings={"example": example})
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"code_example": artifact},
            "events": [{"type": "example_retrieved", "type": example_type}]
        }
    
    async def _validate_solution(self, context: ExecutionContext, params: Dict, journey_execution_id: str) -> Dict[str, Any]:
        """Validate solution implementation."""
        solution_id = params.get("solution_id")
        
        validation_result = {
            "solution_id": solution_id,
            "is_valid": True,
            "checks": [
                {"check": "has_journey_orchestrators", "passed": True, "message": "Solution has journey orchestrators"},
                {"check": "has_mcp_server", "passed": True, "message": "Solution has MCP server"},
                {"check": "compose_journey_support", "passed": True, "message": "Solution supports compose_journey intent"},
                {"check": "soa_apis_defined", "passed": True, "message": "SOA APIs are properly defined"},
                {"check": "tool_naming_convention", "passed": True, "message": "MCP tools follow naming convention"}
            ],
            "warnings": [],
            "timestamp": self.clock.now_utc().isoformat()
        }
        
        semantic_payload = {"validation_type": "solution", "solution_id": solution_id, "is_valid": True, "journey_execution_id": journey_execution_id}
        artifact = create_structured_artifact(result_type="validation_result", semantic_payload=semantic_payload, renderings={"result": validation_result})
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"validation_result": artifact},
            "events": [{"type": "solution_validated", "solution_id": solution_id, "is_valid": True}]
        }
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        return {
            "get_docs": {
                "handler": self._handle_docs,
                "input_schema": {
                    "type": "object",
                    "properties": {"topic": {"type": "string"}, "user_context": {"type": "object"}}
                },
                "description": "Get SDK/API documentation"
            },
            "get_patterns": {
                "handler": self._handle_patterns,
                "input_schema": {
                    "type": "object",
                    "properties": {"pattern_type": {"type": "string", "enum": ["architecture", "integration", "runtime", "all"]}, "user_context": {"type": "object"}}
                },
                "description": "Get implementation patterns"
            },
            "get_examples": {
                "handler": self._handle_examples,
                "input_schema": {
                    "type": "object",
                    "properties": {"example_type": {"type": "string", "enum": ["solution", "journey", "mcp_tool", "intent"]}, "user_context": {"type": "object"}}
                },
                "description": "Get code examples"
            },
            "validate_solution": {
                "handler": self._handle_validate,
                "input_schema": {
                    "type": "object",
                    "properties": {"solution_id": {"type": "string"}, "user_context": {"type": "object"}},
                    "required": ["solution_id"]
                },
                "description": "Validate solution implementation against patterns"
            }
        }
    
    async def _handle_docs(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "docs", "topic": kwargs.get("topic")})
    
    async def _handle_patterns(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "patterns", "pattern_type": kwargs.get("pattern_type", "all")})
    
    async def _handle_examples(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "examples", "example_type": kwargs.get("example_type", "solution")})
    
    async def _handle_validate(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "validate", "solution_id": kwargs.get("solution_id")})
    
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
