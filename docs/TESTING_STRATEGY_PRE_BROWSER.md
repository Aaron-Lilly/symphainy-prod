# Pre-Browser Testing Strategy

**Date:** January 2026  
**Status:** 🟢 **ACTIVE**  
**Purpose:** Systematic platform testing before browser testing to avoid symptom-chasing

---

## Executive Summary

This document outlines a **layered, systematic testing approach** that validates the platform from infrastructure to security before moving to browser testing. The strategy uses **real infrastructure** (per platform principle) and follows a **bottom-up approach** to identify root causes rather than symptoms.

### Key Principle

> **Test the platform systematically, layer by layer, using real infrastructure.**
> 
> This ensures we catch issues at their source rather than chasing symptoms in the browser.

---

## Platform Understanding

### Architecture Overview

**4-Layer Platform:**
- **Runtime Plane** (Port 8000): Execution core, WAL, Saga, state management
- **Smart City Plane**: Policy/governance, materialization rules, access control
- **Realm Plane** (Port 8002): Domain-specific logic (Content, Insights, Journey, Outcomes)
- **Experience Plane** (Port 8001): REST APIs, WebSocket, intent submission

**Infrastructure Services:**
- Redis: Hot state (sessions, cache)
- ArangoDB: Durable state (execution state, graph data)
- Supabase: Metadata, lineage, artifacts
- GCS: File storage
- Consul: Service discovery
- Meilisearch: Semantic search

**Frontend:**
- Next.js/React/TypeScript
- AuthProvider context for authentication
- WebSocket connections for real-time updates

### Current State

- **Test Pass Rate:** 85% (22/26 tests)
- **Known Issues:**
  - EmbeddingService placeholder (critical)
  - Journey Realm Artifact Plane gaps
  - AuthProvider context errors (browser symptom)
  - Some error handling too permissive

---

## Testing Strategy: 7 Layers

### Layer 1: Infrastructure Health & Connectivity (Foundation)

**Purpose:** Verify all services start correctly and can communicate

**What We Test:**
1. **Service Startup Sequence**
   - Infrastructure services (Redis, ArangoDB, Consul, Meilisearch) become healthy
   - Runtime service starts and registers all realms
   - Experience service connects to Runtime successfully
   - Frontend build succeeds (if applicable)

2. **Health Check Validation**
   - All `/health` endpoints return correct status
   - Service dependencies are satisfied
   - Database connections established
   - Service discovery working

3. **Network Connectivity**
   - Runtime ↔ Experience communication
   - Experience ↔ Frontend (CORS, API endpoints)
   - Service-to-service authentication
   - WebSocket connections can be established

**Test Files:**
- `tests/smoke/test_service_startup.py`
- `tests/integration/infrastructure/test_docker_compose_test.py`
- `tests/integration/infrastructure/test_state_abstraction.py`

**Success Criteria:**
- ✅ All services healthy
- ✅ All health checks pass
- ✅ Services can communicate
- ✅ No startup errors in logs

---

### Layer 2: API Contract Validation (Contracts)

**Purpose:** Verify API contracts match expectations

**What We Test:**
1. **Runtime API Contracts**
   - Session creation (`POST /api/session/create`)
   - Intent submission (`POST /api/intent/submit`)
   - Execution status (`GET /api/execution/{id}/status`)
   - Artifact retrieval (`GET /api/artifacts/{id}`)
   - Realm listing (`GET /api/realms`)

2. **Experience API Contracts**
   - Authentication endpoints (`POST /api/auth/*`)
   - WebSocket connections (`WS /api/ws`)
   - Intent submission via Experience (`POST /api/intents/*`)
   - Admin dashboard APIs (`GET /api/admin/*`)

3. **Request/Response Validation**
   - Required fields present
   - Data types correct
   - Error responses follow contract
   - Status codes appropriate

**Test Files:**
- `tests/integration/test_basic_integration.py`
- `tests/integration/experience/test_admin_dashboard.py`
- `tests/integration/test_auth_and_websocket_inline.py`

**Success Criteria:**
- ✅ All endpoints return expected contracts
- ✅ Request validation works
- ✅ Error responses are consistent
- ✅ Status codes are correct

---

### Layer 3: Integration Flow Tests (Flows)

**Purpose:** Verify end-to-end flows work correctly

**What We Test:**
1. **Intent Execution Flows**
   - Experience → Runtime → Realm → Response
   - Session creation → Intent submission → Execution completion
   - Multi-step saga execution
   - WebSocket state streaming

