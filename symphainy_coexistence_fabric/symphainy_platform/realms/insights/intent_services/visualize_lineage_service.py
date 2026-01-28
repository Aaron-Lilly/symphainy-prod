"""
Visualize Lineage Intent Service

Implements the visualize_lineage intent for the Insights Realm.

Contract: docs/intent_contracts/journey_insights_lineage/intent_visualize_lineage.md

Purpose: Visualize complete data lineage from upload to analysis ("Your Data Mash").
Shows the flow of data through the platform and all transformations.

WHAT (Intent Service Role): I visualize data lineage and transformations
HOW (Intent Service Implementation): I build lineage graph from artifacts
    and generate visualization for "Your Data Mash" view

Naming Convention:
- Realm: Insights Realm
- Artifacts: insights_lineage
- Solution = platform construct (InsightsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class VisualizeLineageService(BaseIntentService):
    """
    Intent service for lineage visualization.
    
    Visualizes data lineage ("Your Data Mash"):
    - File upload → Parsing → Embedding → Analysis
    - Shows all transformations and artifacts
    - Enables interactive exploration
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize VisualizeLineageService."""
        super().__init__(
            service_id="visualize_lineage_service",
            intent_type="visualize_lineage",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the visualize_lineage intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            # Can be session-based or artifact-based
            session_id = intent_params.get("session_id") or context.session_id
            artifact_id = intent_params.get("artifact_id")
            
            # Build lineage graph
            lineage_nodes = await self._build_lineage_nodes(session_id, artifact_id, context)
            
            # Build lineage edges
            lineage_edges = await self._build_lineage_edges(lineage_nodes)
            
            # Generate visualization data
            visualization = await self._generate_visualization(lineage_nodes, lineage_edges)
            
            # Build lineage result
            lineage_id = f"lineage_{generate_event_id()}"
            
            lineage = {
                "lineage_id": lineage_id,
                "session_id": session_id,
                "artifact_id": artifact_id,
                "nodes": lineage_nodes,
                "edges": lineage_edges,
                "visualization": visualization,
                "statistics": self._calculate_statistics(lineage_nodes, lineage_edges),
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Lineage visualized: {lineage_id} ({len(lineage_nodes)} nodes)")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "lineage_id": lineage_id, "nodes_count": len(lineage_nodes)
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "lineage": lineage
                },
                "events": [
                    {
                        "type": "lineage_visualized",
                        "lineage_id": lineage_id,
                        "nodes_count": len(lineage_nodes)
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _build_lineage_nodes(
        self,
        session_id: str,
        artifact_id: Optional[str],
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """Build lineage nodes from artifacts."""
        nodes = []
        
        # Get session state for artifacts
        session_state = {}
        if context.state_surface:
            try:
                session_state = await context.state_surface.get_session_state(
                    session_id, context.tenant_id
                ) or {}
            except Exception:
                pass
        
        # Add file upload nodes
        files = session_state.get("uploaded_files", [])
        for i, file_info in enumerate(files if isinstance(files, list) else []):
            nodes.append({
                "node_id": f"file_{i}",
                "node_type": "file",
                "label": file_info.get("name", f"File {i}") if isinstance(file_info, dict) else f"File {i}",
                "stage": "upload",
                "position": {"x": 100, "y": 100 + i * 80}
            })
        
        # Add parsing nodes
        parsed_files = session_state.get("parsed_files", [])
        for i, parsed_info in enumerate(parsed_files if isinstance(parsed_files, list) else []):
            nodes.append({
                "node_id": f"parsed_{i}",
                "node_type": "parsed",
                "label": f"Parsed Content {i}",
                "stage": "parsing",
                "position": {"x": 300, "y": 100 + i * 80}
            })
        
        # Add embedding nodes
        embeddings = session_state.get("embeddings", [])
        for i, emb_info in enumerate(embeddings if isinstance(embeddings, list) else []):
            nodes.append({
                "node_id": f"embedding_{i}",
                "node_type": "embedding",
                "label": f"Embedding {i}",
                "stage": "embedding",
                "position": {"x": 500, "y": 100 + i * 80}
            })
        
        # Add analysis nodes
        analyses = session_state.get("analyses", [])
        for i, analysis_info in enumerate(analyses if isinstance(analyses, list) else []):
            nodes.append({
                "node_id": f"analysis_{i}",
                "node_type": "analysis",
                "label": f"Analysis {i}",
                "stage": "analysis",
                "position": {"x": 700, "y": 100 + i * 80}
            })
        
        # Add placeholder nodes if no data
        if not nodes:
            nodes = [
                {"node_id": "file_0", "node_type": "file", "label": "Upload File", "stage": "upload", "position": {"x": 100, "y": 150}},
                {"node_id": "parsed_0", "node_type": "parsed", "label": "Parse Content", "stage": "parsing", "position": {"x": 300, "y": 150}},
                {"node_id": "embedding_0", "node_type": "embedding", "label": "Create Embeddings", "stage": "embedding", "position": {"x": 500, "y": 150}},
                {"node_id": "analysis_0", "node_type": "analysis", "label": "Generate Insights", "stage": "analysis", "position": {"x": 700, "y": 150}}
            ]
        
        return nodes
    
    async def _build_lineage_edges(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build lineage edges between nodes."""
        edges = []
        
        # Group nodes by stage
        stages = ["upload", "parsing", "embedding", "analysis"]
        nodes_by_stage = {stage: [n for n in nodes if n.get("stage") == stage] for stage in stages}
        
        # Connect sequential stages
        for i, stage in enumerate(stages[:-1]):
            next_stage = stages[i + 1]
            source_nodes = nodes_by_stage.get(stage, [])
            target_nodes = nodes_by_stage.get(next_stage, [])
            
            for source in source_nodes:
                for target in target_nodes:
                    edges.append({
                        "edge_id": f"{source['node_id']}_to_{target['node_id']}",
                        "source": source["node_id"],
                        "target": target["node_id"],
                        "relationship": "transforms_to"
                    })
        
        return edges
    
    async def _generate_visualization(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate visualization configuration."""
        return {
            "type": "data_mash",
            "layout": "horizontal",
            "stages": ["upload", "parsing", "embedding", "analysis"],
            "stage_colors": {
                "upload": "#3498db",
                "parsing": "#2ecc71",
                "embedding": "#9b59b6",
                "analysis": "#e74c3c"
            },
            "node_config": {
                "shape": "roundedRect",
                "width": 150,
                "height": 60
            },
            "edge_config": {
                "type": "bezier",
                "animated": True
            },
            "title": "Your Data Mash",
            "description": "Visualize your data journey from upload to insights"
        }
    
    def _calculate_statistics(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate lineage statistics."""
        stages = {}
        for node in nodes:
            stage = node.get("stage", "unknown")
            stages[stage] = stages.get(stage, 0) + 1
        
        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "nodes_by_stage": stages,
            "pipeline_depth": len(set(n.get("stage") for n in nodes))
        }
