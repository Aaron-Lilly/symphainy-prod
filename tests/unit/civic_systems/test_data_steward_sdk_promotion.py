"""
Unit tests for Data Steward SDK promotion to Record of Fact workflow.

Tests the explicit promotion workflow from Working Material to Record of Fact.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK
from symphainy_platform.civic_systems.smart_city.primitives.data_steward_primitives import DataStewardPrimitives


@pytest.mark.unit
@pytest.mark.civic_systems
class TestDataStewardSDKPromotion:
    """Test Data Steward SDK promotion to Record of Fact."""
    
    @pytest.fixture
    def mock_supabase_adapter(self):
        """Mock Supabase adapter."""
        adapter = Mock()
        adapter.service_client = Mock()
        adapter.service_client.table = Mock(return_value=Mock())
        return adapter
    
    @pytest.fixture
    def mock_data_steward_primitives(self):
        """Mock Data Steward Primitives."""
        primitives = Mock(spec=DataStewardPrimitives)
        primitives.boundary_contract_store = Mock()
        return primitives
    
    @pytest.fixture
    def data_steward_sdk(self, mock_data_steward_primitives):
        """Create DataStewardSDK instance with mocked dependencies."""
        return DataStewardSDK(
            data_steward_primitives=mock_data_steward_primitives
        )
    
    @pytest.mark.asyncio
    async def test_promote_to_record_of_fact_deterministic_embedding(
        self, data_steward_sdk, mock_supabase_adapter, mock_data_steward_primitives
    ):
        """Test promoting deterministic embedding to Record of Fact."""
        # Mock boundary contract validation
        mock_boundary_contract_store = Mock()
        mock_boundary_contract_store.get_boundary_contract_by_id = AsyncMock(return_value={
            "contract_id": "contract_123",
            "materialization_type": "deterministic",
            "access_granted": True
        })
        mock_data_steward_primitives.boundary_contract_store = mock_boundary_contract_store
        
        # Mock Supabase insert
        mock_table = Mock()
        mock_insert = Mock()
        mock_insert.execute.return_value = Mock(
            data=[{
                "record_id": "record_123"
            }]
        )
        mock_table.insert.return_value = mock_insert
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        record_id = await data_steward_sdk.promote_to_record_of_fact(
            source_file_id="file_123",
            source_boundary_contract_id="contract_123",
            tenant_id="tenant_123",
            record_type="deterministic_embedding",
            record_content={"embedding": [0.1, 0.2, 0.3]},
            embedding_id="embedding_123",
            arango_collection="structured_embeddings",
            arango_key="embedding_123",
            model_name="test_model",
            supabase_adapter=mock_supabase_adapter
        )
        
        assert record_id == "record_123"
        assert mock_table.insert.called
    
    @pytest.mark.asyncio
    async def test_promote_to_record_of_fact_semantic_embedding(
        self, data_steward_sdk, mock_supabase_adapter, mock_data_steward_primitives
    ):
        """Test promoting semantic embedding to Record of Fact."""
        # Mock boundary contract validation
        mock_boundary_contract_store = Mock()
        mock_boundary_contract_store.get_boundary_contract_by_id = AsyncMock(return_value={
            "contract_id": "contract_123",
            "materialization_type": "semantic_embedding",
            "access_granted": True
        })
        mock_data_steward_primitives.boundary_contract_store = mock_boundary_contract_store
        
        # Mock Supabase insert
        mock_table = Mock()
        mock_insert = Mock()
        mock_insert.execute.return_value = Mock(
            data=[{
                "record_id": "record_456"
            }]
        )
        mock_table.insert.return_value = mock_insert
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        record_id = await data_steward_sdk.promote_to_record_of_fact(
            source_file_id="file_123",
            source_boundary_contract_id="contract_123",
            tenant_id="tenant_123",
            record_type="semantic_embedding",
            record_content={"embedding": [0.4, 0.5, 0.6]},
            embedding_id="embedding_456",
            arango_collection="structured_embeddings",
            arango_key="embedding_456",
            model_name="semantic_model",
            supabase_adapter=mock_supabase_adapter
        )
        
        assert record_id == "record_456"
    
    @pytest.mark.asyncio
    async def test_promote_to_record_of_fact_interpretation(
        self, data_steward_sdk, mock_supabase_adapter, mock_data_steward_primitives
    ):
        """Test promoting interpretation to Record of Fact."""
        # Mock boundary contract validation
        mock_boundary_contract_store = Mock()
        mock_boundary_contract_store.get_boundary_contract_by_id = AsyncMock(return_value={
            "contract_id": "contract_123",
            "materialization_type": "deterministic",
            "access_granted": True
        })
        mock_data_steward_primitives.boundary_contract_store = mock_boundary_contract_store
        
        # Mock Supabase insert
        mock_table = Mock()
        mock_insert = Mock()
        mock_insert.execute.return_value = Mock(
            data=[{
                "record_id": "record_789"
            }]
        )
        mock_table.insert.return_value = mock_insert
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        record_id = await data_steward_sdk.promote_to_record_of_fact(
            source_file_id="file_123",
            source_boundary_contract_id="contract_123",
            tenant_id="tenant_123",
            record_type="interpretation",
            record_content={
                "entities": ["entity1", "entity2"],
                "relationships": [{"from": "entity1", "to": "entity2"}]
            },
            interpretation_id="interpretation_123",
            confidence_score=0.95,
            supabase_adapter=mock_supabase_adapter
        )
        
        assert record_id == "record_789"
    
    @pytest.mark.asyncio
    async def test_promote_to_record_of_fact_invalid_type(
        self, data_steward_sdk, mock_supabase_adapter
    ):
        """Test that invalid record_type is rejected."""
        record_id = await data_steward_sdk.promote_to_record_of_fact(
            source_file_id="file_123",
            source_boundary_contract_id="contract_123",
            tenant_id="tenant_123",
            record_type="invalid_type",
            record_content={},
            supabase_adapter=mock_supabase_adapter
        )
        
        assert record_id is None
    
    @pytest.mark.asyncio
    async def test_promote_to_record_of_fact_missing_boundary_contract(
        self, data_steward_sdk, mock_supabase_adapter, mock_data_steward_primitives
    ):
        """Test that promotion fails if boundary contract not found."""
        # Mock boundary contract not found
        mock_boundary_contract_store = Mock()
        mock_boundary_contract_store.get_boundary_contract_by_id = AsyncMock(return_value=None)
        mock_data_steward_primitives.boundary_contract_store = mock_boundary_contract_store
        
        record_id = await data_steward_sdk.promote_to_record_of_fact(
            source_file_id="file_123",
            source_boundary_contract_id="nonexistent_contract",
            tenant_id="tenant_123",
            record_type="deterministic_embedding",
            record_content={},
            supabase_adapter=mock_supabase_adapter
        )
        
        assert record_id is None
    
    @pytest.mark.asyncio
    async def test_promote_to_record_of_fact_no_supabase_adapter(
        self, data_steward_sdk
    ):
        """Test that promotion fails if Supabase adapter not available."""
        record_id = await data_steward_sdk.promote_to_record_of_fact(
            source_file_id="file_123",
            source_boundary_contract_id="contract_123",
            tenant_id="tenant_123",
            record_type="deterministic_embedding",
            record_content={},
            supabase_adapter=None
        )
        
        assert record_id is None
    
    @pytest.mark.asyncio
    async def test_promote_to_record_of_fact_with_promotion_metadata(
        self, data_steward_sdk, mock_supabase_adapter, mock_data_steward_primitives
    ):
        """Test promotion with promotion metadata (promoted_by, promotion_reason)."""
        # Mock boundary contract validation
        mock_boundary_contract_store = Mock()
        mock_boundary_contract_store.get_boundary_contract_by_id = AsyncMock(return_value={
            "contract_id": "contract_123",
            "materialization_type": "deterministic",
            "access_granted": True
        })
        mock_data_steward_primitives.boundary_contract_store = mock_boundary_contract_store
        
        # Mock Supabase insert
        mock_table = Mock()
        mock_insert = Mock()
        mock_insert.execute.return_value = Mock(
            data=[{
                "record_id": "record_123"
            }]
        )
        mock_table.insert.return_value = mock_insert
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        record_id = await data_steward_sdk.promote_to_record_of_fact(
            source_file_id="file_123",
            source_boundary_contract_id="contract_123",
            tenant_id="tenant_123",
            record_type="deterministic_embedding",
            record_content={},
            promoted_by="user_123",
            promotion_reason="Embedding created for semantic search",
            supabase_adapter=mock_supabase_adapter
        )
        
        assert record_id == "record_123"
        
        # Verify promotion metadata was included
        call_args = mock_table.insert.call_args
        inserted_data = call_args[0][0]
        assert inserted_data.get("promoted_by") == "user_123"
        assert inserted_data.get("promotion_reason") == "Embedding created for semantic search"
    
    @pytest.mark.asyncio
    async def test_promote_to_record_of_fact_source_expired_tracking(
        self, data_steward_sdk, mock_supabase_adapter, mock_data_steward_primitives
    ):
        """Test that source_expired_at is initially NULL (tracked separately)."""
        # Mock boundary contract validation
        mock_boundary_contract_store = Mock()
        mock_boundary_contract_store.get_boundary_contract_by_id = AsyncMock(return_value={
            "contract_id": "contract_123",
            "materialization_type": "deterministic",
            "access_granted": True
        })
        mock_data_steward_primitives.boundary_contract_store = mock_boundary_contract_store
        
        # Mock Supabase insert
        mock_table = Mock()
        mock_insert = Mock()
        mock_insert.execute.return_value = Mock(
            data=[{
                "record_id": "record_123"
            }]
        )
        mock_table.insert.return_value = mock_insert
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        record_id = await data_steward_sdk.promote_to_record_of_fact(
            source_file_id="file_123",
            source_boundary_contract_id="contract_123",
            tenant_id="tenant_123",
            record_type="deterministic_embedding",
            record_content={},
            supabase_adapter=mock_supabase_adapter
        )
        
        assert record_id == "record_123"
        
        # Verify source_expired_at is NULL initially
        call_args = mock_table.insert.call_args
        inserted_data = call_args[0][0]
        assert inserted_data.get("source_expired_at") is None
