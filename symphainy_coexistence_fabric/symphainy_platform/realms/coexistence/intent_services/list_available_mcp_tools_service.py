"""
List Available MCP Tools Intent Service

Implements the list_available_mcp_tools intent for the Coexistence Realm.

Purpose: List all available MCP tools from all solutions that can be
invoked by agents.

WHAT (Intent Service Role): I list MCP tools for agent discovery
HOW (Intent Service Implementation): I query Curator for all registered
    MCP tools across all solutions
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class ListAvailableMCPToolsService(BaseIntentService):
    """
    Intent service for listing available MCP tools.
    
    Returns all MCP tools registered with Curator including:
    - Tool name and description
    - Required parameters
    - Owning solution
    """
    
    # MCP tools catalog (would normally come from Curator)
    MCP_TOOLS_CATALOG = {
        "content_": [
            {
                "tool_name": "content_compose_journey",
                "description": "Compose a content journey (file ingestion, parsing, etc.)",
                "parameters": {
                    "journey_name": {"type": "string", "required": True},
                    "params": {"type": "object", "required": False}
                },
                "solution": "content_solution"
            },
            {
                "tool_name": "content_ingest_file",
                "description": "Ingest a file into the platform",
                "parameters": {
                    "file_content": {"type": "string", "required": True},
                    "filename": {"type": "string", "required": True}
                },
                "solution": "content_solution"
            },
            {
                "tool_name": "content_parse",
                "description": "Parse uploaded content",
                "parameters": {
                    "artifact_id": {"type": "string", "required": True}
                },
                "solution": "content_solution"
            }
        ],
        "insights_": [
            {
                "tool_name": "insights_compose_journey",
                "description": "Compose an insights journey",
                "parameters": {
                    "journey_name": {"type": "string", "required": True},
                    "params": {"type": "object", "required": False}
                },
                "solution": "insights_solution"
            },
            {
                "tool_name": "insights_assess_quality",
                "description": "Assess data quality for an artifact",
                "parameters": {
                    "artifact_id": {"type": "string", "required": True}
                },
                "solution": "insights_solution"
            },
            {
                "tool_name": "insights_interpret",
                "description": "AI-powered data interpretation",
                "parameters": {
                    "artifact_id": {"type": "string", "required": True},
                    "mode": {"type": "string", "required": False, "default": "self_discovery"}
                },
                "solution": "insights_solution"
            }
        ],
        "ops_": [
            {
                "tool_name": "ops_compose_journey",
                "description": "Compose an operations journey",
                "parameters": {
                    "journey_name": {"type": "string", "required": True},
                    "params": {"type": "object", "required": False}
                },
                "solution": "operations_solution"
            },
            {
                "tool_name": "ops_generate_sop",
                "description": "Generate an SOP from process description",
                "parameters": {
                    "process_description": {"type": "string", "required": True}
                },
                "solution": "operations_solution"
            },
            {
                "tool_name": "ops_analyze_coexistence",
                "description": "Analyze system coexistence",
                "parameters": {
                    "systems": {"type": "array", "required": True}
                },
                "solution": "operations_solution"
            }
        ],
        "outcomes_": [
            {
                "tool_name": "outcomes_compose_journey",
                "description": "Compose an outcomes journey",
                "parameters": {
                    "journey_name": {"type": "string", "required": True},
                    "params": {"type": "object", "required": False}
                },
                "solution": "outcomes_solution"
            },
            {
                "tool_name": "outcomes_synthesize",
                "description": "Synthesize outcomes from inputs",
                "parameters": {
                    "artifact_ids": {"type": "array", "required": True}
                },
                "solution": "outcomes_solution"
            },
            {
                "tool_name": "outcomes_roadmap",
                "description": "Generate a strategic roadmap",
                "parameters": {
                    "goals": {"type": "array", "required": True}
                },
                "solution": "outcomes_solution"
            }
        ],
        "coexist_": [
            {
                "tool_name": "coexist_introduce_platform",
                "description": "Introduce the platform to a user",
                "parameters": {},
                "solution": "coexistence_solution"
            },
            {
                "tool_name": "coexist_show_catalog",
                "description": "Show solution catalog",
                "parameters": {},
                "solution": "coexistence_solution"
            },
            {
                "tool_name": "coexist_navigate_to_solution",
                "description": "Navigate to a specific solution",
                "parameters": {
                    "solution_id": {"type": "string", "required": True}
                },
                "solution": "coexistence_solution"
            }
        ]
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize ListAvailableMCPToolsService."""
        super().__init__(
            service_id="list_available_mcp_tools_service",
            intent_type="list_available_mcp_tools",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the list_available_mcp_tools intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            solution_filter = intent_params.get("solution")
            prefix_filter = intent_params.get("prefix")
            
            # Get tools from Curator or fallback catalog
            tools = await self._get_mcp_tools(solution_filter, prefix_filter)
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success", "tool_count": len(tools)},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "tools": tools,
                "tool_count": len(tools),
                "prefixes": list(self.MCP_TOOLS_CATALOG.keys()),
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "mcp_tools_listed",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list MCP tools: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_mcp_tools(
        self, 
        solution_filter: Optional[str],
        prefix_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get MCP tools from Curator or fallback catalog."""
        tools = []
        
        # Try to get from Curator first (if available via public_works)
        # For now, use the fallback catalog
        
        for prefix, prefix_tools in self.MCP_TOOLS_CATALOG.items():
            # Apply prefix filter
            if prefix_filter and not prefix.startswith(prefix_filter):
                continue
            
            for tool in prefix_tools:
                # Apply solution filter
                if solution_filter and tool.get("solution") != solution_filter:
                    continue
                
                tools.append(tool)
        
        return tools
