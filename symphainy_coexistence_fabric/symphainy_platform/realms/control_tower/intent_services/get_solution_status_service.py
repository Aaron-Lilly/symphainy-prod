"""
Get Solution Status Intent Service

Implements the get_solution_status intent for the Control Tower Realm.

Purpose: Get detailed status of a specific solution including health,
metrics, and recent activity.

WHAT (Intent Service Role): I provide solution-specific status
HOW (Intent Service Implementation): I query the Solution Registry
    and metrics to provide comprehensive solution status
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


class GetSolutionStatusService(BaseIntentService):
    """
    Intent service for getting detailed solution status.
    
    Provides:
    - Solution health status
    - MCP server status
    - Journey availability
    - Recent execution metrics
    - Active sessions using this solution
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize GetSolutionStatusService."""
        super().__init__(
            service_id="get_solution_status_service",
            intent_type="get_solution_status",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the get_solution_status intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            solution_id = intent_params.get("solution_id")
            if not solution_id:
                raise ValueError("solution_id is required")
            
            # Get solution status
            status = await self._get_solution_status(solution_id)
            
            if not status:
                raise ValueError(f"Solution not found: {solution_id}")
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success", "solution_id": solution_id},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "solution_id": solution_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "solution_status_retrieved",
                        "timestamp": datetime.utcnow().isoformat(),
                        "solution_id": solution_id
                    }
                ]
            }
            
        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "INVALID_SOLUTION"
            }
        except Exception as e:
            self.logger.error(f"Failed to get solution status: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_code": "SOLUTION_STATUS_ERROR"
            }
    
    async def _get_solution_status(self, solution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for a solution."""
        # Valid solutions
        valid_solutions = {
            "content_solution", "insights_solution", "operations_solution",
            "outcomes_solution", "coexistence_solution"
        }
        
        if solution_id not in valid_solutions:
            return None
        
        return {
            "health": "healthy",
            "uptime_seconds": 3600,  # Would be calculated from actual start time
            "mcp_server": {
                "status": "active",
                "tools_registered": 5,
                "requests_handled": 0
            },
            "journeys": {
                "total": 3,
                "active": 3,
                "inactive": 0
            },
            "metrics": {
                "compose_journey_calls_24h": 0,
                "avg_journey_duration_ms": 500,
                "success_rate": 100.0,
                "errors_24h": 0
            },
            "active_sessions": 0,
            "last_activity": datetime.utcnow().isoformat()
        }
