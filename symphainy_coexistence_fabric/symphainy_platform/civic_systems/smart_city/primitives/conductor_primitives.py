"""
Conductor Primitives - Policy Decisions for Workflow and Saga

Primitives for Conductor policy decisions (used by Runtime only).
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from dataclasses import dataclass

from utilities import get_logger


@dataclass
class WorkflowTransitionValidation:
    """Workflow transition validation result."""
    is_valid: bool
    workflow_id: str
    from_state: str
    to_state: str
    reason: Optional[str] = None


@dataclass
class SagaConstraintsCheck:
    """Saga constraints check result."""
    is_valid: bool
    saga_id: str
    constraints: Dict[str, Any]
    reason: Optional[str] = None


class ConductorPrimitives:
    """
    Conductor Primitives - Policy Decisions
    
    Makes policy decisions for workflow and saga execution.
    """
    
    def __init__(self, policy_store: Optional[Any] = None):
        self.policy_store = policy_store
        self.logger = get_logger(self.__class__.__name__)
    
    async def validate_workflow_transition(
        self,
        workflow_id: str,
        from_state: str,
        to_state: str,
        tenant_id: str
    ) -> WorkflowTransitionValidation:
        """Validate workflow transition (policy decision)."""
        # MVP: Basic validation
        if not workflow_id:
            return WorkflowTransitionValidation(
                is_valid=False,
                workflow_id=workflow_id,
                from_state=from_state,
                to_state=to_state,
                reason="Workflow ID is required"
            )
        
        return WorkflowTransitionValidation(
            is_valid=True,
            workflow_id=workflow_id,
            from_state=from_state,
            to_state=to_state
        )
    
    async def check_saga_constraints(
        self,
        saga_id: str,
        constraints: Dict[str, Any],
        tenant_id: str
    ) -> SagaConstraintsCheck:
        """Check saga constraints (policy decision)."""
        # MVP: Basic validation
        if not saga_id:
            return SagaConstraintsCheck(
                is_valid=False,
                saga_id=saga_id,
                constraints=constraints,
                reason="Saga ID is required"
            )
        
        return SagaConstraintsCheck(
            is_valid=True,
            saga_id=saga_id,
            constraints=constraints
        )
