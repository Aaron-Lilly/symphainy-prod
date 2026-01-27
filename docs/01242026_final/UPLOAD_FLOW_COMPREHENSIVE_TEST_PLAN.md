# Upload Flow Comprehensive Test Plan

**Date:** January 25, 2026  
**Status:** ✅ **READY FOR EXECUTION**  
**Test Target:** Two-Phase File Upload (Upload → Save)

---

## Test Philosophy

### Three-Perspective Approach

1. **Functional Testing:** Does the feature work as intended?
2. **Architectural Testing:** Does it follow platform principles?
3. **SRE/Distributed Systems Testing:** Does it work in production-like environment?

---

## System Architecture Context

### Deployment Topology

```
Browser (User) 
  ↓ HTTP/HTTPS
Traefik Reverse Proxy (Port 80/443)
  ↓ Routing Rules
Frontend Container (Next.js)
  ↓ API Calls
Backend Container (FastAPI Runtime)
  ↓ Intent Execution
Content Realm Orchestrator
  ↓ Ingestion
Public Works (GCS, Supabase)
```

### System Boundaries

1. **Browser → Traefik Proxy**
2. **Traefik → Frontend Container**
3. **Frontend → Backend (API Call)**
4. **Backend → Auth/Authorization**
5. **Backend → Runtime/ExecutionLifecycleManager**
6. **Runtime → Data Steward SDK**
7. **Data Steward → MaterializationPolicyStore**
8. **Content Realm → IngestionAbstraction**
9. **IngestionAbstraction → GCS**
10. **Content Realm → FileStorageAbstraction (Supabase)**

---

## Test 1: Upload Phase (ingest_file intent)

### Functional Test

**User Action:** User selects file and clicks "Upload"

**Expected Behavior:**
- File is uploaded
- `ingest_file` intent is submitted
- File goes to GCS
- Boundary contract is created (pending materialization)
- UI shows "File uploaded. Click 'Save' to make it available for parsing."

**Validation:**
- ✅ File appears in UI with "pending" status
- ✅ "Save" button is visible
- ✅ No errors displayed

---

### Architectural Test

**Validates:**
- ✅ Intent-based API pattern (no legacy endpoints)
- ✅ Session-First pattern (uses SessionBoundaryProvider)
- ✅ Platform State pattern (uses PlatformStateProvider)
- ✅ Two-phase pattern (upload → save)
- ✅ Policy in Civic Systems (Data Steward assigns boundary contract)

**Validation:**
- ✅ No direct API calls to `/api/v1/*` endpoints
- ✅ Intent submitted via `/api/intent/submit`
- ✅ Session state from SessionBoundaryProvider
- ✅ Execution tracked in PlatformStateProvider

---

### SRE/Distributed Systems Test

#### Boundary 1: Browser → Traefik Proxy

**What Must Be True:**
- Browser can resolve domain/IP
- Traefik is listening on port 80/443
- SSL certificate valid (if HTTPS)
- Network connectivity exists

**Common Failure Modes:**
- DNS resolution failure
- Traefik container not running
- Port not exposed
- SSL certificate expired/invalid
- Network timeout

**Logs/Signals:**
- Browser: Network error in DevTools
- Traefik: Access logs show request arrival
- Traefik: Error logs show routing failures

**Test:**
```bash
# Check Traefik is running
docker ps | grep traefik

# Check Traefik logs for request
docker logs traefik-container --tail 50 | grep "upload\|intent"

# Check browser network tab
# - Request should show 200/201 status
# - Response headers should include Traefik metadata
```

---

#### Boundary 2: Traefik → Frontend Container

**What Must Be True:**
- Traefik routing rules configured correctly
- Frontend container is running
- Frontend container is healthy
- Service discovery working

**Common Failure Modes:**
- Routing rule misconfiguration
- Frontend container crashed
- Frontend container not in Traefik network
- Health check failing

**Logs/Signals:**
- Traefik: Routing logs show target service
- Frontend: Next.js logs show request received
- Frontend: Error logs show processing failures
- Docker: Container status shows "Up"

**Test:**
```bash
# Check frontend container status
docker ps | grep frontend

# Check frontend logs
docker logs frontend-container --tail 50 | grep -i "upload\|error"

# Check Traefik routing
docker exec traefik-container cat /etc/traefik/traefik.yml | grep -A 10 "frontend"

# Check frontend health
curl -I http://localhost/api/health  # If health endpoint exists
```

---

#### Boundary 3: Frontend → Backend (API Call)

**What Must Be True:**
- Frontend can resolve backend service
- Backend API endpoint exists (`/api/intent/submit`)
- Request format matches backend expectations
- CORS configured correctly (if cross-origin)

