# Holistic E2E 3-Dimensional Test Plan

**Date:** January 25, 2026  
**Status:** 📋 **TEMPLATE - TO BE COMPLETED AFTER ALL PHASES**  
**Purpose:** Comprehensive system validation across all pages/pillars/components

---

## Executive Summary

This document provides a comprehensive 3-dimensional test plan for validating the entire Symphainy platform after all phases are complete. It tests functional, architectural, and SRE perspectives across all pages, pillars, and components to ensure we have a **real working platform**.

**Key Principle:** This test plan validates the **entire system working together**, not individual features in isolation.

---

## Test Philosophy

### Three-Perspective Validation

Every aspect of the platform must be validated from three perspectives:

1. **Functional:** Does it work as intended from a user perspective?
2. **Architectural:** Does it follow platform principles and patterns?
3. **SRE/Distributed Systems:** Does it work in a production-like multi-container environment?

**Success Criteria:** All three dimensions must pass for the platform to be considered production-ready.

---

## System Architecture Context

### Deployment Topology

```
Browser (User)
  ↓ HTTP/HTTPS
Traefik Reverse Proxy (Port 80/443)
  ↓ Routing Rules
Frontend Container (Next.js)
  ↓ API Calls / WebSocket
Backend Container (FastAPI Runtime)
  ↓ Intent Execution
ExecutionLifecycleManager
  ↓ Policy & Governance
Civic Systems (Data Steward SDK)
  ↓ Storage & Ingestion
Public Works (GCS, Supabase)
```

### System Boundaries (11+)

1. **Browser → Traefik Proxy** (HTTP/HTTPS)
2. **Traefik → Frontend Container** (Static Assets, API Routes)
3. **Frontend → Backend** (API Calls - `/api/intent/submit`)
4. **Frontend → Backend** (WebSocket - Agent Communication)
5. **Backend → Auth/Authorization** (Session Validation)
6. **Backend → Runtime/ExecutionLifecycleManager** (Intent Execution)
7. **Runtime → Data Steward SDK** (Boundary Contract Creation)
8. **Data Steward → MaterializationPolicyStore** (Policy Retrieval)
9. **Content Realm → IngestionAbstraction** (GCS File Upload)
10. **Content Realm → FileStorageAbstraction** (Supabase Metadata)
11. **Backend → Agent Services** (Guide/Liaison Agent Communication)

---

## Test Coverage Matrix

### By Page/Pillar

| Page/Pillar | Functional | Architectural | SRE Boundaries |
|------------|------------|---------------|----------------|
| Landing Page | ⏳ | ⏳ | ⏳ |
| Content Pillar | ⏳ | ⏳ | ⏳ |
| Insights Pillar | ⏳ | ⏳ | ⏳ |
| Journey Pillar | ⏳ | ⏳ | ⏳ |
| Outcomes Pillar | ⏳ | ⏳ | ⏳ |
| Admin Dashboard | ⏳ | ⏳ | ⏳ |
| Artifact Library | ⏳ | ⏳ | ⏳ |
| Login Page | ⏳ | ⏳ | ⏳ |

### By User Journey

| Journey | Functional | Architectural | SRE Boundaries |
|---------|------------|---------------|----------------|
| New User Journey | ⏳ | ⏳ | ⏳ |
| Artifact Creation Journey | ⏳ | ⏳ | ⏳ |
| Coexistence Analysis Journey | ⏳ | ⏳ | ⏳ |
| Cross-Pillar Synthesis Journey | ⏳ | ⏳ | ⏳ |

### By System Boundary

| Boundary | Functional | Architectural | SRE Validation |
|----------|------------|---------------|----------------|
| Browser → Traefik | ⏳ | ⏳ | ⏳ |
| Traefik → Frontend | ⏳ | ⏳ | ⏳ |
| Frontend → Backend (API) | ⏳ | ⏳ | ⏳ |
| Frontend → Backend (WebSocket) | ⏳ | ⏳ | ⏳ |
| Backend → Auth | ⏳ | ⏳ | ⏳ |
| Backend → Runtime | ⏳ | ⏳ | ⏳ |
| Runtime → Data Steward | ⏳ | ⏳ | ⏳ |
| Data Steward → Policy Store | ⏳ | ⏳ | ⏳ |
| Content → Ingestion (GCS) | ⏳ | ⏳ | ⏳ |
| Content → Storage (Supabase) | ⏳ | ⏳ | ⏳ |
| Backend → Agent Services | ⏳ | ⏳ | ⏳ |

