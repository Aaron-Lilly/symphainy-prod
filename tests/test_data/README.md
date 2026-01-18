# Test Data Files

This directory contains test files aligned with platform use cases for comprehensive integration testing.

## File Inventory

### Structured Data Files

#### `sample.csv`
- **Type**: CSV
- **Content**: Employee data (id, name, email, department, salary)
- **Use Case**: General structured data parsing
- **Parser**: CSV Parser

#### `sample.json`
- **Type**: JSON
- **Content**: Organization and employee data
- **Use Case**: Structured JSON parsing
- **Parser**: JSON Parser

#### `variable_life_insurance_policy.xlsx`
- **Type**: Excel (XLSX)
- **Content**: Variable life insurance policy data with multiple sheets
  - Policy Details sheet: Policy numbers, insured names, face amounts, premiums, cash values, beneficiaries
  - Variable Accounts sheet: Investment allocations and options
- **Use Case**: Insurance use case - Variable life insurance policy data
- **Parser**: Excel Parser

### Document Files

#### `permit_oil_gas.pdf`
- **Type**: PDF (Structured)
- **Content**: Oil and gas permit application with:
  - Permit number, applicant, location
  - Permit requirements (drilling, environmental, water usage, fracking, reporting)
  - Compliance dates
- **Use Case**: Permit Data Extraction (Use Case 2) - Oil & Gas company permit processing
- **Parser**: PDF Parser (Structured extraction)

#### `aar_after_action_report.pdf`
- **Type**: PDF (Unstructured)
- **Content**: After Action Report (AAR) with:
  - Test event information
  - Test objectives and results
  - Key findings and recommendations
- **Use Case**: Testing & Evaluation (Use Case 1) - AAR Analysis
- **Parser**: PDF Parser (Unstructured text extraction)

#### `insurance_policy_documentation.docx`
- **Type**: DOCX (Word Document)
- **Content**: Insurance policy documentation with:
  - Policy information
  - Coverage details
  - Beneficiary information
  - Terms and conditions
- **Use Case**: General document processing
- **Parser**: Word Parser

### Workflow Files

#### `workflow_data_migration.bpmn`
- **Type**: BPMN (Business Process Model and Notation)
- **Content**: Insurance policy data migration workflow
  - Extract source data
  - Validate data quality
  - Transform data format
  - Load to target system
  - Verify migration success
- **Use Case**: Insurance Migration (Use Case 3) - Data migration workflow
- **Parser**: Workflow Parser / BPMN Parser

#### `workflow_beneficiary_change.bpmn`
- **Type**: BPMN
- **Content**: Life insurance beneficiary change workflow
  - Verify policy status
  - Validate new beneficiary
  - Update beneficiary record
  - Send confirmation
- **Use Case**: Insurance use case - Beneficiary change workflow
- **Parser**: Workflow Parser / BPMN Parser

### Binary Files (Mainframe)

#### `insurance_policy_ascii.bin`
- **Type**: Binary (ASCII-encoded)
- **Content**: Fixed-length insurance policy records
- **Structure**: Matches `copybook_insurance_ascii.txt`
- **Use Case**: Insurance Migration (Use Case 3) - Mainframe binary file parsing with ASCII encoding
- **Parser**: Binary Parser with Copybook

#### `insurance_policy_ebcdic.bin`
- **Type**: Binary (EBCDIC-encoded)
- **Content**: Fixed-length insurance policy records
- **Structure**: Matches `copybook_insurance_ebcdic.txt`
- **Use Case**: Insurance Migration (Use Case 3) - Mainframe binary file parsing with EBCDIC encoding
- **Parser**: Binary Parser with Copybook

#### `copybook_insurance_ascii.txt`
- **Type**: Text (Copybook definition)
- **Content**: COBOL copybook for ASCII binary files
- **Fields**: Policy number, insured name, DOB, policy type, face amount, premium, cash value, beneficiary, status, dates
- **Use Case**: Insurance Migration - Copybook reference for ASCII binary parsing

#### `copybook_insurance_ebcdic.txt`
- **Type**: Text (Copybook definition)
- **Content**: COBOL copybook for EBCDIC binary files
- **Fields**: Same as ASCII copybook with EBCDIC encoding marker
- **Use Case**: Insurance Migration - Copybook reference for EBCDIC binary parsing

