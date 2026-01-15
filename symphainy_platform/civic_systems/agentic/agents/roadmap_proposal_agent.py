"""
Roadmap Proposal Agent - Proposal Agent for Outcomes Realm

Context-aware roadmap and POC proposal generation.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List

from .proposal_agent import ProposalAgentBase
from symphainy_platform.runtime.execution_context import ExecutionContext


class RoadmapProposalAgent(ProposalAgentBase):
    """
    Roadmap Proposal Agent - Proposal agent for Outcomes realm.
    
    Generates context-aware roadmaps and POC proposals based on user journey.
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
        Generate roadmap/POC proposal based on user journey.
        """
        journey = request.get("journey", {})
        platform_context = request.get("platform_context", {})
        proposal_type = request.get("proposal_type", "roadmap")
        
        # Generate proposal
        proposal = await self.generate_proposal(
            journey=journey,
            platform_context=platform_context,
            request=request,
            context=context
        )
        
        return {
            "artifact_type": "proposal",
            "artifact": {
                "proposal": proposal,
                "proposal_type": proposal_type,
                "context_aware": True
            },
            "confidence": 0.82
        }
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return f"Roadmap Proposal Agent ({self.agent_id}) - Context-aware roadmap/POC proposals"
    
    async def generate_proposal(
        self,
        journey: Dict[str, Any],
        platform_context: Dict[str, Any],
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate proposal (roadmap or POC).
        """
        proposal_type = request.get("proposal_type", "roadmap")
        journey_stages = journey.get("stages", [])
        
        proposal = {
            "type": proposal_type,
            "journey_stages": len(journey_stages),
            "recommendations": []
        }
        
        # Generate recommendations based on journey stages
        for stage in journey_stages:
            stage_name = stage.get("name", "Unknown Stage")
            proposal["recommendations"].append({
                "stage": stage_name,
                "recommendation": f"Optimize {stage_name} for coexistence",
                "priority": "medium"
            })
        
        return proposal
