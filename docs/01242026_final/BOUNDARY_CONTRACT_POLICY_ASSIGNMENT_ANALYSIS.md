# Boundary Contract Policy Assignment Analysis

**Date:** January 25, 2026  
**Status:** 🔴 **ARCHITECTURAL ISSUE IDENTIFIED**  
**Prepared For:** CTO Review & Team Implementation

---

## Executive Summary

**Problem:** `ExecutionLifecycleManager` (Runtime Plane) is creating boundary contracts, which is **policy/governance logic** that belongs in **Civic Systems** (Data Steward), not Runtime.

**CTO's Concern:** Public Works should enable swappable infrastructure, not create or define policy. Policy is the domain of Civic Systems.

**Recommendation:** Move boundary contract **assignment** (policy decision) to **Data Steward Primitives** (Civic Systems). ExecutionLifecycleManager should only **request** boundary contracts, not create them.

---

## Current Architecture (PROBLEM)

### Current Flow

```
1. Intent arrives at ExecutionLifecycleManager (Runtime Plane)
2. ExecutionLifecycleManager calls Data Steward SDK.request_data_access()
3. If Data Steward SDK is unavailable OR access denied:
   → ExecutionLifecycleManager._create_permissive_mvp_contract() creates contract
4. Contract is stored in context.metadata
5. Realm receives intent with boundary_contract_id
```

### The Problem

**ExecutionLifecycleManager is making policy decisions:**

```python
# ❌ WRONG: Runtime creating policy
async def _create_permissive_mvp_contract(self, intent, context):
    # Hardcoded MVP permissive policy
    policy = {
        "allow_all_types": True,
        "default_ttl_days": 30,
        "default_backing_store": "gcs",
        "no_restrictions": True
    }
    # Creates contract with policy decision
    contract_data = {
        "materialization_policy": policy,
        "access_granted": True,
        "policy_basis": "mvp_permissive_policy"
    }
    # ...
```

**Why This Is Wrong:**
- ❌ Runtime Plane is making **policy decisions** (should be Civic Systems)
- ❌ Runtime Plane is **creating contracts** (should be Data Steward)
- ❌ Policy logic is **hardcoded in Runtime** (should be configurable in Civic Systems)
- ❌ Violates separation: Runtime executes, Civic Systems govern

---

## Correct Architecture (RECOMMENDATION)

### Correct Flow

```
1. Intent arrives at ExecutionLifecycleManager (Runtime Plane)
2. ExecutionLifecycleManager calls Data Steward SDK.request_data_access()
3. Data Steward SDK calls Data Steward Primitives.request_data_access()
4. Data Steward Primitives:
   - Makes policy decision (access granted? what type? TTL? scope?)
   - Creates boundary contract with policy decision
   - Returns contract_id
5. If Data Steward is unavailable:
   → ExecutionLifecycleManager FAILS (doesn't create contracts)
   → OR: Data Steward has default policy that always succeeds
6. Contract is stored in context.metadata
7. Realm receives intent with boundary_contract_id
```

### Key Principle

**Runtime requests, Civic Systems assign.**

- **Runtime Plane:** Requests boundary contract assignment
- **Civic Systems (Data Steward):** Assigns boundary contract based on policy
- **Public Works:** Provides infrastructure (storage, state) - no policy

---

## Recommended Solution

### Option 1: Data Steward Always Assigns (RECOMMENDED)

**Data Steward Primitives always creates contracts, even with default policy.**

**Changes:**

1. **Remove `_create_permissive_mvp_contract()` from ExecutionLifecycleManager**
   - Runtime should not create contracts
   - Runtime should only request from Data Steward

2. **Data Steward Primitives always succeeds (with default policy)**
   - If no explicit policy, use default permissive policy
   - Policy decision stays in Civic Systems
   - Runtime never makes policy decisions

3. **ExecutionLifecycleManager flow:**
   ```python
   # ✅ CORRECT: Runtime requests, doesn't create
   if intent.intent_type == "ingest_file":
       if not self.data_steward_sdk:
           raise RuntimeError("Data Steward SDK required for boundary contract assignment")
       
       access_request = await self.data_steward_sdk.request_data_access(...)
       
       if not access_request.access_granted:
           raise ValueError(f"Data access denied: {access_request.access_reason}")
       
       boundary_contract_id = access_request.contract_id
       context.metadata["boundary_contract_id"] = boundary_contract_id
   ```