**Common Failure Modes:**
- Backend service not found
- API endpoint doesn't exist
- Request format mismatch (missing required fields)
- CORS policy blocking request
- Network timeout

**Logs/Signals:**
- Frontend: Network tab shows API call
- Frontend: Console shows error messages
- Backend: Access logs show request arrival
- Backend: Error logs show validation failures
- Traefik: Routing logs show backend target

**Test:**
```bash
# Check backend container status
docker ps | grep backend

# Check backend logs for intent submission
docker logs backend-container --tail 100 | grep -i "intent\|submit\|upload"

# Check backend API endpoint exists
curl -X POST http://localhost/api/intent/submit \
  -H "Content-Type: application/json" \
  -d '{"intent_type":"ingest_file","tenant_id":"test","session_id":"test","parameters":{}}' \
  -v

# Check frontend network tab
# - Request URL: /api/intent/submit
# - Request method: POST
# - Request payload: JSON with intent_type, parameters
# - Response status: 200/201 (not 404, 500, CORS error)
```

---

#### Boundary 4: Backend → Auth/Authorization

**What Must Be True:**
- Session token valid
- Tenant ID valid
- User authorized for operation
- Session exists in session store

**Common Failure Modes:**
- Missing/invalid session token
- Session expired
- Tenant ID mismatch
- Authorization failure
- Session store unavailable

**Logs/Signals:**
- Backend: Auth middleware logs show validation
- Backend: Error logs show auth failures (401, 403)
- Session store: Logs show session lookup
- Backend: Access logs show authenticated requests

**Test:**
```bash
# Check backend auth logs
docker logs backend-container --tail 100 | grep -i "auth\|session\|tenant\|401\|403"

# Check session store (if Redis/DB)
# - Session exists
# - Session not expired
# - Tenant ID matches

# Check request headers in browser
# - Authorization header present
# - X-Session-Token header present (if used)
# - X-Tenant-ID header present (if used)
```

---

#### Boundary 5: Backend → Runtime/ExecutionLifecycleManager

**What Must Be True:**
- ExecutionLifecycleManager initialized
- Intent type registered
- Intent handler exists
- Execution context created

**Common Failure Modes:**
- ExecutionLifecycleManager not initialized
- Intent type not found
- Handler missing
- Context creation failure
- Runtime service unavailable

**Logs/Signals:**
- Backend: Runtime logs show intent received
- Backend: Runtime logs show execution started
- Backend: Error logs show intent registration failures
- Backend: Error logs show handler not found

**Test:**
```bash
# Check runtime logs
docker logs backend-container --tail 200 | grep -i "execution\|intent\|ingest_file"

# Check intent registration
docker logs backend-container | grep -i "intent.*registered\|supported.*intent"

# Check execution lifecycle
docker logs backend-container | grep -i "execution.*started\|execution.*completed\|execution.*failed"
```

---

#### Boundary 6: Runtime → Data Steward SDK

**What Must Be True:**
- DataStewardSDK initialized
- DataStewardSDK available in ExecutionLifecycleManager
- SDK can communicate with Data Steward Primitives

**Common Failure Modes:**
- DataStewardSDK not initialized
- SDK unavailable (None/null)
- SDK initialization failure
- Circular dependency

**Logs/Signals:**
- Backend: Runtime logs show Data Steward SDK initialization
- Backend: Runtime logs show boundary contract request
- Backend: Error logs show "Data Steward SDK required" (if missing)
- Backend: Error logs show SDK access failures

**Test:**
```bash
# Check Data Steward SDK initialization
docker logs backend-container | grep -i "data.*steward.*sdk\|data.*steward.*initialized"

# Check boundary contract creation
docker logs backend-container | grep -i "boundary.*contract\|request.*data.*access"

# Check for SDK errors
docker logs backend-container | grep -i "data.*steward.*required\|data.*steward.*unavailable"
```

---

#### Boundary 7: Data Steward → MaterializationPolicyStore

**What Must Be True:**
- MaterializationPolicyStore initialized
- Policy store has database connection (Supabase)
- Policy can be retrieved (tenant-specific or default)
- Policy decision can be made

**Common Failure Modes:**
- Policy store not initialized
- Database connection failure
- Policy not found (no default)
- Policy retrieval timeout

**Logs/Signals:**
- Backend: Data Steward logs show policy store initialization
- Backend: Data Steward logs show policy retrieval
- Backend: Error logs show database connection failures
- Backend: Error logs show policy not found

**Test:**
```bash
# Check MaterializationPolicyStore initialization
docker logs backend-container | grep -i "materialization.*policy.*store\|policy.*store.*initialized"

# Check policy retrieval
docker logs backend-container | grep -i "policy.*retrieved\|get.*policy\|default.*policy"

# Check database connection
docker logs backend-container | grep -i "supabase\|database.*connection\|policy.*store.*error"
```

