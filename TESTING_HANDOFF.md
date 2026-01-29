# Symphainy Platform - Testing Handoff

This document provides everything needed to run and test the Symphainy platform end-to-end.

## Quick Start

### Prerequisites

- Docker & Docker Compose v2.0+
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

### Start Full Stack

```bash
# From workspace root
docker-compose -f docker-compose.fullstack.yml up --build

# Access points:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:80/api
# - Traefik Dashboard: http://localhost:8080
# - ArangoDB UI: http://localhost:8529
# - Consul UI: http://localhost:8500
```

### Stop Full Stack

```bash
docker-compose -f docker-compose.fullstack.yml down

# To also remove volumes (fresh start):
docker-compose -f docker-compose.fullstack.yml down -v
```

---

## Running Tests

### Backend Tests

```bash
# Start infrastructure only (for running tests locally)
docker-compose -f docker-compose.test.yml up -d

# Run all backend tests
cd symphainy_coexistence_fabric
pytest tests/ -v --timeout=60

# Run specific test categories
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only
pytest tests/ -k "test_session" -v       # Tests matching pattern

# Current status: 321 passed, 1 skipped
```

### Frontend Tests

```bash
cd symphainy-frontend

# Install dependencies
npm install

# Unit tests with Jest
npm test

# Run tests with coverage
npm test -- --coverage

# Watch mode for development
npm test -- --watch
```

### E2E Tests (Playwright)

```bash
cd symphainy-frontend

# Install Playwright browsers
npx playwright install --with-deps chromium

# Run E2E tests (requires full stack running)
npx playwright test

# Run in headed mode (visible browser)
npx playwright test --headed

# Run specific test file
npx playwright test e2e/critical-journeys.spec.ts

# View test report
npx playwright show-report
```

### Integration Tests

```bash
# Ensure full stack is running first
docker-compose -f docker-compose.fullstack.yml up -d

# Wait for services to be healthy
docker-compose -f docker-compose.fullstack.yml ps

# Run integration tests
cd symphainy-frontend
npm run test:integration
```

---

## Test Categories

### Backend Tests (pytest)

| Category | Count | Status | Description |
|----------|-------|--------|-------------|
| Unit | ~200 | ✅ Passing | Fast, isolated tests with mocked dependencies |
| Integration | ~100 | ✅ Passing | Tests with real infrastructure services |
| E2E | ~20 | ✅ Passing | Full journey tests through the runtime |

### Frontend Tests (Jest)

| Category | Count | Status | Description |
|----------|-------|--------|-------------|
| Unit | ~150 | ⚠️ ~50% passing | Component and utility tests |
| Integration | ~50 | ⚠️ Needs real backend | Service integration tests |
| E2E | ~20 | ⚠️ Needs setup | Playwright browser tests |

---

## Critical User Journeys to Test

### Journey 1: Session Creation & Authentication

1. User navigates to home page
2. Anonymous session is automatically created
3. Session token is stored in browser
4. User can authenticate (login/register)

**Test Command:**
```bash
npx playwright test -g "session"
```

### Journey 2: File Upload & Analysis

1. User logs in (session created)
2. User navigates to Content pillar
3. User uploads file (ingest_file intent)
4. File is parsed (parse_content intent)
5. Embeddings created (extract_embeddings intent)
6. User can view file details

**Test Command:**
```bash
npx playwright test -g "upload"
```

### Journey 3: Insights Analysis

1. User navigates to Insights pillar
2. User selects a file for analysis
3. Analysis runs (run_analysis intent)
4. Results are displayed
5. User can interact with results

**Test Command:**
```bash
npx playwright test -g "insights"
```

### Journey 4: Workflow Creation

1. User selects SOP document
2. System analyzes document
3. Workflow generated
4. User reviews and approves

**Test Command:**
```bash
npx playwright test -g "workflow"
```

### Journey 5: Roadmap Generation

1. User navigates to Outcomes pillar
2. User defines goals
3. System generates roadmap
4. User refines roadmap
5. Export to PDF/document

**Test Command:**
```bash
npx playwright test -g "roadmap"
```

---

## Environment Variables

### Backend (.env)

