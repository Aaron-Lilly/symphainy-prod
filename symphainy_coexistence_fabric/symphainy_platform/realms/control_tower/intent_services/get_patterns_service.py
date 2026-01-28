"""
Get Patterns Intent Service

Implements the get_patterns intent for the Control Tower Realm.

Purpose: Retrieve platform architectural patterns for developer reference.

WHAT (Intent Service Role): I provide architectural pattern documentation
HOW (Intent Service Implementation): I return structured pattern information
    from the platform's pattern catalog
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


class GetPatternsService(BaseIntentService):
    """
    Intent service for retrieving architectural patterns.
    
    Provides documentation on:
    - Solution Pattern
    - Intent Service Pattern
    - Public Works Pattern
    - MCP Server Pattern
    - Journey Orchestration Pattern
    """
    
    PATTERNS = {
        "solution_pattern": {
            "name": "Solution Pattern",
            "description": "Top-level platform construct that composes Journeys and exposes SOA APIs",
            "when_to_use": "When creating a user-facing capability that spans multiple intents",
            "components": [
                "Solution class (extends SolutionBase)",
                "Journey orchestrators",
                "MCP Server",
                "SOA API definitions"
            ],
            "example": """
class ContentSolution(SolutionBase):
    SOLUTION_ID = "content_solution"
    
    async def compose_journey(self, context, journey_params):
        # Orchestrate intent services
        pass
    
    def get_soa_apis(self):
        return {"compose_journey": self._soa_compose_journey}
""",
            "anti_patterns": [
                "Direct infrastructure access",
                "Orchestration logic in Realms",
                "MCP servers in Realms"
            ]
        },
        "intent_service_pattern": {
            "name": "Intent Service Pattern",
            "description": "Atomic service that handles a single intent type",
            "when_to_use": "When implementing a specific platform capability",
            "components": [
                "Service class (extends BaseIntentService)",
                "execute() method",
                "Artifact registration",
                "Telemetry recording"
            ],
            "example": """
class IngestFileService(BaseIntentService):
    def __init__(self, public_works, state_surface):
        super().__init__(
            service_id="ingest_file_service",
            intent_type="ingest_file",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(self, context, params=None):
        # Handle the ingest_file intent
        pass
""",
            "anti_patterns": [
                "Multiple intent handling",
                "Direct database access",
                "Orchestration logic"
            ]
        },
        "public_works_pattern": {
            "name": "Public Works Pattern",
            "description": "Infrastructure abstraction layer - all infrastructure via abstractions",
            "when_to_use": "When accessing any infrastructure (storage, database, auth, etc.)",
            "components": [
                "Adapters (infrastructure implementations)",
                "Abstractions (business interfaces)",
                "Protocols (interface contracts)"
            ],
            "example": """
# CORRECT - Use abstraction
file_storage = public_works.get_file_storage_abstraction()
await file_storage.upload_file(...)

# WRONG - Direct adapter access
await gcs_adapter.upload(...)  # Anti-pattern!
""",
            "anti_patterns": [
                "Direct adapter access in business logic",
                "Infrastructure code in Realms",
                "Bypassing abstractions"
            ]
        },
        "mcp_server_pattern": {
            "name": "MCP Server Pattern",
            "description": "Solutions expose tools as MCP tools for agent consumption",
            "when_to_use": "When enabling agents to use solution capabilities",
            "components": [
                "MCPServerBase extension",
                "Tool registration",
                "Curator registration"
            ],
            "example": """
class ContentMCPServer(MCPServerBase):
    def __init__(self, solution):
        super().__init__(prefix="content_")
        self.solution = solution
    
    def register_tools(self):
        self.register_tool("compose_journey", self.solution.compose_journey)
""",
            "anti_patterns": [
                "MCP servers in Realms",
                "Direct intent execution from MCP tools",
                "Missing Curator registration"
            ]
        },
        "journey_orchestration_pattern": {
            "name": "Journey Orchestration Pattern",
            "description": "Solutions compose journeys that orchestrate multiple intents",
            "when_to_use": "When a user workflow requires multiple intents in sequence",
            "components": [
                "Journey class",
                "compose_journey() method",
                "Intent sequencing",
                "Context management"
            ],
            "example": """
class FileIngestionJourney:
    async def compose_journey(self, context, params):
        # 1. Ingest file
        ingest_result = await self._execute_intent("ingest_file", context, params)
        
        # 2. Parse content
        parse_result = await self._execute_intent("parse_content", context, {
            "artifact_id": ingest_result["artifact_id"]
        })
        
        return {"artifacts": [ingest_result, parse_result]}
""",
            "anti_patterns": [
                "Orchestration in intent services",
                "Orchestration in Realms",
                "Missing context propagation"
            ]
        }
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize GetPatternsService."""
        super().__init__(
            service_id="get_patterns_service",
            intent_type="get_patterns",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the get_patterns intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            pattern_name = intent_params.get("pattern_name")  # Optional - specific pattern
            include_examples = intent_params.get("include_examples", True)
            
            if pattern_name:
                # Get specific pattern
                if pattern_name not in self.PATTERNS:
                    raise ValueError(f"Unknown pattern: {pattern_name}. Available: {list(self.PATTERNS.keys())}")
                patterns = {pattern_name: self.PATTERNS[pattern_name]}
            else:
                # Get all patterns
                patterns = self.PATTERNS
            
            # Optionally strip examples
            if not include_examples:
                patterns = {
                    k: {key: val for key, val in v.items() if key != "example"}
                    for k, v in patterns.items()
                }
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success"},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "patterns": patterns,
                "pattern_count": len(patterns),
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "patterns_retrieved",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ]
            }
            
        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_PATTERN"
            }
        except Exception as e:
            self.logger.error(f"Failed to get patterns: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_code": "GET_PATTERNS_ERROR"
            }