---

#### Boundary 8: Content Realm → IngestionAbstraction

**What Must Be True:**
- IngestionAbstraction initialized
- GCS connection configured
- File can be uploaded to GCS
- File metadata stored

**Common Failure Modes:**
- IngestionAbstraction not initialized
- GCS credentials invalid/missing
- GCS bucket doesn't exist
- Network timeout to GCS
- File upload failure

**Logs/Signals:**
- Backend: Content Realm logs show ingestion started
- Backend: IngestionAbstraction logs show GCS upload
- Backend: Error logs show GCS connection failures
- Backend: Error logs show upload failures
- GCS: Access logs show file upload (if accessible)

**Test:**
```bash
# Check IngestionAbstraction initialization
docker logs backend-container | grep -i "ingestion.*abstraction\|gcs.*initialized"

# Check file upload to GCS
docker logs backend-container | grep -i "gcs.*upload\|file.*uploaded\|ingestion.*result"

# Check GCS errors
docker logs backend-container | grep -i "gcs.*error\|upload.*failed\|bucket.*not.*found"

# Verify file in GCS (if GCS CLI available)
# gsutil ls gs://bucket-name/path/to/file
```

---

#### Boundary 9: Content Realm → FileStorageAbstraction (Supabase)

**What Must Be True:**
- FileStorageAbstraction initialized
- Supabase connection configured
- File metadata can be stored (if needed in upload phase)
- Boundary contract stored

**Common Failure Modes:**
- FileStorageAbstraction not initialized
- Supabase credentials invalid
- Supabase connection timeout
- Database write failure

**Logs/Signals:**
- Backend: Content Realm logs show file storage operations
- Backend: Supabase logs show database operations
- Backend: Error logs show Supabase connection failures
- Backend: Error logs show database write failures

**Test:**
```bash
# Check FileStorageAbstraction initialization
docker logs backend-container | grep -i "file.*storage.*abstraction\|supabase.*initialized"

# Check Supabase operations
docker logs backend-container | grep -i "supabase\|database.*write\|boundary.*contract.*stored"

# Check Supabase errors
docker logs backend-container | grep -i "supabase.*error\|database.*error\|connection.*failed"
```

---

## Test 2: Save Phase (save_materialization intent)

### Functional Test

**User Action:** User clicks "Save" button

**Expected Behavior:**
- `save_materialization` intent is submitted
- Materialization is authorized
- File metadata registered in Supabase
- UI shows "File saved successfully! File is now available for parsing."

**Validation:**
- ✅ File status changes to "saved"
- ✅ "Save" button disappears or becomes disabled
- ✅ File is available for parsing
- ✅ No errors displayed

---

### Architectural Test

**Validates:**
- ✅ Two-phase pattern completion
- ✅ Materialization authorization
- ✅ Supabase registration

**Validation:**
- ✅ `save_materialization` intent submitted
- ✅ Boundary contract activated
- ✅ File registered in materialization index

---

### SRE/Distributed Systems Test

**Same boundaries as Test 1, plus:**

#### Boundary 10: save_materialization → Materialization Authorization

**What Must Be True:**
- Boundary contract exists
- Materialization can be authorized
- Data Steward SDK available

**Common Failure Modes:**
- Boundary contract not found
- Authorization failure
- Data Steward SDK unavailable

**Logs/Signals:**
- Backend: Runtime logs show materialization authorization
- Backend: Error logs show boundary contract not found
- Backend: Error logs show authorization failure

**Test:**
```bash
# Check materialization authorization
docker logs backend-container | grep -i "materialization.*authorized\|save.*materialization"

# Check boundary contract lookup
docker logs backend-container | grep -i "boundary.*contract.*not.*found\|boundary.*contract.*id"
```

---

#### Boundary 11: save_materialization → Supabase Registration

**What Must Be True:**
- Supabase connection available
- Materialization can be registered
- File metadata can be stored

**Common Failure Modes:**
- Supabase connection failure
- Registration failure
- Database constraint violation

**Logs/Signals:**
- Backend: Content Realm logs show materialization registration
- Backend: Supabase logs show INSERT operation
- Backend: Error logs show registration failures

**Test:**
```bash
# Check materialization registration
docker logs backend-container | grep -i "materialization.*registered\|register.*materialization"

# Check Supabase registration
docker logs backend-container | grep -i "supabase.*insert\|project_files.*insert"

# Verify in Supabase (if Supabase CLI available)
# supabase db query "SELECT * FROM project_files WHERE file_id = '...'"
```

