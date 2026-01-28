"""
Show Solution Catalog Intent Service

Implements the show_solution_catalog intent for the Coexistence Realm.

Purpose: Display the catalog of available solutions with their
capabilities and how to access them.

WHAT (Intent Service Role): I show available solutions
HOW (Intent Service Implementation): I return structured catalog
    of all solutions with capabilities and access methods
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


class ShowSolutionCatalogService(BaseIntentService):
    """
    Intent service for showing solution catalog.
    
    Provides detailed information about each solution:
    - Description and capabilities
    - Available journeys
    - How to access via API or agents
    """
    
    SOLUTION_CATALOG = {
        "content_solution": {
            "name": "Content Solution",
            "realm": "content",
            "icon": "📁",
            "tagline": "Intelligent file and content management",
            "description": "Upload, parse, and manage your files with AI-powered understanding.",
            "capabilities": [
                {"name": "File Ingestion", "description": "Upload files from various sources"},
                {"name": "Content Parsing", "description": "Extract structured data from documents"},
                {"name": "Embedding Creation", "description": "Generate semantic embeddings for search"},
                {"name": "File Management", "description": "Archive, retrieve, and manage files"}
            ],
            "journeys": [
                {"name": "FileIngestionJourney", "description": "Complete file upload workflow"},
                {"name": "FileParsingJourney", "description": "Parse and extract content"},
                {"name": "DeterministicEmbeddingJourney", "description": "Create searchable embeddings"}
            ],
            "use_cases": [
                "Upload invoices for processing",
                "Parse contracts for key terms",
                "Index documents for search"
            ],
            "mcp_tools": ["content_compose_journey", "content_ingest_file", "content_parse"]
        },
        "insights_solution": {
            "name": "Insights Solution",
            "realm": "insights",
            "icon": "🔍",
            "tagline": "AI-powered data analysis and discovery",
            "description": "Analyze your data to discover patterns, assess quality, and generate insights.",
            "capabilities": [
                {"name": "Data Quality Assessment", "description": "Evaluate data completeness and accuracy"},
                {"name": "Data Interpretation", "description": "AI-driven data understanding"},
                {"name": "Lineage Visualization", "description": "Track data flow and transformations"},
                {"name": "Relationship Mapping", "description": "Discover entity relationships"}
            ],
            "journeys": [
                {"name": "DataQualityJourney", "description": "Comprehensive quality assessment"},
                {"name": "DataInterpretationJourney", "description": "AI-powered interpretation"},
                {"name": "LineageVisualizationJourney", "description": "Visualize data lineage"}
            ],
            "use_cases": [
                "Assess data quality before migration",
                "Understand data relationships",
                "Generate data dictionaries"
            ],
            "mcp_tools": ["insights_compose_journey", "insights_assess_quality", "insights_interpret"]
        },
        "operations_solution": {
            "name": "Operations Solution",
            "realm": "operations",
            "icon": "⚙️",
            "tagline": "Workflow optimization and SOP generation",
            "description": "Optimize processes, generate SOPs, and analyze system coexistence.",
            "capabilities": [
                {"name": "Process Optimization", "description": "Identify and reduce friction"},
                {"name": "SOP Generation", "description": "Create standard operating procedures"},
                {"name": "Workflow Creation", "description": "Build automated workflows"},
                {"name": "Coexistence Analysis", "description": "Analyze system interactions"}
            ],
            "journeys": [
                {"name": "WorkflowOptimizationJourney", "description": "Optimize existing workflows"},
                {"name": "SOPGenerationJourney", "description": "Generate SOPs from processes"},
                {"name": "CoexistenceAnalysisJourney", "description": "Analyze coexistence patterns"}
            ],
            "use_cases": [
                "Generate SOPs for new processes",
                "Optimize order-to-cash workflow",
                "Analyze ERP-CRM coexistence"
            ],
            "mcp_tools": ["ops_compose_journey", "ops_generate_sop", "ops_analyze_coexistence"]
        },
        "outcomes_solution": {
            "name": "Outcomes Solution",
            "realm": "outcomes",
            "icon": "🎯",
            "tagline": "Strategic deliverables and roadmaps",
            "description": "Synthesize outcomes, create roadmaps, POCs, and strategic blueprints.",
            "capabilities": [
                {"name": "Outcome Synthesis", "description": "Combine insights into outcomes"},
                {"name": "Roadmap Generation", "description": "Create strategic roadmaps"},
                {"name": "POC Creation", "description": "Generate proof-of-concept proposals"},
                {"name": "Blueprint Creation", "description": "Design coexistence blueprints"}
            ],
            "journeys": [
                {"name": "OutcomeSynthesisJourney", "description": "Synthesize strategic outcomes"},
                {"name": "RoadmapGenerationJourney", "description": "Generate implementation roadmaps"},
                {"name": "POCCreationJourney", "description": "Create POC proposals"}
            ],
            "use_cases": [
                "Create transformation roadmap",
                "Generate POC for new integration",
                "Synthesize migration blueprint"
            ],
            "mcp_tools": ["outcomes_compose_journey", "outcomes_synthesize", "outcomes_roadmap"]
        },
        "coexistence_solution": {
            "name": "Coexistence Solution",
            "realm": "coexistence",
            "icon": "🤝",
            "tagline": "Your guide to platform navigation",
            "description": "Navigate the platform, get guidance, and connect with specialist agents.",
            "capabilities": [
                {"name": "Platform Introduction", "description": "Learn about platform capabilities"},
                {"name": "Guided Navigation", "description": "Find the right solution for your needs"},
                {"name": "Guide Agent", "description": "AI assistant for platform guidance"},
                {"name": "Specialist Handoff", "description": "Connect with domain experts"}
            ],
            "journeys": [
                {"name": "IntroductionJourney", "description": "Platform introduction and onboarding"},
                {"name": "NavigationJourney", "description": "Navigate to the right solution"},
                {"name": "GuideAgentJourney", "description": "Interactive AI guidance"}
            ],
            "use_cases": [
                "Get started with the platform",
                "Find the right solution",
                "Get help from an AI guide"
            ],
            "mcp_tools": ["coexist_compose_journey", "coexist_navigate", "coexist_guide"]
        }
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize ShowSolutionCatalogService."""
        super().__init__(
            service_id="show_solution_catalog_service",
            intent_type="show_solution_catalog",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the show_solution_catalog intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            solution_filter = intent_params.get("solution_id")
            include_journeys = intent_params.get("include_journeys", True)
            include_mcp = intent_params.get("include_mcp_tools", True)
            
            catalog = self._build_catalog(solution_filter, include_journeys, include_mcp)
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success"},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "catalog": catalog,
                "solution_count": len(catalog),
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "catalog_shown",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to show catalog: {e}")
            return {"success": False, "error": str(e)}
    
    def _build_catalog(
        self, 
        solution_filter: Optional[str],
        include_journeys: bool,
        include_mcp: bool
    ) -> Dict[str, Any]:
        """Build the solution catalog."""
        if solution_filter:
            if solution_filter not in self.SOLUTION_CATALOG:
                return {}
            catalog = {solution_filter: self.SOLUTION_CATALOG[solution_filter].copy()}
        else:
            catalog = {k: v.copy() for k, v in self.SOLUTION_CATALOG.items()}
        
        # Filter out optional fields
        for solution_id, solution in catalog.items():
            if not include_journeys:
                solution.pop("journeys", None)
            if not include_mcp:
                solution.pop("mcp_tools", None)
        
        return catalog
