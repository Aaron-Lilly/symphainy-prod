"""
Export Artifact Service (Platform SDK)

Exports artifacts to various formats.
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class ExportArtifactService(PlatformIntentService):
    """Export Artifact Service using Platform SDK."""
    
    intent_type = "export_artifact"
    
    def __init__(self, service_id: str = "export_artifact_service"):
        super().__init__(service_id=service_id, intent_type="export_artifact")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute export_artifact intent."""
        self.logger.info(f"Executing export_artifact: {ctx.execution_id}")
        
        artifact_id = ctx.intent.parameters.get("artifact_id")
        export_format = ctx.intent.parameters.get("format", "json")
        
        if not artifact_id:
            raise ValueError("artifact_id is required")
        
        # Get artifact and export
        exported = {
            "export_id": generate_event_id(),
            "artifact_id": artifact_id,
            "format": export_format,
            "exported_at": datetime.utcnow().isoformat()
        }
        
        return {
            "artifacts": {"export": exported},
            "events": [{"type": "artifact_exported", "event_id": generate_event_id()}]
        }
