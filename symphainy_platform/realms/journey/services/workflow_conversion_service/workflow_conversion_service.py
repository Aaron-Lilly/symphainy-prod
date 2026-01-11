"""
Workflow Conversion Service

Deterministic service for bi-directional conversion between SOPs and workflows.
Uses State Surface for file retrieval (references).
Stores workflows in ArangoDB with references in State Surface.

WHAT (Journey Realm): I convert between SOPs and workflows
HOW (Service): I provide deterministic conversion algorithms
"""

import json
import uuid
from typing import Dict, Any, Optional

from utilities import get_logger, get_clock

logger = get_logger(__name__)


class WorkflowConversionService:
    """
    Workflow Conversion Service.
    
    Provides deterministic conversion capabilities:
    - Convert SOP to workflow (bidirectional)
    - Convert workflow to SOP (bidirectional)
    - Validate conversions
    
    Pattern:
    - Deterministic
    - Stateless
    - Input → Output
    - No orchestration
    - No reasoning
    """
    
    def __init__(
        self,
        state_surface: Any,
        file_storage_abstraction: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize Workflow Conversion Service.
        
        Args:
            state_surface: State Surface instance for file retrieval
            file_storage_abstraction: File Storage Abstraction for artifact storage
            platform_gateway: Platform Gateway for accessing abstractions
        """
        self.state_surface = state_surface
        self.file_storage = file_storage_abstraction
        self.platform_gateway = platform_gateway
        self.logger = logger
        self.clock = get_clock()
        
        # Workflow patterns
        self.workflow_patterns = {
            "sequential": {"type": "linear", "description": "Step-by-step sequential execution"},
            "parallel": {"type": "concurrent", "description": "Multiple steps executed in parallel"},
            "conditional": {"type": "branching", "description": "Steps with conditional logic"},
            "iterative": {"type": "loop", "description": "Steps that repeat based on conditions"}
        }
        
        self.logger.info("✅ Workflow Conversion Service initialized")
    
    async def convert_sop_to_workflow(
        self,
        sop_file_reference: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert SOP to workflow.
        
        Args:
            sop_file_reference: State Surface reference to SOP file
            options: Optional conversion options (workflow_pattern, etc.)
        
        Returns:
            Dict with workflow_structure (for orchestrator to store)
        """
        try:
            self.logger.info(f"Converting SOP to workflow: {sop_file_reference}")
            
            # Get SOP from State Surface (reference) → retrieve from GCS
            sop_metadata = await self.state_surface.get_file_metadata(sop_file_reference)
            if not sop_metadata:
                return {
                    "success": False,
                    "error": "SOP reference not found in State Surface"
                }
            
            storage_location = sop_metadata.get("storage_location")
            if not storage_location:
                return {
                    "success": False,
                    "error": "SOP storage location not found"
                }
            
            # Retrieve SOP artifact from GCS
            sop_data_bytes = await self.file_storage.download_file(storage_location)
            if not sop_data_bytes:
                return {
                    "success": False,
                    "error": "Failed to retrieve SOP artifact from storage"
                }
            
            # Parse SOP content
            sop_content = json.loads(sop_data_bytes.decode('utf-8'))
            
            # Convert SOP to workflow structure (deterministic algorithm)
            workflow_structure = await self._sop_to_workflow_algorithm(sop_content, options)
            
            self.logger.info("✅ SOP converted to workflow structure")
            
            return {
                "success": True,
                "workflow_structure": workflow_structure,
                "conversion_metadata": {
                    "source_reference": sop_file_reference,
                    "conversion_type": "sop_to_workflow",
                    "converted_at": self.clock.now_iso()
                }
            }
        
        except Exception as e:
            self.logger.error(f"Failed to convert SOP to workflow: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def convert_workflow_to_sop(
        self,
        workflow_file_reference: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert workflow to SOP.
        
        Args:
            workflow_file_reference: State Surface reference to workflow file
            options: Optional conversion options (template_type, etc.)
        
        Returns:
            Dict with sop_structure (for orchestrator to store)
        """
        try:
            self.logger.info(f"Converting workflow to SOP: {workflow_file_reference}")
            
            # Get workflow from State Surface (reference) → retrieve from storage
            # Note: For now, we'll assume workflows are also stored in GCS
            # In production, workflows would be in ArangoDB
            workflow_metadata = await self.state_surface.get_file_metadata(workflow_file_reference)
            if not workflow_metadata:
                return {
                    "success": False,
                    "error": "Workflow reference not found in State Surface"
                }
            
            storage_location = workflow_metadata.get("storage_location")
            if not storage_location:
                return {
                    "success": False,
                    "error": "Workflow storage location not found"
                }
            
            # Retrieve workflow artifact from storage
            workflow_data_bytes = await self.file_storage.download_file(storage_location)
            if not workflow_data_bytes:
                return {
                    "success": False,
                    "error": "Failed to retrieve workflow artifact from storage"
                }
            
            # Parse workflow content
            workflow_content = json.loads(workflow_data_bytes.decode('utf-8'))
            
            # Convert workflow to SOP structure (deterministic algorithm)
            sop_structure = await self._workflow_to_sop_algorithm(workflow_content, options)
            
            self.logger.info("✅ Workflow converted to SOP structure")
            
            return {
                "success": True,
                "sop_structure": sop_structure,
                "conversion_metadata": {
                    "source_reference": workflow_file_reference,
                    "conversion_type": "workflow_to_sop",
                    "converted_at": self.clock.now_iso()
                }
            }
        
        except Exception as e:
            self.logger.error(f"Failed to convert workflow to SOP: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_conversion(
        self,
        source_reference: str,
        target_reference: str,
        conversion_type: str
    ) -> Dict[str, Any]:
        """
        Validate conversion between source and target.
        
        Args:
            source_reference: State Surface reference to source artifact
            target_reference: State Surface reference to target artifact
            conversion_type: Type of conversion (sop_to_workflow or workflow_to_sop)
        
        Returns:
            Dict with validation results
        """
        try:
            self.logger.info(f"Validating conversion: {conversion_type}")
            
            # Get source and target metadata
            source_metadata = await self.state_surface.get_file_metadata(source_reference)
            target_metadata = await self.state_surface.get_file_metadata(target_reference)
            
            if not source_metadata or not target_metadata:
                return {
                    "success": False,
                    "error": "Source or target reference not found"
                }
            
            # Basic validation: check that both artifacts exist
            source_location = source_metadata.get("storage_location")
            target_location = target_metadata.get("storage_location")
            
            # Check if files exist by trying to retrieve them
            try:
                source_data = await self.file_storage.download_file(source_location) if source_location else None
                source_exists = source_data is not None
            except:
                source_exists = False
            
            try:
                target_data = await self.file_storage.download_file(target_location) if target_location else None
                target_exists = target_data is not None
            except:
                target_exists = False
            
            valid = source_exists and target_exists
            
            return {
                "success": True,
                "valid": valid,
                "source_exists": source_exists,
                "target_exists": target_exists,
                "conversion_type": conversion_type,
                "validated_at": self.clock.now_iso()
            }
        
        except Exception as e:
            self.logger.error(f"Failed to validate conversion: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _sop_to_workflow_algorithm(
        self,
        sop_content: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Convert SOP content to workflow structure (deterministic algorithm)."""
        workflow_pattern = options.get("workflow_pattern", "sequential") if options else "sequential"
        
        # Extract procedures from SOP
        procedures = sop_content.get("sections", {}).get("procedures", [])
        if isinstance(procedures, str):
            # If procedures is a string, split into steps
            procedures = [step.strip() for step in procedures.split("\n") if step.strip()]
        
        # Build workflow structure
        workflow_structure = {
            "workflow_id": str(uuid.uuid4()),
            "workflow_name": sop_content.get("title", "Untitled Workflow"),
            "workflow_type": workflow_pattern,
            "description": sop_content.get("sections", {}).get("purpose", ""),
            "nodes": [],
            "edges": [],
            "metadata": {
                "source_sop": sop_content.get("sop_id"),
                "created_at": self.clock.now_iso()
            }
        }
        
        # Convert procedures to workflow nodes
        for i, procedure in enumerate(procedures):
            node = {
                "node_id": f"node_{i+1}",
                "node_type": "task",
                "label": procedure if isinstance(procedure, str) else procedure.get("description", f"Step {i+1}"),
                "position": {"x": 100, "y": (i+1) * 100}
            }
            workflow_structure["nodes"].append(node)
            
            # Add edge from previous node
            if i > 0:
                edge = {
                    "edge_id": f"edge_{i}",
                    "source": f"node_{i}",
                    "target": f"node_{i+1}",
                    "type": "sequential"
                }
                workflow_structure["edges"].append(edge)
        
        return workflow_structure
    
    async def _workflow_to_sop_algorithm(
        self,
        workflow_content: Dict[str, Any],
        options: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Convert workflow content to SOP structure (deterministic algorithm)."""
        template_type = options.get("template_type", "standard") if options else "standard"
        
        # Extract nodes from workflow
        nodes = workflow_content.get("nodes", [])
        
        # Build SOP structure
        sop_structure = {
            "template_type": template_type,
            "title": workflow_content.get("workflow_name", "Untitled SOP"),
            "purpose": workflow_content.get("description", ""),
            "sections": {
                "procedures": []
            },
            "metadata": {
                "source_workflow": workflow_content.get("workflow_id"),
                "created_at": self.clock.now_iso()
            }
        }
        
        # Convert workflow nodes to procedures
        for node in nodes:
            if node.get("node_type") == "task":
                procedure = {
                    "step": len(sop_structure["sections"]["procedures"]) + 1,
                    "description": node.get("label", ""),
                    "node_id": node.get("node_id")
                }
                sop_structure["sections"]["procedures"].append(procedure)
        
        return sop_structure
