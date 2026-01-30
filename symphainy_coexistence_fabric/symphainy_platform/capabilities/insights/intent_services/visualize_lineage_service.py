"""
Visualize Lineage Service (Platform SDK)

Generates data lineage visualizations.

Contract: docs/intent_contracts/journey_insights_lineage/intent_visualize_lineage.md
"""

from typing import Dict, Any, List
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class VisualizeLineageService(PlatformIntentService):
    """
    Visualize Lineage Service using Platform SDK.
    
    Generates "Your Data Mash" lineage visualizations:
    - Source → Transform → Destination paths
    - Data flow diagrams
    - Dependency graphs
    """
    
    def __init__(self, service_id: str = "visualize_lineage_service"):
        """Initialize Visualize Lineage Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute visualize_lineage intent."""
        self.logger.info(f"Executing visualize_lineage: {ctx.execution_id}")
        
        artifact_ids = ctx.intent.parameters.get("artifact_ids", [])
        visualization_type = ctx.intent.parameters.get("visualization_type", "flow")
        
        if not artifact_ids:
            # Get all artifacts for session
            artifact_ids = await self._get_session_artifacts(ctx)
        
        # Build lineage graph
        lineage = self._build_lineage_graph(artifact_ids, visualization_type)
        
        lineage_result = {
            "lineage_id": generate_event_id(),
            "artifact_ids": artifact_ids,
            "visualization_type": visualization_type,
            "lineage": lineage,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Lineage visualization generated")
        
        return {
            "artifacts": {
                "lineage": lineage_result
            },
            "events": [{
                "type": "lineage_visualized",
                "event_id": generate_event_id(),
                "artifact_count": len(artifact_ids)
            }]
        }
    
    async def _get_session_artifacts(self, ctx: PlatformContext) -> List[str]:
        """Get all artifacts for current session."""
        if ctx.platform and ctx.platform.registry:
            try:
                files = await ctx.platform.registry.list_files(
                    tenant_id=ctx.tenant_id,
                    session_id=ctx.session_id,
                    limit=100
                )
                return [f.get("uuid") or f.get("file_id") for f in (files or [])]
            except Exception as e:
                self.logger.warning(f"Could not get session artifacts: {e}")
        return []
    
    def _build_lineage_graph(self, artifact_ids: List[str], viz_type: str) -> Dict[str, Any]:
        """Build lineage graph from artifacts."""
        nodes = []
        edges = []
        
        # Create nodes for each artifact
        for i, artifact_id in enumerate(artifact_ids):
            nodes.append({
                "id": artifact_id,
                "label": f"Artifact {i + 1}",
                "type": "artifact"
            })
        
        # Create flow edges (simplified)
        for i in range(len(artifact_ids) - 1):
            edges.append({
                "source": artifact_ids[i],
                "target": artifact_ids[i + 1],
                "type": "derived_from"
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "layout": viz_type,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }
