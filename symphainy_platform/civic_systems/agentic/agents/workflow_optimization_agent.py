"""
Workflow Optimization Agent Base - Coexistence Optimization Suggestions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List
from ..agent_base import AgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext


class WorkflowOptimizationAgentBase(AgentBase):
    """
    Base for workflow optimization agents.
    
    Purpose: Review workflows, suggest Coexistence optimizations.
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: List[str],
        collaboration_router=None,
        **kwargs
    ):
        """Initialize workflow optimization agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="workflow_optimization",
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
        # 1. Get workflow (via Conductor SDK tool)
        workflow_id = request.get("workflow_id")
        workflow = await self.use_tool(
            "conductor_get_workflow",
            {"workflow_id": workflow_id},
            context
        )
        
        # 2. Analyze workflow for Coexistence opportunities
        analysis = await self.analyze_workflow(workflow, context)
        
        # 3. Generate optimization suggestions
        suggestions = await self.generate_suggestions(analysis, context)
        
        # 4. Return structured output (non-executing)
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
        return f"Workflow Optimization agent ({self.agent_id}) - Reviews workflows and suggests Coexistence optimizations"
    
    async def analyze_workflow(
        self,
        workflow: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Analyze workflow for Coexistence opportunities (abstract method).
        
        Subclasses should implement this.
        
        Args:
            workflow: Workflow dictionary
            context: Execution context
        
        Returns:
            Analysis dictionary
        """
        # Default implementation: Basic analysis
        return {
            "workflow_id": workflow.get("workflow_id", "unknown"),
            "steps_count": len(workflow.get("steps", [])),
            "coexistence_opportunities": []
        }
    
    async def generate_suggestions(
        self,
        analysis: Dict[str, Any],
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """
        Generate optimization suggestions (abstract method).
        
        Subclasses should implement this.
        
        Args:
            analysis: Analysis dictionary
            context: Execution context
        
        Returns:
            List of suggestion dictionaries
        """
        # Default implementation: Empty suggestions
        return []
