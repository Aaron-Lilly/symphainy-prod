# Mainframe Parsing Implementation Plan for `symphainy_source_code`

**Date:** January 10, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Target:** Best-of-breed mainframe parsing aligned with latest analysis

---

## 🎯 Executive Summary

This document provides a comprehensive implementation plan for both mainframe parsing capabilities in `symphainy_source_code`:

1. **Custom Implementation** - Pure Python, bytes-based, production-ready
2. **Cobrix Implementation** - Industry-standard, simplified, gold-standard approach

**Key Principles:**
- ✅ Use State Surface for file references (not passing bytes)
- ✅ Extract 88-level metadata BEFORE cleaning (for insights pillar)
- ✅ Strategy pattern for unified interface
- ✅ Minimal preprocessing (trust Cobrix capabilities)
- ✅ Clean, maintainable code structure

---

## 📊 Current State in `symphainy_source_code`

### What Exists
- ✅ Foundation structure: `symphainy_platform/foundations/public_works/`
- ✅ Adapters directory: `adapters/` (currently has Redis, Consul)
- ✅ Abstractions directory: `abstractions/` (currently has State, Service Discovery)
- ✅ Protocols directory: `protocols/` (State, Service Discovery protocols)
- ✅ State Surface abstraction available

### What's Missing
- ❌ No mainframe parsing adapters
- ❌ No file parsing protocols/abstractions
- ❌ No copybook parsing utilities
- ❌ No 88-level metadata extraction

---

## 🏗️ Target Architecture

### Directory Structure

```
symphainy_platform/
  foundations/
    public_works/
      adapters/
        mainframe_parsing/
          __init__.py
          base.py                    # Base strategy protocol
          custom_strategy.py         # Custom implementation
          cobrix_strategy.py         # Cobrix implementation (simplified)
          unified_adapter.py         # Unified adapter with strategy selection
      file_parsing/
        copybook_parser.py           # Shared copybook parsing
        copybook_preprocessing.py   # Shared preprocessing utilities
        field_handlers.py            # OCCURS, REDEFINES, FILLER handlers
        metadata_extractor.py       # 88-level and level-01 metadata extraction
      __init__.py
      consul_adapter.py              # Existing
      redis_adapter.py               # Existing
      
      abstractions/
        mainframe_processing_abstraction.py  # Mainframe processing abstraction
        file_parsing_abstraction.py          # File parsing abstraction (if needed)
        __init__.py
        
      protocols/
        mainframe_parsing_protocol.py        # Mainframe parsing protocol
        file_parsing_protocol.py             # File parsing protocol
        __init__.py
```

---

## 📋 Implementation Phases

### Phase 1: Foundation - Protocols and Shared Utilities (Week 1)

**Goal:** Create protocols and shared utilities that both implementations will use.

#### 1.1 Create File Parsing Protocol

**File:** `symphainy_platform/foundations/public_works/protocols/file_parsing_protocol.py`

```python
"""
File Parsing Protocol

Defines the interface for file parsing operations.
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileParsingRequest:
    """Request for file parsing."""
    file_reference: str  # State Surface reference
    copybook_reference: Optional[str] = None  # State Surface reference for mainframe files
    filename: str = ""
    options: Optional[Dict[str, Any]] = None

@dataclass
class FileParsingResult:
    """Result of file parsing."""
    success: bool
    text_content: str = ""
    structured_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None  # 88-level fields, level-01 metadata
    error: Optional[str] = None
    timestamp: str = ""

class FileParsingProtocol(Protocol):
    """Protocol for file parsing operations."""
    
    async def parse_file(
        self,
        request: FileParsingRequest
    ) -> FileParsingResult:
        """Parse file using copybook (if provided)."""
        ...
```

#### 1.2 Create Mainframe Parsing Protocol

**File:** `symphainy_platform/foundations/public_works/protocols/mainframe_parsing_protocol.py`

