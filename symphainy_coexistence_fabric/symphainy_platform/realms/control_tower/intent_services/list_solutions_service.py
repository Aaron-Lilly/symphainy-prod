"""
List Solutions Intent Service

Implements the list_solutions intent for the Control Tower Realm.

Purpose: List all registered solutions with their status, capabilities,
and MCP server information.

WHAT (Intent Service Role): I list all platform solutions
HOW (Intent Service Implementation): I query the Solution Registry
    and return comprehensive solution information
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


class ListSolutionsService(BaseIntentService):
    """
    Intent service for listing registered solutions.
    
    Returns information about all platform solutions including:
    - Solution ID and description
    - Status (active/inactive)
    - Supported journeys
    - MCP server tools
    - SOA APIs
    """
    
    # Solution metadata (canonical source of truth)
    SOLUTIONS = {
        "content_solution": {
            "name": "Content Solution",
            "description": "Manages file ingestion, parsing, and content lifecycle",
            "realm": "content",
            "journeys": [
                "FileIngestionJourney",
                "FileParsingJourney",
                "DeterministicEmbeddingJourney",
                "FileManagementJourney"
            ],
            "mcp_prefix": "content_",
            "soa_apis": ["compose_journey", "ingest_and_parse", "create_embeddings"]
        },
        "insights_solution": {
            "name": "Insights Solution",
            "description": "Provides data analysis, quality assessment, and intelligence",
            "realm": "insights",
            "journeys": [
                "DataQualityJourney",
                "DataInterpretationJourney",
                "LineageVisualizationJourney",
                "StructuredExtractionJourney"
            ],
            "mcp_prefix": "insights_",
            "soa_apis": ["compose_journey", "assess_quality", "interpret_data", "visualize_lineage"]
        },
        "operations_solution": {
            "name": "Operations Solution",
            "description": "Handles workflow optimization, SOP generation, coexistence analysis",
            "realm": "operations",
            "journeys": [
                "WorkflowOptimizationJourney",
                "SOPGenerationJourney",
                "CoexistenceAnalysisJourney"
            ],
            "mcp_prefix": "ops_",
            "soa_apis": ["compose_journey", "optimize_workflow", "generate_sop", "analyze_coexistence"]
        },
        "outcomes_solution": {
            "name": "Outcomes Solution",
            "description": "Synthesizes outcomes, roadmaps, POCs, and blueprints",
            "realm": "outcomes",
            "journeys": [
                "OutcomeSynthesisJourney",
                "RoadmapGenerationJourney",
                "POCCreationJourney",
                "BlueprintCreationJourney"
            ],
            "mcp_prefix": "outcomes_",
            "soa_apis": ["compose_journey", "synthesize", "generate_roadmap", "create_poc"]
        },
        "coexistence_solution": {
            "name": "Coexistence Solution",
            "description": "Platform entry, navigation, Guide Agent, and Liaison Agents",
            "realm": "coexistence",
            "journeys": [
                "IntroductionJourney",
                "NavigationJourney",
                "GuideAgentJourney"
            ],
            "mcp_prefix": "coexist_",
            "soa_apis": ["compose_journey", "introduce_platform", "navigate_to_solution", "start_guide_session"]
        }
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize ListSolutionsService."""
        super().__init__(
            service_id="list_solutions_service",
            intent_type="list_solutions",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the list_solutions intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            # Optional filters
            status_filter = intent_params.get("status")  # "active", "inactive", or None for all
            realm_filter = intent_params.get("realm")  # Filter by realm
            include_details = intent_params.get("include_details", True)
            
            # Get solutions list
            solutions = await self._get_solutions(status_filter, realm_filter, include_details)
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success", "solution_count": len(solutions)},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "solutions": solutions,
                "total_count": len(solutions),
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "solutions_listed",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list solutions: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_code": "LIST_SOLUTIONS_ERROR"
            }
    
    async def _get_solutions(
        self, 
        status_filter: Optional[str], 
        realm_filter: Optional[str],
        include_details: bool
    ) -> List[Dict[str, Any]]:
        """Get list of solutions with optional filtering."""
        solutions = []
        
        for solution_id, info in self.SOLUTIONS.items():
            # Apply filters
            if realm_filter and info["realm"] != realm_filter:
                continue
            
            solution = {
                "solution_id": solution_id,
                "name": info["name"],
                "description": info["description"],
                "realm": info["realm"],
                "status": "active"  # All solutions are active in this implementation
            }
            
            # Apply status filter
            if status_filter and solution["status"] != status_filter:
                continue
            
            if include_details:
                solution["journeys"] = info["journeys"]
                solution["mcp_prefix"] = info["mcp_prefix"]
                solution["soa_apis"] = info["soa_apis"]
                solution["mcp_tools"] = self._get_mcp_tools(solution_id, info)
            
            solutions.append(solution)
        
        return solutions
    
    def _get_mcp_tools(self, solution_id: str, info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get MCP tools for a solution."""
        prefix = info["mcp_prefix"]
        tools = []
        
        for api in info["soa_apis"]:
            tools.append({
                "tool_name": f"{prefix}{api}",
                "description": f"{info['name']} - {api.replace('_', ' ').title()}",
                "parameters": ["context", "params"]
            })
        
        return tools
