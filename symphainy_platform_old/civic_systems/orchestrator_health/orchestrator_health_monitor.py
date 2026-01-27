"""
Orchestrator Health Monitor - Monitor Orchestrator Health and Performance

Monitors orchestrator health, availability, and performance metrics.

WHAT (Health Monitor Role): I monitor orchestrator health and performance
HOW (Health Monitor Implementation): I track health metrics and provide health status

Key Principle: Orchestrators should be monitored for availability, performance, and resource usage.
"""

import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from utilities import get_logger
from symphainy_platform.civic_systems.agentic.telemetry.agentic_telemetry_service import (
    AgenticTelemetryService
)


class OrchestratorHealthMonitor:
    """
    Orchestrator Health Monitor - Monitor orchestrator health and performance.
    
    Provides:
    - Health status tracking
    - Performance metrics
    - Availability monitoring
    - Intent handling metrics
    """
    
    def __init__(
        self,
        telemetry_service: Optional[AgenticTelemetryService] = None
    ):
        """
        Initialize Orchestrator Health Monitor.
        
        Args:
            telemetry_service: Optional telemetry service for metrics
        """
        self.logger = get_logger(self.__class__.__name__)
        self.telemetry_service = telemetry_service
        self._monitored_orchestrators: Dict[str, Dict[str, Any]] = {}  # orchestrator_id -> health data
    
    async def start_monitoring(self, orchestrator_id: str):
        """
        Start monitoring an orchestrator.
        
        Args:
            orchestrator_id: Orchestrator identifier (e.g., "insights_orchestrator")
        """
        if orchestrator_id not in self._monitored_orchestrators:
            self._monitored_orchestrators[orchestrator_id] = {
                "status": "monitoring",
                "started_at": datetime.utcnow().isoformat(),
                "last_health_check": None,
                "health_history": [],
                "intent_counts": {}  # intent_type -> count
            }
            self.logger.info(f"Started monitoring orchestrator: {orchestrator_id}")
    
    async def get_health(self, orchestrator_id: str) -> Dict[str, Any]:
        """
        Get orchestrator health status.
        
        Args:
            orchestrator_id: Orchestrator identifier
        
        Returns:
            Dict with health status:
            {
                "status": str,  # "healthy", "degraded", "unhealthy", "unknown"
                "availability": float,  # 0.0-1.0
                "performance": Dict[str, Any],
                "last_check": str,
                "metrics": Dict[str, Any],
                "intent_counts": Dict[str, int]
            }
        """
        if orchestrator_id not in self._monitored_orchestrators:
            return {
                "status": "unknown",
                "availability": 0.0,
                "performance": {},
                "last_check": None,
                "metrics": {},
                "intent_counts": {}
            }
        
        # Get recent metrics from telemetry
        metrics = {}
        if self.telemetry_service:
            # Get metrics for last 24 hours
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            metrics = await self.telemetry_service.get_orchestrator_metrics(
                orchestrator_id=orchestrator_id,
                time_range=(start_time, end_time)
            )
        
        # Determine health status
        status = "healthy"
        if metrics:
            success_rate = metrics.get("success_rate", 1.0)
            error_rate = metrics.get("error_rate", 0.0)
            
            if error_rate > 0.5:
                status = "unhealthy"
            elif error_rate > 0.1:
                status = "degraded"
            else:
                status = "healthy"
        
        # Calculate availability (based on execution count)
        availability = 1.0
        if metrics and metrics.get("intent_count", 0) > 0:
            # Availability is based on success rate
            availability = metrics.get("success_rate", 1.0)
        
        # Update monitored orchestrator
        orchestrator_data = self._monitored_orchestrators[orchestrator_id]
        orchestrator_data["last_health_check"] = datetime.utcnow().isoformat()
        orchestrator_data["status"] = status
        
        return {
            "status": status,
            "availability": availability,
            "performance": {
                "avg_latency_ms": metrics.get("avg_latency_ms", 0.0),
                "total_intents": metrics.get("intent_count", 0),
                "success_rate": metrics.get("success_rate", 1.0),
                "error_rate": metrics.get("error_rate", 0.0)
            },
            "last_check": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "intent_counts": orchestrator_data.get("intent_counts", {})
        }
    
    async def record_intent_handled(
        self,
        orchestrator_id: str,
        intent_type: str,
        success: bool,
        latency_ms: float
    ):
        """
        Record intent handling metric.
        
        Args:
            orchestrator_id: Orchestrator identifier
            intent_type: Intent type (e.g., "interpret_data")
            success: Whether intent was handled successfully
            latency_ms: Latency in milliseconds
        """
        if orchestrator_id not in self._monitored_orchestrators:
            await self.start_monitoring(orchestrator_id)
        
        orchestrator_data = self._monitored_orchestrators[orchestrator_id]
        
        # Update intent counts
        if "intent_counts" not in orchestrator_data:
            orchestrator_data["intent_counts"] = {}
        
        intent_counts = orchestrator_data["intent_counts"]
        if intent_type not in intent_counts:
            intent_counts[intent_type] = {"total": 0, "success": 0, "failed": 0, "total_latency_ms": 0.0}
        
        intent_counts[intent_type]["total"] += 1
        if success:
            intent_counts[intent_type]["success"] += 1
        else:
            intent_counts[intent_type]["failed"] += 1
        intent_counts[intent_type]["total_latency_ms"] += latency_ms
    
    async def record_health_status(
        self,
        orchestrator_id: str,
        orchestrator_name: str,
        health_status: Dict[str, Any],
        tenant_id: Optional[str] = None
    ):
        """
        Record health status to telemetry.
        
        Args:
            orchestrator_id: Orchestrator identifier
            orchestrator_name: Orchestrator name
            health_status: Health status dictionary
            tenant_id: Optional tenant identifier
        """
        if self.telemetry_service:
            await self.telemetry_service.record_orchestrator_health(
                orchestrator_id=orchestrator_id,
                orchestrator_name=orchestrator_name,
                health_status=health_status,
                tenant_id=tenant_id
            )
    
    async def get_all_health_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get health status for all monitored orchestrators.
        
        Returns:
            Dict mapping orchestrator_id -> health status
        """
        statuses = {}
        for orchestrator_id in self._monitored_orchestrators.keys():
            statuses[orchestrator_id] = await self.get_health(orchestrator_id)
        return statuses
