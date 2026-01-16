"""
Visual Generation Service - Outcomes Realm

Enabling service for visual generation operations in Outcomes Realm.

WHAT (Enabling Service Role): I generate visuals for summaries, roadmaps, and POCs
HOW (Enabling Service Implementation): I use Public Works visual generation abstraction
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext


class VisualGenerationService:
    """
    Visual Generation Service for Outcomes Realm.
    
    Generates visuals for summaries, roadmaps, and POCs using Public Works visual generation abstraction.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Visual Generation Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Get visual generation abstraction from Public Works
        self.visual_abstraction = None
        if public_works:
            self.visual_abstraction = public_works.get_visual_generation_abstraction()
    
    async def generate_summary_visual(
        self,
        pillar_outputs: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate summary dashboard visualization.
        
        Args:
            pillar_outputs: Summary outputs from Content, Insights, and Journey pillars
            tenant_id: Tenant ID
            context: Execution context
            
        Returns:
            Dict with visualization result
        """
        if not self.visual_abstraction:
            raise RuntimeError("Visual generation abstraction not available")
        
        try:
            self.logger.info(f"Generating summary dashboard for tenant {tenant_id}")
            
            result = await self.visual_abstraction.create_summary_dashboard(
                pillar_outputs=pillar_outputs,
                tenant_id=tenant_id
            )
            
            if result.success:
                return {
                    "success": True,
                    "visualization_type": "summary_dashboard",
                    "image_base64": result.image_base64,
                    "storage_path": result.metadata.get("storage_path"),
                    "metadata": result.metadata
                }
            else:
                return {
                    "success": False,
                    "error": result.error
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to generate summary dashboard: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_roadmap_visual(
        self,
        roadmap_data: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate roadmap visualization.
        
        Args:
            roadmap_data: Roadmap data (phases, timeline, milestones)
            tenant_id: Tenant ID
            context: Execution context
            
        Returns:
            Dict with visualization result
        """
        if not self.visual_abstraction:
            raise RuntimeError("Visual generation abstraction not available")
        
        try:
            self.logger.info(f"Generating roadmap visualization for tenant {tenant_id}")
            
            result = await self.visual_abstraction.create_roadmap_visual(
                roadmap_data=roadmap_data,
                tenant_id=tenant_id
            )
            
            if result.success:
                return {
                    "success": True,
                    "visualization_type": "roadmap",
                    "image_base64": result.image_base64,
                    "storage_path": result.metadata.get("storage_path"),
                    "metadata": result.metadata
                }
            else:
                return {
                    "success": False,
                    "error": result.error
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to generate roadmap visualization: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_poc_visual(
        self,
        poc_data: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate POC visualization.
        
        Args:
            poc_data: POC data (proposal, scope, timeline)
            tenant_id: Tenant ID
            context: Execution context
            
        Returns:
            Dict with visualization result
        """
        if not self.visual_abstraction:
            raise RuntimeError("Visual generation abstraction not available")
        
        try:
            self.logger.info(f"Generating POC visualization for tenant {tenant_id}")
            
            result = await self.visual_abstraction.create_poc_visual(
                poc_data=poc_data,
                tenant_id=tenant_id
            )
            
            if result.success:
                return {
                    "success": True,
                    "visualization_type": "poc",
                    "image_base64": result.image_base64,
                    "storage_path": result.metadata.get("storage_path"),
                    "metadata": result.metadata
                }
            else:
                return {
                    "success": False,
                    "error": result.error
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to generate POC visualization: {e}")
            return {
                "success": False,
                "error": str(e)
            }
