"""Get Execution Metrics Service (Platform SDK)

Returns execution metrics for the Control Room dashboard.
Uses WALQueryProtocol via ctx.platform.get_wal_query_interface() when available.
"""

from typing import Dict, Any
from datetime import datetime
from utilities import get_logger, generate_event_id
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext


class GetExecutionMetricsService(PlatformIntentService):
    """Get Execution Metrics Service using Platform SDK."""
    
    intent_type = "get_execution_metrics"
    
    def __init__(self, service_id: str = "get_execution_metrics_service"):
        super().__init__(service_id=service_id, intent_type="get_execution_metrics")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        self.logger.info(f"Executing get_execution_metrics: {ctx.execution_id}")
        
        params = getattr(ctx.intent, "parameters", None) or ctx.parameters or {}
        time_range = params.get("time_range", "1h")
        tenant_id = getattr(ctx, "tenant_id", None)

        wal_query = None
        if ctx.platform and hasattr(ctx.platform, "get_wal_query_interface"):
            wal_query = ctx.platform.get_wal_query_interface()

        if wal_query and hasattr(wal_query, "get_execution_metrics"):
            try:
                metrics = await wal_query.get_execution_metrics(
                    tenant_id=tenant_id,
                    time_range=time_range,
                )
                metrics["metrics_id"] = generate_event_id()
                return {"artifacts": {"metrics": metrics}, "events": []}
            except Exception as e:
                self.logger.warning(f"WAL query failed, returning placeholder: {e}")

        created_at = getattr(ctx, "created_at", None)
        metrics = {
            "metrics_id": generate_event_id(),
            "time_range": time_range,
            "timestamp": created_at.isoformat() if created_at else datetime.utcnow().isoformat(),
            "total_intents": 0,
            "successful_intents": 0,
            "failed_intents": 0,
            "success_rate": 0.0,
            "average_execution_time_ms": 0.0,
            "intent_distribution": {},
            "error_rate": 0.0,
            "note": "WAL query interface not available or failed; provide Redis and tenant_id for real metrics",
        }
        return {"artifacts": {"metrics": metrics}, "events": []}
