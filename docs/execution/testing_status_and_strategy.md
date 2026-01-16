# Testing Status & Updated E2E Strategy

**Date:** January 2026  
**Status:** 📋 **UPDATED TESTING STRATEGY**  
**Context:** After implementing 6 new parsing adapters, we need to update our E2E testing approach

---

## ✅ What We've Validated

### 1. **Infrastructure & Foundation**
- ✅ Runtime service startup and health checks
- ✅ Experience Plane service startup
- ✅ Public Works Foundation initialization
- ✅ State Surface initialization
- ✅ GCS adapter (required, fail-fast)
- ✅ Supabase file adapter (required, fail-fast)
- ✅ ArangoDB adapter and graph adapter
- ✅ Redis adapter (WAL, State Surface)
- ✅ Basic session creation and retrieval

### 2. **Content Realm - Basic Flow**
- ✅ Realm registration with Runtime
- ✅ Intent submission (`ingest_file`, `parse_content`)
- ✅ File upload to GCS (binary storage)
- ✅ File metadata storage in Supabase
- ✅ State Surface file reference registration
- ✅ Basic parsing flow (CSV, JSON, TXT, Markdown, BPMN)

### 3. **Parsing - MVP Fallbacks**
- ✅ CSV parsing (direct Python `csv` module - MVP fallback)
- ✅ JSON parsing (direct Python `json` module - MVP fallback)
- ✅ PDF parsing (basic text extraction - MVP fallback)
- ✅ Text parsing (direct text processing)

### 4. **Complex Parsing Flows**
- ✅ Binary file parsing with copybook (Cobrix strategy)
- ✅ PDF parsing variants (structured, unstructured, hybrid)
- ✅ Kreuzberg integration for PDF parsing

### 5. **Integration Points**
- ✅ Experience Plane → Runtime API integration
- ✅ Runtime → Content Realm intent flow
- ✅ State Surface file retrieval pattern
- ✅ Public Works abstraction usage

---

## ❌ What Still Needs Testing

### 1. **New Parsing Adapters (Just Implemented)**

We just created 6 new parsing adapters that need systematic testing:

#### **CSV Adapter** (`csv_adapter.py`)
- ❌ CSV parsing via adapter (currently using MVP fallback)
- ❌ UTF-8 vs Latin-1 encoding handling
- ❌ Large CSV files (> 1MB)
- ❌ CSV with special characters
- ❌ CSV with different delimiters (comma, semicolon, tab)

#### **Excel Adapter** (`excel_adapter.py`)
- ❌ Excel parsing via adapter (pandas/openpyxl)
- ❌ Multiple sheets handling
- ❌ Table extraction from Excel
- ❌ Large Excel files
- ❌ Excel with formulas
- ❌ Excel with merged cells

#### **PDF Adapter** (`pdf_adapter.py`)
- ❌ PDF parsing via adapter (pdfplumber/PyPDF2)
- ❌ Table extraction from PDF
- ❌ Multi-page PDF handling
- ❌ PDF with images
- ❌ Scanned PDF (OCR needed)
- ❌ PDF with complex layouts

#### **Word Adapter** (`word_adapter.py`)
- ❌ Word document parsing via adapter (python-docx)
- ❌ Table extraction from Word
- ❌ Multi-paragraph handling
- ❌ Word with images
- ❌ Word with headers/footers
- ❌ Word with styles/formatting

#### **HTML Adapter** (`html_adapter.py`)
- ❌ HTML parsing via adapter (BeautifulSoup)
- ❌ Table extraction from HTML
- ❌ Link extraction
- ❌ Heading extraction
- ❌ HTML with embedded content
- ❌ Malformed HTML handling

#### **Image/OCR Adapter** (`image_adapter.py`)
- ❌ Image OCR via adapter (pytesseract/PIL)
- ❌ Text extraction from images
- ❌ Multiple image formats (PNG, JPG, TIFF)
- ❌ Scanned document OCR
- ❌ Image with complex layouts
- ❌ Low-quality image handling

### 2. **Adapter → Abstraction Integration**

