"""
Generate SOP Service (Platform SDK)

Generates Standard Operating Procedures using SOPGenerationAgent.

Uses ctx.reasoning.agents.invoke() for real AI SOP generation.

Contract: docs/intent_contracts/journey_operations_sop/intent_generate_sop.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class GenerateSOPService(PlatformIntentService):
    """
    Generate SOP Service using Platform SDK.
    
    Handles the `generate_sop` intent:
    - Invokes REAL SOPGenerationAgent via ctx.reasoning
    - Generates structured SOP documents
    - Supports multiple output formats
    """
    
    def __init__(self, service_id: str = "generate_sop_service"):
        """Initialize Generate SOP Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute generate_sop intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with generated SOP
        """
        self.logger.info(f"Executing generate_sop: {ctx.execution_id}")
        
        process_description = ctx.intent.parameters.get("process_description")
        context_data = ctx.intent.parameters.get("context", {})
        output_format = ctx.intent.parameters.get("output_format", "markdown")
        
        if not process_description:
            raise ValueError("process_description is required")
        
        # Generate SOP via REAL SOPGenerationAgent
        sop = await self._generate_via_agent(ctx, process_description, context_data, output_format)
        
        sop_result = {
            "sop_id": generate_event_id(),
            "process_description": process_description,
            "output_format": output_format,
            "sop": sop,
            "used_real_llm": sop.get("used_real_llm", False),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ SOP generated")
        
        return {
            "artifacts": {
                "sop": sop_result
            },
            "events": [{
                "type": "sop_generated",
                "event_id": generate_event_id(),
                "sop_id": sop_result["sop_id"],
                "used_real_llm": sop.get("used_real_llm", False)
            }]
        }
    
    async def _generate_via_agent(
        self,
        ctx: PlatformContext,
        process_description: str,
        context_data: Dict[str, Any],
        output_format: str
    ) -> Dict[str, Any]:
        """Generate SOP using real SOPGenerationAgent."""
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "sop_generation_agent",
                    params={
                        "action": "generate",
                        "process_description": process_description,
                        "context": context_data,
                        "output_format": output_format
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    result = agent_result.get("result", {})
                    result["used_real_llm"] = True
                    self.logger.info("✅ Got SOP from real SOPGenerationAgent")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"SOPGenerationAgent invocation failed: {e}")
        
        # Fallback to template
        return self._template_sop(process_description)
    
    def _template_sop(self, process_description: str) -> Dict[str, Any]:
        """Template-based SOP fallback."""
        return {
            "title": f"SOP: {process_description[:50]}...",
            "sections": [
                {"title": "Purpose", "content": "Define the purpose here"},
                {"title": "Scope", "content": "Define the scope here"},
                {"title": "Procedure", "content": "Define procedures here"},
                {"title": "Responsibilities", "content": "Define responsibilities here"}
            ],
            "note": "Template SOP - invoke real agent for AI-generated content",
            "used_real_llm": False
        }
