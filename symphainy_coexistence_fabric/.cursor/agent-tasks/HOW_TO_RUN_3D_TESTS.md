# How to Run 3D Tests

## 📋 Overview

The 3D test suite is organized into **3 phases** that run progressively:

1. **Phase 1: Unit Tests** - No services needed (mocked infrastructure)
2. **Phase 2: Journey Tests** - Light integration (may need some services)
3. **Phase 3: E2E Tests** - Full services required (Docker Compose)

---

## 🏗️ Test Structure

```
tests/
├── 3d/                          # 3D test suite
│   ├── conftest.py              # Shared fixtures (mocks, solutions)
│   ├── startup/                 # Phase 1: Solution initialization tests
│   ├── solution/                # Phase 1: Solution-level tests
│   ├── mcp/                     # Phase 1: MCP server tests
│   ├── agents/                  # Phase 1: Agent tests
│   ├── artifacts/               # Phase 1: Artifact tests
│   ├── security/                # Phase 1: Security unit tests
│   ├── intent/                  # Phase 2: Intent service tests
│   ├── journey/                 # Phase 2: Journey orchestration tests
│   └── ...
├── e2e/                         # Phase 3: End-to-end demo paths
│   └── demo_paths/              # Full user journey tests
└── infrastructure/              # Test infrastructure
    ├── docker-compose.3d-test.yml  # Services for E2E tests
    └── wait_for_services.py     # Health check script
```

---

## 🚀 Running Tests Locally

### Prerequisites

1. **Tests are already in your project** - They're on GitHub main branch
2. **You need `.env.secrets`** - For LLM API keys (OpenAI, etc.)
3. **Python 3.11+** with pytest installed
4. **Docker & Docker Compose** (for Phase 3 E2E tests only)

### Step 1: Pull Test Files from GitHub

The test files are on GitHub but may not be in your local working directory. Check if they exist:

```bash
cd /home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric
ls tests/3d/
```

If they don't exist, they're in git but not checked out. The tests are **already committed** to main branch, so you just need to ensure your working directory has them.

### Step 2: Install Test Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

**For Unit Tests (Phase 1):**
- Unit tests use **mocked infrastructure** (see `conftest.py`)
- They don't need real services or API keys
- You can run these without `.env.secrets`

**For Journey/Intent Tests (Phase 2):**
- Some tests may call real LLM APIs
- You **need `.env.secrets`** in the project root
- The config system will automatically find it (see `config_helper.py`)

**For E2E Tests (Phase 3):**
- Need full infrastructure (Redis, ArangoDB, services)
- Need `.env.secrets` for LLM APIs
- Use Docker Compose to spin up services

### Step 4: Run Tests by Phase

#### Phase 1: Unit Tests (No Services Needed)

```bash
# Run all unit tests
pytest tests/3d/startup/ -v
pytest tests/3d/solution/ -v
pytest tests/3d/mcp/ -v
pytest tests/3d/agents/ -v
pytest tests/3d/artifacts/ -v
pytest tests/3d/security/ -v

# Or run all at once
pytest tests/3d/startup/ tests/3d/solution/ tests/3d/mcp/ tests/3d/agents/ tests/3d/artifacts/ tests/3d/security/ -v
```

**These use mocked services** - no real infrastructure needed!

#### Phase 2: Journey Tests (May Need Services)

```bash
# Run journey tests
pytest tests/3d/journey/ -v

# Or by solution
pytest tests/3d/journey/coexistence/ -v
pytest tests/3d/journey/content_solution/ -v
pytest tests/3d/journey/insights_solution/ -v
pytest tests/3d/journey/operations_solution/ -v
```

**Note:** These may need `.env.secrets` if they call real LLM APIs.

#### Phase 3: E2E Tests (Full Services Required)

```bash
# Start test infrastructure
cd tests/infrastructure
docker-compose -f docker-compose.3d-test.yml up -d

# Wait for services to be healthy
python wait_for_services.py

# Run E2E tests
cd ../..
pytest tests/e2e/demo_paths/ -v

# Clean up
cd tests/infrastructure
docker-compose -f docker-compose.3d-test.yml down
```

---

## 🔑 Environment Variables & LLM Testing

### How `.env.secrets` is Loaded

The platform automatically finds `.env.secrets` using this priority:

