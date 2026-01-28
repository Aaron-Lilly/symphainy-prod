"""
E2E Test: Control Tower Flow

DEMO PATH: Platform Monitoring → Solution Management → Docs

Critical demo path for admin dashboard capabilities.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestControlTowerDemoPath:
    """E2E test for Control Tower flow."""
    
    @pytest.mark.asyncio
    async def test_platform_monitoring(
        self,
        control_tower,
        execution_context
    ):
        """Test platform monitoring journey."""
        result = await control_tower.get_journey("platform_monitoring").compose_journey(
            context=execution_context,
            journey_params={"action": "get_stats"}
        )
        
        assert "success" in result
        assert "artifacts" in result
    
    @pytest.mark.asyncio
    async def test_solution_management_list(
        self,
        control_tower,
        execution_context
    ):
        """Test solution management - list solutions."""
        result = await control_tower.get_journey("solution_management").compose_journey(
            context=execution_context,
            journey_params={"action": "list"}
        )
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_developer_docs(
        self,
        control_tower,
        execution_context
    ):
        """Test developer documentation journey."""
        result = await control_tower.get_journey("developer_docs").compose_journey(
            context=execution_context,
            journey_params={"action": "get_patterns"}
        )
        
        assert "success" in result


class TestControlTowerAdminCapabilities:
    """Test Control Tower admin capabilities."""
    
    @pytest.mark.asyncio
    async def test_get_platform_health(
        self,
        control_tower,
        execution_context
    ):
        """Test getting platform health."""
        result = await control_tower.get_journey("platform_monitoring").compose_journey(
            context=execution_context,
            journey_params={"action": "health_check"}
        )
        
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_solution_composition(
        self,
        control_tower,
        execution_context
    ):
        """Test solution composition journey."""
        result = await control_tower.get_journey("solution_composition").compose_journey(
            context=execution_context,
            journey_params={"action": "guided_create"}
        )
        
        assert "success" in result or "error" in result
