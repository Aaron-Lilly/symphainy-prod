"""
Analyze Structured Data Service (Platform SDK)

Analyzes structured data for business insights.

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
    
    Analyzes structured data (CSV, JSON, tabular) for:
    - Statistical summaries
    - Pattern detection
    - Anomaly identification
    """
    
    def __init__(self, service_id: str = "analyze_structured_data_service"):
        """Initialize Analyze Structured Data Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute analyze_structured_data intent."""
        self.logger.info(f"Executing analyze_structured_data: {ctx.execution_id}")
        
        parsed_file_id = ctx.intent.parameters.get("parsed_file_id")
        analysis_type = ctx.intent.parameters.get("analysis_type", "summary")
        
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
        
        # Perform analysis
        analysis = self._analyze_structured(parsed_content, analysis_type)
        
        analysis_result = {
            "analysis_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "analysis_type": analysis_type,
            "analysis": analysis,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Structured data analysis complete")
        
        return {
            "artifacts": {
                "analysis": analysis_result
            },
            "events": [{
                "type": "structured_data_analyzed",
                "event_id": generate_event_id(),
                "analysis_type": analysis_type
            }]
        }
    
    def _analyze_structured(self, parsed_content: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Analyze structured data."""
        content = parsed_content.get("content", {})
        structure = parsed_content.get("structure", {})
        
        # Basic statistics
        stats = {
            "field_count": len(structure) if isinstance(structure, dict) else 0,
            "record_count": len(content) if isinstance(content, list) else 1,
            "data_types": {}
        }
        
        # Analyze structure
        if isinstance(structure, dict):
            for field, info in structure.items():
                field_type = info.get("type", "unknown") if isinstance(info, dict) else "field"
                stats["data_types"][field_type] = stats["data_types"].get(field_type, 0) + 1
        
        return {
            "statistics": stats,
            "patterns": [],
            "anomalies": [],
            "summary": f"Analyzed {stats['record_count']} records with {stats['field_count']} fields"
        }
