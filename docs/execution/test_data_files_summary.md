# Test Data Files Summary

## Overview

Comprehensive test data files have been created aligned with platform use cases, covering all parsing utilities and scenarios.

## Files Created

### ✅ Use Case-Aligned Files

1. **Permit PDF** (`permit_oil_gas.pdf`)
   - Oil & gas permit application
   - Structured data extraction use case
   - Requirements, compliance dates, permit details

2. **After Action Report PDF** (`aar_after_action_report.pdf`)
   - Testing & Evaluation use case
   - Unstructured text extraction
   - Test objectives, results, findings, recommendations

3. **Variable Life Insurance Policy Excel** (`variable_life_insurance_policy.xlsx`)
   - Insurance use case
   - Multiple sheets (Policy Details, Variable Accounts)
   - Policy numbers, premiums, cash values, beneficiaries

4. **Mainframe Binary Files**:
   - `insurance_policy_ascii.bin` - ASCII-encoded binary
   - `insurance_policy_ebcdic.bin` - EBCDIC-encoded binary
   - `copybook_insurance_ascii.txt` - ASCII copybook definition
   - `copybook_insurance_ebcdic.txt` - EBCDIC copybook definition
   - Insurance migration use case
   - Fixed-length record structure

5. **BPMN Workflow Files**:
   - `workflow_data_migration.bpmn` - Data migration workflow
   - `workflow_beneficiary_change.bpmn` - Beneficiary change workflow
   - Insurance use cases
   - Process definitions with tasks, gateways, flows

6. **DOCX File** (`insurance_policy_documentation.docx`)
   - Insurance policy documentation
   - Policy information, coverage, terms

7. **Image Files**:
   - `test_document.jpg` - JPEG image with text and shapes
   - `test_document.png` - PNG image with text and shapes
   - OCR testing content

### ✅ Existing Files (Updated)

- `sample.csv` - Employee data
- `sample.json` - Structured JSON
- `sample.txt` - Plain text

## Parser Coverage

### Structured Parsers ✅
- CSV Parser: `sample.csv`
- JSON Parser: `sample.json`
- Excel Parser: `variable_life_insurance_policy.xlsx`
- Binary Parser: `insurance_policy_ascii.bin`, `insurance_policy_ebcdic.bin` (with copybooks)

### Unstructured Parsers ✅
- PDF Parser (Structured): `permit_oil_gas.pdf`
- PDF Parser (Unstructured): `aar_after_action_report.pdf`
- Word Parser: `insurance_policy_documentation.docx`
- Text Parser: `sample.txt`
- Image Parser: `test_document.jpg`, `test_document.png`

### Workflow Parsers ✅
- BPMN Parser: `workflow_data_migration.bpmn`, `workflow_beneficiary_change.bpmn`

## Use Case Alignment

### Use Case 1: Testing & Evaluation Enablement
- **File**: `aar_after_action_report.pdf`
- **Purpose**: Extract metrics, gaps, outcomes from AARs

### Use Case 2: Permit Data Extraction
- **File**: `permit_oil_gas.pdf`
- **Purpose**: Extract permit data, map to templates

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

## File Type Support

Updated `test_data_utils.py` to support:
- ✅ CSV, JSON, TXT (existing)
- ✅ PDF (structured and unstructured)
- ✅ Excel (XLSX, XLS)
- ✅ DOCX, DOC
- ✅ BPMN (XML)
- ✅ Images (JPG, JPEG, PNG, GIF)
- ✅ Binary (BIN) with copybook support

## Next Steps

1. ✅ All test files created
2. ✅ Test data utilities updated
3. ⏭️ Update realm tests to use new test files
4. ⏭️ Verify all parsers work with test files
5. ⏭️ Run integration tests with seeded data

## File Locations

- Test files: `tests/test_data/files/`
- Test utilities: `tests/test_data/test_data_utils.py`
- Documentation: `tests/test_data/README.md`
