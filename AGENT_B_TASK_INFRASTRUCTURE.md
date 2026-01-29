# Agent B Task: Infrastructure, WebSocket & Testing Setup

**Branch to create:** `cursor/infrastructure-testing-setup`
**Base branch:** `cursor/parameter-assertion-tests-829c`
**Estimated time:** 4-6 hours

---

## Your Mission

You are setting up the infrastructure layer that enables the Symphainy platform to be tested end-to-end. This includes:

1. **Traefik WebSocket Proxy Configuration**
2. **Docker Compose for Full Stack Testing**
3. **Testing Handoff Documentation**
4. **E2E Test Suite Setup**

**You are NOT touching:**
- Component code
- Provider code
- Type definitions
- API stub files

**Another agent is handling those in parallel.**

---

## Context: What Already Exists

### Backend (Working)
- Location: `/workspace/symphainy_coexistence_fabric/`
- Runtime API: `symphainy_platform/runtime/runtime_api.py`
- Endpoints already exist:
  - `POST /api/session/create` - Create session
  - `POST /api/session/create-anonymous` - Anonymous session
  - `POST /api/intent/submit` - Submit intent
  - `GET /api/execution/{id}/status` - Execution status
  - WebSocket: `/ws/` (needs Traefik routing)

### Frontend (Being Fixed)
- Location: `/workspace/symphainy-frontend/`
- ExperiencePlaneClient: `shared/services/ExperiencePlaneClient.ts`
- WebSocket Client: `shared/services/UnifiedWebSocketClient.ts`
- Config: `shared/config/api-config.ts`

### Existing Docker Config
- Test compose: `/workspace/docker-compose.test.yml`
- Services: Redis, ArangoDB, Consul, Meilisearch, GCS Emulator

---

## Task 1: Traefik WebSocket Proxy Configuration

### Goal
Configure Traefik to proxy both REST API and WebSocket connections from frontend to backend.

### Files to Create

**1. `/workspace/traefik/traefik.yml`** (static config)
```yaml
# Traefik Static Configuration
api:
  dashboard: true
  insecure: true  # For local dev only

entryPoints:
  web:
    address: ":80"
  websocket:
    address: ":8080"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
  file:
    filename: /etc/traefik/dynamic.yml
    watch: true

log:
  level: DEBUG
```

**2. `/workspace/traefik/dynamic.yml`** (dynamic config)
```yaml
# Traefik Dynamic Configuration
http:
  routers:
    # REST API Router
    api-router:
      rule: "PathPrefix(`/api`)"
      service: backend
      entryPoints:
        - web

    # WebSocket Router
    ws-router:
      rule: "PathPrefix(`/ws`)"
      service: backend-ws
      entryPoints:
        - web
      middlewares:
        - websocket-headers

  middlewares:
    websocket-headers:
      headers:
        customRequestHeaders:
          Connection: "Upgrade"
          Upgrade: "websocket"

  services:
    backend:
      loadBalancer:
        servers:
          - url: "http://backend:8000"

    backend-ws:
      loadBalancer:
        servers:
          - url: "http://backend:8000"
        sticky:
          cookie:
            name: ws_affinity
            secure: false
            httpOnly: true
```

### Update Next.js Config

Update `/workspace/symphainy-frontend/next.config.js` to use Traefik:

```javascript
// In rewrites() function, ensure these exist:
async rewrites() {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:80';
  
  return [
    {
      source: '/api/:path*',
      destination: `${backendUrl}/api/:path*`,
    },
    {
      source: '/ws/:path*', 
      destination: `${backendUrl}/ws/:path*`,
    },
  ];
}
```

### Update WebSocket Client

Review `/workspace/symphainy-frontend/shared/services/UnifiedWebSocketClient.ts` and ensure it:
1. Uses the correct WebSocket URL from config
2. Handles reconnection properly
3. Works through Traefik proxy

Check `/workspace/symphainy-frontend/shared/config/api-config.ts` for WebSocket URL configuration.

---

## Task 2: Docker Compose for Full Stack

### Goal
Create a docker-compose that runs frontend + backend + infrastructure for testing.

### File to Create: `/workspace/docker-compose.fullstack.yml`