4. **Data Steward Primitives always creates contract:**
   ```python
   # ✅ CORRECT: Policy decision in Civic Systems
   async def request_data_access(...):
       # Check policy (or use default)
       policy = await self._get_policy(tenant_id) or self._get_default_policy()
       
       # Make policy decision
       access_granted = policy.allow_access(...)
       materialization_type = policy.get_materialization_type(...)
       ttl_days = policy.get_ttl_days(...)
       
       # Create contract with policy decision
       contract_id = await self.boundary_contract_store.create_boundary_contract({
           "access_granted": access_granted,
           "materialization_type": materialization_type,
           "ttl_days": ttl_days,
           "policy_basis": policy.policy_name
       })
       
       return DataAccessRequest(
           access_granted=access_granted,
           contract_id=contract_id,
           ...
       )
   ```

**Pros:**
- ✅ Clear separation: Runtime executes, Civic Systems govern
- ✅ Policy is configurable in Civic Systems
- ✅ Runtime never makes policy decisions
- ✅ Public Works stays infrastructure-only

**Cons:**
- ⚠️ Requires Data Steward SDK to always be available
- ⚠️ Need to ensure default policy exists

---

### Option 2: Data Steward Optional with Runtime Fallback (NOT RECOMMENDED)

**Keep current flow but move policy to Data Steward.**

**Changes:**

1. **Move `_create_permissive_mvp_contract()` logic to Data Steward Primitives**
2. **ExecutionLifecycleManager calls Data Steward, falls back to Data Steward default**
3. **Runtime never creates contracts directly**

**Pros:**
- ✅ Maintains backward compatibility
- ✅ Policy still in Civic Systems

**Cons:**
- ❌ Still allows Runtime to bypass Data Steward
- ❌ Fallback logic is still policy (should fail instead)

---

## Implementation Plan

### Phase 1: Move Policy to Data Steward Primitives

**File:** `symphainy_platform/civic_systems/smart_city/primitives/data_steward_primitives.py`

