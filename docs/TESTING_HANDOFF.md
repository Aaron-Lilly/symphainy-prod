# Integration Testing Handoff

This document explains how to run integration tests that prove the platform **actually works**.

## Philosophy

Our testing approach prioritizes:
1. **Real infrastructure** - Tests run against actual services (Redis, ArangoDB, GCS emulator)
2. **Real files** - Tests use actual CSV, JSON, PDF files from `tests/test_data/files/`
3. **Real validation** - Tests compare outputs against expected results, not just "API responded"

**Goal:** Tests fail if the platform produces wrong results, not just if services are down.

## Quick Start

### Option 1: Full Docker Stack (Recommended)

```bash
# Run all integration tests with Docker
./scripts/run_integration_tests_docker.sh

# Keep infrastructure running after tests for debugging
./scripts/run_integration_tests_docker.sh --keep-up

# Include runtime backend tests
./scripts/run_integration_tests_docker.sh --runtime

# Run full E2E tests (includes frontend)
./scripts/run_integration_tests_docker.sh --e2e --verbose
```

### Option 2: Manual Docker Compose

```bash
# Start infrastructure only
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be ready
./scripts/wait-for-services.sh --infra

# Run tests
pytest tests/integration/ -v -m integration

# Cleanup
docker-compose -f docker-compose.test.yml down -v
```

### Option 3: CI/CD

Integration tests run automatically on:
- Push to `main` or `develop`
- Pull requests targeting `main` or `develop`

See `.github/workflows/integration-tests.yml` for configuration.

## Test Infrastructure

### Services (docker-compose.test.yml)

| Service | Test Port | Purpose |
|---------|-----------|---------|
| Redis | 6380 | State management, caching |
| ArangoDB | 8530 | Graph database |
| Consul | 8501 | Service discovery |
| Meilisearch | 7701 | Search indexing |
| GCS Emulator | 9023 | File storage (fake-gcs-server) |
| Runtime | 8100 | Backend API (optional) |
| Frontend | 3100 | Next.js app (optional, E2E only) |

### Test Ports vs Production Ports

Test infrastructure uses different ports to avoid conflicts:
- Production Redis: 6379 → Test: 6380
- Production ArangoDB: 8529 → Test: 8530
- Production Runtime: 8000 → Test: 8100

## Test Categories

### Integration Tests (`tests/integration/`)

Test platform components with real infrastructure:

```bash
# Run all integration tests
pytest tests/integration/ -v -m integration

# Run specific test file
pytest tests/integration/test_file_upload_parse_flow.py -v
```

**Key test file:** `test_file_upload_parse_flow.py`
- `test_csv_upload_and_parse_produces_expected_output` - Proves CSV parsing works
- `test_json_upload_and_parse_produces_expected_output` - Proves JSON parsing works
- `test_uploaded_file_exists_in_storage` - Proves files are persisted

### E2E Tests (`tests/e2e/`)

Full stack tests with frontend + backend:

```bash
# Requires --e2e flag to start frontend
./scripts/run_integration_tests_docker.sh --e2e
```

### Infrastructure Tests (`tests/infrastructure/`)

Test individual infrastructure adapters:

```bash
pytest tests/infrastructure/ -v -m infrastructure
```

## Validation Framework

### Expected Outputs (`tests/expected/`)

Expected outputs define what correct parsing results look like:

```
tests/expected/
├── csv/
│   └── sample_csv_expected.json    # Expected output for sample.csv
├── json/
│   └── sample_json_expected.json   # Expected output for sample.json
├── validation_rules.py              # Validation functions
└── README.md
```

### Using Validators in Tests

```python
from tests.expected.validation_rules import (
    validate_csv_parse,
    validate_file_upload,
    validate_upload_and_parse_flow,
)

# Validate CSV parsing result
csv_validation = validate_csv_parse(parse_result, "sample.csv")
assert csv_validation.is_valid, f"Errors: {csv_validation.errors}"

# Validate complete flow
flow_validation = validate_upload_and_parse_flow(
    upload_result=upload_result,
    parse_result=parse_result,
    file_name="sample.csv",
    file_type="text/csv",
)
assert flow_validation.is_valid, f"Flow failed: {flow_validation.errors}"
```

