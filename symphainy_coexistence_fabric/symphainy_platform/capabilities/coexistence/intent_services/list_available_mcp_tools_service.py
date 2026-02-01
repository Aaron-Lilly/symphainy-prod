"""
List Available MCP Tools Service (Platform SDK)

Lists available MCP tools for orchestration.

Contract: docs/intent_contracts/coexistence/intent_list_available_mcp_tools.md
"""

from typing import Dict, Any, List
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class ListAvailableMCPToolsService(PlatformIntentService):
    """
    List Available MCP Tools Service using Platform SDK.
    
    Handles the `list_available_mcp_tools` intent:
    - Discovers available MCP servers
    - Lists tools from each server
    - Returns tool catalog
    """
    
    intent_type = "list_available_mcp_tools"
    
    def __init__(self, service_id: str = "list_available_mcp_tools_service"):
        """Initialize List Available MCP Tools Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute list_available_mcp_tools intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with available MCP tools
        """
        self.logger.info(f"Executing list_available_mcp_tools: {ctx.execution_id}")
        
        solution_filter = ctx.intent.parameters.get("solution_id")
        category_filter = ctx.intent.parameters.get("category")
        
        # Get available tools
        tools = await self._discover_tools(ctx, solution_filter, category_filter)
        
        self.logger.info(f"✅ Discovered {len(tools)} MCP tools")
        
        return {
            "artifacts": {
                "tools": tools,
                "total_count": len(tools),
                "discovered_at": datetime.utcnow().isoformat()
            },
            "events": [{
                "type": "mcp_tools_listed",
                "event_id": generate_event_id(),
                "tool_count": len(tools)
            }]
        }
    
    async def _discover_tools(
        self,
        ctx: PlatformContext,
        solution_filter: str = None,
        category_filter: str = None
    ) -> List[Dict[str, Any]]:
        """Discover available MCP tools."""
        # Base tool catalog (these are registered by solutions)
        tools = [
            # Content Solution Tools
            {
                "tool_id": "content_ingest_file",
                "name": "Ingest File",
                "solution": "content_solution",
                "category": "content",
                "description": "Upload and ingest a file into the platform",
                "parameters": ["file_data", "filename", "content_type"]
            },
            {
                "tool_id": "content_parse",
                "name": "Parse Content",
                "solution": "content_solution",
                "category": "content",
                "description": "Parse and extract content from an uploaded file",
                "parameters": ["file_id"]
            },
            {
                "tool_id": "content_create_embeddings",
                "name": "Create Embeddings",
                "solution": "content_solution",
                "category": "content",
                "description": "Generate deterministic embeddings for parsed content",
                "parameters": ["parsed_file_id"]
            },
            # Insights Solution Tools
            {
                "tool_id": "insights_assess_quality",
                "name": "Assess Data Quality",
                "solution": "insights_solution",
                "category": "analytics",
                "description": "Assess data quality of ingested content",
                "parameters": ["artifact_id"]
            },
            {
                "tool_id": "insights_interpret",
                "name": "Interpret Data",
                "solution": "insights_solution",
                "category": "analytics",
                "description": "AI-powered data interpretation and insights",
                "parameters": ["artifact_id", "interpretation_mode"]
            },
            # Operations Solution Tools
            {
                "tool_id": "ops_generate_sop",
                "name": "Generate SOP",
                "solution": "operations_solution",
                "category": "operations",
                "description": "Generate Standard Operating Procedure from process description",
                "parameters": ["process_description", "context"]
            },
            {
                "tool_id": "ops_create_workflow",
                "name": "Create Workflow",
                "solution": "operations_solution",
                "category": "operations",
                "description": "Create an optimized workflow",
                "parameters": ["workflow_description"]
            },
            # Outcomes Solution Tools
            {
                "tool_id": "outcomes_synthesize",
                "name": "Synthesize Outcome",
                "solution": "outcomes_solution",
                "category": "strategy",
                "description": "Synthesize insights into strategic outcomes",
                "parameters": ["insight_ids", "outcome_type"]
            },
            {
                "tool_id": "outcomes_roadmap",
                "name": "Generate Roadmap",
                "solution": "outcomes_solution",
                "category": "strategy",
                "description": "Generate strategic roadmap",
                "parameters": ["outcome_id", "timeframe"]
            }
        ]
        
        # Apply filters
        if solution_filter:
            tools = [t for t in tools if t["solution"] == solution_filter]
        
        if category_filter:
            tools = [t for t in tools if t["category"] == category_filter]
        
        return tools