```yaml
version: '3.8'

services:
  # ==========================================================================
  # TRAEFIK - API Gateway & WebSocket Proxy
  # ==========================================================================
  traefik:
    image: traefik:v2.10
    container_name: symphainy-traefik
    ports:
      - "80:80"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik/traefik.yml:/etc/traefik/traefik.yml:ro
      - ./traefik/dynamic.yml:/etc/traefik/dynamic.yml:ro
    networks:
      - symphainy_net
    depends_on:
      - backend

  # ==========================================================================
  # BACKEND - Symphainy Runtime
  # ==========================================================================
  backend:
    build:
      context: .
      dockerfile: Dockerfile.smart-city
    container_name: symphainy-backend
    environment:
      - REDIS_URL=redis://redis:6379
      - ARANGODB_URL=http://arango:8529
      - ARANGODB_PASSWORD=symphainy_dev
      - CONSUL_HOST=consul
      - CONSUL_PORT=8500
      - MEILISEARCH_URL=http://meilisearch:7700
      - MEILISEARCH_MASTER_KEY=dev_master_key
      - GCS_EMULATOR_HOST=gcs-emulator:9023
      - ENVIRONMENT=development
    expose:
      - "8000"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=PathPrefix(`/api`) || PathPrefix(`/ws`)"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
    networks:
      - symphainy_net
    depends_on:
      redis:
        condition: service_healthy
      arango:
        condition: service_healthy
      consul:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  # ==========================================================================
  # FRONTEND - Next.js Application
  # ==========================================================================
  frontend:
    build:
      context: ./symphainy-frontend
      dockerfile: Dockerfile
    container_name: symphainy-frontend
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://traefik:80
      - NEXT_PUBLIC_API_URL=http://traefik:80
      - NEXT_PUBLIC_WS_URL=ws://traefik:80
    ports:
      - "3000:3000"
    networks:
      - symphainy_net
    depends_on:
      - traefik
      - backend

  # ==========================================================================
  # INFRASTRUCTURE SERVICES
  # ==========================================================================
  
  redis:
    image: redis:7-alpine
    container_name: symphainy-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 3
    networks:
      - symphainy_net

  arango:
    image: arangodb:3.11
    container_name: symphainy-arango
    ports:
      - "8529:8529"
    environment:
      ARANGO_ROOT_PASSWORD: symphainy_dev
    healthcheck:
      test: ["CMD-SHELL", "wget --spider -q http://localhost:8529/_api/version || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - symphainy_net

  consul:
    image: hashicorp/consul:latest
    container_name: symphainy-consul
    ports:
      - "8500:8500"
    command: agent -server -bootstrap-expect=1 -client=0.0.0.0 -ui
    healthcheck:
      test: ["CMD", "consul", "info"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - symphainy_net

  meilisearch:
    image: getmeili/meilisearch:v1.5
    container_name: symphainy-meilisearch
    ports:
      - "7700:7700"
    environment:
      - MEILI_MASTER_KEY=dev_master_key
      - MEILI_ENV=development
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:7700/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - symphainy_net

  gcs-emulator:
    image: fsouza/fake-gcs-server:latest
    container_name: symphainy-gcs
    ports:
      - "9023:9023"
    command: -scheme http -port 9023 -public-host localhost:9023 -backend memory
    networks:
      - symphainy_net

networks:
  symphainy_net:
    driver: bridge

volumes:
  redis_data:
  arango_data:
  consul_data:
  meilisearch_data:
```

---

## Task 3: Frontend Dockerfile

### File to Create: `/workspace/symphainy-frontend/Dockerfile`

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Set build-time environment variables
ARG NEXT_PUBLIC_BACKEND_URL=http://localhost:80
ARG NEXT_PUBLIC_API_URL=http://localhost:80
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built application
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

---

## Task 4: Testing Handoff Document

### File to Create: `/workspace/TESTING_HANDOFF.md`

```markdown
# Symphainy Platform - Testing Handoff

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Start Full Stack
```bash
# From workspace root
docker-compose -f docker-compose.fullstack.yml up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:80/api
# Traefik Dashboard: http://localhost:8080
```

### Run Backend Tests
```bash
# With infrastructure running:
docker-compose -f docker-compose.test.yml up -d

# Run tests
cd symphainy_coexistence_fabric
pytest tests/ -v --timeout=60

