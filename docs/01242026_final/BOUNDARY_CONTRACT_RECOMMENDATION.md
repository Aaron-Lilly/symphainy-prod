# Boundary Contract Recommendation

**Date:** January 25, 2026  
**Question:** How should we handle `boundary_contract_id` for MVP?

---

## Answer: It's BOTH a Test Issue AND a Potential UI Gap

### Summary

1. **For MVP:** ExecutionLifecycleManager should handle it automatically (creates permissive MVP contracts)
2. **For Tests:** E2E tests should use ExecutionLifecycleManager, not call orchestrators directly
3. **For UI:** If UI goes through Runtime/ExecutionLifecycleManager → ✅ No gap. If UI calls orchestrators directly → ❌ Real gap

---

## The Two-Phase Materialization Flow

### What It Is

The platform uses a **two-phase materialization flow**:

1. **Phase 1: Upload** (`ingest_file`)
   - Creates boundary contract (pending materialization)
   - Returns `file_id` and `boundary_contract_id`

2. **Phase 2: Save** (`save_materialization`)
   - Authorizes materialization
   - Registers file in materialization index
   - File becomes available for parsing

3. **Phase 3: Parse** (`parse_content`)
   - Can now parse the saved file

### Why It Exists

Boundary contracts enforce **governance**:
- Who can access the file
- What operations are allowed
- Where the file is stored
- Materialization scope and type

---

## How It's Supposed to Work

### ExecutionLifecycleManager Handles It Automatically

**Code Location:** `symphainy_platform/runtime/execution_lifecycle_manager.py`

```python
# Phase 1: For ingest_file - always create boundary contract (permissive MVP if needed)
if intent.intent_type == "ingest_file":
    # Try to create boundary contract via Data Steward SDK
    # If that fails, create permissive MVP contract
    boundary_contract_id = await self._create_permissive_mvp_contract(intent, context)
    
    # ALWAYS set boundary contract in context (required - no exceptions)
    context.metadata["boundary_contract_id"] = boundary_contract_id
```

**Key Point:** ExecutionLifecycleManager **ALWAYS** creates boundary contracts, even if it's just a "permissive MVP contract."

---

## Is This a UI Gap?

### Depends on Architecture

**Scenario A: Frontend → Runtime API → ExecutionLifecycleManager → Orchestrator**
- ✅ **No gap** - ExecutionLifecycleManager handles it automatically
- Boundary contracts created automatically
- System works as designed

**Scenario B: Frontend → Orchestrator (direct call)**
- ❌ **Real gap** - Frontend would need to handle boundary contracts
- This would be a logical gap in the UI flow
- Frontend shouldn't need to know about boundary contracts

### Recommendation for MVP

**Ensure all requests go through Runtime/ExecutionLifecycleManager:**
- This is the correct architectural pattern
- Boundary contracts are handled automatically
- Frontend doesn't need to know about them

**If frontend currently calls orchestrators directly:**
- This is a **real architectural gap**
- Should be fixed to go through Runtime
- Boundary contracts are a core architectural concept

---

## Solution for E2E Tests

### Option 1: Use ExecutionLifecycleManager (Recommended)

**Why:** Tests the real production flow

```python
from symphainy_platform.runtime.execution_lifecycle_manager import ExecutionLifecycleManager
from symphainy_platform.runtime.intent_registry import IntentRegistry
from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.runtime.wal import WriteAheadLog

# Create ExecutionLifecycleManager with test infrastructure
intent_registry = IntentRegistry()
state_surface = test_public_works.get_state_abstraction()
wal = WriteAheadLog(...)

lifecycle_manager = ExecutionLifecycleManager(
    intent_registry=intent_registry,
    state_surface=state_surface,
    wal=wal,
    public_works=test_public_works
)

# Execute through lifecycle manager (creates boundary contracts automatically)
result = await lifecycle_manager.execute(intent)
```

**Pros:**
- Tests real production flow
- Boundary contracts created automatically
- Validates entire system works end-to-end

**Cons:**
- More setup required
- Need to initialize ExecutionLifecycleManager properly

### Option 2: Create Boundary Contract Manually in Test

```python
# Create permissive MVP contract manually
from symphainy_platform.runtime.execution_lifecycle_manager import ExecutionLifecycleManager

lifecycle_manager = ExecutionLifecycleManager(...)
boundary_contract_id = await lifecycle_manager._create_permissive_mvp_contract(intent, context)
test_context.metadata["boundary_contract_id"] = boundary_contract_id

# Then call orchestrator
result = await content_orch.handle_intent(intent, test_context)
```

**Pros:**
- Simpler test setup
- Direct orchestrator testing

**Cons:**
- Doesn't test ExecutionLifecycleManager integration
- May miss integration issues

### Option 3: Use Test Helper (Simplest for MVP)

For MVP testing, we could create a test helper that:
1. Creates a default boundary contract
2. Adds it to context metadata
3. Then calls orchestrator

**Pros:**
- Simplest
- Quick to implement

**Cons:**
- Doesn't test real flow
- May hide real issues

---

## Recommendation

### For E2E Tests

**Use Option 1** - Go through ExecutionLifecycleManager:
- Tests the real production flow
- Boundary contracts created automatically
- Validates the entire system works end-to-end

**Implementation:**
- Follow the pattern from `test_content_realm_e2e_phases_1_4.py`
- Initialize ExecutionLifecycleManager with test infrastructure
- Use `lifecycle_manager.execute(intent)` instead of `orchestrator.handle_intent()`

### For MVP/Production

**Ensure:**
1. All requests go through Runtime/ExecutionLifecycleManager
2. ExecutionLifecycleManager always creates permissive MVP contracts
3. Frontend never calls orchestrators directly

**If frontend currently bypasses Runtime:**
- This is a **real gap** that should be fixed
- Boundary contracts are a core architectural concept
- They should be handled automatically by the system, not by the UI

---

## Code References

### ExecutionLifecycleManager Creates Contracts

**File:** `symphainy_platform/runtime/execution_lifecycle_manager.py:232-288`

```python
# Phase 1: For ingest_file - always create boundary contract (permissive MVP if needed)
if intent.intent_type == "ingest_file":
    # Try Data Steward SDK first, fallback to permissive MVP
    boundary_contract_id = await self._create_permissive_mvp_contract(intent, context)
    
    # ALWAYS set boundary contract in context
    context.metadata["boundary_contract_id"] = boundary_contract_id
```

### Orchestrator Expects Contract

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py:250-265`

```python
boundary_contract_id = context.metadata.get("boundary_contract_id")

if not boundary_contract_id:
    raise ValueError(
        "boundary_contract_id is required for ingest_file intent. "
        "This indicates a bug in ExecutionLifecycleManager - boundary contracts should "
        "always be created (permissive MVP contracts are acceptable)."
    )
```

---

## Conclusion

**This is BOTH:**
1. **Test Issue:** E2E tests bypass ExecutionLifecycleManager - should use it
2. **Potential UI Gap:** If frontend bypasses Runtime, it's a real gap

**For MVP:**
- ExecutionLifecycleManager should handle it automatically ✅
- Frontend should go through Runtime ✅
- If frontend doesn't, that's a gap to fix ❌

**For E2E Tests:**
- Use ExecutionLifecycleManager (Option 1) ✅
- This tests the real production flow ✅
- Validates the system works end-to-end ✅

---

**Last Updated:** January 25, 2026
