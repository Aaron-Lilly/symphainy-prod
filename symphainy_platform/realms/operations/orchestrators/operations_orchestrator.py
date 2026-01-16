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
        """Handle create_workflow intent."""
        sop_id = intent.parameters.get("sop_id")
        if not sop_id:
            raise ValueError("sop_id is required for create_workflow intent")
        
        # Create workflow via WorkflowConversionService
        workflow_result = await self.workflow_conversion_service.create_workflow(
            sop_id=sop_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "workflow": workflow_result,
                "sop_id": sop_id
            },
            "events": [
                {
                    "type": "workflow_created",
                    "sop_id": sop_id
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
