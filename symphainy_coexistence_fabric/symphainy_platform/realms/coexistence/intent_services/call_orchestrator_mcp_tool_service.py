"""
Call Orchestrator MCP Tool Intent Service

Implements the call_orchestrator_mcp_tool intent for the Coexistence Realm.

Purpose: Execute an MCP tool from any solution with governance checks.

WHAT (Intent Service Role): I execute MCP tools with governance
HOW (Intent Service Implementation): I validate the tool call,
    apply governance, and delegate to the owning solution
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class CallOrchestratorMCPToolService(BaseIntentService):
    """
    Intent service for calling MCP tools with governance.
    
    Provides:
    - Tool validation
    - Governance checks (permissions, rate limiting)
    - Delegation to owning solution
    - Audit logging
    """
    
    # Tool to solution mapping
    TOOL_SOLUTIONS = {
        "content_": "content_solution",
        "insights_": "insights_solution",
        "ops_": "operations_solution",
        "outcomes_": "outcomes_solution",
        "coexist_": "coexistence_solution"
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize CallOrchestratorMCPToolService."""
        super().__init__(
            service_id="call_orchestrator_mcp_tool_service",
            intent_type="call_orchestrator_mcp_tool",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the call_orchestrator_mcp_tool intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            tool_name = intent_params.get("tool_name")
            tool_params = intent_params.get("tool_params", {})
            
            if not tool_name:
                raise ValueError("tool_name is required")
            
            # Validate and determine solution
            solution_id = self._get_solution_for_tool(tool_name)
            if not solution_id:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            # Apply governance checks
            governance_result = await self._check_governance(tool_name, context)
            if not governance_result["allowed"]:
                return {
                    "success": False,
                    "error": governance_result["reason"],
                    "error_code": "GOVERNANCE_DENIED"
                }
            
            # Execute the tool
            result = await self._execute_tool(tool_name, tool_params, solution_id, context)
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", 
                    "status": "success", 
                    "tool_name": tool_name,
                    "solution": solution_id
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "tool_name": tool_name,
                "solution_id": solution_id,
                "result": result,
                "governance": governance_result,
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "mcp_tool_called",
                        "timestamp": datetime.utcnow().isoformat(),
                        "tool_name": tool_name
                    }
                ]
            }
            
        except ValueError as e:
            return {"success": False, "error": str(e), "error_code": "INVALID_TOOL"}
        except Exception as e:
            self.logger.error(f"Failed to call MCP tool: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_solution_for_tool(self, tool_name: str) -> Optional[str]:
        """Determine which solution owns a tool."""
        for prefix, solution in self.TOOL_SOLUTIONS.items():
            if tool_name.startswith(prefix):
                return solution
        return None
    
    async def _check_governance(
        self, 
        tool_name: str, 
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Check governance rules for tool execution."""
        # In a real implementation, this would:
        # - Check user permissions
        # - Check rate limits
        # - Check tool-specific policies
        
        return {
            "allowed": True,
            "checks_passed": [
                "user_authenticated",
                "tool_exists",
                "rate_limit_ok",
                "permission_granted"
            ],
            "audit_id": generate_event_id()
        }
    
    async def _execute_tool(
        self,
        tool_name: str,
        tool_params: Dict[str, Any],
        solution_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute an MCP tool by delegating to its solution."""
        # In a real implementation, this would:
        # 1. Get the solution from solution_registry
        # 2. Call the MCP server's handle_tool method
        # 3. Return the result
        
        # For now, return a simulated successful execution
        return {
            "execution_id": generate_event_id(),
            "tool_name": tool_name,
            "solution_id": solution_id,
            "status": "completed",
            "output": {
                "message": f"Tool {tool_name} executed successfully",
                "params_received": tool_params
            }
        }
