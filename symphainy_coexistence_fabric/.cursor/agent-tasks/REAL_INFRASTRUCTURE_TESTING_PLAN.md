# Real Infrastructure Testing Plan

**Date:** January 28, 2026  
**Status:** Ready for implementation

---

## 🎯 Goal

Create tests that validate against **REAL infrastructure** (not mocks) to catch actual demo failures. This addresses the concern that current tests are "superficial" and don't catch real integration issues.

---

## 🔍 What We Found

### Existing Pattern (from symphainy_source)
- ✅ Real Redis tests (`test_redis_adapter_real.py`)
- ✅ Real ArangoDB tests (`test_arangodb_adapter_real.py`)
- ✅ Real LLM tests (`test_agent_conversation_real.py`)
- ✅ Real API endpoint tests (`test_api_endpoints_reality.py`)

**Pattern:**
- Use environment variables for service URLs
- Load `.env.secrets` for API keys
- Connect to actual services (not mocks)
- Test actual operations (set/get, create/read, etc.)
- Mark with `@pytest.mark.real_infrastructure` or `@pytest.mark.integration`

---

## 🚨 Demo Failure Points to Test

### 1. Browser Not Available ✅
**Test:** `test_runtime_api_accessible`, `test_experience_api_accessible`
- Tests that Runtime/Experience APIs are accessible
- Catches: Connection errors, service not running

### 2. Can't Login ✅
**Test:** `test_real_user_login`
- Tests real authentication flow
- Tests real session creation
- Tests real state persistence
- Catches: Auth failures, session not saved, state lost

### 3. File Upload Fails Silently ✅
**Test:** `test_real_file_upload`, `test_real_file_upload_persistence`
- Tests real file upload
- Tests file is actually saved
- Tests file can be retrieved
- Catches: Silent failures, persistence issues

### 4. Parsing Returns Gibberish ✅
**Test:** `test_real_parsing_quality`
- Tests parsing returns meaningful content
- Validates content quality
- Catches: Parsing errors, gibberish output

### 5. Chat Agents Just Echo ✅
**Test:** `test_guide_agent_quality`, `test_guide_agent_uses_real_llm`
- Tests agents generate real responses
- Tests LLM integration works
- Tests response quality
- Catches: Echo issues, LLM failures, poor responses

### 6. Navigation Doesn't Work ✅
**Test:** `test_real_navigation`, `test_real_navigation_persistence`
- Tests navigation actually routes
- Tests state persists
- Catches: Navigation failures, state loss

---

## 📋 Test Suite Structure

### SRE Tests (Infrastructure)
**File:** `test_real_infrastructure_connectivity.py`
- Real Redis connectivity
- Real ArangoDB connectivity
- Real PublicWorks integration

### Functional Tests (Demo Paths)
**File:** `test_demo_critical_paths.py`
- Real authentication flow
- Real file upload and persistence
- Real file parsing quality
- Real chat agent responses
- Real navigation and state persistence
- Real API accessibility

### LLM Tests (If Used)
**File:** `test_real_llm_integration.py`
- LLM API key validation
- Real LLM calls
- GuideAgent LLM integration

---

## 🛠️ Implementation

### Fixtures (conftest.py)
- `real_redis_client` - Real Redis connection
- `real_arangodb_client` - Real ArangoDB connection
- `real_public_works` - Real PublicWorks with actual adapters
- `real_state_surface` - Real StateSurface with real persistence
- `real_solutions` - Real solutions with real infrastructure
- `real_execution_context` - Real execution context

### Test Markers
- `@pytest.mark.real_infrastructure` - All real infrastructure tests
- `@pytest.mark.sre` - SRE/infrastructure tests
- `@pytest.mark.functional` - Functional/demo path tests
- `@pytest.mark.critical` - Critical demo paths
- `@pytest.mark.llm` - LLM integration tests

---

## 🚀 How to Run

### Prerequisites
```bash
# Start services
cd tests/infrastructure
docker-compose -f docker-compose.3d-test.yml up -d redis arangodb consul

# Set environment variables
export REDIS_URL=redis://localhost:6379
export ARANGO_URL=http://localhost:8529
export ARANGO_ROOT_PASSWORD=test_password

# Optional: LLM API keys in .env.secrets
# LLM_OPENAI_API_KEY=sk-...
```

### Run Tests
```bash
# All real infrastructure tests
pytest tests/3d/real_infrastructure/ -v -m real_infrastructure

# Just critical demo paths
pytest tests/3d/real_infrastructure/ -v -m critical

# Just SRE tests
pytest tests/3d/real_infrastructure/ -v -m sre
```

---

## ✅ What This Tests

### Infrastructure (SRE)
- ✅ Real Redis connectivity and operations
- ✅ Real ArangoDB connectivity and operations
- ✅ Real PublicWorks integration

### Demo Paths (Functional)
- ✅ Real authentication (catches login failures)
- ✅ Real file upload (catches silent failures)
- ✅ Real file parsing (catches gibberish)
- ✅ Real chat agents (catches echo issues)
- ✅ Real navigation (catches routing failures)
- ✅ Real API accessibility (catches browser issues)

### LLM (If Configured)
- ✅ Real LLM API calls
- ✅ GuideAgent LLM integration
- ✅ Response quality

---

## 🎯 Expected Outcomes

### What These Tests Catch
- ✅ **Service connection failures** - Redis/ArangoDB not available
- ✅ **Authentication failures** - Can't login
- ✅ **Silent file upload failures** - Files not saved
- ✅ **Parsing quality issues** - Gibberish output
- ✅ **LLM integration failures** - Agents echo or fail
- ✅ **Navigation failures** - Routing doesn't work
- ✅ **State persistence issues** - Data not saved
- ✅ **API accessibility issues** - Services not reachable

### Confidence Level
- **Before:** 🟡 MEDIUM (mocked tests)
- **After:** 🟢 HIGH (real infrastructure tests)

---

## 📝 Next Steps

1. ✅ Create test structure
2. ⏳ Add to CI/CD (Phase 4 or new Phase 5)
3. ⏳ Run tests locally to validate
4. ⏳ Document findings
5. ⏳ Fix any issues found

---

**Status:** Real infrastructure test suite created. Ready to run against actual services.