---

## Phase-by-Phase Test Results

### Phase 1: Foundation & Agent Visibility

**Status:** ✅ **COMPLETE** (with documented issues)

#### Functional Tests
- ✅ Chat panel visible by default
- ✅ Agent indicators display correctly
- ✅ Pillar badges show correct Liaison Agent
- ✅ Toggle between Guide and Liaison works
- ⚠️ Next.js Server Action error in logs (non-blocking)

#### Architectural Tests
- ✅ No Jotai atoms (removed)
- ✅ PlatformStateProvider used correctly
- ✅ SessionBoundaryProvider used correctly
- ✅ Agent info setup in all pillar pages
- ✅ No legacy endpoint calls

#### SRE Tests
- ⏳ **Deferred to holistic E2E testing**
- **Note:** SRE boundaries are system-wide and will be validated holistically

#### Known Issues
1. **Next.js Server Action Error** (Non-blocking)
   - **Error:** "Failed to find Server Action 'x'. This request might be from an older or newer deployment. Original error: Cannot read properties of undefined (reading 'workers')"
   - **Location:** Frontend logs (`symphainy-frontend`)
   - **Impact:** Does not affect Phase 1 functionality (chat panel, agent visibility, pillar badges all work correctly)
   - **Root Cause:** Likely a Next.js Server Actions configuration issue or deployment mismatch
   - **Status:** Monitor during holistic E2E testing. If persistent, investigate Next.js Server Actions configuration.
   - **Action:** Not a blocker for Phase 1 completion. Will investigate during holistic E2E testing if it affects functionality.

#### Test Execution
- **Date:** January 25, 2026
- **Script:** `scripts/smoke_test_phase1.sh`
- **Results:** 12 passed, 1 failed (Next.js error - non-blocking), 6 warnings (expected)

---

### Phase 2: Artifact Plane Showcase

**Status:** ✅ **COMPLETE**

#### Functional Tests
- ✅ Artifact gallery displays on landing page
- ✅ Artifact library page accessible
- ✅ Filtering and search work correctly
- ✅ Artifact cards display correctly
- ✅ Navigation to pillar pages works
- ✅ Lifecycle status displays correctly
- ✅ Synthesis inputs show correctly

#### Architectural Tests
- ✅ No legacy endpoint calls
- ✅ Uses PlatformStateProvider (`getRealmState`)
- ✅ No direct API calls (uses realm state)
- ✅ All components created correctly
- ✅ Integration in landing page correct
- ✅ Outcomes pillar enhancements present

#### SRE Tests
- ⏳ **Deferred to holistic E2E testing**
- **Note:** SRE boundaries are system-wide and will be validated holistically

#### Known Issues
- None identified

#### Test Execution
- **Date:** January 25, 2026
- **Script:** `scripts/smoke_test_phase2.sh`
- **Results:** 6 passed, 0 failed, 1 warning (pre-existing TypeScript errors)
- **Full Details:** See `PHASE_1_2_TEST_RESULTS_SUMMARY.md`

---

### Phase 3: Coexistence Fabric Showcase

**Status:** ✅ **COMPLETE**

#### Functional Tests
- ✅ Coexistence explanation displays on landing page
- ✅ Coexistence diagram displays (static)
- ✅ Coexistence analysis enhanced in Journey pillar
- ✅ Coexistence context shown in Outcomes pillar

#### Architectural Tests
- ✅ No legacy endpoint calls
- ✅ Informational components only (no API calls)
- ✅ Preserves Session-First architecture
- ✅ Uses existing `analyze_coexistence` intent

#### SRE Tests
- ⏳ **Deferred to holistic E2E testing**

