# Strategic Testing Vision

## Core Philosophy

**Tests must prove the platform ACTUALLY WORKS.**

This means:
- Tests use **actual infrastructure** (not mocks)
- Tests process **real files** (not synthetic data)
- Tests validate **real answers** (not just "API responded")

## What We're NOT Testing For

We're NOT just checking:
- "API returns 200 OK"
- "Function doesn't throw"
- "Mock was called with correct args"

These tests pass even when the platform is broken.

## What We ARE Testing For

We ARE proving:
- "Uploaded CSV produces exactly 5 rows with correct values"
- "Parsed JSON contains organization name 'SymphAIny Platform'"
- "Stored file can be retrieved with identical content"
- "Execution status transitions correctly: pending → running → completed"

## Validation Pyramid

```
                    ┌─────────────────┐
                    │   E2E Journey   │  ← User completes full workflow
                    │     Tests       │    Upload → Parse → Analyze → Export
                    └────────┬────────┘
                             │
               ┌─────────────┴─────────────┐
               │   Integration Tests       │  ← Components work together
               │   (Real Infrastructure)   │    File + Storage + Parse = Result
               └─────────────┬─────────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │         Validation Tests            │  ← Outputs are correct
          │   (Expected vs Actual Comparison)   │    Parse result matches expected
          └──────────────────┬──────────────────┘
                             │
    ┌────────────────────────┴────────────────────────┐
    │              Unit Tests (Mocked)                │  ← Logic is correct
    │         (Business logic, transformations)       │    (Still valuable, but not sufficient)
    └─────────────────────────────────────────────────┘
```

## Test Categories

### 1. File Processing Tests (Highest Priority)

**Proves:** The platform can ingest, store, and parse real files.

| Test | Proves |
|------|--------|
| Upload CSV → Parse → Validate columns | CSV parser works correctly |
| Upload JSON → Parse → Validate structure | JSON parser works correctly |
| Upload PDF → Parse → Validate extracted text | PDF parser works correctly |
| Upload binary → Parse with copybook → Validate records | Binary/COBOL parser works |

**Validation approach:**
```python
# Expected output (tests/expected/csv/sample_csv_expected.json)
{
  "total_rows": 5,
  "columns": ["id", "name", "email", "department", "salary"],
  "first_row": {"id": 1, "name": "John Doe", ...}
}

# Test validates against expected
result = await parse_file("sample.csv")
validation = validate_csv_parse(result)
assert validation.is_valid
```

### 2. Storage Verification Tests

**Proves:** Files are actually persisted, not just acknowledged.

| Test | Proves |
|------|--------|
| Upload → Check GCS blob exists | File was stored |
| Upload → Download → Compare bytes | Content preserved |
| Upload → Delete → Verify removed | Deletion works |

### 3. Execution Flow Tests

**Proves:** Intent-based execution works end-to-end.

| Test | Proves |
|------|--------|
| Submit intent → Poll status → Get completed | Execution lifecycle works |
| Execute → Check artifacts present | Results are captured |
| Execute → Verify state in Redis/Arango | State management works |

### 4. Insights/Analytics Tests

**Proves:** Analysis produces meaningful, correct results.

| Test | Proves |
|------|--------|
| Parse CSV → Analyze → Verify statistics | Analytics are calculated correctly |
| Parse JSON → Assess quality → Verify scores | Quality assessment works |
| Parse → Create embeddings → Verify vector | Embedding generation works |

### 5. E2E Journey Tests

**Proves:** Complete user workflows function correctly.

| Journey | Steps Tested |
|---------|--------------|
| Content Journey | Upload → Parse → Store → List → Download |
| Insights Journey | Upload → Parse → Analyze → Visualize |
| Outcomes Journey | Upload → Parse → Create Blueprint → Export |

## Validation Patterns

### Pattern 1: Structural Validation

```python
def validate_structure(result):
    """Verify result has expected structure."""
    errors = []
    if "artifacts" not in result:
        errors.append("Missing artifacts")
    if "status" not in result:
        errors.append("Missing status")
    return errors
```

### Pattern 2: Value Validation

```python
def validate_values(result, expected):
    """Verify result contains expected values."""
    errors = []
    actual_org = result.get("organization")
    expected_org = expected.get("organization")
    if actual_org != expected_org:
        errors.append(f"Organization mismatch: {actual_org} != {expected_org}")
    return errors
```

### Pattern 3: Statistical Validation

```python
def validate_statistics(result, expected):
    """Verify computed statistics are correct."""
    errors = []
    actual_avg = result.get("statistics", {}).get("salary_avg")
    expected_avg = expected.get("statistics", {}).get("salary_avg")
    # Allow small floating point tolerance
    if abs(actual_avg - expected_avg) > 0.01:
        errors.append(f"Average salary mismatch: {actual_avg} != {expected_avg}")
    return errors
```

### Pattern 4: Quality Validation

```python
def validate_quality(result):
    """Verify result meets quality standards."""
    errors = []
    rows = result.get("rows", [])
    
    # Check for null values
    for row in rows:
        for key, value in row.items():
            if value is None:
                errors.append(f"Null value found in {key}")
    
    # Check email format
    email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    for row in rows:
        email = row.get("email", "")
        if email and not email_pattern.match(email):
            errors.append(f"Invalid email: {email}")
    
    return errors
```

## Infrastructure Requirements

### For Integration Tests

```yaml
# docker-compose.test.yml provides:
- redis:6380        # State management
- arango:8530       # Graph database
- consul:8501       # Service discovery
- meilisearch:7701  # Search indexing
- gcs-emulator:9023 # File storage
```

### For E2E Tests (adds)

```yaml
- runtime:8100      # Backend API
- frontend:3100     # Next.js app
```

## CI/CD Strategy

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   PR Check   │───►│  Integration │───►│    E2E       │
│  (All PRs)   │    │   (Main)     │    │  (Deploy)    │
└──────────────┘    └──────────────┘    └──────────────┘
      │                    │                    │
      ▼                    ▼                    ▼
  Unit tests          Integration          Full stack
  Lint checks         + Validation         + Frontend
  Type checks         + Infrastructure     + User flows
```

## Success Criteria

A test suite is successful when:

1. **Test passes = Platform works** - If tests pass, users can trust the platform
2. **Test fails = Real problem** - Failures indicate actual bugs, not flaky tests
3. **Coverage is meaningful** - Tests cover what matters (file processing, not CSS)
4. **Maintenance is low** - Tests don't break on refactors that preserve behavior

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
| Mock everything | Tests pass even when real code is broken | Use real infrastructure |
| Test implementation details | Tests break on refactors | Test behavior/outcomes |
| "API responds 200" | Doesn't verify correctness | Validate response content |
| Synthetic test data | Doesn't catch real-world edge cases | Use representative files |
| Skip flaky tests | Hides real problems | Fix the flakiness |

## Migration Path

### Phase 1: Infrastructure (DONE)
- docker-compose.test.yml with full stack
- wait-for-services.sh script
- CI workflow for integration tests

### Phase 2: Core Validation (DONE)
- Expected outputs for CSV, JSON
- Validation rules module
- File upload/parse integration tests

### Phase 3: Extended Validation
- Add PDF expected outputs
- Add Excel expected outputs
- Add binary/COBOL expected outputs

### Phase 4: Insights Validation
- Add expected outputs for analytics
- Add quality assessment validation
- Add embedding validation

### Phase 5: E2E Journeys
- Content pillar journey tests
- Insights pillar journey tests
- Outcomes pillar journey tests

### Phase 6: Continuous Improvement
- Add performance benchmarks
- Add stress tests for large files
- Add chaos tests for infrastructure failures
