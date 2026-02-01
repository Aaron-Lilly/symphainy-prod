"""Compose Solution Service (Platform SDK)

Creates solutions from templates or custom configurations.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from utilities import get_logger, generate_event_id
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext


# Import templates from the templates service
from .get_solution_templates_service import SOLUTION_TEMPLATES


class ComposeSolutionService(PlatformIntentService):
    """Compose Solution Service using Platform SDK."""
    
    intent_type = "compose_solution"
    
    def __init__(self, service_id: str = "compose_solution_service"):
        super().__init__(service_id=service_id, intent_type="compose_solution")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        self.logger.info(f"Executing compose_solution: {ctx.execution_id}")
        
        params = ctx.parameters or {}
        template_id = params.get("template_id")
        customizations = params.get("customizations", {})
        solution_config = params.get("solution_config")
        
        try:
            if template_id:
                # Create from template
                solution = await self._create_from_template(template_id, customizations)
            elif solution_config:
                # Create from custom config
                solution = await self._create_from_config(solution_config)
            else:
                return {
                    "artifacts": {
                        "error": "Either template_id or solution_config is required",
                        "success": False
                    },
                    "events": []
                }
            
            return {
                "artifacts": {
                    "solution": solution,
                    "success": True,
                    "created_at": datetime.utcnow().isoformat()
                },
                "events": [{
                    "event_type": "solution_composed",
                    "data": {"solution_id": solution.get("solution_id")}
                }]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to compose solution: {e}", exc_info=True)
            return {
                "artifacts": {
                    "error": str(e),
                    "success": False
                },
                "events": []
            }
    
    async def _create_from_template(
        self,
        template_id: str,
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create solution from template with optional customizations."""
        
        if template_id not in SOLUTION_TEMPLATES:
            raise ValueError(f"Template not found: {template_id}. Available: {list(SOLUTION_TEMPLATES.keys())}")
        
        template = SOLUTION_TEMPLATES[template_id]
        config = template["config"].copy()
        
        # Apply customizations
        if customizations:
            if "goals" in customizations:
                config["context"]["goals"] = customizations["goals"]
            if "constraints" in customizations:
                config["context"]["constraints"] = customizations["constraints"]
            if "additional_intents" in customizations:
                config["supported_intents"].extend(customizations["additional_intents"])
        
        # Generate solution
        solution_id = f"{template_id}_{generate_event_id()[:8]}"
        
        return {
            "solution_id": solution_id,
            "template_id": template_id,
            "template_title": template["title"],
            "context": config["context"],
            "domain_service_bindings": config["domain_service_bindings"],
            "supported_intents": config["supported_intents"],
            "created_from": "template"
        }
    
    async def _create_from_config(
        self,
        solution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create solution from custom configuration."""
        
        # Validate required fields
        required = ["context", "domain_service_bindings", "supported_intents"]
        for field in required:
            if field not in solution_config:
                raise ValueError(f"Missing required field: {field}")
        
        # Generate solution
        solution_id = f"custom_{generate_event_id()[:8]}"
        
        return {
            "solution_id": solution_id,
            "context": solution_config["context"],
            "domain_service_bindings": solution_config["domain_service_bindings"],
            "supported_intents": solution_config["supported_intents"],
            "metadata": solution_config.get("metadata", {}),
            "created_from": "custom_config"
        }