#### Test Execution
- **Date:** January 25, 2026
- **Script:** `scripts/smoke_test_phase3.sh`
- **Results:** 5 passed, 0 failed, 1 warning (pattern matching)
- **Full Details:** See `PHASE_3_COEXISTENCE_FABRIC_COMPLETE.md`

---

### Phase 4: Advanced Capabilities

**Status:** ⏳ **PENDING**

#### Functional Tests
- ⏳ Lineage visualization enhanced
- ⏳ Process optimization works
- ⏳ Relationship mapping works

#### Architectural Tests
- ⏳ No legacy endpoint calls
- ⏳ Uses intent-based API
- ⏳ Preserves Session-First architecture

#### SRE Tests
- ⏳ **Deferred to holistic E2E testing**

---

## Holistic E2E Test Scenarios

### Scenario 1: New User Journey

**Path:** Landing → Content → Upload → Parse → Insights → Journey → Outcomes

**Functional Test:**
1. User lands on landing page
2. Sees artifact gallery (if artifacts exist)
3. Sees coexistence explanation
4. Clicks "Start Journey"
5. Navigates to Content pillar
6. Uploads file
7. Parses file
8. Navigates to Insights pillar
9. Generates insights
10. Navigates to Journey pillar
11. Analyzes coexistence
12. Navigates to Outcomes pillar
13. Generates artifacts
14. Views artifacts

**Architectural Test:**
- ✅ All operations use intent-based API
- ✅ All state via PlatformStateProvider
- ✅ Session via SessionBoundaryProvider
- ✅ No legacy endpoint calls

**SRE Test:**
- ✅ All boundaries crossed successfully
- ✅ No errors in logs
- ✅ State synchronization works
- ✅ WebSocket connections stable

---

### Scenario 2: Artifact Creation Journey

**Path:** Outcomes → Generate Roadmap → Generate POC → Generate Blueprint → View Artifacts

**Functional Test:**
1. User in Outcomes pillar
2. Generates roadmap
3. Generates POC
4. Generates blueprint
5. Views artifacts in modal
6. Exports artifact
7. Navigates to artifact library
8. Filters artifacts
9. Views artifact details

**Architectural Test:**
- ✅ All artifact operations use intent-based API
- ✅ Artifacts retrieved from realm state
- ✅ No direct API calls

**SRE Test:**
- ✅ Artifact generation boundaries work
- ✅ Artifact storage boundaries work
- ✅ Artifact retrieval boundaries work

---

### Scenario 3: Coexistence Analysis Journey

**Path:** Journey → Upload SOP → Upload Workflow → Analyze Coexistence → Generate Blueprint

**Functional Test:**
1. User in Journey pillar
2. Uploads SOP file
3. Uploads workflow file
4. Analyzes coexistence
5. Views coexistence blueprint
6. Generates coexistence blueprint artifact

**Architectural Test:**
- ✅ Coexistence analysis uses `analyze_coexistence` intent
- ✅ Blueprint generation uses intent-based API

**SRE Test:**
- ✅ Coexistence analysis boundaries work
- ✅ Blueprint generation boundaries work

---

### Scenario 4: Cross-Pillar Synthesis Journey

**Path:** Content → Insights → Journey → Outcomes Synthesis

**Functional Test:**
1. User completes work in Content pillar
2. User completes work in Insights pillar
3. User completes work in Journey pillar
4. User navigates to Outcomes pillar
5. Synthesis automatically generated
6. Synthesis inputs displayed
7. Artifacts generated from synthesis

**Architectural Test:**
- ✅ Synthesis uses `synthesize_outcome` intent
- ✅ Cross-pillar data retrieved from realm states

**SRE Test:**
- ✅ Synthesis boundaries work
- ✅ Cross-pillar data retrieval works

---

## SRE Boundary Validation

### Boundary 1: Browser → Traefik Proxy

**What Must Be True:**
- Browser can resolve domain/IP
- Traefik is listening on port 80/443
- SSL certificate valid (if HTTPS)
- Network connectivity exists

**Test:**
```bash
# Check Traefik is running
docker ps | grep traefik

# Check Traefik logs
docker logs symphainy-traefik --tail 100

# Check browser network tab
# - All requests show 200 status
# - No CORS errors
# - No 404 errors
```