# Current status: 321 passed, 1 skipped
```

### Run Frontend Tests
```bash
cd symphainy-frontend

# Unit tests
npm test

# E2E tests (requires full stack running)
npm run test:e2e
```

### Run Integration Tests
```bash
# Ensure full stack is running first
docker-compose -f docker-compose.fullstack.yml up -d

# Run integration tests
cd symphainy-frontend
npm run test:integration
```

## Test Categories

### Backend Tests (pytest)
| Category | Count | Status |
|----------|-------|--------|
| Unit | ~200 | ✅ Passing |
| Integration | ~100 | ✅ Passing |
| E2E | ~20 | ✅ Passing |

### Frontend Tests (Jest)
| Category | Count | Status |
|----------|-------|--------|
| Unit | ~150 | ⚠️ ~50% passing |
| Integration | ~50 | ⚠️ Needs real backend |
| E2E | ~20 | ⚠️ Needs setup |

## Critical User Journeys to Test

### Journey 1: File Upload & Analysis
1. User logs in (session created)
2. User uploads file (ingest_file intent)
3. File is parsed (parse_content intent)
4. Embeddings created (extract_embeddings intent)
5. Analysis run (run_analysis intent)

### Journey 2: Workflow Creation
1. User selects SOP document
2. System analyzes document
3. Workflow generated
4. User reviews and approves

### Journey 3: Roadmap Generation
1. User defines goals
2. System generates roadmap
3. User refines roadmap
4. Export to PDF/document

## Environment Variables

### Backend
```env
REDIS_URL=redis://localhost:6379
ARANGODB_URL=http://localhost:8529
ARANGODB_PASSWORD=symphainy_dev
CONSUL_HOST=localhost
CONSUL_PORT=8500
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_MASTER_KEY=dev_master_key
```

### Frontend
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:80
NEXT_PUBLIC_API_URL=http://localhost:80
NEXT_PUBLIC_WS_URL=ws://localhost:80
```

## Troubleshooting

### Backend won't start
- Check Redis is running: `redis-cli ping`
- Check ArangoDB is running: `curl http://localhost:8529/_api/version`
- Check logs: `docker-compose logs backend`

### Frontend build fails
- Ensure NEXT_PUBLIC_BACKEND_URL is set
- Check for TypeScript errors: `npm run build`

### WebSocket won't connect
- Verify Traefik is routing `/ws/*` correctly
- Check Traefik dashboard at http://localhost:8080
- Verify backend WebSocket endpoint is up

### Tests timeout
- Increase timeout: `pytest --timeout=120`
- Check infrastructure health
- Look for deadlocks in async code
```

---

## Task 5: E2E Test Setup (Playwright)

### File to Create: `/workspace/symphainy-frontend/e2e/critical-journeys.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Critical User Journeys', () => {
  test.beforeEach(async ({ page }) => {
    // Start at home page
    await page.goto('/');
  });

  test('Journey 1: Anonymous session creation', async ({ page }) => {
    // Verify session is created on page load
    await expect(page.locator('[data-testid="session-status"]')).toBeVisible();
    
    // Check session token exists
    const sessionToken = await page.evaluate(() => {
      return sessionStorage.getItem('session_token');
    });
    expect(sessionToken).toBeTruthy();
  });

  test('Journey 2: File upload flow', async ({ page }) => {
    // Navigate to content pillar
    await page.click('[data-testid="nav-content"]');
    await expect(page).toHaveURL(/.*pillars\/content/);

    // Upload a test file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from('name,value\ntest,123'),
    });

    // Verify upload started
    await expect(page.locator('[data-testid="upload-progress"]')).toBeVisible();
    
    // Wait for completion (with timeout)
    await expect(page.locator('[data-testid="upload-success"]')).toBeVisible({
      timeout: 30000,
    });
  });

  test('Journey 3: Insights analysis', async ({ page }) => {
    // Navigate to insights pillar
    await page.click('[data-testid="nav-insights"]');
    await expect(page).toHaveURL(/.*pillars\/insights/);

    // Select a file for analysis
    await page.click('[data-testid="select-file"]');
    
    // Run analysis
    await page.click('[data-testid="run-analysis"]');
    
    // Verify results appear
    await expect(page.locator('[data-testid="analysis-results"]')).toBeVisible({
      timeout: 60000,
    });
  });

  test('WebSocket connection', async ({ page }) => {
    // Navigate to a page that uses WebSocket
    await page.goto('/pillars/journey');
    
    // Verify WebSocket connected
    const wsConnected = await page.evaluate(() => {
      // Check if WebSocket is in OPEN state
      return (window as any).__wsClient?.readyState === WebSocket.OPEN;
    });
    
    // Note: This test may need adjustment based on actual implementation
    // The important thing is to verify WebSocket connectivity
  });
});
```

### Update Playwright Config

Review and update `/workspace/symphainy-frontend/playwright.config.ts`:

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Start services before tests
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

---

## Task 6: CI/CD Integration Test Workflow

### File to Create: `/workspace/.github/workflows/integration-tests.yml`

```yaml
name: Integration Tests

