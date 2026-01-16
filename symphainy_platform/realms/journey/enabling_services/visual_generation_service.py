"""
Visual Generation Service - Journey Realm

Enabling service for visual generation operations in Journey Realm.

WHAT (Enabling Service Role): I generate visuals for workflows and SOPs
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
    Visual Generation Service for Journey Realm.
    
    Generates visuals for workflows and SOPs using Public Works visual generation abstraction.
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
    
    async def generate_workflow_visual(
        self,
        workflow_data: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate workflow visualization.
        
        Args:
            workflow_data: Workflow data (steps, decisions, flows)
            tenant_id: Tenant ID
            context: Execution context
            
        Returns:
            Dict with visualization result
        """
        if not self.visual_abstraction:
            raise RuntimeError("Visual generation abstraction not available")
        
        try:
            self.logger.info(f"Generating workflow visualization for tenant {tenant_id}")
            
            result = await self.visual_abstraction.create_workflow_visual(
                workflow_data=workflow_data,
                tenant_id=tenant_id
            )
            
            if result.success:
                return {
                    "success": True,
                    "visualization_type": "workflow",
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
            self.logger.error(f"❌ Failed to generate workflow visualization: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_sop_visual(
        self,
        sop_data: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate SOP visualization.
        
        Args:
            sop_data: SOP data (steps, procedures, checkpoints)
            tenant_id: Tenant ID
            context: Execution context
            
        Returns:
            Dict with visualization result
        """
        if not self.visual_abstraction:
            raise RuntimeError("Visual generation abstraction not available")
        
        try:
            self.logger.info(f"Generating SOP visualization for tenant {tenant_id}")
            
            result = await self.visual_abstraction.create_sop_visual(
                sop_data=sop_data,
                tenant_id=tenant_id
            )
            
            if result.success:
                return {
                    "success": True,
                    "visualization_type": "sop",
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
            self.logger.error(f"❌ Failed to generate SOP visualization: {e}")
            return {
                "success": False,
                "error": str(e)
            }
