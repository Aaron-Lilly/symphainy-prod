"""
Workflow Optimization Specialist Agent - Workflow Optimization Agent

Reviews workflows and suggests Coexistence optimizations.
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

from typing import Dict, Any, List

from .workflow_optimization_agent import WorkflowOptimizationAgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext


class WorkflowOptimizationSpecialist(WorkflowOptimizationAgentBase):
    """
    Workflow Optimization Specialist - Workflow optimization agent.
    
    Reviews workflows and suggests human+AI coexistence optimizations.
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: List[str],
        collaboration_router=None
    ):
        super().__init__(
            agent_id=agent_id,
            capabilities=capabilities,
            collaboration_router=collaboration_router
        )
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Review workflow and suggest optimizations.
        """
        workflow_id = request.get("workflow_id")
        workflow = request.get("workflow", {})
        
        # Analyze workflow for Coexistence opportunities
        analysis = await self.analyze_workflow(workflow, context)
        
        # Generate optimization suggestions
        suggestions = await self.generate_suggestions(analysis, context)
        
        return {
            "artifact_type": "proposal",
            "artifact": {
                "workflow_analysis": analysis,
                "optimization_suggestions": suggestions
            },
            "confidence": 0.87
        }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return f"Workflow Optimization Specialist ({self.agent_id}) - Reviews workflows and suggests Coexistence optimizations"
    
    async def analyze_workflow(
        self,
        workflow: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Analyze workflow for Coexistence opportunities.
        """
        # Extract workflow structure
        steps = workflow.get("steps", [])
        
        analysis = {
            "workflow_id": workflow.get("workflow_id", "unknown"),
            "steps_count": len(steps),
            "coexistence_opportunities": []
        }
        
        # Identify opportunities (simple heuristic for MVP)
        for i, step in enumerate(steps):
            step_type = step.get("type", "unknown")
            if step_type in ["manual", "human_review"]:
                analysis["coexistence_opportunities"].append({
                    "step_index": i,
                    "step_name": step.get("name", f"Step {i}"),
                    "opportunity": "Consider AI-assisted automation",
                    "confidence": 0.7
                })
        
        return analysis
    
    async def generate_suggestions(
        self,
        analysis: Dict[str, Any],
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """
        Generate optimization suggestions.
        """
        suggestions = []
        
        opportunities = analysis.get("coexistence_opportunities", [])
        for opp in opportunities:
            suggestions.append({
                "type": "coexistence_optimization",
                "step": opp["step_name"],
                "recommendation": opp["opportunity"],
                "impact": "medium",
                "effort": "low"
            })
        
        return suggestions if suggestions else []
        