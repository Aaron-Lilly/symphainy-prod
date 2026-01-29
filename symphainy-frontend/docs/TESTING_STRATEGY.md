# Symphainy Frontend Testing Strategy

**Status:** Active
**Last Updated:** January 2026

## Philosophy

> **Tests exist to prove the platform works, not to prove code compiles.**

Our testing strategy prioritizes:
1. **Real infrastructure** over mocks
2. **Real files** over synthetic data
3. **Real answers** over API availability checks
4. **User journeys** over unit coverage

## The Problem with Current Tests

Most frontend tests follow the "mock everything" pattern:

```typescript
// ❌ BAD: This test passes even if the backend is broken
jest.mock('@/shared/services/ExperiencePlaneClient');
const mockClient = { submitIntent: jest.fn().mockResolvedValue({ execution_id: '123' }) };

test('submits intent', async () => {
  await submitIntent('ingest_file', {});
  expect(mockClient.submitIntent).toHaveBeenCalled(); // ✅ Passes
  // But does the file actually get ingested? We don't know.
});
```

These tests verify:
- ✅ Code runs without throwing
- ✅ Functions are called with expected arguments
- ❌ Files are actually parsed correctly
- ❌ Data flows through the real system
- ❌ Results are semantically correct

## Testing Pyramid (Inverted for Platform Validation)

Traditional pyramid (unit-heavy):
```
        /\
       /  \  E2E (few)
      /----\
     /      \  Integration (some)
    /--------\
   /          \  Unit (many)
  /______________\
```

**Our pyramid (integration-heavy):**
```
  ______________
  \            /  Unit (few - pure logic only)
   \----------/
    \        /  Integration (many - real backend)
     \------/
      \    /  E2E (comprehensive - full journeys)
       \  /
        \/
```

## Test Categories

### 1. Unit Tests (Minimal)
**Purpose:** Test pure logic with no I/O
**Infrastructure:** None (runs in Jest)
**Examples:**
- Date formatting utilities
- Validation regex
- State reducers (pure functions)

**NOT unit tests:**
- Anything that calls an API
- Anything that reads/writes files
- Anything that depends on session state

### 2. Integration Tests (Primary Focus)
**Purpose:** Prove features work with real backend
**Infrastructure:** Docker Compose (backend + DB + storage)
**Examples:**
- File upload → verify file exists in storage
- Parse file → verify parsed content is correct
- Submit intent → verify execution completes with expected artifacts

```typescript
// ✅ GOOD: Integration test with real backend
describe('File Upload Integration', () => {
  beforeAll(async () => {
    // Start real backend via Docker
    await startBackendServices();
    // Create real session
    session = await createRealSession();
  });

  test('uploads CSV file and parses it correctly', async () => {
    // Upload REAL file
    const file = await readTestFile('fixtures/sample-data.csv');
    const uploadResult = await uploadFile(file);
    
    // Verify file EXISTS in real storage
    expect(uploadResult.success).toBe(true);
    const storedFile = await getFileFromStorage(uploadResult.file_id);
    expect(storedFile).not.toBeNull();
    
    // Parse and verify REAL content
    const parseResult = await parseFile(uploadResult.file_id);
    expect(parseResult.success).toBe(true);
    
    // Verify parsed data matches expected structure
    expect(parseResult.parsed_data.columns).toContain('name');
    expect(parseResult.parsed_data.columns).toContain('value');
    expect(parseResult.parsed_data.row_count).toBe(100);
  });
});
```

### 3. E2E Tests (User Journeys)
**Purpose:** Prove complete user workflows work
**Infrastructure:** Full stack (frontend + backend + all services)
**Tool:** Playwright
**Examples:**
- User uploads file → parses → analyzes → exports results
- User creates session → navigates pillars → submits intents → sees results