on:
  push:
    branches: [main, 'cursor/*']
  pull_request:
    branches: [main]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install backend dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-timeout

      - name: Install frontend dependencies
        working-directory: symphainy-frontend
        run: npm ci

      - name: Start backend
        run: |
          cd symphainy_coexistence_fabric
          python -m uvicorn symphainy_platform.runtime.runtime_api:create_app --host 0.0.0.0 --port 8000 &
          sleep 10

      - name: Run backend tests
        run: |
          cd symphainy_coexistence_fabric
          pytest tests/ -v --timeout=60

      - name: Build frontend
        working-directory: symphainy-frontend
        env:
          NEXT_PUBLIC_BACKEND_URL: http://localhost:8000
          NEXT_PUBLIC_API_URL: http://localhost:8000
        run: npm run build

      - name: Run frontend tests
        working-directory: symphainy-frontend
        env:
          NEXT_PUBLIC_BACKEND_URL: http://localhost:8000
          NEXT_PUBLIC_API_URL: http://localhost:8000
        run: npm test

      - name: Install Playwright
        working-directory: symphainy-frontend
        run: npx playwright install --with-deps chromium

      - name: Run E2E tests
        working-directory: symphainy-frontend
        env:
          PLAYWRIGHT_BASE_URL: http://localhost:3000
          NEXT_PUBLIC_BACKEND_URL: http://localhost:8000
        run: |
          npm run start &
          sleep 10
          npx playwright test
```

---

## Files You Will Create/Modify

### Create New:
- `/workspace/traefik/traefik.yml`
- `/workspace/traefik/dynamic.yml`
- `/workspace/docker-compose.fullstack.yml`
- `/workspace/symphainy-frontend/Dockerfile`
- `/workspace/symphainy-frontend/e2e/critical-journeys.spec.ts`
- `/workspace/TESTING_HANDOFF.md`
- `/workspace/.github/workflows/integration-tests.yml`

### Modify:
- `/workspace/symphainy-frontend/next.config.js` (add WebSocket rewrite)
- `/workspace/symphainy-frontend/playwright.config.ts` (update config)
- `/workspace/symphainy-frontend/shared/config/api-config.ts` (verify WS URL)

### Do NOT Modify:
- `/workspace/symphainy-frontend/shared/types/*`
- `/workspace/symphainy-frontend/shared/state/*`
- `/workspace/symphainy-frontend/shared/services/ExperiencePlaneClient.ts`
- `/workspace/symphainy-frontend/lib/api/*`
- Any component files

---

## Success Criteria

1. **Traefik routes work:**
   - `curl http://localhost:80/api/health` returns 200
   - WebSocket connects through `ws://localhost:80/ws`

2. **Docker Compose starts cleanly:**
   - `docker-compose -f docker-compose.fullstack.yml up` starts all services
   - All health checks pass

3. **E2E tests run:**
   - `npx playwright test` executes without infrastructure errors
   - At least the session creation test passes

4. **Documentation is complete:**
   - TESTING_HANDOFF.md has all necessary commands
   - README sections updated if needed

---

## Questions?

If you encounter issues:
1. Check the existing `/workspace/docker-compose.test.yml` for reference
2. Check `/workspace/symphainy-frontend/shared/config/api-config.ts` for URL patterns
3. The backend API structure is in `/workspace/symphainy_coexistence_fabric/symphainy_platform/runtime/runtime_api.py`

The other agent (Agent A) is working on provider consolidation and stub elimination. Your work is independent and should not conflict.
