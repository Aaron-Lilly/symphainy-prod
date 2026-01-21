"""
Unit tests for Materialization Policy Store.

Tests database-backed policy store with tenant-scoped support and platform defaults.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from symphainy_platform.civic_systems.smart_city.stores.materialization_policy_store import MaterializationPolicyStore


@pytest.mark.unit
@pytest.mark.civic_systems
class TestMaterializationPolicyStore:
    """Test Materialization Policy Store."""
    
    @pytest.fixture
    def mock_supabase_adapter(self):
        """Mock Supabase adapter."""
        adapter = Mock()
        adapter.service_client = Mock()
        adapter.service_client.table = Mock(return_value=Mock())
        return adapter
    
    @pytest.fixture
    def policy_store(self, mock_supabase_adapter):
        """Create MaterializationPolicyStore instance with mocked Supabase adapter."""
        return MaterializationPolicyStore(supabase_adapter=mock_supabase_adapter)
    
    @pytest.fixture
    def policy_store_no_adapter(self):
        """Create MaterializationPolicyStore without Supabase adapter (fallback mode)."""
        return MaterializationPolicyStore(supabase_adapter=None)
    
    @pytest.mark.asyncio
    async def test_get_mvp_permissive_policy_fallback(self, policy_store_no_adapter):
        """Test that MVP permissive policy is returned when no database available."""
        policy = await policy_store_no_adapter.get_policy()
        
        assert policy is not None
        assert policy.get("allow_all_types") is True
        assert policy.get("default_ttl_days") == 30
        assert policy.get("default_backing_store") == "gcs"
        assert policy.get("no_restrictions") is True
    
    @pytest.mark.asyncio
    async def test_get_platform_default_policy(self, policy_store, mock_supabase_adapter):
        """Test getting platform default policy from database."""
        # Mock database response
        mock_table = Mock()
        mock_query = Mock()
        mock_query.is_.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = Mock(
            data=[{
                "policy_id": "policy_123",
                "policy_rules": {
                    "allow_all_types": True,
                    "default_ttl_days": 30,
                    "default_backing_store": "gcs"
                }
            }]
        )
        mock_table.select.return_value = mock_query
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        policy = await policy_store.get_policy()
        
        assert policy is not None
        assert policy.get("allow_all_types") is True
        assert policy.get("default_ttl_days") == 30
    
    @pytest.mark.asyncio
    async def test_get_tenant_policy(self, policy_store, mock_supabase_adapter):
        """Test getting tenant-specific policy."""
        # Mock database response for tenant policy
        mock_table = Mock()
        mock_query = Mock()
        mock_query.eq.return_value = mock_query
        mock_query.is_.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = Mock(
            data=[{
                "policy_id": "tenant_policy_123",
                "policy_rules": {
                    "allow_all_types": False,
                    "allowed_types": ["full_artifact"],
                    "default_ttl_days": 7
                }
            }]
        )
        mock_table.select.return_value = mock_query
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        policy = await policy_store.get_policy(tenant_id="tenant_123")
        
        assert policy is not None
        assert policy.get("allow_all_types") is False
        assert policy.get("allowed_types") == ["full_artifact"]
    
    @pytest.mark.asyncio
    async def test_policy_resolution_order_solution_first(self, policy_store, mock_supabase_adapter):
        """Test that solution policy takes precedence over tenant policy."""
        # Mock: Solution policy exists
        def mock_table_side_effect(table_name):
            mock_table = Mock()
            mock_query = Mock()
            
            if table_name == "materialization_policies":
                # First call: solution policy (should be returned)
                if not hasattr(mock_table_side_effect, 'call_count'):
                    mock_table_side_effect.call_count = 0
                mock_table_side_effect.call_count += 1
                
                if mock_table_side_effect.call_count == 1:
                    # Solution policy query
                    mock_query.eq.return_value = mock_query
                    mock_query.order.return_value = mock_query
                    mock_query.limit.return_value = mock_query
                    mock_query.execute.return_value = Mock(
                        data=[{
                            "policy_rules": {
                                "allow_all_types": True,
                                "default_ttl_days": 60,  # Solution-specific TTL
                                "policy_version": "solution_1.0"
                            }
                        }]
                    )
            
            mock_table.select.return_value = mock_query
            return mock_table
        
        mock_supabase_adapter.service_client.table.side_effect = mock_table_side_effect
        
        policy = await policy_store.get_policy(tenant_id="tenant_123", solution_id="solution_123")
        
        assert policy is not None
        assert policy.get("default_ttl_days") == 60  # Solution policy TTL
    
    @pytest.mark.asyncio
    async def test_evaluate_policy_allow_all_types(self, policy_store_no_adapter):
        """Test policy evaluation when allow_all_types is True (MVP permissive)."""
        decision = await policy_store_no_adapter.evaluate_policy(
            artifact_type="file",
            requested_type="full_artifact"
        )
        
        assert decision.get("allowed") is True
        assert decision.get("materialization_type") == "full_artifact"
        assert decision.get("backing_store") == "gcs"
        assert decision.get("ttl_days") == 30
    
    @pytest.mark.asyncio
    async def test_evaluate_policy_allowed_type(self, policy_store, mock_supabase_adapter):
        """Test policy evaluation when requested type is in allowed_types."""
        # Mock policy that doesn't allow all types
        mock_table = Mock()
        mock_query = Mock()
        mock_query.is_.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = Mock(
            data=[{
                "policy_rules": {
                    "allow_all_types": False,
                    "allowed_types": ["full_artifact", "deterministic"],
                    "default_ttl_days": 7,
                    "default_backing_store": "gcs"
                }
            }]
        )
        mock_table.select.return_value = mock_query
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        decision = await policy_store.evaluate_policy(
            artifact_type="file",
            requested_type="full_artifact"
        )
        
        assert decision.get("allowed") is True
        assert decision.get("materialization_type") == "full_artifact"
    
    @pytest.mark.asyncio
    async def test_evaluate_policy_denied_type(self, policy_store, mock_supabase_adapter):
        """Test policy evaluation when requested type is not allowed."""
        # Mock policy that doesn't allow the requested type
        mock_table = Mock()
        mock_query = Mock()
        mock_query.is_.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = Mock(
            data=[{
                "policy_rules": {
                    "allow_all_types": False,
                    "allowed_types": ["deterministic"],  # full_artifact not allowed
                    "default_ttl_days": 7
                }
            }]
        )
        mock_table.select.return_value = mock_query
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        decision = await policy_store.evaluate_policy(
            artifact_type="file",
            requested_type="full_artifact"  # Not in allowed_types
        )
        
        assert decision.get("allowed") is False
        assert decision.get("materialization_type") is None
    
    @pytest.mark.asyncio
    async def test_evaluate_policy_with_ttl(self, policy_store_no_adapter):
        """Test policy evaluation includes TTL from policy."""
        decision = await policy_store_no_adapter.evaluate_policy(
            artifact_type="file",
            requested_type="full_artifact"
        )
        
        assert decision.get("ttl_days") == 30  # From MVP policy
    
    @pytest.mark.asyncio
    async def test_create_tenant_policy(self, policy_store, mock_supabase_adapter):
        """Test creating a tenant-specific policy."""
        # Mock database insert
        mock_table = Mock()
        mock_insert = Mock()
        mock_insert.execute.return_value = Mock(
            data=[{
                "policy_id": "new_policy_123"
            }]
        )
        mock_table.insert.return_value = mock_insert
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        policy_id = await policy_store.create_tenant_policy(
            tenant_id="tenant_123",
            policy_rules={
                "allow_all_types": False,
                "allowed_types": ["deterministic"],
                "default_ttl_days": 7
            },
            policy_name="Strict Tenant Policy"
        )
        
        assert policy_id == "new_policy_123"
        assert mock_table.insert.called
    
    @pytest.mark.asyncio
    async def test_policy_caching(self, policy_store, mock_supabase_adapter):
        """Test that policies are cached after first lookup."""
        # Mock database response
        mock_table = Mock()
        mock_query = Mock()
        mock_query.is_.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.execute.return_value = Mock(
            data=[{
                "policy_rules": {
                    "allow_all_types": True,
                    "default_ttl_days": 30
                }
            }]
        )
        mock_table.select.return_value = mock_query
        mock_supabase_adapter.service_client.table.return_value = mock_table
        
        # First call
        policy1 = await policy_store.get_policy(tenant_id="tenant_123")
        
        # Second call (should use cache)
        policy2 = await policy_store.get_policy(tenant_id="tenant_123")
        
        assert policy1 == policy2
        # Verify database was only queried once (cached on second call)
        assert mock_table.select.call_count == 1