**Success Criteria:**
- ✅ All page loads successful
- ✅ No network errors in browser
- ✅ Traefik routing logs show requests

---

### Boundary 2: Traefik → Frontend Container

**What Must Be True:**
- Traefik routing rules configured correctly
- Frontend container is running
- Frontend container is healthy
- Next.js server responding

**Test:**
```bash
# Check frontend container status
docker ps | grep frontend

# Check frontend logs
docker logs symphainy-frontend --tail 100

# Check frontend build
docker logs symphainy-frontend | grep -i "compiled\|ready"
```

**Success Criteria:**
- ✅ Frontend container healthy
- ✅ No build errors
- ✅ Next.js server responding

---

### Boundary 3: Frontend → Backend (API Calls)

**What Must Be True:**
- Frontend can resolve backend service
- Backend API endpoint exists (`/api/intent/submit`)
- Request format matches backend expectations
- CORS configured correctly

**Test:**
```bash
# Check backend container status
docker ps | grep runtime

# Check backend logs for intent submissions
docker logs symphainy-runtime --tail 200 | grep -i "intent.*submit"

# Check browser network tab
# - API calls show 200/201 status
# - Request payload correct
# - Response format correct
```

**Success Criteria:**
- ✅ All intent submissions successful
- ✅ No API errors
- ✅ Execution IDs returned

---

### Boundary 4: Frontend → Backend (WebSocket)

**What Must Be True:**
- WebSocket connection can be established
- Backend WebSocket endpoint available
- Connection persists
- Messages can be sent/received

**Test:**
```bash
# Check backend logs for WebSocket connections
docker logs symphainy-runtime --tail 100 | grep -i "websocket\|ws.*connect"

# Check frontend logs for WebSocket
docker logs symphainy-frontend --tail 100 | grep -i "websocket\|ws.*connect"

# Check browser network tab
# - WebSocket connection shows "101 Switching Protocols"
# - Connection status is "Open"
# - Messages can be sent/received
```

**Success Criteria:**
- ✅ WebSocket connections established
- ✅ Agent messages received
- ✅ No connection drops

---

### Boundary 5: Backend → Auth/Authorization

**What Must Be True:**
- Session token valid
- Tenant ID valid
- User authorized for operation
- Session exists in session store

**Test:**
```bash
# Check backend auth logs
docker logs symphainy-runtime --tail 100 | grep -i "auth\|session\|tenant\|401\|403"

# Check session store (Redis)
docker exec symphainy-redis redis-cli KEYS "session:*"
```

**Success Criteria:**
- ✅ No auth errors (401, 403)
- ✅ Sessions validated correctly
- ✅ Tenant IDs match

---

### Boundary 6: Backend → Runtime/ExecutionLifecycleManager

**What Must Be True:**
- ExecutionLifecycleManager initialized
- Intent type registered
- Intent handler exists
- Execution context created

**Test:**
```bash
# Check runtime logs
docker logs symphainy-runtime --tail 200 | grep -i "execution\|intent\|executionlifecyclemanager"

# Check intent registration
docker logs symphainy-runtime | grep -i "intent.*registered\|supported.*intent"
```

**Success Criteria:**
- ✅ All intents registered
- ✅ Executions started successfully
- ✅ No handler not found errors

---

### Boundary 7: Runtime → Data Steward SDK

**What Must Be True:**
- DataStewardSDK initialized
- DataStewardSDK available in ExecutionLifecycleManager
- SDK can communicate with Data Steward Primitives

**Test:**
```bash
# Check Data Steward SDK initialization
docker logs symphainy-runtime | grep -i "data.*steward.*sdk\|data.*steward.*initialized"

# Check boundary contract creation
docker logs symphainy-runtime | grep -i "boundary.*contract\|request.*data.*access"
```

**Success Criteria:**
- ✅ Data Steward SDK initialized
- ✅ Boundary contracts created
- ✅ No SDK errors

---

### Boundary 8: Data Steward → MaterializationPolicyStore

**What Must Be True:**
- MaterializationPolicyStore initialized
- Policy store has database connection (Supabase)
- Policy can be retrieved (tenant-specific or default)
- Policy decision can be made

