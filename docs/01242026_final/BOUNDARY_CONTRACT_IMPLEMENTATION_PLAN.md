# Boundary Contract Policy Assignment - Implementation Plan

**Date:** January 25, 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION**  
**CTO Answers:** ✅ **VALIDATED**

---

## Executive Summary

**Goal:** Move boundary contract assignment (policy decisions) from Runtime Plane to Civic Systems (Data Steward Primitives).

**Key Decisions (CTO Validated):**
1. ✅ Runtime should fail if Data Steward is unavailable
2. ✅ Default policy should be configurable via policy store (not hardcoded)
3. ✅ ExecutionLifecycleManager calls Data Steward directly (no Traffic Cop routing)

---

## Implementation Steps

### Step 1: Update Data Steward Primitives to Use Policy Store

**File:** `symphainy_platform/civic_systems/smart_city/primitives/data_steward_primitives.py`

**Changes:**
1. Ensure `materialization_policy_store` is passed to `__init__` and stored
2. Update `request_data_access()` to use `MaterializationPolicyStore.get_policy()`
3. Remove hardcoded policy logic
4. Always create contract (use policy store's built-in default if needed)

**Code Changes:**

```python
# In __init__:
def __init__(
    self,
    boundary_contract_store: Optional[Any] = None,
    materialization_policy_store: Optional[Any] = None,  # ✅ Ensure this is stored
    ...
):
    self.boundary_contract_store = boundary_contract_store
    self.materialization_policy_store = materialization_policy_store  # ✅ Store it
    ...

# In request_data_access():
async def request_data_access(...):
    # ✅ Get policy from MaterializationPolicyStore (configurable)
    policy = None
    if self.materialization_policy_store:
        try:
            policy = await self.materialization_policy_store.get_policy(
                tenant_id=tenant_id,
                solution_id=context.get("solution_id")
            )
        except Exception as e:
            self.logger.warning(f"Failed to get policy from store: {e}")
            # Policy store has built-in fallback to MVP permissive
    
    # ✅ Use policy store's built-in default if no policy found
    if not policy and self.materialization_policy_store:
        policy = self.materialization_policy_store._get_mvp_permissive_policy()
    
    # ✅ Make policy decision (in Civic Systems, not Runtime)
    access_granted = True  # MVP: Always grant (policy decision)
    materialization_type = policy.get("default_materialization_type", "full_artifact")
    ttl_days = policy.get("default_ttl_days", 30)
    
    # ✅ Create contract (ALWAYS succeeds - policy decision made)
    contract_id = await self.boundary_contract_store.create_boundary_contract({
        "access_granted": access_granted,
        "materialization_type": materialization_type,
        "materialization_expires_at": self._calculate_expiry(ttl_days),
        "policy_basis": policy.get("policy_version", "mvp_1.0"),
        ...
    })
    
    return DataAccessRequest(
        access_granted=access_granted,
        contract_id=contract_id,
        ...
    )
```

---

### Step 2: Remove Policy Logic from ExecutionLifecycleManager

**File:** `symphainy_platform/runtime/execution_lifecycle_manager.py`

**Changes:**
1. Remove `_create_permissive_mvp_contract()` method entirely
2. Require Data Steward SDK (fail if not available)
3. Remove all policy decision logic
4. Only request contracts, never create them

**Code Changes:**

```python
# ❌ REMOVE: _create_permissive_mvp_contract() method (lines ~841-926)

# ✅ UPDATE: Require Data Steward SDK
if intent.intent_type == "ingest_file":
    if not self.data_steward_sdk:
        raise RuntimeError(
            "Data Steward SDK required for boundary contract assignment. "
            "Boundary contracts must be assigned by Civic Systems (Data Steward), not Runtime. "
            "Please ensure Data Steward SDK is initialized."
        )
    
    try:
        # ✅ Request boundary contract from Data Steward (Civic Systems)
        access_request = await self.data_steward_sdk.request_data_access(
            intent={
                "intent_id": intent.intent_id,
                "intent_type": intent.intent_type,
                "tenant_id": intent.tenant_id,
                "parameters": intent.parameters
            },
            context={
                "tenant_id": intent.tenant_id,
                "user_id": context.metadata.get("user_id", "system"),
                "session_id": context.session_id,
                "solution_id": context.metadata.get("solution_id")
            },
            external_source_type=external_source_type,
            external_source_identifier=external_source_identifier,
            external_source_metadata=external_source_metadata
        )
        
        if not access_request.access_granted:
            raise ValueError(f"Data access denied: {access_request.access_reason}")
        
        boundary_contract_id = access_request.contract_id
        context.metadata["boundary_contract_id"] = boundary_contract_id
        context.metadata["materialization_pending"] = True
        
        self.logger.info(f"✅ Boundary contract assigned by Data Steward: {boundary_contract_id}")
        
    except Exception as e:
        # ✅ Fail if Data Steward is unavailable (don't create fallback)
        self.logger.error(f"Boundary contract assignment failed: {e}", exc_info=True)
        raise RuntimeError(
            f"Failed to assign boundary contract via Data Steward: {e}. "
            "Boundary contracts must be assigned by Civic Systems (Data Steward). "
            "Please ensure Data Steward SDK is properly initialized and available."
        )
```

---

### Step 3: Update Data Steward SDK Initialization

**File:** Wherever Data Steward SDK is initialized (likely in Runtime initialization)

**Changes:**
1. Ensure `MaterializationPolicyStore` is passed to Data Steward SDK
2. Ensure Data Steward SDK passes policy store to Data Steward Primitives

**Code Pattern:**

```python
# Initialize MaterializationPolicyStore
materialization_policy_store = MaterializationPolicyStore(
    supabase_adapter=public_works.supabase_adapter
)

# Initialize Data Steward Primitives with policy store
data_steward_primitives = DataStewardPrimitives(
    boundary_contract_store=boundary_contract_store,
    materialization_policy_store=materialization_policy_store  # ✅ Pass policy store
)

# Initialize Data Steward SDK with primitives
data_steward_sdk = DataStewardSDK(
    data_steward_primitives=data_steward_primitives,
    materialization_policy=materialization_policy_store
)

# Initialize ExecutionLifecycleManager with Data Steward SDK
execution_lifecycle_manager = ExecutionLifecycleManager(
    data_steward_sdk=data_steward_sdk,  # ✅ Required, not optional
    materialization_policy_store=materialization_policy_store,
    ...
)
```

---

### Step 4: Update Tests

**Files:** All test files that use ExecutionLifecycleManager

**Changes:**
1. Ensure all tests provide Data Steward SDK
2. Remove tests that expect Runtime to create contracts
3. Test that Runtime fails if Data Steward unavailable

**Test Pattern:**

```python
# ✅ CORRECT: Provide Data Steward SDK
@pytest.fixture
async def data_steward_sdk(public_works):
    materialization_policy_store = MaterializationPolicyStore(
        supabase_adapter=public_works.supabase_adapter
    )
    
    data_steward_primitives = DataStewardPrimitives(
        boundary_contract_store=boundary_contract_store,
        materialization_policy_store=materialization_policy_store
    )
    
    return DataStewardSDK(
        data_steward_primitives=data_steward_primitives,
        materialization_policy=materialization_policy_store
    )

@pytest.fixture
async def execution_lifecycle_manager(public_works, data_steward_sdk):
    return ExecutionLifecycleManager(
        data_steward_sdk=data_steward_sdk,  # ✅ Required
        ...
    )

# ✅ Test: Runtime requests, Data Steward assigns
async def test_boundary_contract_assigned_by_data_steward(
    execution_lifecycle_manager, intent, context
):
    result = await execution_lifecycle_manager.execute(intent)
    assert result.metadata["boundary_contract_id"] is not None

# ✅ Test: Runtime fails if Data Steward unavailable
async def test_runtime_fails_without_data_steward(public_works, intent, context):
    execution_lifecycle_manager = ExecutionLifecycleManager(
        data_steward_sdk=None,  # ❌ Not provided
        ...
    )
    
    with pytest.raises(RuntimeError, match="Data Steward SDK required"):
        await execution_lifecycle_manager.execute(intent)
```

---

## Validation Checklist

- [ ] Data Steward Primitives uses `MaterializationPolicyStore.get_policy()`
- [ ] No hardcoded policy in Data Steward Primitives
- [ ] `_create_permissive_mvp_contract()` removed from ExecutionLifecycleManager
- [ ] ExecutionLifecycleManager requires Data Steward SDK (fails if not available)
- [ ] ExecutionLifecycleManager never creates contracts directly
- [ ] All tests provide Data Steward SDK
- [ ] Tests validate Runtime fails if Data Steward unavailable
- [ ] Policy is configurable via MaterializationPolicyStore
- [ ] Default policy comes from policy store (not hardcoded)

---

## Success Criteria

- ✅ No policy logic in ExecutionLifecycleManager
- ✅ No contract creation in Runtime Plane
- ✅ All policy decisions in Data Steward Primitives
- ✅ Policy configurable via MaterializationPolicyStore
- ✅ Runtime only requests, never creates
- ✅ Runtime fails if Data Steward unavailable
- ✅ Public Works stays infrastructure-only
- ✅ Tests validate proper separation

---

## Files to Modify

1. `symphainy_platform/civic_systems/smart_city/primitives/data_steward_primitives.py`
   - Update `request_data_access()` to use policy store

2. `symphainy_platform/runtime/execution_lifecycle_manager.py`
   - Remove `_create_permissive_mvp_contract()`
   - Require Data Steward SDK
   - Remove policy logic

3. Runtime initialization (wherever ExecutionLifecycleManager is created)
   - Ensure Data Steward SDK is provided
   - Ensure MaterializationPolicyStore is passed to Data Steward

4. Test files
   - Update to provide Data Steward SDK
   - Add test for Runtime failure without Data Steward

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION**
