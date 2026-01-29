# Expected Test Outputs

This directory contains expected outputs for integration test validation.

## Philosophy

Tests should validate that the platform **actually works** by comparing:
1. Real file inputs → Real platform processing → Expected structured outputs

This is NOT about checking API availability - it's about proving the platform produces correct results.

## Structure

```
expected/
├── csv/
│   └── sample_csv_expected.json      # Expected parsed output for sample.csv
├── json/
│   └── sample_json_expected.json     # Expected parsed output for sample.json  
├── pdf/
│   └── permit_pdf_expected.json      # Expected parsed output for permit_oil_gas.pdf
├── validation_rules.py               # Validation functions
└── README.md                         # This file
```

## Validation Approach

### Structural Validation
- Verify expected fields exist
- Verify field types match
- Verify record counts match

### Semantic Validation  
- Verify known values are extracted correctly
- Verify calculations (totals, averages) are correct
- Verify relationships between fields

### Quality Validation
- Verify completeness (no missing required fields)
- Verify accuracy (values within expected ranges)
- Verify consistency (related fields are coherent)

## Usage

```python
from tests.expected.validation_rules import validate_csv_parse, validate_json_parse

# After parsing a file
result = await realm.handle_intent(parse_intent, context)

# Validate the result
is_valid, errors = validate_csv_parse(result, "sample.csv")
assert is_valid, f"Validation failed: {errors}"
```
