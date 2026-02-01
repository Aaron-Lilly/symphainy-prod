"""
Analyze Unstructured Data Service (Platform SDK)

Analyzes unstructured data for business insights.

Contract: docs/intent_contracts/journey_insights_analysis/intent_analyze_unstructured_data.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class AnalyzeUnstructuredDataService(PlatformIntentService):
    """
    Analyze Unstructured Data Service using Platform SDK.
    
    Analyzes unstructured data (text, documents) for:
    - Topic extraction
    - Sentiment analysis
    - Key phrase detection
    
    Returns unavailable status if AI agent not available (no fake data).
    """
    
    intent_type = "analyze_unstructured_data"
    
    def __init__(self, service_id: str = "analyze_unstructured_data_service"):
        """Initialize Analyze Unstructured Data Service."""
        super().__init__(service_id=service_id, intent_type="analyze_unstructured_data")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute analyze_unstructured_data intent."""
        self.logger.info(f"Executing analyze_unstructured_data: {ctx.execution_id}")
        
        parsed_file_id = ctx.intent.parameters.get("parsed_file_id")
        analysis_type = ctx.intent.parameters.get("analysis_type", "topics")
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required")
        
        # Get parsed content
        parsed_content = await ctx.platform.get_parsed_file(
            parsed_file_id=parsed_file_id,
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id
        )
        
        if not parsed_content:
            raise ValueError(f"Parsed file not found: {parsed_file_id}")
        
        # Try to use StructuredExtractionAgent for AI analysis
        analysis = await self._analyze_via_agent(ctx, parsed_content, analysis_type)
        
        analysis_result = {
            "analysis_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "analysis_type": analysis_type,
            "analysis": analysis,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Unstructured data analysis complete")
        
        return {
            "artifacts": {
                "analysis": analysis_result
            },
            "events": [{
                "type": "unstructured_data_analyzed",
                "event_id": generate_event_id(),
                "analysis_type": analysis_type
            }]
        }
    
    async def _analyze_via_agent(
        self,
        ctx: PlatformContext,
        parsed_content: Dict[str, Any],
        analysis_type: str
    ) -> Dict[str, Any]:
        """Analyze using StructuredExtractionAgent."""
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "structured_extraction_agent",
                    params={
                        "action": "extract",
                        "content": parsed_content.get("content"),
                        "analysis_type": analysis_type
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    result = agent_result.get("result", {})
                    result["used_real_llm"] = True
                    return result
                    
            except Exception as e:
                self.logger.error(f"Agent invocation failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "used_real_llm": False
                }
        
        # Agent not available - return unavailable status (NO FAKE DATA)
        self.logger.warning("AI reasoning service not available for unstructured data analysis")
        return {
            "status": "unavailable",
            "error": "AI reasoning service not configured",
            "analysis_type": analysis_type,
            "used_real_llm": False,
            "note": "Unstructured data analysis requires AI agent - please ensure reasoning service is configured"
        }