---

## Comprehensive Test Execution Plan

### Phase 1: Pre-Test Validation

```bash
# 1. Check all containers are running
docker ps

# 2. Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# 3. Check Traefik routing
docker exec traefik-container cat /etc/traefik/traefik.yml

# 4. Check network connectivity
docker network ls
docker network inspect <network-name>

# 5. Check logs are accessible
docker logs backend-container --tail 10
docker logs frontend-container --tail 10
docker logs traefik-container --tail 10
```

---

### Phase 2: Functional Test Execution

1. **Open browser DevTools**
   - Network tab: Monitor all requests
   - Console tab: Monitor errors/warnings
   - Application tab: Check session storage

2. **Execute Upload Flow**
   - Select file
   - Click "Upload"
   - Verify UI state
   - Click "Save"
   - Verify UI state

3. **Capture Evidence**
   - Screenshots of UI states
   - Network request/response logs
   - Console errors/warnings
   - Browser session storage

---

### Phase 3: Architectural Validation

1. **Check Intent-Based API Usage**
   ```bash
   # Verify no legacy endpoint calls
   docker logs frontend-container | grep -i "/api/v1/"
   
   # Verify intent submissions
   docker logs backend-container | grep -i "intent.*submit\|/api/intent/submit"
   ```

2. **Check Session-First Pattern**
   ```bash
   # Verify session state usage
   docker logs frontend-container | grep -i "session.*boundary\|session.*state"
   ```

3. **Check Two-Phase Pattern**
   ```bash
   # Verify ingest_file intent
   docker logs backend-container | grep -i "ingest_file"
   
   # Verify save_materialization intent
   docker logs backend-container | grep -i "save_materialization"
   ```

---

### Phase 4: SRE Boundary Validation

For each boundary (1-11), execute:

1. **Check Preconditions**
   - Service is running
   - Service is healthy
   - Configuration is correct

2. **Monitor Logs During Test**
   - Capture logs for each boundary
   - Identify any errors/warnings
   - Verify successful operations

3. **Verify Post-Conditions**
   - File in GCS (if applicable)
   - Metadata in Supabase (if applicable)
   - Execution state in Runtime

---

## Success Criteria

### Functional
- ✅ File uploads successfully
- ✅ File can be saved
- ✅ UI reflects correct state
- ✅ No user-facing errors

### Architectural
- ✅ Uses intent-based API
- ✅ Follows Session-First pattern
- ✅ Follows two-phase pattern
- ✅ Policy in Civic Systems

### SRE/Distributed Systems
- ✅ All boundaries crossed successfully
- ✅ No errors in any boundary
- ✅ Logs confirm successful operations
- ✅ System is observable

---

## Failure Investigation Checklist

If any test fails:

1. **Identify Failed Boundary**
   - Check logs for first error
   - Trace request path
   - Identify boundary where failure occurred

2. **Check Preconditions**
   - Service running?
   - Service healthy?
   - Configuration correct?

3. **Check Common Failure Modes**
   - Review failure modes for that boundary
   - Check logs for specific errors
   - Verify network connectivity

4. **Check Logs**
   - All containers: Recent errors
   - Specific boundary: Operation logs
   - Network: Connection logs

5. **Verify Fix**
   - Fix identified issue
   - Re-run test
   - Verify all boundaries pass

---

## Test Execution Script

```bash
#!/bin/bash
# upload_flow_test.sh

echo "=== Upload Flow Comprehensive Test ==="
echo ""

echo "Phase 1: Pre-Test Validation"
echo "Checking containers..."
docker ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "Phase 2: Functional Test"
echo "Please execute upload flow in browser..."
echo "Press Enter when complete..."
read

echo ""
echo "Phase 3: Architectural Validation"
echo "Checking intent-based API usage..."
docker logs backend-container --tail 200 | grep -i "intent.*submit" | tail -5

echo ""
echo "Phase 4: SRE Boundary Validation"
echo "Checking boundary logs..."
echo "Boundary 1-2: Traefik/Frontend"
docker logs traefik-container --tail 20 | grep -i "upload\|intent"
docker logs frontend-container --tail 20 | grep -i "upload\|intent"

echo "Boundary 3-5: Backend/Auth/Runtime"
docker logs backend-container --tail 50 | grep -i "intent\|auth\|execution"

echo "Boundary 6-7: Data Steward/Policy"
docker logs backend-container --tail 50 | grep -i "data.*steward\|policy"

echo "Boundary 8-9: Ingestion/Storage"
docker logs backend-container --tail 50 | grep -i "ingestion\|gcs\|supabase"

echo ""
echo "Test complete. Review logs above for any errors."
```

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **READY FOR EXECUTION**
