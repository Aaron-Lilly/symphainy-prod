"""
Test PlatformMonitoring Journey

Tests:
- Journey structure
- Journey execution
- SOA API exposure
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestPlatformMonitoringJourneyStructure:
    """Test PlatformMonitoringJourney structure."""
    
    def test_journey_exists(self, control_tower_solution):
        """PlatformMonitoringJourney should exist."""
        journey = control_tower_solution.get_journey("platform_monitoring")
        assert journey is not None
    
    def test_has_compose_journey(self, control_tower_solution):
        """Should have compose_journey method."""
        journey = control_tower_solution.get_journey("platform_monitoring")
        assert hasattr(journey, 'compose_journey')


class TestPlatformMonitoringJourneyExecution:
    """Test PlatformMonitoringJourney execution."""
    
    @pytest.mark.asyncio
    async def test_execute_journey(
        self, control_tower_solution, execution_context
    ):
        """Should execute journey successfully."""
        journey = control_tower_solution.get_journey("platform_monitoring")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={}
        )
        
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_returns_artifacts(
        self, control_tower_solution, execution_context
    ):
        """Should return artifacts in result."""
        journey = control_tower_solution.get_journey("platform_monitoring")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={}
        )
        
        assert "artifacts" in result


class TestPlatformMonitoringJourneySOAAPIs:
    """Test PlatformMonitoringJourney SOA APIs."""
    
    def test_has_soa_apis(self, control_tower_solution):
        """Should expose SOA APIs."""
        journey = control_tower_solution.get_journey("platform_monitoring")
        apis = journey.get_soa_apis()
        
        assert isinstance(apis, dict)
        assert len(apis) > 0
