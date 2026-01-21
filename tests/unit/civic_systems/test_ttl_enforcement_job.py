"""
Unit tests for TTL Enforcement Job.

Tests automated purge of expired Working Materials.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from symphainy_platform.civic_systems.smart_city.jobs.ttl_enforcement_job import TTLEnforcementJob


@pytest.mark.unit
@pytest.mark.civic_systems
class TestTTLEnforcementJob:
    """Test TTL Enforcement Job."""
    
    @pytest.fixture
    def mock_supabase_adapter(self):
        """Mock Supabase adapter."""
        adapter = Mock()
        adapter.service_client = Mock()
        adapter.service_client.table = Mock(return_value=Mock())
        return adapter
    
    @pytest.fixture
    def mock_gcs_adapter(self):
        """Mock GCS adapter."""
        adapter = Mock()
        adapter.delete_blob = AsyncMock(return_value=True)
        return adapter
    
    @pytest.fixture
    def ttl_job(self, mock_supabase_adapter, mock_gcs_adapter):
        """Create TTLEnforcementJob instance with mocked dependencies."""
        return TTLEnforcementJob(
            supabase_adapter=mock_supabase_adapter,
            gcs_adapter=mock_gcs_adapter
        )
    
    @pytest.mark.asyncio
    async def test_find_expired_contracts(self, ttl_job, mock_supabase_adapter):
        """Test finding expired boundary contracts."""
        # Mock database response
        mock_table = Mock()
        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.lt.return_value = mock_query
        mock_query.execute.return_value = Mock(
            data=[
                {"contract_id": "contract_1", "materialization_expires_at": "2026-01-01T00:00:00Z"},
                {"contract_id": "contract_2", "materialization_expires_at": "2026-01-02T00:00:00Z"}
            ]
        )
        mock_table.select.return_value = mock_query
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        expired_contracts = await ttl_job._find_expired_contracts()
        
        assert len(expired_contracts) == 2
        assert expired_contracts[0]["contract_id"] == "contract_1"
    
    @pytest.mark.asyncio
    async def test_process_expired_contract_full_artifact(
        self, ttl_job, mock_supabase_adapter, mock_gcs_adapter
    ):
        """Test processing expired contract with full_artifact materialization."""
        contract = {
            "contract_id": "contract_123",
            "tenant_id": "tenant_123",
            "materialization_type": "full_artifact",
            "external_source_identifier": "gs://bucket/path/to/file",
            "external_source_metadata": {
                "file_id": "file_123",
                "file_path": "gs://bucket/path/to/file"
            }
        }
        
        # Mock contract status update
        mock_table = Mock()
        mock_update = Mock()
        mock_update.eq.return_value = mock_update
        mock_update.execute.return_value = Mock(data=[{"contract_id": "contract_123"}])
        mock_table.update.return_value = mock_update
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        results = {
            "expired_contracts_found": 0,
            "materials_purged": 0,
            "contracts_updated": 0,
            "records_of_fact_updated": 0,
            "errors": []
        }
        
        await ttl_job._process_expired_contract(contract, results)
        
        assert results["materials_purged"] == 1
        assert results["contracts_updated"] == 1
        assert mock_gcs_adapter.delete_blob.called
    
    @pytest.mark.asyncio
    async def test_process_expired_contract_updates_records_of_fact(
        self, ttl_job, mock_supabase_adapter, mock_gcs_adapter
    ):
        """Test that processing expired contract updates Records of Fact."""
        contract = {
            "contract_id": "contract_123",
            "tenant_id": "tenant_123",
            "materialization_type": "full_artifact",
            "external_source_metadata": {
                "file_id": "file_123"
            }
        }
        
        # Mock contract status update
        mock_table = Mock()
        mock_update = Mock()
        mock_update.eq.return_value = mock_update
        mock_update.is_.return_value = mock_update
        mock_update.execute.return_value = Mock(data=[
            {"record_id": "record_1"},
            {"record_id": "record_2"}
        ])
        mock_table.update.return_value = mock_update
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        results = {
            "expired_contracts_found": 0,
            "materials_purged": 0,
            "contracts_updated": 0,
            "records_of_fact_updated": 0,
            "errors": []
        }
        
        await ttl_job._process_expired_contract(contract, results)
        
        assert results["records_of_fact_updated"] == 2
    
    @pytest.mark.asyncio
    async def test_run_job(self, ttl_job, mock_supabase_adapter, mock_gcs_adapter):
        """Test running the full TTL enforcement job."""
        # Mock finding expired contracts
        mock_table = Mock()
        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.lt.return_value = mock_query
        mock_query.execute.return_value = Mock(
            data=[
                {
                    "contract_id": "contract_1",
                    "tenant_id": "tenant_123",
                    "materialization_type": "full_artifact",
                    "external_source_metadata": {"file_id": "file_1"}
                }
            ]
        )
        mock_table.select.return_value = mock_query
        mock_table.update.return_value = Mock()
        mock_table.update.return_value.eq.return_value = Mock()
        mock_table.update.return_value.is_.return_value = Mock()
        mock_table.update.return_value.execute.return_value = Mock(data=[{"contract_id": "contract_1"}])
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        results = await ttl_job.run()
        
        assert results["expired_contracts_found"] == 1
        assert results["contracts_updated"] == 1
        assert len(results["errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_run_job_no_supabase_adapter(self):
        """Test that job fails gracefully if Supabase adapter not available."""
        job = TTLEnforcementJob(supabase_adapter=None)
        
        results = await job.run()
        
        assert len(results["errors"]) > 0
        assert "Supabase adapter not available" in results["errors"][0]
    
    @pytest.mark.asyncio
    async def test_extract_file_path_from_metadata(self, ttl_job):
        """Test extracting file path from contract metadata."""
        contract = {
            "external_source_metadata": {
                "file_path": "gs://bucket/path/to/file"
            }
        }
        
        file_path = ttl_job._extract_file_path(contract)
        
        assert file_path == "gs://bucket/path/to/file"
    
    @pytest.mark.asyncio
    async def test_extract_file_path_from_identifier(self, ttl_job):
        """Test extracting file path from external_source_identifier."""
        contract = {
            "external_source_identifier": "gs://bucket/path/to/file"
        }
        
        file_path = ttl_job._extract_file_path(contract)
        
        assert file_path == "gs://bucket/path/to/file"
