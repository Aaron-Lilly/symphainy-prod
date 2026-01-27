# Phase 3: Frontend Integration Plan

**Date:** January 26, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Prerequisites:** Phase 1, Phase 2, Phase 2b complete

---

## Summary

Phase 3 integrates the artifact-centric architecture and intent execution log into the frontend. This includes artifact resolution, artifact listing, and pending intent management.

---

## ✅ Prerequisites Complete

### Backend Ready:
1. ✅ Artifact Registry (State Surface) - Phase 1
2. ✅ Runtime API endpoints (`/api/artifact/resolve`, `/api/artifact/list`) - Phase 2
3. ✅ Artifact Index table (`artifact_index`) - Phase 2b
4. ✅ Intent Executions table (`intent_executions`) - Just completed
5. ✅ RegistryAbstraction.list_artifacts() - Implemented
6. ✅ RegistryAbstraction intent methods (create_pending_intent, get_pending_intents) - Implemented
7. ✅ Structured lineage in artifact_index - Implemented

---

## Phase 3 Implementation Plan

### Step 1: Add Artifact API Methods to Frontend

**Files to Update:**
- `ContentAPIManager.ts` (or equivalent)
- `PlatformState.ts` (or equivalent)

**New Methods Needed:**

#### 1.1 `resolveArtifact()`
```typescript
async resolveArtifact(
  artifactId: string,
  artifactType: string,
  tenantId: string
): Promise<ArtifactRecord> {
  // Calls POST /api/artifact/resolve
  // Returns full artifact record with materializations
}
```

#### 1.2 `listArtifacts()`
```typescript
async listArtifacts(filters: {
  tenantId: string,
  artifactType?: string,
  lifecycleState?: string,
  eligibleFor?: string  // Next intent
}): Promise<ArtifactListItem[]> {
  // Calls POST /api/artifact/list
  // Returns artifact metadata (not content)
}
```

#### 1.3 `getPendingIntents()` (NEW - for intent execution log)
```typescript
async getPendingIntents(filters: {
  tenantId: string,
  targetArtifactId?: string,
  intentType?: string
}): Promise<PendingIntent[]> {
  // Calls new endpoint: POST /api/intent/pending
  // Returns pending intents with context (ingestion_profile)
}
```

#### 1.4 `createPendingIntent()` (NEW - for intent execution log)
```typescript
async createPendingIntent(
  intentType: string,
  targetArtifactId: string,
  context: {
    ingestion_profile?: string,
    parse_options?: any
  },
  tenantId: string
): Promise<{ intentId: string, status: string }> {
  // Calls new endpoint: POST /api/intent/pending/create
  // Creates pending intent where ingestion_profile lives
}
```

---

### Step 2: Add Runtime API Endpoints for Pending Intents

**File:** `symphainy_platform/runtime/runtime_api.py`

**New Endpoints:**

#### 2.1 `POST /api/intent/pending/list`
```python
async def list_pending_intents_endpoint(request: PendingIntentListRequest):
    """List pending intents for UI."""
    return await runtime_api.list_pending_intents(request)
```

#### 2.2 `POST /api/intent/pending/create`
```python
async def create_pending_intent_endpoint(request: PendingIntentCreateRequest):
    """Create pending intent (where ingestion_profile lives)."""
    return await runtime_api.create_pending_intent(request)
```

**New Methods in RuntimeAPI:**
```python
async def list_pending_intents(request: PendingIntentListRequest) -> PendingIntentListResponse:
    """List pending intents via RegistryAbstraction."""
    if not self.registry_abstraction:
        return PendingIntentListResponse(intents=[], total=0)
    
    intents = await self.registry_abstraction.get_pending_intents(
        tenant_id=request.tenant_id,
        target_artifact_id=request.target_artifact_id,
        intent_type=request.intent_type
    )
    return PendingIntentListResponse(intents=intents, total=len(intents))

async def create_pending_intent(request: PendingIntentCreateRequest) -> PendingIntentCreateResponse:
    """Create pending intent via RegistryAbstraction."""
    if not self.registry_abstraction:
        raise HTTPException(500, "Registry abstraction not available")
    
    result = await self.registry_abstraction.create_pending_intent(
        intent_id=request.intent_id or f"{request.intent_type}_{request.target_artifact_id}_{generate_event_id()}",
        intent_type=request.intent_type,
        target_artifact_id=request.target_artifact_id,
        context=request.context,
        tenant_id=request.tenant_id,
        user_id=request.user_id,
        session_id=request.session_id
    )
    
    if result.get("success"):
        return PendingIntentCreateResponse(
            intent_id=result["data"]["intent_id"],
            status="pending"
        )
    else:
        raise HTTPException(500, result.get("error"))
```

---

### Step 3: Migrate UI Dropdowns

**Current Pattern (WRONG):**
```typescript
// OLD: List files
const files = await contentAPIManager.listFiles(tenantId);
// Returns file-centric objects
```

