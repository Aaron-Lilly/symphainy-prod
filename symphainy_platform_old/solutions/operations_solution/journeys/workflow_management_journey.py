"""
Workflow Management Journey Orchestrator

Composes workflow management operations into a coherent user journey.

WHAT (Journey Role): I compose workflow management operations
HOW (Journey Implementation): I orchestrate CreateWorkflowService calls
    and expose SOA APIs for MCP server

Architecture:
- Journey is thin composer (delegates to intent services)
- Uses CreateWorkflowService from Operations Realm
- Exposes create_workflow SOA API
- Records telemetry and journey execution
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utilities import get_logger, generate_event_id
from symphainy_platform.bases.orchestrator_base import BaseOrchestrator
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_coexistence_fabric.symphainy_platform.realms.operations import CreateWorkflowService


class WorkflowManagementJourney(BaseOrchestrator):
    """
    Workflow Management Journey Orchestrator.
    
    Composes:
    - CreateWorkflowService for workflow creation
    
    SOA APIs:
    - create_workflow: Create workflow from SOP or BPMN
    """
    
    JOURNEY_ID = "journey_operations_workflow_management"
    
    def __init__(self, public_works=None, state_surface=None):
        """Initialize WorkflowManagementJourney."""
        super().__init__(
            orchestrator_id="workflow_management_journey",
            public_works=public_works
        )
        self.state_surface = state_surface
        
        # Initialize intent services
        self.create_workflow_service = CreateWorkflowService(
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def compose_journey(
        self,
        journey_id: str,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose workflow management journey.
        
        Args:
            journey_id: The journey being composed
            context: Execution context
            journey_params: Journey-specific parameters
            
        Returns:
            Dict with artifacts and events
        """
        journey_execution_id = f"wf_journey_{generate_event_id()}"
        start_time = datetime.utcnow()
        
        self.logger.info(f"Starting workflow management journey: {journey_execution_id}")
        
        try:
            params = journey_params or {}
            
            if journey_id in ["workflow_management", "create_workflow"]:
                result = await self.create_workflow_service.execute(context, params)
            else:
                raise ValueError(f"Unknown journey_id: {journey_id}")
            
            # Record telemetry
            end_time = datetime.utcnow()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            await self.record_telemetry(
                telemetry_data={
                    "journey_id": journey_id,
                    "journey_execution_id": journey_execution_id,
                    "latency_ms": latency_ms,
                    "status": "completed"
                },
                tenant_id=context.tenant_id
            )
            
            # Add journey metadata
            result["journey_execution_id"] = journey_execution_id
            result["journey_id"] = self.JOURNEY_ID
            
            return result
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={
                    "journey_id": journey_id,
                    "journey_execution_id": journey_execution_id,
                    "status": "failed",
                    "error": str(e)
                },
                tenant_id=context.tenant_id
            )
            raise
    
    def get_soa_apis(self) -> Dict[str, Callable]:
        """Get SOA APIs for this journey."""
        return {
            "create_workflow": self._handle_create_workflow_soa
        }
    
    async def _handle_create_workflow_soa(
        self,
        context: ExecutionContext,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """SOA API handler for create_workflow."""
        return await self.compose_journey(
            journey_id="create_workflow",
            context=context,
            journey_params=params
        )