```python
"""
Mainframe Parsing Protocol

Defines the interface for mainframe parsing strategies.
"""

from typing import Protocol, Dict, Any

class MainframeParsingStrategy(Protocol):
    """Protocol for mainframe parsing strategies."""
    
    async def parse_file(
        self,
        file_reference: str,  # State Surface reference
        copybook_reference: str,  # State Surface reference
        options: Dict[str, Any]
    ) -> FileParsingResult:
        """Parse mainframe file using copybook."""
        ...
    
    def supports_feature(self, feature: str) -> bool:
        """
        Check if strategy supports a COBOL feature.
        
        Features: "OCCURS", "REDEFINES", "COMP-3", "88-level", "VALUE", 
                  "large_files", "parallel"
        """
        ...
```

#### 1.3 Create Metadata Extractor

**File:** `symphainy_platform/foundations/public_works/adapters/file_parsing/metadata_extractor.py`

```python
"""
Metadata Extractor

Extracts 88-level fields and level-01 metadata records from copybooks.
Used by both custom and Cobrix implementations.
"""

from typing import Dict, Any, List
import re

class MetadataExtractor:
    """Extracts validation rules from copybook metadata."""
    
    def extract_88_level_fields(self, copybook_content: str) -> List[Dict[str, Any]]:
        """
        Extract 88-level field validation rules.
        
        Returns:
            [
                {
                    "field_name": "STATUS-CODE",
                    "condition_name": "ACTIVE",
                    "value": "A",
                    "line_number": 123
                },
                ...
            ]
        """
        # Use logic from MainframeProcessingAdapter._extract_validation_rules()
        # Or use Level88Extractor from cobrix-parser service
        ...
    
    def extract_level_01_metadata(self, copybook_content: str) -> List[Dict[str, Any]]:
        """
        Extract level-01 metadata record validation rules.
        
        Returns:
            [
                {
                    "record_name": "POLICY-TYPES",
                    "field_name": "TERM-LIFE",
                    "value": "Term Life",
                    "target_field": "POLICY-TYPE",
                    "line_number": 456
                },
                ...
            ]
        """
        # Use logic from MainframeProcessingAdapter._extract_validation_rules()
        ...
    
    def extract_all_validation_rules(self, copybook_content: str) -> Dict[str, Any]:
        """
        Extract all validation rules (88-level + level-01 metadata).
        
        Returns:
            {
                "88_level_fields": [...],
                "metadata_records": [...]
            }
        """
        return {
            "88_level_fields": self.extract_88_level_fields(copybook_content),
            "metadata_records": self.extract_level_01_metadata(copybook_content)
        }
```

#### 1.4 Create Copybook Parser

**File:** `symphainy_platform/foundations/public_works/adapters/file_parsing/copybook_parser.py`

```python
"""
Copybook Parser

Parses COBOL copybooks into field definitions.
Handles OCCURS, REDEFINES, FILLER renaming.
"""

from typing import List, Dict, Any

class CopybookParser:
    """Parses COBOL copybooks into field definitions."""
    
    def parse(
        self,
        copybook_content: str,
        handle_occurs: bool = True,
        handle_redefines: bool = True,
        rename_fillers: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Parse copybook into field definitions.
        
        Args:
            copybook_content: COBOL copybook text
            handle_occurs: Flatten OCCURS clauses
            handle_redefines: Handle REDEFINES clauses
            rename_fillers: Rename FILLER fields
        
        Returns:
            List of field definitions
        """
        # Use logic from MainframeProcessingAdapter._parse_copybook_from_string()
        # Include OCCURS, REDEFINES, FILLER handling
        ...
```

#### 1.5 Create Field Handlers

**File:** `symphainy_platform/foundations/public_works/adapters/file_parsing/field_handlers.py`

