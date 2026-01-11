"""
Tests for Coexistence Analysis Service.

Tests coexistence analysis and blueprint generation.
"""

import pytest


@pytest.mark.unit
@pytest.mark.journey
@pytest.mark.asyncio
class TestCoexistenceAnalysisService:
    """Test Coexistence Analysis Service."""
    
    async def test_analyze_coexistence(self, coexistence_analysis_service, sample_workflow_data):
        """Test analyzing coexistence opportunities."""
        result = await coexistence_analysis_service.analyze_coexistence(
            current_state=sample_workflow_data,
            target_state=None
        )
        
        assert result["success"] is True
        assert "analysis_result" in result
        analysis = result["analysis_result"]
        assert "analysis_id" in analysis
        assert "opportunities" in analysis
        assert "recommended_patterns" in analysis
        assert len(analysis["opportunities"]) > 0
    
    async def test_generate_blueprint(
        self,
        coexistence_analysis_service,
        sample_workflow_data
    ):
        """Test generating coexistence blueprint."""
        # First analyze
        analysis_result = await coexistence_analysis_service.analyze_coexistence(
            current_state=sample_workflow_data
        )
        analysis_data = analysis_result["analysis_result"]
        
        # Generate blueprint
        blueprint_result = await coexistence_analysis_service.generate_blueprint(
            analysis_result=analysis_data,
            options={}
        )
        
        assert blueprint_result["success"] is True
        assert "blueprint_structure" in blueprint_result
        blueprint = blueprint_result["blueprint_structure"]
        assert "blueprint_id" in blueprint
        assert "recommended_patterns" in blueprint
        assert "implementation_plan" in blueprint
        assert "optimization_metrics" in blueprint
    
    async def test_optimize_coexistence(
        self,
        coexistence_analysis_service,
        state_surface,
        in_memory_file_storage,
        sample_session_id,
        sample_tenant_id,
        sample_workflow_data
    ):
        """Test optimizing coexistence blueprint."""
        import json
        import uuid
        
        # Analyze and generate blueprint
        analysis_result = await coexistence_analysis_service.analyze_coexistence(
            current_state=sample_workflow_data
        )
        analysis_data = analysis_result["analysis_result"]
        
        blueprint_result = await coexistence_analysis_service.generate_blueprint(
            analysis_result=analysis_data
        )
        blueprint_data = blueprint_result["blueprint_structure"]
        
        # Store blueprint
        blueprint_id = blueprint_data["blueprint_id"]
        storage_path = f"{sample_tenant_id}/{sample_session_id}/{blueprint_id}/blueprint.json"
        await in_memory_file_storage.upload_file(
            file_path=storage_path,
            file_data=json.dumps(blueprint_data).encode('utf-8')
        )
        
        blueprint_reference = f"blueprint:{blueprint_id}"
        await state_surface.store_file_reference(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            file_reference=blueprint_reference,
            storage_location=storage_path,
            filename=f"blueprint_{blueprint_id}.json",
            metadata={"type": "blueprint"}
        )
        
        # Optimize blueprint
        optimization_result = await coexistence_analysis_service.optimize_coexistence(
            blueprint_reference=blueprint_reference,
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            optimization_criteria={
                "prioritize_efficiency": True,
                "prioritize_cost_reduction": True
            }
        )
        
        assert optimization_result["success"] is True
        assert "optimized_blueprint" in optimization_result
        optimized = optimization_result["optimized_blueprint"]
        assert "optimized_at" in optimized
        assert "optimization_criteria" in optimized
