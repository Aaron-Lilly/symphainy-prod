"""
Developer View Service - Platform SDK Documentation & Developer Tools

Provides developer-focused capabilities: documentation, playground, feature submission.

WHAT (Developer View Role): I provide developer tools and documentation
HOW (Developer View Implementation): I expose Platform SDK documentation and playground
"""

import sys
from pathlib import Path

# Add project root to path
# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger
from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder
from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry


class DeveloperViewService:
    """
    Developer View Service - Developer tools and documentation.
    
    Provides:
    - Platform SDK documentation
    - Code examples
    - Patterns & best practices
    - Solution Builder Playground (gated)
    - Feature submission (gated - "Coming Soon" for MVP)
    """
    
    def __init__(
        self,
        solution_registry: Optional[SolutionRegistry] = None,
        public_works: Optional[Any] = None
    ):
        """
        Initialize Developer View Service.
        
        Args:
            solution_registry: Solution registry for playground
            public_works: Public Works Foundation Service
        """
        self.logger = get_logger(self.__class__.__name__)
        self.solution_registry = solution_registry or SolutionRegistry()
        self.public_works = public_works
    
    async def get_documentation(self, section: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Platform SDK documentation.
        
        Args:
            section: Optional documentation section
        
        Returns:
            Dict with documentation content
        """
        # For MVP: Return structure
        # In Phase 2: Load from markdown files or generate from code
        
        docs = {
            "sections": {
                "architecture": {
                    "title": "Architecture Overview",
                    "content": "Platform architecture: Runtime, Civic Systems, Realms, Foundations"
                },
                "solution_sdk": {
                    "title": "Solution SDK",
                    "content": "How to build and register solutions using Solution SDK"
                },
                "realm_sdk": {
                    "title": "Realm SDK",
                    "content": "How to implement realms using RealmBase and Runtime Participation Contract"
                },
                "smart_city_sdk": {
                    "title": "Smart City SDK",
                    "content": "Smart City SDK: Security Guard, Traffic Cop, Post Office"
                },
                "agentic_sdk": {
                    "title": "Agentic SDK",
                    "content": "How to implement agents using AgentBase and collaboration patterns"
                },
                "public_works": {
                    "title": "Public Works",
                    "content": "Public Works pattern: Adapters, Abstractions, Protocols"
                }
            }
        }
        
        if section:
            return docs["sections"].get(section, {})
        
        return docs
    
    async def get_code_examples(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get code examples.
        
        Args:
            category: Optional example category
        
        Returns:
            Dict with code examples
        """
        examples = {
            "creating_realm": {
                "title": "Creating a Realm",
                "language": "python",
                "code": """
from symphainy_platform.civic_systems.platform_sdk.realm_sdk import RealmBase
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext

class MyRealm(RealmBase):
    def __init__(self, realm_name: str = "my_realm"):
        super().__init__(realm_name)
    
    def declare_intents(self) -> List[str]:
        return ["my_intent"]
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        # Handle intent
        return {"artifacts": {}, "events": []}
"""
            },
            "building_solution": {
                "title": "Building a Solution",
                "language": "python",
                "code": """
from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder

solution = SolutionBuilder() \\
    .with_context(goals=["..."], constraints=["..."]) \\
    .add_domain_binding(domain="content", system_name="...", adapter_type="...") \\
    .register_intents(["ingest_file", "parse_content"]) \\
    .build()
"""
            }
        }
        
        if category:
            return examples.get(category, {})
        
        return {"examples": examples}
    
    async def get_patterns(self) -> Dict[str, Any]:
        """
        Get patterns and best practices.
        
        Returns:
            Dict with patterns
        """
        return {
            "patterns": {
                "realm_implementation": {
                    "title": "Realm Implementation Pattern",
                    "description": "How to implement realms following the Runtime Participation Contract"
                },
                "solution_composition": {
                    "title": "Solution Composition Pattern",
                    "description": "How to compose solutions from domain services"
                },
                "agent_collaboration": {
                    "title": "Agent Collaboration Pattern",
                    "description": "How agents collaborate via Runtime, not direct invocation"
                },
                "public_works_pattern": {
                    "title": "Public Works Pattern",
                    "description": "How to create adapters, abstractions, and protocols"
                }
            }
        }
    
    async def validate_solution(
        self,
        solution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a solution configuration (Solution Builder Playground).
        
        Args:
            solution_config: Solution configuration dictionary
        
        Returns:
            Dict with validation result
        """
        try:
            # Build solution from config
            builder = SolutionBuilder.from_config(solution_config)
            solution = builder.build()
            
            return {
                "valid": True,
                "solution": solution.to_dict(),
                "message": "Solution is valid"
            }
        except ValueError as e:
            return {
                "valid": False,
                "error": str(e),
                "message": "Solution validation failed"
            }
        except Exception as e:
            self.logger.error(f"Solution validation error: {e}", exc_info=True)
            return {
                "valid": False,
                "error": str(e),
                "message": "Internal error during validation"
            }
    
    async def preview_solution(
        self,
        solution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Preview a solution structure (Solution Builder Playground).
        
        Args:
            solution_config: Solution configuration dictionary
        
        Returns:
            Dict with solution preview
        """
        try:
            builder = SolutionBuilder.from_config(solution_config)
            solution = builder.build()
            
            return {
                "solution_id": solution.solution_id,
                "context": solution.solution_context.to_dict(),
                "domain_bindings": [b.to_dict() for b in solution.domain_service_bindings],
                "sync_strategies": [s.to_dict() for s in solution.sync_strategies],
                "supported_intents": solution.supported_intents,
                "metadata": solution.metadata
            }
        except Exception as e:
            self.logger.error(f"Solution preview error: {e}", exc_info=True)
            return {
                "error": str(e),
                "message": "Failed to generate preview"
            }
    
    async def submit_feature_request(
        self,
        feature_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit a feature request (gated - "Coming Soon" for MVP).
        
        Args:
            feature_request: Feature request data
        
        Returns:
            Dict with submission result
        """
        # For MVP: Return "Coming Soon" message
        # In Phase 2: Store feature request and trigger governance workflow
        
        return {
            "status": "coming_soon",
            "message": "Feature submission is coming soon! This will enable developers to submit feature proposals for platform team review.",
            "feature_request": feature_request  # Echo back for demo purposes
        }
