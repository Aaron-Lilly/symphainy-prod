# Modular Parsing Test Plan

## Overview

This document outlines the modular approach to building comprehensive parsing tests for the two-phase materialization flow.

---

## Modular Structure

### Benefits
1. **Small, focused files** - Each test is ~150-200 lines
2. **One file type per test** - Clear separation of concerns
3. **Reusable base class** - Common functionality in `BaseCapabilityTest`
4. **Easy to extend** - Add new file types without modifying existing tests
5. **Consistent pattern** - All tests follow the same flow

---

## Test Organization

```
file_parsing/
├── README.md                          # Overview and patterns
├── MODULAR_TESTING_PLAN.md           # This file
├── test_csv_parsing.py                # ✅ CSV parsing (updated)
├── test_json_parsing.py               # ✅ JSON parsing (needs update)
├── test_pdf_parsing.py                # 📋 PDF parsing (to create)
├── test_excel_parsing.py              # 📋 Excel parsing (to create)
├── test_text_parsing.py                # 📋 Text parsing (to create)
├── test_binary_parsing.py              # 📋 Binary parsing (to create)
├── test_image_parsing.py               # 📋 Image parsing (to create)
└── test_bpmn_parsing.py                # 📋 BPMN parsing (to create)
```

---

## Standard Test Pattern

Every parsing test follows this pattern:

### 1. Setup
```python
class TestYourFileTypeParsing(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Your File Type Parsing - Two-Phase Flow",
            test_id_prefix="parse_<type>"
        )
```

### 2. Test Flow
```python
async def run_test(self) -> bool:
    # Step 1: Authenticate
    if not await self.authenticate():
        return False
    
    # Step 2: Phase 1 - Upload file
    upload_status = await self.submit_intent_and_poll(
        intent_type="ingest_file",
        parameters={...}
    )
    
    # Extract IDs
    file_artifact = upload_status["artifacts"]["file"]
    semantic_payload = file_artifact["semantic_payload"]
    boundary_contract_id = semantic_payload["boundary_contract_id"]
    file_id = semantic_payload["file_id"]
    
    # Step 3: Phase 2 - Save file (REQUIRED)
    if not await self.save_materialization(boundary_contract_id, file_id):
        return False
    
    # Step 4: Phase 3 - Parse file
    parse_status = await self.submit_intent_and_poll(
        intent_type="parse_content",
        parameters={
            "file_id": file_id,
            "file_reference": semantic_payload.get("file_reference"),
            "parse_options": {...}
        }
    )
    
    # Step 5: Validate parsed content
    # ... validation logic ...
    
    return True
```

---

## Test Files to Create

### Priority 1: Core File Types
1. ✅ **CSV** - `test_csv_parsing.py` (updated for two-phase flow)
2. 📋 **JSON** - `test_json_parsing.py` (needs update)
3. 📋 **Text** - `test_text_parsing.py` (simple, good starting point)

### Priority 2: Document Types
4. 📋 **PDF** - `test_pdf_parsing.py` (structured/unstructured)
5. 📋 **Excel** - `test_excel_parsing.py` (XLSX, CSV)

### Priority 3: Specialized Types
6. 📋 **Binary** - `test_binary_parsing.py` (with copybooks)
7. 📋 **Image** - `test_image_parsing.py` (OCR)
8. 📋 **BPMN** - `test_bpmn_parsing.py` (workflow parsing)

---

## Creating New Tests

### Template
Use `test_csv_parsing.py` as a template. Key sections:

1. **File Content Preparation** - Create test file content
2. **Phase 1: Upload** - Upload file, extract IDs
3. **Phase 2: Save** - Save materialization
4. **Phase 3: Parse** - Parse file
5. **Validation** - Validate parsed content

### File Size Target
- **Minimum:** ~120 lines (simple file types)
- **Target:** ~150-180 lines (most file types)
- **Maximum:** ~200 lines (complex file types with extensive validation)

---

## Running Tests

### Individual Test
```bash
python3 tests/integration/capabilities/phase2/file_parsing/test_csv_parsing.py
```

### All Parsing Tests
```bash
for test in tests/integration/capabilities/phase2/file_parsing/test_*.py; do
    echo "Running $test..."
    python3 "$test" && echo "✅ PASSED" || echo "❌ FAILED"
done
```

### Specific File Type
```bash
python3 tests/integration/capabilities/phase2/file_parsing/test_pdf_parsing.py
```

---

## Validation Checklist

Each test should validate:

- ✅ Upload creates pending boundary contract
- ✅ Save authorizes materialization
- ✅ File is available for parsing after save
- ✅ Parsing succeeds
- ✅ Parsed content is meaningful (not empty)
- ✅ Parsed content contains expected data

---

## Error Cases (Future)

Create separate test files for error cases:

- `test_parse_without_save.py` - Should fail
- `test_parse_invalid_file.py` - Should handle gracefully
- `test_parse_unsupported_type.py` - Should return error

---

## Next Steps

1. ✅ Update `test_csv_parsing.py` for two-phase flow
2. 📋 Update `test_json_parsing.py` for two-phase flow
3. 📋 Create `test_text_parsing.py` (simple starting point)
4. 📋 Create remaining test files following the pattern
5. 📋 Add error case tests

---

**Last Updated:** January 19, 2026