**Test:**
```bash
# Check MaterializationPolicyStore initialization
docker logs symphainy-runtime | grep -i "materialization.*policy.*store\|policy.*store.*initialized"

# Check policy retrieval
docker logs symphainy-runtime | grep -i "policy.*retrieved\|get.*policy\|default.*policy"
```

**Success Criteria:**
- ✅ Policy store initialized
- ✅ Policies retrieved successfully
- ✅ No policy errors

---

### Boundary 9: Content Realm → IngestionAbstraction (GCS)

**What Must Be True:**
- IngestionAbstraction initialized
- GCS connection configured
- File can be uploaded to GCS
- File metadata stored

**Test:**
```bash
# Check IngestionAbstraction initialization
docker logs symphainy-runtime | grep -i "ingestion.*abstraction\|gcs.*initialized"

# Check file upload to GCS
docker logs symphainy-runtime | grep -i "gcs.*upload\|file.*uploaded\|ingestion.*result"
```

**Success Criteria:**
- ✅ Files uploaded to GCS
- ✅ No upload errors
- ✅ File metadata stored

---

### Boundary 10: Content Realm → FileStorageAbstraction (Supabase)

**What Must Be True:**
- FileStorageAbstraction initialized
- Supabase connection configured
- File metadata can be stored
- Boundary contract stored

**Test:**
```bash
# Check FileStorageAbstraction initialization
docker logs symphainy-runtime | grep -i "file.*storage.*abstraction\|supabase.*initialized"

# Check Supabase operations
docker logs symphainy-runtime | grep -i "supabase\|database.*write\|boundary.*contract.*stored"
```

**Success Criteria:**
- ✅ Supabase operations successful
- ✅ File metadata stored
- ✅ Boundary contracts stored

---

### Boundary 11: Backend → Agent Services

**What Must Be True:**
- Agent services available
- Messages can be sent to agents
- Agent responses received
- Agent state synchronized

**Test:**
```bash
# Check backend logs for agent communication
docker logs symphainy-runtime --tail 100 | grep -i "agent.*message\|guide.*agent\|liaison.*agent"

# Check frontend logs for agent communication
docker logs symphainy-frontend --tail 100 | grep -i "agent.*response\|websocket.*message"
```

**Success Criteria:**
- ✅ Agent communication working
- ✅ Messages delivered
- ✅ Responses received

---

## Comprehensive Test Execution Plan

### Pre-Test Validation

```bash
# 1. Check all containers are running
docker ps

# 2. Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# 3. Check frontend build
docker logs symphainy-frontend | grep -i "compiled\|ready"

# 4. Check backend health
docker logs symphainy-runtime --tail 20 | grep -i "started\|ready\|uvicorn"

# 5. Check Traefik routing
docker exec symphainy-traefik cat /etc/traefik/traefik.yml
```

---

### Test Execution Workflow

#### Step 1: Functional Testing (Browser)
1. Open browser DevTools (Network, Console, Application tabs)
2. Execute each user journey scenario
3. Verify UI reflects correct state
4. Capture screenshots
5. Document any issues

#### Step 2: Architectural Validation
```bash
# Run comprehensive architectural checks
./scripts/holistic_architectural_validation.sh
```

**Validates:**
- No legacy endpoint calls across all pages
- PlatformStateProvider usage everywhere
- SessionBoundaryProvider usage everywhere
- Intent-based API usage everywhere
- No anti-patterns

#### Step 3: SRE Boundary Validation
```bash
# Run SRE boundary validation
./scripts/holistic_sre_validation.sh
```

**Validates:**
- All 11+ system boundaries
- No errors in any boundary
- Logs confirm successful operations
- System is observable

---

## Success Criteria

### Functional
- ✅ All user journeys complete successfully
- ✅ All features work as intended
- ✅ UI reflects correct state
- ✅ No user-facing errors

### Architectural
- ✅ No legacy endpoint calls
- ✅ All operations use intent-based API
- ✅ PlatformStateProvider used everywhere
- ✅ SessionBoundaryProvider used everywhere
- ✅ No anti-patterns

