"""
Conductor SDK - Workflow and Saga Coordination

SDK for Conductor coordination (used by Experience, Solution, Realms).
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from utilities import get_logger, get_clock


@dataclass
class WorkflowRequest:
    """Workflow request with execution contract."""
    workflow_id: str
    workflow_definition: Dict[str, Any]
    execution_contract: Dict[str, Any]


@dataclass
class SagaStepRequest:
    """Saga step request with execution contract."""
    saga_id: str
    step_name: str
    step_data: Dict[str, Any]
    execution_contract: Dict[str, Any]


class ConductorSDK:
    """
    Conductor SDK - Coordination Logic
    
    Coordinates workflow and saga execution.
    """
    
    def __init__(
        self,
        workflow_abstraction: Optional[Any] = None,
        policy_resolver: Optional[Any] = None
    ):
        self.workflow_abstraction = workflow_abstraction
        self.policy_resolver = policy_resolver
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def create_workflow(
        self,
        workflow_definition: Dict[str, Any],
        tenant_id: str,
        solution_id: str
    ) -> WorkflowRequest:
        """Create workflow (prepare workflow contract)."""
        execution_contract = {
            "action": "create_workflow",
            "workflow_definition": workflow_definition,
            "tenant_id": tenant_id,
            "solution_id": solution_id,
            "timestamp": self.clock.now_iso()
        }
        
        return WorkflowRequest(
            workflow_id=f"workflow_{self.clock.now_iso()}",
            workflow_definition=workflow_definition,
            execution_contract=execution_contract
        )
    
    async def execute_saga_step(
        self,
        saga_id: str,
        step_name: str,
        step_data: Dict[str, Any],
        tenant_id: str
    ) -> SagaStepRequest:
        """Execute saga step (prepare saga contract)."""
        execution_contract = {
            "action": "execute_saga_step",
            "saga_id": saga_id,
            "step_name": step_name,
            "step_data": step_data,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return SagaStepRequest(
            saga_id=saga_id,
            step_name=step_name,
            step_data=step_data,
            execution_contract=execution_contract
        )
    
    async def get_workflow_state(
        self,
        workflow_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get workflow state (prepare state contract)."""
        execution_contract = {
            "action": "get_workflow_state",
            "workflow_id": workflow_id,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return {
            "workflow_id": workflow_id,
            "state": "unknown",
            "execution_contract": execution_contract
        }
