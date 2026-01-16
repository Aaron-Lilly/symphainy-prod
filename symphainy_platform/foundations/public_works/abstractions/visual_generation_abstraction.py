"""
Visual Generation Abstraction - Business Logic Implementation (Layer 1)

Implements visual generation operations using visual generation adapter.
Coordinates visual generation and storage.

WHAT (Infrastructure Role): I provide visual generation services
HOW (Infrastructure Implementation): I use visual generation adapter for generation and file storage for persistence
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger
from ..protocols.visual_generation_protocol import VisualGenerationProtocol, VisualizationResult
from ..adapters.visual_generation_adapter import VisualGenerationAdapter
from ..abstractions.file_storage_abstraction import FileStorageAbstraction


class VisualGenerationAbstraction(VisualGenerationProtocol):
    """
    Visual generation abstraction with business logic.
    
    Coordinates between visual generation adapter (generation) and file storage (persistence).
    Provides visual generation for workflows, SOPs, roadmaps, POCs, summaries, and lineage graphs.
    """
    
    def __init__(
        self,
        visual_generation_adapter: VisualGenerationAdapter,
        file_storage_abstraction: Optional[FileStorageAbstraction] = None
    ):
        """
        Initialize Visual Generation abstraction.
        
        Args:
            visual_generation_adapter: Visual generation adapter for creating visuals (Layer 0)
            file_storage_abstraction: File storage abstraction for persisting visuals (Layer 1, optional)
        """
        self.visual_adapter = visual_generation_adapter
        self.file_storage = file_storage_abstraction
        self.logger = get_logger(self.__class__.__name__)
        
        self.logger.info("✅ Visual Generation Abstraction initialized")
    
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
            result = await self.visual_adapter.create_workflow_visual(workflow_data, tenant_id)
            
            # Optionally store visualization in GCS
            if result.success and self.file_storage:
                try:
                    # Store visualization image
                    visual_path = f"visuals/{tenant_id}/workflows/{workflow_data.get('id', 'unknown')}.png"
                    image_bytes = bytes(result.image_base64, 'utf-8')  # Base64 string
                    # Note: In production, decode base64 to bytes before storing
                    import base64
                    image_bytes = base64.b64decode(result.image_base64)
                    
                    await self.file_storage.upload_file(
                        file_path=visual_path,
                        file_data=image_bytes,
                        metadata={
                            "visualization_type": "workflow",
                            "tenant_id": tenant_id,
                            "workflow_id": workflow_data.get("id")
                        }
                    )
                    
                    # Update metadata with storage path
                    result.metadata["storage_path"] = visual_path
                except Exception as e:
                    self.logger.warning(f"Failed to store workflow visualization: {e}")
            
            return result
            
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
            result = await self.visual_adapter.create_sop_visual(sop_data, tenant_id)
            
            # Optionally store visualization in GCS
            if result.success and self.file_storage:
                try:
                    visual_path = f"visuals/{tenant_id}/sops/{sop_data.get('id', 'unknown')}.png"
                    import base64
                    image_bytes = base64.b64decode(result.image_base64)
                    
                    await self.file_storage.upload_file(
                        file_path=visual_path,
                        file_data=image_bytes,
                        metadata={
                            "visualization_type": "sop",
                            "tenant_id": tenant_id,
                            "sop_id": sop_data.get("id")
                        }
                    )
                    
                    result.metadata["storage_path"] = visual_path
                except Exception as e:
                    self.logger.warning(f"Failed to store SOP visualization: {e}")
            
            return result
            
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
            result = await self.visual_adapter.create_summary_dashboard(pillar_outputs, tenant_id)
            
            # Optionally store visualization in GCS
            if result.success and self.file_storage:
                try:
                    visual_path = f"visuals/{tenant_id}/summaries/{pillar_outputs.get('session_id', 'unknown')}.png"
                    import base64
                    image_bytes = base64.b64decode(result.image_base64)
                    
                    await self.file_storage.upload_file(
                        file_path=visual_path,
                        file_data=image_bytes,
                        metadata={
                            "visualization_type": "summary_dashboard",
                            "tenant_id": tenant_id
                        }
                    )
                    
                    result.metadata["storage_path"] = visual_path
                except Exception as e:
                    self.logger.warning(f"Failed to store summary dashboard: {e}")
            
            return result
            
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
            result = await self.visual_adapter.create_roadmap_visual(roadmap_data, tenant_id)
            
            # Optionally store visualization in GCS
            if result.success and self.file_storage:
                try:
                    visual_path = f"visuals/{tenant_id}/roadmaps/{roadmap_data.get('id', 'unknown')}.png"
                    import base64
                    image_bytes = base64.b64decode(result.image_base64)
                    
                    await self.file_storage.upload_file(
                        file_path=visual_path,
                        file_data=image_bytes,
                        metadata={
                            "visualization_type": "roadmap",
                            "tenant_id": tenant_id,
                            "roadmap_id": roadmap_data.get("id")
                        }
                    )
                    
                    result.metadata["storage_path"] = visual_path
                except Exception as e:
                    self.logger.warning(f"Failed to store roadmap visualization: {e}")
            
            return result
            
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
            result = await self.visual_adapter.create_poc_visual(poc_data, tenant_id)
            
            # Optionally store visualization in GCS
            if result.success and self.file_storage:
                try:
                    visual_path = f"visuals/{tenant_id}/pocs/{poc_data.get('id', 'unknown')}.png"
                    import base64
                    image_bytes = base64.b64decode(result.image_base64)
                    
                    await self.file_storage.upload_file(
                        file_path=visual_path,
                        file_data=image_bytes,
                        metadata={
                            "visualization_type": "poc",
                            "tenant_id": tenant_id,
                            "poc_id": poc_data.get("id")
                        }
                    )
                    
                    result.metadata["storage_path"] = visual_path
                except Exception as e:
                    self.logger.warning(f"Failed to store POC visualization: {e}")
            
            return result
            
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
            result = await self.visual_adapter.create_lineage_graph(lineage_data, tenant_id)
            
            # Optionally store visualization in GCS
            if result.success and self.file_storage:
                try:
                    visual_path = f"visuals/{tenant_id}/lineage/{lineage_data.get('file_id', 'unknown')}.png"
                    import base64
                    image_bytes = base64.b64decode(result.image_base64)
                    
                    await self.file_storage.upload_file(
                        file_path=visual_path,
                        file_data=image_bytes,
                        metadata={
                            "visualization_type": "lineage_graph",
                            "tenant_id": tenant_id,
                            "file_id": lineage_data.get("file_id")
                        }
                    )
                    
                    result.metadata["storage_path"] = visual_path
                except Exception as e:
                    self.logger.warning(f"Failed to store lineage graph: {e}")
            
            return result
            
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
        """Perform health check on the abstraction."""
        try:
            adapter_health = await self.visual_adapter.health_check()
            
            return {
                "status": "healthy" if adapter_health.get("status") == "healthy" else "unhealthy",
                "abstraction": "VisualGenerationAbstraction",
                "adapter": adapter_health,
                "file_storage_available": self.file_storage is not None,
                "capabilities": [
                    "workflow_visual",
                    "sop_visual",
                    "summary_dashboard",
                    "roadmap_visual",
                    "poc_visual",
                    "lineage_graph"
                ]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "abstraction": "VisualGenerationAbstraction",
                "error": str(e)
            }
