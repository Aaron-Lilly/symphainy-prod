# Startup Architecture Testing Plan

**Date:** January 26, 2026  
**Status:** 📋 **READY FOR TESTING**

---

## Test Objectives

1. ✅ Verify services initialize correctly
2. ✅ Verify all API routes are registered
3. ✅ Test artifact listing/resolution
4. ✅ Test pending intents
5. ✅ Test intent execution

---

## Test Scenarios

### 1. Service Initialization Test

**Goal:** Verify object graph builds correctly

**Steps:**
1. Call `create_runtime_services(config)`
2. Verify RuntimeServices object created
3. Verify all required services are not None
4. Verify PublicWorksFoundationService initialized
5. Verify StateSurface created
6. Verify ExecutionLifecycleManager created
7. Verify IntentRegistry has handlers registered

**Expected:**
- All services initialized
- No exceptions
- Intent handlers registered

---

### 2. FastAPI App Creation Test

**Goal:** Verify FastAPI app receives services correctly

**Steps:**
1. Create RuntimeServices
2. Call `create_fastapi_app(services)`
3. Verify FastAPI app created
4. Verify routes are registered
5. Check `/health` endpoint works

**Expected:**
- FastAPI app created
- Routes registered
- Health endpoint returns 200

---

### 3. API Route Registration Test

**Goal:** Verify all routes are accessible

**Routes to Test:**
- ✅ `GET /health`
- ✅ `POST /api/session/create`
- ✅ `POST /api/intent/submit`
- ✅ `POST /api/artifact/resolve`
- ✅ `POST /api/artifact/list`
- ✅ `POST /api/intent/pending/list`
- ✅ `POST /api/intent/pending/create`

**Expected:**
- All routes return 200 or appropriate status
- No 404 errors

---

### 4. Intent Handler Registration Test

**Goal:** Verify intent handlers are registered

**Steps:**
1. Create RuntimeServices
2. Check IntentRegistry
3. Verify content realm intents registered
4. Test intent submission

**Expected:**
- 15 content realm intents registered
- Intent submission routes to ContentOrchestrator

---

### 5. End-to-End Workflow Test

**Goal:** Verify complete workflow works

**Steps:**
1. Start runtime service
2. Create session
3. Submit intent (e.g., `ingest_file`)
4. Verify intent executes
5. Verify artifacts created
6. Test artifact listing
7. Test artifact resolution

**Expected:**
- Complete workflow executes
- Artifacts created and accessible
- No errors

---

## Running Tests

### Manual Test (Quick)
```bash
# Start runtime service
cd /home/founders/demoversion/symphainy_source_code
python3 runtime_main.py

# In another terminal, test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/artifact/list -H "Content-Type: application/json" -d '{"tenant_id":"test"}'
```

### Integration Test (Comprehensive)
```bash
# Run Phase 3 artifact API tests
cd symphainy-frontend
npm run test:integration -- phase3_artifact_api.test.ts
```

---

## Success Criteria

### ✅ All Tests Pass
- Services initialize without errors
- All routes are registered
- Intent handlers work
- Artifacts can be listed/resolved
- Pending intents work

### ✅ No Red Flags
- No side effects on import ✅
- Routes don't create services ✅
- Startup order is explicit ✅
- Works identically locally and in Docker ✅

---

## Next Steps After Testing

1. **Fix Any Issues** - Address test failures
2. **Register Other Realm Handlers** - Insights, Outcomes, Journey, Admin
3. **Intent/Journey Contract Validation** - Back to morning's work

---

## Status

**Implementation:** ✅ **COMPLETE**
**Testing:** ⏳ **READY TO START**