1. `symphainy_platform/.env.secrets`
2. `.env.secrets` (project root) ← **This is where yours is**
3. Fallback paths

**Your `.env.secrets` is at:**
```
/home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric/.env.secrets
```

### What Tests Need API Keys

**Tests that call LLM APIs:**
- Intent service tests (if they use AI agents)
- Journey tests (if they use AI orchestration)
- E2E demo path tests (full user journeys)

**Tests that DON'T need API keys:**
- Unit tests (fully mocked)
- Solution initialization tests
- MCP server structure tests
- Artifact structure tests

### Running Tests Without API Keys

If you want to run tests without real LLM calls:

1. **Unit tests** - Already mocked, no API keys needed
2. **Integration tests** - May fail if they try to call real APIs
3. **Use pytest markers** to skip LLM-dependent tests:

```bash
# Skip tests marked as requiring LLM
pytest -m "not llm_required" -v
```

---

## 🐳 Docker Compose for E2E Tests

The `docker-compose.3d-test.yml` spins up:

- **Redis** (port 6379) - State management
- **ArangoDB** (port 8529) - Graph storage
- **Consul** (port 8500) - Service discovery
- **Runtime Service** (port 8000) - Platform runtime
- **Experience Service** (port 8001) - Realm services

**To use:**

```bash
cd tests/infrastructure
docker-compose -f docker-compose.3d-test.yml up -d
python wait_for_services.py  # Wait for health checks
```

**Environment variables** for Docker services are set in the compose file. Your `.env.secrets` is used by the Python code, not Docker.

---

## 📊 Test Execution Flow

### In CI/CD (GitHub Actions)

1. **Phase 1** runs first (unit tests, no services)
2. **Phase 2** runs after Phase 1 passes (journey tests)
3. **Phase 3** runs after Phase 2 passes (E2E with services)

### Locally

You can run phases independently:

```bash
# Just unit tests
pytest tests/3d/startup/ tests/3d/solution/ -v

# Just one solution's journey tests
pytest tests/3d/journey/content_solution/ -v

# Full E2E with services
docker-compose -f tests/infrastructure/docker-compose.3d-test.yml up -d
pytest tests/e2e/demo_paths/ -v
```

---

## 🔍 Understanding Test Fixtures

All tests use fixtures from `tests/3d/conftest.py`:

- **`mock_public_works`** - Mocked infrastructure (no real services)
- **`mock_state_surface`** - Mocked state management
- **`execution_context`** - Test execution context
- **`{solution}_solution`** - Solution instances (e.g., `content_solution`, `operations_solution`)

**Unit tests** use mocks - no real infrastructure.

**Integration tests** may use real services if configured.

---

## ⚠️ Common Issues

### Issue: Tests can't find `.env.secrets`

**Solution:** Ensure `.env.secrets` is in project root:
```bash
ls /home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric/.env.secrets
```

### Issue: Tests fail with "Module not found"

**Solution:** Tests add project root to `sys.path` automatically. Ensure you're running from project root:
```bash
cd /home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric
pytest tests/3d/...
```

### Issue: E2E tests can't connect to services

**Solution:** 
1. Check Docker services are running: `docker ps`
2. Check health: `python tests/infrastructure/wait_for_services.py`
3. Check ports aren't in use: `netstat -tuln | grep -E "6379|8529|8500|8000|8001"`

### Issue: LLM API rate limits

**Solution:** Tests should handle rate limits gracefully. If hitting limits:
- Run tests in smaller batches
- Use test markers to skip LLM-dependent tests
- Check your API key quotas

---

## 📝 Summary

**To run tests locally:**

1. ✅ Tests are already in GitHub (commit `b46dd37`)
2. ✅ You have `.env.secrets` in project root
3. ✅ Install pytest: `pip install pytest pytest-asyncio`
4. ✅ Run Phase 1 (unit tests) - no services needed
5. ✅ Run Phase 2 (journey tests) - may need `.env.secrets`
6. ✅ Run Phase 3 (E2E) - need Docker Compose + `.env.secrets`

**You don't need to "bring tests into project folder"** - they're already part of the repo! Just ensure your local checkout has them (they should be there after `git pull`).

---

**Last Updated:** January 27, 2026  
**Status:** ✅ Ready to use
