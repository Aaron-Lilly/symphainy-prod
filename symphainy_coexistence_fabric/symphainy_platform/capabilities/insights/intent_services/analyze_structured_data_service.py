"""
Analyze Structured Data Service (Platform SDK)

AI-powered analysis of structured data using InsightsEDAAgent.

Uses ctx.reasoning.agents.invoke() for REAL statistical analysis,
pattern detection, and anomaly identification - NOT just field counting.

Contract: docs/intent_contracts/journey_insights_analysis/intent_analyze_structured_data.md
"""

from typing import Dict, Any, List
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class AnalyzeStructuredDataService(PlatformIntentService):
    """
    Analyze Structured Data Service using Platform SDK.
    
    Uses REAL InsightsEDAAgent via ctx.reasoning.agents.invoke() for:
    - Statistical summaries with AI-powered insights
    - Intelligent pattern detection
    - Anomaly identification with explanations
    
    NO MORE FIELD COUNTING - This uses actual LLM reasoning.
    """
    
    def __init__(self, service_id: str = "analyze_structured_data_service"):
        """Initialize Analyze Structured Data Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute analyze_structured_data intent."""
        self.logger.info(f"Executing analyze_structured_data: {ctx.execution_id}")
        
        parsed_file_id = ctx.intent.parameters.get("parsed_file_id")
        analysis_type = ctx.intent.parameters.get("analysis_type", "comprehensive")
        include_patterns = ctx.intent.parameters.get("include_patterns", True)
        include_anomalies = ctx.intent.parameters.get("include_anomalies", True)
        
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
        
        # Perform AI-powered analysis via InsightsEDAAgent
        analysis = await self._analyze_via_agent(
            ctx, parsed_content, analysis_type, include_patterns, include_anomalies
        )
        
        analysis_result = {
            "analysis_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "analysis_type": analysis_type,
            "analysis": analysis,
            "used_real_llm": analysis.get("used_real_llm", False),
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Structured data analysis complete (AI: {analysis.get('used_real_llm', False)})")
        
        return {
            "artifacts": {
                "analysis": analysis_result
            },
            "events": [{
                "type": "structured_data_analyzed",
                "event_id": generate_event_id(),
                "analysis_type": analysis_type,
                "used_real_llm": analysis.get("used_real_llm", False)
            }]
        }
    
    async def _analyze_via_agent(
        self,
        ctx: PlatformContext,
        parsed_content: Dict[str, Any],
        analysis_type: str,
        include_patterns: bool,
        include_anomalies: bool
    ) -> Dict[str, Any]:
        """
        Analyze structured data using real InsightsEDAAgent.
        
        This provides intelligent analysis, not just field counting.
        """
        content = parsed_content.get("content", {})
        structure = parsed_content.get("structure", {})
        
        # Try to invoke real InsightsEDAAgent for AI-powered analysis
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "insights_eda_agent",
                    params={
                        "action": "analyze_structured",
                        "content": content,
                        "structure": structure,
                        "analysis_type": analysis_type,
                        "include_patterns": include_patterns,
                        "include_anomalies": include_anomalies,
                        "analysis_goals": [
                            "statistical_summary",
                            "pattern_detection", 
                            "anomaly_identification",
                            "data_quality_insights",
                            "business_recommendations"
                        ]
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    result = agent_result.get("result", {})
                    result["used_real_llm"] = True
                    self.logger.info("✅ Got analysis from real InsightsEDAAgent")
                    return result
                    
            except Exception as e:
                self.logger.warning(f"InsightsEDAAgent invocation failed: {e}")
        
        # Fallback to basic structural analysis (still better than nothing)
        self.logger.warning("Falling back to basic structural analysis")
        return self._basic_structural_analysis(parsed_content, include_patterns, include_anomalies)
    
    def _basic_structural_analysis(
        self,
        parsed_content: Dict[str, Any],
        include_patterns: bool,
        include_anomalies: bool
    ) -> Dict[str, Any]:
        """
        Basic structural analysis fallback when agent unavailable.
        
        Still provides useful metadata even without AI.
        """
        content = parsed_content.get("content", {})
        structure = parsed_content.get("structure", {})
        
        # Calculate structural statistics
        field_count = len(structure) if isinstance(structure, dict) else 0
        record_count = len(content) if isinstance(content, list) else 1
        
        # Analyze data types
        data_types = {}
        if isinstance(structure, dict):
            for field, info in structure.items():
                field_type = info.get("type", "unknown") if isinstance(info, dict) else "field"
                data_types[field_type] = data_types.get(field_type, 0) + 1
        
        # Basic pattern detection (heuristic)
        patterns = []
        if include_patterns and isinstance(content, list) and len(content) > 1:
            patterns.append({
                "pattern_type": "tabular_data",
                "description": f"Data appears to be tabular with {record_count} records",
                "confidence": 0.7,
                "source": "heuristic"
            })
        
        # Basic anomaly detection (heuristic - check for nulls, empty values)
        anomalies = []
        if include_anomalies:
            null_fields = self._count_null_fields(content)
            if null_fields > 0:
                anomalies.append({
                    "anomaly_type": "missing_data",
                    "description": f"Found {null_fields} fields with null/empty values",
                    "severity": "medium" if null_fields < 5 else "high",
                    "source": "heuristic"
                })
        
        return {
            "statistics": {
                "field_count": field_count,
                "record_count": record_count,
                "data_types": data_types
            },
            "patterns": patterns,
            "anomalies": anomalies,
            "insights": [
                "Full AI-powered analysis requires agent configuration",
                "Structural analysis completed - invoke with agent for deeper insights"
            ],
            "summary": f"Analyzed {record_count} records with {field_count} fields (basic analysis)",
            "used_real_llm": False,
            "fallback_reason": "AI agent unavailable"
        }
    
    def _count_null_fields(self, content: Any) -> int:
        """Count null/empty fields in content."""
        null_count = 0
        
        if isinstance(content, dict):
            for value in content.values():
                if value is None or value == "" or value == []:
                    null_count += 1
        elif isinstance(content, list) and content:
            # Sample first record
            sample = content[0] if isinstance(content[0], dict) else {}
            for value in sample.values():
                if value is None or value == "" or value == []:
                    null_count += 1
        
        return null_count
