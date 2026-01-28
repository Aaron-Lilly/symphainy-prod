"""
Artifact Export Journey Orchestrator

Composes the artifact export journey:
1. Validate artifact_type, artifact_id, and export_format
2. Execute export_artifact intent
3. Store exported file
4. Return download URL

WHAT (Journey Role): I orchestrate artifact export
HOW (Journey Implementation): I compose export_artifact intent

Key Principle: Journey orchestrators compose intent services into journeys.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext


class ArtifactExportJourney:
    """
    Artifact Export Journey Orchestrator.
    
    Journey Flow:
    1. Validate artifact_type, artifact_id, export_format (required)
    2. Execute export_artifact intent
    3. Store exported file
    4. Return download URL
    
    Provides MCP Tools:
    - outcomes_export_artifact: Export artifact in various formats
    """
    
    JOURNEY_ID = "artifact_export"
    JOURNEY_NAME = "Artifact Export"
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """Initialize Artifact Export Journey."""
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        
        self._intent_service = None
        self.telemetry_service = None
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose the artifact export journey.
        
        Args:
            context: Execution context
            journey_params: Journey parameters including:
                - artifact_type: Type of artifact (roadmap, poc, blueprint) (required)
                - artifact_id: Artifact identifier (required)
                - export_format: Export format (json, yaml, docx) (required)
        
        Returns:
            Journey result with download URL
        """
        journey_params = journey_params or {}
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        await self._ensure_telemetry()
        
        journey_execution_id = generate_event_id()
        await self._record_telemetry({
            "action": "journey_started",
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id
        }, context.tenant_id)
        
        try:
            # Validate required parameters
            artifact_type = journey_params.get("artifact_type")
            artifact_id = journey_params.get("artifact_id")
            export_format = journey_params.get("export_format")
            
            if not artifact_type:
                raise ValueError("artifact_type is required")
            if not artifact_id:
                raise ValueError("artifact_id is required")
            if not export_format:
                raise ValueError("export_format is required")
            
            valid_types = ["roadmap", "poc", "blueprint", "synthesis"]
            if artifact_type not in valid_types:
                raise ValueError(f"Invalid artifact_type: {artifact_type}. Must be one of: {valid_types}")
            
            valid_formats = ["json", "yaml", "docx"]
            if export_format not in valid_formats:
                raise ValueError(f"Invalid export_format: {export_format}. Must be one of: {valid_formats}")
            
            # Get intent service
            intent_service = await self._get_intent_service()
            
            # Execute export_artifact intent
            result = await intent_service.execute(context, journey_params)
            
            # Build journey result
            journey_result = self._build_journey_result(
                intent_result=result,
                journey_execution_id=journey_execution_id
            )
            
            await self._record_telemetry({
                "action": "journey_completed",
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "artifact_type": artifact_type,
                "export_format": export_format
            }, context.tenant_id)
            
            return journey_result
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            
            await self._record_telemetry({
                "action": "journey_failed",
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "error": str(e)
            }, context.tenant_id)
            
            return {
                "success": False,
                "error": str(e),
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "artifacts": {},
                "events": [{"type": "journey_failed", "journey_id": self.journey_id, "error": str(e)}]
            }
    
    async def _get_intent_service(self):
        """Get or create the intent service."""
        if not self._intent_service:
            from symphainy_platform.realms.outcomes.intent_services import (
                ExportArtifactService
            )
            self._intent_service = ExportArtifactService(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        return self._intent_service
    
    def _build_journey_result(
        self,
        intent_result: Dict[str, Any],
        journey_execution_id: str
    ) -> Dict[str, Any]:
        """Build journey result from intent result."""
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": intent_result.get("artifacts", {}),
            "events": [
                {"type": "journey_completed", "journey_id": self.journey_id, "journey_execution_id": journey_execution_id},
                *intent_result.get("events", [])
            ]
        }
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA APIs provided by this journey."""
        return {
            "export_artifact": {
                "handler": self._soa_export_artifact,
                "description": "Export artifact in various formats",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "artifact_type": {
                            "type": "string",
                            "enum": ["roadmap", "poc", "blueprint", "synthesis"],
                            "description": "Type of artifact"
                        },
                        "artifact_id": {
                            "type": "string",
                            "description": "Artifact identifier"
                        },
                        "export_format": {
                            "type": "string",
                            "enum": ["json", "yaml", "docx"],
                            "description": "Export format"
                        },
                        "tenant_id": {"type": "string", "description": "Tenant identifier"},
                        "session_id": {"type": "string", "description": "Session identifier"}
                    },
                    "required": ["artifact_type", "artifact_id", "export_format", "tenant_id", "session_id"]
                }
            }
        }
    
    async def _soa_export_artifact(
        self,
        artifact_type: str,
        artifact_id: str,
        export_format: str,
        tenant_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """SOA API: Export artifact."""
        execution_id = generate_event_id()
        
        context = ExecutionContext(
            execution_id=execution_id,
            tenant_id=tenant_id,
            session_id=session_id,
            intent=None,
            state_surface=self.state_surface
        )
        
        journey_params = {
            "artifact_type": artifact_type,
            "artifact_id": artifact_id,
            "export_format": export_format
        }
        
        return await self.compose_journey(context, journey_params)
    
    async def _ensure_telemetry(self):
        if not self.telemetry_service and self.public_works:
            try:
                self.telemetry_service = self.public_works.get_telemetry_service()
            except Exception:
                pass
    
    async def _record_telemetry(self, telemetry_data: Dict[str, Any], tenant_id: str):
        if self.telemetry_service:
            try:
                await self.telemetry_service.record({"journey_id": self.journey_id, "tenant_id": tenant_id, **telemetry_data})
            except Exception:
                pass
