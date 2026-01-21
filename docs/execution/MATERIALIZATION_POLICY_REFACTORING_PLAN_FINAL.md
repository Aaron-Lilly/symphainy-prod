# Materialization Policy Refactoring Plan - Final

**Date:** January 19, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Goal:** Holistic refactoring following Smart City policy pattern

---

## Executive Summary

**Key Finding:** Materialization policy should follow the Smart City pattern (like Security, Rate Limiting), NOT the Public Works pattern.

**Pattern:**
- **Policy Decision:** Smart City Primitive (governance layer)
- **Policy Enforcement:** Runtime (execution layer, using Primitive)
- **Policy Storage:** Public Works (infrastructure layer)
- **Policy Configuration:** Smart City SDK (coordination layer)

**Benefits:**
- Consistent with all other policies
- No policy proliferation
- Proper layer separation
- Easy to understand and maintain

---

## Implementation Plan

### Phase 1: Create Materialization Policy Primitive (Days 1-2)

**Goal:** Create `MaterializationPolicyPrimitives` following `SecurityGuardPrimitives` pattern.

**Files to Create:**

1. **`civic_systems/smart_city/primitives/materialization_policy_primitives.py`**
   ```python
   class MaterializationPolicyStore:
       """Policy store for materialization policies."""
       async def get_materialization_policy(...) -> Optional[Dict[str, Any]]
       async def evaluate_policy(...) -> str  # "persist", "cache", "discard"
   
   class MaterializationPolicyPrimitives:
       """Policy validation - pure functions, deterministic, used by Runtime only."""
       @staticmethod
       async def evaluate_policy(
           result_type: str,
           semantic_payload: Dict[str, Any],
           renderings: Dict[str, Any],
           intent: Any,
           context: Any,
           policy_store: MaterializationPolicyStore,
           execution_contract: Dict[str, Any]
       ) -> MaterializationDecision:  # PERSIST, CACHE, DISCARD
   ```

2. **`civic_systems/smart_city/sdk/materialization_policy_sdk.py`** (Optional)
   ```python
   class MaterializationPolicySDK:
       """Coordination - prepares execution contracts."""
       async def configure_materialization_policy(...) -> Dict[str, Any]
   ```

**Files to Update:**

1. **`runtime/execution_lifecycle_manager.py`**
   - Remove `MaterializationPolicyAbstraction` usage
   - Use `MaterializationPolicyPrimitives.evaluate_policy()`
   - Pass `policy_store` and `execution_contract`

2. **`runtime_main.py`**
   - Initialize `MaterializationPolicyStore`
   - Load policy from config file
   - Pass to `ExecutionLifecycleManager`

**Files to Delete:**

1. **`runtime/policies/materialization_policy_abstraction.py`**
2. **`runtime/policies/materialization_policy_protocol.py`**

**Tasks:**
- [ ] Create `MaterializationPolicyStore` class
- [ ] Create `MaterializationPolicyPrimitives` class
- [ ] Create `MaterializationPolicySDK` class (optional)
- [ ] Update `ExecutionLifecycleManager` to use Primitive
- [ ] Update `runtime_main.py` to initialize policy store
- [ ] Delete old policy files
- [ ] Update all imports
- [ ] Update tests

---

### Phase 2: Separate Content Realm FMS from Artifacts (Days 3-4)

**Goal:** Clear separation between FMS operations (infrastructure) and artifact operations (materialization).

**Files to Update:**

1. **`realms/content/orchestrators/content_orchestrator.py`**
   - Document FMS operations (no materialization):
     - `_handle_ingest_file` → Returns flat format
     - `_handle_retrieve_file` → Returns flat format
     - `_handle_list_files` → Returns flat format
   - Document artifact operations (materialization):
     - `_handle_register_file` → Returns structured format
     - `_handle_retrieve_file_artifact` → Returns structured format

**Tasks:**
- [ ] Document FMS operations (no materialization)
- [ ] Document artifact operations (materialization)
- [ ] Ensure clear separation in code
- [ ] Update tests to reflect separation

---

### Phase 3: Fix Execution State Storage (Day 5)

**Goal:** Execution state stores structured artifacts correctly.

**Files to Update:**

1. **`runtime/execution_lifecycle_manager.py`**
   - Store structured artifacts as-is
   - Preserve format: `{"file": {"result_type": "file", "semantic_payload": {...}, "renderings": {...}}}`
   - Remove format conversion logic
   - Remove `_sanitize_artifacts_for_storage()` (no longer needed)

