"""
POC Generation Service - Pure Data Processing for POC Proposal Generation

Enabling service for POC proposal generation.

WHAT (Enabling Service Role): I execute POC proposal generation
HOW (Enabling Service Implementation): I use Public Works abstractions and agents for reasoning

Key Principle: Pure data processing - agents reason, services execute.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from datetime import datetime

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.execution_context import ExecutionContext


class POCGenerationService:
    """
    POC Generation Service - Pure data processing for POC proposal generation.
    
    Uses agents for reasoning, Public Works abstractions for storage.
    Returns raw data only - no business logic.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize POC Generation Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
    
    async def generate_poc_proposal(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        additional_context: Dict[str, Any],
        poc_options: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate POC proposal from pillar summaries.
        
        Args:
            content_summary: Content pillar summary
            insights_summary: Insights pillar summary
            journey_summary: Journey pillar summary
            additional_context: Additional context from user
            poc_options: POC generation options
            tenant_id: Tenant ID
            context: Execution context
        
        Returns:
            Dict with POC proposal data
        """
        proposal_id = generate_event_id()
        
        # For MVP: Generate basic POC proposal structure
        # In full implementation: Use agents for reasoning
        proposal = {
            "proposal_id": proposal_id,
            "title": poc_options.get("title", "POC Proposal"),
            "description": "",
            "objectives": [],
            "scope": {},
            "timeline": poc_options.get("timeline", "3 months"),
            "resources": {},
            "success_criteria": [],
            "risks": [],
            "financials": {
                "estimated_cost": 0,
                "roi": 0,
                "payback_period": "N/A"
            }
        }
        
        # Extract objectives from summaries
        if content_summary:
            proposal["objectives"].append("Validate content processing capabilities")
        
        if insights_summary:
            proposal["objectives"].append("Validate insights generation capabilities")
        
        if journey_summary:
            proposal["objectives"].append("Validate journey design capabilities")
        
        # Add financials if provided
        if "financials" in poc_options:
            proposal["financials"].update(poc_options["financials"])
        
        return {
            "proposal_id": proposal_id,
            "proposal": proposal,
            "created_at": datetime.utcnow().isoformat()
        }
