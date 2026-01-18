# Realm Tests Updated with Test Data

## Overview

All realm integration tests have been updated to use the new test data files and fixtures, enabling comprehensive testing with real file uploads and seeded data.

## Updates Made

### Content Realm Tests (`test_content_realm.py`)

#### ✅ Updated Tests

1. **`test_content_realm_intent_handling`**
   - Now uses `seeded_content_data` fixture
   - Tests with real CSV file from GCS
   - Uses actual file_id and gcs_blob_path

2. **`test_content_realm_execution_flow`**
   - Now uses `test_data_seeder` to upload permit PDF
   - Tests full execution flow with permit file (Use Case 2)
   - Seeds source file record in Supabase
   - Includes cleanup after test

3. **`test_lineage_tracking_parsed_results`** & **`test_lineage_tracking_embeddings`**
   - Updated to use `public_works` from setup
   - Ensures realm has access to Supabase for lineage tracking

#### ✅ New Tests Added

4. **`test_parse_pdf_permit`**
   - Tests parsing permit PDF file (Use Case 2: Permit Data Extraction)
   - Uploads `permit_oil_gas.pdf` to GCS
   - Seeds source file record
   - Tests full ingest_file intent flow

5. **`test_parse_excel_insurance`**
   - Tests parsing Excel insurance policy file (Use Case 3: Insurance Migration)
   - Uploads `variable_life_insurance_policy.xlsx` to GCS
   - Seeds source file record
   - Tests Excel parsing capabilities

#### 🔧 Fixture Updates

- `content_realm_setup` now includes `test_public_works`
- Added imports for `test_gcs`, `test_supabase`, `test_public_works`
- Added imports for `test_data_seeder`, `seeded_content_data`

### Insights Realm Tests (`test_insights_realm.py`)

#### ✅ Updated Tests

1. **`test_phase1_data_quality_intent`**
   - Now uses `seeded_insights_data` fixture
   - Uses real `source_file_id` and `parsed_file_id` from seeded data
   - Tests data quality assessment with actual file data

2. **`test_phase2_self_discovery_intent`**
   - Now uses `seeded_insights_data` fixture
   - Uses real `file_id` and `parsed_result_id`
   - Tests semantic self-discovery with actual data

3. **`test_phase2_guided_discovery_intent`**
   - Now uses `seeded_insights_data` fixture
   - Uses real file IDs from seeded data
   - Tests guided discovery with actual data

#### 🔧 Fixture Updates

- All tests now use `public_works` from setup
- Added imports for `seeded_insights_data`, `test_data_seeder`

### Journey Realm Tests (`test_journey_realm.py`)

#### ✅ Updated Tests

1. **`test_create_workflow_with_visual`**
   - Now uses `test_data_seeder` to upload BPMN workflow file
   - Tests with `workflow_data_migration.bpmn` (Use Case 3: Insurance Migration)
   - Uploads workflow file to GCS
   - Tests workflow creation with visual generation
   - Includes cleanup after test

2. **`test_generate_sop_with_visual`**
   - Now uses `test_data_seeder` to upload BPMN workflow file
   - Tests with `workflow_beneficiary_change.bpmn` (Insurance use case)
   - First creates workflow from BPMN, then generates SOP
   - Tests SOP generation with visual generation
   - Includes cleanup after test

#### 🔧 Fixture Updates

- `journey_realm_setup` now includes `test_public_works`
- Added imports for `test_public_works`, `test_data_seeder`

## Test Data Files Used

### Content Realm
- `sample.csv` - Via `seeded_content_data` fixture
- `permit_oil_gas.pdf` - Permit data extraction use case
- `variable_life_insurance_policy.xlsx` - Insurance migration use case

### Insights Realm
- `sample.csv` - Via `seeded_insights_data` fixture (includes parsed results)

### Journey Realm
- `workflow_data_migration.bpmn` - Data migration workflow
- `workflow_beneficiary_change.bpmn` - Beneficiary change workflow

## Benefits

1. **Real File Testing**: Tests now use actual files uploaded to GCS
2. **Seeded Data**: Tests use pre-seeded data in Supabase for realistic scenarios
3. **Use Case Alignment**: Test files align with platform use cases
4. **Comprehensive Coverage**: Tests cover multiple file types (PDF, Excel, BPMN, CSV)
5. **Automatic Cleanup**: All tests clean up test data after execution
6. **No Hardcoded IDs**: Tests use real file IDs from seeded data

## Test Execution

### Running Updated Tests

```bash
# Run Content Realm tests
pytest tests/integration/realms/test_content_realm.py -v

# Run Insights Realm tests
pytest tests/integration/realms/test_insights_realm.py -v

# Run Journey Realm tests
pytest tests/integration/realms/test_journey_realm.py -v

# Run all realm tests
pytest tests/integration/realms/ -v
```

### Expected Results

- Tests should now pass with real file data
- Previously skipped tests should now run
- Tests verify actual file parsing and processing
- Lineage tracking tests verify Supabase integration

## Next Steps

1. ✅ All realm tests updated
2. ⏭️ Run tests to verify they work with seeded data
3. ⏭️ Add more test cases for other file types (binary, images, DOCX)
4. ⏭️ Update Outcomes Realm tests if needed

## Files Modified

- `tests/integration/realms/test_content_realm.py`
- `tests/integration/realms/test_insights_realm.py`
- `tests/integration/realms/test_journey_realm.py`

## Dependencies

- `tests/infrastructure/test_data_fixtures.py` - Test data fixtures
- `tests/test_data/test_data_utils.py` - Test data utilities
- `tests/test_data/files/*` - Test data files
