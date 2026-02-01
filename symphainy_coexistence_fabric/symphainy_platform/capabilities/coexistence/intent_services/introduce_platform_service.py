"""
Introduce Platform Service (Platform SDK)

Introduces the platform to new users with welcome message and guidance.

Contract: docs/intent_contracts/coexistence/intent_introduce_platform.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class IntroducePlatformService(PlatformIntentService):
    """
    Introduce Platform Service using Platform SDK.
    
    Handles the `introduce_platform` intent:
    - Returns welcome message
    - Lists available solutions
    - Provides getting started guidance
    """
    
    intent_type = "introduce_platform"
    
    def __init__(self, service_id: str = "introduce_platform_service"):
        """Initialize Introduce Platform Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute introduce_platform intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with platform introduction content
        """
        self.logger.info(f"Executing introduce_platform: {ctx.execution_id}")
        
        user_context = ctx.intent.parameters.get("user_context", {})
        personalize = ctx.intent.parameters.get("personalize", True)
        
        # Build introduction content
        introduction = self._build_introduction(user_context, personalize)
        
        self.logger.info(f"✅ Platform introduction generated")
        
        return {
            "artifacts": {
                "introduction": introduction
            },
            "events": [{
                "type": "platform_introduced",
                "event_id": generate_event_id(),
                "tenant_id": ctx.tenant_id
            }]
        }
    
    def _build_introduction(self, user_context: Dict[str, Any], personalize: bool) -> Dict[str, Any]:
        """Build platform introduction content."""
        introduction = {
            "welcome": {
                "title": "Welcome to Symphainy Platform",
                "message": "Symphainy is an AI-powered platform that helps you manage content, derive insights, optimize operations, and achieve strategic outcomes.",
                "tagline": "Transform your workflows with intelligent automation"
            },
            "solutions": [
                {
                    "id": "content_solution",
                    "name": "Content Solution",
                    "description": "Upload, parse, and manage files with AI-powered content understanding",
                    "icon": "folder",
                    "capabilities": ["File upload", "Content parsing", "Semantic embeddings", "File management"]
                },
                {
                    "id": "insights_solution",
                    "name": "Insights Solution",
                    "description": "Analyze data quality, discover patterns, and visualize relationships",
                    "icon": "chart",
                    "capabilities": ["Data quality assessment", "AI interpretation", "Lineage visualization", "Relationship mapping"]
                },
                {
                    "id": "operations_solution",
                    "name": "Operations Solution",
                    "description": "Create SOPs, optimize workflows, and analyze operational patterns",
                    "icon": "cog",
                    "capabilities": ["SOP generation", "Workflow optimization", "Coexistence analysis", "Process documentation"]
                },
                {
                    "id": "outcomes_solution",
                    "name": "Outcomes Solution",
                    "description": "Synthesize insights into outcomes, generate roadmaps, and create POCs",
                    "icon": "target",
                    "capabilities": ["Outcome synthesis", "Roadmap generation", "POC creation", "Blueprint design"]
                }
            ],
            "getting_started": {
                "steps": [
                    {"step": 1, "title": "Upload your data", "description": "Start by uploading files to the Content Solution"},
                    {"step": 2, "title": "Analyze and understand", "description": "Use Insights to assess data quality and discover patterns"},
                    {"step": 3, "title": "Optimize processes", "description": "Create SOPs and workflows with Operations"},
                    {"step": 4, "title": "Achieve outcomes", "description": "Generate roadmaps and deliverables with Outcomes"}
                ],
                "quick_actions": [
                    {"action": "initiate_guide_agent", "label": "Start with AI Guide"},
                    {"action": "show_solution_catalog", "label": "Browse Solutions"},
                    {"action": "upload_file", "label": "Upload a File"}
                ]
            },
            "ai_assistant": {
                "available": True,
                "name": "Guide Agent",
                "description": "AI-powered assistant to help you navigate the platform and accomplish your goals"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Personalize if requested and context available
        if personalize and user_context:
            if user_context.get("industry"):
                introduction["personalization"] = {
                    "industry": user_context.get("industry"),
                    "message": f"We've tailored recommendations for the {user_context.get('industry')} industry."
                }
        
        return introduction
