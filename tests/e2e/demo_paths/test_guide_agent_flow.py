"""
E2E Test: GuideAgent Interaction Flow

DEMO PATH: Landing → GuideAgent → Tool Discovery → Specialist Handoff

Critical demo path for AI-powered assistance.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestGuideAgentDemoPath:
    """E2E test for GuideAgent interaction flow."""
    
    @pytest.mark.asyncio
    async def test_full_guide_agent_flow(
        self,
        coexistence_solution,
        execution_context
    ):
        """Test complete GuideAgent flow: initiate → message → route."""
        guide_journey = coexistence_solution.get_journey("guide_agent")
        
        # Step 1: Initiate session
        init_result = await guide_journey.compose_journey(
            context=execution_context,
            journey_params={"action": "initiate"}
        )
        
        assert "success" in init_result
        
        # Step 2: Process user message
        message_result = await guide_journey.compose_journey(
            context=execution_context,
            journey_params={
                "action": "process_message",
                "message": "I need help uploading a document"
            }
        )
        
        assert "success" in message_result
        
        # Step 3: Route to specialist (if needed)
        route_result = await guide_journey.compose_journey(
            context=execution_context,
            journey_params={
                "action": "route_to_liaison",
                "pillar_type": "content",
                "user_query": "Upload document"
            }
        )
        
        assert "success" in route_result
    
    @pytest.mark.asyncio
    async def test_introduction_to_guide_agent(
        self,
        coexistence_solution,
        execution_context
    ):
        """Test introduction → GuideAgent transition."""
        # Step 1: Get platform introduction
        intro_result = await coexistence_solution.get_journey("introduction").compose_journey(
            context=execution_context,
            journey_params={"action": "introduce"}
        )
        
        assert "success" in intro_result
        
        # Step 2: Start GuideAgent session
        guide_result = await coexistence_solution.get_journey("guide_agent").compose_journey(
            context=execution_context,
            journey_params={"action": "initiate"}
        )
        
        assert "success" in guide_result


class TestCoexistenceNavigationFlow:
    """Test coexistence navigation flow."""
    
    @pytest.mark.asyncio
    async def test_navigate_to_content_solution(
        self,
        coexistence_solution,
        execution_context
    ):
        """Test navigation to Content Solution."""
        result = await coexistence_solution.get_journey("navigation").compose_journey(
            context=execution_context,
            journey_params={
                "action": "navigate",
                "solution_id": "content_solution"
            }
        )
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_establish_solution_context(
        self,
        coexistence_solution,
        execution_context
    ):
        """Test establishing solution context."""
        result = await coexistence_solution.get_journey("navigation").compose_journey(
            context=execution_context,
            journey_params={
                "action": "establish_context",
                "solution_id": "insights_solution",
                "context_data": {"current_analysis": "data_quality"}
            }
        )
        
        assert "success" in result
