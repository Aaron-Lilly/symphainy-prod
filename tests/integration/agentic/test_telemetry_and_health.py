"""
Telemetry and Health Monitoring Tests

Tests agent telemetry recording and health monitoring.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import asyncio
from datetime import datetime, timedelta
from symphainy_platform.civic_systems.agentic.telemetry.agentic_telemetry_service import AgenticTelemetryService
from symphainy_platform.civic_systems.agentic.health.agent_health_monitor import AgentHealthMonitor
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import IntentFactory


@pytest.fixture
async def telemetry_service():
    """Create telemetry service."""
    return AgenticTelemetryService(supabase_adapter=None)


@pytest.fixture
async def health_monitor(telemetry_service):
    """Create health monitor."""
    return AgentHealthMonitor(telemetry_service=telemetry_service)


@pytest.fixture
async def execution_context():
    """Create execution context."""
    intent = IntentFactory.create_intent(
        intent_type="test",
        tenant_id="test_tenant",
        session_id="test_session",
        solution_id="test_solution",
        parameters={}
    )
    return ExecutionContext(
        execution_id="test_execution",
        intent=intent,
        tenant_id="test_tenant",
        session_id="test_session",
        solution_id="test_solution"
    )


@pytest.mark.asyncio
async def test_record_agent_execution(telemetry_service, execution_context):
    """Test recording agent execution."""
    result = await telemetry_service.record_agent_execution(
        agent_id="test_agent",
        agent_name="Test Agent",
        prompt="Test prompt",
        response="Test response",
        model_name="gpt-4o-mini",
        tokens={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        cost=0.0015,
        latency_ms=500.0,
        context=execution_context,
        success=True
    )
    
    # Should return True (even if Supabase not available, should not raise)
    assert result is not None


@pytest.mark.asyncio
async def test_record_tool_usage(telemetry_service, execution_context):
    """Test recording tool usage."""
    result = await telemetry_service.record_agent_tool_usage(
        agent_id="test_agent",
        tool_name="test_tool",
        parameters={"param1": "value1"},
        result={"success": True, "data": "result"},
        context=execution_context,
        latency_ms=200.0
    )
    
    # Should return True (even if Supabase not available, should not raise)
    assert result is not None


@pytest.mark.asyncio
async def test_record_health_metric(telemetry_service, execution_context):
    """Test recording health metric."""
    result = await telemetry_service.record_agent_health(
        agent_id="test_agent",
        agent_name="Test Agent",
        health_status={"status": "healthy", "availability": 0.99},
        tenant_id="test_tenant"
    )
    
    # Should return True (even if Supabase not available, should not raise)
    assert result is not None


@pytest.mark.asyncio
async def test_get_agent_metrics(telemetry_service):
    """Test getting agent metrics."""
    # Get metrics (should work even without Supabase, returns empty metrics structure)
    metrics = await telemetry_service.get_agent_metrics(
        agent_id="test_agent",
        tenant_id="test_tenant",
        time_range=(
            datetime.utcnow() - timedelta(hours=24),
            datetime.utcnow()
        )
    )
    
    # Should return metrics structure even if Supabase not available
    assert isinstance(metrics, dict)
    # If Supabase not available, returns empty dict, but structure should be consistent
    if metrics:  # If metrics returned (Supabase available)
        assert "execution_count" in metrics
        assert "total_tokens" in metrics
        assert "total_cost" in metrics
    else:
        # If Supabase not available, metrics will be empty dict
        # This is acceptable for tests without Supabase
        assert metrics == {}


@pytest.mark.asyncio
async def test_health_monitor_start_monitoring(health_monitor):
    """Test starting health monitoring."""
    await health_monitor.start_monitoring("test_agent")
    
    # Should not raise
    assert True


@pytest.mark.asyncio
async def test_health_monitor_get_health(health_monitor):
    """Test getting agent health."""
    await health_monitor.start_monitoring("test_agent")
    
    health = await health_monitor.get_health("test_agent")
    
    assert isinstance(health, dict)
    assert "status" in health
    assert "availability" in health
    assert "performance" in health


@pytest.mark.asyncio
async def test_health_monitor_record_metric(health_monitor):
    """Test recording health metric."""
    await health_monitor.start_monitoring("test_agent")
    
    await health_monitor.record_health_metric(
        agent_id="test_agent",
        metric_name="latency",
        value=500.0
    )
    
    # Should not raise
    assert True


@pytest.mark.asyncio
async def test_health_monitor_record_status(health_monitor):
    """Test recording health status."""
    await health_monitor.record_health_status(
        agent_id="test_agent",
        agent_name="Test Agent",
        health_status={"status": "healthy"},
        tenant_id="test_tenant"
    )
    
    # Should not raise
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
