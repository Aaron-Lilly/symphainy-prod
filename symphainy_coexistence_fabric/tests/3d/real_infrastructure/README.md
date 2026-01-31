# Real Infrastructure Tests - SRE + Functional + Architectural

**Purpose:** Test against REAL infrastructure to catch actual demo failures.

---

## 🎯 What These Tests Catch

### Demo Failure Points
- ✅ **Browser not available** - Tests API accessibility
- ✅ **Can't login** - Tests real authentication flow
- ✅ **File upload fails silently** - Tests real file operations and persistence
- ✅ **Parsing returns gibberish** - Tests parsing quality
- ✅ **Chat agents just echo** - Tests LLM integration and response quality
- ✅ **Navigation doesn't work** - Tests real navigation and state persistence

---

## 🏗️ Test Structure

### SRE Tests (Infrastructure)
- `test_real_infrastructure_connectivity.py`
  - Real Redis connectivity and operations
  - Real ArangoDB connectivity and operations
  - Real PublicWorks integration

### Functional Tests (Demo Paths)
- `test_demo_critical_paths.py`
  - Real authentication flow
  - Real file upload and persistence
  - Real file parsing quality
  - Real chat agent responses
  - Real navigation and state persistence
  - Real API accessibility

### LLM Tests (If Used)
- `test_real_llm_integration.py`
  - LLM API key validation
  - Real LLM calls
  - GuideAgent LLM integration

---

## 🚀 How to Run

### Prerequisites
1. **Services Running:**
   ```bash
   cd tests/infrastructure
   docker-compose -f docker-compose.3d-test.yml up -d redis arangodb consul meilisearch
   ```
   (Meilisearch is containerized in the 3d-test compose; no cloud required.)

2. **Environment Variables:**
   ```bash
   export REDIS_URL=redis://localhost:6379
   export ARANGO_URL=http://localhost:8529
   export ARANGO_ROOT_PASSWORD=test_password
   ```

3. **LLM API Keys (Optional):**
   ```bash
   # In .env.secrets
   LLM_OPENAI_API_KEY=sk-...
   # OR
   LLM_ANTHROPIC_API_KEY=sk-ant-...
   ```

### Run Tests
```bash
# All real infrastructure tests
pytest tests/3d/real_infrastructure/ -v -m real_infrastructure

# Just SRE tests
pytest tests/3d/real_infrastructure/ -v -m sre

# Just functional tests
pytest tests/3d/real_infrastructure/ -v -m functional

# Just critical demo paths
pytest tests/3d/real_infrastructure/ -v -m critical

# Just LLM tests
pytest tests/3d/real_infrastructure/ -v -m llm
```

---

## 📋 Test Markers

- `@pytest.mark.real_infrastructure` - All real infrastructure tests
- `@pytest.mark.sre` - SRE/infrastructure tests
- `@pytest.mark.functional` - Functional/demo path tests
- `@pytest.mark.critical` - Critical demo paths
- `@pytest.mark.llm` - LLM integration tests

---

## ⚠️ Important Notes

1. **These tests use REAL services** - Make sure services are running
2. **These tests may have costs** - LLM tests make real API calls
3. **These tests may be slow** - Real infrastructure operations take time
4. **These tests may fail if services are down** - That's the point!

---

## 🎯 What Gets Tested

### Infrastructure
- ✅ Real Redis connectivity and operations
- ✅ Real ArangoDB connectivity and operations
- ✅ Real PublicWorks integration

### Demo Paths
- ✅ Real user registration and login
- ✅ Real file upload and retrieval
- ✅ Real file parsing quality
- ✅ Real chat agent responses
- ✅ Real navigation and state persistence
- ✅ Real API accessibility

### LLM (If Configured)
- ✅ Real LLM API calls
- ✅ GuideAgent LLM integration
- ✅ Response quality validation

---

**Status:** These tests validate REAL infrastructure and catch actual demo failures.