```python
"""
Field Handlers

Handles OCCURS, REDEFINES, and FILLER field processing.
"""

from typing import List, Dict, Any

class FieldHandlers:
    """Handles COBOL field processing (OCCURS, REDEFINES, FILLER)."""
    
    def handle_occurs(
        self,
        lines: List[Dict[str, Any]],
        occurs: int,
        level_diff: int = 0,
        name_postfix: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Denormalize COBOL by handling OCCURS clauses.
        Flattens OCCURS into multiple field instances.
        """
        # Use logic from MainframeProcessingAdapter._handle_occurs()
        ...
    
    def handle_redefines(self, lines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Handle REDEFINES clauses.
        Removes redefined field and replaces with redefining field.
        """
        # Use logic from MainframeProcessingAdapter (needs implementation)
        ...
    
    def rename_fillers(self, field_definitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rename FILLER fields to FILLER_1, FILLER_2, etc.
        """
        # Use logic from MainframeProcessingAdapter._rename_filler_fields()
        ...
```

#### 1.6 Create Copybook Preprocessing

**File:** `symphainy_platform/foundations/public_works/adapters/file_parsing/copybook_preprocessing.py`

```python
"""
Copybook Preprocessing

Minimal preprocessing for Cobrix (gold standard approach).
"""

from typing import Dict, Any

class CopybookPreprocessor:
    """Minimal copybook preprocessing for Cobrix."""
    
    def extract_88_level_metadata(self, copybook_text: str) -> Dict[str, Any]:
        """
        Extract 88-level metadata BEFORE cleaning (CRITICAL for insights pillar).
        
        Returns:
            {
                "88_level_fields": [...],
                "metadata_records": [...]
            }
        """
        # Use MetadataExtractor
        ...
    
    def clean_for_cobrix(self, copybook_text: str) -> str:
        """
        Minimal copybook cleaning for Cobrix.
        
        Steps:
        1. Remove 88-level fields (already extracted)
        2. Remove VALUE clauses
        3. Remove identifiers (simple regex)
        4. Ensure standard COBOL format (columns 6-72)
        
        Returns:
            Cleaned copybook text
        """
        # Use simplified approach from COBRIX_GOLD_STANDARD_FIX.md
        ...
```

---

### Phase 2: Custom Strategy Implementation (Week 1-2)

**Goal:** Implement custom mainframe parsing strategy (production-ready).

#### 2.1 Create Custom Strategy

**File:** `symphainy_platform/foundations/public_works/adapters/mainframe_parsing/custom_strategy.py`

**Implementation:**
- Extract from `MainframeProcessingAdapter` (old repo)
- Use State Surface for file retrieval
- Include OCCURS, REDEFINES, FILLER handling
- Extract 88-level metadata
- Return `FileParsingResult` with `validation_rules`

**Key Features:**
- Bytes-based parsing (no temp files)
- Encoding detection (ASCII vs EBCDIC)
- Header filtering
- Validation rules extraction

---

### Phase 3: Cobrix Strategy Implementation (Week 2)

**Goal:** Implement simplified Cobrix strategy (gold standard approach).

#### 3.1 Create Cobrix Strategy

**File:** `symphainy_platform/foundations/public_works/adapters/mainframe_parsing/cobrix_strategy.py`

**Implementation:**
- Extract 88-level metadata BEFORE cleaning
- Minimal copybook cleaning (gold standard)
- Simple file format detection
- Use Cobrix options (file_start_offset, file_trailer_length)
- No workarounds, no manual field fixes
- Return `FileParsingResult` with `validation_rules`

**Key Features:**
- Trust Cobrix capabilities
- Minimal preprocessing (~200 lines vs 1400+)
- Proper error handling
- Temp file management (Cobrix requires file paths)

---

### Phase 4: Unified Adapter (Week 2)

**Goal:** Create unified adapter with automatic strategy selection.

#### 4.1 Create Unified Adapter

**File:** `symphainy_platform/foundations/public_works/adapters/mainframe_parsing/unified_adapter.py`

**Implementation:**
- Strategy pattern
- Automatic strategy selection:
  - User preference (prefer_cobrix, prefer_custom)
  - File size (>10MB → Cobrix)
  - Copybook complexity (OCCURS, REDEFINES → Cobrix)
  - Default: Custom (simpler, faster for most cases)
