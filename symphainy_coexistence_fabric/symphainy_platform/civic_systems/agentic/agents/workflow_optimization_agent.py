"""
Workflow Optimization Agent Base - Coexistence Optimization Suggestions
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

from typing import Dict, Any, List, Optional
from ..agent_base import AgentBase
from ..models.agent_runtime_context import AgentRuntimeContext
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
            collaboration_router=collaboration_router,
            **kwargs
        )
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: AgentRuntimeContext,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request with assembled prompt (4-layer model).
        
        This method is called by AgentBase.process_request() after assembling
        the system and user messages from the 4-layer model.
        
        Args:
            system_message: Assembled system message (from layers 1-3)
            user_message: Assembled user message
            runtime_context: Runtime context with business_context
            context: Execution context
        
        Returns:
            Dict with workflow optimization suggestions
        """
        # Extract request from user_message or runtime_context
        request_data = {}
        try:
            import json
            if user_message.strip().startswith("{"):
                request_data = json.loads(user_message)
            else:
                # Try to extract from runtime_context.business_context
                if hasattr(runtime_context, 'business_context') and runtime_context.business_context:
                    request_data = runtime_context.business_context.get("request", {})
                # If still empty, try to infer from user_message
                if not request_data:
                    # Check if user_message contains workflow_id
                    if "workflow_id" in user_message.lower():
                        import re
                        workflow_id_match = re.search(r'workflow_id["\']?\s*[:=]\s*["\']?([^"\'\s]+)', user_message)
                        if workflow_id_match:
                            request_data = {"workflow_id": workflow_id_match.group(1)}
                    else:
                        # Default: empty request (will be handled by process_request)
                        request_data = {}
        except (json.JSONDecodeError, ValueError):
            request_data = {}
        
        # Use business context from runtime_context if available
        if runtime_context.business_context:
            request_data.setdefault("business_context", runtime_context.business_context)
        
        # Execute workflow optimization logic directly (avoid circular call)
        workflow_id = request_data.get("workflow_id")
        if not workflow_id:
            return {
                "artifact_type": "error",
                "artifact": {"error": "workflow_id is required"},
                "confidence": 0.0
            }
        
        # Get workflow via tool
        workflow = await self.use_tool(
            "conductor_get_workflow",
            {"workflow_id": workflow_id},
            context
        )
        
        # Analyze workflow
        analysis = await self.analyze_workflow(workflow, context)
        
        # Generate suggestions
        suggestions = await self.generate_suggestions(analysis, context)
        
        # Return structured output
        return {
            "artifact_type": "proposal",
            "artifact": {
                "workflow_analysis": analysis,
                "optimization_suggestions": suggestions
            },
            "confidence": 0.87
        }
    
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