**Tasks:**
- [ ] Update execution state storage to preserve structured format
- [ ] Remove format conversion logic
- [ ] Remove sanitization methods
- [ ] Test execution state storage

---

### Phase 4: Fix Execution Status API (Day 6)

**Goal:** Execution status API handles structured artifacts correctly.

**Files to Update:**

1. **`runtime/runtime_api.py`**
   - Update `get_execution_status()` expansion patterns
   - Pattern 1: Structured artifacts (CHECK FIRST)
   - Pattern 2: Artifact ID references
   - Remove incorrect patterns (file_id, file_reference expansion)

**Tasks:**
- [ ] Update expansion patterns
- [ ] Remove incorrect patterns
- [ ] Test API returns structured artifacts

---

### Phase 5: Integrate with Civic Systems (Days 7-8)

**Goal:** Civic Systems understand materialization policy.

**Files to Update:**

1. **`civic_systems/experience/experience_service.py`**
   - Use `MaterializationPolicySDK` to query policy decisions

2. **`civic_systems/smart_city/sdk/city_manager_sdk.py`**
   - Add `configure_materialization_policy()` method

**Tasks:**
- [ ] Add policy awareness to Experience Service
- [ ] Add policy configuration to Smart City
- [ ] Update agents to understand policy

---

### Phase 6: Testing & Validation (Day 9)

**Goal:** All layers work together correctly.

**Tasks:**
- [ ] Test all layers work together
- [ ] Test Content Realm FMS operations
- [ ] Test Content Realm artifact operations
- [ ] Test execution state storage
- [ ] Test execution status API
- [ ] Test Civic Systems integration

---

## Key Changes from Original Plan

### What Changed:

1. **Policy Location:**
   - **Original:** Move to Public Works (infrastructure)
   - **Updated:** Move to Smart City Primitives (governance)
   - **Reason:** Policies are governance decisions, not infrastructure

2. **Policy Pattern:**
   - **Original:** Policy abstraction in Public Works
   - **Updated:** Policy primitive in Smart City (follows SecurityGuardPrimitives)
   - **Reason:** All policies follow same pattern

3. **Policy Evaluation:**
   - **Original:** Runtime uses policy abstraction
   - **Updated:** Runtime uses policy primitive (like SecurityGuardPrimitives)
   - **Reason:** Consistent with how Runtime validates other policies

4. **Policy Configuration:**
   - **Original:** Policy config in Public Works
   - **Updated:** Policy config in Smart City SDK (like CityManagerSDK)
   - **Reason:** Policy configuration is coordination, not infrastructure

### What Stays the Same:

1. **Content Realm Separation:** FMS vs Artifacts (still needed)
2. **Execution State Storage:** Store structured artifacts (still needed)
3. **Execution Status API:** Handle structured artifacts (still needed)
4. **Civic Systems Integration:** Policy awareness (still needed)

---

## Success Criteria

### ✅ Phase 1 Complete When:
- `MaterializationPolicyPrimitives` created (follows SecurityGuardPrimitives pattern)
- `MaterializationPolicyStore` created (follows PolicyStore pattern)
- Runtime uses Primitive to evaluate policy
- Old policy files removed
- All tests pass

### ✅ Phase 2 Complete When:
- FMS operations documented (no materialization)
- Artifact operations documented (materialization)
- Clear separation in code
- Tests pass

### ✅ Phase 3 Complete When:
- Execution state stores structured artifacts correctly
- No format conversion needed
- Tests pass

### ✅ Phase 4 Complete When:
- Execution status API returns structured artifacts
- No incorrect expansion
- Tests pass

### ✅ Phase 5 Complete When:
- Experience Service understands policy
- Smart City can configure policy
- Agents understand policy
- Tests pass

### ✅ Phase 6 Complete When:
- All tests pass
- All layers work together
- Architecture is consistent and maintainable

---

## Architectural Principle

**"Policies are governance decisions, not infrastructure operations."**

- Policies → Smart City Primitives (governance layer)
- Storage → Public Works (infrastructure layer)
- Enforcement → Runtime (execution layer)
- Configuration → Smart City SDKs (coordination layer)

---

**Last Updated:** January 19, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Priority:** 🔴 **CRITICAL** (Architectural Alignment)
