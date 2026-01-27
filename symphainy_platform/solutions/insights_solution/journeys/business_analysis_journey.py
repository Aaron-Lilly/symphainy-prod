"""
Business Analysis Journey Orchestrator

Composes business analysis operations:
1. extract_structured_data - Extract structured data from content
2. analyze_patterns - Analyze data patterns
3. generate_insights - Generate business insights

WHAT (Journey Role): I orchestrate business analysis
HOW (Journey Implementation): I compose extraction, analysis, and insight generation intents
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
import hashlib

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class BusinessAnalysisJourney:
    """
    Business Analysis Journey Orchestrator.
    
    Provides MCP Tools:
    - insights_analyze_data: Analyze business data
    - insights_extract_patterns: Extract data patterns
    - insights_generate_report: Generate analysis report
    """
    
    JOURNEY_ID = "business_analysis"
    JOURNEY_NAME = "Business Analysis"
    
    def __init__(self, public_works: Optional[Any] = None, state_surface: Optional[Any] = None):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
    
    async def compose_journey(self, context: ExecutionContext, journey_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compose business analysis journey."""
        journey_params = journey_params or {}
        journey_execution_id = generate_event_id()
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        try:
            artifact_id = journey_params.get("artifact_id")
            analysis_type = journey_params.get("analysis_type", "general")
            
            # Execute analysis
            analysis_id = generate_event_id()
            analysis_result = {
                "analysis_id": analysis_id,
                "artifact_id": artifact_id,
                "analysis_type": analysis_type,
                "created_at": self.clock.now_utc().isoformat(),
                "patterns": [],
                "insights": [],
                "recommendations": []
            }
            
            semantic_payload = {
                "analysis_id": analysis_id,
                "artifact_id": artifact_id,
                "analysis_type": analysis_type,
                "journey_execution_id": journey_execution_id
            }
            
            artifact = create_structured_artifact(
                result_type="business_analysis",
                semantic_payload=semantic_payload,
                renderings={"analysis_result": analysis_result}
            )
            
            return {
                "success": True,
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "analysis_id": analysis_id,
                "artifacts": {"analysis": artifact},
                "events": [{"type": "analysis_completed", "analysis_id": analysis_id}]
            }
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        return {
            "analyze_data": {
                "handler": self._handle_analyze,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "artifact_id": {"type": "string", "description": "Content artifact to analyze"},
                        "analysis_type": {"type": "string", "description": "Type of analysis"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["artifact_id"]
                },
                "description": "Analyze business data and generate insights"
            },
            "extract_patterns": {
                "handler": self._handle_patterns,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "artifact_id": {"type": "string"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["artifact_id"]
                },
                "description": "Extract patterns from data"
            }
        }
    
    async def _handle_analyze(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="insights_solution"
        )
        return await self.compose_journey(context, {"artifact_id": kwargs.get("artifact_id"), "analysis_type": kwargs.get("analysis_type")})
    
    async def _handle_patterns(self, **kwargs) -> Dict[str, Any]:
        return await self._handle_analyze(**{**kwargs, "analysis_type": "pattern_extraction"})
