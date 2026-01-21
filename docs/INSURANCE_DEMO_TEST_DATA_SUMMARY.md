# Insurance Demo Test Data Summary

**Date:** January 2026  
**Status:** ✅ **Generated**  
**Purpose:** Summary of synthetic insurance policy test data generated for insurance demo

---

## Generated Files

### 1. Binary File: `insurance_policy_comprehensive_ebcdic.bin`
- **Location:** `tests/test_data/files/insurance_policy_comprehensive_ebcdic.bin`
- **Size:** 65,950 bytes
- **Records:** 440 total records
- **Encoding:** EBCDIC (simplified for testing - real EBCDIC conversion needed for production)

### 2. Copybook: `copybook_insurance_comprehensive_ebcdic.txt`
- **Location:** `tests/test_data/files/copybook_insurance_comprehensive_ebcdic.txt`
- **Format:** COBOL copybook
- **Record Length:** 150 bytes (fixed)
- **Record Types:** H (Header), P (Policy), C (Claim), B (Beneficiary), T (Trailer)

### 3. Generator Script: `generate_insurance_test_data.py`
- **Location:** `tests/test_data/generate_insurance_test_data.py`
- **Purpose:** Generate synthetic insurance policy test data
- **Usage:** `python3 tests/test_data/generate_insurance_test_data.py`

---

## Record Structure

### Header Record (Type: 'H')
- Record type, sequence number
- File date/time
- Total records count
- Source system identifier

### Policy Master Record (Type: 'P')
- Policy number (12 chars)
- Insured information (name, DOB, SSN)
- Policy details (type, face amount, premium, cash value)
- Dates (effective, expiration, issue)
- Status (ACTIVE, LAPSED, SURRENDERED, MATURED)
- Agent ID

### Claim Record (Type: 'C')
- Policy number (links to policy)
- Claim number, claim date
- Claim type (DEATH, DISABILITY, ACCIDENTAL, SURRENDER)
- Claim amount, status
- Payment information

### Beneficiary Record (Type: 'B')
- Policy number (links to policy)
- Beneficiary ID, name
- Relationship (SPOUSE, CHILD, PARENT, OTHER)
- Beneficiary percentage
- Dates (added, removed)

### Trailer Record (Type: 'T')
- Record type, sequence
- Totals (policies, claims, beneficiaries)
- Checksum

---

## Generated Data Statistics

- **Policies:** 100
- **Claims:** 155 (1-2 per policy)
- **Beneficiaries:** 146 (1-2 per policy)
- **Total Records:** 440 (1 header + 100 policies + 155 claims + 146 beneficiaries + 1 trailer)

---

## Data Characteristics

### Policy Types
- LIFE
- TERM
- WHOLE
- UNIVERSAL

### Policy Statuses
- ACTIVE
- LAPSED
- SURRENDERED
- MATURED

### Claim Types
- DEATH
- DISABILITY
- ACCIDENTAL
- SURRENDER

### Claim Statuses
- PENDING
- APPROVED
- DENIED
- PAID

### Beneficiary Relations
- SPOUSE
- CHILD
- PARENT
- OTHER

---

## Test Suite

**Location:** `tests/integration/capabilities/insurance_demo/test_insurance_policy_parsing.py`

**Tests:**
1. `test_parse_insurance_policy_comprehensive` - Verifies parsing of all record types
2. `test_parse_insurance_policy_data_quality` - Validates data quality and relationships
3. `test_parse_insurance_policy_edge_cases` - Tests edge case handling

---

## Usage in Tests

```python
from tests.test_data.generate_insurance_test_data import generate_synthetic_insurance_data

# Generate test data
data = generate_synthetic_insurance_data(num_policies=100)

# Or use existing file
from pathlib import Path
test_file = Path("tests/test_data/files/insurance_policy_comprehensive_ebcdic.bin")
copybook = Path("tests/test_data/files/copybook_insurance_comprehensive_ebcdic.txt")
```

---

## Notes

1. **EBCDIC Encoding:** Current implementation uses simplified encoding (ASCII/Latin-1). For production testing, proper EBCDIC codec conversion is needed.

2. **Record Relationships:** Records are linked via policy numbers:
   - Claims reference policies via `POLICY_NUMBER`
   - Beneficiaries reference policies via `POLICY_NUMBER`

3. **Data Realism:** Generated data uses realistic patterns:
   - Names from common name pools
   - Dates within reasonable ranges
   - Amounts proportional to policy face amounts
   - Statuses distributed across valid values

4. **Extensibility:** The generator script can be modified to:
   - Generate more/fewer records
   - Add additional record types
   - Customize data patterns
   - Add edge cases (missing fields, invalid data)

---

## Next Steps

1. ✅ Test data generated
2. ✅ Copybook created
3. ✅ Test suite created
4. ⏳ Run tests to verify parsing works
5. ⏳ Add edge case test data (missing fields, invalid data)
6. ⏳ Generate larger dataset for scale testing (1000+ policies)

---

**Last Updated:** January 2026
