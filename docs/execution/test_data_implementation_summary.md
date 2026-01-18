# Test Data Management Implementation Summary

## Overview

This document summarizes the implementation of test data management for the SymphAIny platform integration tests.

## Implementation Status

### ✅ Completed

1. **Test Data Strategy Document**
   - Created comprehensive strategy for managing test data across all infrastructure
   - Defined cleanup patterns and test isolation strategies
   - Documented file upload testing approach

2. **Test Data Utilities**
   - Created `tests/test_data/test_data_utils.py` with `TestDataSeeder` class
   - Implemented GCS file seeding and cleanup
   - Implemented Supabase record seeding and cleanup
   - Implemented ArangoDB collection cleanup
   - Implemented Meilisearch index cleanup
   - Created convenience functions for realm-specific test data

3. **Sample Test Files**
   - Created `sample.csv` - Sample CSV with employee data
   - Created `sample.json` - Sample JSON with structured data
   - Created `sample.txt` - Sample text file for text processing tests

4. **Enhanced Test Fixtures**
   - Created `tests/infrastructure/test_data_fixtures.py`
   - Implemented `test_data_seeder` fixture
   - Implemented `seeded_content_data` fixture
   - Implemented `seeded_insights_data` fixture
   - Implemented `shared_test_files` fixture for performance

## Architecture

### Test Data Lifecycle

```
1. Test Setup
   ├─ Infrastructure starts (docker-compose)
   ├─ Test fixtures initialize adapters
   ├─ Test data seeder created
   ├─ Cleanup existing test data (if any)
   └─ Seed required test data

2. Test Execution
   ├─ Test runs with seeded data
   └─ Test may create additional data

3. Test Cleanup
   ├─ Delete test-specific data (test/{test_id}/*)
   ├─ Delete test records from Supabase
   ├─ Keep shared test data (test/samples/*)
   └─ Disconnect from infrastructure
```

### Test Data Organization

```
GCS:
  test/
    samples/          # Shared test files (reused across tests)
      sample.csv
      sample.json
      sample.txt
    {test_id}/        # Test-specific files (cleaned up after test)
      sample.csv
      ...

Supabase:
  Tables:
    source_files      # Test records with test_* tenant_id
    parsed_results    # Test records with test_* tenant_id
    embeddings        # Test records with test_* tenant_id
    ...

ArangoDB:
  Collections:
    test_*            # Test collections (cleaned up after test)
```

## Usage Examples

### Example 1: Using Seeded Content Data

```python
@pytest.mark.asyncio
async def test_content_ingest_file(
    seeded_content_data,
    content_realm_setup
):
    """Test content realm with seeded file."""
    file_id = seeded_content_data["file_id"]
    gcs_blob_path = seeded_content_data["gcs_blob_path"]
    
    # Test uses seeded data
    intent = IntentFactory.create_intent(
        intent_type="ingest_file",
        parameters={
            "file_path": gcs_blob_path,
            "file_id": file_id
        }
    )
    
    # Test execution...
```

### Example 2: Using Seeded Insights Data

```python
@pytest.mark.asyncio
async def test_insights_data_quality(
    seeded_insights_data,
    insights_realm_setup
):
    """Test insights realm with seeded data."""
    file_id = seeded_insights_data["file_id"]
    parsed_file_id = seeded_insights_data["parsed_file_id"]
    
    intent = IntentFactory.create_intent(
        intent_type="assess_data_quality",
        parameters={
            "source_file_id": file_id,
            "parsed_file_id": parsed_file_id
        }
    )
    
    # Test execution...
```

### Example 3: Using Test Data Seeder Directly

```python
@pytest.mark.asyncio
async def test_custom_data(
    test_data_seeder
):
    """Test with custom data seeding."""
    # Upload custom file
    blob_path = await test_data_seeder.upload_test_file(
        "sample.csv",
        test_id="custom_test"
    )
    
    # Seed Supabase record
    file_id = await test_data_seeder.seed_source_file(
        file_id="custom_file_123",
        gcs_blob_path=blob_path
    )
    
    # Test execution...
    
    # Cleanup (automatic via fixture, but can be manual)
    await test_data_seeder.cleanup_test_files("custom_test")
```

## Next Steps

### Phase 1: Update Realm Tests (Immediate)

1. **Update Content Realm Tests**
   - Use `seeded_content_data` fixture
   - Remove hardcoded test file IDs
   - Test actual file upload and processing

2. **Update Insights Realm Tests**
   - Use `seeded_insights_data` fixture
   - Provide real `source_file_id` and `parsed_file_id`
   - Test actual data quality assessment

3. **Update Journey Realm Tests**
   - Seed workflow/SOP test data if needed
   - Test visual generation with real data

4. **Update Outcomes Realm Tests**
   - Seed outcome synthesis test data if needed
   - Test visual generation with real data

### Phase 2: Verify All Tests Pass

1. Run all realm tests
2. Verify all 9 skipped tests now pass
3. Document any remaining issues

### Phase 3: Enhancements (Future)

1. Add more sample files (PDF, Excel, etc.)
2. Create realm-specific seed functions
3. Add performance testing with large files
4. Add stress testing with multiple concurrent uploads

## Files Created

1. `docs/execution/test_data_management_strategy.md` - Strategy document
2. `tests/test_data/__init__.py` - Package init
3. `tests/test_data/test_data_utils.py` - Test data utilities
4. `tests/test_data/files/sample.csv` - Sample CSV file
5. `tests/test_data/files/sample.json` - Sample JSON file
6. `tests/test_data/files/sample.txt` - Sample text file
7. `tests/infrastructure/test_data_fixtures.py` - Enhanced test fixtures
8. `docs/execution/test_data_implementation_summary.md` - This document

## Key Design Decisions

1. **Test Isolation**: Each test gets its own data with unique test_id
2. **Shared Data**: Common files in `test/samples/` for performance
3. **Automatic Cleanup**: Fixtures handle cleanup automatically
4. **Flexible Seeding**: Both convenience functions and direct seeder access
5. **Infrastructure Agnostic**: Works with all adapters (GCS, Supabase, ArangoDB, Meilisearch)

## Testing the Implementation

To test the implementation:

```bash
# Run content realm tests with seeded data
pytest tests/integration/realms/test_content_realm.py -v

# Run insights realm tests with seeded data
pytest tests/integration/realms/test_insights_realm.py -v

# Run all realm tests
pytest tests/integration/realms/ -v
```

## Questions Answered

### Q1: How should we handle test data in GCS and Arango?

**Answer**: 
- **GCS**: Use test-specific prefixes (`test/{test_id}/`) for isolation, with shared files in `test/samples/` for performance. Cleanup deletes test-specific files after each test.
- **ArangoDB**: Use test database (`symphainy_platform_test`) with collection cleanup. Test collections are deleted after each test.
- **Supabase**: Use test-specific `tenant_id` and `session_id` for isolation. Cleanup deletes test records after each test.
- **Redis**: Already handled by `test_redis` fixture (flushes DB before/after).
- **Meilisearch**: Use `test_` prefix for indexes, cleanup deletes test indexes after each test.

### Q2: How can we seed the platform with test files?

**Answer**:
- Created `TestDataSeeder` class with methods to upload files to GCS and seed records in Supabase
- Created sample test files (CSV, JSON, TXT) in `tests/test_data/files/`
- Created convenience fixtures (`seeded_content_data`, `seeded_insights_data`) that automatically seed and clean up
- Created `shared_test_files` fixture for performance (uploads once per session)
- Tests can use these fixtures to get pre-seeded data, or use the seeder directly for custom data
