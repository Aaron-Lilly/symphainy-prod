"""
Operations Orchestrator - Coordinates Operations

Coordinates enabling services for workflow optimization and SOP management.

WHAT (Orchestrator Role): I coordinate operations
HOW (Orchestrator Implementation): I route intents to enabling services and compose results

⚠️ CRITICAL: Orchestrators coordinate within a single intent only.
They may NOT spawn long-running sagas, manage retries, or track cross-intent progress.
"""

import sys
from pathlib import Path
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from ..enabling_services.workflow_conversion_service import WorkflowConversionService
from ..enabling_services.coexistence_analysis_service import CoexistenceAnalysisService


class OperationsOrchestrator:
    """
    Operations Orchestrator - Coordinates operations.
    
    Coordinates:
    - Workflow conversion
    - SOP generation
    - Coexistence analysis
    - Blueprint creation
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Operations Orchestrator.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Initialize enabling services with Public Works
        self.workflow_conversion_service = WorkflowConversionService(public_works=public_works)
        self.coexistence_analysis_service = CoexistenceAnalysisService(public_works=public_works)
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent by coordinating enabling services.
        
        Args:
            intent: The intent to handle
            context: Runtime execution context
        
        Returns:
            Dict with "artifacts" and "events" keys
        """
        intent_type = intent.intent_type
        
        if intent_type == "optimize_process":
            return await self._handle_optimize_process(intent, context)
        elif intent_type == "generate_sop":
            return await self._handle_generate_sop(intent, context)
        elif intent_type == "create_workflow":
            return await self._handle_create_workflow(intent, context)
        elif intent_type == "analyze_coexistence":
            return await self._handle_analyze_coexistence(intent, context)
        elif intent_type == "create_blueprint":
            return await self._handle_create_blueprint(intent, context)
        else:
            raise ValueError(f"Unknown intent type: {intent_type}")
    
    async def _handle_optimize_process(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle optimize_process intent."""
        workflow_id = intent.parameters.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required for optimize_process intent")
        
        # Optimize workflow via WorkflowConversionService
        optimization_result = await self.workflow_conversion_service.optimize_workflow(
            workflow_id=workflow_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "optimization": optimization_result,
                "workflow_id": workflow_id
            },
            "events": [
                {
                    "type": "process_optimized",
                    "workflow_id": workflow_id
                }
            ]
        }
    
    async def _handle_generate_sop(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle generate_sop intent."""
        workflow_id = intent.parameters.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required for generate_sop intent")
        
        # Generate SOP via WorkflowConversionService
        sop_result = await self.workflow_conversion_service.generate_sop(
            workflow_id=workflow_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "sop": sop_result,
                "workflow_id": workflow_id
            },
            "events": [
                {
                    "type": "sop_generated",
                    "workflow_id": workflow_id
                }
            ]
        }
    
    async def _handle_create_workflow(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle create_workflow intent.
        
        Supports two modes:
        1. From SOP: sop_id is provided
        2. From BPMN file: workflow_file_path is provided (and optionally workflow_type)
        """
        sop_id = intent.parameters.get("sop_id")
        workflow_file_path = intent.parameters.get("workflow_file_path")
        workflow_type = intent.parameters.get("workflow_type", "bpmn")
        
        if not sop_id and not workflow_file_path:
            raise ValueError("Either sop_id or workflow_file_path is required for create_workflow intent")
        
        # Mode 1: Create workflow from SOP
        if sop_id:
            # Create workflow via WorkflowConversionService
            workflow_result = await self.workflow_conversion_service.create_workflow(
                sop_id=sop_id,
                tenant_id=context.tenant_id,
                context=context
            )
        # Mode 2: Create workflow from BPMN file
        else:
            # Parse BPMN file and create workflow
            self.logger.info(f"Parsing BPMN file: {workflow_file_path}")
            
            # Get BPMN file content
            bpmn_xml = None
            
            # Try to get from parsed file if workflow_file_path is a file_id
            if self.public_works:
                try:
                    from symphainy_platform.realms.content.enabling_services.file_parser_service import FileParserService
                    file_parser_service = FileParserService(public_works=self.public_works)
                    parsed_content = await file_parser_service.get_parsed_file(
                        parsed_file_id=workflow_file_path,
                        tenant_id=context.tenant_id,
                        context=context
                    )
                    
                    if parsed_content:
                        bpmn_xml = parsed_content.get("data") or parsed_content.get("content")
                        if isinstance(bpmn_xml, bytes):
                            bpmn_xml = bpmn_xml.decode('utf-8')
                        elif isinstance(bpmn_xml, dict):
                            bpmn_xml = parsed_content.get("metadata", {}).get("bpmn_xml") or str(parsed_content.get("content", ""))
                except Exception as e:
                    self.logger.debug(f"Could not get parsed file: {e}, trying file storage")
            
            # If not found, try file storage abstraction
            if not bpmn_xml and self.public_works:
                try:
                    file_storage = self.public_works.get_file_storage_abstraction()
                    if file_storage:
                        file_content = await file_storage.download_file(workflow_file_path)
                        if file_content:
                            if isinstance(file_content, bytes):
                                bpmn_xml = file_content.decode('utf-8')
                            else:
                                bpmn_xml = str(file_content)
                except Exception as e:
                    self.logger.warning(f"Could not get file from storage: {e}")
            
            # Parse BPMN XML via WorkflowConversionService
            if bpmn_xml:
                workflow_result = await self.workflow_conversion_service.parse_bpmn_file(
                    bpmn_xml=bpmn_xml,
                    workflow_id=None,
                    tenant_id=context.tenant_id,
                    context=context
                )
                workflow_result["source_file"] = workflow_file_path
                workflow_result["workflow_type"] = workflow_type
            else:
                # Fallback: Create basic workflow structure
                self.logger.warning(f"BPMN content not found for {workflow_file_path}, creating basic workflow structure")
                from utilities import generate_event_id
                workflow_id = generate_event_id()
                workflow_result = {
                    "workflow_id": workflow_id,
                    "workflow_type": workflow_type,
                    "source_file": workflow_file_path,
                    "workflow_status": "created_from_file",
                    "workflow_content": {
                        "workflow_id": workflow_id,
                        "workflow_name": f"Workflow from {workflow_file_path.split('/')[-1]}",
                        "tasks": [],
                        "sequence_flows": []
                    },
                    "metadata": {
                        "created_date": context.created_at.isoformat() if hasattr(context, 'created_at') else None,
                        "source": "bpmn_file"
                    }
                }
        
        # Generate workflow visualization if visual generation service is available
        visual_result = None
        try:
            if hasattr(self, 'visual_generation_service') and self.visual_generation_service:
                visual_result = await self.visual_generation_service.generate_workflow_visual(
                    workflow_data=workflow_result,
                    tenant_id=context.tenant_id,
                    context=context
                )
        except Exception as e:
            self.logger.warning(f"Failed to generate workflow visualization: {e}")
        
        artifacts = {
            "workflow": workflow_result,
            "sop_id": sop_id
        }
        
        if visual_result and visual_result.get("success"):
            artifacts["workflow_visual"] = {
                "image_base64": visual_result.get("image_base64"),
                "storage_path": visual_result.get("storage_path")
            }
        
        return {
            "artifacts": artifacts,
            "events": [
                {
                    "type": "workflow_created",
                    "sop_id": sop_id,
                    "workflow_id": workflow_result.get("workflow_id")
                }
            ]
        }
    
    async def _handle_analyze_coexistence(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle analyze_coexistence intent."""
        workflow_id = intent.parameters.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required for analyze_coexistence intent")
        
        # Analyze coexistence via CoexistenceAnalysisService
        analysis_result = await self.coexistence_analysis_service.analyze_coexistence(
            workflow_id=workflow_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "coexistence_analysis": analysis_result,
                "workflow_id": workflow_id
            },
            "events": [
                {
                    "type": "coexistence_analyzed",
                    "workflow_id": workflow_id
                }
            ]
        }
    
    async def _handle_create_blueprint(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle create_blueprint intent."""
        workflow_id = intent.parameters.get("workflow_id")
        if not workflow_id:
            raise ValueError("workflow_id is required for create_blueprint intent")
        
        # Create blueprint via CoexistenceAnalysisService
        blueprint_result = await self.coexistence_analysis_service.create_blueprint(
            workflow_id=workflow_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "blueprint": blueprint_result,
                "workflow_id": workflow_id
            },
            "events": [
                {
                    "type": "blueprint_created",
                    "workflow_id": workflow_id
                }
            ]
        }
