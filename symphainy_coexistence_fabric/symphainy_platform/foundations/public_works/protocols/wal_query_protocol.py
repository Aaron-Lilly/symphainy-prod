"""
WAL Query Protocol - Abstraction Contract (Layer 2)

Defines the contract for querying the write-ahead log (execution events) for
metrics aggregation. Used by GetExecutionMetricsService and Control Room dashboard.

Implementations use EventLogProtocol (get_wal_backend()) inside Public Works; no adapter at boundary.

WHAT (Infrastructure Role): I define the contract for WAL query / execution metrics
HOW (Infrastructure Implementation): Implementations wrap event log backend; aggregate by event type and time
"""

from typing import Protocol, Dict, Any, Optional, List


class WALQueryProtocol(Protocol):
    """
    Protocol for querying WAL and aggregating execution metrics.

    GetExecutionMetricsService uses this via get_wal_query_interface() (or ctx).
    Implementations use EventLogProtocol (e.g. Redis Streams) inside Public Works only.
    """

    async def get_execution_metrics(
        self,
        tenant_id: Optional[str] = None,
        time_range: str = "1h",
    ) -> Dict[str, Any]:
        """
        Aggregate execution metrics from WAL for the given tenant and time range.

        Args:
            tenant_id: Optional tenant filter (None = all tenants or default)
            time_range: Time range (e.g. "1h", "24h", "7d")

        Returns:
            Dict with at least: total_intents, successful_intents, failed_intents,
            success_rate, average_execution_time_ms, intent_distribution, error_rate,
            timestamp, time_range
        """
        ...

    async def query_events(
        self,
        tenant_id: str,
        start_iso: Optional[str] = None,
        end_iso: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query raw WAL events (optional; for debugging or custom aggregation).

        Args:
            tenant_id: Tenant identifier
            start_iso: Start time (ISO format)
            end_iso: End time (ISO format)
            event_types: Optional filter by event type
            limit: Max events to return

        Returns:
            List of event dicts (event_id, event_type, tenant_id, timestamp, payload)
        """
        ...
