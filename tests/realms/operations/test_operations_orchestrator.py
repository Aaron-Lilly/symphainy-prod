"""
Tests for Operations Orchestrator.

Tests all saga steps.

NOTE: Migrated from Journey Orchestrator tests. Some tests may need
updating to match the new Operations Realm API structure.
"""

import pytest
import json
import uuid


@pytest.mark.integration
@pytest.mark.operations
@pytest.mark.asyncio
@pytest.mark.skip(reason="Tests need to be updated for new Operations Realm API structure")
class TestOperationsOrchestrator:
    """Test Operations Orchestrator (formerly Journey Orchestrator)."""
    
    async def test_create_sop_from_workflow(
        self,
        journey_orchestrator,
        state_surface,
        in_memory_file_storage,
        sample_session_id,
        sample_tenant_id,
        sample_workflow_data
    ):
        """Test creating SOP from workflow (orchestrator saga)."""
        # Store workflow first
        workflow_id = str(uuid.uuid4())
        storage_path = f"{sample_tenant_id}/{sample_session_id}/{workflow_id}/workflow.json"
        await in_memory_file_storage.upload_file(
            file_path=storage_path,
            file_data=json.dumps(sample_workflow_data).encode('utf-8')
        )
        
        workflow_reference = f"workflow:{sample_tenant_id}:{sample_session_id}:{workflow_id}"
        await state_surface.store_file_reference(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            file_reference=workflow_reference,
            storage_location=storage_path,
            filename=f"workflow_{workflow_id}.json",
            metadata={"type": "workflow"}
        )
        
        # Create SOP from workflow
        result = await journey_orchestrator.create_sop_from_workflow(
            workflow_reference=workflow_reference,
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            options={}
        )
        
        assert result["success"] is True
        assert "sop_reference" in result
        assert "sop_metadata" in result
        assert result["sop_metadata"]["source_workflow"] == workflow_reference
    
    async def test_create_workflow_from_sop(
        self,
        journey_orchestrator,
        state_surface,
        in_memory_file_storage,
        sample_session_id,
        sample_tenant_id,
        sample_sop_data
    ):
        """Test creating workflow from SOP (orchestrator saga)."""
        # Store SOP first
        sop_id = str(uuid.uuid4())
        storage_path = f"{sample_tenant_id}/{sample_session_id}/{sop_id}/sop.json"
        await in_memory_file_storage.upload_file(
            file_path=storage_path,
            file_data=json.dumps(sample_sop_data).encode('utf-8')
        )
        
        sop_reference = f"sop:{sample_tenant_id}:{sample_session_id}:{sop_id}"
        await state_surface.store_file_reference(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            file_reference=sop_reference,
            storage_location=storage_path,
            filename=f"sop_{sop_id}.json",
            metadata={"type": "sop"}
        )
        
        # Create workflow from SOP
        result = await journey_orchestrator.create_workflow_from_sop(
            sop_file_reference=sop_reference,
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            options={}
        )
        
        assert result["success"] is True
        assert "workflow_reference" in result
        assert "workflow_metadata" in result
        assert result["workflow_metadata"]["source_sop"] == sop_reference
    
    async def test_sop_wizard_flow(
        self,
        journey_orchestrator,
        sample_session_id,
        sample_tenant_id
    ):
        """Test complete SOP wizard flow (orchestrator saga)."""
        # Start wizard
        start_result = await journey_orchestrator.start_sop_wizard(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            initial_description="Test process"
        )
        
        assert start_result["success"] is True
        session_token = start_result["session_token"]
        
        # Process steps
        await journey_orchestrator.process_sop_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"sop_type": "standard"}
        )
        await journey_orchestrator.process_sop_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"title": "Test SOP"}
        )
        await journey_orchestrator.process_sop_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"purpose": "Test purpose"}
        )
        await journey_orchestrator.process_sop_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"procedures": ["Step 1", "Step 2"]}
        )
        await journey_orchestrator.process_sop_wizard_step(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token,
            step_data={"additional_sections": {}}
        )
        
        # Complete wizard
        complete_result = await journey_orchestrator.complete_sop_wizard(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            session_token=session_token
        )
        
        assert complete_result["success"] is True
        assert "sop_reference" in complete_result
        assert "sop_metadata" in complete_result
    
    async def test_analyze_coexistence_saga(
        self,
        journey_orchestrator,
        state_surface,
        in_memory_file_storage,
        sample_session_id,
        sample_tenant_id,
        sample_workflow_data
    ):
        """Test coexistence analysis saga."""
        # Store workflow
        workflow_id = str(uuid.uuid4())
        storage_path = f"{sample_tenant_id}/{sample_session_id}/{workflow_id}/workflow.json"
        await in_memory_file_storage.upload_file(
            file_path=storage_path,
            file_data=json.dumps(sample_workflow_data).encode('utf-8')
        )
        
        workflow_reference = f"workflow:{sample_tenant_id}:{sample_session_id}:{workflow_id}"
        await state_surface.store_file_reference(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            file_reference=workflow_reference,
            storage_location=storage_path,
            filename=f"workflow_{workflow_id}.json",
            metadata={"type": "workflow"}
        )
        
        # Analyze coexistence
        result = await journey_orchestrator.analyze_coexistence(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            workflow_reference=workflow_reference,
            sop_reference=None,
            options={}
        )
        
        assert result["success"] is True
        assert "analysis_reference" in result
        assert "analysis_metadata" in result
        assert result["analysis_metadata"]["opportunities_count"] > 0
    
    async def test_generate_blueprint_saga(
        self,
        journey_orchestrator,
        state_surface,
        in_memory_file_storage,
        sample_session_id,
        sample_tenant_id,
        sample_workflow_data
    ):
        """Test blueprint generation saga."""
        # First analyze
        workflow_id = str(uuid.uuid4())
        storage_path = f"{sample_tenant_id}/{sample_session_id}/{workflow_id}/workflow.json"
        await in_memory_file_storage.upload_file(
            file_path=storage_path,
            file_data=json.dumps(sample_workflow_data).encode('utf-8')
        )
        
        workflow_reference = f"workflow:{sample_tenant_id}:{sample_session_id}:{workflow_id}"
        await state_surface.store_file_reference(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            file_reference=workflow_reference,
            storage_location=storage_path,
            filename=f"workflow_{workflow_id}.json",
            metadata={"type": "workflow"}
        )
        
        analysis_result = await journey_orchestrator.analyze_coexistence(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            workflow_reference=workflow_reference,
            sop_reference=None
        )
        analysis_reference = analysis_result["analysis_reference"]
        
        # Generate blueprint
        blueprint_result = await journey_orchestrator.generate_coexistence_blueprint(
            analysis_reference=analysis_reference,
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            options={}
        )
        
        assert blueprint_result["success"] is True
        assert "blueprint_reference" in blueprint_result
        assert "blueprint_metadata" in blueprint_result
    
    async def test_create_platform_journey_saga(
        self,
        journey_orchestrator,
        state_surface,
        in_memory_file_storage,
        sample_session_id,
        sample_tenant_id,
        sample_workflow_data
    ):
        """Test platform journey creation saga."""
        # Create analysis and blueprint first
        workflow_id = str(uuid.uuid4())
        storage_path = f"{sample_tenant_id}/{sample_session_id}/{workflow_id}/workflow.json"
        await in_memory_file_storage.upload_file(
            file_path=storage_path,
            file_data=json.dumps(sample_workflow_data).encode('utf-8')
        )
        
        workflow_reference = f"workflow:{sample_tenant_id}:{sample_session_id}:{workflow_id}"
        await state_surface.store_file_reference(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            file_reference=workflow_reference,
            storage_location=storage_path,
            filename=f"workflow_{workflow_id}.json",
            metadata={"type": "workflow"}
        )
        
        analysis_result = await journey_orchestrator.analyze_coexistence(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            workflow_reference=workflow_reference
        )
        analysis_reference = analysis_result["analysis_reference"]
        
        blueprint_result = await journey_orchestrator.generate_coexistence_blueprint(
            analysis_reference=analysis_reference,
            session_id=sample_session_id,
            tenant_id=sample_tenant_id
        )
        blueprint_reference = blueprint_result["blueprint_reference"]
        
        # Create platform journey
        journey_result = await journey_orchestrator.create_platform_journey(
            blueprint_reference=blueprint_reference,
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            options={}
        )
        
        assert journey_result["success"] is True
        assert "journey_reference" in journey_result
        assert "journey_metadata" in journey_result
        assert journey_result["journey_metadata"]["source_blueprint"] == blueprint_reference
