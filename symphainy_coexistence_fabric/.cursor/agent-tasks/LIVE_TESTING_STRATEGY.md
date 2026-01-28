# Live Production Testing Strategy

**Date:** January 28, 2026  
**Status:** Ready for implementation - defines when and how to test with live containers

---

## 🎯 Overview

This document defines when and how to perform "live production" testing with actual platform containers running. This is different from unit tests (mocks) and integration tests (partial services).

---

## 📊 Testing Phases

### Phase 1: Unit Tests (No Services) ✅ **CURRENT**

**What:** Tests that don't require any running services  
**Status:** ✅ Running in CI/CD  
**Location:** `tests/3d/startup/`, `tests/3d/solution/`, `tests/3d/mcp/`, `tests/3d/artifacts/`

**Services Required:** None  
**Infrastructure:** None  
**CI/CD Job:** `unit-tests`

**Examples:**
- Solution initialization tests
- Solution structure tests
- MCP server initialization tests
- Artifact creation tests

**When to Run:** Always - on every commit/PR

---

### Phase 2: Journey Tests (Mocked Services) ✅ **CURRENT**

**What:** Tests that use mocks for external dependencies  
**Status:** ✅ Running in CI/CD  
**Location:** `tests/3d/journey/`, `tests/3d/intent/`

**Services Required:** None (mocked)  
**Infrastructure:** None  
**CI/CD Job:** `journey-tests`

**Examples:**
- Journey execution tests (with mocked services)
- Intent service tests (with mocked dependencies)
- SOA API tests

**When to Run:** Always - on every commit/PR

---

### Phase 3: E2E Tests (Minimal Services) ⚠️ **PARTIAL**

**What:** Tests that require basic services (Redis, etc.)  
**Status:** ⚠️ Partially implemented  
**Location:** `tests/e2e/demo_paths/`

**Services Required:**
- ✅ Redis (in CI/CD)
- ❌ ArangoDB (not in CI/CD yet)
- ❌ Consul (not in CI/CD yet)

**Infrastructure:** GitHub Actions services  
**CI/CD Job:** `e2e-tests`

**Examples:**
- Demo path tests
- Cross-solution integration tests
- Real artifact persistence tests

**When to Run:** On PRs, before merge

**Current Status:**
- ✅ Redis service available in CI/CD
- ❌ Full docker-compose not used in CI/CD
- ❌ Runtime/Experience services not in CI/CD

---

### Phase 4: Full Integration Tests (All Services) ❌ **NOT YET**

**What:** Tests that require all platform services running  
**Status:** ❌ Not in CI/CD yet  
**Location:** `tests/e2e/full_integration/` (to be created)

**Services Required:**
- ✅ Redis
- ✅ ArangoDB
- ✅ Consul
- ✅ Runtime Service
- ✅ Experience Service

**Infrastructure:** Full docker-compose (`tests/infrastructure/docker-compose.3d-test.yml`)  
**CI/CD Job:** `full-integration-tests` (to be created)

**Examples:**
- Full platform startup tests
- Real API endpoint tests
- Real database interaction tests
- Real service discovery tests
- Performance tests
- Load tests

**When to Run:** 
- On main branch (after merge)
- Before releases
- Manual trigger for deep validation

**Docker Compose File:** `tests/infrastructure/docker-compose.3d-test.yml`

---

### Phase 5: Production-Like Tests (Full Stack) ❌ **FUTURE**

**What:** Tests that simulate production environment  
**Status:** ❌ Future enhancement  
**Location:** `tests/e2e/production_like/` (to be created)

**Services Required:**
- All services from Phase 4
- Plus: Load balancers, monitoring, logging
- Plus: Real LLM API keys (from secrets)

**Infrastructure:** Full production-like stack  
**CI/CD Job:** `production-like-tests` (future)

**Examples:**
- Real LLM API calls
- Real external system integrations
- Real authentication flows
- Real session management
- Real data persistence
- Real error recovery

**When to Run:**
- Before major releases
- Weekly scheduled runs
- Manual trigger for critical validation

---

## 🚀 When to Start Live Testing

### Current State (Now)

**What's Running:**
- ✅ Phase 1: Unit tests (no services)
- ✅ Phase 2: Journey tests (mocked services)
- ⚠️ Phase 3: E2E tests (Redis only)

**What's NOT Running:**
- ❌ Phase 4: Full integration (all services)
- ❌ Phase 5: Production-like (full stack)

**Recommendation:** 
- ✅ **Continue with current phases** (1-3)
- ⏳ **Start Phase 4 when:** Unit + Journey tests are >90% passing
- ⏳ **Start Phase 5 when:** Phase 4 tests are >80% passing

---

### Phase 4 Readiness Criteria

**Start Phase 4 (Full Integration) when:**