### SRE/Distributed Systems
- ✅ All boundaries crossed successfully
- ✅ No errors in any boundary
- ✅ Logs confirm successful operations
- ✅ WebSocket connections stable
- ✅ State synchronization working
- ✅ System is observable

---

## Failure Investigation Checklist

If any test fails:

1. **Identify Failed Dimension:**
   - Functional failure?
   - Architectural failure?
   - SRE failure?

2. **Identify Failed Boundary:**
   - Which system boundary failed?
   - Check logs for that boundary
   - Review failure modes

3. **Root Cause Analysis:**
   - Check preconditions
   - Review common failure modes
   - Check logs for specific errors

4. **Fix and Verify:**
   - Fix identified issue
   - Re-run tests
   - Verify all dimensions pass

---

## Test Execution Scripts

### Holistic Architectural Validation
**Location:** `scripts/holistic_architectural_validation.sh`

**Purpose:** Validate architectural compliance across all pages/pillars

### Holistic SRE Validation
**Location:** `scripts/holistic_sre_validation.sh`

**Purpose:** Validate all system boundaries end-to-end

### Holistic Functional Test Guide
**Location:** `docs/01242026_final/HOLISTIC_FUNCTIONAL_TEST_GUIDE.md`

**Purpose:** Manual functional testing checklist for all user journeys

---

## Test Results Summary

### Phase 1 Results
- **Date:** January 25, 2026
- **Status:** ✅ Complete (with documented issues)
- **Smoke Test Script:** `scripts/smoke_test_phase1.sh`
- **Tests Passed:** 12
- **Tests Failed:** 1 (Next.js Server Action error - non-blocking)
- **Warnings:** 6 (expected - no user interaction yet)
- **Known Issues:** 
  1. **Next.js Server Action Error** (Non-blocking)
     - **Error:** "Failed to find Server Action 'x'. This request might be from an older or newer deployment. Original error: Cannot read properties of undefined (reading 'workers')"
     - **Location:** Frontend logs (`symphainy-frontend`)
     - **Impact:** Does not affect Phase 1 functionality (chat panel, agent visibility, pillar badges all work)
     - **Root Cause:** Likely a Next.js Server Actions configuration issue or deployment mismatch
     - **Status:** Monitor during holistic E2E testing. If persistent, investigate Next.js Server Actions configuration.
     - **Action:** Not a blocker for Phase 1 completion. Will investigate during holistic E2E testing if it affects functionality.

### Phase 2 Results
- **Date:** January 25, 2026
- **Status:** ✅ Complete
- **Smoke Test Script:** `scripts/smoke_test_phase2.sh`
- **Tests Passed:** 6
- **Tests Failed:** 0
- **Warnings:** 1 (TypeScript compilation errors - pre-existing, not related to Phase 2)
- **Known Issues:** None identified

**Test Details:**
- ✅ No legacy endpoint calls in Phase 2 components
- ✅ PlatformStateProvider used in Phase 2 components
- ✅ No direct API calls (using getRealmState)
- ✅ All Phase 2 components created (ArtifactCard, ArtifactGallery, artifacts page)
- ✅ ArtifactGallery integrated in landing page
- ✅ Outcomes pillar enhancements found (synthesis inputs, lifecycle status)

**TypeScript Warnings:**
- Pre-existing TypeScript errors in other files (ParsePreview.tsx, DataMappingSection.tsx, etc.)
- Not related to Phase 2 changes
- Will be addressed separately

### Phase 3 Results
- **Status:** ⏳ Pending

### Phase 4 Results
- **Status:** ⏳ Pending

### Holistic E2E Results
- **Status:** ⏳ To be executed after all phases complete
- **Execution Date:** TBD
- **Results:** TBD

---

## Next Steps

1. **Complete remaining phases** (Phase 3, Phase 4)
2. **Execute smoke tests** at end of each phase
3. **Create holistic test scripts** (architectural, SRE, functional)
4. **Execute holistic E2E testing** after all phases complete
5. **Document results** and fix any issues
6. **Validate production readiness**

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 📋 **TEMPLATE - TO BE COMPLETED AFTER ALL PHASES**
