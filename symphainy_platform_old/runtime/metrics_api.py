"""
Metrics API - Metrics Dashboard Endpoints

API endpoints for metrics dashboard (admin dashboard feature).

WHAT (API Role): I provide metrics data for dashboard
HOW (API Implementation): I aggregate telemetry data and return metrics
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

from fastapi import APIRouter, HTTPException, Depends, Query
from starlette.requests import Request
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from utilities import get_logger
from symphainy_platform.civic_systems.agentic.telemetry.agentic_telemetry_service import AgenticTelemetryService
from symphainy_platform.civic_systems.agentic.health.agent_health_monitor import AgentHealthMonitor
from symphainy_platform.civic_systems.orchestrator_health import OrchestratorHealthMonitor

logger = get_logger("MetricsAPI")

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])


# Request/Response Models
class MetricsRequest(BaseModel):
    """Request model for metrics."""
    tenant_id: Optional[str] = None
    time_range_hours: Optional[int] = 24  # Default to last 24 hours


class AgentMetricsResponse(BaseModel):
    """Response model for agent metrics."""
    agent_id: str
    agent_name: str
    metrics: Dict[str, Any]
    health: Dict[str, Any]


class OrchestratorMetricsResponse(BaseModel):
    """Response model for orchestrator metrics."""
    orchestrator_id: str
    orchestrator_name: str
    metrics: Dict[str, Any]
    health: Dict[str, Any]


class PlatformMetricsResponse(BaseModel):
    """Response model for platform-wide metrics."""
    agents: List[AgentMetricsResponse]
    orchestrators: List[OrchestratorMetricsResponse]
    summary: Dict[str, Any]


# Dependency to get Telemetry Service
def get_telemetry_service(request: Request = None) -> AgenticTelemetryService:
    """Get telemetry service from app state."""
    if request and hasattr(request.app.state, "telemetry_service"):
        return request.app.state.telemetry_service
    # Otherwise, create a basic one (will skip recording if no Supabase)
    return AgenticTelemetryService()


# Dependency to get Health Monitors
def get_health_monitors(request) -> Dict[str, Any]:
    """Get health monitors from app state."""
    telemetry_service = get_telemetry_service(request)
    
    return {
        "agent_health_monitor": AgentHealthMonitor(telemetry_service=telemetry_service),
        "orchestrator_health_monitor": OrchestratorHealthMonitor(telemetry_service=telemetry_service)
    }


@router.get("/agents", response_model=List[AgentMetricsResponse])
async def get_agent_metrics(
    tenant_id: Optional[str] = Query(None),
    time_range_hours: int = Query(24),
    request: Request = None,
    telemetry_service: AgenticTelemetryService = Depends(get_telemetry_service)
):
    """
    Get metrics for all agents.
    
    Returns metrics and health status for all monitored agents.
    """
    try:
        # Get time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        # List of known agents (could be dynamic from registry)
        known_agents = [
            ("business_analysis_agent", "Business Analysis Agent"),
            ("sop_generation_agent", "SOP Generation Agent"),
            ("coexistence_analysis_agent", "Coexistence Analysis Agent"),
            ("blueprint_creation_agent", "Blueprint Creation Agent"),
            ("outcomes_synthesis_agent", "Outcomes Synthesis Agent"),
            ("roadmap_generation_agent", "Roadmap Generation Agent"),
            ("poc_generation_agent", "POC Generation Agent"),
            ("content_liaison_agent", "Content Liaison Agent"),
            ("outcomes_liaison_agent", "Outcomes Liaison Agent"),
            ("journey_liaison_agent", "Journey Liaison Agent"),
            ("insights_liaison_agent", "Insights Liaison Agent"),
            ("structured_extraction_agent", "Structured Extraction Agent"),
            ("guide_agent", "Guide Agent")
        ]
        
        agent_health_monitor = AgentHealthMonitor(telemetry_service=telemetry_service)
        
        results = []
        for agent_id, agent_name in known_agents:
            # Get metrics
            metrics = await telemetry_service.get_agent_metrics(
                agent_id=agent_id,
                tenant_id=tenant_id,
                time_range=(start_time, end_time)
            )
            
            # Get health
            await agent_health_monitor.start_monitoring(agent_id)
            health = await agent_health_monitor.get_health(agent_id)
            
            results.append(AgentMetricsResponse(
                agent_id=agent_id,
                agent_name=agent_name,
                metrics=metrics,
                health=health
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get agent metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orchestrators", response_model=List[OrchestratorMetricsResponse])
async def get_orchestrator_metrics(
    tenant_id: Optional[str] = Query(None),
    time_range_hours: int = Query(24),
    request: Request = None,
    telemetry_service: AgenticTelemetryService = Depends(get_telemetry_service)
):
    """
    Get metrics for all orchestrators.
    
    Returns metrics and health status for all monitored orchestrators.
    """
    try:
        # Get time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        # List of known orchestrators
        known_orchestrators = [
            ("insights_orchestrator", "Insights Orchestrator"),
            ("journey_orchestrator", "Journey Orchestrator"),
            ("content_orchestrator", "Content Orchestrator"),
            ("outcomes_orchestrator", "Outcomes Orchestrator")
        ]
        
        orchestrator_health_monitor = OrchestratorHealthMonitor(telemetry_service=telemetry_service)
        
        results = []
        for orchestrator_id, orchestrator_name in known_orchestrators:
            # Get metrics
            metrics = await telemetry_service.get_orchestrator_metrics(
                orchestrator_id=orchestrator_id,
                tenant_id=tenant_id,
                time_range=(start_time, end_time)
            )
            
            # Get health
            await orchestrator_health_monitor.start_monitoring(orchestrator_id)
            health = await orchestrator_health_monitor.get_health(orchestrator_id)
            
            results.append(OrchestratorMetricsResponse(
                orchestrator_id=orchestrator_id,
                orchestrator_name=orchestrator_name,
                metrics=metrics,
                health=health
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get orchestrator metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/platform", response_model=PlatformMetricsResponse)
async def get_platform_metrics(
    tenant_id: Optional[str] = Query(None),
    time_range_hours: int = Query(24),
    request: Request = None,
    telemetry_service: AgenticTelemetryService = Depends(get_telemetry_service)
):
    """
    Get platform-wide metrics.
    
    Returns aggregated metrics for all agents and orchestrators.
    """
    try:
        # Get agent metrics
        agent_metrics = await get_agent_metrics(
            tenant_id=tenant_id,
            time_range_hours=time_range_hours,
            request=request,
            telemetry_service=telemetry_service
        )
        
        # Get orchestrator metrics
        orchestrator_metrics = await get_orchestrator_metrics(
            tenant_id=tenant_id,
            time_range_hours=time_range_hours,
            request=request,
            telemetry_service=telemetry_service
        )
        
        # Calculate summary
        total_agent_executions = sum(m.metrics.get("execution_count", 0) for m in agent_metrics)
        total_orchestrator_intents = sum(m.metrics.get("intent_count", 0) for m in orchestrator_metrics)
        total_cost = sum(m.metrics.get("total_cost", 0.0) for m in agent_metrics)
        
        healthy_agents = sum(1 for m in agent_metrics if m.health.get("status") == "healthy")
        healthy_orchestrators = sum(1 for m in orchestrator_metrics if m.health.get("status") == "healthy")
        
        summary = {
            "total_agent_executions": total_agent_executions,
            "total_orchestrator_intents": total_orchestrator_intents,
            "total_cost_usd": total_cost,
            "healthy_agents": healthy_agents,
            "total_agents": len(agent_metrics),
            "healthy_orchestrators": healthy_orchestrators,
            "total_orchestrators": len(orchestrator_metrics),
            "agent_health_rate": healthy_agents / len(agent_metrics) if agent_metrics else 0.0,
            "orchestrator_health_rate": healthy_orchestrators / len(orchestrator_metrics) if orchestrator_metrics else 0.0
        }
        
        return PlatformMetricsResponse(
            agents=agent_metrics,
            orchestrators=orchestrator_metrics,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Failed to get platform metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
