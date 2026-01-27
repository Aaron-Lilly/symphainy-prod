"""
Lineage Visualization Service - Insights Realm

Enabling service for visualizing the complete data lineage pipeline.

WHAT (Enabling Service Role): I visualize the complete data lineage pipeline
HOW (Enabling Service Implementation): I query lineage tables and generate visual graph

This is the reimagined "Virtual Data Mapper" - it visualizes how data flows through
the system without requiring data ingestion, showing the complete pipeline from
file → parsed → embedding → interpretation → analysis.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext


class LineageVisualizationService:
    """
    Lineage Visualization Service for Insights Realm.
    
    Visualizes the complete data lineage pipeline by querying Supabase lineage tables
    and generating a visual graph showing the flow from file to final analysis.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Lineage Visualization Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Get adapters from Public Works
        self.supabase_adapter = None
        self.arango_adapter = None
        self.visual_abstraction = None
        
        if public_works:
            self.supabase_adapter = public_works.get_supabase_adapter()
            self.arango_adapter = public_works.get_arango_adapter()
            self.visual_abstraction = public_works.get_visual_generation_abstraction()
    
    async def visualize_lineage(
        self,
        file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Visualize complete lineage pipeline for a file.
        
        Args:
            file_id: File ID to visualize lineage for
            tenant_id: Tenant ID
            context: Execution context
            
        Returns:
            Dict with lineage visualization result
        """
        if not self.supabase_adapter:
            raise RuntimeError("Supabase adapter not available")
        if not self.visual_abstraction:
            raise RuntimeError("Visual generation abstraction not available")
        
        try:
            self.logger.info(f"Visualizing lineage for file {file_id}")
            
            # Build lineage graph by querying Supabase tables
            lineage_graph = await self._build_lineage_graph(file_id, tenant_id)
            
            # Generate visual graph
            visual_result = await self.visual_abstraction.create_lineage_graph(
                lineage_data=lineage_graph,
                tenant_id=tenant_id
            )
            
            if visual_result.success:
                return {
                    "success": True,
                    "visualization_type": "lineage_graph",
                    "image_base64": visual_result.image_base64,
                    "storage_path": visual_result.metadata.get("storage_path"),
                    "lineage_graph": lineage_graph,
                    "metadata": visual_result.metadata
                }
            else:
                return {
                    "success": False,
                    "error": visual_result.error
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to visualize lineage: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _build_lineage_graph(
        self,
        file_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Build lineage graph by querying Supabase lineage tables.
        
        Returns:
            Dict with nodes and edges for lineage graph
        """
        nodes = []
        edges = []
        
        # Node: File (source)
        nodes.append({
            "id": f"file_{file_id}",
            "label": "Source File",
            "type": "file",
            "file_id": file_id
        })
        
        # Query parsed_results table
        parsed_results = await self._query_parsed_results(file_id, tenant_id)
        
        for parsed_result in parsed_results:
            parsed_result_id = parsed_result.get("parsed_result_id")
            nodes.append({
                "id": f"parsed_{parsed_result_id}",
                "label": f"Parsed Result\n({parsed_result.get('parser_type', 'unknown')})",
                "type": "parsed_result",
                "parsed_result_id": parsed_result_id,
                "record_count": parsed_result.get("record_count", 0)
            })
            
            # Edge: File → Parsed Result
            edges.append({
                "source": f"file_{file_id}",
                "target": f"parsed_{parsed_result_id}",
                "type": "parsed_from"
            })
            
            # Query embeddings table
            embeddings = await self._query_embeddings(parsed_result.get("id"), tenant_id)
            
            for embedding in embeddings:
                embedding_id = embedding.get("embedding_id")
                nodes.append({
                    "id": f"embedding_{embedding_id}",
                    "label": f"Embedding\n({embedding.get('embedding_count', 0)} vectors)",
                    "type": "embedding",
                    "embedding_id": embedding_id,
                    "model_name": embedding.get("model_name")
                })
                
                # Edge: Parsed Result → Embedding
                edges.append({
                    "source": f"parsed_{parsed_result_id}",
                    "target": f"embedding_{embedding_id}",
                    "type": "embedded_from"
                })
                
                # Query interpretations table
                interpretations = await self._query_interpretations(embedding.get("id"), tenant_id)
                
                for interpretation in interpretations:
                    interpretation_id = interpretation.get("id")
                    interpretation_type = interpretation.get("interpretation_type", "unknown")
                    guide_id = interpretation.get("guide_id")
                    
                    nodes.append({
                        "id": f"interpretation_{interpretation_id}",
                        "label": f"Interpretation\n({interpretation_type})",
                        "type": "interpretation",
                        "interpretation_id": interpretation_id,
                        "interpretation_type": interpretation_type,
                        "confidence_score": interpretation.get("confidence_score")
                    })
                    
                    # Edge: Embedding → Interpretation
                    edges.append({
                        "source": f"embedding_{embedding_id}",
                        "target": f"interpretation_{interpretation_id}",
                        "type": "interpreted_from"
                    })
                    
                    # Edge: Guide → Interpretation (if guide used)
                    if guide_id:
                        guide_node_id = f"guide_{guide_id}"
                        # Check if guide node already exists
                        if not any(n["id"] == guide_node_id for n in nodes):
                            nodes.append({
                                "id": guide_node_id,
                                "label": f"Guide\n({guide_id})",
                                "type": "guide",
                                "guide_id": guide_id
                            })
                        
                        edges.append({
                            "source": guide_node_id,
                            "target": f"interpretation_{interpretation_id}",
                            "type": "guided_by"
                        })
                    
                    # Query analyses table
                    analyses = await self._query_analyses(interpretation_id, tenant_id)
                    
                    for analysis in analyses:
                        analysis_id = analysis.get("id")
                        analysis_type = analysis.get("analysis_type", "unknown")
                        agent_session_id = analysis.get("agent_session_id")
                        
                        nodes.append({
                            "id": f"analysis_{analysis_id}",
                            "label": f"Analysis\n({analysis_type})",
                            "type": "analysis",
                            "analysis_id": analysis_id,
                            "analysis_type": analysis_type,
                            "deep_dive": analysis.get("deep_dive", False)
                        })
                        
                        # Edge: Interpretation → Analysis
                        edges.append({
                            "source": f"interpretation_{interpretation_id}",
                            "target": f"analysis_{analysis_id}",
                            "type": "analyzed_from"
                        })
                        
                        # Edge: Agent Session → Analysis (if deep dive)
                        if agent_session_id:
                            agent_node_id = f"agent_{agent_session_id}"
                            # Check if agent node already exists
                            if not any(n["id"] == agent_node_id for n in nodes):
                                nodes.append({
                                    "id": agent_node_id,
                                    "label": f"Agent Session\n({agent_session_id[:8]}...)",
                                    "type": "agent_session",
                                    "agent_session_id": agent_session_id
                                })
                            
                            edges.append({
                                "source": agent_node_id,
                                "target": f"analysis_{analysis_id}",
                                "type": "deep_dive_by"
                            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "file_id": file_id,
            "tenant_id": tenant_id
        }
    
    async def _query_parsed_results(
        self,
        file_id: str,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Query parsed_results table."""
        try:
            result = await self.supabase_adapter.query(
                table="parsed_results",
                filters={
                    "file_id": file_id,
                    "tenant_id": tenant_id
                }
            )
            return result if result else []
        except Exception as e:
            self.logger.warning(f"Failed to query parsed_results: {e}")
            return []
    
    async def _query_embeddings(
        self,
        parsed_result_id: str,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Query embeddings table."""
        try:
            result = await self.supabase_adapter.query(
                table="embeddings",
                filters={
                    "parsed_result_id": parsed_result_id,
                    "tenant_id": tenant_id
                }
            )
            return result if result else []
        except Exception as e:
            self.logger.warning(f"Failed to query embeddings: {e}")
            return []
    
    async def _query_interpretations(
        self,
        embedding_id: str,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Query interpretations table."""
        try:
            result = await self.supabase_adapter.query(
                table="interpretations",
                filters={
                    "embedding_id": embedding_id,
                    "tenant_id": tenant_id
                }
            )
            return result if result else []
        except Exception as e:
            self.logger.warning(f"Failed to query interpretations: {e}")
            return []
    
    async def _query_analyses(
        self,
        interpretation_id: str,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Query analyses table."""
        try:
            result = await self.supabase_adapter.query(
                table="analyses",
                filters={
                    "interpretation_id": interpretation_id,
                    "tenant_id": tenant_id
                }
            )
            return result if result else []
        except Exception as e:
            self.logger.warning(f"Failed to query analyses: {e}")
            return []
