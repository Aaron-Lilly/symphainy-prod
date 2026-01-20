"""
Integration tests for the four-class data framework architecture.

Tests the complete data flow:
- Working Material → Record of Fact → Purpose-Bound Outcome → Platform DNA
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timedelta

# Import components
from symphainy_platform.civic_systems.artifact_plane.artifact_plane import ArtifactPlane
from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK
from symphainy_platform.civic_systems.smart_city.services.curator_service import CuratorService
from symphainy_platform.civic_systems.smart_city.primitives.curator_primitives import CuratorPrimitives
from symphainy_platform.civic_systems.smart_city.stores.materialization_policy_store import MaterializationPolicyStore
from symphainy_platform.runtime.execution_context import ExecutionContext


@pytest.mark.integration
class TestFourClassDataFramework:
    """Integration tests for the four-class data framework."""
    
    @pytest.fixture
    def mock_supabase_adapter(self):
        """Mock Supabase adapter with realistic responses."""
        adapter = Mock()
        adapter.service_client = Mock()
        
        # Mock table responses
        def mock_table(table_name):
            table = Mock()
            
            if table_name == "artifacts":
                # Mock artifacts table
                table.insert = Mock(return_value=Mock(
                    execute=Mock(return_value=Mock(
                        data=[{"artifact_id": "artifact_123", "created_at": datetime.now().isoformat()}]
                    ))
                ))
                table.select = Mock(return_value=Mock(
                    eq=Mock(return_value=Mock(
                        execute=Mock(return_value=Mock(data=[]))
                    ))
                ))
            elif table_name == "materialization_policies":
                # Mock materialization policies table
                table.select = Mock(return_value=Mock(
                    eq=Mock(return_value=Mock(
                        is_=Mock(return_value=Mock(
                            execute=Mock(return_value=Mock(
                                data=[{
                                    "policy_id": "policy_123",
                                    "policy_rules": {
                                        "allow_all_types": True,
                                        "default_ttl_days": 30,
                                        "default_backing_store": "gcs"
                                    }
                                }]
                            ))
                        ))
                    ))
                ))
            elif table_name in ["solution_registry", "intent_registry", "realm_registry"]:
                # Mock registry tables
                table.insert = Mock(return_value=Mock(
                    execute=Mock(return_value=Mock(
                        data=[{"registry_id": f"registry_{table_name}_123"}]
                    ))
                ))
            elif table_name == "records_of_fact":
                # Mock records_of_fact table
                table.insert = Mock(return_value=Mock(
                    execute=Mock(return_value=Mock(
                        data=[{"record_id": "record_123"}]
                    ))
                ))
            
            return table
        
        adapter.service_client.table = mock_table
        return adapter
    
    @pytest.fixture
    def mock_state_management(self):
        """Mock state management protocol."""
        state_mgmt = Mock()
        state_mgmt.store_state = AsyncMock(return_value=True)
        state_mgmt.retrieve_state = AsyncMock(return_value={
            "artifact_id": "artifact_123",
            "artifact_type": "blueprint",
            "lifecycle_state": "draft",
            "tenant_id": "tenant_123"
        })
        state_mgmt.list_states = AsyncMock(return_value=[])
        state_mgmt.update_state = AsyncMock(return_value=True)
        return state_mgmt
    
    @pytest.fixture
    def mock_artifact_storage(self):
        """Mock artifact storage protocol."""
        storage = Mock()
        storage.store_artifact = AsyncMock(return_value={"storage_path": "gs://bucket/artifact_123"})
        storage.get_artifact = AsyncMock(return_value={"payload": "test_payload"})
        return storage
    
    @pytest.fixture
    def artifact_plane(self, mock_artifact_storage, mock_state_management):
        """Create ArtifactPlane instance."""
        return ArtifactPlane(
            artifact_storage=mock_artifact_storage,
            state_management=mock_state_management
        )
    
    @pytest.fixture
    def materialization_policy_store(self, mock_supabase_adapter):
        """Create MaterializationPolicyStore instance."""
        return MaterializationPolicyStore(supabase_adapter=mock_supabase_adapter)
    
    @pytest.fixture
    def data_steward_sdk(self, mock_supabase_adapter, materialization_policy_store):
        """Create DataStewardSDK instance."""
        # DataStewardSDK needs materialization_policy_store passed as materialization_policy
        return DataStewardSDK(
            materialization_policy=materialization_policy_store
        )
    
    @pytest.fixture
    def curator_primitives(self):
        """Create CuratorPrimitives instance."""
        return CuratorPrimitives()
    
    @pytest.fixture
    def curator_service(self, mock_supabase_adapter, artifact_plane, curator_primitives):
        """Create CuratorService instance."""
        return CuratorService(
            supabase_adapter=mock_supabase_adapter,
            artifact_plane=artifact_plane,
            curator_primitives=curator_primitives
        )
    
    @pytest.fixture
    def execution_context(self):
        """Create execution context."""
        return ExecutionContext(
            tenant_id="tenant_123",
            user_id="user_123",
            session_id="session_123",
            solution_id="solution_123"
        )
    
    @pytest.mark.asyncio
    async def test_working_material_to_record_of_fact(
        self, data_steward_sdk, mock_supabase_adapter
    ):
        """Test promotion from Working Material to Record of Fact."""
        # Promote to Record of Fact
        record_id = await data_steward_sdk.promote_to_record_of_fact(
            source_file_id="file_123",
            source_boundary_contract_id="contract_123",
            tenant_id="tenant_123",
            record_type="semantic_embedding",
            record_content={"embedding": [0.1, 0.2, 0.3], "text": "test content"},
            promoted_by="system",
            promotion_reason="Test promotion"
        )
        
        # Verify promotion succeeded
        assert record_id is not None
        # Verify records_of_fact table was queried/inserted
        assert mock_supabase_adapter.service_client.table.called
    
    @pytest.mark.asyncio
    async def test_purpose_bound_outcome_creation(
        self, artifact_plane, execution_context
    ):
        """Test creation of Purpose-Bound Outcome in Artifact Plane."""
        # Create artifact (Purpose-Bound Outcome)
        artifact_result = await artifact_plane.create_artifact(
            artifact_type="blueprint",
            artifact_id="blueprint_123",
            payload={
                "semantic_payload": {
                    "blueprint_id": "blueprint_123",
                    "components": ["component1", "component2"]
                }
            },
            context=execution_context,
            lifecycle_state="draft",
            owner="client",
            purpose="delivery"
        )
        
        # Verify artifact was created
        assert artifact_result is not None
        assert artifact_result.get("artifact_id") == "blueprint_123"
        assert artifact_plane.artifact_storage.store_artifact.called
        assert artifact_plane.state_management.store_state.called
    
    @pytest.mark.asyncio
    async def test_lifecycle_transition(
        self, artifact_plane, execution_context
    ):
        """Test lifecycle state transition (draft → accepted)."""
        # Create artifact in draft state
        await artifact_plane.create_artifact(
            artifact_type="blueprint",
            artifact_id="blueprint_123",
            payload={"test": "data"},
            context=execution_context,
            lifecycle_state="draft"
        )
        
        # Transition to accepted
        success = await artifact_plane.transition_lifecycle_state(
            artifact_id="blueprint_123",
            tenant_id="tenant_123",
            new_state="accepted",
            transitioned_by="user_123",
            reason="Approved for production"
        )
        
        # Verify transition succeeded
        assert success is True
        assert artifact_plane.state_management.update_state.called
    
    @pytest.mark.asyncio
    async def test_purpose_bound_outcome_to_platform_dna(
        self, curator_service, artifact_plane, execution_context
    ):
        """Test promotion from Purpose-Bound Outcome to Platform DNA."""
        # Create artifact (Purpose-Bound Outcome)
        artifact_result = await artifact_plane.create_artifact(
            artifact_type="blueprint",
            artifact_id="blueprint_123",
            payload={
                "semantic_payload": {
                    "blueprint_id": "blueprint_123",
                    "components": ["component1"]
                }
            },
            context=execution_context,
            lifecycle_state="accepted"  # Must be accepted for promotion
        )
        
        artifact_id = artifact_result.get("artifact_id")
        
        # Promote to Platform DNA
        registry_id = await curator_service.promote_to_platform_dna(
            artifact_id=artifact_id,
            tenant_id="tenant_123",
            registry_type="solution",
            registry_name="Test Solution",
            promoted_by="curator_123"
        )
        
        # Verify promotion succeeded
        assert registry_id is not None
    
    @pytest.mark.asyncio
    async def test_full_data_flow(
        self, data_steward_sdk, artifact_plane, curator_service, execution_context, mock_supabase_adapter
    ):
        """Test complete data flow: Working Material → Record of Fact → Purpose-Bound Outcome → Platform DNA."""
        tenant_id = "tenant_123"
        
        # Step 1: Create Working Material (via boundary contract)
        # (In real flow, this would be created by Data Steward)
        
        # Step 2: Promote to Record of Fact
        record_id = await data_steward_sdk.promote_to_record_of_fact(
            source_file_id="file_123",
            source_boundary_contract_id="contract_123",
            tenant_id=tenant_id,
            record_type="interpretation",
            record_content={"interpretation": "This is a test interpretation"},
            promoted_by="system",
            supabase_adapter=mock_supabase_adapter
        )
        
        # Step 3: Create Purpose-Bound Outcome from Record of Fact
        artifact_result = await artifact_plane.create_artifact(
            artifact_type="blueprint",
            artifact_id="blueprint_123",
            payload={
                "semantic_payload": {
                    "blueprint_id": "blueprint_123",
                    "source_record_id": record_id
                }
            },
            context=execution_context,
            lifecycle_state="draft"
        )
        
        # Step 4: Transition to accepted
        await artifact_plane.transition_lifecycle_state(
            artifact_id=artifact_result.get("artifact_id"),
            tenant_id=tenant_id,
            new_state="accepted",
            transitioned_by="user_123"
        )
        
        # Step 5: Promote to Platform DNA
        registry_id = await curator_service.promote_to_platform_dna(
            artifact_id=artifact_result.get("artifact_id"),
            tenant_id=tenant_id,
            registry_type="solution",
            registry_name="Test Solution",
            promoted_by="curator_123"
        )
        
        # Verify complete flow succeeded
        assert record_id is not None
        assert artifact_result is not None
        assert registry_id is not None
    
    @pytest.mark.asyncio
    async def test_materialization_policy_evaluation(
        self, materialization_policy_store
    ):
        """Test materialization policy evaluation."""
        # Get policy
        policy = await materialization_policy_store.get_policy(
            tenant_id="tenant_123"
        )
        
        # Verify policy structure
        assert policy is not None
        assert "allow_all_types" in policy or "allowed_types" in policy
        
        # Evaluate policy
        decision = await materialization_policy_store.evaluate_policy(
            artifact_type="file",
            tenant_id="tenant_123",
            requested_type="full_artifact"
        )
        
        # Verify decision
        assert decision is not None
        assert decision.get("allowed") is True
        assert decision.get("materialization_type") is not None
    
    @pytest.mark.asyncio
    async def test_cross_realm_artifact_retrieval(
        self, artifact_plane, execution_context
    ):
        """Test that artifacts can be retrieved across realms."""
        # Create artifact in one realm
        artifact_result = await artifact_plane.create_artifact(
            artifact_type="blueprint",
            artifact_id="blueprint_123",
            payload={"test": "data"},
            context=execution_context
        )
        
        artifact_id = artifact_result.get("artifact_id")
        
        # Retrieve artifact (should work from any realm)
        retrieved = await artifact_plane.get_artifact(
            artifact_id=artifact_id,
            tenant_id="tenant_123"
        )
        
        # Verify retrieval succeeded
        assert retrieved is not None
        assert retrieved.get("artifact_id") == artifact_id
    
    @pytest.mark.asyncio
    async def test_artifact_dependencies(
        self, artifact_plane, execution_context
    ):
        """Test artifact dependency tracking."""
        # Create source artifact
        source_result = await artifact_plane.create_artifact(
            artifact_type="workflow",
            artifact_id="workflow_123",
            payload={"test": "workflow"},
            context=execution_context
        )
        
        # Create dependent artifact
        dependent_result = await artifact_plane.create_artifact(
            artifact_type="blueprint",
            artifact_id="blueprint_123",
            payload={"test": "blueprint"},
            context=execution_context,
            source_artifact_ids=[source_result.get("artifact_id")]
        )
        
        # Verify dependency was tracked
        assert dependent_result is not None
        assert dependent_result.get("artifact_id") == "blueprint_123"
        
        # Verify source_artifact_ids were stored
        stored_data = artifact_plane.state_management.store_state.call_args[0][1]
        assert "source_artifact_ids" in stored_data or stored_data.get("source_artifact_ids") == [source_result.get("artifact_id")]