### Validation Checks

**Structural validation:**
- Required fields exist
- Field types match
- Record counts match

**Semantic validation:**
- Known values extracted correctly
- Calculations (totals, averages) correct
- Relationships between fields coherent

**Quality validation:**
- No missing required fields
- Values within expected ranges
- Email formats valid

## Test Data

### Location: `tests/test_data/files/`

| File | Type | Purpose |
|------|------|---------|
| sample.csv | CSV | Employee data (5 rows, 5 columns) |
| sample.json | JSON | Organization with employees |
| permit_oil_gas.pdf | PDF | Permit extraction test |
| variable_life_insurance_policy.xlsx | Excel | Insurance data test |
| insurance_policy_ascii.bin | Binary | Mainframe file test |

### Adding New Test Files

1. Add file to `tests/test_data/files/`
2. Create expected output in `tests/expected/{type}/`
3. Add validation function to `validation_rules.py`
4. Update `tests/test_data/README.md`

## Environment Variables

```bash
# Infrastructure ports
TEST_REDIS_PORT=6380
TEST_ARANGO_PORT=8530
TEST_CONSUL_PORT=8501
TEST_MEILISEARCH_PORT=7701
TEST_GCS_EMULATOR_PORT=9023

# Runtime port (when running --runtime)
TEST_RUNTIME_PORT=8100

# Frontend port (when running --e2e)
TEST_FRONTEND_PORT=3100

# Credentials
TEST_ARANGO_ROOT_PASSWORD=test_password
TEST_MEILISEARCH_MASTER_KEY=test_master_key

# GCS emulator
STORAGE_EMULATOR_HOST=http://localhost:9023
```

## Troubleshooting

### Services Not Starting

```bash
# Check service status
docker-compose -f docker-compose.test.yml ps

# View logs
docker-compose -f docker-compose.test.yml logs redis
docker-compose -f docker-compose.test.yml logs arango
docker-compose -f docker-compose.test.yml logs runtime
```

### Tests Timing Out

```bash
# Increase wait timeout
MAX_RETRIES=120 ./scripts/wait-for-services.sh --infra
```

### Port Conflicts

```bash
# Check what's using the port
lsof -i :6380

# Use different ports
TEST_REDIS_PORT=6381 docker-compose -f docker-compose.test.yml up -d
```

### GCS Bucket Issues

```bash
# Create test bucket manually
curl -X POST "http://localhost:9023/storage/v1/b?project=test-project" \
  -H "Content-Type: application/json" \
  -d '{"name": "symphainy-test-bucket"}'
```

## CI/CD Integration

GitHub Actions workflow (`.github/workflows/integration-tests.yml`):

1. **integration-tests** job: Runs on every PR/push
   - Starts infrastructure services
   - Runs `tests/integration/` tests
   - Runs `tests/infrastructure/` tests

2. **e2e-tests** job: Runs only on main branch
   - Builds runtime container
   - Starts full stack
   - Runs `tests/e2e/` tests

3. **validation-tests** job: Validates expected output files

## What This Proves

When integration tests pass, it proves:

1. **File Upload Works** - Files are stored in GCS and can be retrieved
2. **File Parsing Works** - Parsers produce correct structured data
3. **State Management Works** - Redis/ArangoDB correctly store execution state
4. **Execution Flow Works** - Intent → Execute → Artifacts pipeline functions
5. **Output Quality** - Parsed data matches expected values (not just structure)

## Next Steps

1. **Add more expected outputs** for PDF, Excel, binary files
2. **Add semantic validators** for insights/analytics results
3. **Add E2E journey tests** for complete user flows
4. **Add performance benchmarks** for parsing large files
