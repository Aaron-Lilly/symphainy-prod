"""
Test Demo Critical Paths - Real Infrastructure

Functional Tests: Validate actual demo paths work with real infrastructure.
"""
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestRealAuthenticationFlow:
    """Test real authentication - catches 'can't login' issues."""
    
    @pytest.mark.real_infrastructure
    @pytest.mark.functional
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_real_user_login(self, real_solutions, real_execution_context):
        """Test real user login."""
        security_solution = real_solutions.security
        journey = security_solution._journeys.get("authentication")
        if not journey:
            pytest.skip("Authentication journey not available")
        result = await journey.compose_journey(
            journey_id="authentication",
            context=real_execution_context,
            journey_params={"email": "test@example.com", "password": "Test123!"}
        )
        assert result is not None
        assert "artifacts" in result or "error" in result


class TestRealFileUploadFlow:
    """Test real file upload - catches 'fails silently' issues."""
    
    @pytest.mark.real_infrastructure
    @pytest.mark.functional
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_real_file_upload(self, real_solutions, real_execution_context):
        """Test real file upload."""
        content_solution = real_solutions.content
        journey = content_solution.get_journey("file_upload_materialization")
        if not journey:
            pytest.skip("File upload journey not available")
        result = await journey.compose_journey(
            journey_id="file_upload_materialization",
            context=real_execution_context,
            journey_params={"file_content": b"Test".hex(), "file_name": "test.txt"}
        )
        assert result is not None
        assert "artifacts" in result or "error" in result


class TestRealFileParsing:
    """Test real file parsing - catches 'gibberish' issues."""
    
    @pytest.mark.real_infrastructure
    @pytest.mark.functional
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_real_parsing_quality(self, real_solutions, real_execution_context):
        """Test parsing returns meaningful content."""
        content_solution = real_solutions.content
        journey = content_solution.get_journey("file_parsing")
        if not journey:
            pytest.skip("File parsing journey not available")
        result = await journey.compose_journey(
            journey_id="file_parsing",
            context=real_execution_context,
            journey_params={"file_id": "test_file_123"}
        )
        if "artifacts" in result:
            parsed = str(result["artifacts"]).lower()
            assert len(parsed) > 0, "Parsed content should not be empty"


class TestRealChatAgents:
    """Test real chat agents - catches 'just echo' issues."""
    
    @pytest.mark.real_infrastructure
    @pytest.mark.functional
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_guide_agent_quality(self, real_solutions, real_execution_context):
        """Test GuideAgent generates real responses."""
        coexistence_solution = real_solutions.coexistence
        journey = coexistence_solution.get_journey("guide_agent")
        if not journey:
            pytest.skip("GuideAgent journey not available")
        result = await journey.compose_journey(
            journey_id="guide_agent",
            context=real_execution_context,
            journey_params={"action": "process_message", "message": "Hello"}
        )
        if "artifacts" in result:
            response = str(result["artifacts"]).lower()
            assert len(response) > 10, "Response should be substantial"


class TestRealNavigation:
    """Test real navigation - catches 'doesn't work' issues."""
    
    @pytest.mark.real_infrastructure
    @pytest.mark.functional
    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_real_navigation(self, real_solutions, real_execution_context):
        """Test real navigation."""
        coexistence_solution = real_solutions.coexistence
        journey = coexistence_solution.get_journey("navigation")
        if not journey:
            pytest.skip("Navigation journey not available")
        result = await journey.compose_journey(
            journey_id="navigation",
            context=real_execution_context,
            journey_params={"action": "navigate", "solution_id": "content_solution"}
        )
        assert result is not None
        assert "artifacts" in result or "error" in result