1. ✅ **Unit tests:** >90% passing
2. ✅ **Journey tests:** >85% passing  
3. ✅ **E2E tests (Redis):** >80% passing
4. ✅ **All critical bugs fixed** (like solution registration)
5. ✅ **Docker compose file validated** locally
6. ✅ **Service health checks working**

**Current Status:**
- Unit tests: ~85% passing ✅ (close)
- Journey tests: ~77% passing ⚠️ (need parameter fixes)
- E2E tests: Unknown (need to check)
- Critical bugs: 1 fixed (solution registration) ✅
- Docker compose: Exists but not validated ⚠️
- Health checks: Defined but not tested ⚠️

**Recommendation:** 
- **Wait until:** Journey tests >85% passing (after web agents fix parameters)
- **Then:** Validate docker-compose locally
- **Then:** Add Phase 4 to CI/CD

---

### Phase 5 Readiness Criteria

**Start Phase 5 (Production-Like) when:**

1. ✅ **Phase 4 tests:** >80% passing
2. ✅ **All services healthy** in Phase 4
3. ✅ **Performance acceptable** (< 2s response times)
4. ✅ **Error handling validated**
5. ✅ **Secrets management configured**
6. ✅ **LLM API keys available** (for real LLM tests)

**Current Status:**
- Phase 4 not started yet ❌
- All other criteria: N/A

**Recommendation:**
- **Wait until:** Phase 4 is stable and passing
- **Then:** Configure secrets management
- **Then:** Add Phase 5 as scheduled/manual job

---

## 🛠️ Implementation Plan

### Step 1: Validate Docker Compose Locally (Now)

**Action:** Test `docker-compose.3d-test.yml` locally

```bash
cd tests/infrastructure
docker-compose -f docker-compose.3d-test.yml up -d
python wait_for_services.py
# Run some tests
docker-compose -f docker-compose.3d-test.yml down
```

**Goal:** Ensure all services start correctly and health checks work

**Timeline:** Do this while web agents fix parameters

---

### Step 2: Add Phase 4 to CI/CD (After Parameter Fixes)

**Action:** Create `full-integration-tests` job in `.github/workflows/3d-tests.yml`

**Requirements:**
- Use docker-compose to spin up all services
- Wait for health checks
- Run integration tests
- Clean up services

**Timeline:** After journey tests >85% passing

---

### Step 3: Create Full Integration Tests (After Phase 4 Setup)

**Action:** Create `tests/e2e/full_integration/` directory

**Test Types:**
- Platform startup tests
- Real API endpoint tests
- Real database tests
- Service discovery tests

**Timeline:** After Phase 4 CI/CD job is working

---

### Step 4: Add Phase 5 (Future)

**Action:** Create production-like test environment

**Requirements:**
- Full stack setup
- Secrets management
- LLM API keys
- Monitoring/logging

**Timeline:** After Phase 4 is stable

---

## 📋 Test Execution Matrix

| Phase | Services | Infrastructure | CI/CD | Manual | When |
|-------|----------|----------------|-------|--------|------|
| **Phase 1** | None | None | ✅ Yes | ✅ Yes | Always |
| **Phase 2** | Mocked | None | ✅ Yes | ✅ Yes | Always |
| **Phase 3** | Redis | GitHub Actions | ✅ Yes | ✅ Yes | On PR |
| **Phase 4** | All Services | Docker Compose | ⏳ Soon | ✅ Yes | After merge |
| **Phase 5** | Full Stack | Production-like | ⏳ Future | ✅ Yes | Before release |

---

## 🎯 Recommendations

### Immediate (Now)

1. ✅ **Continue with Phases 1-3** (current state)
2. ✅ **Let web agents fix parameters** (get to >85% passing)
3. ⏳ **Validate docker-compose locally** (while waiting)

### Short Term (This Week)

4. ⏳ **Add Phase 4 to CI/CD** (after parameters fixed)
5. ⏳ **Create full integration tests** (after Phase 4 working)
6. ⏳ **Run Phase 4 on main branch** (validate full stack)

### Medium Term (Next Week)

7. ⏳ **Add Phase 5 setup** (production-like environment)
8. ⏳ **Configure secrets management** (for LLM API keys)
9. ⏳ **Add Phase 5 tests** (real LLM calls, etc.)

---

## 📊 Current Status Summary

**What's Working:**
- ✅ Unit tests (no services)
- ✅ Journey tests (mocked services)
- ⚠️ E2E tests (Redis only)

**What's Next:**
- ⏳ Full integration tests (all services) - **Start when journey tests >85%**
- ⏳ Production-like tests (full stack) - **Start when Phase 4 stable**

**Timeline:**
- **This Week:** Fix parameters, validate docker-compose
- **Next Week:** Add Phase 4 to CI/CD
- **Week After:** Add Phase 5 setup

---

**Status:** Ready to start Phase 4 after parameter fixes complete.
