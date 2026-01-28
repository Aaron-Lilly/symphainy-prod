"""
Agent Health Monitor - Monitor Agent Health and Performance

Monitors agent health, availability, and performance metrics.

WHAT (Health Monitor Role): I monitor agent health and performance
HOW (Health Monitor Implementation): I track health metrics and provide health status

Key Principle: Agents should be monitored for availability, performance, and resource usage.
"""

import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
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


class AgentHealthMonitor:
    """
    Agent Health Monitor - Monitor agent health and performance.
    
    Provides:
    - Health status tracking
    - Performance metrics
    - Availability monitoring
    - Resource usage tracking
    """
    
    def __init__(
        self,
        telemetry_service: Optional[AgenticTelemetryService] = None
    ):
        """
        Initialize Agent Health Monitor.
        
        Args:
            telemetry_service: Optional telemetry service for metrics
        """
        self.logger = get_logger(self.__class__.__name__)
        self.telemetry_service = telemetry_service
        self._monitored_agents: Dict[str, Dict[str, Any]] = {}  # agent_id -> health data
    
    async def start_monitoring(self, agent_id: str):
        """
        Start monitoring an agent.
        
        Args:
            agent_id: Agent identifier
        """
        if agent_id not in self._monitored_agents:
            self._monitored_agents[agent_id] = {
                "status": "monitoring",
                "started_at": datetime.utcnow().isoformat(),
                "last_health_check": None,
                "health_history": []
            }
            self.logger.info(f"Started monitoring agent: {agent_id}")
    
    async def get_health(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent health status.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Dict with health status:
            {
                "status": str,  # "healthy", "degraded", "unhealthy", "unknown"
                "availability": float,  # 0.0-1.0
                "performance": Dict[str, Any],
                "last_check": str,
                "metrics": Dict[str, Any]
            }
        """
        if agent_id not in self._monitored_agents:
            return {
                "status": "unknown",
                "availability": 0.0,
                "performance": {},
                "last_check": None,
                "metrics": {}
            }
        
        # Get recent metrics from telemetry
        metrics = {}
        if self.telemetry_service:
            # Get metrics for last 24 hours
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            metrics = await self.telemetry_service.get_agent_metrics(
                agent_id=agent_id,
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
        if metrics and metrics.get("execution_count", 0) > 0:
            # Availability is based on success rate
            availability = metrics.get("success_rate", 1.0)
        
        # Update monitored agent
        self._monitored_agents[agent_id]["last_health_check"] = datetime.utcnow().isoformat()
        self._monitored_agents[agent_id]["status"] = status
        
        return {
            "status": status,
            "availability": availability,
            "performance": {
                "avg_latency_ms": metrics.get("avg_latency_ms", 0.0),
                "total_executions": metrics.get("execution_count", 0),
                "success_rate": metrics.get("success_rate", 1.0)
            },
            "last_check": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
    
    async def record_health_metric(
        self,
        agent_id: str,
        metric_name: str,
        value: float
    ):
        """
        Record health metric.
        
        Args:
            agent_id: Agent identifier
            metric_name: Metric name
            value: Metric value
        """
        if agent_id not in self._monitored_agents:
            await self.start_monitoring(agent_id)
        
        if "health_history" not in self._monitored_agents[agent_id]:
            self._monitored_agents[agent_id]["health_history"] = []
        
        self._monitored_agents[agent_id]["health_history"].append({
            "metric_name": metric_name,
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 100 metrics
        if len(self._monitored_agents[agent_id]["health_history"]) > 100:
            self._monitored_agents[agent_id]["health_history"] = \
                self._monitored_agents[agent_id]["health_history"][-100:]
    
    async def record_health_status(
        self,
        agent_id: str,
        agent_name: str,
        health_status: Dict[str, Any],
        tenant_id: Optional[str] = None
    ):
        """
        Record health status to telemetry.
        
        Args:
            agent_id: Agent identifier
            agent_name: Agent name
            health_status: Health status dictionary
            tenant_id: Optional tenant identifier
        """
        if self.telemetry_service:
            await self.telemetry_service.record_agent_health(
                agent_id=agent_id,
                agent_name=agent_name,
                health_status=health_status,
                tenant_id=tenant_id
            )
