"""
Visualize Lineage Service (Platform SDK)

AI-enhanced data lineage visualizations.

Uses artifact metadata for actual provenance tracking, with optional
AI-powered insights about data flow patterns.

Contract: docs/intent_contracts/journey_insights_lineage/intent_visualize_lineage.md
"""

from typing import Dict, Any, List, Optional
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
    - Source → Transform → Destination paths (from actual provenance)
    - Data flow diagrams with relationship types
    - Dependency graphs
    - AI-powered lineage insights (optional)
    """
    
    intent_type = "visualize_lineage"
    
    def __init__(self, service_id: str = "visualize_lineage_service"):
        """Initialize Visualize Lineage Service."""
        super().__init__(service_id=service_id, intent_type="visualize_lineage")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute visualize_lineage intent."""
        self.logger.info(f"Executing visualize_lineage: {ctx.execution_id}")
        
        artifact_ids = ctx.intent.parameters.get("artifact_ids", [])
        visualization_type = ctx.intent.parameters.get("visualization_type", "flow")
        include_insights = ctx.intent.parameters.get("include_insights", True)
        
        if not artifact_ids:
            # Get all artifacts for session
            artifact_ids = await self._get_session_artifacts(ctx)
        
        # Get artifact metadata to build actual lineage
        artifacts_metadata = await self._get_artifacts_metadata(ctx, artifact_ids)
        
        # Build lineage graph from actual provenance
        lineage = self._build_lineage_graph(artifact_ids, artifacts_metadata, visualization_type)
        
        # Optionally add AI-powered insights
        insights = None
        if include_insights and lineage.get("nodes"):
            insights = await self._generate_lineage_insights(ctx, lineage, artifacts_metadata)
        
        lineage_result = {
            "lineage_id": generate_event_id(),
            "artifact_ids": artifact_ids,
            "visualization_type": visualization_type,
            "lineage": lineage,
            "insights": insights,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Lineage visualization generated ({len(lineage.get('nodes', []))} nodes)")
        
        return {
            "artifacts": {
                "lineage": lineage_result
            },
            "events": [{
                "type": "lineage_visualized",
                "event_id": generate_event_id(),
                "artifact_count": len(artifact_ids),
                "has_insights": insights is not None
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
    
    async def _get_artifacts_metadata(
        self,
        ctx: PlatformContext,
        artifact_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all artifacts including provenance info."""
        metadata = {}
        
        if ctx.platform and ctx.platform.registry:
            for artifact_id in artifact_ids:
                try:
                    file_meta = await ctx.platform.registry.get_file(
                        file_id=artifact_id,
                        tenant_id=ctx.tenant_id
                    )
                    if file_meta:
                        metadata[artifact_id] = file_meta
                except Exception as e:
                    self.logger.debug(f"Could not get metadata for {artifact_id}: {e}")
        
        return metadata
    
    def _build_lineage_graph(
        self,
        artifact_ids: List[str],
        artifacts_metadata: Dict[str, Dict[str, Any]],
        viz_type: str
    ) -> Dict[str, Any]:
        """Build lineage graph from artifact metadata."""
        nodes = []
        edges = []
        seen_edges = set()
        
        # Create nodes for each artifact with rich metadata
        for i, artifact_id in enumerate(artifact_ids):
            meta = artifacts_metadata.get(artifact_id, {})
            
            node = {
                "id": artifact_id,
                "label": meta.get("file_name", f"Artifact {i + 1}"),
                "type": meta.get("file_type", "unknown"),
                "created_at": meta.get("created_at"),
                "artifact_type": meta.get("artifact_type", "file")
            }
            nodes.append(node)
            
            # Check for derived_from relationships in metadata
            derived_from = meta.get("derived_from") or meta.get("source_artifact_id")
            if derived_from and derived_from in artifact_ids:
                edge_key = f"{derived_from}->{artifact_id}"
                if edge_key not in seen_edges:
                    edges.append({
                        "source": derived_from,
                        "target": artifact_id,
                        "type": "derived_from",
                        "relationship": "transforms"
                    })
                    seen_edges.add(edge_key)
            
            # Check for parent_file relationships
            parent_file = meta.get("parent_file_id")
            if parent_file and parent_file in artifact_ids:
                edge_key = f"{parent_file}->{artifact_id}"
                if edge_key not in seen_edges:
                    edges.append({
                        "source": parent_file,
                        "target": artifact_id,
                        "type": "parent",
                        "relationship": "contains"
                    })
                    seen_edges.add(edge_key)
        
        # If no edges found from metadata, create sequential flow based on creation time
        if not edges and len(nodes) > 1:
            # Sort by creation time if available
            sorted_artifacts = sorted(
                artifact_ids,
                key=lambda x: artifacts_metadata.get(x, {}).get("created_at", "")
            )
            for i in range(len(sorted_artifacts) - 1):
                edges.append({
                    "source": sorted_artifacts[i],
                    "target": sorted_artifacts[i + 1],
                    "type": "sequential",
                    "relationship": "followed_by"
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "layout": viz_type,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "has_provenance": any(e.get("type") == "derived_from" for e in edges)
            }
        }
    
    async def _generate_lineage_insights(
        self,
        ctx: PlatformContext,
        lineage: Dict[str, Any],
        artifacts_metadata: Dict[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Generate AI-powered insights about the lineage."""
        if not ctx.reasoning or not ctx.reasoning.agents:
            return None
        
        try:
            # Use InsightsEDAAgent to analyze the lineage
            agent_result = await ctx.reasoning.agents.invoke(
                "insights_eda_agent",
                params={
                    "action": "analyze_lineage",
                    "lineage_graph": lineage,
                    "artifacts_summary": [
                        {
                            "id": k,
                            "type": v.get("file_type"),
                            "name": v.get("file_name")
                        }
                        for k, v in list(artifacts_metadata.items())[:10]
                    ]
                },
                context={
                    "tenant_id": ctx.tenant_id,
                    "session_id": ctx.session_id
                }
            )
            
            if agent_result.get("status") == "completed":
                result = agent_result.get("result", {})
                result["source"] = "ai"
                return result
                
        except Exception as e:
            self.logger.warning(f"AI lineage insights failed: {e}")
        
        # Fallback insights
        nodes = lineage.get("nodes", [])
        edges = lineage.get("edges", [])
        
        return {
            "summary": f"Lineage shows {len(nodes)} artifacts with {len(edges)} connections",
            "patterns": self._detect_patterns(lineage),
            "recommendations": [
                "Review source artifacts for data quality" if len(nodes) > 3 else "Lineage is straightforward"
            ],
            "source": "heuristic"
        }
    
    def _detect_patterns(self, lineage: Dict[str, Any]) -> List[str]:
        """Detect simple patterns in lineage graph."""
        patterns = []
        nodes = lineage.get("nodes", [])
        edges = lineage.get("edges", [])
        
        if len(nodes) == 1:
            patterns.append("single_source")
        elif len(edges) == len(nodes) - 1:
            patterns.append("linear_flow")
        elif len(edges) > len(nodes):
            patterns.append("complex_transforms")
        
        # Check for transformation types
        edge_types = set(e.get("type") for e in edges)
        if "derived_from" in edge_types:
            patterns.append("has_derivations")
        
        return patterns