Each adapter needs to be tested through its abstraction:

- ❌ CSV adapter → `CsvProcessingAbstraction` → Content Realm
- ❌ Excel adapter → `ExcelProcessingAbstraction` → Content Realm
- ❌ PDF adapter → `PdfProcessingAbstraction` → Content Realm
- ❌ Word adapter → `WordProcessingAbstraction` → Content Realm
- ❌ HTML adapter → `HtmlProcessingAbstraction` → Content Realm
- ❌ Image adapter → `ImageProcessingAbstraction` → Content Realm

### 3. **Content Realm - Full E2E Flow**

For each file type, test the complete flow:

- ❌ Upload → Parse → Preview → Embeddings → Lineage
- ❌ Verify file stored in GCS
- ❌ Verify metadata in Supabase
- ❌ Verify parsed data in GCS
- ❌ Verify preview generation
- ❌ Verify embeddings in ArangoDB (when implemented)
- ❌ Verify lineage in Supabase

### 4. **Error Handling & Edge Cases**

- ❌ Missing adapter dependencies (graceful degradation vs fail-fast)
- ❌ Invalid file formats
- ❌ Corrupted files
- ❌ Very large files (> 100MB)
- ❌ Empty files
- ❌ Files with no content
- ❌ Encoding issues (UTF-8, Latin-1, EBCDIC)

### 5. **Performance & Scalability**

- ❌ Parsing performance for each file type
- ❌ Memory usage for large files
- ❌ Concurrent file parsing
- ❌ Timeout handling

### 6. **Custom Mainframe Strategy** ✅ **READY TO TEST**

- ✅ Custom mainframe adapter ported (72KB implementation)
- ❌ Custom mainframe parsing E2E tests
- ❌ OCCURS clause handling
- ❌ COMP-3 field parsing
- ❌ COMP/BINARY field parsing
- ❌ ASCII vs EBCDIC encoding
- ❌ Strategy selection (Custom vs Cobrix)
- ❌ Unified adapter strategy selection logic

---

## 🎯 Updated E2E Testing Strategy

### **Phase 1: Adapter Unit Tests** (Foundation)

Create focused unit tests for each adapter to verify they work in isolation:

```
tests/unit/adapters/
├── test_csv_adapter.py
├── test_excel_adapter.py
├── test_pdf_adapter.py
├── test_word_adapter.py
├── test_html_adapter.py
├── test_image_adapter.py
├── test_json_adapter.py
└── test_mainframe_adapter.py  # Custom + Cobrix strategies
```

**Purpose:** Verify each adapter can parse files correctly without Runtime/State Surface dependencies.

**Test Structure:**
- Test with sample file bytes
- Test encoding handling
- Test error cases
- Test edge cases (empty files, invalid formats)

---

### **Phase 2: Abstraction Integration Tests** (Coordination)

Test each abstraction with its adapter:

```
tests/integration/abstractions/
├── test_csv_processing_abstraction.py
├── test_excel_processing_abstraction.py
├── test_pdf_processing_abstraction.py
├── test_word_processing_abstraction.py
├── test_html_processing_abstraction.py
└── test_image_processing_abstraction.py
```

**Purpose:** Verify abstractions correctly coordinate with adapters and State Surface.

**Test Structure:**
- Test abstraction → adapter flow
- Test State Surface file retrieval
- Test FileParsingResult conversion
- Test error handling

---

### **Phase 3: Content Realm E2E Tests** (Full Flow)

Update existing E2E tests to systematically test all file types:

```
tests/integration/
├── test_content_realm_parsing_e2e.py  # NEW: Systematic parsing tests
├── test_content_realm_comprehensive_e2e.py  # UPDATE: Add new file types
└── test_complex_parsing_flows.py  # UPDATE: Add adapter-specific tests
```

**Purpose:** Verify complete Content Realm flow for each file type.

**Test Structure:**
- For each file type (CSV, Excel, PDF, Word, HTML, Image):
  - Upload file
  - Parse file
  - Verify parsed data
  - Verify preview
  - Verify metadata
  - Verify lineage