- Unified interface

---

### Phase 5: Abstraction Layer (Week 2)

**Goal:** Create abstraction layer for mainframe processing.

#### 5.1 Create Mainframe Processing Abstraction

**File:** `symphainy_platform/foundations/public_works/abstractions/mainframe_processing_abstraction.py`

**Implementation:**
- Lightweight coordination layer
- Uses unified adapter
- Implements `FileParsingProtocol`
- Handles State Surface file references
- Converts between protocols

---

### Phase 6: Integration and Testing (Week 3)

**Goal:** Integrate with platform and test thoroughly.

#### 6.1 Integration Points

1. **Content Realm File Parser Service**
   - Use `MainframeProcessingAbstraction`
   - Pass file references (not bytes)
   - Include validation_rules in response

2. **Insights Realm Data Quality Validation**
   - Use validation_rules from parse result
   - Validate records against 88-level fields
   - Validate records against level-01 metadata

3. **State Surface Integration**
   - Store files in State Surface
   - Pass references through layers
   - Cache copybooks

#### 6.2 Testing

1. **Unit Tests**
   - Copybook parsing (OCCURS, REDEFINES, FILLER)
   - Metadata extraction (88-level, level-01)
   - Custom strategy parsing
   - Cobrix strategy parsing (mocked)

2. **Integration Tests**
   - End-to-end parsing with State Surface
   - Validation rules extraction and usage
   - Strategy selection logic

3. **E2E Tests**
   - Full parsing workflow
   - Insights pillar validation
   - Multiple file formats

---

## 📝 Detailed Implementation Checklist

### Phase 1: Foundation (Week 1)

#### Protocols
- [ ] Create `file_parsing_protocol.py`
  - [ ] `FileParsingRequest` dataclass
  - [ ] `FileParsingResult` dataclass
  - [ ] `FileParsingProtocol` protocol

- [ ] Create `mainframe_parsing_protocol.py`
  - [ ] `MainframeParsingStrategy` protocol
  - [ ] `supports_feature()` method

#### Shared Utilities
- [ ] Create `metadata_extractor.py`
  - [ ] `extract_88_level_fields()` method
  - [ ] `extract_level_01_metadata()` method
  - [ ] `extract_all_validation_rules()` method
  - [ ] Use logic from old `MainframeProcessingAdapter._extract_validation_rules()`

- [ ] Create `copybook_parser.py`
  - [ ] `parse()` method with options (handle_occurs, handle_redefines, rename_fillers)
  - [ ] Use logic from old `MainframeProcessingAdapter._parse_copybook_from_string()`
  - [ ] Include OCCURS handling (from `_handle_occurs()`)
  - [ ] Include REDEFINES handling (needs implementation/verification)
  - [ ] Include FILLER renaming (from `_rename_filler_fields()`)

- [ ] Create `field_handlers.py`
  - [ ] `handle_occurs()` method
  - [ ] `handle_redefines()` method
  - [ ] `rename_fillers()` method

- [ ] Create `copybook_preprocessing.py`
  - [ ] `extract_88_level_metadata()` method (BEFORE cleaning)
  - [ ] `clean_for_cobrix()` method (minimal cleaning)
  - [ ] Use simplified approach from `COBRIX_GOLD_STANDARD_FIX.md`

---

### Phase 2: Custom Strategy (Week 1-2)

- [ ] Create `custom_strategy.py`
  - [ ] `__init__()` - Initialize with State Surface, copybook parser, field handlers
  - [ ] `parse_file()` method
    - [ ] Retrieve files from State Surface
    - [ ] Extract 88-level metadata (BEFORE parsing)
    - [ ] Parse copybook (with OCCURS, REDEFINES, FILLER)
    - [ ] Parse binary records
    - [ ] Return `FileParsingResult` with validation_rules
  - [ ] `supports_feature()` method
  - [ ] Use logic from old `MainframeProcessingAdapter`
    - [ ] `_parse_binary_records()` method
    - [ ] `_parse_pic_clause()` method
    - [ ] `_clean_cobol()` method
    - [ ] Encoding detection
    - [ ] Header filtering

