# Phase 3 Readiness Check

**Date:** January 26, 2026  
**Status:** ✅ **ALMOST READY - One Gap to Fill**

---

## ✅ What We Have (Backend)

1. ✅ **Artifact Registry** (State Surface) - Phase 1
2. ✅ **Runtime API: `/api/artifact/resolve`** - Phase 2
3. ✅ **Runtime API: `/api/artifact/list`** - Phase 2
4. ✅ **Artifact Index table** (`artifact_index`) - Phase 2b
5. ✅ **Intent Executions table** (`intent_executions`) - Just completed
6. ✅ **RegistryAbstraction.list_artifacts()** - Implemented
7. ✅ **RegistryAbstraction intent methods** - Implemented
8. ✅ **Structured lineage** - Implemented

---

## ⚠️ What's Missing (Backend)

### Missing: Runtime API Endpoints for Pending Intents

**Need to Add:**
- `POST /api/intent/pending/list` - List pending intents for UI
- `POST /api/intent/pending/create` - Create pending intent (where ingestion_profile lives)

**Why:** Frontend needs these endpoints to:
- Query pending intents for display ("Files with pending parse intents")
- Create pending intents when user selects ingestion_profile

**Status:** ⏳ **TODO** (Quick to add - ~30 minutes)

---

## ✅ What We Have (Frontend)

- Existing `ContentAPIManager` (or equivalent)
- Existing `PlatformState` (or equivalent)
- Existing UI components

---

## ⚠️ What's Missing (Frontend)

### Missing: Artifact-Centric API Methods

**Need to Add:**
- `resolveArtifact()` - Calls `/api/artifact/resolve`
- `listArtifacts()` - Calls `/api/artifact/list`
- `getPendingIntents()` - Calls `/api/intent/pending/list` (NEW)
- `createPendingIntent()` - Calls `/api/intent/pending/create` (NEW)

**Status:** ⏳ **TODO** (Frontend work)

---

## Recommended Sequence

### Step 1: Add Missing Runtime API Endpoints (30 min)

**File:** `symphainy_platform/runtime/runtime_api.py`

**Add:**
- `PendingIntentListRequest` / `PendingIntentListResponse` models
- `PendingIntentCreateRequest` / `PendingIntentCreateResponse` models
- `list_pending_intents()` method in RuntimeAPI
- `create_pending_intent()` method in RuntimeAPI
- `POST /api/intent/pending/list` endpoint
- `POST /api/intent/pending/create` endpoint

**Why First:** Frontend can't work without these endpoints.

---

### Step 2: Add Frontend API Methods (1-2 hours)

**Files:** Frontend API manager files

**Add:**
- `resolveArtifact()`
- `listArtifacts()`
- `getPendingIntents()`
- `createPendingIntent()`

---

### Step 3: Migrate UI Dropdowns (2-3 hours)

**Files:** UI component files

**Update:**
- File selection dropdowns → use `listArtifacts()`
- Parsed file dropdowns → use `listArtifacts()`
- Embedding source dropdowns → use `listArtifacts()`

---

### Step 4: Add Pending Intent UI (1-2 hours)

**Files:** UI component files

**Add:**
- Pending intent indicators
- Create pending intent on profile selection
- Resume pending intent on parse action

---

### Step 5: Test End-to-End (1 hour)

- Test artifact resolution
- Test artifact listing
- Test pending intent creation
- Test pending intent execution
- Test resumable workflow

---

## Then: Intent/Journey Contract Validation

**After Phase 3 Complete:**
1. ✅ Frontend uses artifact-centric APIs
2. ✅ UI shows pending intents
3. ✅ Dropdowns use artifact listing
4. ✅ System is fully artifact-centric

**Then we can:**
- Complete remaining intent contracts
- Validate Journey 1 contract
- Run 3D tests (Functional, Architectural, SRE)
- Test with real UI end-to-end

---

## Answer: Are We Ready?

**Almost!** We need:

1. ⏳ **Add Runtime API endpoints for pending intents** (30 min)
2. ⏳ **Then proceed with Phase 3 frontend integration**

**After Phase 3:**
- ✅ Get back to intent/journey contract validation
- ✅ Test with fully functional artifact-centric system

---

## Recommendation

**Do this now:**
1. Add Runtime API endpoints for pending intents (quick)
2. Then proceed with Phase 3 frontend integration
3. Then get back to intent/journey contract validation

**This sequence makes sense** because:
- Frontend needs the endpoints to work
- Once frontend is integrated, we can test contracts with real UI
- Intent/journey validation will be more meaningful with full system

---

## Summary

**You're thinking correctly!** The sequence is:

1. ✅ **Phases 1-2b Complete** (Backend foundation)
2. ⏳ **Add pending intent API endpoints** (Quick - 30 min)
3. ⏳ **Phase 3: Frontend Integration** (With intent execution log support)
4. ⏳ **Intent/Journey Contract Validation** (Back to morning's work)

**Missing piece:** Runtime API endpoints for pending intents (easy to add).
