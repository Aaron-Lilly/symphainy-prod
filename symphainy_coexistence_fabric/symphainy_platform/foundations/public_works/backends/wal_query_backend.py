"""
WAL Query Backend - WALQueryProtocol implementation

Implements WALQueryProtocol using EventLogProtocol (e.g. Redis Streams).
Used by GetExecutionMetricsService via get_wal_query_interface().
Lives inside Public Works; callers receive only WALQueryProtocol.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta
import json

from utilities import get_logger, get_clock
from ..protocols.event_log_protocol import EventLogProtocol


def _stream_name(tenant_id: str, d: date) -> str:
    """Stream name convention: wal:{tenant_id}:{date} (must match runtime/wal.py)."""
    return f"wal:{tenant_id}:{d.isoformat()}"


class WalQueryBackend:
    """
    WALQueryProtocol implementation using EventLogProtocol.

    Queries WAL streams (wal:tenant_id:date) and aggregates execution metrics.
    Created by foundation_service when WAL backend is available; exposed via get_wal_query_interface().
    """

    def __init__(self, event_log: EventLogProtocol):
        self._event_log = event_log
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()

    async def get_execution_metrics(
        self,
        tenant_id: Optional[str] = None,
        time_range: str = "1h",
    ) -> Dict[str, Any]:
        """
        Aggregate execution metrics from WAL. When tenant_id is provided and backend is wired,
        scans relevant streams; otherwise returns placeholder structure.
        """
        if not self._event_log:
            return self._placeholder_metrics(time_range)

        if not tenant_id:
            # Cannot enumerate streams without tenant_id (Redis has no stream list by prefix)
            self.logger.debug("get_execution_metrics called without tenant_id; returning placeholder")
            return self._placeholder_metrics(time_range)

        try:
            return await self._aggregate_metrics(tenant_id, time_range)
        except Exception as e:
            self.logger.warning(f"WAL aggregation failed, returning placeholder: {e}")
            return self._placeholder_metrics(time_range)

    def _placeholder_metrics(self, time_range: str) -> Dict[str, Any]:
        """Placeholder structure for MVP or when backend/tenant unavailable."""
        return {
            "time_range": time_range,
            "timestamp": self.clock.now_utc().isoformat(),
            "total_intents": 0,
            "successful_intents": 0,
            "failed_intents": 0,
            "success_rate": 0.0,
            "average_execution_time_ms": 0.0,
            "intent_distribution": {},
            "error_rate": 0.0,
            "note": "Real metrics when WAL query is wired with tenant_id and time range",
        }

    async def _aggregate_metrics(self, tenant_id: str, time_range: str) -> Dict[str, Any]:
        """Aggregate from WAL streams for tenant and time range."""
        # Parse time range (e.g. 1h, 24h, 7d)
        now = self.clock.now_utc()
        start = now
        if time_range == "1h":
            start = now - timedelta(hours=1)
        elif time_range == "24h":
            start = now - timedelta(days=1)
        elif time_range == "7d":
            start = now - timedelta(days=7)
        else:
            try:
                if time_range.endswith("h"):
                    start = now - timedelta(hours=int(time_range[:-1]))
                elif time_range.endswith("d"):
                    start = now - timedelta(days=int(time_range[:-1]))
            except (ValueError, AttributeError):
                pass

        total_intents = 0
        successful_intents = 0
        failed_intents = 0
        intent_distribution: Dict[str, int] = {}
        execution_times_ms: List[float] = []

        current = start.date()
        end_date = now.date()
        while current <= end_date:
            stream_name = _stream_name(tenant_id, current)
            try:
                entries = await self._event_log.xrange(
                    stream_name, start="-", end="+", count=5000
                )
                for _msg_id, fields in entries:
                    event_type = fields.get("event_type", "")
                    payload_str = fields.get("payload", "{}")
                    try:
                        payload = json.loads(payload_str) if isinstance(payload_str, str) else payload_str
                    except Exception:
                        payload = {}
                    intent_distribution[event_type] = intent_distribution.get(event_type, 0) + 1
                    if event_type in ("intent_received", "execution_started"):
                        total_intents += 1
                    if event_type == "execution_completed":
                        successful_intents += 1
                        if isinstance(payload.get("duration_ms"), (int, float)):
                            execution_times_ms.append(float(payload["duration_ms"]))
                    if event_type == "execution_failed":
                        failed_intents += 1
            except Exception as e:
                self.logger.debug(f"No stream or error for {stream_name}: {e}")
            current += timedelta(days=1)

        avg_ms = sum(execution_times_ms) / len(execution_times_ms) if execution_times_ms else 0.0
        success_rate = (successful_intents / total_intents) if total_intents else 0.0
        error_rate = (failed_intents / total_intents) if total_intents else 0.0

        return {
            "time_range": time_range,
            "timestamp": now.isoformat(),
            "total_intents": total_intents,
            "successful_intents": successful_intents,
            "failed_intents": failed_intents,
            "success_rate": round(success_rate, 4),
            "average_execution_time_ms": round(avg_ms, 2),
            "intent_distribution": intent_distribution,
            "error_rate": round(error_rate, 4),
            "note": None,
        }

    async def query_events(
        self,
        tenant_id: str,
        start_iso: Optional[str] = None,
        end_iso: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query raw WAL events from streams for tenant and optional time/type filter."""
        if not self._event_log:
            return []

        try:
            start_date = datetime.fromisoformat(start_iso.replace("Z", "+00:00")).date() if start_iso else self.clock.now_utc().date()
            end_date = datetime.fromisoformat(end_iso.replace("Z", "+00:00")).date() if end_iso else start_date
        except Exception:
            start_date = end_date = self.clock.now_utc().date()

        out: List[Dict[str, Any]] = []
        current = start_date
        while current <= end_date and len(out) < limit:
            stream_name = _stream_name(tenant_id, current)
            try:
                entries = await self._event_log.xrange(
                    stream_name, start="-", end="+", count=limit - len(out)
                )
                for msg_id, fields in entries:
                    event_type = fields.get("event_type", "")
                    if event_types and event_type not in event_types:
                        continue
                    payload_str = fields.get("payload", "{}")
                    try:
                        payload = json.loads(payload_str) if isinstance(payload_str, str) else payload_str
                    except Exception:
                        payload = {}
                    out.append({
                        "event_id": fields.get("event_id", msg_id),
                        "event_type": event_type,
                        "tenant_id": fields.get("tenant_id", tenant_id),
                        "timestamp": fields.get("timestamp", ""),
                        "payload": payload,
                    })
                    if len(out) >= limit:
                        break
            except Exception as e:
                self.logger.debug(f"query_events stream {stream_name}: {e}")
            current += timedelta(days=1)

        return out[:limit]