---

### Phase 3: Cobrix Strategy (Week 2)

- [ ] Create `cobrix_strategy.py`
  - [ ] `__init__()` - Initialize with State Surface, Cobrix service URL, preprocessor
  - [ ] `parse_file()` method
    - [ ] Extract 88-level metadata (BEFORE cleaning) - CRITICAL
    - [ ] Clean copybook (minimal)
    - [ ] Detect file format (encoding, offsets)
    - [ ] Create temp files (Cobrix requires file paths)
    - [ ] Call Cobrix service with correct options
    - [ ] Read results
    - [ ] Cleanup temp files
    - [ ] Return `FileParsingResult` with validation_rules
  - [ ] `supports_feature()` method
  - [ ] Use simplified approach from `COBRIX_GOLD_STANDARD_FIX.md`
    - [ ] No workarounds
    - [ ] No manual field fixes
    - [ ] Trust Cobrix capabilities

- [ ] Update Cobrix Service (if needed)
  - [ ] Ensure Scala code accepts `file_start_offset` and `file_trailer_length`
  - [ ] Simplify server.py (remove 1400+ lines of preprocessing)

---

### Phase 4: Unified Adapter (Week 2)

- [ ] Create `base.py`
  - [ ] `MainframeParsingStrategy` protocol (if not in protocols/)

- [ ] Create `unified_adapter.py`
  - [ ] `__init__()` - Initialize with State Surface, both strategies
  - [ ] `parse_file()` method
    - [ ] Select strategy (automatic or user preference)
    - [ ] Delegate to selected strategy
  - [ ] `_select_strategy()` method
    - [ ] Check user preference
    - [ ] Check file size
    - [ ] Check copybook complexity
    - [ ] Default to custom

---

### Phase 5: Abstraction Layer (Week 2)

- [ ] Create `mainframe_processing_abstraction.py`
  - [ ] `__init__()` - Initialize with unified adapter
  - [ ] `parse_file()` method - Implements `FileParsingProtocol`
    - [ ] Convert `FileParsingRequest` to strategy call
    - [ ] Handle State Surface references
    - [ ] Return `FileParsingResult`

---

### Phase 6: Integration (Week 3)

#### Content Realm Integration
- [ ] Update File Parser Service
  - [ ] Use `MainframeProcessingAbstraction`
  - [ ] Store files in State Surface
  - [ ] Pass file references (not bytes)
  - [ ] Include validation_rules in response

#### Insights Realm Integration
- [ ] Verify Data Quality Validation Service
  - [ ] Uses validation_rules from parse result
  - [ ] Validates 88-level fields
  - [ ] Validates level-01 metadata

#### State Surface Integration
- [ ] Ensure State Surface has file storage methods
  - [ ] `store_file()` - Store file data
  - [ ] `get_file()` - Retrieve file data
  - [ ] `get_file_metadata()` - Get file metadata (size, etc.)

---

### Phase 7: Testing (Week 3)

#### Unit Tests
- [ ] Test `MetadataExtractor`
  - [ ] 88-level field extraction
  - [ ] Level-01 metadata extraction

- [ ] Test `CopybookParser`
  - [ ] Basic parsing
  - [ ] OCCURS handling
  - [ ] REDEFINES handling
  - [ ] FILLER renaming

- [ ] Test `CopybookPreprocessor`
  - [ ] 88-level metadata extraction (before cleaning)
  - [ ] Minimal cleaning for Cobrix

- [ ] Test `CustomStrategy`
  - [ ] Basic parsing
  - [ ] Encoding detection
  - [ ] Header filtering
  - [ ] Validation rules extraction

