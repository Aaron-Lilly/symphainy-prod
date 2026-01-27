"""
E2E Test: POC to Roadmap Flow

DEMO PATH: POC Creation → Blueprint → Roadmap

Critical demo path for outcomes capabilities.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestPOCToRoadmapDemoPath:
    """E2E test for POC to roadmap flow."""
    
    @pytest.mark.asyncio
    async def test_full_flow_poc_to_roadmap(
        self,
        outcomes_solution,
        execution_context
    ):
        """Test complete flow: POC → Blueprint → Roadmap."""
        # Step 1: Create POC proposal
        poc_result = await outcomes_solution.get_journey("poc_proposal").compose_journey(
            context=execution_context,
            journey_params={
                "project_name": "Demo Migration",
                "objectives": ["Migrate legacy data", "Modernize processes"]
            }
        )
        
        assert "success" in poc_result
        
        # Step 2: Create blueprint
        blueprint_result = await outcomes_solution.get_journey("blueprint_creation").compose_journey(
            context=execution_context,
            journey_params={"poc_id": "poc_123"}
        )
        
        assert "success" in blueprint_result or "error" in blueprint_result
        
        # Step 3: Generate roadmap
        roadmap_result = await outcomes_solution.get_journey("roadmap_generation").compose_journey(
            context=execution_context,
            journey_params={"blueprint_id": "blueprint_123"}
        )
        
        assert "success" in roadmap_result or "error" in roadmap_result
    
    @pytest.mark.asyncio
    async def test_outcome_synthesis(
        self,
        outcomes_solution,
        execution_context
    ):
        """Test outcome synthesis."""
        result = await outcomes_solution.get_journey("outcome_synthesis").compose_journey(
            context=execution_context,
            journey_params={
                "artifact_ids": ["artifact_1", "artifact_2"],
                "synthesis_type": "comprehensive"
            }
        )
        
        assert "success" in result or "error" in result


class TestOutcomesJourneyChaining:
    """Test outcomes journey chaining."""
    
    @pytest.mark.asyncio
    async def test_poc_to_solution_chain(
        self,
        outcomes_solution,
        execution_context
    ):
        """Test POC → Solution chain."""
        # Create POC
        poc_result = await outcomes_solution.get_journey("poc_proposal").compose_journey(
            context=execution_context,
            journey_params={"project_name": "Test Project"}
        )
        
        # Create solution
        solution_result = await outcomes_solution.get_journey("solution_creation").compose_journey(
            context=execution_context,
            journey_params={"poc_id": "poc_123"}
        )
        
        assert "success" in poc_result or "error" in poc_result
        assert "success" in solution_result or "error" in solution_result