---

### **Phase 4: Cross-Realm E2E Tests** (Integration)

Test how parsed files flow to other realms:

```
tests/integration/
├── test_content_to_insights_e2e.py  # Content → Insights flow
├── test_content_to_operations_e2e.py  # Content → Operations flow
└── test_complete_realm_journey_e2e.py  # All realms in sequence
```

**Purpose:** Verify parsed files can be used by Insights and Operations realms.

---

## 📋 Recommended Test Implementation Order

### **Immediate Priority (This Session)**

1. **Create adapter unit tests** (30 min)
   - Quick smoke tests for each adapter
   - Verify they can parse sample files
   - Verify error handling

2. **Update Content Realm E2E tests** (1 hour)
   - Add tests for Excel, Word, HTML, Image file types
   - Verify full flow (upload → parse → preview)
   - Verify adapter is used (not MVP fallback)

3. **Create systematic parsing test suite** (1 hour)
   - `test_content_realm_parsing_e2e.py`
   - Test each file type systematically
   - Test adapter → abstraction → realm flow

### **Next Session**

4. **Error handling tests** (30 min)
   - Missing dependencies
   - Invalid files
   - Edge cases

5. **Performance tests** (30 min)
   - Large files
   - Concurrent parsing

6. **Cross-realm tests** (1 hour)
   - Content → Insights
   - Content → Operations

---

## 🧪 Test File Structure

### **New Test File: `test_content_realm_parsing_e2e.py`**

```python
"""
Systematic Parsing E2E Tests for Content Realm

Tests all file types through complete flow:
- Upload → Parse → Preview → Metadata → Lineage

WHAT (Test Role): I verify all parsing adapters work end-to-end
HOW (Test Implementation): I test each file type systematically
"""

# Test Structure:
# - test_csv_parsing_e2e()
# - test_excel_parsing_e2e()
# - test_pdf_parsing_e2e()
# - test_word_parsing_e2e()
# - test_html_parsing_e2e()
# - test_image_ocr_e2e()
# - test_parsing_error_handling()
# - test_parsing_performance()
```

### **Updated Test File: `test_content_realm_comprehensive_e2e.py`**

Add new test cases for:
- Excel file upload and parsing
- Word document upload and parsing
- HTML file upload and parsing
- Image upload and OCR

---

## ✅ Success Criteria

### **Adapter Tests**
- ✅ All 6 adapters can parse sample files
- ✅ All adapters handle errors gracefully
- ✅ All adapters return correct data structures

### **Abstraction Tests**
- ✅ All abstractions correctly use their adapters
- ✅ All abstractions handle State Surface correctly
- ✅ All abstractions return FileParsingResult correctly

### **E2E Tests**
- ✅ All file types can be uploaded and parsed
- ✅ Parsed data is stored correctly
- ✅ Previews are generated correctly
- ✅ Metadata is stored correctly
- ✅ Lineage is tracked correctly

### **Integration Tests**
- ✅ Parsed files can be used by Insights realm
- ✅ Parsed files can be used by Operations realm
- ✅ Complete journey works end-to-end

---

## 🚀 Next Steps

1. **Create adapter unit tests** (quick smoke tests)
2. **Update Content Realm E2E tests** (add new file types)
3. **Create systematic parsing test suite** (comprehensive coverage)
4. **Run tests and fix issues** (iterative)
5. **Add error handling tests** (edge cases)
6. **Add performance tests** (scalability)

---

## 📝 Notes

- **MVP Fallbacks**: Some abstractions have MVP fallbacks (CSV, JSON, PDF). We should verify adapters are used when available, and fallbacks work when adapters are missing.

- **Dependencies**: Some adapters require external libraries (pandas, openpyxl, pdfplumber, python-docx, beautifulsoup4, pytesseract, PIL). Tests should verify graceful degradation if dependencies are missing.

- **State Surface Pattern**: All file access must go through State Surface. Tests should verify this pattern is followed.

- **Fail-Fast Principle**: Critical infrastructure (GCS, Supabase) should fail fast. Tests should verify this behavior.
