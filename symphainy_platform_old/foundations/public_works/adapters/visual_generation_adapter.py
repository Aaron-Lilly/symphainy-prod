"""
Visual Generation Adapter

Infrastructure adapter for visual generation capabilities using plotly, matplotlib, graphviz.

WHAT (Infrastructure Adapter Role): I provide visual generation capabilities
HOW (Adapter Implementation): I wrap plotly, matplotlib, graphviz for visual displays
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import logging
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, Any, Optional
from datetime import datetime
import base64
import io

from utilities import get_logger
from ..protocols.visual_generation_protocol import VisualizationResult, VisualGenerationProtocol


class VisualGenerationAdapter:
    """
    Visual Generation Adapter
    
    Provides visual generation capabilities using plotly, matplotlib, graphviz.
    """
    
    def __init__(self):
        """Initialize Visual Generation Adapter."""
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("🏗️ VisualGenerationAdapter initialized")
    
    async def create_workflow_visual(
        self,
        workflow_data: Dict[str, Any],
        tenant_id: str
    ) -> VisualizationResult:
        """
        Create workflow visualization.
        
        Args:
            workflow_data: Workflow data (steps, decisions, flows)
            tenant_id: Tenant ID
            
        Returns:
            VisualizationResult: Workflow visualization
        """
        try:
            self.logger.info(f"Creating workflow visualization for tenant {tenant_id}...")
            
            # Extract workflow steps
            steps = workflow_data.get("steps", [])
            if not steps:
                return VisualizationResult(
                    success=False,
                    visualization_type="workflow",
                    chart_data={},
                    image_base64="",
                    metadata={},
                    error="No workflow steps provided"
                )
            
            # Create flowchart-style visualization
            fig = go.Figure()
            
            # Create nodes and edges
            node_x = []
            node_y = []
            node_text = []
            node_ids = []
            
            # Position nodes in a flow
            for i, step in enumerate(steps):
                node_x.append(i * 2)
                node_y.append(0)
                node_text.append(step.get("name", f"Step {i+1}"))
                node_ids.append(step.get("id", f"step_{i}"))
            
            # Add edges (connections between steps)
            for i in range(len(steps) - 1):
                fig.add_trace(go.Scatter(
                    x=[node_x[i], node_x[i+1]],
                    y=[node_y[i], node_y[i+1]],
                    mode="lines+markers",
                    line=dict(color="blue", width=2),
                    showlegend=False,
                    hoverinfo="skip"
                ))
            
            # Add nodes
            fig.add_trace(go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                text=node_text,
                textposition="middle center",
                marker=dict(size=50, color="lightblue", line=dict(width=2, color="darkblue")),
                showlegend=False,
                hoverinfo="text",
                hovertext=[f"{text}<br>ID: {node_ids[i]}" for i, text in enumerate(node_text)]
            ))
            
            # Update layout
            fig.update_layout(
                title="Workflow Visualization",
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                height=400,
                showlegend=False,
                plot_bgcolor="white"
            )
            
            # Convert to base64 for web display
            img_bytes = fig.to_image(format="png", width=1200, height=400)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return VisualizationResult(
                success=True,
                visualization_type="workflow",
                chart_data=fig.to_dict(),
                image_base64=img_base64,
                metadata={
                    "creation_method": "plotly",
                    "steps_count": len(steps),
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create workflow visualization: {e}")
            return VisualizationResult(
                success=False,
                visualization_type="workflow",
                chart_data={},
                image_base64="",
                metadata={},
                error=str(e)
            )
    
    async def create_sop_visual(
        self,
        sop_data: Dict[str, Any],
        tenant_id: str
    ) -> VisualizationResult:
        """
        Create SOP visualization.
        
        Args:
            sop_data: SOP data (steps, procedures, checkpoints)
            tenant_id: Tenant ID
            
        Returns:
            VisualizationResult: SOP visualization
        """
        try:
            self.logger.info(f"Creating SOP visualization for tenant {tenant_id}...")
            
            # Extract SOP steps
            steps = sop_data.get("steps", [])
            if not steps:
                return VisualizationResult(
                    success=False,
                    visualization_type="sop",
                    chart_data={},
                    image_base64="",
                    metadata={},
                    error="No SOP steps provided"
                )
            
            # Create vertical flow visualization
            fig = go.Figure()
            
            # Create nodes
            node_y = []
            node_text = []
            node_descriptions = []
            
            for i, step in enumerate(steps):
                node_y.append(len(steps) - i)  # Reverse order (top to bottom)
                node_text.append(step.get("name", f"Step {i+1}"))
                node_descriptions.append(step.get("description", ""))
            
            # Add edges (vertical connections)
            for i in range(len(steps) - 1):
                fig.add_trace(go.Scatter(
                    x=[0, 0],
                    y=[node_y[i], node_y[i+1]],
                    mode="lines",
                    line=dict(color="green", width=3),
                    showlegend=False,
                    hoverinfo="skip"
                ))
            
            # Add nodes
            fig.add_trace(go.Scatter(
                x=[0] * len(steps),
                y=node_y,
                mode="markers+text",
                text=node_text,
                textposition="middle right",
                marker=dict(size=60, color="lightgreen", line=dict(width=2, color="darkgreen")),
                showlegend=False,
                hoverinfo="text",
                hovertext=[f"{text}<br>{desc}" for text, desc in zip(node_text, node_descriptions)]
            ))
            
            # Update layout
            fig.update_layout(
                title="SOP Visualization",
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-1, 1]),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                height=max(400, len(steps) * 100),
                showlegend=False,
                plot_bgcolor="white"
            )
            
            # Convert to base64 for web display
            img_bytes = fig.to_image(format="png", width=800, height=max(400, len(steps) * 100))
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return VisualizationResult(
                success=True,
                visualization_type="sop",
                chart_data=fig.to_dict(),
                image_base64=img_base64,
                metadata={
                    "creation_method": "plotly",
                    "steps_count": len(steps),
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create SOP visualization: {e}")
            return VisualizationResult(
                success=False,
                visualization_type="sop",
                chart_data={},
                image_base64="",
                metadata={},
                error=str(e)
            )
    
    async def create_summary_dashboard(
        self,
        pillar_outputs: Dict[str, Any],
        tenant_id: str
    ) -> VisualizationResult:
        """
        Create summary dashboard showing outputs from all pillars.
        
        Args:
            pillar_outputs: Summary outputs from Content, Insights, and Journey pillars
            tenant_id: Tenant ID
            
        Returns:
            VisualizationResult: Dashboard visualization
        """
        try:
            self.logger.info(f"Creating summary dashboard for tenant {tenant_id}...")
            
            # Create subplot layout
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    "Content Pillar Summary",
                    "Insights Pillar Summary",
                    "Journey Pillar Summary",
                    "Overall Progress"
                ],
                specs=[[{"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "bar"}]]
            )
            
            # Content Pillar Summary
            content_summary = pillar_outputs.get("content_pillar", {})
            files_uploaded = content_summary.get("files_uploaded", 0)
            files_parsed = content_summary.get("files_parsed", 0)
            
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=files_uploaded,
                    title={"text": "Files Uploaded"},
                    delta={"reference": 0},
                    domain={"row": 0, "column": 0}
                )
            )
            
            # Insights Pillar Summary
            insights_summary = pillar_outputs.get("insights_pillar", {})
            insights_count = insights_summary.get("insights_generated", 0)
            
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=insights_count,
                    title={"text": "Insights Generated"},
                    delta={"reference": 0},
                    domain={"row": 0, "column": 1}
                )
            )
            
            # Journey Pillar Summary
            journey_summary = pillar_outputs.get("journey_pillar", {})
            workflows_created = journey_summary.get("workflows_created", 0)
            
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=workflows_created,
                    title={"text": "Workflows Created"},
                    delta={"reference": 0},
                    domain={"row": 1, "column": 0}
                )
            )
            
            # Overall Progress
            progress_data = {
                "Content": 100 if files_uploaded > 0 else 0,
                "Insights": 100 if insights_count > 0 else 0,
                "Journey": 100 if workflows_created > 0 else 0
            }
            
            fig.add_trace(
                go.Bar(
                    x=list(progress_data.keys()),
                    y=list(progress_data.values()),
                    name="Progress",
                    marker_color=["green", "blue", "orange"]
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title="Platform Summary Dashboard",
                height=600,
                showlegend=False
            )
            
            # Convert to base64 for web display
            img_bytes = fig.to_image(format="png", width=1000, height=600)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return VisualizationResult(
                success=True,
                visualization_type="summary_dashboard",
                chart_data=fig.to_dict(),
                image_base64=img_base64,
                metadata={
                    "creation_method": "plotly",
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create summary dashboard: {e}")
            return VisualizationResult(
                success=False,
                visualization_type="summary_dashboard",
                chart_data={},
                image_base64="",
                metadata={},
                error=str(e)
            )
    
    async def create_roadmap_visual(
        self,
        roadmap_data: Dict[str, Any],
        tenant_id: str
    ) -> VisualizationResult:
        """
        Create roadmap visualization.
        
        Args:
            roadmap_data: Roadmap data (phases, timeline, milestones)
            tenant_id: Tenant ID
            
        Returns:
            VisualizationResult: Roadmap visualization
        """
        try:
            self.logger.info(f"Creating roadmap visualization for tenant {tenant_id}...")
            
            # Extract phases and timeline data
            phases = roadmap_data.get("phases", [])
            if not phases:
                return VisualizationResult(
                    success=False,
                    visualization_type="roadmap",
                    chart_data={},
                    image_base64="",
                    metadata={},
                    error="No phases data available for roadmap"
                )
            
            # Create Gantt chart
            fig = go.Figure()
            
            # Calculate cumulative timeline
            current_week = 0
            for i, phase in enumerate(phases):
                duration = phase.get("duration_weeks", 4)
                phase_name = phase.get("name", f"Phase {i+1}")
                
                fig.add_trace(go.Scatter(
                    x=[current_week, current_week + duration, current_week + duration, current_week, current_week],
                    y=[i, i, i+0.8, i+0.8, i],
                    fill="toself",
                    fillcolor=f"hsl({i*60}, 70%, 80%)",
                    line=dict(color=f"hsl({i*60}, 70%, 50%)", width=2),
                    name=phase_name,
                    text=f"{phase_name}<br>{duration} weeks",
                    textposition="middle center",
                    hoverinfo="text"
                ))
                
                current_week += duration
            
            # Update layout
            fig.update_layout(
                title="Strategic Roadmap Timeline",
                xaxis_title="Weeks",
                yaxis_title="Phases",
                height=400,
                showlegend=True,
                yaxis=dict(
                    tickmode="array",
                    tickvals=list(range(len(phases))),
                    ticktext=[phase.get("name", f"Phase {i+1}") for i, phase in enumerate(phases)]
                )
            )
            
            # Convert to base64 for web display
            img_bytes = fig.to_image(format="png", width=1200, height=400)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return VisualizationResult(
                success=True,
                visualization_type="roadmap",
                chart_data=fig.to_dict(),
                image_base64=img_base64,
                metadata={
                    "creation_method": "plotly",
                    "phases_count": len(phases),
                    "total_duration_weeks": current_week,
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create roadmap visualization: {e}")
            return VisualizationResult(
                success=False,
                visualization_type="roadmap",
                chart_data={},
                image_base64="",
                metadata={},
                error=str(e)
            )
    
    async def create_poc_visual(
        self,
        poc_data: Dict[str, Any],
        tenant_id: str
    ) -> VisualizationResult:
        """
        Create POC visualization.
        
        Args:
            poc_data: POC data (proposal, scope, timeline)
            tenant_id: Tenant ID
            
        Returns:
            VisualizationResult: POC visualization
        """
        try:
            self.logger.info(f"Creating POC visualization for tenant {tenant_id}...")
            
            # Extract POC components
            scope = poc_data.get("scope", {})
            timeline = poc_data.get("timeline", {})
            objectives = poc_data.get("objectives", [])
            
            # Create subplot layout
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=["POC Scope", "Timeline"],
                specs=[[{"type": "pie"}, {"type": "bar"}]]
            )
            
            # POC Scope (pie chart)
            if scope:
                scope_items = list(scope.keys())
                scope_values = list(scope.values())
                
                fig.add_trace(
                    go.Pie(
                        labels=scope_items,
                        values=scope_values,
                        name="Scope"
                    ),
                    row=1, col=1
                )
            
            # Timeline (bar chart)
            if timeline:
                timeline_items = list(timeline.keys())
                timeline_values = list(timeline.values())
                
                fig.add_trace(
                    go.Bar(
                        x=timeline_items,
                        y=timeline_values,
                        name="Timeline",
                        marker_color="lightblue"
                    ),
                    row=1, col=2
                )
            
            # Update layout
            fig.update_layout(
                title="POC Proposal Visualization",
                height=400,
                showlegend=True
            )
            
            # Convert to base64 for web display
            img_bytes = fig.to_image(format="png", width=1200, height=400)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return VisualizationResult(
                success=True,
                visualization_type="poc",
                chart_data=fig.to_dict(),
                image_base64=img_base64,
                metadata={
                    "creation_method": "plotly",
                    "objectives_count": len(objectives),
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create POC visualization: {e}")
            return VisualizationResult(
                success=False,
                visualization_type="poc",
                chart_data={},
                image_base64="",
                metadata={},
                error=str(e)
            )
    
    async def create_lineage_graph(
        self,
        lineage_data: Dict[str, Any],
        tenant_id: str
    ) -> VisualizationResult:
        """
        Create lineage graph visualization.
        
        Args:
            lineage_data: Lineage data (nodes, edges, relationships)
            tenant_id: Tenant ID
            
        Returns:
            VisualizationResult: Lineage graph visualization
        """
        try:
            self.logger.info(f"Creating lineage graph for tenant {tenant_id}...")
            
            # Extract nodes and edges
            nodes = lineage_data.get("nodes", [])
            edges = lineage_data.get("edges", [])
            
            if not nodes:
                return VisualizationResult(
                    success=False,
                    visualization_type="lineage_graph",
                    chart_data={},
                    image_base64="",
                    metadata={},
                    error="No nodes provided for lineage graph"
                )
            
            # Create network graph
            fig = go.Figure()
            
            # Position nodes (simple layout)
            node_positions = {}
            for i, node in enumerate(nodes):
                node_id = node.get("id", f"node_{i}")
                # Simple circular layout
                angle = 2 * 3.14159 * i / len(nodes)
                node_positions[node_id] = {
                    "x": 5 * (1 + 0.5 * (i % 3)),
                    "y": 5 * (1 + 0.5 * (i // 3))
                }
            
            # Add edges
            for edge in edges:
                source = edge.get("source")
                target = edge.get("target")
                
                if source in node_positions and target in node_positions:
                    fig.add_trace(go.Scatter(
                        x=[node_positions[source]["x"], node_positions[target]["x"]],
                        y=[node_positions[source]["y"], node_positions[target]["y"]],
                        mode="lines",
                        line=dict(color="gray", width=1),
                        showlegend=False,
                        hoverinfo="skip"
                    ))
            
            # Add nodes
            node_x = [node_positions[node.get("id", f"node_{i}")]["x"] for i, node in enumerate(nodes)]
            node_y = [node_positions[node.get("id", f"node_{i}")]["y"] for i, node in enumerate(nodes)]
            node_text = [node.get("label", node.get("id", f"Node {i}")) for i, node in enumerate(nodes)]
            
            fig.add_trace(go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                text=node_text,
                textposition="middle center",
                marker=dict(size=50, color="lightblue", line=dict(width=2, color="darkblue")),
                showlegend=False,
                hoverinfo="text"
            ))
            
            # Update layout
            fig.update_layout(
                title="Data Lineage Graph",
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                height=600,
                showlegend=False,
                plot_bgcolor="white"
            )
            
            # Convert to base64 for web display
            img_bytes = fig.to_image(format="png", width=1200, height=600)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return VisualizationResult(
                success=True,
                visualization_type="lineage_graph",
                chart_data=fig.to_dict(),
                image_base64=img_base64,
                metadata={
                    "creation_method": "plotly",
                    "nodes_count": len(nodes),
                    "edges_count": len(edges),
                    "tenant_id": tenant_id,
                    "created_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create lineage graph: {e}")
            return VisualizationResult(
                success=False,
                visualization_type="lineage_graph",
                chart_data={},
                image_base64="",
                metadata={},
                error=str(e)
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the adapter."""
        try:
            # Test basic functionality
            test_data = {
                "steps": [{"name": "Test Step", "id": "test_1"}]
            }
            
            result = await self.create_workflow_visual(test_data, "test_tenant")
            
            return {
                "status": "healthy" if result.success else "unhealthy",
                "adapter": "VisualGenerationAdapter",
                "capabilities": [
                    "workflow_visual",
                    "sop_visual",
                    "summary_dashboard",
                    "roadmap_visual",
                    "poc_visual",
                    "lineage_graph"
                ],
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "adapter": "VisualGenerationAdapter",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
