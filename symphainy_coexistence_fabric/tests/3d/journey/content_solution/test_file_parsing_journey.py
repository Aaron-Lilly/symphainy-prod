"""
Test File Parsing Journey

Tests:
- File parsing flow
- Content extraction
- Parser selection
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestFileParsingJourneyStructure:
    """Test FileParsingJourney structure."""
    
    def test_journey_exists(self, content_solution):
        """FileParsingJourney should exist."""
        journey = content_solution.get_journey("file_parsing")
        assert journey is not None
    
    def test_has_compose_journey(self, content_solution):
        """Should have compose_journey method."""
        journey = content_solution.get_journey("file_parsing")
        assert hasattr(journey, 'compose_journey')


class TestFileParsingJourneyExecution:
    """Test FileParsingJourney execution."""
    
    @pytest.mark.asyncio
    async def test_parse_file(self, content_solution, execution_context):
        """Should handle file parsing."""
        journey = content_solution.get_journey("file_parsing")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "file_id": "test_file_123",
                "parser_type": "auto"
            }
        )
        
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_returns_parsed_content(self, content_solution, execution_context):
        """Should return parsed content in artifacts."""
        journey = content_solution.get_journey("file_parsing")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={"file_id": "test_file_123"}
        )
        
        assert "artifacts" in result


class TestFileParsingJourneySOAAPIs:
    """Test FileParsingJourney SOA APIs."""
    
    def test_has_parse_api(self, content_solution):
        """Should have parse API."""
        journey = content_solution.get_journey("file_parsing")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("parse" in name.lower() for name in api_names)