2. **Realm-Specific Flows**
   - **Content Realm:** File upload → Parse → Extract embeddings → Store
   - **Insights Realm:** Data quality → Semantic interpretation → Analysis
   - **Journey Realm:** Blueprint creation → SOP generation → Workflow creation
   - **Outcomes Realm:** Solution synthesis → Roadmap generation → POC creation

3. **Cross-Realm Flows**
   - Content → Insights → Journey → Outcomes
   - Artifact retrieval across realms
   - State persistence across sessions
   - Lineage tracking across realms

**Test Files:**
- `tests/integration/realms/test_content_realm.py`
- `tests/integration/realms/test_insights_realm.py`
- `tests/integration/realms/test_journey_realm.py`
- `tests/integration/realms/test_outcomes_realm.py`
- `tests/integration/test_architecture_integration.py`

**Success Criteria:**
- ✅ At least one successful flow per realm
- ✅ Cross-realm flows complete
- ✅ Artifacts created and retrievable
- ✅ State persists correctly

---

### Layer 4: Data Integrity & Persistence (Data)

**Purpose:** Verify data is stored and retrieved correctly

**What We Test:**
1. **State Persistence**
   - Session state persists across requests
   - Execution state in State Surface
   - WAL entries written correctly
   - Transactional outbox working

2. **Artifact Storage**
   - Artifacts stored in Artifact Plane
   - File artifacts in GCS
   - Metadata in Supabase
   - Graph relationships in ArangoDB

3. **Data Consistency**
   - Boundary contracts match materialization
   - Lineage tracking accurate
   - TTL enforcement working
   - No orphaned records

**Test Files:**
- `tests/integration/infrastructure/test_state_abstraction.py`
- `tests/integration/infrastructure/test_arango_adapter.py`
- `tests/integration/test_artifact_storage_smoke.py`
- `tests/integration/runtime/test_wal.py`
- `tests/integration/infrastructure/test_transactional_outbox.py`

**Success Criteria:**
- ✅ All data persists correctly
- ✅ Artifacts retrievable after creation
- ✅ Lineage tracking accurate
- ✅ No data corruption

---

### Layer 5: Error Handling & Edge Cases (Resilience)

**Purpose:** Verify graceful failure handling

**What We Test:**
1. **Error Scenarios**
   - Invalid intent parameters
   - Missing dependencies
   - Service failures
   - Network timeouts
   - Database connection failures

2. **Edge Cases**
   - Empty payloads
   - Very large files
   - Concurrent requests
   - Resource exhaustion
   - Invalid session IDs

3. **Recovery**
   - Failed executions can be retried
   - Partial failures don't corrupt state
   - Error messages are actionable
   - Logs provide debugging info

**Test Files:**
- `tests/integration/test_error_handling_edge_cases.py`
- `tests/integration/test_websocket_robustness.py`
- `tests/integration/test_complex_parsing_flows.py`

**Success Criteria:**
- ✅ Errors handled gracefully
- ✅ No crashes on invalid input
- ✅ Error messages are helpful
- ✅ System recovers from failures

---

### Layer 6: Performance & Pressure Tests (Performance)

**Purpose:** Verify system behavior under load

**What We Test:**
1. **Load Testing**
   - Concurrent sessions (10+)
   - Multiple intent submissions
   - WebSocket connection limits
   - Database query performance
   - File upload throughput

2. **Stress Testing**
   - High message volume
   - Large file processing
   - Memory usage under load
   - Connection pool exhaustion
   - Long-running executions

3. **Resource Limits**
   - Rate limiting works
   - Timeout handling
   - Graceful degradation
   - Resource cleanup

**Test Files:**
- `tests/integration/test_performance_load.py`
- `tests/integration/test_complex_parsing_flows.py`

**Success Criteria:**
- ✅ System handles 10+ concurrent sessions
- ✅ No memory leaks
- ✅ Response times acceptable
- ✅ Graceful degradation under load

---

### Layer 7: Authentication & Authorization (Security)

**Purpose:** Verify security boundaries

**What We Test:**
1. **Authentication**
   - AuthProvider context works
   - JWT validation
   - Session management
   - Token refresh
   - Logout functionality

2. **Authorization**
   - Tenant isolation
   - User permissions
   - Resource access control
   - Policy enforcement
   - Multi-tenant data separation

