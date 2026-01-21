"""
Smoke Test: Data Quality Assessment

Quick validation that data quality assessment works with deterministic embeddings.
"""

import pytest
from typing import Dict, Any

from symphainy_platform.realms.insights.enabling_services.data_quality_service import DataQualityService


@pytest.mark.asyncio
@pytest.mark.smoke
class TestDataQualitySmoke:
    """Smoke tests for data quality assessment."""
    
    async def test_data_quality_service_initialization(self):
        """Test service initialization."""
        service = DataQualityService(public_works=None)
        assert service is not None
        assert hasattr(service, 'assess_data_quality')
    
    async def test_parsing_confidence_calculation(self):
        """Test parsing confidence calculation."""
        service = DataQualityService(public_works=None)
        
        # Good quality
        good_quality = {"status": "good", "issues": []}
        confidence = service._calculate_parsing_confidence(good_quality)
        assert confidence == 0.95
        
        # Issues quality
        issues_quality = {
            "status": "issues",
            "issues": [
                {"severity": "medium", "type": "warning"}
            ]
        }
        confidence = service._calculate_parsing_confidence(issues_quality)
        assert 0.0 <= confidence <= 1.0
        assert confidence < 0.95
        
        # Poor quality
        poor_quality = {"status": "poor", "issues": []}
        confidence = service._calculate_parsing_confidence(poor_quality)
        assert confidence == 0.3
    
    async def test_embedding_confidence_calculation(self):
        """Test embedding confidence calculation."""
        service = DataQualityService(public_works=None)
        
        # Good quality with exact match
        good_quality = {
            "status": "good",
            "issues": [],
            "schema_match": {"exact_match": True}
        }
        confidence = service._calculate_embedding_confidence(good_quality)
        assert confidence == 0.95
        
        # Issues quality
        issues_quality = {
            "status": "issues",
            "issues": [{"severity": "high", "type": "schema_mismatch"}],
            "schema_match": {"exact_match": False}
        }
        confidence = service._calculate_embedding_confidence(issues_quality)
        assert 0.0 <= confidence <= 1.0
        assert confidence < 0.95
    
    async def test_confidence_issue_identification(self):
        """Test confidence-based issue identification."""
        service = DataQualityService(public_works=None)
        
        # Low parsing confidence (bad scan)
        issues = service._identify_confidence_issues(
            parsing_confidence=0.5,  # Below threshold
            embedding_confidence=0.8,
            overall_confidence=0.65
        )
        assert len(issues) > 0
        assert any(i["type"] == "bad_scan" for i in issues)
        
        # Low embedding confidence (bad schema)
        issues = service._identify_confidence_issues(
            parsing_confidence=0.8,
            embedding_confidence=0.5,  # Below threshold
            overall_confidence=0.65
        )
        assert len(issues) > 0
        assert any(i["type"] == "bad_schema" for i in issues)
        
        # Both good
        issues = service._identify_confidence_issues(
            parsing_confidence=0.9,
            embedding_confidence=0.9,
            overall_confidence=0.9
        )
        assert len(issues) == 0