```typescript
// ✅ GOOD: E2E test validating real user journey
test('Content Pillar: Upload to Insights Flow', async ({ page }) => {
  // Login with real credentials
  await page.goto('/login');
  await page.fill('[data-testid="email"]', testUser.email);
  await page.fill('[data-testid="password"]', testUser.password);
  await page.click('[data-testid="login-button"]');
  
  // Navigate to Content pillar
  await page.goto('/pillars/content');
  
  // Upload real file
  const fileInput = page.locator('[data-testid="file-upload"]');
  await fileInput.setInputFiles('tests/fixtures/financial-data.csv');
  
  // Wait for upload completion
  await expect(page.locator('[data-testid="upload-success"]')).toBeVisible();
  
  // Parse file
  await page.click('[data-testid="parse-button"]');
  await expect(page.locator('[data-testid="parse-complete"]')).toBeVisible();
  
  // Navigate to Insights
  await page.goto('/pillars/insights');
  
  // Select uploaded file for analysis
  await page.click('[data-testid="file-selector"]');
  await page.click(`text=${testFile.name}`);
  
  // Run analysis
  await page.click('[data-testid="analyze-button"]');
  
  // Verify REAL insights are generated
  const insightsPanel = page.locator('[data-testid="insights-panel"]');
  await expect(insightsPanel).toContainText('columns detected');
  await expect(insightsPanel).toContainText('data quality');
});
```

## Test Fixtures

### Real Test Files
Location: `tests/fixtures/`

```
tests/fixtures/
├── csv/
│   ├── simple-10-rows.csv        # Basic CSV, 10 rows
│   ├── financial-data.csv        # Financial data, 1000 rows
│   ├── malformed.csv             # Invalid CSV for error testing
│   └── unicode-content.csv       # UTF-8 special characters
├── json/
│   ├── simple-object.json
│   ├── nested-array.json
│   └── large-dataset.json        # 10MB JSON
├── pdf/
│   ├── simple-text.pdf
│   ├── with-tables.pdf
│   └── scanned-image.pdf
└── excel/
    ├── single-sheet.xlsx
    └── multi-sheet.xlsx
```

### Expected Results
Each fixture has corresponding expected results:

```
tests/expected/
├── csv/
│   ├── simple-10-rows.parsed.json
│   ├── simple-10-rows.quality.json
│   └── simple-10-rows.insights.json
└── ...
```

## Validation Patterns

### 1. Structural Validation
```typescript
// Verify response has expected shape
expect(result).toMatchObject({
  success: true,
  artifacts: {
    parsed_content: expect.objectContaining({
      columns: expect.any(Array),
      row_count: expect.any(Number),
    }),
  },
});
```

### 2. Semantic Validation
```typescript
// Verify content is semantically correct
const parsed = result.artifacts.parsed_content;
expect(parsed.columns).toEqual(['id', 'name', 'value', 'date']);
expect(parsed.row_count).toBe(100);
expect(parsed.rows[0].name).toBe('First Item');
```

### 3. Quality Validation
```typescript
// Verify quality assessment is accurate
const quality = result.artifacts.quality_report;
expect(quality.completeness).toBeGreaterThan(0.95);
expect(quality.issues).toHaveLength(0);
```

### 4. Cross-System Validation
```typescript
// Verify data flows correctly between systems
const uploadResult = await uploadFile(file);
const parseResult = await parseFile(uploadResult.file_id);
const insightsResult = await analyzeFile(parseResult.parsed_file_id);

// Verify lineage is preserved
expect(insightsResult.artifacts.lineage.source_file_id).toBe(uploadResult.file_id);
expect(insightsResult.artifacts.lineage.parsed_file_id).toBe(parseResult.parsed_file_id);
```

## Infrastructure Requirements

### Docker Compose Setup
```yaml
# docker-compose.test.yml
services:
  backend:
    image: symphainy-backend:test
    environment:
      - DATABASE_URL=postgresql://test:test@db:5432/test
      - STORAGE_BACKEND=minio
    depends_on:
      - db
      - minio
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=test
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
  
  minio:
    image: minio/minio
    command: server /data
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin

  frontend:
    build: ./symphainy-frontend
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://backend:8000
    depends_on:
      - backend
```