```env
# Infrastructure Services
REDIS_URL=redis://localhost:6379
ARANGODB_URL=http://localhost:8529
ARANGODB_PASSWORD=symphainy_dev
CONSUL_HOST=localhost
CONSUL_PORT=8500
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_MASTER_KEY=dev_master_key
GCS_EMULATOR_HOST=localhost:9023

# Runtime Configuration
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

### Frontend (.env.local)

```env
# API Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:80
NEXT_PUBLIC_API_URL=http://localhost:80/api
NEXT_PUBLIC_WS_URL=ws://localhost:80

# For local development without Docker
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Test Environment

```env
# Test infrastructure uses different ports to avoid conflicts
TEST_REDIS_PORT=6380
TEST_ARANGO_PORT=8530
TEST_CONSUL_PORT=8501
TEST_MEILISEARCH_PORT=7701
TEST_GCS_EMULATOR_PORT=9023
```

---

## Troubleshooting

### Backend won't start

1. **Check Redis is running:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. **Check ArangoDB is running:**
   ```bash
   curl http://localhost:8529/_api/version
   ```

3. **Check container logs:**
   ```bash
   docker-compose logs backend
   ```

4. **Check all services are healthy:**
   ```bash
   docker-compose ps
   ```

### Frontend build fails

1. **Ensure environment variables are set:**
   ```bash
   echo $NEXT_PUBLIC_BACKEND_URL
   ```

2. **Check for TypeScript errors:**
   ```bash
   cd symphainy-frontend
   npm run build
   ```

3. **Clear build cache:**
   ```bash
   rm -rf .next
   npm run build
   ```

### WebSocket won't connect

1. **Verify Traefik is routing correctly:**
   - Open http://localhost:8080 (Traefik dashboard)
   - Check that `/ws` and `/api/runtime/agent` routes exist

2. **Check backend WebSocket endpoint:**
   ```bash
   curl -i http://localhost:80/api/health
   ```

3. **Test WebSocket directly:**
   ```javascript
   // In browser console
   const ws = new WebSocket('ws://localhost:80/api/runtime/agent?session_token=test');
   ws.onopen = () => console.log('Connected');
   ws.onerror = (e) => console.error('Error', e);
   ```

### Tests timeout

1. **Increase timeout:**
   ```bash
   pytest --timeout=120
   ```

2. **Check infrastructure health:**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

3. **Look for deadlocks in async code:**
   - Check for missing `await` statements
   - Check for circular dependencies

### Tests fail with connection errors

1. **Ensure test infrastructure is running:**
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   ```

2. **Wait for services to be ready:**
   ```bash
   sleep 30  # Or use health check scripts
   ```

3. **Verify connectivity:**
   ```bash
   # Redis
   redis-cli -p 6380 ping
   
   # ArangoDB
   curl http://localhost:8530/_api/version
   ```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         TRAEFIK                                  │
│                    (API Gateway & Proxy)                        │
│  Port 80: HTTP    Port 8080: Dashboard                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐          ┌─────────────────────────────┐     │
│   │  Frontend   │  ──────> │        Backend              │     │
│   │  (Next.js)  │          │    (Runtime API)            │     │
│   │  Port 3000  │          │      Port 8000              │     │
│   └─────────────┘          └─────────────────────────────┘     │
│                                       │                         │
│                                       │                         │
│   ┌───────────────────────────────────┴───────────────────────┐ │
│   │                  Infrastructure Services                   │ │
│   │                                                            │ │
│   │  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────────────┐ │ │
│   │  │  Redis  │  │ ArangoDB │  │ Consul │  │ Meilisearch  │ │ │
│   │  │  :6379  │  │  :8529   │  │ :8500  │  │    :7700     │ │ │
│   │  └─────────┘  └──────────┘  └────────┘  └──────────────┘ │ │
│   │                                                            │ │
│   │  ┌──────────────┐                                         │ │
│   │  │ GCS Emulator │                                         │ │
│   │  │    :9023     │                                         │ │
│   │  └──────────────┘                                         │ │
│   │                                                            │ │
│   └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## CI/CD Integration

Tests are automatically run in CI/CD pipeline:

1. **On Push:** Unit tests run for affected services
2. **On PR:** Full integration test suite
3. **On Merge to Main:** E2E tests with full stack

See `.github/workflows/integration-tests.yml` for details.

---

## Contact & Support

- **Backend Issues:** Check `symphainy_coexistence_fabric/` directory
- **Frontend Issues:** Check `symphainy-frontend/` directory
- **Infrastructure Issues:** Check `docker-compose.*.yml` files
- **Documentation:** Check `docs/` directory

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-28 | 1.0.0 | Initial testing handoff documentation |
