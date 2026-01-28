"""
Get Code Examples Intent Service

Implements the get_code_examples intent for the Control Tower Realm.

Purpose: Retrieve code examples for common platform development tasks.

WHAT (Intent Service Role): I provide code examples for developers
HOW (Intent Service Implementation): I return categorized code examples
    from the platform's example catalog
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class GetCodeExamplesService(BaseIntentService):
    """
    Intent service for retrieving code examples.
    
    Provides examples for:
    - Creating intent services
    - Creating solutions
    - Using Public Works
    - Registering MCP tools
    - Creating journeys
    """
    
    EXAMPLES = {
        "create_intent_service": {
            "title": "Create an Intent Service",
            "description": "How to create a new intent service in a realm",
            "category": "intent_services",
            "code": '''
"""
Example Intent Service - DoSomethingService

Place this in: symphainy_platform/realms/{realm}/intent_services/do_something_service.py
"""
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class DoSomethingService(BaseIntentService):
    """Intent service for doing something."""
    
    def __init__(self, public_works, state_surface):
        super().__init__(
            service_id="do_something_service",
            intent_type="do_something",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the do_something intent."""
        # Record start telemetry
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            # Get parameters
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            # Do the actual work using Public Works abstractions
            result = await self._do_something(intent_params)
            
            # Record success
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success"},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "result": result,
                "events": [{"event_id": generate_event_id(), "event_type": "something_done"}]
            }
            
        except Exception as e:
            self.logger.error(f"Failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _do_something(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implementation logic using Public Works."""
        # Use public_works abstractions - never direct infrastructure
        return {"message": "Done!"}
''',
            "notes": [
                "Always extend BaseIntentService",
                "Use public_works for all infrastructure",
                "Record telemetry at start and end",
                "Return structured result with events"
            ]
        },
        "create_solution": {
            "title": "Create a Solution",
            "description": "How to create a new Solution that composes journeys",
            "category": "solutions",
            "code": '''
"""
Example Solution - MySolution

Place this in: symphainy_platform/solutions/my_solution/my_solution.py
"""
from typing import Dict, Any, Optional, List

from symphainy_platform.bases.solution_base import SolutionBase
from symphainy_platform.runtime.execution_context import ExecutionContext


class MySolution(SolutionBase):
    """Solution that composes journeys for a business capability."""
    
    SOLUTION_ID = "my_solution"
    SUPPORTED_INTENTS = ["compose_journey", "my_intent"]
    
    def __init__(self, public_works=None, state_surface=None):
        super().__init__(
            solution_id=self.SOLUTION_ID,
            public_works=public_works,
            state_surface=state_surface
        )
        self._initialize_journeys()
    
    def _initialize_journeys(self):
        """Initialize journey orchestrators."""
        from .journeys import MyJourney
        self.journeys = {
            "my_journey": MyJourney(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        }
    
    async def handle_intent(self, intent, context: ExecutionContext) -> Dict[str, Any]:
        """Handle incoming intents."""
        if intent.intent_type == "compose_journey":
            return await self._handle_compose_journey(intent, context)
        return {"success": False, "error": f"Unknown intent: {intent.intent_type}"}
    
    async def _handle_compose_journey(self, intent, context) -> Dict[str, Any]:
        """Handle compose_journey intent."""
        journey_name = intent.parameters.get("journey_name")
        journey = self.journeys.get(journey_name)
        if not journey:
            return {"success": False, "error": f"Unknown journey: {journey_name}"}
        return await journey.compose_journey(context, intent.parameters)
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Return SOA APIs exposed by this solution."""
        return {
            "compose_journey": {
                "description": "Compose a journey",
                "handler": self._soa_compose_journey
            }
        }
''',
            "notes": [
                "Extend SolutionBase",
                "Define SOLUTION_ID and SUPPORTED_INTENTS",
                "Initialize journeys in _initialize_journeys()",
                "Expose SOA APIs via get_soa_apis()"
            ]
        },
        "use_public_works": {
            "title": "Use Public Works Abstractions",
            "description": "How to use Public Works for infrastructure access",
            "category": "infrastructure",
            "code": '''
"""
Using Public Works Abstractions

Public Works provides abstractions for all infrastructure.
Never access adapters directly in business logic.
"""

# File Storage
async def upload_file(public_works, content: bytes, path: str):
    file_storage = public_works.file_storage_abstraction
    result = await file_storage.upload_file(
        content=content,
        path=path,
        content_type="application/octet-stream"
    )
    return result

# State Storage (Redis)
async def store_state(public_works, key: str, value: dict):
    state = public_works.state_abstraction
    await state.set(key, value, ttl=3600)

# Registry (Postgres)
async def register_entity(public_works, entity: dict):
    registry = public_works.registry_abstraction
    await registry.register(entity)

# Auth
async def validate_token(public_works, token: str):
    auth = public_works.auth_abstraction
    return await auth.validate_token(token)

# Telemetry
async def record_metric(public_works, metric: dict):
    telemetry = public_works.telemetry_abstraction
    await telemetry.record(metric)
''',
            "notes": [
                "Always use abstractions, never adapters",
                "Public Works is injected via constructor",
                "Each abstraction has a specific purpose",
                "Abstractions handle retry, error handling, etc."
            ]
        },
        "register_mcp_tools": {
            "title": "Register MCP Tools",
            "description": "How to expose Solution capabilities as MCP tools",
            "category": "mcp",
            "code": '''
"""
MCP Server - Exposing Solution Tools

Place this in: symphainy_platform/solutions/my_solution/mcp_server/my_mcp_server.py
"""
from typing import Dict, Any, List

from symphainy_platform.civic_systems.agentic.mcp.mcp_server_base import MCPServerBase


class MyMCPServer(MCPServerBase):
    """MCP Server for MySolution."""
    
    def __init__(self, solution):
        super().__init__(
            server_id="my_mcp_server",
            prefix="my_"  # Tools will be prefixed: my_compose_journey, etc.
        )
        self.solution = solution
        self._register_tools()
    
    def _register_tools(self):
        """Register solution tools as MCP tools."""
        # Register compose_journey tool
        self.register_tool(
            name="compose_journey",
            description="Compose a journey in MySolution",
            handler=self._handle_compose_journey,
            parameters={
                "journey_name": {"type": "string", "required": True},
                "params": {"type": "object", "required": False}
            }
        )
        
        # Register other tools...
    
    async def _handle_compose_journey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle compose_journey MCP tool call."""
        # Delegate to solution
        return await self.solution.compose_journey(params)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of registered tools for Curator."""
        return self.tools
''',
            "notes": [
                "Extend MCPServerBase",
                "Use consistent prefix for tool names",
                "Register with Curator for discovery",
                "Delegate to Solution methods"
            ]
        },
        "create_journey": {
            "title": "Create a Journey",
            "description": "How to create a journey that orchestrates intents",
            "category": "journeys",
            "code": '''
"""
Example Journey - MyJourney

Place this in: symphainy_platform/solutions/my_solution/journeys/my_journey.py
"""
from typing import Dict, Any, Optional

from symphainy_platform.bases.journey_base import JourneyBase
from symphainy_platform.runtime.execution_context import ExecutionContext


class MyJourney(JourneyBase):
    """Journey that orchestrates multiple intents."""
    
    JOURNEY_ID = "my_journey"
    
    def __init__(self, public_works=None, state_surface=None):
        super().__init__(
            journey_id=self.JOURNEY_ID,
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compose the journey by orchestrating intents."""
        params = journey_params or {}
        artifacts = []
        events = []
        
        # Step 1: First intent
        step1_result = await self._execute_intent(
            intent_type="first_intent",
            context=context,
            params={"input": params.get("input")}
        )
        artifacts.append(step1_result.get("artifact"))
        events.extend(step1_result.get("events", []))
        
        # Step 2: Second intent (uses output from step 1)
        step2_result = await self._execute_intent(
            intent_type="second_intent",
            context=context,
            params={"artifact_id": step1_result["artifact"]["artifact_id"]}
        )
        artifacts.append(step2_result.get("artifact"))
        events.extend(step2_result.get("events", []))
        
        return {
            "success": True,
            "journey_id": self.JOURNEY_ID,
            "artifacts": artifacts,
            "events": events
        }
    
    async def _execute_intent(
        self,
        intent_type: str,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an intent via the intent registry."""
        # This would call the intent registry
        # Simplified for example
        return {"artifact": {"artifact_id": "abc123"}, "events": []}
''',
            "notes": [
                "Extend JourneyBase",
                "Implement compose_journey() method",
                "Orchestrate intents in sequence",
                "Propagate context and collect artifacts"
            ]
        }
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize GetCodeExamplesService."""
        super().__init__(
            service_id="get_code_examples_service",
            intent_type="get_code_examples",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the get_code_examples intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            example_name = intent_params.get("example_name")  # Optional
            category = intent_params.get("category")  # Optional filter
            
            if example_name:
                if example_name not in self.EXAMPLES:
                    raise ValueError(f"Unknown example: {example_name}")
                examples = {example_name: self.EXAMPLES[example_name]}
            elif category:
                examples = {
                    k: v for k, v in self.EXAMPLES.items()
                    if v.get("category") == category
                }
            else:
                examples = self.EXAMPLES
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success"},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "examples": examples,
                "example_count": len(examples),
                "categories": list(set(e["category"] for e in self.EXAMPLES.values())),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except ValueError as e:
            return {"success": False, "error": str(e), "error_code": "INVALID_EXAMPLE"}
        except Exception as e:
            self.logger.error(f"Failed to get examples: {e}")
            return {"success": False, "error": str(e), "error_code": "GET_EXAMPLES_ERROR"}
