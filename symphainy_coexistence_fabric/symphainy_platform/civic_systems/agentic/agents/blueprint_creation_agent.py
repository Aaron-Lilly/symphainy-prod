"""
Blueprint Creation Agent - Coexistence Blueprint Design

Reasons about workflow transformation and designs coexistence blueprints
with human-positive responsibility matrices.

WHAT (Agent Role): I design coexistence blueprints with friction removal focus
HOW (Agent Implementation): I use MCP tools to analyze workflows and create blueprints
"""

import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional
from ..agent_base import AgentBase
from ..models.agent_runtime_context import AgentRuntimeContext
from symphainy_platform.runtime.execution_context import ExecutionContext


class BlueprintCreationAgent(AgentBase):
    """
    Blueprint Creation Agent - Designs coexistence blueprints.
    
    Purpose: Reason about workflow transformation and design blueprints
    with human-positive responsibility matrices, focusing on friction
    removal and human augmentation.
    
    Capabilities:
    - Blueprint design
    - Workflow transformation reasoning
    - Phase design
    - Responsibility matrix creation
    """
    
    def __init__(
        self,
        agent_id: str = "blueprint_creation_agent",
        capabilities: Optional[List[str]] = None,
        collaboration_router=None,
        public_works=None,
        **kwargs
    ):
        """Initialize Blueprint Creation Agent."""
        if capabilities is None:
            capabilities = [
                "blueprint_design",
                "workflow_transformation_reasoning",
                "phase_design",
                "responsibility_matrix_creation"
            ]
        
        super().__init__(
            agent_id=agent_id,
            agent_type="specialized",
            capabilities=capabilities,
            collaboration_router=collaboration_router,
            **kwargs
        )
        self.public_works = public_works
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext,
        runtime_context: Optional[AgentRuntimeContext] = None
    ) -> Dict[str, Any]:
        """
        Process blueprint creation request.
        
        Args:
            request: Request with workflow_id and blueprint options
            context: Execution context
            runtime_context: Optional runtime context
        
        Returns:
            Dict with blueprint artifact
        """
        workflow_id = request.get("workflow_id")
        coexistence_analysis_id = request.get("coexistence_analysis_id")
        blueprint_options = request.get("blueprint_options", {})
        
        # 1. Get workflow data
        workflow_data = {}
        if workflow_id:
            workflow_data = await self.use_tool(
                "operations_get_workflow",
                {"workflow_id": workflow_id},
                context
            )
        
        # 2. Get or perform coexistence analysis
        coexistence_data = {}
        if coexistence_analysis_id:
            coexistence_data = await self.use_tool(
                "operations_get_coexistence_analysis",
                {"analysis_id": coexistence_analysis_id},
                context
            )
        elif workflow_id:
            coexistence_data = await self.use_tool(
                "operations_analyze_coexistence",
                {"workflow_id": workflow_id},
                context
            )
        
        # 3. Design blueprint with human-positive focus
        blueprint = await self._design_blueprint(
            workflow_data=workflow_data,
            coexistence_data=coexistence_data,
            options=blueprint_options,
            context=context
        )
        
        # 4. Create responsibility matrix
        responsibility_matrix = await self._create_responsibility_matrix(
            blueprint=blueprint,
            coexistence_data=coexistence_data,
            context=context
        )
        
        blueprint["responsibility_matrix"] = responsibility_matrix
        
        return {
            "artifact_type": "blueprint",
            "artifact": blueprint,
            "confidence": 0.85
        }
    
    async def _design_blueprint(
        self,
        workflow_data: Dict[str, Any],
        coexistence_data: Dict[str, Any],
        options: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Design coexistence blueprint with human-positive focus."""
        # Extract friction points from coexistence analysis
        friction_points = coexistence_data.get("friction_points", [])
        
        # Design phases based on friction removal
        phases = []
        for i, friction in enumerate(friction_points[:5]):  # Max 5 phases
            phase = {
                "phase_number": i + 1,
                "name": f"Phase {i + 1}: {friction.get('category', 'Optimization')}",
                "focus": "friction_removal",
                "friction_addressed": friction.get("description", ""),
                "human_value": self._identify_human_value(friction),
                "ai_augmentation": self._identify_ai_augmentation(friction),
                "milestones": [
                    f"Identify {friction.get('category', 'issue')} patterns",
                    f"Design human-AI collaboration for {friction.get('category', 'task')}",
                    f"Validate with stakeholders"
                ]
            }
            phases.append(phase)
        
        # If no friction points, create default phases
        if not phases:
            phases = [
                {
                    "phase_number": 1,
                    "name": "Phase 1: Assessment",
                    "focus": "understanding",
                    "human_value": "Preserve domain expertise",
                    "ai_augmentation": "Data analysis support",
                    "milestones": ["Analyze current state", "Identify opportunities"]
                },
                {
                    "phase_number": 2,
                    "name": "Phase 2: Implementation",
                    "focus": "integration",
                    "human_value": "Decision authority",
                    "ai_augmentation": "Recommendation engine",
                    "milestones": ["Deploy augmentation tools", "Train users"]
                }
            ]
        
        return {
            "blueprint_id": f"blueprint_{context.execution_id}",
            "workflow_id": workflow_data.get("workflow_id"),
            "title": options.get("title", "Coexistence Blueprint"),
            "description": options.get("description", "Human-AI coexistence implementation plan"),
            "phases": phases,
            "coexistence_state": {
                "friction_points_addressed": len(friction_points),
                "human_tasks_preserved": coexistence_data.get("human_tasks_count", 0),
                "ai_augmented_tasks": coexistence_data.get("ai_assisted_tasks_count", 0)
            }
        }
    
    def _identify_human_value(self, friction: Dict[str, Any]) -> str:
        """Identify human value to preserve for a friction point."""
        category = friction.get("category", "").lower()
        if "decision" in category:
            return "Decision-making authority preserved"
        elif "communication" in category:
            return "Human relationship management"
        elif "creative" in category:
            return "Creative direction and judgment"
        else:
            return "Domain expertise and oversight"
    
    def _identify_ai_augmentation(self, friction: Dict[str, Any]) -> str:
        """Identify AI augmentation opportunity for a friction point."""
        category = friction.get("category", "").lower()
        if "data" in category:
            return "Data processing and analysis"
        elif "repetitive" in category:
            return "Automation of routine tasks"
        elif "speed" in category:
            return "Real-time processing support"
        else:
            return "Information synthesis and recommendations"
    
    async def _create_responsibility_matrix(
        self,
        blueprint: Dict[str, Any],
        coexistence_data: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Create human-positive responsibility matrix."""
        responsibilities = []
        
        # Create responsibilities for each phase
        for phase in blueprint.get("phases", []):
            responsibility = {
                "phase": phase.get("name"),
                "human_responsibilities": [
                    "Strategic oversight",
                    "Quality validation",
                    "Stakeholder communication",
                    phase.get("human_value", "Domain expertise")
                ],
                "ai_responsibilities": [
                    "Data processing",
                    "Pattern recognition",
                    "Recommendation generation",
                    phase.get("ai_augmentation", "Analysis support")
                ],
                "collaboration_points": [
                    "Review AI recommendations",
                    "Approve automated actions",
                    "Provide feedback for improvement"
                ]
            }
            responsibilities.append(responsibility)
        
        return {
            "matrix_type": "human_positive",
            "focus": "augmentation_not_replacement",
            "responsibilities": responsibilities,
            "governance": {
                "human_override": True,
                "ai_transparency": True,
                "continuous_feedback": True
            }
        }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Blueprint Creation Agent - Designs coexistence blueprints with human-positive focus"