**Test Files:**
- `tests/integration/test_auth_security_comprehensive.py`
- `tests/integration/test_auth_and_websocket_inline.py`
- `tests/integration/smart_city/test_security_guard_e2e.py`

**Success Criteria:**
- ✅ Authentication works
- ✅ Tenant isolation verified
- ✅ Unauthorized access blocked
- ✅ Policies enforced

---

## Test Execution Order

Execute tests in this order to surface issues systematically:

### Phase 1: Foundation (30 min)
```bash
# 1. Start all services
./scripts/startup.sh

# 2. Verify infrastructure health
pytest tests/smoke/test_service_startup.py -v
pytest tests/integration/infrastructure/ -v -m infrastructure

# 3. Basic connectivity
pytest tests/integration/test_basic_integration.py -v
```

### Phase 2: Core Flows (45 min)
```bash
# 4. API contracts
pytest tests/integration/test_basic_integration.py -v
pytest tests/integration/experience/ -v

# 5. Realm flows
pytest tests/integration/realms/ -v

# 6. Cross-realm flows
pytest tests/integration/test_architecture_integration.py -v
```

### Phase 3: Data & Resilience (30 min)
```bash
# 7. Data integrity
pytest tests/integration/infrastructure/test_state_abstraction.py -v
pytest tests/integration/test_artifact_storage_smoke.py -v
pytest tests/integration/runtime/test_wal.py -v

# 8. Error handling
pytest tests/integration/test_error_handling_edge_cases.py -v
```

### Phase 4: Performance (20 min)
```bash
# 9. Performance
pytest tests/integration/test_performance_load.py -v
```

### Phase 5: Security (15 min)
```bash
# 10. Security
pytest tests/integration/test_auth_security_comprehensive.py -v
```

**Total Estimated Time:** ~2.5 hours

---

## Success Criteria Before Browser Testing

All of the following must pass:

1. ✅ **Infrastructure Health:** All services healthy, all health checks pass
2. ✅ **API Contracts:** All endpoints return expected contracts
3. ✅ **Core Flows:** At least one successful flow per realm
4. ✅ **Data Integrity:** Artifacts persist and can be retrieved
5. ✅ **Error Handling:** Graceful failures, no crashes
6. ✅ **Performance:** System handles 10+ concurrent sessions
7. ✅ **Security:** Authentication works, tenant isolation verified

---

## Issue Tracking Approach

For each failing test, document:

1. **Test Name and Location**
2. **Expected Behavior**
3. **Actual Behavior**
4. **Error Message/Logs**
5. **Impact Assessment** (Critical/High/Medium/Low)
6. **Root Cause Hypothesis**
7. **Fix Priority**

### Test Results Template

Create `docs/TEST_EXECUTION_RESULTS.md` with:

```markdown
# Test Execution Results

**Date:** [Date]
**Phase:** [Phase Number]
**Status:** [Pass/Fail/Partial]

## Results Summary
- Total Tests: X
- Passed: Y
- Failed: Z
- Skipped: W

## Failures

### Test: [Test Name]
- **Location:** `tests/path/to/test.py::test_name`
- **Expected:** [Expected behavior]
- **Actual:** [Actual behavior]
- **Error:** [Error message]
- **Impact:** [Critical/High/Medium/Low]
- **Root Cause:** [Hypothesis]
- **Priority:** [1-5]
```

---

## Running the Full Test Suite

Use the execution script:

```bash
# Run all phases
./scripts/run_pre_browser_tests.sh

# Run specific phase
./scripts/run_pre_browser_tests.sh --phase 1

# Run with detailed output
./scripts/run_pre_browser_tests.sh --verbose
```

---

## Next Steps After Testing

Once all layers pass:

1. **Document any issues found** in `docs/TEST_EXECUTION_RESULTS.md`
2. **Prioritize fixes** based on impact
3. **Fix critical issues** before browser testing
4. **Re-run failed tests** to verify fixes
5. **Proceed to browser testing** with confidence

---

## Questions & Answers

**Q: What if a test fails?**  
A: Document it in the test results, assess impact, and decide whether to fix before proceeding or continue testing to find all issues.

**Q: Can we skip some layers?**  
A: Not recommended. Each layer builds on the previous one. Skipping layers may hide issues that surface later.

**Q: How long does this take?**  
A: ~2.5 hours for full suite. Can be run in phases over multiple sessions.

**Q: What if services don't start?**  
A: Fix infrastructure issues first. Use `./scripts/startup.sh` and check logs.

---

**Last Updated:** January 2026  
**Status:** Active
