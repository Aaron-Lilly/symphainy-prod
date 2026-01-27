"""
Proposal Agent Base - Context-Aware Roadmap/POC Proposals
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


class ProposalAgentBase(AgentBase):
    """
    Base for roadmap/POC proposal agents.
    
    Purpose: Context-aware, journey-informed proposals.
    """
    
    def __init__(
        self,
        agent_id: str,
        capabilities: List[str],
        collaboration_router=None,
        **kwargs
    ):
        """Initialize proposal agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="proposal",
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
            Dict with proposal artifacts
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
                # If still empty, use user_message as description
                if not request_data:
                    request_data = {"description": user_message.strip()}
        except (json.JSONDecodeError, ValueError):
            request_data = {"description": user_message.strip()}
        
        # Use business context from runtime_context if available
        if runtime_context.business_context:
            request_data.setdefault("business_context", runtime_context.business_context)
        
        # Execute proposal generation logic directly (avoid circular call)
        # Get user journey
        journey = await context.get_state("user_journey") if hasattr(context, 'get_state') else request_data.get("journey", {})
        
        # Get platform context via tool
        platform_context = await self.use_tool(
            "city_manager_get_platform_state",
            {},
            context
        )
        
        # Generate proposal
        proposal = await self.generate_proposal(
            journey=journey,
            platform_context=platform_context,
            request=request_data,
            context=context
        )
        
        # Return structured output
        return {
            "artifact_type": "proposal",
            "artifact": {
                "proposal": proposal,
                "context_aware": True
            },
            "confidence": 0.82
        }
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext,
        runtime_context: Optional[AgentRuntimeContext] = None
    ) -> Dict[str, Any]:
        """
        Generate roadmap/POC proposal based on user journey.
        
        ARCHITECTURAL PRINCIPLE: This method can be called directly, but for
        4-layer model support, it should be called via AgentBase.process_request().
        """
        # 1. Get user journey (via Runtime State Surface)
        journey = await context.get_state("user_journey") if hasattr(context, 'get_state') else request.get("journey", {})
        
        # 2. Get platform context (via Smart City SDK tool)
        platform_context = await self.use_tool(
            "city_manager_get_platform_state",
            {},
            context
        )
        
        # 3. Generate proposal
        proposal = await self.generate_proposal(
            journey=journey,
            platform_context=platform_context,
            request=request,
            context=context
        )
        
        # 4. Return structured output (non-executing)
        return {
            "artifact_type": "proposal",
            "artifact": {
                "proposal": proposal,
                "context_aware": True
            },
            "confidence": 0.82
        }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return f"Proposal agent ({self.agent_id}) - Context-aware roadmap/POC proposals"
    
    async def generate_proposal(
        self,
        journey: Dict[str, Any],
        platform_context: Dict[str, Any],
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate proposal (abstract method).
        
        Subclasses should implement this.
        
        Args:
            journey: User journey dictionary
            platform_context: Platform context dictionary
            request: Request dictionary
            context: Execution context
        
        Returns:
            Proposal dictionary
        """
        # Default implementation: Basic proposal
        return {
            "type": request.get("proposal_type", "roadmap"),
            "journey_stages": len(journey.get("stages", [])),
            "recommendations": []
        }
