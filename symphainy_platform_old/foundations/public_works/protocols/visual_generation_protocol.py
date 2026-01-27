"""
Visual Generation Protocol

Protocol for visual generation capabilities.

WHAT (Protocol Role): I define the interface for visual generation services
HOW (Protocol Implementation): I specify methods for creating visual displays
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class VisualizationResult:
    """Result from visualization operations."""
    success: bool
    visualization_type: str
    chart_data: Dict[str, Any]
    image_base64: str
    metadata: Dict[str, Any]
    error: Optional[str] = None


class VisualGenerationProtocol(Protocol):
    """
    Protocol for visual generation capabilities.
    
    Defines the interface for creating visual displays including:
    - Workflow visualizations
    - SOP visualizations
    - Summary dashboards
    - Roadmap visualizations
    - POC visualizations
    - Lineage graphs
    """
    
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
        ...
    
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
        ...
    
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
        ...
    
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
        ...
    
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
        ...
    
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
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the visual generation adapter.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        ...