### Test Execution
```bash
# Start infrastructure
docker-compose -f docker-compose.test.yml up -d

# Wait for services
./scripts/wait-for-services.sh

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e

# Cleanup
docker-compose -f docker-compose.test.yml down -v
```

## Test Organization

```
tests/
├── unit/                    # Pure logic tests (minimal)
│   └── utils/
├── integration/             # Real backend tests (primary)
│   ├── content/
│   │   ├── file-upload.test.ts
│   │   ├── file-parse.test.ts
│   │   └── embeddings.test.ts
│   ├── insights/
│   │   ├── data-quality.test.ts
│   │   └── analysis.test.ts
│   └── journeys/
│       └── upload-to-insight.test.ts
├── e2e/                     # Playwright user journey tests
│   ├── content-pillar.spec.ts
│   ├── insights-pillar.spec.ts
│   └── cross-pillar-flow.spec.ts
├── fixtures/                # Real test files
└── expected/                # Expected results for validation
```

## Success Criteria

A test suite is successful when:

1. **Coverage is meaningful**
   - Not "80% line coverage" but "all critical paths tested with real data"

2. **Failures indicate real problems**
   - If a test fails, the platform is actually broken
   - No flaky tests that fail randomly

3. **Tests are maintainable**
   - Adding a new feature = adding corresponding integration test
   - Changing backend contract = updating test expectations

4. **Tests run in CI**
   - Every PR runs integration tests
   - Merge blocked if tests fail

## Migration Plan

### Phase 1: Infrastructure Setup
- [ ] Create `docker-compose.test.yml`
- [ ] Create test fixture files
- [ ] Create `scripts/wait-for-services.sh`
- [ ] Add CI workflow for integration tests

### Phase 2: Core Integration Tests
- [ ] File upload integration test
- [ ] File parse integration test
- [ ] Data quality assessment test
- [ ] Intent submission test

### Phase 3: Journey Tests
- [ ] Content pillar journey (upload → parse → embed)
- [ ] Insights pillar journey (select → analyze → visualize)
- [ ] Cross-pillar journey (content → insights)

### Phase 4: E2E Tests
- [ ] Login flow
- [ ] File management flow
- [ ] Analysis flow
- [ ] Full user journey

### Phase 5: Retire Mock Tests
- [ ] Identify tests that only test mocks
- [ ] Replace with integration tests or delete
- [ ] Keep only pure unit tests

## Anti-Patterns to Avoid

### ❌ Testing Mocks
```typescript
// BAD: Testing that a mock was called
expect(mockClient.submitIntent).toHaveBeenCalledWith(expectedArgs);
```

### ❌ Asserting on Shapes Only
```typescript
// BAD: Only checking structure exists
expect(result).toHaveProperty('artifacts');
```

### ❌ Ignoring Real Behavior
```typescript
// BAD: Assuming success without verification
const result = await uploadFile(file);
expect(result.success).toBe(true); // OK but not enough
// Missing: verify file actually exists in storage
```

### ✅ Testing Real Outcomes
```typescript
// GOOD: Verify actual behavior
const result = await uploadFile(file);
expect(result.success).toBe(true);

// Verify in storage
const stored = await storage.getFile(result.file_id);
expect(stored.content).toEqual(await file.arrayBuffer());

// Verify in database
const metadata = await db.getFileMetadata(result.file_id);
expect(metadata.filename).toBe(file.name);
```

## Conclusion

Our testing strategy is:
1. **Few unit tests** - Pure logic only
2. **Many integration tests** - Real backend, real files, real validation
3. **Comprehensive E2E tests** - Full user journeys

The goal is that when tests pass, we have **confidence the platform works**, not just that code runs.
