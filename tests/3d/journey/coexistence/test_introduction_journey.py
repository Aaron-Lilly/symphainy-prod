"""
Test Introduction Journey - Platform Entry Point

Tests:
- Platform introduction
- Solution catalog display
- Coexistence explanation
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestIntroductionJourneyStructure:
    """Test IntroductionJourney structure."""
    
    def test_journey_exists(self, coexistence_solution):
        """IntroductionJourney should exist."""
        journey = coexistence_solution.get_journey("introduction")
        assert journey is not None
    
    def test_has_journey_id(self, coexistence_solution):
        """Should have JOURNEY_ID attribute."""
        journey = coexistence_solution.get_journey("introduction")
        assert hasattr(journey, 'JOURNEY_ID')
        assert journey.JOURNEY_ID == "introduction"
    
    def test_has_compose_journey(self, coexistence_solution):
        """Should have compose_journey method."""
        journey = coexistence_solution.get_journey("introduction")
        assert hasattr(journey, 'compose_journey')
        assert callable(journey.compose_journey)
    
    def test_has_get_soa_apis(self, coexistence_solution):
        """Should have get_soa_apis method."""
        journey = coexistence_solution.get_journey("introduction")
        assert hasattr(journey, 'get_soa_apis')


class TestIntroductionJourneyActions:
    """Test IntroductionJourney actions."""
    
    @pytest.mark.asyncio
    async def test_introduce_action(
        self, coexistence_solution, execution_context
    ):
        """Should handle 'introduce' action."""
        journey = coexistence_solution.get_journey("introduction")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={"action": "introduce"}
        )
        
        assert "success" in result
        assert result.get("success") is True
        assert "artifacts" in result
    
    @pytest.mark.asyncio
    async def test_catalog_action(
        self, coexistence_solution, execution_context
    ):
        """Should handle 'catalog' action."""
        journey = coexistence_solution.get_journey("introduction")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={"action": "catalog"}
        )
        
        assert "success" in result
        assert "artifacts" in result
    
    @pytest.mark.asyncio
    async def test_explain_action(
        self, coexistence_solution, execution_context
    ):
        """Should handle 'explain' action."""
        journey = coexistence_solution.get_journey("introduction")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={"action": "explain"}
        )
        
        assert "success" in result


class TestIntroductionJourneySOAAPIs:
    """Test IntroductionJourney SOA APIs."""
    
    def test_exposes_soa_apis(self, coexistence_solution):
        """Should expose SOA APIs."""
        journey = coexistence_solution.get_journey("introduction")
        apis = journey.get_soa_apis()
        assert len(apis) > 0
    
    def test_has_introduce_platform_api(self, coexistence_solution):
        """Should have introduce_platform API."""
        journey = coexistence_solution.get_journey("introduction")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("introduce" in name for name in api_names)
    
    def test_has_show_catalog_api(self, coexistence_solution):
        """Should have show_catalog API."""
        journey = coexistence_solution.get_journey("introduction")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("catalog" in name for name in api_names)


class TestIntroductionJourneyArtifacts:
    """Test IntroductionJourney artifacts."""
    
    @pytest.mark.asyncio
    async def test_returns_structured_artifacts(
        self, coexistence_solution, execution_context
    ):
        """Should return structured artifacts."""
        journey = coexistence_solution.get_journey("introduction")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={"action": "introduce"}
        )
        
        artifacts = result.get("artifacts", {})
        assert isinstance(artifacts, dict)
        
        # If artifacts exist, verify structure
        for key, artifact in artifacts.items():
            if isinstance(artifact, dict) and "result_type" in artifact:
                assert "semantic_payload" in artifact
                assert "renderings" in artifact
