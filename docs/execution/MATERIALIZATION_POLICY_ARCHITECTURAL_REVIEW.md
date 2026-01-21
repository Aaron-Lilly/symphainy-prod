# Materialization Policy Architectural Review

**Date:** January 19, 2026  
**Status:** 🔴 **CRITICAL ARCHITECTURAL REVIEW**  
**Goal:** Holistic review of materialization policy implementation across all platform layers

---

## Executive Summary

**Problem Statement:** Materialization policy was added as a layer on top of existing systems without proper architectural integration. This has led to:

1. **Content Realm Misalignment:** Traditional FMS (File Management System) pattern conflicts with structured artifact pattern
2. **Execution State Confusion:** Artifacts stored in old format despite handler returning structured format
3. **API Inconsistency:** Execution status API expanding artifacts incorrectly
4. **Ad-hoc Fixes:** Multiple attempts to patch symptoms rather than address root cause

**Root Cause:** Materialization policy was "bolted on" to Runtime without:
- Proper integration with Public Works adapter→abstraction pattern
- Alignment with Civic Systems (Experience, Smart City)
- Consistent artifact format across Realms
- Clear separation of concerns between layers

**Solution:** Holistic architectural refactoring to properly integrate materialization policy at each layer.

---

## Current Architecture Analysis

### Layer 1: Public Works Foundation (Infrastructure)

#### ✅ **Properly Aligned:**
- **Adapter→Abstraction Pattern:** Well-established pattern
  - `ArtifactStorageAbstraction` → `GCSAdapter` + `SupabaseFileAdapter`
  - `FileStorageAbstraction` → `SupabaseFileAdapter` + `GCSAdapter`
  - `StateManagementAbstraction` → `ArangoAdapter` + `RedisAdapter`
  - `AuthAbstraction` → `SupabaseAdapter` (raw authentication data)
  - `AuthorizationAbstraction` → `SupabaseAdapter` (raw permission data)
- **Foundation Service:** Provides abstractions for infrastructure operations
- **Protocol→Abstraction→Adapter:** Clean separation
- **Infrastructure Only:** Public Works provides raw data access, NOT policy decisions

#### ✅ **Policy Pattern Discovery:**
**Key Finding:** Policies are NOT in Public Works. They follow a different pattern:

1. **Smart City Primitives** (Policy Validation):
   - `SecurityGuardPrimitives` - validates permissions, authentication
   - `TrafficCopPrimitives` - validates sessions, rate limiting
   - `DataStewardPrimitives` - validates data permissions
   - `CityManagerPrimitives` - validates realm activation, lifecycle
   - Each has `PolicyStore` for policy data
   - **Pure functions, deterministic, used by Runtime only**

2. **Smart City SDKs** (Coordination):
   - `SecurityGuardSDK` - coordinates auth, prepares execution contracts
   - `CityManagerSDK` - coordinates lifecycle, prepares execution contracts
   - Uses Public Works abstractions to get raw data
   - Prepares execution contracts for Runtime validation

3. **Runtime** (Enforcement):
   - Uses Smart City Primitives to validate execution contracts
   - Does NOT use SDKs (SDKs are for Experience/Realms)

#### ⚠️ **Issues:**
1. **Materialization Policy NOT Following Pattern:**
   - Policy abstraction is in `runtime/policies/` (Runtime layer)
   - Should follow Smart City pattern:
     - **Policy Decision:** Smart City Primitive (like `SecurityGuardPrimitives`)
     - **Policy Enforcement:** Public Works (storage operations)
     - **Policy Configuration:** Smart City SDK (like `CityManagerSDK`)

2. **Dual Storage Systems:**
   - `ArtifactStorageAbstraction` (for structured artifacts)
   - `FileStorageAbstraction` (for files)
   - No unified abstraction for "artifact materialization"

3. **Missing Integration:**
   - No `MaterializationPolicyPrimitive` in Smart City
   - No `MaterializationPolicySDK` in Smart City
   - Policy evaluation logic mixed with Runtime execution logic

