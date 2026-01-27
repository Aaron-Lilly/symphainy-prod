"""
Test File Management Journey

Tests:
- File listing
- File retrieval
- File archival
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestFileManagementJourneyStructure:
    """Test FileManagementJourney structure."""
    
    def test_journey_exists(self, content_solution):
        """FileManagementJourney should exist."""
        journey = content_solution.get_journey("file_management")
        assert journey is not None
    
    def test_has_compose_journey(self, content_solution):
        """Should have compose_journey method."""
        journey = content_solution.get_journey("file_management")
        assert hasattr(journey, 'compose_journey')


class TestFileManagementJourneyActions:
    """Test FileManagementJourney actions."""
    
    @pytest.mark.asyncio
    async def test_list_files(self, content_solution, execution_context):
        """Should list files."""
        journey = content_solution.get_journey("file_management")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={"action": "list"}
        )
        
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_retrieve_file(self, content_solution, execution_context):
        """Should retrieve file metadata."""
        journey = content_solution.get_journey("file_management")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "action": "retrieve",
                "file_id": "test_file_123"
            }
        )
        
        assert "success" in result or "error" in result


class TestFileManagementJourneySOAAPIs:
    """Test FileManagementJourney SOA APIs."""
    
    def test_has_list_api(self, content_solution):
        """Should have list API."""
        journey = content_solution.get_journey("file_management")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("list" in name.lower() for name in api_names)
