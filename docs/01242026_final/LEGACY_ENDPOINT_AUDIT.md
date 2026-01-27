# Legacy Endpoint Audit

**Date:** January 25, 2026  
**Purpose:** Identify legacy endpoint patterns and determine if they're production issues or just old test code

---

## Executive Summary

⚠️ **Legacy endpoint pattern found in frontend** - `/api/v1/business_enablement/content/upload-file`  
✅ **Current proper pattern** - `/api/intent/submit` with `ingest_file` intent  
❌ **No backend router exists** - Legacy endpoints are not implemented in current codebase

---

## Legacy Endpoint Pattern

### Found in Frontend

**Location 1:** `symphainy-frontend/app/(protected)/pillars/content/components/ContentPillarUpload.tsx:141`

```typescript
const response = await fetch("/api/v1/business_enablement/content/upload-file", {
  method: "POST",
  body: formData,
  headers: {
    "X-Session-Token": sessionToken
  }
});
```

**Location 2:** `symphainy-frontend/shared/services/content/file-processing.ts:53`

```typescript
const response = await fetch('/api/v1/business_enablement/content/upload-file', {
  method: 'POST',
  body: formData,
});
```

### Also Found: Mixed Pattern

**Location 3:** `symphainy-frontend/shared/managers/ContentAPIManager.ts:139`

```typescript
const uploadURL = getApiEndpointUrl('/api/v1/content-pillar/upload-file');
```

**Note:** This uses `/api/v1/content-pillar/upload-file` (different pattern, also likely legacy)

---

## Current Proper Pattern

### Correct Approach: Intent-Based API

**Endpoint:** `/api/intent/submit`  
**Intent Type:** `ingest_file`  
**Flow:** Frontend → Experience API → Runtime API → ExecutionLifecycleManager → Orchestrator

**Example:**

```typescript
// Frontend should use this pattern
const response = await fetch('/api/intent/submit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    intent_type: 'ingest_file',
    tenant_id: tenantId,
    session_id: sessionId,
    solution_id: solutionId,
    parameters: {
      ingestion_type: 'upload',
      file_content: fileContentHex,
      ui_name: fileName,
      file_type: fileType,
      mime_type: mimeType
    }
  })
});
```

**Benefits:**
- ✅ Uses ExecutionLifecycleManager (creates boundary contracts automatically)
- ✅ Consistent with platform architecture
- ✅ Proper intent-based flow
- ✅ Boundary contracts handled automatically

---

## Backend Verification

### Search Results

**No backend routers found for:**
- ❌ `/api/v1/business_enablement/content/upload-file` - **NOT FOUND**
- ❌ `/api/v1/content-pillar/upload-file` - **NOT FOUND**

**Current backend API structure:**
- ✅ `/api/intent/submit` - **EXISTS** (Experience API → Runtime API)
- ✅ `/api/session/*` - **EXISTS** (Session management)
- ✅ `/api/runtime/agent` - **EXISTS** (Agent communication)

### Conclusion

**The legacy endpoints are NOT implemented in the current backend codebase.**

This means:
1. **If frontend calls these endpoints, they will fail** (404 or similar)
2. **This is a frontend bug** - using non-existent endpoints
3. **Not a production/platform issue** - backend doesn't have these endpoints
4. **Legacy code** - old patterns that were never updated

---

## Impact Assessment

### Is This a Production Issue?

**Answer: NO** - These endpoints don't exist in the backend, so:
- Frontend calls to these endpoints will fail
- This is a **frontend bug** (calling non-existent endpoints)
- Not a backend/platform issue

### Is This a Test Pattern?

**Answer: PARTIALLY** - The endpoints are:
- Referenced in frontend code (legacy)
- Not implemented in backend (so they can't work)
- Likely from old architecture before intent-based API

---

## Recommendations

### Immediate Actions

1. **Update Frontend to Use Intent-Based API**
   - Replace `/api/v1/business_enablement/content/upload-file` with `/api/intent/submit`
   - Use `ingest_file` intent type
   - Follow the proper intent-based pattern

2. **Files to Update:**
   - `symphainy-frontend/app/(protected)/pillars/content/components/ContentPillarUpload.tsx`
   - `symphainy-frontend/shared/services/content/file-processing.ts`
   - `symphainy-frontend/shared/managers/ContentAPIManager.ts`

3. **Verify No Other Legacy Patterns**
   - Search for other `/api/v1/business_enablement/*` references
   - Search for other `/api/v1/content-pillar/*` references
   - Update all to use `/api/intent/submit`

### Long-Term

1. **Document Intent-Based API Pattern**
   - Create frontend SDK/helper for intent submission
   - Document all available intents
   - Provide examples for common operations

2. **Remove Legacy Code**
   - Once updated, remove old endpoint references
   - Clean up unused code

---

## Files Requiring Updates

### Frontend Files

1. **ContentPillarUpload.tsx**
   - **Current:** `/api/v1/business_enablement/content/upload-file`
   - **Should be:** `/api/intent/submit` with `ingest_file` intent

2. **file-processing.ts**
   - **Current:** `/api/v1/business_enablement/content/upload-file`
   - **Should be:** `/api/intent/submit` with `ingest_file` intent

3. **ContentAPIManager.ts**
   - **Current:** `/api/v1/content-pillar/upload-file`
   - **Should be:** `/api/intent/submit` with `ingest_file` intent

---

## Conclusion

**Status:** ✅ **NOT A PRODUCTION ISSUE** - Legacy frontend code calling non-existent endpoints

**Action Required:**
- Update frontend to use `/api/intent/submit` with `ingest_file` intent
- This will ensure boundary contracts are created automatically
- Matches current platform architecture

**Priority:** 🟡 **MEDIUM** - Frontend bug, but endpoints don't exist so it's not breaking production (just failing silently or with errors)

---

**Last Updated:** January 25, 2026