- [ ] Test `CobrixStrategy`
  - [ ] Metadata extraction (before cleaning)
  - [ ] Copybook cleaning
  - [ ] File format detection
  - [ ] Error handling

- [ ] Test `UnifiedAdapter`
  - [ ] Strategy selection logic
  - [ ] User preference
  - [ ] Auto-selection

#### Integration Tests
- [ ] Test with State Surface
  - [ ] File storage and retrieval
  - [ ] Reference passing

- [ ] Test end-to-end parsing
  - [ ] Custom strategy
  - [ ] Cobrix strategy
  - [ ] Automatic selection

- [ ] Test validation rules flow
  - [ ] Extraction during parsing
  - [ ] Passing to insights pillar
  - [ ] Validation against rules

#### E2E Tests
- [ ] Test full workflow
  - [ ] File upload → Parse → Validate
  - [ ] Multiple file formats
  - [ ] Multiple copybook formats

---

## 🔄 Migration from Old Repo

### Source Files (Old Repo)

**Custom Implementation:**
- `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/mainframe_processing_adapter.py`
  - Extract: `_parse_copybook_from_string()`, `_parse_binary_records()`, `_extract_validation_rules()`, `_handle_occurs()`, `_rename_filler_fields()`, `_clean_cobol()`, `_parse_pic_clause()`

**Cobrix Implementation:**
- `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/cobrix_service_adapter.py`
  - Extract: HTTP API call logic (simplified)
- `services/cobrix-parser/app/server.py`
  - Extract: Simplified preprocessing (from `COBRIX_GOLD_STANDARD_FIX.md`)
- `services/cobrix-parser/app/cobol_88_field_extractor.py`
  - Extract: 88-level field extraction logic

**Abstraction:**
- `symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/mainframe_processing_abstraction.py`
  - Extract: Protocol implementation pattern

### Migration Steps

1. **Create directory structure** in `symphainy_source_code`
2. **Copy and refactor** source files:
   - Split into modules (strategy, parser, preprocessor, etc.)
   - Update imports for new structure
   - Integrate with State Surface
   - Update to use new protocols
3. **Test** each module independently
4. **Integrate** with platform
5. **Test** end-to-end

---

## 📊 Implementation Priorities

### Must Have (MVP)
1. ✅ Custom strategy (production-ready)
2. ✅ 88-level metadata extraction
3. ✅ Unified adapter with strategy selection
4. ✅ State Surface integration
5. ✅ Insights pillar integration

### Should Have (Phase 2)
1. ✅ Cobrix strategy (simplified, gold standard)
2. ✅ REDEFINES handling verification
3. ✅ Comprehensive testing

### Nice to Have (Phase 3)
1. ⚠️ Performance optimizations
2. ⚠️ Advanced copybook features
3. ⚠️ Caching strategies

---

## 🎯 Success Criteria

### Functional
- ✅ Both strategies parse mainframe files correctly
- ✅ 88-level metadata extracted and passed to insights pillar
- ✅ Validation rules work in insights pillar
- ✅ State Surface used for file references
- ✅ Strategy selection works correctly

### Quality
- ✅ Code is clean and maintainable
- ✅ Tests cover all major scenarios
- ✅ Documentation is complete
- ✅ No workarounds or hacks

### Performance
- ✅ Custom strategy fast for small-medium files
- ✅ Cobrix strategy handles large files
- ✅ No unnecessary file copying
- ✅ Efficient State Surface usage

---

## 📝 Next Steps

1. **Review this plan** - Confirm approach and priorities
2. **Create implementation tasks** - Break down into actionable items
3. **Start Phase 1** - Create protocols and shared utilities
4. **Implement Custom Strategy** - Production-ready first
5. **Implement Cobrix Strategy** - Simplified, gold standard
6. **Create Unified Adapter** - Strategy pattern
7. **Integrate and Test** - End-to-end validation

---

**Status:** Ready for implementation  
**Estimated Effort:** 3 weeks  
**Priority:** High (needed for production mainframe parsing)
