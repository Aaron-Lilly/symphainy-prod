# Phase 6: Update Parsing Abstractions - SAFE IMPLEMENTATION PLAN

**Date:** January 10, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Goal:** Update parsing-related abstractions to new architecture WITHOUT impacting smart city abstractions

---

## 🎯 Scope - Parsing Abstractions ONLY

### ✅ WILL UPDATE (Parsing-Related)

These abstractions are parsing-related and need to be updated:

1. **PDF Processing Abstraction** - `pdf_processing_abstraction.py`
2. **Word Processing Abstraction** - `word_processing_abstraction.py`
3. **Excel Processing Abstraction** - `excel_processing_abstraction.py`
4. **CSV Processing Abstraction** - `csv_processing_abstraction.py`
5. **JSON Processing Abstraction** - `json_processing_abstraction.py`
6. **Text Processing Abstraction** - `text_processing_abstraction.py`
7. **Image Processing Abstraction** - `image_processing_abstraction.py` (OCR)
8. **HTML Processing Abstraction** - `html_processing_abstraction.py`

### ❌ WILL NOT TOUCH (Smart City Abstractions)

These abstractions are being worked on by another team - DO NOT UPDATE:

1. **Auth Abstraction** - `auth_abstraction.py` (Security Guard service)
2. **Semantic Search Abstraction** - `semantic_search_abstraction.py` (Librarian service)
3. **Service Discovery Abstraction** - `service_discovery_abstraction.py` (City Manager service)
4. **State Abstraction** - `state_abstraction.py` (general state management)
5. **File Storage Abstraction** - `file_storage_abstraction.py` (Data Steward service) - if it exists

### ✅ ALREADY COMPLETE

1. **Kreuzberg Processing Abstraction** - `kreuzberg_processing_abstraction.py` (Phase 1)
2. **Mainframe Processing Abstraction** - `mainframe_processing_abstraction.py` (Phase 7)

---

## 📋 Implementation Strategy

### Approach: Create New Abstractions (Don't Modify Old Ones)

**Strategy:** Create new parsing abstractions in `symphainy_source_code` that:
1. Use State Surface for file retrieval (not bytes)
2. Implement `FileParsingProtocol`
3. Follow new architecture patterns
4. Can coexist with old abstractions (no conflicts)

**Benefits:**
- ✅ No risk of breaking smart city abstractions
- ✅ Clean separation between old and new
- ✅ Can migrate gradually
- ✅ No merge conflicts with other team

---

## 🏗️ Implementation Plan

### Step 1: Create Parsing Abstractions (New Architecture)

**Location:** `symphainy_platform/foundations/public_works/abstractions/`

**Pattern for Each Abstraction:**

```python
"""
[File Type] Processing Abstraction - Layer 1

Lightweight coordination layer for [file type] processing operations.
Uses State Surface for file retrieval.

WHAT (Infrastructure): I coordinate [file type] processing operations
HOW (Abstraction): I provide lightweight coordination for [file type] adapter
"""

from ..adapters.[file_type]_adapter import [FileType]Adapter
from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

class [FileType]ProcessingAbstraction:
    """[File Type] Processing Infrastructure Abstraction."""
    
    def __init__(self, adapter, state_surface=None):
        self.adapter = adapter
        self.state_surface = state_surface
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        # 1. Get State Surface from request
        # 2. Retrieve file from State Surface
        # 3. Call adapter
        # 4. Return FileParsingResult
        ...
```

### Step 2: Create/Update Adapters (If Needed)

**Location:** `symphainy_platform/foundations/public_works/adapters/`

**Check if adapters exist:**
- If adapter exists: Update to work with bytes (retrieved by abstraction)
- If adapter doesn't exist: Create new adapter

**Pattern:**
- Adapters work with bytes (retrieved by abstractions)
- Abstractions handle State Surface retrieval
- Clean separation of concerns

---

## 📝 Implementation Checklist

### PDF Processing
- [ ] Check if `pdf_processing_adapter.py` exists
- [ ] Create/update `pdf_processing_adapter.py` (bytes-based)
- [ ] Create `pdf_processing_abstraction.py` (State Surface + FileParsingProtocol)

### Word Processing
- [ ] Check if `word_processing_adapter.py` exists
- [ ] Create/update `word_processing_adapter.py` (bytes-based)
- [ ] Create `word_processing_abstraction.py` (State Surface + FileParsingProtocol)

### Excel Processing
- [ ] Check if `excel_processing_adapter.py` exists
- [ ] Create/update `excel_processing_adapter.py` (bytes-based)
- [ ] Create `excel_processing_abstraction.py` (State Surface + FileParsingProtocol)

### CSV Processing
- [ ] Check if `csv_processing_adapter.py` exists
- [ ] Create/update `csv_processing_adapter.py` (bytes-based)
- [ ] Create `csv_processing_abstraction.py` (State Surface + FileParsingProtocol)

### JSON Processing
- [ ] Check if `json_processing_adapter.py` exists
- [ ] Create/update `json_processing_adapter.py` (bytes-based)
- [ ] Create `json_processing_abstraction.py` (State Surface + FileParsingProtocol)

### Text Processing
- [ ] Check if `text_processing_adapter.py` exists
- [ ] Create/update `text_processing_adapter.py` (bytes-based)
- [ ] Create `text_processing_abstraction.py` (State Surface + FileParsingProtocol)

### Image Processing (OCR)
- [ ] Check if `image_processing_adapter.py` or `ocr_processing_adapter.py` exists
- [ ] Create/update adapter (bytes-based)
- [ ] Create `image_processing_abstraction.py` or `ocr_processing_abstraction.py` (State Surface + FileParsingProtocol)

### HTML Processing
- [ ] Check if `html_processing_adapter.py` exists
- [ ] Create/update `html_processing_adapter.py` (bytes-based)
- [ ] Create `html_processing_abstraction.py` (State Surface + FileParsingProtocol)

---

## 🔒 Safety Measures

1. **Separate Files:** New abstractions in new repo, don't modify old ones
2. **No Smart City Dependencies:** Don't import or reference smart city abstractions
3. **Clear Naming:** Use consistent naming patterns
4. **Documentation:** Document what's safe to update vs. what's not

---

## 📊 Progress Tracking

- **Total Parsing Abstractions:** 8
- **Already Complete:** 2 (Kreuzberg, Mainframe)
- **To Implement:** 6 (PDF, Word, Excel, CSV, JSON, Text, Image, HTML)

---

## 🔗 Related Documents

- `docs/PARSING_IMPLEMENTATION_STATUS.md` - Overall parsing status
- `docs/HOLISTIC_PARSING_IMPLEMENTATION_PLAN.md` - Original plan
- `docs/PHASE_7_MAINFRAME_PARSING_COMPLETE.md` - Mainframe implementation
