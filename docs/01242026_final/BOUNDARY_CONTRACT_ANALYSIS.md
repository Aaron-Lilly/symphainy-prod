# Boundary Contract Analysis

**Date:** January 25, 2026  
**Question:** Is `boundary_contract_id` requirement a test issue or a real UI gap?

---

## Executive Summary

**Answer: It's BOTH - a test setup issue AND a potential UI gap.**

1. **Test Issue:** E2E tests bypass `ExecutionLifecycleManager`, which should create boundary contracts automatically
2. **Potential UI Gap:** If frontend can call orchestrators directly (bypassing Runtime), it would hit the same issue
3. **MVP Solution:** `ExecutionLifecycleManager` should create "permissive MVP contracts" automatically

---

## What is boundary_contract_id?

### Two-Phase Materialization Flow

The platform uses a **two-phase materialization flow** for file operations:

1. **Phase 1: Upload** (`ingest_file` intent)
   - File is uploaded
   - Creates a **boundary contract** (pending materialization)
   - Returns `file_id` and `boundary_contract_id`

2. **Phase 2: Save** (`save_materialization` intent)
   - Authorizes the materialization
   - Registers file in materialization index
   - File becomes available for parsing

3. **Phase 3: Parse** (`parse_content` intent)
   - Can now parse the saved file

### Purpose

Boundary contracts enforce **governance and authorization**:
- Who can access the file
- What operations are allowed
- Where the file is stored
- Materialization scope and type

---

## How It's Supposed to Work

### ExecutionLifecycleManager Responsibility

According to the code comments in `content_orchestrator.py`:

```python
# CRITICAL: Files are NEVER ingested directly. A boundary contract is required.
# Boundary contract negotiation happens in Runtime/ExecutionLifecycleManager before realm execution.
# ExecutionLifecycleManager ALWAYS creates boundary contracts (permissive MVP if needed).
```

**Expected Flow:**
1. Request comes in (from UI/API)
2. **ExecutionLifecycleManager** intercepts it
3. **ExecutionLifecycleManager** creates boundary contract (permissive MVP if needed)
4. **ExecutionLifecycleManager** adds `boundary_contract_id` to `context.metadata`
5. Orchestrator receives request with `boundary_contract_id` already set

### Permissive MVP Contracts

The system has a fallback mechanism:
- If boundary contract negotiation fails
- Or if no explicit contract is provided
- **ExecutionLifecycleManager** should create a "permissive MVP contract" automatically
- This ensures the system always works, even in MVP scenarios

---

## Current Issue

### In E2E Tests

**Problem:** Our E2E test bypasses `ExecutionLifecycleManager`:

```python
# Current test (WRONG):
result = await content_orch.handle_intent(intent, test_context)
# This bypasses ExecutionLifecycleManager!
```

**Why it fails:**
- Test calls orchestrator directly
- No `ExecutionLifecycleManager` to create boundary contract
- `context.metadata` doesn't have `boundary_contract_id`
- Orchestrator correctly rejects it (enforcing the requirement)

### In Production (If UI Calls Orchestrators Directly)

**If the frontend/API calls orchestrators directly** (bypassing Runtime/ExecutionLifecycleManager):
- Same issue would occur
- This would be a **real UI gap**

**If the frontend/API goes through Runtime/ExecutionLifecycleManager:**
- Boundary contracts would be created automatically
- No gap - system works as designed

---

## Is This a UI Gap?

### Depends on Architecture

**Scenario A: Frontend → Runtime → ExecutionLifecycleManager → Orchestrator**
- ✅ **No gap** - ExecutionLifecycleManager handles it
- Boundary contracts created automatically
- System works as designed

**Scenario B: Frontend → Orchestrator (direct)**
- ❌ **Real gap** - Frontend would need to handle boundary contracts
- This would be a logical gap in the UI flow
- Frontend shouldn't need to know about boundary contracts

### Recommendation

**For MVP:**
1. **Ensure all requests go through Runtime/ExecutionLifecycleManager**
2. **ExecutionLifecycleManager should ALWAYS create permissive MVP contracts**
3. **Frontend should NEVER call orchestrators directly**

**If frontend currently calls orchestrators directly:**
- This is a **real architectural gap**
- Should be fixed to go through Runtime
- Or ExecutionLifecycleManager logic should be extracted to a shared service

---

## Solution for E2E Tests

### Option 1: Use ExecutionLifecycleManager (Recommended)

```python
from symphainy_platform.runtime.execution_lifecycle_manager import ExecutionLifecycleManager

# Create ExecutionLifecycleManager
lifecycle_manager = ExecutionLifecycleManager(public_works=test_public_works)

# Execute through lifecycle manager (creates boundary contracts automatically)
result = await lifecycle_manager.execute_intent(intent, test_context)
```

**Pros:**
- Tests real production flow
- Boundary contracts created automatically
- Tests the actual system behavior

**Cons:**
- More setup required
- Need to initialize ExecutionLifecycleManager

### Option 2: Create Boundary Contract in Test

```python
# Create permissive MVP contract manually
boundary_contract_id = await create_permissive_mvp_contract(...)
test_context.metadata["boundary_contract_id"] = boundary_contract_id

# Then call orchestrator
result = await content_orch.handle_intent(intent, test_context)
```

**Pros:**
- Simpler test setup
- Direct orchestrator testing

**Cons:**
- Doesn't test ExecutionLifecycleManager
- May miss integration issues

### Option 3: Mock/Default Boundary Contract

```python
# For MVP testing, use a default contract ID
test_context.metadata["boundary_contract_id"] = "mvp_permissive_default"
```

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

**File:** `symphainy_platform/runtime/execution_lifecycle_manager.py`

```python
# Phase 1: For ingest_file - always create boundary contract (permissive MVP if needed)
if intent.intent_type == "ingest_file":
    # Try to create boundary contract
    try:
        boundary_contract_id = await self._create_permissive_mvp_contract(intent, context)
    except Exception as e:
        # Fallback: create permissive MVP contract
        boundary_contract_id = await self._create_permissive_mvp_contract(intent, context)
    
    # Add to context metadata
    context.metadata["boundary_contract_id"] = boundary_contract_id
```

### Orchestrator Expects Contract

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

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
- ExecutionLifecycleManager should handle it automatically
- Frontend should go through Runtime
- If frontend doesn't, that's a gap to fix

**For E2E Tests:**
- Use ExecutionLifecycleManager (Option 1)
- This tests the real production flow
- Validates the system works end-to-end

---

**Last Updated:** January 25, 2026