### Image Files

#### `test_document.jpg`
- **Type**: JPEG Image
- **Content**: Test document image with:
  - Text content (policy information)
  - Shapes and lines
  - OCR-testable content
- **Use Case**: Image parsing and OCR testing
- **Parser**: Image Parser / OCR

#### `test_document.png`
- **Type**: PNG Image
- **Content**: Same as JPG version
- **Use Case**: Image parsing and OCR testing
- **Parser**: Image Parser / OCR

### Text Files

#### `sample.txt`
- **Type**: Plain Text
- **Content**: General text document for text processing
- **Use Case**: General text parsing
- **Parser**: Text Parser

## Use Case Mapping

### Use Case 1: Testing & Evaluation Enablement
- **Files**: `aar_after_action_report.pdf`
- **Purpose**: Extract insights from AAR documents

### Use Case 2: Permit Data Extraction
- **Files**: `permit_oil_gas.pdf`
- **Purpose**: Extract permit data and map to templates

### Use Case 3: Insurance Migration
- **Files**: 
  - `variable_life_insurance_policy.xlsx`
  - `insurance_policy_ascii.bin` + `copybook_insurance_ascii.txt`
  - `insurance_policy_ebcdic.bin` + `copybook_insurance_ebcdic.txt`
  - `workflow_data_migration.bpmn`
- **Purpose**: Parse binary files with copybooks, design migration workflows

### Insurance Use Cases (General)
- **Files**:
  - `variable_life_insurance_policy.xlsx`
  - `insurance_policy_documentation.docx`
  - `workflow_beneficiary_change.bpmn`
- **Purpose**: Test insurance-specific parsing and workflows

## Parser Coverage

This test data set covers all parsing utilities:

1. **Structured Parsers**:
   - ✅ CSV Parser (`sample.csv`)
   - ✅ JSON Parser (`sample.json`)
   - ✅ Excel Parser (`variable_life_insurance_policy.xlsx`)
   - ✅ Binary Parser (`insurance_policy_ascii.bin`, `insurance_policy_ebcdic.bin`)

2. **Unstructured Parsers**:
   - ✅ PDF Parser (`permit_oil_gas.pdf`, `aar_after_action_report.pdf`)
   - ✅ Word Parser (`insurance_policy_documentation.docx`)
   - ✅ Text Parser (`sample.txt`)
   - ✅ Image Parser (`test_document.jpg`, `test_document.png`)

3. **Workflow Parsers**:
   - ✅ BPMN Parser (`workflow_data_migration.bpmn`, `workflow_beneficiary_change.bpmn`)

4. **Hybrid Parsers**:
   - ✅ Structured PDF extraction (`permit_oil_gas.pdf`)
   - ✅ Unstructured PDF extraction (`aar_after_action_report.pdf`)

## Usage in Tests

### Example: Seeding Content Realm Test Data

```python
from tests.test_data.test_data_utils import TestDataSeeder

seeder = TestDataSeeder(gcs_adapter=test_gcs, supabase_adapter=test_supabase)

# Upload permit PDF
blob_path = await seeder.upload_sample_file("permit_oil_gas.pdf")

# Seed source file record
file_id = await seeder.seed_source_file(
    file_id="permit_001",
    gcs_blob_path=blob_path,
    file_type="application/pdf"
)
```

### Example: Seeding Insurance Test Data

```python
# Upload Excel policy file
blob_path = await seeder.upload_sample_file("variable_life_insurance_policy.xlsx")

# Upload binary file with copybook
binary_path = await seeder.upload_sample_file("insurance_policy_ascii.bin")
copybook_path = await seeder.upload_sample_file("copybook_insurance_ascii.txt")
```

## File Naming Conventions

- **Use case prefix**: Files aligned with specific use cases have descriptive names (e.g., `permit_`, `aar_`, `insurance_`)
- **Type suffix**: File extensions indicate parser type
- **Copybook files**: Named to match their corresponding binary files

## Maintenance

When adding new test files:
1. Add file to `tests/test_data/files/`
2. Update this README with file description
3. Update `test_data_utils.py` content_type_map if new file type
4. Document use case mapping
5. Verify parser coverage