**Changes:**
1. Add `materialization_policy_store` parameter to `__init__` (already exists, ensure it's used)
2. Update `request_data_access()` to use `MaterializationPolicyStore.get_policy()` for policy decisions
3. Ensure `request_data_access()` always creates contract (with policy store default if needed)
4. Remove any "fallback" logic that returns None

**Key:** Use existing `MaterializationPolicyStore` from `symphainy_platform/civic_systems/smart_city/stores/materialization_policy_store.py`

**Code:**
```python
async def request_data_access(...):
    # Get policy from MaterializationPolicyStore (configurable, not hardcoded)
    policy = None
    if self.materialization_policy_store:
        try:
            policy = await self.materialization_policy_store.get_policy(
                tenant_id=tenant_id,
                solution_id=context.get("solution_id")
            )
        except Exception as e:
            self.logger.warning(f"Failed to get policy from store: {e}, using store default")
            # Policy store has built-in fallback to MVP permissive policy
    
    # If no policy store, use store's built-in default (via _get_mvp_permissive_policy)
    if not policy and self.materialization_policy_store:
        policy = self.materialization_policy_store._get_mvp_permissive_policy()
    
    # Make policy decision (policy decision in Civic Systems, not Runtime)
    access_granted = True  # MVP: Always grant (policy decision)
    materialization_type = policy.get("default_materialization_type", "full_artifact")
    ttl_days = policy.get("default_ttl_days", 30)
    
    # Create contract (ALWAYS succeeds - policy decision made)
    contract_id = await self.boundary_contract_store.create_boundary_contract({
        "access_granted": access_granted,
        "materialization_type": materialization_type,
        "materialization_expires_at": self._calculate_expiry(ttl_days),
        "policy_basis": policy.get("policy_name", "default"),
        ...
    })
    
    return DataAccessRequest(
        access_granted=access_granted,
        contract_id=contract_id,
        ...
    )
```

---

### Phase 2: Remove Policy Logic from ExecutionLifecycleManager

**File:** `symphainy_platform/runtime/execution_lifecycle_manager.py`

**Changes:**
1. Remove `_create_permissive_mvp_contract()` method
2. Remove all policy decision logic
3. Require Data Steward SDK (fail if not available)
4. Only request contracts, never create them

**Code:**
```python
# ❌ REMOVE: _create_permissive_mvp_contract() method entirely

# ✅ UPDATE: Only request, never create
if intent.intent_type == "ingest_file":
    if not self.data_steward_sdk:
        raise RuntimeError(
            "Data Steward SDK required for boundary contract assignment. "
            "Boundary contracts must be assigned by Civic Systems (Data Steward), not Runtime."
        )
    
    try:
        access_request = await self.data_steward_sdk.request_data_access(...)
        
        if not access_request.access_granted:
            raise ValueError(f"Data access denied: {access_request.access_reason}")
        
        boundary_contract_id = access_request.contract_id
        context.metadata["boundary_contract_id"] = boundary_contract_id
        
    except Exception as e:
        # Don't create fallback contract - fail instead
        self.logger.error(f"Boundary contract assignment failed: {e}", exc_info=True)
        raise RuntimeError(
            f"Failed to assign boundary contract via Data Steward: {e}. "
            "Boundary contracts must be assigned by Civic Systems."
        )
```

---

### Phase 3: Update Tests

**Changes:**
1. Ensure all tests provide Data Steward SDK
2. Remove tests that expect Runtime to create contracts
3. Test that Runtime fails if Data Steward unavailable

**Test Pattern:**
```python
# ✅ CORRECT: Provide Data Steward SDK
data_steward_sdk = DataStewardSDK(
    data_steward_primitives=DataStewardPrimitives(...)
)

lifecycle_manager = ExecutionLifecycleManager(
    data_steward_sdk=data_steward_sdk,
    ...
)

# ✅ CORRECT: Runtime requests, Data Steward assigns
result = await lifecycle_manager.execute(intent)
assert result.metadata["boundary_contract_id"] is not None
```

---

## Where Should Boundary Contracts Be Assigned?

### Answer: Data Steward Primitives (Civic Systems)

**Location:** `symphainy_platform/civic_systems/smart_city/primitives/data_steward_primitives.py`

**Why:**
- ✅ Civic Systems own policy/governance
- ✅ Data Steward is responsible for data boundaries
- ✅ Primitives make policy decisions
- ✅ SDK coordinates, Primitives decide

**Flow:**
```
ExecutionLifecycleManager (Runtime)
  ↓ requests
Data Steward SDK (Civic Systems - Coordination)
  ↓ coordinates
Data Steward Primitives (Civic Systems - Policy Decision)
  ↓ assigns
Boundary Contract Store (Public Works - Infrastructure)
```

---

## Updated Flow Diagram

### Before (WRONG)
```
Intent → ExecutionLifecycleManager
  ↓
  ├─→ Data Steward SDK (if available)
  │     └─→ Data Steward Primitives
  │           └─→ Contract created
  │
  └─→ _create_permissive_mvp_contract() ❌ POLICY IN RUNTIME
        └─→ Contract created with hardcoded policy
```

### After (CORRECT)
```
Intent → ExecutionLifecycleManager
  ↓
  └─→ Data Steward SDK (REQUIRED)
        └─→ Data Steward Primitives
              ├─→ Get policy (or default)
              ├─→ Make policy decision ✅ POLICY IN CIVIC SYSTEMS
              └─→ Create contract with policy
```

---

## CTO Answers (Validated)

1. **Should Runtime fail if Data Steward is unavailable?**
   - ✅ **Answer: Yes, Runtime should fail if Data Steward is unavailable**
   - Default policy is OK, subject to answer 2

2. **Should default policy be configurable?**
   - ✅ **Answer: Default policy should be set and configurable via a policy store**
   - Not hardcoded in Data Steward Primitives

3. **Should Traffic Cop route to Data Steward, or is a direct call acceptable?**
   - ✅ **Answer: ExecutionLifecycleManager should call Data Steward directly**
   - This avoids circular references/dependencies between services

---

## Success Criteria

- ✅ No policy logic in ExecutionLifecycleManager
- ✅ No contract creation in Runtime Plane
- ✅ All policy decisions in Data Steward Primitives
- ✅ Runtime only requests, never creates
- ✅ Public Works stays infrastructure-only
- ✅ Tests validate proper separation

---

## Migration Steps

1. **Add default policy to Data Steward Primitives**
2. **Ensure Data Steward Primitives always creates contracts**
3. **Remove `_create_permissive_mvp_contract()` from ExecutionLifecycleManager**
4. **Update ExecutionLifecycleManager to require Data Steward SDK**
5. **Update tests to provide Data Steward SDK**
6. **Validate: Runtime fails if Data Steward unavailable**
7. **Validate: All contracts created by Data Steward**

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **READY FOR CTO REVIEW**
