"""Get Solution Templates Service (Platform SDK)

Returns available solution templates for the Business User View.
"""

from typing import Dict, Any
from datetime import datetime
from utilities import get_logger, generate_event_id
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext


# Solution templates (pre-built configurations)
SOLUTION_TEMPLATES = {
    "content_insights": {
        "id": "content_insights",
        "title": "Content + Insights Solution",
        "description": "Solution combining content processing with insights generation",
        "domains": ["content", "insights"],
        "intents": ["ingest_file", "parse_content", "analyze_structured_data", "interpret_data_self_discovery"],
        "config": {
            "context": {
                "goals": ["Process content", "Generate insights"],
                "constraints": [],
                "risk": "Low"
            },
            "domain_service_bindings": [
                {"domain": "content", "system_name": "symphainy_platform", "adapter_type": "internal_adapter"},
                {"domain": "insights", "system_name": "symphainy_platform", "adapter_type": "internal_adapter"}
            ],
            "supported_intents": ["ingest_file", "parse_content", "analyze_structured_data", "interpret_data_self_discovery"]
        }
    },
    "full_platform": {
        "id": "full_platform",
        "title": "Full Platform Solution",
        "description": "Solution using all capabilities: Content, Insights, Operations, Outcomes",
        "domains": ["content", "insights", "operations", "outcomes"],
        "intents": ["ingest_file", "parse_content", "analyze_structured_data", "create_workflow", "synthesize_outcome"],
        "config": {
            "context": {
                "goals": ["Complete platform showcase"],
                "constraints": [],
                "risk": "Medium"
            },
            "domain_service_bindings": [
                {"domain": "content", "system_name": "symphainy_platform", "adapter_type": "internal_adapter"},
                {"domain": "insights", "system_name": "symphainy_platform", "adapter_type": "internal_adapter"},
                {"domain": "operations", "system_name": "symphainy_platform", "adapter_type": "internal_adapter"},
                {"domain": "outcomes", "system_name": "symphainy_platform", "adapter_type": "internal_adapter"}
            ],
            "supported_intents": ["ingest_file", "parse_content", "analyze_structured_data", "create_workflow", "synthesize_outcome"]
        }
    },
    "operations_focused": {
        "id": "operations_focused",
        "title": "Operations-Focused Solution",
        "description": "Solution for workflow and SOP generation",
        "domains": ["content", "operations"],
        "intents": ["ingest_file", "create_workflow", "generate_sop", "optimize_process"],
        "config": {
            "context": {
                "goals": ["Automate operations", "Generate SOPs"],
                "constraints": [],
                "risk": "Low"
            },
            "domain_service_bindings": [
                {"domain": "content", "system_name": "symphainy_platform", "adapter_type": "internal_adapter"},
                {"domain": "operations", "system_name": "symphainy_platform", "adapter_type": "internal_adapter"}
            ],
            "supported_intents": ["ingest_file", "create_workflow", "generate_sop", "optimize_process"]
        }
    }
}


class GetSolutionTemplatesService(PlatformIntentService):
    """Get Solution Templates Service using Platform SDK."""
    
    intent_type = "get_solution_templates"
    
    def __init__(self, service_id: str = "get_solution_templates_service"):
        super().__init__(service_id=service_id, intent_type="get_solution_templates")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        self.logger.info(f"Executing get_solution_templates: {ctx.execution_id}")
        
        # Return available templates
        templates_list = list(SOLUTION_TEMPLATES.values())
        
        result = {
            "templates_id": generate_event_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "templates": templates_list,
            "count": len(templates_list)
        }
        
        return {"artifacts": result, "events": []}
