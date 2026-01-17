"""
Solution Synthesis Service - Pure Data Processing for Solution Creation

Enabling service for creating platform solutions from roadmaps/POCs.

WHAT (Enabling Service Role): I execute solution creation
HOW (Enabling Service Implementation): I use Solution SDK to create and register solutions

Key Principle: Uses Solution SDK (Platform SDK) - no special powers needed.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder
from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry


class SolutionSynthesisService:
    """
    Solution Synthesis Service - Creates platform solutions from artifacts.
    
    Uses Solution SDK (Platform SDK) to create and register solutions.
    No special powers - uses standard Platform SDK mechanisms.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Solution Synthesis Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Solution Registry (create new instance for MVP)
        # In production, this could be injected or accessed via context
        self.solution_registry = SolutionRegistry()
    
    async def create_solution_from_artifact(
        self,
        solution_source: str,  # "roadmap" or "poc"
        source_id: str,
        source_data: Any,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Create platform solution from roadmap or POC artifact.
        
        Uses Solution Builder to create solution, then registers it.
        
        Args:
            solution_source: Source type ("roadmap" or "poc")
            source_id: Source artifact ID
            source_data: Source artifact data
            tenant_id: Tenant ID
            context: Execution context
        
        Returns:
            Dict with solution data
        """
        # Parse source data
        if isinstance(source_data, bytes):
            import json
            source_data = json.loads(source_data.decode('utf-8'))
        
        # Extract goals and context from source
        goals = []
        constraints = []
        
        if solution_source == "roadmap":
            roadmap = source_data.get("roadmap", {}) or source_data
            strategic_plan = source_data.get("strategic_plan", {})
            
            # Extract goals from strategic plan
            goals = strategic_plan.get("goals", [])
            
            # Extract phases as objectives
            phases = roadmap.get("phases", [])
            for phase in phases:
                if phase.get("status") == "completed":
                    goals.append(f"Complete {phase.get('phase', 'phase')}")
        
        elif solution_source == "poc":
            proposal = source_data.get("proposal", {}) or source_data
            
            # Extract objectives as goals
            objectives = proposal.get("objectives", [])
            goals = objectives
            
            # Extract constraints from financials
            financials = proposal.get("financials", {})
            if financials.get("estimated_cost"):
                constraints.append(f"Budget: ${financials['estimated_cost']}")
        
        elif solution_source == "blueprint":
            blueprint = source_data.get("blueprint", {}) or source_data
            
            # Extract goals from roadmap phases
            roadmap = blueprint.get("roadmap", {})
            if roadmap:
                phases = roadmap.get("phases", [])
                for phase in phases:
                    objectives = phase.get("objectives", [])
                    goals.extend([f"{phase.get('name', 'Phase')}: {obj}" for obj in objectives])
            
            # Extract constraints from integration requirements
            sections = blueprint.get("sections", [])
            for section in sections:
                if section.get("section") == "Integration Requirements":
                    resource_requirements = section.get("resource_requirements", [])
                    constraints.extend(resource_requirements)
        
        # Create solution using Solution Builder
        solution_builder = SolutionBuilder()
        
        # Set context
        solution_builder.with_context(
            goals=goals,
            constraints=constraints,
            risk="Medium",  # Default risk level
            metadata={
                "source": solution_source,
                "source_id": source_id,
                "tenant_id": tenant_id
            }
        )
        
        # Add domain bindings based on pillar summaries
        # Content domain
        solution_builder.add_domain_binding(
            domain="content",
            system_name="symphainy_platform",
            adapter_type="internal_adapter",
            adapter_config={},
            metadata={"realm": "content"}
        )
        
        # Insights domain
        solution_builder.add_domain_binding(
            domain="insights",
            system_name="symphainy_platform",
            adapter_type="internal_adapter",
            adapter_config={},
            metadata={"realm": "insights"}
        )
        
        # Journey domain
        solution_builder.add_domain_binding(
            domain="journey",
            system_name="symphainy_platform",
            adapter_type="internal_adapter",
            adapter_config={},
            metadata={"realm": "journey"}
        )
        
        # Register intents (based on source)
        if solution_source == "roadmap":
            solution_builder.register_intents([
                "synthesize_outcome",
                "generate_roadmap",
                "create_solution"
            ])
        elif solution_source == "poc":
            solution_builder.register_intents([
                "synthesize_outcome",
                "create_poc",
                "create_solution"
            ])
        elif solution_source == "blueprint":
            # Blueprint-based solutions need journey and content intents
            solution_builder.register_intents([
                "analyze_coexistence",
                "create_blueprint",
                "create_workflow",
                "create_solution_from_blueprint"
            ])
        
        # Build solution
        solution = solution_builder.build()
        
        # Register solution (if registry available)
        if self.solution_registry:
            if self.solution_registry.register_solution(solution):
                self.logger.info(f"Solution registered: {solution.solution_id}")
            else:
                self.logger.warning(f"Failed to register solution: {solution.solution_id}")
        else:
            # For MVP: Log that solution was created but not registered
            # In production, registry should be injected
            self.logger.info(f"Solution created (not registered - no registry): {solution.solution_id}")
        
        return {
            "solution_id": solution.solution_id,
            "solution": solution.to_dict(),
            "source": solution_source,
            "source_id": source_id
        }
