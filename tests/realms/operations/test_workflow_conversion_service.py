"""
Tests for Workflow Conversion Service.

Tests SOP ↔ Workflow conversion.
"""

import pytest
import json


@pytest.mark.unit
@pytest.mark.operations
@pytest.mark.asyncio
class TestWorkflowConversionService:
    """Test Workflow Conversion Service."""
    
    async def test_convert_sop_to_workflow(
        self,
        workflow_conversion_service,
        state_surface,
        in_memory_file_storage,
        sample_session_id,
        sample_tenant_id,
        sample_sop_data
    ):
        """Test converting SOP to workflow."""
        # Store SOP in State Surface first
        import uuid
        sop_id = str(uuid.uuid4())
        storage_path = f"{sample_tenant_id}/{sample_session_id}/{sop_id}/sop.json"
        
        # Store SOP artifact
        await in_memory_file_storage.upload_file(
            file_path=storage_path,
            file_data=json.dumps(sample_sop_data).encode('utf-8'),
            metadata={"type": "sop"}
        )
        
        # Store SOP reference in State Surface
        sop_reference = f"sop:{sample_tenant_id}:{sample_session_id}:{sop_id}"
        await state_surface.store_file_reference(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            file_reference=sop_reference,
            storage_location=storage_path,
            filename=f"sop_{sop_id}.json",
            metadata={"type": "sop"}
        )
        
        # Convert SOP to workflow
        result = await workflow_conversion_service.convert_sop_to_workflow(
            sop_file_reference=sop_reference,
            options={"workflow_pattern": "sequential"}
        )
        
        assert result["success"] is True
        assert "workflow_structure" in result
        assert result["workflow_structure"]["workflow_type"] == "sequential"
        assert "nodes" in result["workflow_structure"]
        assert "edges" in result["workflow_structure"]
        assert len(result["workflow_structure"]["nodes"]) > 0
    
    async def test_convert_workflow_to_sop(
        self,
        workflow_conversion_service,
        state_surface,
        in_memory_file_storage,
        sample_session_id,
        sample_tenant_id,
        sample_workflow_data
    ):
        """Test converting workflow to SOP."""
        # Store workflow in State Surface first
        import uuid
        workflow_id = str(uuid.uuid4())
        storage_path = f"{sample_tenant_id}/{sample_session_id}/{workflow_id}/workflow.json"
        
        # Store workflow artifact
        await in_memory_file_storage.upload_file(
            file_path=storage_path,
            file_data=json.dumps(sample_workflow_data).encode('utf-8'),
            metadata={"type": "workflow"}
        )
        
        # Store workflow reference in State Surface
        workflow_reference = f"workflow:{sample_tenant_id}:{sample_session_id}:{workflow_id}"
        await state_surface.store_file_reference(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            file_reference=workflow_reference,
            storage_location=storage_path,
            filename=f"workflow_{workflow_id}.json",
            metadata={"type": "workflow"}
        )
        
        # Convert workflow to SOP
        result = await workflow_conversion_service.convert_workflow_to_sop(
            workflow_file_reference=workflow_reference,
            options={"template_type": "standard"}
        )
        
        assert result["success"] is True
        assert "sop_structure" in result
        assert result["sop_structure"]["template_type"] == "standard"
        assert "title" in result["sop_structure"]
        assert "sections" in result["sop_structure"]
        assert "procedures" in result["sop_structure"]["sections"]
    
    async def test_validate_conversion(
        self,
        workflow_conversion_service,
        state_surface,
        in_memory_file_storage,
        sample_session_id,
        sample_tenant_id,
        sample_sop_data,
        sample_workflow_data
    ):
        """Test validating conversion."""
        import uuid
        
        # Store SOP
        sop_id = str(uuid.uuid4())
        sop_storage_path = f"{sample_tenant_id}/{sample_session_id}/{sop_id}/sop.json"
        await in_memory_file_storage.upload_file(
            file_path=sop_storage_path,
            file_data=json.dumps(sample_sop_data).encode('utf-8')
        )
        sop_reference = f"sop:{sample_tenant_id}:{sample_session_id}:{sop_id}"
        await state_surface.store_file_reference(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            file_reference=sop_reference,
            storage_location=sop_storage_path,
            filename=f"sop_{sop_id}.json",
            metadata={"type": "sop"}
        )
        
        # Store workflow
        workflow_id = str(uuid.uuid4())
        workflow_storage_path = f"{sample_tenant_id}/{sample_session_id}/{workflow_id}/workflow.json"
        await in_memory_file_storage.upload_file(
            file_path=workflow_storage_path,
            file_data=json.dumps(sample_workflow_data).encode('utf-8')
        )
        workflow_reference = f"workflow:{sample_tenant_id}:{sample_session_id}:{workflow_id}"
        await state_surface.store_file_reference(
            session_id=sample_session_id,
            tenant_id=sample_tenant_id,
            file_reference=workflow_reference,
            storage_location=workflow_storage_path,
            filename=f"workflow_{workflow_id}.json",
            metadata={"type": "workflow"}
        )
        
        # Validate conversion
        result = await workflow_conversion_service.validate_conversion(
            source_reference=sop_reference,
            target_reference=workflow_reference,
            conversion_type="sop_to_workflow"
        )
        
        assert result["success"] is True
        assert result["valid"] is True
        assert result["source_exists"] is True
        assert result["target_exists"] is True
