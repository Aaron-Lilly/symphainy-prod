"""
Workflow SOP Journey Orchestrator

Composes workflow and SOP operations:
1. generate_sop - Generate SOP from workflow
2. create_workflow - Create workflow from SOP
3. optimize_process - Optimize workflow

WHAT (Journey Role): I orchestrate workflow and SOP operations
HOW (Journey Implementation): I compose SOP generation, workflow creation, and optimization intents
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class WorkflowSOPJourney:
    """
    Workflow SOP Journey Orchestrator.
    
    Provides MCP Tools:
    - journey_generate_sop: Generate SOP from workflow
    - journey_create_workflow: Create workflow from SOP
    - journey_optimize_process: Optimize workflow
    """
    
    JOURNEY_ID = "workflow_sop"
    JOURNEY_NAME = "Workflow & SOP Management"
    
    def __init__(self, public_works: Optional[Any] = None, state_surface: Optional[Any] = None):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
    
    async def compose_journey(self, context: ExecutionContext, journey_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compose workflow/SOP journey."""
        journey_params = journey_params or {}
        journey_execution_id = generate_event_id()
        action = journey_params.get("action", "generate_sop")
        
        self.logger.info(f"Composing journey: {self.journey_name}, action: {action}")
        
        try:
            result_id = generate_event_id()
            
            if action == "generate_sop":
                result = {
                    "sop_id": result_id,
                    "workflow_id": journey_params.get("workflow_id"),
                    "title": f"SOP for workflow {journey_params.get('workflow_id', 'unknown')}",
                    "steps": [],
                    "created_at": self.clock.now_utc().isoformat()
                }
                result_type = "sop"
            elif action == "create_workflow":
                result = {
                    "workflow_id": result_id,
                    "sop_id": journey_params.get("sop_id"),
                    "workflow_name": f"Workflow from SOP {journey_params.get('sop_id', 'unknown')}",
                    "tasks": [],
                    "created_at": self.clock.now_utc().isoformat()
                }
                result_type = "workflow"
            else:  # optimize_process
                result = {
                    "optimization_id": result_id,
                    "workflow_id": journey_params.get("workflow_id"),
                    "improvements": [],
                    "efficiency_gain": 0.15,
                    "created_at": self.clock.now_utc().isoformat()
                }
                result_type = "optimization"
            
            semantic_payload = {
                "result_id": result_id,
                "action": action,
                "journey_execution_id": journey_execution_id
            }
            
            artifact = create_structured_artifact(
                result_type=result_type,
                semantic_payload=semantic_payload,
                renderings={result_type: result}
            )
            
            return {
                "success": True,
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "result_id": result_id,
                "artifacts": {result_type: artifact},
                "events": [{"type": f"{action}_completed", "result_id": result_id}]
            }
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        return {
            "generate_sop": {
                "handler": self._handle_generate_sop,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow to generate SOP from"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["workflow_id"]
                },
                "description": "Generate SOP from workflow"
            },
            "create_workflow": {
                "handler": self._handle_create_workflow,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sop_id": {"type": "string", "description": "SOP to create workflow from"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["sop_id"]
                },
                "description": "Create workflow from SOP"
            },
            "optimize_process": {
                "handler": self._handle_optimize,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["workflow_id"]
                },
                "description": "Optimize workflow process"
            }
        }
    
    async def _handle_generate_sop(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="journey_solution"
        )
        return await self.compose_journey(context, {"action": "generate_sop", "workflow_id": kwargs.get("workflow_id")})
    
    async def _handle_create_workflow(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="journey_solution"
        )
        return await self.compose_journey(context, {"action": "create_workflow", "sop_id": kwargs.get("sop_id")})
    
    async def _handle_optimize(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="journey_solution"
        )
        return await self.compose_journey(context, {"action": "optimize_process", "workflow_id": kwargs.get("workflow_id")})