**New Pattern (CORRECT):**
```typescript
// NEW: List artifacts filtered by eligibility
const artifacts = await contentAPIManager.listArtifacts({
  tenantId: tenantId,
  artifactType: "file",
  lifecycleState: "READY",
  eligibleFor: "parse_content"  // Next intent
});
// Returns artifact-centric objects with eligibility
```

**UI Components to Update:**
- File upload dropdowns
- Parsed file dropdowns
- Embedding source dropdowns
- Any "select file" components

---

### Step 4: Add Pending Intent UI

**New UI Features:**

#### 4.1 Show Pending Intents
```typescript
// Query pending intents for display
const pendingIntents = await contentAPIManager.getPendingIntents({
  tenantId: tenantId,
  intentType: "parse_content"
});

// Display: "3 files with pending parse intents"
// Show list of files with pending parse actions
```

#### 4.2 Create Pending Intent on Profile Selection
```typescript
// When user selects ingestion_profile after upload
await contentAPIManager.createPendingIntent(
  "parse_content",
  fileId,
  {
    ingestion_profile: selectedProfile,  // "structured", "unstructured", "hybrid", etc.
    parse_options: {}
  },
  tenantId
);

// Intent persists → can resume later
```

#### 4.3 Resume Pending Intent
```typescript
// When user clicks "Parse" on file with pending intent
// Just submit parse_content intent - backend finds pending intent automatically
await submitIntent({
  intent_type: "parse_content",
  file_id: fileId
  // ingestion_profile comes from pending intent ✅
});
```

---

## Implementation Checklist

### Backend (Runtime API)
- [ ] Add `PendingIntentListRequest` and `PendingIntentListResponse` models
- [ ] Add `PendingIntentCreateRequest` and `PendingIntentCreateResponse` models
- [ ] Add `list_pending_intents()` method to RuntimeAPI
- [ ] Add `create_pending_intent()` method to RuntimeAPI
- [ ] Add `POST /api/intent/pending/list` endpoint
- [ ] Add `POST /api/intent/pending/create` endpoint

### Frontend (ContentAPIManager)
- [ ] Add `resolveArtifact()` method
- [ ] Add `listArtifacts()` method
- [ ] Add `getPendingIntents()` method
- [ ] Add `createPendingIntent()` method

### Frontend (UI Components)
- [ ] Migrate file dropdowns to use `listArtifacts()`
- [ ] Add pending intent indicators ("Files with pending parse")
- [ ] Update file upload flow to create pending intent on profile selection
- [ ] Update parse action to use pending intents

---

## Key Patterns

### Artifact Resolution (Authoritative)
```typescript
// Get full artifact content
const artifact = await resolveArtifact(artifactId, "file", tenantId);
// Returns: full artifact record with materializations
// Use: When you need actual artifact content
```

### Artifact Listing (Discovery)
```typescript
// List artifacts for dropdowns
const artifacts = await listArtifacts({
  tenantId,
  artifactType: "file",
  lifecycleState: "READY",
  eligibleFor: "parse_content"
});
// Returns: artifact metadata (not content)
// Use: For UI dropdowns, filtering
```

### Pending Intent Management
```typescript
// Create pending intent (ingestion_profile lives here)
await createPendingIntent("parse_content", fileId, {
  ingestion_profile: "hybrid"
}, tenantId);

// Query pending intents
const pending = await getPendingIntents({
  tenantId,
  intentType: "parse_content"
});

// Resume: Just submit intent, backend finds pending intent
await submitIntent({ intent_type: "parse_content", file_id: fileId });
```

---

## What About Intent/Journey Contracts?

**You're right!** After Phase 3, we should get back to:

1. **Intent Contract Validation** - Complete remaining content realm intent contracts
2. **Journey Contract Validation** - Complete Journey 1 contract validation
3. **3D Testing** - Functional, Architectural, SRE testing

**But Phase 3 comes first** because:
- Frontend needs artifact-centric APIs to work properly
- UI needs to show pending intents
- Dropdowns need artifact listing
- Then we can test end-to-end with real UI

---

## Next Steps

1. **Add Runtime API endpoints for pending intents** (Step 2)
2. **Add frontend API methods** (Step 1)
3. **Migrate UI dropdowns** (Step 3)
4. **Add pending intent UI** (Step 4)
5. **Test end-to-end**
6. **Then: Intent/Journey contract validation**

---

## Status

**Ready for Phase 3?** ✅ **YES**

**Prerequisites:** ✅ All complete
**Backend APIs:** ✅ Ready (need pending intent endpoints)
**Frontend:** ⏳ Ready to implement

**After Phase 3:** Intent/Journey contract validation

---

## Summary

You're thinking correctly! The sequence is:

1. ✅ **Phase 1-2b Complete** (Backend foundation)
2. ⏳ **Phase 3: Frontend Integration** (Add artifact APIs + pending intents)
3. ⏳ **Intent/Journey Contract Validation** (Back to morning's work)

Phase 3 incorporates the new intent execution log so the UI can:
- Show pending intents
- Create pending intents when user selects ingestion_profile
- Resume pending intents when user clicks "Parse"

Then we can validate intent/journey contracts with a fully functional artifact-centric system.