---

### Layer 2: Runtime Plane (Execution Orchestration)

#### ✅ **Properly Aligned:**
- **Execution Lifecycle Manager:** Orchestrates execution flow
- **State Surface:** Stores execution state
- **WAL:** Audit trail
- **Intent Registry:** Handler discovery

#### ⚠️ **Issues:**
1. **Materialization Policy Location:**
   - Policy abstraction in `runtime/policies/` (should be in Public Works)
   - Policy evaluation in `ExecutionLifecycleManager` (correct location)
   - Policy configuration loaded in `runtime_main.py` (should be in Public Works)

2. **Artifact Format Confusion:**
   - Handler returns structured artifacts: `{"file": {"result_type": "file", "semantic_payload": {...}, "renderings": {...}}}`
   - Execution state stores old format: `{"artifact_type": "file", "file_id": "...", ...}`
   - Execution status API expands incorrectly

3. **Policy Evaluation Timing:**
   - Policy evaluated AFTER artifacts received (correct)
   - But artifacts stored in execution state BEFORE policy evaluation
   - Should store structured artifacts, then evaluate policy

4. **Missing Integration:**
   - No clear contract between Runtime and Smart City for policy
   - Policy passed as optional parameter (should use Smart City Primitive)
   - Policy should follow same pattern as SecurityGuardPrimitives, TrafficCopPrimitives

---

### Layer 3: Civic Systems (Platform Services)

#### ✅ **Properly Aligned:**
- **Experience Service:** Translates user actions to intents
- **Smart City Primitives:** Data Steward, City Manager, etc.
- **Agent System:** Agentic coordination

#### ⚠️ **Issues:**
1. **No Materialization Policy Awareness:**
   - Experience Service doesn't know about materialization policy
   - Smart City primitives don't configure policy
   - Agents don't understand policy decisions

2. **Missing Integration Points:**
   - No way for Smart City to override policy per solution
   - No way for Experience to query policy decisions
   - No way for agents to understand what gets persisted

3. **Platform vs MVP:**
   - Experience should distinguish platform (ephemeral) vs MVP (persist)
   - Currently hardcoded in `runtime_main.py`

---

### Layer 4: Realms (Domain Services)

#### ✅ **Properly Aligned:**
- **Structured Artifacts Utility:** `realms/utils/structured_artifacts.py`
- **Journey Realm:** Uses structured artifacts correctly
- **Outcomes Realm:** Uses structured artifacts correctly
- **Insights Realm:** Uses structured artifacts correctly

#### ⚠️ **Issues:**
1. **Content Realm Misalignment:**
   - **Root Cause:** Content Realm built as traditional FMS (File Management System)
   - Files stored directly via `FileStorageAbstraction`
   - Returns flat artifacts: `{"file_id": "...", "file_path": "...", ...}`
   - **Attempted Fix:** Refactored to structured artifacts, but execution state still shows old format
   - **Real Issue:** Content Realm has dual identity:
     - FMS operations (ingest, retrieve, list files)
     - Artifact operations (should use materialization policy)

2. **Inconsistent Artifact Format:**
   - Some realms return structured: `{"workflow": {"result_type": "workflow", ...}}`
   - Content Realm (after refactoring) returns structured: `{"file": {"result_type": "file", ...}}`
   - But execution state stores old format

3. **Missing Policy Integration:**
   - Realms don't know about materialization policy
   - Realms just produce artifacts, Runtime evaluates policy (correct)
   - But Realms should understand artifact format requirements

---

## Root Cause Analysis

### Problem 1: Materialization Policy Location

**Current:**
```
runtime/policies/materialization_policy_abstraction.py  ❌ Wrong layer, wrong pattern
```

**Should Be:**
```
civic_systems/smart_city/primitives/materialization_policy_primitives.py  ✅ Correct layer, correct pattern
```

