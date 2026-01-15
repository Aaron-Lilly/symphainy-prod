"""
Proposal Agent Base - Context-Aware Roadmap/POC Proposals
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
            collaboration_router=collaboration_router
        )
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate roadmap/POC proposal based on user journey.
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
