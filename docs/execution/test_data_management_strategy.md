# Test Data Management Strategy

## Overview

This document outlines the strategy for managing test data across all platform infrastructure (GCS, ArangoDB, Supabase, Redis, Meilisearch) to enable comprehensive integration testing.

## Key Principles

1. **Test Isolation**: Each test should have clean, predictable data
2. **Test Data Separation**: Test data should be clearly separated from production data
3. **Automatic Cleanup**: Tests should clean up after themselves
4. **Reproducible Seeds**: Test data should be seedable and reproducible
5. **Performance**: Cleanup should be fast and not slow down test execution

## Infrastructure-Specific Strategies

### 1. GCS (Google Cloud Storage)

**Strategy**: Use test-specific bucket prefixes and cleanup after tests

- **Test Bucket**: `symphainy-test-bucket` (already configured)
- **Test Prefix**: `test/` prefix for all test files
- **Cleanup**: Delete all blobs with `test/` prefix after each test
- **Seeding**: Upload sample files to `test/samples/` for reusable test data

**Implementation**:
- Test fixtures create files under `test/{test_name}/` for isolation
- After test, delete all blobs matching `test/{test_name}/*`
- Keep `test/samples/` for shared test data (CSV, JSON, PDF, etc.)

### 2. ArangoDB

**Strategy**: Use test database with collection cleanup

- **Test Database**: `symphainy_platform_test` (already configured)
- **Collection Prefix**: No prefix needed (test database is isolated)
- **Cleanup**: Delete test collections after each test
- **Seeding**: Create test collections with sample data

**Implementation**:
- Test fixtures clean collections before/after tests
- Use `clean_test_db` fixture for automatic cleanup
- Seed collections with minimal required data for each test

### 3. Supabase

**Strategy**: Use test project with row-level cleanup

- **Test Project**: Hosted test Supabase project (already configured)
- **Table Isolation**: Use `tenant_id` and `session_id` for test isolation
- **Cleanup**: Delete test rows after each test
- **Seeding**: Insert test records with known IDs

**Implementation**:
- Use test-specific `tenant_id` and `session_id` prefixes
- Clean up test rows after each test using these identifiers
- Seed tables with minimal required data (parsed_results, embeddings, etc.)

### 4. Redis

**Strategy**: Use test database with flush

- **Test Database**: DB 15 (already configured)
- **Cleanup**: `FLUSHDB` before and after each test
- **Seeding**: Set test keys as needed

**Implementation**:
- `test_redis` fixture already flushes DB before/after
- No additional cleanup needed

### 5. Meilisearch

**Strategy**: Use test indexes with cleanup

- **Index Prefix**: `test_` prefix for all test indexes
- **Cleanup**: Delete test indexes after each test
- **Seeding**: Create test indexes with sample documents

**Implementation**:
- Create indexes with `test_` prefix
- Delete indexes matching `test_*` after each test

## Test Data Seeding

### Seed Files Location

```
tests/
  test_data/
    files/
      sample.csv          # Sample CSV file
      sample.json         # Sample JSON file
      sample.pdf          # Sample PDF file
      sample.txt          # Sample text file
    seeds/
      content_seed.py     # Content realm test data
      insights_seed.py    # Insights realm test data
      journey_seed.py     # Journey realm test data
      outcomes_seed.py    # Outcomes realm test data
```

### Seeding Strategy

1. **Shared Test Data**: Upload common files (CSV, JSON, PDF) to GCS `test/samples/`
2. **Test-Specific Data**: Create data as needed in each test
3. **Fixture-Based Seeding**: Use pytest fixtures to seed data before tests

## Implementation Plan

### Phase 1: Test Data Utilities
- [x] Create `tests/test_data/` directory structure
- [ ] Create test data seeding utilities
- [ ] Create sample test files (CSV, JSON, PDF, TXT)
- [ ] Create cleanup utilities for each infrastructure

### Phase 2: Test Fixtures Enhancement
- [ ] Enhance `test_gcs` fixture with cleanup
- [ ] Enhance `test_arango` fixture with collection cleanup
- [ ] Create `test_supabase` cleanup utilities
- [ ] Create `test_meilisearch` cleanup utilities

### Phase 3: Test Data Seeds
- [ ] Create content realm test data seeds
- [ ] Create insights realm test data seeds
- [ ] Create journey realm test data seeds
- [ ] Create outcomes realm test data seeds

### Phase 4: Integration
- [ ] Update realm tests to use seeded data
- [ ] Verify all 9 skipped tests can run
- [ ] Document test data requirements

## Test Data Lifecycle

```
1. Test Setup
   ├─ Infrastructure starts (docker-compose)
   ├─ Test fixtures initialize
   ├─ Cleanup existing test data
   └─ Seed required test data

2. Test Execution
   ├─ Test runs with seeded data
   └─ Test may create additional data

3. Test Cleanup
   ├─ Delete test-specific data
   ├─ Keep shared test data (test/samples/)
   └─ Disconnect from infrastructure
```

## File Upload Testing

### Sample Files Needed

1. **CSV File** (`sample.csv`): Simple CSV with headers and data rows
2. **JSON File** (`sample.json`): Structured JSON data
3. **PDF File** (`sample.pdf`): Sample PDF document
4. **Text File** (`sample.txt`): Plain text file

### Upload Flow Testing

1. Upload file to GCS `test/samples/`
2. Create file record in Supabase `source_files` table
3. Trigger content realm `ingest_file` intent
4. Verify parsed result in Supabase `parsed_results` table
5. Verify embeddings in Supabase `embeddings` table
6. Test lineage tracking

## Cleanup Patterns

### Pattern 1: Test-Specific Cleanup (Recommended)
```python
@pytest.fixture
async def test_with_data(test_gcs, test_supabase):
    # Setup: Create test data
    test_file_id = await seed_test_file(test_gcs, test_supabase)
    
    yield test_file_id
    
    # Cleanup: Delete test data
    await cleanup_test_file(test_gcs, test_supabase, test_file_id)
```

### Pattern 2: Shared Test Data (For Performance)
```python
@pytest.fixture(scope="session")
async def shared_test_data(test_gcs):
    # Upload once per test session
    file_id = await upload_sample_file(test_gcs, "test/samples/sample.csv")
    yield file_id
    # Don't cleanup - reuse across tests
```

## Next Steps

1. Create test data utilities module
2. Create sample test files
3. Implement cleanup utilities
4. Update test fixtures
5. Seed test data for realm tests
6. Run and verify all tests pass
