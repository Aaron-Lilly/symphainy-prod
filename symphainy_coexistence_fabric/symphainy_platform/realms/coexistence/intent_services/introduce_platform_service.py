"""
Introduce Platform Intent Service

Implements the introduce_platform intent for the Coexistence Realm.

Purpose: Introduce the platform to new users with welcome message,
available solutions, and getting started guidance.

WHAT (Intent Service Role): I welcome users and introduce the platform
HOW (Intent Service Implementation): I return structured introduction
    content including solutions, capabilities, and next steps
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class IntroducePlatformService(BaseIntentService):
    """
    Intent service for platform introduction.
    
    Provides:
    - Welcome message
    - Platform overview
    - Available solutions
    - Getting started steps
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize IntroducePlatformService."""
        super().__init__(
            service_id="introduce_platform_service",
            intent_type="introduce_platform",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the introduce_platform intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            user_context = intent_params.get("user_context", {})
            personalize = intent_params.get("personalize", True)
            
            # Build introduction content
            introduction = await self._build_introduction(user_context, personalize)
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success"},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "introduction": introduction,
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "platform_introduced",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to introduce platform: {e}")
            return {"success": False, "error": str(e)}
    
    async def _build_introduction(self, user_context: Dict, personalize: bool) -> Dict[str, Any]:
        """Build introduction content."""
        return {
            "welcome": {
                "title": "Welcome to SymphAIny",
                "message": "Your intelligent platform for data coexistence and business transformation.",
                "tagline": "Where AI meets enterprise data management"
            },
            "overview": {
                "description": """
SymphAIny is a governed execution platform that helps organizations:
- Understand and analyze their data across systems
- Generate operational procedures and workflows
- Create strategic roadmaps and outcomes
- Navigate the journey to AI-enabled operations
                """.strip(),
                "key_capabilities": [
                    "Intelligent file ingestion and parsing",
                    "AI-powered data analysis and insights",
                    "Automated SOP and workflow generation",
                    "Strategic outcome synthesis",
                    "Cross-system coexistence analysis"
                ]
            },
            "solutions": [
                {
                    "name": "Content Solution",
                    "description": "Upload, parse, and manage your files",
                    "icon": "📁",
                    "key_actions": ["Upload files", "Parse documents", "Create embeddings"]
                },
                {
                    "name": "Insights Solution",
                    "description": "Analyze data and discover patterns",
                    "icon": "🔍",
                    "key_actions": ["Assess data quality", "Interpret data", "Map relationships"]
                },
                {
                    "name": "Operations Solution",
                    "description": "Optimize workflows and generate SOPs",
                    "icon": "⚙️",
                    "key_actions": ["Generate SOPs", "Create workflows", "Analyze coexistence"]
                },
                {
                    "name": "Outcomes Solution",
                    "description": "Create strategic deliverables",
                    "icon": "🎯",
                    "key_actions": ["Synthesize outcomes", "Generate roadmaps", "Create POCs"]
                }
            ],
            "getting_started": {
                "steps": [
                    {"step": 1, "action": "Start a conversation with the Guide Agent", "description": "Get personalized guidance"},
                    {"step": 2, "action": "Upload your first file", "description": "Use Content Solution to ingest data"},
                    {"step": 3, "action": "Analyze your data", "description": "Use Insights Solution to understand your data"},
                    {"step": 4, "action": "Generate outcomes", "description": "Use Outcomes Solution to create deliverables"}
                ],
                "quick_start_prompt": "What would you like to accomplish today?"
            },
            "guide_agent": {
                "available": True,
                "description": "I'm your intelligent assistant. I can help you navigate the platform, understand capabilities, and guide you to the right solutions.",
                "suggested_prompts": [
                    "What can this platform do?",
                    "Help me upload and analyze a file",
                    "Generate an SOP for my workflow",
                    "Create a strategic roadmap"
                ]
            }
        }
