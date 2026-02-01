"""
Analyze Coexistence Service (Platform SDK)

Analyzes coexistence patterns between legacy and modern systems.

Contract: docs/intent_contracts/journey_operations_coexistence/intent_analyze_coexistence.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class AnalyzeCoexistenceService(PlatformIntentService):
    """
    Analyze Coexistence Service using Platform SDK.
    
    Analyzes coexistence patterns using CoexistenceAnalysisAgent.
    Returns unavailable status if AI agent not available (no fake data).
    """
    
    intent_type = "analyze_coexistence"
    
    def __init__(self, service_id: str = "analyze_coexistence_service"):
        """Initialize Analyze Coexistence Service."""
        super().__init__(service_id=service_id, intent_type="analyze_coexistence")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute analyze_coexistence intent."""
        self.logger.info(f"Executing analyze_coexistence: {ctx.execution_id}")
        
        artifact_ids = ctx.intent.parameters.get("artifact_ids", [])
        analysis_type = ctx.intent.parameters.get("analysis_type", "full")
        
        # Analyze via CoexistenceAnalysisAgent
        analysis = await self._analyze_via_agent(ctx, artifact_ids, analysis_type)
        
        analysis_result = {
            "analysis_id": generate_event_id(),
            "artifact_ids": artifact_ids,
            "analysis_type": analysis_type,
            "analysis": analysis,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Coexistence analysis complete")
        
        return {
            "artifacts": {
                "analysis": analysis_result
            },
            "events": [{
                "type": "coexistence_analyzed",
                "event_id": generate_event_id()
            }]
        }
    
    async def _analyze_via_agent(
        self,
        ctx: PlatformContext,
        artifact_ids: list,
        analysis_type: str
    ) -> Dict[str, Any]:
        """Analyze using CoexistenceAnalysisAgent."""
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "coexistence_analysis_agent",
                    params={
                        "action": "analyze",
                        "artifact_ids": artifact_ids,
                        "analysis_type": analysis_type
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    return agent_result.get("result", {})
                    
            except Exception as e:
                self.logger.error(f"Agent invocation failed: {e}")
                return {
                    "status": "error",
                    "error": str(e)
                }
        
        # Agent not available - return unavailable status (NO FAKE DATA)
        self.logger.warning("AI reasoning service not available for coexistence analysis")
        return {
            "status": "unavailable",
            "error": "AI reasoning service not configured",
            "note": "Coexistence analysis requires AI agent - please ensure reasoning service is configured"
        }
