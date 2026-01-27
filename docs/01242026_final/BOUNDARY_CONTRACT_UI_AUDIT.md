# Boundary Contract UI Audit

**Date:** January 25, 2026  
**Purpose:** Verify that UI flow properly uses Runtime/ExecutionLifecycleManager and doesn't bypass boundary contract creation

---

## Executive Summary

✅ **Runtime API uses ExecutionLifecycleManager** - All intents go through proper flow  
⚠️ **Legacy endpoint may exist** - Need to verify `/api/v1/business_enablement/content/upload-file`  
✅ **E2E tests updated** - Now use ExecutionLifecycleManager (matches production flow)

---

## Architecture Flow

### Correct Flow (Production)

```
Frontend → Experience API (/api/intent/submit) 
         → Runtime API (/api/intent/submit) 
         → ExecutionLifecycleManager.execute()
         → Creates boundary contract (permissive MVP if needed)
         → Orchestrator.handle_intent()
```

**Key Points:**
- ExecutionLifecycleManager **ALWAYS** creates boundary contracts for `ingest_file` intents
- Boundary contracts are created automatically (permissive MVP if needed)
- Frontend doesn't need to know about boundary contracts

### Verified Components

#### 1. Runtime API (`/api/intent/submit`)

**File:** `symphainy_platform/runtime/runtime_api.py:297`

```python
async def submit_intent(self, request: IntentSubmitRequest):
    # Create intent
    intent = IntentFactory.create_intent(...)
    
    # Execute intent via ExecutionLifecycleManager
    result = await self.execution_lifecycle_manager.execute(intent)
```

✅ **Uses ExecutionLifecycleManager** - Boundary contracts created automatically

#### 2. Experience API (`/api/intent/submit`)

**File:** `symphainy_platform/civic_systems/experience/api/intents.py:121`

```python
@router.post("/submit", response_model=IntentSubmitResponse)
async def submit_intent(request: IntentSubmitRequest, ...):
    # Create intent
    intent = IntentFactory.create_intent(...)
    
    # Submit to Runtime (which uses ExecutionLifecycleManager)
    result = await runtime_client.submit_intent(intent)
```

✅ **Calls Runtime API** - Goes through ExecutionLifecycleManager

#### 3. RuntimeClient

**File:** `symphainy_platform/civic_systems/experience/sdk/runtime_client.py:163`

```python
async def submit_intent(self, intent: Intent):
    response = await self.client.post(
        f"{self.runtime_url}/api/intent/submit",
        json=intent.to_dict()
    )
```

✅ **Calls Runtime API** - Goes through ExecutionLifecycleManager

---

## Potential Issues

### Legacy Endpoint: `/api/v1/business_enablement/content/upload-file`

**Frontend Usage:**
- `ContentPillarUpload.tsx` calls `/api/v1/business_enablement/content/upload-file`
- `ContentAPIManager.ts` also references this endpoint

**Status:** ⚠️ **NEEDS VERIFICATION**

**Action Required:**
1. Find where this endpoint is defined
2. Verify it uses Runtime/ExecutionLifecycleManager
3. If it bypasses Runtime, it's a **real gap** that needs fixing

---

## E2E Test Updates

### Before (Incorrect)

```python
# Called orchestrator directly - bypassed ExecutionLifecycleManager
content_orch = orchestrators["content"]
result = await content_orch.handle_intent(intent, test_context)
# ❌ No boundary contract created
```

### After (Correct)

```python
# Uses ExecutionLifecycleManager - matches production flow
execution_manager = e2e_setup["execution_manager"]
result = await execution_manager.execute(intent)
# ✅ Boundary contract created automatically
```

**Benefits:**
- Tests real production flow
- Boundary contracts created automatically
- Validates entire system works end-to-end

---

## Recommendations

### For MVP

1. **Ensure all file upload endpoints use Runtime/ExecutionLifecycleManager**
   - If `/api/v1/business_enablement/content/upload-file` exists and bypasses Runtime, fix it
   - All file operations should go through `/api/intent/submit` → Runtime → ExecutionLifecycleManager

2. **Frontend should use `/api/intent/submit` for all operations**
   - This ensures boundary contracts are always created
   - Frontend doesn't need to know about boundary contracts

3. **Remove any direct orchestrator calls from frontend**
   - Frontend should never call orchestrators directly
   - All operations should go through Runtime API

### For Testing

1. **All E2E tests should use ExecutionLifecycleManager**
   - ✅ Updated `test_platform_e2e.py` to use ExecutionLifecycleManager
   - Matches production flow
   - Validates boundary contract creation

---

## Next Steps

1. ✅ **Completed:**
   - Updated E2E test to use ExecutionLifecycleManager
   - Verified Runtime API uses ExecutionLifecycleManager
   - Verified Experience API calls Runtime API

2. ⚠️ **Pending:**
   - Find and verify `/api/v1/business_enablement/content/upload-file` endpoint
   - If it bypasses Runtime, document as gap and fix

---

## Conclusion

**Current Status:**
- ✅ Runtime API properly uses ExecutionLifecycleManager
- ✅ Experience API properly calls Runtime API
- ✅ E2E tests updated to match production flow
- ⚠️ Legacy endpoint needs verification

**If legacy endpoint bypasses Runtime:**
- This is a **real UI gap**
- Should be fixed to use Runtime/ExecutionLifecycleManager
- Boundary contracts are a core architectural concept

---

**Last Updated:** January 25, 2026
