# Phase 2 Capability Tests - Modular Structure

## Overview

Phase 2 tests are organized into small, focused modules for better maintainability. Each test file is ~70-170 lines and tests one specific capability.

## Structure

```
phase2/
├── file_management/
│   ├── test_register_file.py      ✅ Created
│   ├── test_retrieve_file.py      (to create)
│   └── test_list_files.py         (to create)
├── file_parsing/
│   ├── test_csv_parsing.py        (to create)
│   └── test_json_parsing.py       (to create)
├── data_quality/
│   └── test_assess_data_quality.py (to create)
├── interactive_analysis/
│   ├── test_structured_analysis.py (to create)
│   └── test_unstructured_analysis.py (to create)
└── lineage_tracking/
    └── test_visualize_lineage.py  (to create)
```

## Base Class

All tests inherit from `BaseCapabilityTest` (in `../base_capability_test.py`) which provides:

- `authenticate()` - Get auth token
- `submit_intent_and_poll()` - Submit intent and wait for completion
- `get_artifact_by_id()` - Retrieve artifacts
- `find_artifact_by_type()` - Find artifacts in results
- `print_*()` methods for standardized logging

## Test Pattern

Each test follows this pattern:

```python
from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestYourCapability(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Your Test Name",
            test_id_prefix="your_test_prefix"
        )
    
    async def run_test(self) -> bool:
        if not await self.authenticate():
            return False
        
        # Prepare test data
        # Submit intent and poll
        status = await self.submit_intent_and_poll(
            intent_type="your_intent",
            parameters={...}
        )
        
        if not status:
            return False
        
        # Validate results
        artifacts = status.get("artifacts", [])
        # ... validation logic ...
        
        return True

async def main():
    test = TestYourCapability()
    result = await test.execute()
    return 0 if result else 1

if __name__ == "__main__":
    import asyncio
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

## Running Tests

### Individual test:
```bash
python3 tests/integration/capabilities/phase2/file_management/test_register_file.py
```

### All tests in a category:
```bash
for test in tests/integration/capabilities/phase2/file_management/*.py; do
    python3 "$test"
done
```

## Benefits

1. **Small files** - Easy to read and maintain
2. **Focused tests** - Each file tests one capability
3. **Reusable base** - Common functionality in base class
4. **Easy to extend** - Add new tests without modifying existing ones
5. **Clear organization** - Grouped by capability domain

## Next Steps

1. Use `test_register_file.py` as a template
2. Create remaining test files following the same pattern
3. Each test should be ~100-150 lines
4. Focus on one capability per file
