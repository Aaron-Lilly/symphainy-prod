# File Parsing Tests - Two-Phase Materialization Flow

## Overview

These tests validate the **File Parsing** capability using the **two-phase materialization flow**:

1. **Phase 1: Upload** (`ingest_file` intent) - Creates pending boundary contract
2. **Phase 2: Save** (`save_materialization` endpoint) - Authorizes materialization
3. **Phase 3: Parse** (`parse_content` intent) - Parses the saved file

**Critical:** Files must be saved before parsing. This is enforced by the workspace-scoped materialization pattern.

---

## Test Structure

Each test file follows this modular pattern:

```
test_<file_type>_parsing.py
├── Upload file (Phase 1)
├── Save file (Phase 2) 
├── Parse file (Phase 3)
└── Validate parsed content
```

**File Size:** ~150-200 lines per test  
**Focus:** One file type per test file

---

## Test Files

### ✅ Created
- `test_csv_parsing.py` - CSV file parsing (updated for two-phase flow)
- `test_json_parsing.py` - JSON file parsing

### 📋 To Create
- `test_pdf_parsing.py` - PDF parsing (structured/unstructured)
- `test_excel_parsing.py` - Excel (XLSX) parsing
- `test_text_parsing.py` - Plain text parsing
- `test_binary_parsing.py` - Binary file parsing (with copybooks)
- `test_image_parsing.py` - Image parsing (OCR)
- `test_bpmn_parsing.py` - BPMN workflow parsing

---

## Test Pattern

Each test inherits from `BaseCapabilityTest` and follows this pattern:

```python
class TestYourFileTypeParsing(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Your File Type Parsing - Two-Phase Flow",
            test_id_prefix="parse_<type>"
        )
    
    async def run_test(self) -> bool:
        # 1. Authenticate
        if not await self.authenticate():
            return False
        
        # 2. Upload file (Phase 1)
        upload_status = await self.submit_intent_and_poll(
            intent_type="ingest_file",
            parameters={...}
        )
        
        # Extract boundary_contract_id and file_id
        file_artifact = upload_status["artifacts"]["file"]
        semantic_payload = file_artifact["semantic_payload"]
        boundary_contract_id = semantic_payload["boundary_contract_id"]
        file_id = semantic_payload["file_id"]
        
        # 3. Save file (Phase 2) - REQUIRED before parsing
        if not await self.save_materialization(boundary_contract_id, file_id):
            return False
        
        # 4. Parse file (Phase 3)
        parse_status = await self.submit_intent_and_poll(
            intent_type="parse_content",
            parameters={
                "file_id": file_id,
                "file_reference": semantic_payload.get("file_reference"),
                "parse_options": {...}
            }
        )
        
        # 5. Validate parsed content
        parsed_artifact = parse_status["artifacts"]["parsed_content"]
        # ... validation logic ...
        
        return True
```

---

## Key Methods

### BaseCapabilityTest Methods

- `authenticate()` - Get auth token
- `submit_intent_and_poll()` - Submit intent and wait for completion
- `save_materialization()` - **NEW** - Save file (Phase 2)
- `get_artifact_by_id()` - Retrieve artifacts
- `find_artifact_by_type()` - Find artifacts in results

---

## Running Tests

### Individual test:
```bash
python3 tests/integration/capabilities/phase2/file_parsing/test_csv_parsing.py
```

### All parsing tests:
```bash
for test in tests/integration/capabilities/phase2/file_parsing/test_*.py; do
    python3 "$test"
done
```

### With output:
```bash
for test in tests/integration/capabilities/phase2/file_parsing/test_*.py; do
    echo "Running $test..."
    python3 "$test" && echo "✅ PASSED" || echo "❌ FAILED"
done
```

---

## Benefits of Modular Structure

1. **Small, focused files** - Easy to read and maintain (~150-200 lines)
2. **One file type per test** - Clear separation of concerns
3. **Reusable base class** - Common functionality (auth, polling, saving) in base
4. **Easy to extend** - Add new file types without modifying existing tests
5. **Clear test flow** - Upload → Save → Parse pattern is explicit

---

## Two-Phase Flow Validation

Each test validates:
- ✅ Upload creates pending boundary contract
- ✅ Save authorizes materialization
- ✅ File is available for parsing after save
- ✅ Parsing succeeds with saved file
- ✅ Parsed content is meaningful

---

## Next Steps

1. Update existing tests (`test_csv_parsing.py`, `test_json_parsing.py`) to include save step
2. Create remaining test files for other file types
3. Add error case tests (parse without save, etc.)
4. Add performance tests (bulk parsing)

---

**Last Updated:** January 19, 2026
