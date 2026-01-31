"""
Interpret Data Self Discovery Service (Platform SDK)

AI-driven semantic discovery using InsightsEDAAgent.

Uses ctx.reasoning.agents.invoke() for real AI analysis.

Contract: docs/intent_contracts/journey_insights_data_interpretation/intent_interpret_data_self_discovery.md
"""

from typing import Dict, Any, List
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class InterpretDataSelfDiscoveryService(PlatformIntentService):
    """
    Interpret Data Self Discovery Service using Platform SDK.
    
    Uses REAL InsightsEDAAgent via ctx.reasoning.agents.invoke() for:
    - Entity discovery
    - Relationship detection
    - Semantic meaning extraction
    
    NO MORE SIMULATED ANALYSIS - This uses actual LLM reasoning.
    """
    
    def __init__(self, service_id: str = "interpret_data_self_discovery_service"):
        """Initialize Interpret Data Self Discovery Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute interpret_data_self_discovery intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with AI-powered discovery results
        """
        self.logger.info(f"Executing interpret_data_self_discovery: {ctx.execution_id}")
        
        parsed_file_id = ctx.intent.parameters.get("parsed_file_id")
        discovery_options = ctx.intent.parameters.get("discovery_options", {})
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for self-discovery")
        
        # Get parsed content
        parsed_content = await ctx.platform.get_parsed_file(
            parsed_file_id=parsed_file_id,
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id
        )
        
        if not parsed_content:
            raise ValueError(f"Parsed file not found: {parsed_file_id}")
        
        # Use REAL InsightsEDAAgent for AI-powered discovery
        interpretation = await self._discover_via_agent(ctx, parsed_content, discovery_options)
        
        # Build interpretation result
        interpretation_result = {
            "interpretation_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "mode": "self_discovery",
            "interpretation": interpretation,
            "used_real_llm": interpretation.get("used_real_llm", False),
            "interpreted_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Self-discovery interpretation complete")
        
        return {
            "artifacts": {
                "interpretation": interpretation_result
            },
            "events": [{
                "type": "data_interpreted",
                "event_id": generate_event_id(),
                "mode": "self_discovery",
                "used_real_llm": interpretation.get("used_real_llm", False)
            }]
        }
    
    async def _discover_via_agent(
        self,
        ctx: PlatformContext,
        parsed_content: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Discover insights using real InsightsEDAAgent."""
        depth = options.get("depth", "medium")
        include_entities = options.get("include_entities", True)
        include_relationships = options.get("include_relationships", True)
        
        # Try to invoke real InsightsEDAAgent
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "insights_eda_agent",
                    params={
                        "action": "discover",
                        "content": parsed_content.get("content"),
                        "structure": parsed_content.get("structure"),
                        "depth": depth,
                        "include_entities": include_entities,
                        "include_relationships": include_relationships
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    result = agent_result.get("result", {})
                    result["used_real_llm"] = True
                    self.logger.info("✅ Got interpretation from real InsightsEDAAgent")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"InsightsEDAAgent invocation failed: {e}")
        
        # Fallback to basic heuristic analysis
        self.logger.warning("Falling back to heuristic analysis")
        return self._heuristic_discovery(parsed_content, options)
    
    def _heuristic_discovery(
        self,
        parsed_content: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Heuristic fallback when agent unavailable."""
        content = parsed_content.get("content", {})
        structure = parsed_content.get("structure", {})
        
        # Basic entity extraction from structure
        entities = []
        if isinstance(structure, dict):
            for field_name, field_info in structure.items():
                entities.append({
                    "name": field_name,
                    "type": field_info.get("type", "unknown") if isinstance(field_info, dict) else "field",
                    "confidence": 0.6
                })
        
        # Basic relationship inference
        relationships = []
        if len(entities) > 1:
            relationships.append({
                "source": entities[0]["name"],
                "target": entities[-1]["name"],
                "type": "related_to",
                "confidence": 0.4
            })
        
        return {
            "entities": entities[:10],  # Limit
            "relationships": relationships,
            "semantic_summary": "Heuristic analysis - invoke real agent for deeper insights",
            "confidence": 0.5,
            "used_real_llm": False,
            "fallback_reason": "Agent unavailable"
        }
