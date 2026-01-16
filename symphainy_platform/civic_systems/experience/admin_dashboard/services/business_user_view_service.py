"""
Business User View Service - Solution Composition & Business Tools

Provides business user-focused capabilities: solution composition, templates, feature requests.

WHAT (Business User View Role): I provide business user tools for solution composition
HOW (Business User View Implementation): I expose Solution Builder and templates
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger
from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder
from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry


# Solution templates (pre-built configurations)
SOLUTION_TEMPLATES = {
    "content_insights": {
        "title": "Content + Insights Solution",
        "description": "Solution combining content processing with insights generation",
        "config": {
            "context": {
                "goals": ["Process content", "Generate insights"],
                "constraints": [],
                "risk": "Low"
            },
            "domain_service_bindings": [
                {
                    "domain": "content",
                    "system_name": "symphainy_platform",
                    "adapter_type": "internal_adapter"
                },
                {
                    "domain": "insights",
                    "system_name": "symphainy_platform",
                    "adapter_type": "internal_adapter"
                }
            ],
            "supported_intents": [
                "ingest_file",
                "parse_content",
                "analyze_content",
                "interpret_data"
            ]
        }
    },
    "full_pillar": {
        "title": "Full Pillar Solution",
        "description": "Solution using all pillars: Content, Insights, Journey, Outcomes",
        "config": {
            "context": {
                "goals": ["Complete platform showcase"],
                "constraints": [],
                "risk": "Medium"
            },
            "domain_service_bindings": [
                {
                    "domain": "content",
                    "system_name": "symphainy_platform",
                    "adapter_type": "internal_adapter"
                },
                {
                    "domain": "insights",
                    "system_name": "symphainy_platform",
                    "adapter_type": "internal_adapter"
                },
                {
                    "domain": "journey",
                    "system_name": "symphainy_platform",
                    "adapter_type": "internal_adapter"
                },
                {
                    "domain": "outcomes",
                    "system_name": "symphainy_platform",
                    "adapter_type": "internal_adapter"
                }
            ],
            "supported_intents": [
                "ingest_file",
                "parse_content",
                "analyze_content",
                "optimize_process",
                "synthesize_outcome"
            ]
        }
    }
}


class BusinessUserViewService:
    """
    Business User View Service - Solution composition and business tools.
    
    Provides:
    - Solution composition guide
    - Solution Builder (advanced, gated)
    - Solution templates (gated)
    - Feature request system
    """
    
    def __init__(
        self,
        solution_registry: Optional[SolutionRegistry] = None,
        public_works: Optional[Any] = None
    ):
        """
        Initialize Business User View Service.
        
        Args:
            solution_registry: Solution registry for solution registration
            public_works: Public Works Foundation Service
        """
        self.logger = get_logger(self.__class__.__name__)
        self.solution_registry = solution_registry or SolutionRegistry()
        self.public_works = public_works
        self.templates = SOLUTION_TEMPLATES.copy()
    
    async def get_composition_guide(self) -> Dict[str, Any]:
        """
        Get solution composition guide.
        
        Returns:
            Dict with composition guide
        """
        return {
            "steps": [
                {
                    "step": 1,
                    "title": "Define Goals",
                    "description": "Define what you want to achieve with this solution"
                },
                {
                    "step": 2,
                    "title": "Select Domains",
                    "description": "Choose which domains (Content, Insights, Journey, Outcomes) to include"
                },
                {
                    "step": 3,
                    "title": "Configure Intents",
                    "description": "Select which intents your solution will support"
                },
                {
                    "step": 4,
                    "title": "Set Context",
                    "description": "Define constraints and risk level"
                },
                {
                    "step": 5,
                    "title": "Review & Register",
                    "description": "Review your solution and register it with the platform"
                }
            ],
            "available_domains": ["content", "insights", "journey", "outcomes"],
            "available_intents": {
                "content": ["ingest_file", "parse_content", "extract_embeddings"],
                "insights": ["analyze_content", "interpret_data", "map_relationships"],
                "journey": ["optimize_process", "generate_sop", "create_blueprint"],
                "outcomes": ["synthesize_outcome", "generate_roadmap", "create_poc"]
            }
        }
    
    async def get_solution_templates(self) -> Dict[str, Any]:
        """
        Get available solution templates.
        
        Returns:
            Dict with solution templates
        """
        return {
            "templates": self.templates,
            "count": len(self.templates)
        }
    
    async def create_from_template(
        self,
        template_id: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create solution from template.
        
        Args:
            template_id: Template identifier
            customizations: Optional customizations to apply
        
        Returns:
            Dict with created solution
        """
        if template_id not in self.templates:
            return {
                "error": f"Template not found: {template_id}",
                "available_templates": list(self.templates.keys())
            }
        
        template = self.templates[template_id]
        config = template["config"].copy()
        
        # Apply customizations
        if customizations:
            if "context" in customizations:
                config["context"].update(customizations["context"])
            if "domain_service_bindings" in customizations:
                config["domain_service_bindings"] = customizations["domain_service_bindings"]
            if "supported_intents" in customizations:
                config["supported_intents"] = customizations["supported_intents"]
        
        # Build solution
        try:
            builder = SolutionBuilder.from_config(config)
            solution = builder.build()
            
            return {
                "solution": solution.to_dict(),
                "template_id": template_id,
                "template_title": template["title"]
            }
        except Exception as e:
            self.logger.error(f"Failed to create solution from template: {e}", exc_info=True)
            return {
                "error": str(e),
                "message": "Failed to create solution from template"
            }
    
    async def compose_solution(
        self,
        solution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compose a solution (advanced builder, gated).
        
        Args:
            solution_config: Solution configuration
        
        Returns:
            Dict with composed solution
        """
        try:
            builder = SolutionBuilder.from_config(solution_config)
            solution = builder.build()
            
            return {
                "solution": solution.to_dict(),
                "valid": True,
                "message": "Solution composed successfully"
            }
        except Exception as e:
            self.logger.error(f"Solution composition error: {e}", exc_info=True)
            return {
                "error": str(e),
                "valid": False,
                "message": "Solution composition failed"
            }
    
    async def register_solution(
        self,
        solution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register a composed solution.
        
        Args:
            solution_config: Solution configuration
        
        Returns:
            Dict with registration result
        """
        try:
            builder = SolutionBuilder.from_config(solution_config)
            solution = builder.build()
            
            # Register solution
            if self.solution_registry.register_solution(solution):
                return {
                    "success": True,
                    "solution_id": solution.solution_id,
                    "message": "Solution registered successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to register solution",
                    "message": "Solution registration failed"
                }
        except Exception as e:
            self.logger.error(f"Solution registration error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Solution registration failed"
            }
    
    async def submit_feature_request(
        self,
        feature_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit a feature request.
        
        Args:
            feature_request: Feature request data
        
        Returns:
            Dict with submission result
        """
        # For MVP: Simple storage (in-memory or ArangoDB)
        # In Phase 2: Full workflow integration
        
        feature_id = f"feature_{feature_request.get('title', 'unknown').lower().replace(' ', '_')}"
        
        return {
            "success": True,
            "feature_request_id": feature_id,
            "message": "Feature request submitted successfully",
            "feature_request": feature_request
        }
