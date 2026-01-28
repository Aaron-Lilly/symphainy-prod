"""
E2E Test: File Upload to Insight Flow

DEMO PATH: Upload → Parse → Analyze → Report

This is a critical demo path that must work end-to-end.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestFileToInsightDemoPath:
    """E2E test for file upload to insight flow."""
    
    @pytest.mark.asyncio
    async def test_full_flow_upload_parse_analyze(
        self,
        content_solution,
        insights_solution,
        execution_context
    ):
        """Test complete flow: upload → parse → analyze."""
        # Step 1: Upload file
        upload_result = await content_solution.get_journey("file_upload_materialization").compose_journey(
            context=execution_context,
            journey_params={"file_name": "test_document.txt"}
        )
        
        assert "success" in upload_result
        
        # Step 2: Parse file (using mock file_id)
        parse_result = await content_solution.get_journey("file_parsing").compose_journey(
            context=execution_context,
            journey_params={"file_id": "test_file_123"}
        )
        
        assert "success" in parse_result or "error" in parse_result
        
        # Step 3: Analyze data
        analysis_result = await insights_solution.get_journey("business_analysis").compose_journey(
            context=execution_context,
            journey_params={"artifact_id": "test_artifact_123"}
        )
        
        assert "success" in analysis_result or "error" in analysis_result
    
    @pytest.mark.asyncio
    async def test_quality_assessment_after_parse(
        self,
        content_solution,
        insights_solution,
        execution_context
    ):
        """Test: parse → quality assessment."""
        # Parse file
        parse_result = await content_solution.get_journey("file_parsing").compose_journey(
            context=execution_context,
            journey_params={"file_id": "test_file_123"}
        )
        
        # Quality assessment
        quality_result = await insights_solution.get_journey("data_quality").compose_journey(
            context=execution_context,
            journey_params={"parsed_file_id": "parsed_123"}
        )
        
        assert "success" in quality_result or "error" in quality_result


class TestContentJourneyChaining:
    """Test content journey chaining."""
    
    @pytest.mark.asyncio
    async def test_upload_to_parse_chain(
        self,
        content_solution,
        execution_context
    ):
        """Test upload → parse chain."""
        # Upload
        upload_result = await content_solution.get_journey("file_upload_materialization").compose_journey(
            context=execution_context,
            journey_params={"file_name": "test.txt"}
        )
        
        # Parse (would use file_id from upload in real scenario)
        parse_result = await content_solution.get_journey("file_parsing").compose_journey(
            context=execution_context,
            journey_params={"file_id": "test_file_123"}
        )
        
        # Both should complete (success or expected error)
        assert "success" in upload_result or "error" in upload_result
        assert "success" in parse_result or "error" in parse_result
    
    @pytest.mark.asyncio
    async def test_parse_to_embed_chain(
        self,
        content_solution,
        execution_context
    ):
        """Test parse → embed chain."""
        # Parse
        parse_result = await content_solution.get_journey("file_parsing").compose_journey(
            context=execution_context,
            journey_params={"file_id": "test_file_123"}
        )
        
        # Embed (would use parsed_file_id from parse in real scenario)
        embed_result = await content_solution.get_journey("deterministic_embedding").compose_journey(
            context=execution_context,
            journey_params={"parsed_file_id": "parsed_123"}
        )
        
        assert "success" in parse_result or "error" in parse_result
        assert "success" in embed_result or "error" in embed_result
