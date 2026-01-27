"""
Data Steward Test Fixtures

Shared fixtures for providing Data Steward SDK in tests.
"""

import pytest
from typing import Optional, Any


@pytest.fixture
def data_steward_sdk():
    """
    Create Data Steward SDK for boundary contract assignment in tests.
    
    This fixture provides a Data Steward SDK with MaterializationPolicyStore
    for use in ExecutionLifecycleManager tests.
    """
    try:
        from symphainy_platform.civic_systems.smart_city.stores.materialization_policy_store import (
            MaterializationPolicyStore
        )
        from symphainy_platform.civic_systems.smart_city.primitives.data_steward_primitives import (
            DataStewardPrimitives,
            BoundaryContractStore
        )
        from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK
        
        # Create MaterializationPolicyStore (will use built-in default if Supabase not available)
        materialization_policy_store = MaterializationPolicyStore(supabase_adapter=None)
        
        # Create BoundaryContractStore (can work without Supabase for tests)
        boundary_contract_store = BoundaryContractStore(supabase_adapter=None)
        
        # Create Data Steward Primitives with MaterializationPolicyStore
        data_steward_primitives = DataStewardPrimitives(
            policy_store=None,  # Legacy - kept for backward compatibility
            boundary_contract_store=boundary_contract_store,
            materialization_policy_store=materialization_policy_store  # ✅ Required for configurable policy
        )
        
        # Create Data Steward SDK
        data_steward_sdk = DataStewardSDK(
            data_governance_abstraction=None,
            policy_resolver=None,
            data_steward_primitives=data_steward_primitives,
            materialization_policy=materialization_policy_store
        )
        
        return data_steward_sdk
    except Exception as e:
        pytest.skip(f"Data Steward SDK not available: {e}")


def create_data_steward_sdk(supabase_adapter: Optional[Any] = None) -> Optional[Any]:
    """
    Helper function to create Data Steward SDK (for use in non-fixture contexts).
    
    Args:
        supabase_adapter: Optional Supabase adapter (if None, uses built-in defaults)
    
    Returns:
        DataStewardSDK instance or None if creation fails
    """
    try:
        from symphainy_platform.civic_systems.smart_city.stores.materialization_policy_store import (
            MaterializationPolicyStore
        )
        from symphainy_platform.civic_systems.smart_city.primitives.data_steward_primitives import (
            DataStewardPrimitives,
            BoundaryContractStore
        )
        from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK
        
        # Create MaterializationPolicyStore
        materialization_policy_store = MaterializationPolicyStore(supabase_adapter=supabase_adapter)
        
        # Create BoundaryContractStore
        boundary_contract_store = BoundaryContractStore(supabase_adapter=supabase_adapter)
        
        # Create Data Steward Primitives with MaterializationPolicyStore
        data_steward_primitives = DataStewardPrimitives(
            policy_store=None,  # Legacy
            boundary_contract_store=boundary_contract_store,
            materialization_policy_store=materialization_policy_store  # ✅ Required
        )
        
        # Create Data Steward SDK
        data_steward_sdk = DataStewardSDK(
            data_governance_abstraction=None,
            policy_resolver=None,
            data_steward_primitives=data_steward_primitives,
            materialization_policy=materialization_policy_store
        )
        
        return data_steward_sdk
    except Exception as e:
        return None
