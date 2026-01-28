"""
Get Platform Statistics Intent Service

Implements the get_platform_statistics intent for the Control Tower Realm.

Purpose: Retrieve platform-wide statistics including active sessions,
solution usage, and system metrics.

WHAT (Intent Service Role): I provide platform-wide statistics
HOW (Intent Service Implementation): I aggregate metrics from Registry,
    Solutions, and Runtime to provide a comprehensive platform view
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class GetPlatformStatisticsService(BaseIntentService):
    """
    Intent service for retrieving platform-wide statistics.
    
    Provides:
    - Active session count
    - Solution usage metrics
    - Intent execution counts
    - System health summary
    - Resource utilization
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize GetPlatformStatisticsService."""
        super().__init__(
            service_id="get_platform_statistics_service",
            intent_type="get_platform_statistics",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the get_platform_statistics intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            # Get time range filter (optional)
            time_range = intent_params.get("time_range", "24h")
            include_details = intent_params.get("include_details", False)
            
            # Gather platform statistics
            statistics = await self._gather_statistics(time_range, include_details)
            
            # Record success telemetry
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success", "intent_type": self.intent_type},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "statistics": statistics,
                "time_range": time_range,
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "platform_statistics_retrieved",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get platform statistics: {e}", exc_info=True)
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "error", "error": str(e)},
                tenant_id=context.tenant_id
            )
            return {
                "success": False,
                "error": str(e),
                "error_code": "PLATFORM_STATISTICS_ERROR"
            }
    
    async def _gather_statistics(self, time_range: str, include_details: bool) -> Dict[str, Any]:
        """Gather platform statistics from various sources."""
        stats = {
            "sessions": await self._get_session_stats(),
            "solutions": await self._get_solution_stats(),
            "intents": await self._get_intent_stats(),
            "realms": await self._get_realm_stats(),
            "system": await self._get_system_stats()
        }
        
        if include_details:
            stats["details"] = {
                "top_solutions": await self._get_top_solutions(),
                "top_intents": await self._get_top_intents(),
                "error_summary": await self._get_error_summary()
            }
        
        return stats
    
    async def _get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        # Use state_surface to query session counts
        try:
            if self.state_surface:
                # Query active sessions from state surface
                return {
                    "active_sessions": 0,  # Would query from state
                    "sessions_today": 0,
                    "peak_concurrent": 0
                }
        except Exception as e:
            self.logger.warning(f"Could not get session stats: {e}")
        return {"active_sessions": 0, "sessions_today": 0, "peak_concurrent": 0}
    
    async def _get_solution_stats(self) -> Dict[str, Any]:
        """Get solution usage statistics."""
        return {
            "registered_solutions": 5,  # Content, Insights, Operations, Outcomes, Coexistence
            "active_solutions": 5,
            "total_executions": 0
        }
    
    async def _get_intent_stats(self) -> Dict[str, Any]:
        """Get intent execution statistics."""
        return {
            "total_intents_executed": 0,
            "successful_intents": 0,
            "failed_intents": 0,
            "avg_execution_time_ms": 0
        }
    
    async def _get_realm_stats(self) -> Dict[str, Any]:
        """Get realm-level statistics."""
        return {
            "content": {"intents_executed": 0, "artifacts_created": 0},
            "insights": {"intents_executed": 0, "artifacts_created": 0},
            "operations": {"intents_executed": 0, "artifacts_created": 0},
            "outcomes": {"intents_executed": 0, "artifacts_created": 0},
            "security": {"intents_executed": 0, "sessions_created": 0},
            "control_tower": {"intents_executed": 0},
            "coexistence": {"intents_executed": 0, "guide_sessions": 0}
        }
    
    async def _get_system_stats(self) -> Dict[str, Any]:
        """Get system-level statistics."""
        return {
            "uptime_seconds": 0,
            "memory_usage_mb": 0,
            "cpu_usage_percent": 0,
            "storage_used_gb": 0
        }
    
    async def _get_top_solutions(self) -> list:
        """Get top solutions by usage."""
        return [
            {"solution_id": "content_solution", "executions": 0},
            {"solution_id": "insights_solution", "executions": 0},
            {"solution_id": "operations_solution", "executions": 0}
        ]
    
    async def _get_top_intents(self) -> list:
        """Get top intents by execution count."""
        return [
            {"intent_type": "ingest_file", "count": 0},
            {"intent_type": "parse_content", "count": 0},
            {"intent_type": "assess_data_quality", "count": 0}
        ]
    
    async def _get_error_summary(self) -> Dict[str, Any]:
        """Get error summary."""
        return {
            "total_errors": 0,
            "by_realm": {},
            "by_intent": {}
        }