**Why:** Materialization policy is a governance decision (like security, rate limiting), not infrastructure. Should follow Smart City Primitive pattern, not Public Works abstraction pattern.

---

### Problem 2: Content Realm Dual Identity

**Content Realm has TWO roles:**

1. **FMS Role (Traditional):**
   - `ingest_file` → Store file in GCS/Supabase
   - `retrieve_file` → Get file from GCS/Supabase
   - `list_files` → Query Supabase
   - **Files are infrastructure, not artifacts**

2. **Artifact Role (Materialization):**
   - `register_file` → Register file as artifact (for materialization)
   - File metadata → Semantic payload
   - File contents → Renderings
   - **Files are artifacts, subject to materialization policy**

**Current Confusion:**
- Content Realm mixes FMS operations with artifact operations
- FMS operations bypass materialization policy (correct)
- Artifact operations should use materialization policy (but don't consistently)

---

### Problem 3: Execution State Storage

**Current Flow:**
```
Handler returns: {"artifacts": {"file": {"result_type": "file", ...}}}
↓
ExecutionLifecycleManager receives structured artifacts
↓
Materialization policy evaluation (extracts semantic_payload, renderings)
↓
Execution state stores: {"artifacts": {"artifact_type": "file", "file_id": "...", ...}}  ❌ Wrong format
```

**Why:** Execution state storage logic doesn't preserve structured format.

---

### Problem 4: Execution Status API Expansion

**Current Flow:**
```
Execution state has: {"artifacts": {"artifact_type": "file", "file_id": "...", ...}}
↓
Execution status API expands artifacts
↓
Pattern 2 matches "file_id" → Retrieves artifact → Returns old format  ❌ Wrong expansion
```

**Why:** Execution status API has patterns for old format, not structured format.

---

## Proposed Solution: Holistic Architectural Refactoring

### Phase 1: Implement Materialization Policy Following Smart City Pattern

**Goal:** Materialization policy should follow the same pattern as other policies (Security, Rate Limiting, etc.).

**Pattern Discovery:**
- **Policies are NOT in Public Works** (Public Works is infrastructure only)
- **Policies are in Smart City Primitives** (policy validation logic)
- **Policy coordination is in Smart City SDKs** (prepare execution contracts)
- **Policy enforcement is in Runtime** (using Primitives to validate)

**Changes:**

1. **Create Materialization Policy Primitive:**
   ```
   civic_systems/smart_city/primitives/materialization_policy_primitives.py
   ```
   - Follows pattern of `SecurityGuardPrimitives`, `TrafficCopPrimitives`
   - Pure functions, deterministic, used by Runtime only
   - Has `MaterializationPolicyStore` for policy data
   - Evaluates policy decisions (PERSIST, CACHE, DISCARD)

2. **Create Materialization Policy SDK (Optional):**
   ```
   civic_systems/smart_city/sdk/materialization_policy_sdk.py
   ```
   - Follows pattern of `SecurityGuardSDK`, `CityManagerSDK`
   - Coordinates policy configuration
   - Prepares execution contracts for Runtime validation
   - Used by Experience, Solution, Realms

3. **Keep Policy Storage in Public Works:**
   - `ArtifactStorageAbstraction` - stores artifacts (infrastructure)
   - `FileStorageAbstraction` - stores files (infrastructure)
   - Public Works provides storage operations, NOT policy decisions

4. **Update Runtime to Use Primitive:**
   ```python
   # In ExecutionLifecycleManager
   from symphainy_platform.civic_systems.smart_city.primitives.materialization_policy_primitives import (
       MaterializationPolicyPrimitives
   )
   
   # Evaluate policy using Primitive
   decision = await MaterializationPolicyPrimitives.evaluate_policy(
       result_type=result_type,
       semantic_payload=semantic_payload,
       renderings=renderings,
       intent=intent,
       context=context,
       policy_store=policy_store,
       execution_contract=execution_contract
   )
   ```

5. **Remove Old Policy Abstraction:**
   - Delete `runtime/policies/materialization_policy_abstraction.py`
   - Delete `runtime/policies/materialization_policy_protocol.py`
   - Update all imports to use Smart City Primitive

**Benefits:**
- Follows established pattern (consistent with Security, Rate Limiting)
- Policy decisions in Smart City (governance layer)
- Policy enforcement in Runtime (execution layer)
- Policy configuration in Smart City SDK (coordination layer)
- No policy proliferation - policies centralized in Smart City
- Consistent with platform architecture

---

### Phase 2: Separate Content Realm FMS from Artifacts

**Goal:** Clear separation between FMS operations and artifact operations.

**Changes:**

1. **FMS Operations (No Materialization):**
   ```python
   # In ContentOrchestrator
   async def _handle_ingest_file(...):
       # FMS operation: Store file in GCS/Supabase
       # Returns: {"file_id": "...", "storage_location": "...", ...}
       # NOT subject to materialization policy
   ```

2. **Artifact Operations (Materialization):**
   ```python
   # In ContentOrchestrator
   async def _handle_register_file(...):
       # Artifact operation: Register file as artifact
       # Returns: {"artifacts": {"file": {"result_type": "file", ...}}}
       # Subject to materialization policy
   ```

3. **Update Intent Types:**
   - `ingest_file` → FMS operation (no materialization)
   - `retrieve_file` → FMS operation (no materialization)
   - `list_files` → FMS operation (no materialization)
   - `register_file` → Artifact operation (materialization)
   - `retrieve_file_artifact` → Artifact operation (materialization)

**Benefits:**
- Clear separation of concerns
- FMS operations don't conflict with materialization
- Artifact operations properly use materialization policy

---

### Phase 3: Fix Execution State Storage

**Goal:** Execution state stores structured artifacts correctly.

**Changes:**

1. **Store Structured Artifacts:**
   ```python
   # In ExecutionLifecycleManager
   artifacts_for_state = {}
   for artifact_key, artifact_data in artifacts.items():
       if isinstance(artifact_data, dict) and "result_type" in artifact_data:
           # Structured format: store as-is
           artifacts_for_state[artifact_key] = artifact_data
       else:
           # Legacy format: convert to structured
           artifacts_for_state[artifact_key] = {
               "result_type": self._infer_result_type(artifact_key, artifact_data),
               "semantic_payload": self._extract_semantic_payload(artifact_data),
               "renderings": artifact_data
           }
   ```

2. **Policy Evaluation After Storage:**
   - Store structured artifacts in execution state
   - Then evaluate materialization policy
   - Store renderings if policy says PERSIST

**Benefits:**
- Execution state has consistent format
- Policy evaluation works correctly
- No format conversion needed

---

### Phase 4: Fix Execution Status API

**Goal:** Execution status API handles structured artifacts correctly.

**Changes:**

1. **Update Expansion Patterns:**
   ```python
   # In RuntimeAPI.get_execution_status
   for key, value in artifacts.items():
       # Pattern 1: Structured artifacts (CHECK FIRST)
       if isinstance(value, dict) and "result_type" in value:
           retrieved_artifacts[key] = value
           continue
       
       # Pattern 2: Artifact ID references
       if key.endswith("_artifact_id"):
           # Retrieve from ArtifactStorageAbstraction
           ...
       
       # Pattern 3: Legacy format (for backward compatibility)
       ...
   ```

2. **Remove Legacy Patterns:**
   - Remove Pattern 2 (file_id expansion) - not needed for structured artifacts
   - Remove Pattern 3 (file_reference expansion) - not needed for structured artifacts

**Benefits:**
- API returns structured artifacts correctly
- No incorrect expansion
- Backward compatible with legacy format

---

### Phase 5: Integrate with Civic Systems

**Goal:** Civic Systems understand materialization policy.

**Changes:**

1. **Experience Service:**
   ```python
   # In Experience Service
   materialization_policy = public_works.get_materialization_policy_abstraction(
       solution_config=solution_config
   )
   # Can query policy decisions
   # Can show users what gets persisted
   ```

2. **Smart City Primitives:**
   ```python
   # In City Manager SDK
   def configure_materialization_policy(
       self,
       solution_id: str,
       policy_overrides: Dict[str, str]
   ):
       """Configure materialization policy for solution."""
       # Store in solution config
       # Runtime uses this for policy evaluation
   ```

3. **Agent System:**
   ```python
   # Agents can understand policy decisions
   # Agents can explain why artifacts are persisted/discarded
   ```

**Benefits:**
- Platform services understand materialization
- Smart City can configure policy per solution
- Agents can explain policy decisions

---

## Implementation Plan

### Step 1: Move Materialization Policy to Public Works (Days 1-2)

- [ ] Move `materialization_policy_abstraction.py` to Public Works
- [ ] Move `materialization_policy_protocol.py` to Public Works
- [ ] Add `get_materialization_policy_abstraction()` to Foundation Service
- [ ] Update Runtime to get policy from Public Works
- [ ] Update imports across codebase

### Step 2: Separate Content Realm FMS from Artifacts (Days 3-4)

- [ ] Document FMS operations (no materialization)
- [ ] Document artifact operations (materialization)
- [ ] Update Content Realm handlers
- [ ] Update tests to reflect separation

### Step 3: Fix Execution State Storage (Day 5)

- [ ] Update `ExecutionLifecycleManager` to store structured artifacts
- [ ] Remove format conversion logic
- [ ] Test execution state storage

### Step 4: Fix Execution Status API (Day 6)

- [ ] Update expansion patterns
- [ ] Remove legacy patterns
- [ ] Test API returns structured artifacts

### Step 5: Integrate with Civic Systems (Days 7-8)

- [ ] Add policy awareness to Experience Service
- [ ] Add policy configuration to Smart City
- [ ] Update agents to understand policy

### Step 6: Testing & Validation (Day 9)

- [ ] Test all layers work together
- [ ] Test Content Realm FMS operations
- [ ] Test Content Realm artifact operations
- [ ] Test execution state storage
- [ ] Test execution status API
- [ ] Test Civic Systems integration

---

## Success Criteria

### ✅ Phase 1 Complete When:
- `MaterializationPolicyPrimitives` created in Smart City (follows `SecurityGuardPrimitives` pattern)
- `MaterializationPolicyStore` created (follows `PolicyStore` pattern)
- `MaterializationPolicySDK` created (optional, follows `SecurityGuardSDK` pattern)
- Runtime uses `MaterializationPolicyPrimitives.evaluate_policy()` (not abstraction)
- Old policy files removed (`runtime/policies/`)
- All imports updated
- Tests pass

### ✅ Phase 2 Complete When:
- Content Realm FMS operations documented (no materialization)
- Content Realm artifact operations documented (materialization)
- Clear separation between FMS and artifacts
- Tests pass

### ✅ Phase 3 Complete When:
- Execution state stores structured artifacts correctly
- Structured format preserved: `{"file": {"result_type": "file", ...}}`
- Semantic payload in execution state
- Renderings handled by materialization policy (not in execution state)
- No format conversion needed
- Tests pass

### ✅ Phase 4 Complete When:
- Execution status API returns structured artifacts correctly
- Pattern 1 (structured artifacts) checked first
- No incorrect expansion (file_id, file_reference patterns removed)
- Backward compatible with legacy format
- Tests pass

### ✅ Phase 5 Complete When:
- Experience Service uses `MaterializationPolicySDK` to query policy
- Smart City (`CityManagerSDK`) can configure policy per solution
- Agents can explain policy decisions
- Tests pass

### ✅ Phase 6 Complete When:
- All tests pass
- All layers work together correctly
- Smart City Primitive → Runtime enforcement → Public Works storage
- No ad-hoc fixes needed
- Architecture is consistent and maintainable

---

## Architectural Benefits

### ✅ Proper Layer Separation
- Materialization policy in Public Works (infrastructure)
- Policy evaluation in Runtime (orchestration)
- Policy configuration in Smart City (governance)

### ✅ Clear Separation of Concerns
- FMS operations (infrastructure) vs Artifact operations (materialization)
- No confusion between file storage and artifact storage

### ✅ Consistent Artifact Format
- All realms return structured artifacts
- Execution state stores structured artifacts
- API returns structured artifacts

### ✅ Proper Integration
- Public Works provides policy abstraction
- Runtime uses policy abstraction
- Civic Systems configure policy

---

## Risk Mitigation

### Risk 1: Breaking Changes
**Mitigation:** 
- Phased approach, backward compatibility during transition
- Old policy abstraction removed only after Primitive is working
- Tests ensure no regressions

### Risk 2: Content Realm Complexity
**Mitigation:** 
- Clear documentation of FMS vs Artifact operations
- Separate handlers for FMS and artifacts
- Tests verify separation

### Risk 3: Policy Configuration
**Mitigation:** 
- Centralized in Smart City (via SDK)
- Can be overridden per solution (via CityManagerSDK)
- Policy store loads from config file (MVP) or ArangoDB (future)

### Risk 4: Pattern Consistency
**Mitigation:**
- Follow established patterns (SecurityGuardPrimitives, TrafficCopPrimitives)
- Code review ensures consistency
- Documentation explains pattern

---

## Overall Refactoring Vision Changes

### What Changed in the Approach:

1. **Policy Location:**
   - **Original Plan:** Move policy to Public Works (infrastructure layer)
   - **Updated Plan:** Move policy to Smart City Primitives (governance layer)
   - **Reason:** Policies are governance decisions, not infrastructure operations

2. **Policy Pattern:**
   - **Original Plan:** Policy abstraction in Public Works
   - **Updated Plan:** Policy primitive in Smart City (follows SecurityGuardPrimitives pattern)
   - **Reason:** All policies follow same pattern - centralized in Smart City

3. **Policy Evaluation:**
   - **Original Plan:** Runtime uses policy abstraction
   - **Updated Plan:** Runtime uses policy primitive (like SecurityGuardPrimitives)
   - **Reason:** Consistent with how Runtime validates other policies

4. **Policy Configuration:**
   - **Original Plan:** Policy config in Public Works
   - **Updated Plan:** Policy config in Smart City SDK (like CityManagerSDK)
   - **Reason:** Policy configuration is coordination, not infrastructure

5. **Storage Operations:**
   - **Unchanged:** `ArtifactStorageAbstraction` remains in Public Works
   - **Reason:** Storage is infrastructure, not policy

### What Stays the Same:

1. **Content Realm Separation:** FMS vs Artifacts (still needed)
2. **Execution State Storage:** Store structured artifacts (still needed)
3. **Execution Status API:** Handle structured artifacts (still needed)
4. **Civic Systems Integration:** Policy awareness (still needed)

### Key Architectural Principle:

**"Policies are governance decisions, not infrastructure operations."**

- Policies → Smart City Primitives (governance layer)
- Storage → Public Works (infrastructure layer)
- Enforcement → Runtime (execution layer)
- Configuration → Smart City SDKs (coordination layer)

---

## Next Steps

1. **Review this plan** - Ensure alignment with architectural vision
2. **Begin Phase 1** - Create MaterializationPolicyPrimitives in Smart City
3. **Test incrementally** - Verify each phase works
4. **Document changes** - Update architecture documentation
5. **Follow pattern** - Ensure consistency with SecurityGuardPrimitives, TrafficCopPrimitives

---

**Last Updated:** January 19, 2026  
**Status:** 📋 **READY FOR REVIEW**  
**Priority:** 🔴 **CRITICAL** (Architectural Alignment)
