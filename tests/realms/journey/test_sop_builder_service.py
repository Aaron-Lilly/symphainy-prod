"""
Tests for SOP Builder Service.

Tests SOP creation, validation, and wizard functionality.
"""

import pytest
import json


@pytest.mark.unit
@pytest.mark.journey
@pytest.mark.asyncio
class TestSOPBuilderService:
    """Test SOP Builder Service."""
    
    async def test_start_wizard_session(self, sop_builder_service, sample_session_id, sample_tenant_id):
        """Test starting a wizard session."""
        result = await sop_builder_service.start_wizard_session(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            initial_description="Test process description"
        )
        
        assert result["success"] is True
        assert "session_token" in result
        assert "wizard_state" in result
        assert result["wizard_state"]["current_step"] == 1
        assert result["wizard_state"]["total_steps"] == 5
        assert result["wizard_state"]["progress_percentage"] == 0.0
    
    async def test_process_wizard_step(self, sop_builder_service, sample_session_id, sample_tenant_id):
        """Test processing a wizard step."""
        # Start wizard
        start_result = await sop_builder_service.start_wizard_session(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id
        )
        session_token = start_result["session_token"]
        
        # Process step 1: SOP type
        step_result = await sop_builder_service.process_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"sop_type": "technical"}
        )
        
        assert step_result["success"] is True
        assert step_result["current_step"] == 2
        assert step_result["progress_percentage"] == 40.0
        assert "next_question" in step_result
    
    async def test_complete_wizard(self, sop_builder_service, sample_session_id, sample_tenant_id):
        """Test completing wizard and generating SOP."""
        # Start wizard
        start_result = await sop_builder_service.start_wizard_session(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id
        )
        session_token = start_result["session_token"]
        
        # Process all steps
        await sop_builder_service.process_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"sop_type": "standard"}
        )
        await sop_builder_service.process_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"title": "Test SOP"}
        )
        await sop_builder_service.process_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"purpose": "Test purpose"}
        )
        await sop_builder_service.process_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"procedures": ["Step 1", "Step 2"]}
        )
        await sop_builder_service.process_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"additional_sections": {}}
        )
        
        # Complete wizard
        complete_result = await sop_builder_service.complete_wizard(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token
        )
        
        assert complete_result["success"] is True
        assert "sop_reference" in complete_result
        assert "sop_metadata" in complete_result
        assert complete_result["sop_metadata"]["template_type"] == "standard"
    
    async def test_create_sop(self, sop_builder_service):
        """Test creating SOP from description."""
        result = await sop_builder_service.create_sop(
            description="This is a test SOP for processing customer orders",
            options={"template_type": "standard"}
        )
        
        assert result["success"] is True
        assert "sop_structure" in result
        assert "sop_content" in result
        assert result["sop_structure"]["template_type"] == "standard"
        assert "title" in result["sop_structure"]
        assert "purpose" in result["sop_structure"]
    
    async def test_validate_sop_valid(self, sop_builder_service, sample_sop_data):
        """Test validating a valid SOP."""
        result = await sop_builder_service.validate_sop(sample_sop_data)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["score"] > 0
    
    async def test_validate_sop_missing_required_field(self, sop_builder_service):
        """Test validating SOP with missing required field."""
        invalid_sop = {
            "template_type": "standard",
            "title": "Test SOP"
            # Missing "purpose" and "procedures"
        }
        
        result = await sop_builder_service.validate_sop(invalid_sop)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert result["score"] < 100
