"""
Show Solution Catalog Service (Platform SDK)

Returns the catalog of available platform solutions.

Contract: docs/intent_contracts/coexistence/intent_show_solution_catalog.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class ShowSolutionCatalogService(PlatformIntentService):
    """
    Show Solution Catalog Service using Platform SDK.
    
    Handles the `show_solution_catalog` intent:
    - Returns available solutions
    - Includes solution details and capabilities
    """
    
    intent_type = "show_solution_catalog"
    
    def __init__(self, service_id: str = "show_solution_catalog_service"):
        """Initialize Show Solution Catalog Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute show_solution_catalog intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with solution catalog
        """
        self.logger.info(f"Executing show_solution_catalog: {ctx.execution_id}")
        
        include_details = ctx.intent.parameters.get("include_details", True)
        category_filter = ctx.intent.parameters.get("category")
        
        # Build catalog
        catalog = self._build_catalog(include_details, category_filter)
        
        self.logger.info(f"✅ Solution catalog generated with {len(catalog['solutions'])} solutions")
        
        return {
            "artifacts": {
                "catalog": catalog
            },
            "events": [{
                "type": "solution_catalog_shown",
                "event_id": generate_event_id(),
                "solution_count": len(catalog["solutions"])
            }]
        }
    
    def _build_catalog(self, include_details: bool, category_filter: str = None) -> Dict[str, Any]:
        """Build solution catalog."""
        solutions = [
            {
                "id": "content_solution",
                "name": "Content Solution",
                "category": "content",
                "description": "Upload, parse, and manage files with AI-powered content understanding",
                "status": "active",
                "icon": "folder",
                "capabilities": ["File upload", "Content parsing", "Semantic embeddings", "File management"],
                "journeys": ["FileIngestionJourney", "FileParsingJourney", "EmbeddingGenerationJourney"],
                "liaison_agent": "content_liaison_agent"
            },
            {
                "id": "insights_solution",
                "name": "Insights Solution",
                "category": "analytics",
                "description": "Analyze data quality, discover patterns, and visualize relationships",
                "status": "active",
                "icon": "chart",
                "capabilities": ["Data quality assessment", "AI interpretation", "Lineage visualization", "Relationship mapping"],
                "journeys": ["DataQualityJourney", "DataInterpretationJourney", "LineageVisualizationJourney"],
                "liaison_agent": "insights_liaison_agent"
            },
            {
                "id": "operations_solution",
                "name": "Operations Solution",
                "category": "operations",
                "description": "Create SOPs, optimize workflows, and analyze operational patterns",
                "status": "active",
                "icon": "cog",
                "capabilities": ["SOP generation", "Workflow optimization", "Coexistence analysis", "Process documentation"],
                "journeys": ["SOPGenerationJourney", "WorkflowOptimizationJourney", "CoexistenceAnalysisJourney"],
                "liaison_agent": "operations_liaison_agent"
            },
            {
                "id": "outcomes_solution",
                "name": "Outcomes Solution",
                "category": "strategy",
                "description": "Synthesize insights into outcomes, generate roadmaps, and create POCs",
                "status": "active",
                "icon": "target",
                "capabilities": ["Outcome synthesis", "Roadmap generation", "POC creation", "Blueprint design"],
                "journeys": ["OutcomeSynthesisJourney", "RoadmapGenerationJourney", "POCCreationJourney"],
                "liaison_agent": "outcomes_liaison_agent"
            },
            {
                "id": "coexistence_solution",
                "name": "Coexistence Solution",
                "category": "navigation",
                "description": "Platform entry point with AI Guide Agent for navigation and assistance",
                "status": "active",
                "icon": "compass",
                "capabilities": ["Platform introduction", "AI-guided navigation", "Solution routing", "Agent handoffs"],
                "journeys": ["GuidedNavigationJourney", "PlatformOnboardingJourney"],
                "liaison_agent": "guide_agent"
            }
        ]
        
        # Apply category filter if specified
        if category_filter:
            solutions = [s for s in solutions if s["category"] == category_filter]
        
        # Remove details if not requested
        if not include_details:
            solutions = [
                {"id": s["id"], "name": s["name"], "description": s["description"], "status": s["status"]}
                for s in solutions
            ]
        
        return {
            "solutions": solutions,
            "total_count": len(solutions),
            "categories": ["content", "analytics", "operations", "strategy", "navigation"],
            "generated_at": datetime.utcnow().isoformat()
        }
