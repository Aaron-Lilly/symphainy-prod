"""
Generate Visual Intent Service

Implements the generate_visual intent for the Outcomes Realm.

Contract: docs/intent_contracts/journey_outcomes_synthesis/intent_generate_visual.md

Purpose: Generate visualizations for platform outputs including dashboards, roadmaps,
POCs, workflows, and SOPs.

WHAT (Intent Service Role): I generate visualizations for platform outputs
HOW (Intent Service Implementation): I use VisualGenerationService libraries
    from foundations to create various visualization types

Naming Convention:
- Realm: Outcomes Realm
- Artifacts: outcomes_visualization
- Solution = platform construct (OutcomesSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.foundations.libraries.visualization.outcome_visual_service import (
    VisualGenerationService as OutcomeVisualService
)
from symphainy_platform.foundations.libraries.visualization.workflow_visual_service import (
    VisualGenerationService as WorkflowVisualService
)
from utilities import generate_event_id


class GenerateVisualService(BaseIntentService):
    """
    Intent service for visualization generation.
    
    Generates visualizations for:
    - Summary dashboards (pillar outputs)
    - Roadmap visualizations
    - POC visualizations
    - Workflow visualizations
    - SOP visualizations
    
    Uses VisualGenerationService libraries for rendering capabilities.
    """
    
    # Supported visualization types
    VISUAL_TYPES = {
        "summary_dashboard",
        "roadmap",
        "poc",
        "workflow",
        "sop",
        "lineage"
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize GenerateVisualService."""
        super().__init__(
            service_id="generate_visual_service",
            intent_type="generate_visual",
            public_works=public_works,
            state_surface=state_surface
        )
        
        # Initialize visualization libraries
        self._outcome_visual_service = OutcomeVisualService(public_works=public_works)
        self._workflow_visual_service = WorkflowVisualService(public_works=public_works)
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the generate_visual intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            # Validate required parameters
            visual_type = intent_params.get("visual_type")
            if not visual_type:
                raise ValueError("visual_type is required (one of: summary_dashboard, roadmap, poc, workflow, sop)")
            
            if visual_type not in self.VISUAL_TYPES:
                raise ValueError(f"Unknown visual_type: {visual_type}. Supported: {self.VISUAL_TYPES}")
            
            data = intent_params.get("data", {})
            
            # Route to appropriate visualization method
            visual_result = await self._generate_visual(
                visual_type=visual_type,
                data=data,
                context=context
            )
            
            visual_id = f"visual_{generate_event_id()}"
            
            # Build result artifact
            visual_artifact = {
                "visual_id": visual_id,
                "visual_type": visual_type,
                "success": visual_result.get("success", False),
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path"),
                "metadata": visual_result.get("metadata", {}),
                "error": visual_result.get("error"),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Artifact Plane if successful
            artifact_id = None
            if visual_artifact["success"]:
                artifact_id = await self._store_visual(visual_artifact, context)
            
            self.logger.info(f"Visual generation completed: {visual_id}, type={visual_type}, success={visual_artifact['success']}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "visual_id": visual_id,
                    "visual_type": visual_type,
                    "success": visual_artifact["success"]
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "visual": visual_artifact,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "visual_generated",
                        "visual_id": visual_id,
                        "visual_type": visual_type,
                        "success": visual_artifact["success"]
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _generate_visual(
        self,
        visual_type: str,
        data: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Route to appropriate visualization generator."""
        
        if visual_type == "summary_dashboard":
            return await self._outcome_visual_service.generate_summary_visual(
                pillar_outputs=data,
                tenant_id=context.tenant_id,
                context=context
            )
        
        elif visual_type == "roadmap":
            return await self._outcome_visual_service.generate_roadmap_visual(
                roadmap_data=data,
                tenant_id=context.tenant_id,
                context=context
            )
        
        elif visual_type == "poc":
            return await self._outcome_visual_service.generate_poc_visual(
                poc_data=data,
                tenant_id=context.tenant_id,
                context=context
            )
        
        elif visual_type == "workflow":
            semantic_signals = data.get("semantic_signals")
            workflow_data = {k: v for k, v in data.items() if k != "semantic_signals"}
            return await self._workflow_visual_service.generate_workflow_visual(
                workflow_data=workflow_data,
                tenant_id=context.tenant_id,
                context=context,
                semantic_signals=semantic_signals
            )
        
        elif visual_type == "sop":
            return await self._workflow_visual_service.generate_sop_visual(
                sop_data=data,
                tenant_id=context.tenant_id,
                context=context
            )
        
        else:
            return {
                "success": False,
                "error": f"Unknown visual type: {visual_type}"
            }
    
    async def generate_summary_dashboard(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate summary dashboard visualization.
        
        Convenience method for summary_dashboard visual type.
        """
        intent_params = params or {}
        intent_params["visual_type"] = "summary_dashboard"
        return await self.execute(context, intent_params)
    
    async def generate_roadmap_visual(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate roadmap visualization.
        
        Convenience method for roadmap visual type.
        """
        intent_params = params or {}
        intent_params["visual_type"] = "roadmap"
        return await self.execute(context, intent_params)
    
    async def generate_workflow_visual(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate workflow visualization.
        
        Convenience method for workflow visual type.
        """
        intent_params = params or {}
        intent_params["visual_type"] = "workflow"
        return await self.execute(context, intent_params)
    
    async def _store_visual(
        self,
        visual: Dict[str, Any],
        context: ExecutionContext
    ) -> Optional[str]:
        """Store visualization in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    # Don't include the full image_base64 in stored metadata to save space
                    stored_visual = {k: v for k, v in visual.items() if k != "image_base64"}
                    stored_visual["has_image"] = bool(visual.get("image_base64"))
                    
                    result = await artifact_plane.create_artifact(
                        artifact_type="visualization",
                        content=stored_visual,
                        metadata={
                            "visual_id": visual.get("visual_id"),
                            "visual_type": visual.get("visual_type")
                        },
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store visual: {e}")
        return None
