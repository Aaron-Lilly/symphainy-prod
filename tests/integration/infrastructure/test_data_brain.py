"""
DataBrain Integration Tests

Tests DataBrain with real ArangoDB instance.

WHAT (Test Role): I verify DataBrain reference tracking and provenance works
HOW (Test Implementation): I use docker-compose ArangoDB and test all DataBrain operations
"""

import pytest
from typing import Dict, Any
from symphainy_platform.foundations.public_works.adapters.arango_adapter import ArangoAdapter
from symphainy_platform.runtime.data_brain import DataBrain
from tests.infrastructure.test_fixtures import test_arango, clean_test_db
from tests.infrastructure.test_data_manager import TestDataManager


@pytest.mark.integration
@pytest.mark.infrastructure
class TestDataBrain:
    """Test DataBrain with real ArangoDB."""
    
    @pytest.fixture
    def data_brain(
        self,
        test_arango: ArangoAdapter
    ) -> DataBrain:
        """Create DataBrain with real ArangoDB adapter."""
        return DataBrain(arango_adapter=test_arango)
    
    @pytest.mark.asyncio
    async def test_initialization(
        self,
        data_brain: DataBrain
    ):
        """Test DataBrain initialization."""
        success = await data_brain.initialize()
        assert success, "DataBrain should initialize successfully"
    
    @pytest.mark.asyncio
    async def test_register_reference(
        self,
        data_brain: DataBrain,
        clean_test_db
    ):
        """Test registering a file reference."""
        await data_brain.initialize()
        
        reference_id = "test_reference_1"
        reference_type = "file"
        storage_location = "gs://bucket/file.txt"
        metadata = {
            "file_id": "file_123",
            "file_type": "text/plain",
            "file_size": 1024,
            "tenant_id": "tenant_1"
        }
        
        success = await data_brain.register_reference(
            reference_id,
            reference_type,
            storage_location,
            metadata=metadata
        )
        assert success, "Reference should be registered"
        
        # Verify reference can be retrieved
        retrieved = await data_brain.get_reference(reference_id)
        assert retrieved is not None, "Reference should be retrievable"
        assert retrieved.reference_id == reference_id, "Reference ID should match"
        assert retrieved.storage_location == storage_location, "Storage location should match"
        assert retrieved.metadata["file_id"] == "file_123", "Metadata should match"
    
    @pytest.mark.asyncio
    async def test_get_reference(
        self,
        data_brain: DataBrain,
        clean_test_db
    ):
        """Test retrieving a reference."""
        await data_brain.initialize()
        
        reference_id = "test_reference_get"
        reference_type = "file"
        storage_location = "gs://bucket/file2.txt"
        metadata = {
            "file_id": "file_456",
            "file_type": "application/json"
        }
        
        # Register reference
        await data_brain.register_reference(reference_id, reference_type, storage_location, metadata=metadata)
        
        # Retrieve reference
        retrieved = await data_brain.get_reference(reference_id)
        assert retrieved is not None, "Reference should be retrievable"
        assert retrieved.metadata["file_id"] == "file_456", "Reference data should match"
        
        # Try to retrieve non-existent reference
        non_existent = await data_brain.get_reference("non_existent_reference")
        assert non_existent is None, "Non-existent reference should return None"
    
    @pytest.mark.asyncio
    async def test_track_provenance(
        self,
        data_brain: DataBrain,
        clean_test_db
    ):
        """Test tracking data provenance."""
        await data_brain.initialize()
        
        reference_id = "test_provenance_ref"
        reference_type = "file"
        storage_location = "gs://bucket/file3.txt"
        metadata = {"file_id": "file_789"}
        
        # Register reference
        await data_brain.register_reference(reference_id, reference_type, storage_location, metadata=metadata)
        
        # Track provenance
        execution_id = "exec_123"
        operation = "parsing"
        provenance_metadata = {
            "source": "ingestion",
            "transformation": "parsing",
            "timestamp": "2026-01-01T00:00:00Z",
            "operator": "content_realm"
        }
        
        success = await data_brain.track_provenance(
            reference_id,
            execution_id,
            operation,
            metadata=provenance_metadata
        )
        assert success, "Provenance should be tracked"
        
        # Retrieve provenance (returns a list)
        retrieved_provenance = await data_brain.get_provenance(reference_id)
        assert len(retrieved_provenance) > 0, "Provenance should be retrievable"
        assert retrieved_provenance[0].operation == operation, "Provenance operation should match"
        assert retrieved_provenance[0].execution_id == execution_id, "Provenance execution_id should match"
    
    @pytest.mark.asyncio
    async def test_get_provenance(
        self,
        data_brain: DataBrain,
        clean_test_db
    ):
        """Test retrieving provenance."""
        await data_brain.initialize()
        
        reference_id = "test_provenance_get"
        reference_type = "file"
        storage_location = "gs://bucket/file_prov.txt"
        metadata = {"file_id": "file_prov"}
        
        # Register reference and track provenance
        await data_brain.register_reference(reference_id, reference_type, storage_location, metadata=metadata)
        execution_id = "exec_test"
        operation = "test_operation"
        await data_brain.track_provenance(
            reference_id,
            execution_id,
            operation,
            metadata={"source": "test_source"}
        )
        
        # Retrieve provenance (returns a list)
        provenance = await data_brain.get_provenance(reference_id)
        assert len(provenance) > 0, "Provenance should be retrievable"
        assert provenance[0].operation == operation, "Provenance should match"
        
        # Try to retrieve provenance for non-existent reference (returns empty list)
        non_existent_prov = await data_brain.get_provenance("non_existent_reference")
        assert isinstance(non_existent_prov, list), "Should return a list"
        assert len(non_existent_prov) == 0, "Non-existent provenance should return empty list"
    
    @pytest.mark.asyncio
    async def test_multiple_references(
        self,
        data_brain: DataBrain,
        clean_test_db
    ):
        """Test registering and retrieving multiple references."""
        await data_brain.initialize()
        
        # Register multiple references
        references = [
            ("ref_1", "file", "gs://bucket/file_1.txt", {"file_id": "file_1", "value": 1}),
            ("ref_2", "file", "gs://bucket/file_2.txt", {"file_id": "file_2", "value": 2}),
            ("ref_3", "file", "gs://bucket/file_3.txt", {"file_id": "file_3", "value": 3})
        ]
        
        for ref_id, ref_type, storage_loc, metadata in references:
            success = await data_brain.register_reference(ref_id, ref_type, storage_loc, metadata=metadata)
            assert success, f"Reference {ref_id} should be registered"
        
        # Retrieve all references
        for ref_id, ref_type, storage_loc, expected_metadata in references:
            retrieved = await data_brain.get_reference(ref_id)
            assert retrieved is not None, f"Reference {ref_id} should be retrievable"
            assert retrieved.metadata["file_id"] == expected_metadata["file_id"], f"Reference {ref_id} data should match"
    
    @pytest.mark.asyncio
    async def test_provenance_chain(
        self,
        data_brain: DataBrain,
        clean_test_db
    ):
        """Test tracking provenance chain (multiple operations)."""
        await data_brain.initialize()
        
        reference_id = "test_provenance_chain"
        reference_type = "file"
        storage_location = "gs://bucket/file_chain.txt"
        metadata = {"file_id": "file_chain"}
        
        # Register reference
        await data_brain.register_reference(reference_id, reference_type, storage_location, metadata=metadata)
        
        # Track multiple provenance entries (chain)
        await data_brain.track_provenance(
            reference_id,
            "exec_1",
            "upload",
            metadata={"source": "ingestion", "step": 1}
        )
        
        await data_brain.track_provenance(
            reference_id,
            "exec_2",
            "parse",
            metadata={"source": "parsing", "step": 2}
        )
        
        # Retrieve provenance (should include all entries)
        retrieved = await data_brain.get_provenance(reference_id)
        assert len(retrieved) >= 2, "Provenance chain should include multiple entries"
        # Verify operations are tracked
        operations = [p.operation for p in retrieved]
        assert "upload" in operations, "Should include upload operation"
        assert "parse" in operations, "Should include parse operation"
    
    @pytest.mark.asyncio
    async def test_reference_with_metadata(
        self,
        data_brain: DataBrain,
        clean_test_db
    ):
        """Test registering reference with metadata."""
        await data_brain.initialize()
        
        reference_id = "test_metadata_ref"
        reference_type = "file"
        storage_location = "gs://bucket/metadata.txt"
        metadata = {
            "file_id": "file_metadata",
            "uploaded_by": "user_123",
            "uploaded_at": "2026-01-01T00:00:00Z",
            "tags": ["important", "processed"]
        }
        
        success = await data_brain.register_reference(reference_id, reference_type, storage_location, metadata=metadata)
        assert success, "Reference with metadata should be registered"
        
        # Verify metadata is preserved
        retrieved = await data_brain.get_reference(reference_id)
        assert retrieved is not None, "Reference should be retrievable"
        assert retrieved.metadata is not None, "Metadata should be preserved"
        assert retrieved.metadata["uploaded_by"] == "user_123", "Metadata should match"
    
    @pytest.mark.asyncio
    async def test_error_handling(
        self,
        data_brain: DataBrain
    ):
        """Test error handling for invalid operations."""
        await data_brain.initialize()
        
        # Try to get non-existent reference
        retrieved = await data_brain.get_reference("non_existent")
        assert retrieved is None, "Should return None for non-existent reference"
        
        # Try to get provenance for non-existent reference (returns empty list)
        provenance = await data_brain.get_provenance("non_existent")
        assert isinstance(provenance, list), "Should return a list"
        assert len(provenance) == 0, "Should return empty list for non-existent provenance"
