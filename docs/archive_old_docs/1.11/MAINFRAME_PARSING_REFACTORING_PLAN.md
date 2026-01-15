# Mainframe Parsing Capabilities - Remediation & Refactoring Plan

**Date:** January 10, 2026  
**Status:** 📋 **PLANNING**  
**Target:** Best-of-breed mainframe parsing for `symphainy_source_code`

---

## 🎯 Executive Summary

This document provides a comprehensive remediation and refactoring plan for both mainframe parsing capabilities:
1. **Custom Implementation** (`MainframeProcessingAdapter`) - Pure Python, bytes-based
2. **Cobrix Implementation** (`CobrixServiceAdapter`) - Industry-standard, Spark-based

**Goal:** Create best-of-breed implementations that can be migrated to the new `symphainy_source_code` architecture with proper state management.

---

## 📊 Current State Analysis

### Implementation 1: Custom MainframeProcessingAdapter

**Location:** `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/mainframe_processing_adapter.py`

**Strengths:**
- ✅ Bytes-based (no file paths needed)
- ✅ Working EBCDIC parsing
- ✅ Handles 88-level fields (validation rules)
- ✅ Handles VALUE clauses
- ✅ Encoding detection (ASCII vs EBCDIC)
- ✅ Header filtering
- ✅ Simple copybook cleaning

**Weaknesses:**
- ✅ **OCCURS handling** - IMPLEMENTED (but needs testing/verification)
- ✅ **REDEFINES handling** - IMPLEMENTED (but needs testing/verification)
- ✅ **FILLER renaming** - IMPLEMENTED
- ⚠️ Complex copybook parsing logic (could be cleaner)
- ⚠️ No state management (files passed as bytes)
- ⚠️ OCCURS/REDEFINES may have edge cases not fully tested

**Current Issues:**
1. Files passed as bytes through multiple layers
2. Copybook retrieval happens in multiple places
3. No proper state coordination
4. Options dictionary can get lost/modified

---

### Implementation 2: CobrixServiceAdapter

**Location:** `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/cobrix_service_adapter.py`

**Strengths:**
- ✅ Industry-standard (Cobrix library)
- ✅ Handles complex COBOL (COMP-3, REDEFINES, OCCURS)
- ✅ Fast for large files (Spark-based)
- ✅ Better error messages

**Weaknesses:**
- ❌ **Requires extensive copybook preprocessing:**
  - Must remove 88-level fields
  - Must remove VALUE clauses
  - Must remove identifiers
  - Must format as standard COBOL
- ❌ **Requires file paths** (can't work directly with bytes - needs temp files)
- ❌ **Heavy dependency** (Spark, JVM, ~500MB container)
- ❌ **Network dependency** (HTTP API calls)
- ❌ **Not working reliably** (500 errors, preprocessing issues)

**Current Issues:**
1. Copybook preprocessing is complex and error-prone
2. Identifier stripping not working reliably
3. Requires temp files (not bytes-based)
4. Container/service dependency

---

## 🔍 Root Cause Analysis

### State Architecture Issues

**Problem:** Files are passed as bytes through multiple layers without proper state management.

**Current Flow:**
```
Frontend
  ↓ (copybook_file_id)
ContentOrchestrator
  ↓ (retrieves copybook, passes as string in parse_options)
FileParserService
  ↓ (retrieves copybook AGAIN, passes as string in options)
MainframeProcessingAbstraction
  ↓ (converts string to bytes)
MainframeProcessingAdapter
  ↓ (parses bytes)
```

**Issues:**
1. **Duplicate copybook retrieval** - Happens in both orchestrator AND file parser service
2. **Inconsistent data types** - Copybook passed as string, bytes, or file_id
3. **No state coordination** - Files passed in function parameters
4. **Options dictionary mutation** - `parse_options.pop("copybook_file_id")` modifies original
5. **No caching** - Copybook retrieved every time, even if same file

### Parsing Issues

**Custom Implementation:**
1. **OCCURS implemented but needs verification** - Code exists but may have edge cases
2. **REDEFINES implemented but needs verification** - Code exists but may have edge cases
3. **FILLER renaming implemented** - Should work correctly
4. **State architecture** - Files passed as bytes, no proper state coordination

**Cobrix Implementation:**
1. **Copybook preprocessing** - Complex and error-prone
2. **Identifier stripping** - Not working reliably
3. **Temp file management** - Needs cleanup, not bytes-based

---

## 🎯 Refactoring Strategy

### Phase 1: Fix State Architecture (Foundation)

**Goal:** Proper state management for files and copybooks.

#### 1.1 Use State Surface for File References

**New Pattern:**
```python
# Instead of passing bytes through layers:
# OLD: parse_file(file_data: bytes, copybook_data: bytes)

# NEW: Use State Surface for file references
# Store files in State Surface, pass references
session_id = request_context.session_id
file_ref = await state_surface.store_file(session_id, file_data, metadata)
copybook_ref = await state_surface.store_file(session_id, copybook_data, metadata)

# Pass references, not bytes
result = await adapter.parse_file(file_ref, copybook_ref)
```

**Benefits:**
- ✅ Files stored once, referenced multiple times
- ✅ No duplicate retrieval
- ✅ Proper state coordination
- ✅ Can cache copybooks
- ✅ Better for large files

#### 1.2 Unified Copybook Handling

**Single Source of Truth:**
```python
# FileParserService owns copybook retrieval
# All other layers use references

class FileParserService:
    async def parse_file(self, file_id: str, parse_options: Dict):
        # Retrieve main file
        file_data = await self._retrieve_file(file_id)
        
        # Handle copybook (single place)
        copybook_data = None
        if "copybook_file_id" in parse_options:
            copybook_id = parse_options.pop("copybook_file_id")
            copybook_data = await self._retrieve_file(copybook_id)
        
        # Store in State Surface
        session_id = user_context.get("session_id")
        file_ref = await self.state_surface.store_file(session_id, file_data)
        copybook_ref = await self.state_surface.store_file(session_id, copybook_data) if copybook_data else None
        
        # Pass references to abstraction
        request = FileParsingRequest(
            file_reference=file_ref,
            copybook_reference=copybook_ref,
            options=parse_options
        )
```

#### 1.3 Remove Duplicate Copybook Retrieval

**Current (BAD):**
- ContentOrchestrator retrieves copybook
- FileParserService retrieves copybook AGAIN

**New (GOOD):**
- Only FileParserService retrieves copybook
- Orchestrator just passes `copybook_file_id`

---

### Phase 2: Enhance Custom Implementation

**Goal:** Make custom implementation production-ready with all COBOL features.

#### 2.1 Add OCCURS Handling

**Implementation:**
```python
def _handle_occurs(self, lines: List[Dict], occurs: int, level_diff: int = 0, name_postfix: str = "") -> List[Dict]:
    """
    Denormalize COBOL by handling OCCURS clauses.
    Flattens OCCURS into multiple field instances.
    
    Adopted from legacy cobol2csv.py handle_occurs function.
    """
    output = []
    for i in range(1, occurs + 1):
        for line in lines:
            new_line = line.copy()
            # Add postfix to field name
            new_line['name'] = f"{line['name']}-{i}"
            # Adjust level for nested structures
            if level_diff > 0:
                new_line['level'] = line['level'] + level_diff
            # Remove INDEXED BY when flattening
            if 'indexed_by' in new_line:
                del new_line['indexed_by']
            output.append(new_line)
    return output
```

**Integration:**
- Call `_handle_occurs` during copybook parsing
- Flatten OCCURS before building field definitions
- Handle nested OCCURS recursively

#### 2.2 Add REDEFINES Handling

**Implementation:**
```python
def _handle_redefines(self, lines: List[Dict]) -> List[Dict]:
    """
    Handle REDEFINES clauses.
    Removes redefined field and replaces with redefining field.
    """
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'redefines' in line and line['redefines']:
            # Find the field being redefined
            redefined_name = line['redefines']
            redefined_level = line['level']
            
            # Find and remove redefined field and its subgroup
            j = i - 1
            while j >= 0:
                if lines[j]['name'] == redefined_name and lines[j]['level'] == redefined_level:
                    # Remove redefined field and subgroup
                    subgroup = self._get_subgroup(redefined_level, lines[j+1:])
                    # Skip redefined field and subgroup
                    i += len(subgroup)  # Skip subgroup
                    break
                j -= 1
            
            # Add redefining field
            output.append(line)
        else:
            output.append(line)
        i += 1
    return output
```

#### 2.3 Add FILLER Renaming

**Implementation:**
```python
def _rename_fillers(self, field_definitions: List[Dict]) -> List[Dict]:
    """
    Rename FILLER fields to avoid duplicate names.
    """
    filler_counter = 1
    for field_def in field_definitions:
        field_name = field_def.get('name', '').upper()
        if field_name == 'FILLER':
            field_def['name'] = f'FILLER_{filler_counter}'
            filler_counter += 1
    return field_definitions
```

#### 2.4 Improve Copybook Parsing

**Current Issues:**
- Complex regex patterns
- Hard to debug
- Edge cases not handled

**Improvements:**
- Cleaner regex patterns
- Better error messages
- More comprehensive test coverage
- Handle edge cases (nested structures, continuation lines)

---

### Phase 3: Fix Cobrix Implementation

**Goal:** Make Cobrix implementation reliable and production-ready.

#### 3.1 Robust Copybook Preprocessing

**Current Issues:**
- Identifier stripping not working
- 88-level removal incomplete
- VALUE clause removal incomplete

**New Implementation:**
```python
def _preprocess_copybook_for_cobrix(self, copybook_content: str) -> str:
    """
    Preprocess copybook for Cobrix compatibility.
    
    Steps:
    1. Remove 88-level fields (condition names)
    2. Remove VALUE clauses
    3. Remove identifiers (alphanumeric prefixes)
    4. Format as standard COBOL (columns 6-72)
    5. Clean continuation lines
    """
    lines = copybook_content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip 88-level fields
        if line.strip().startswith('88'):
            continue
        
        # Remove VALUE clauses
        line = re.sub(r'\s+VALUE\s+[^.]*\.', '', line)
        
        # Remove identifiers (alphanumeric prefix before level number)
        # Pattern: "AF1019 01 RECORD" -> "01 RECORD"
        line = re.sub(r'^([A-Z0-9-]+\s+)(\d{2}\s)', r'\2', line)
        
        # Format as standard COBOL (columns 6-72)
        if len(line) > 6:
            # Ensure level number at column 6
            if re.match(r'^\s*\d{2}', line):
                # Already has level number, ensure proper spacing
                line = ' ' * 6 + line.strip()
            else:
                # No level number, skip or handle
                continue
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)
```

#### 3.2 Bytes-to-Temp-File Handling

**Current Issue:** Cobrix requires file paths, but we have bytes.

**Solution:**
```python
async def _prepare_files_for_cobrix(
    self, 
    file_data: bytes, 
    copybook_data: bytes
) -> Tuple[str, str]:
    """
    Create temp files for Cobrix (requires file paths).
    Returns (binary_file_path, copybook_file_path).
    """
    import tempfile
    import os
    
    # Create temp directory for this parsing session
    temp_dir = tempfile.mkdtemp(prefix='cobrix_')
    
    binary_path = os.path.join(temp_dir, 'data.bin')
    copybook_path = os.path.join(temp_dir, 'copybook.cpy')
    
    # Write bytes to temp files
    with open(binary_path, 'wb') as f:
        f.write(file_data)
    
    with open(copybook_path, 'wb') as f:
        f.write(copybook_data)
    
    return binary_path, copybook_path

async def _cleanup_temp_files(self, *file_paths: str):
    """Clean up temp files after parsing."""
    import shutil
    for path in file_paths:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {path}: {e}")
```

#### 3.3 Better Error Handling

**Current Issue:** 500 errors with no clear cause.

**Improvements:**
- Validate copybook before sending to Cobrix
- Better error messages from Cobrix service
- Retry logic for transient failures
- Fallback to custom implementation if Cobrix fails

---

### Phase 4: Unified Interface

**Goal:** Single interface that can use either implementation.

#### 4.1 Strategy Pattern

**Implementation:**
```python
class MainframeParsingStrategy(Protocol):
    """Protocol for mainframe parsing strategies."""
    async def parse_file(
        self, 
        file_reference: str, 
        copybook_reference: str,
        options: Dict[str, Any]
    ) -> FileParsingResult:
        ...

class MainframeProcessingAdapter:
    """Unified adapter that can use either strategy."""
    
    def __init__(
        self, 
        strategy: MainframeParsingStrategy = None,
        prefer_cobrix: bool = False
    ):
        if strategy:
            self.strategy = strategy
        elif prefer_cobrix:
            self.strategy = CobrixParsingStrategy()
        else:
            self.strategy = CustomParsingStrategy()
    
    async def parse_file(self, file_ref: str, copybook_ref: str, options: Dict) -> FileParsingResult:
        """Delegate to strategy."""
        return await self.strategy.parse_file(file_ref, copybook_ref, options)
```

#### 4.2 Automatic Strategy Selection

**Logic:**
```python
def _select_strategy(self, file_size: int, copybook_complexity: str, options: Dict) -> MainframeParsingStrategy:
    """
    Select best parsing strategy based on file characteristics.
    
    - Small files (<10MB): Custom (faster, no Spark overhead)
    - Large files (>10MB): Cobrix (parallel processing)
    - Simple copybooks: Custom (no preprocessing needed)
    - Complex copybooks (OCCURS, REDEFINES): Cobrix (handles automatically)
    - User preference: Check options["prefer_cobrix"] or options["prefer_custom"]
    """
    # Check user preference first
    if options.get("prefer_cobrix"):
        return CobrixParsingStrategy()
    if options.get("prefer_custom"):
        return CustomParsingStrategy()
    
    # Auto-select based on characteristics
    if file_size > 10 * 1024 * 1024:  # >10MB
        return CobrixParsingStrategy()
    
    if copybook_complexity == "complex":  # Has OCCURS, REDEFINES
        return CobrixParsingStrategy()
    
    # Default to custom (simpler, faster for most cases)
    return CustomParsingStrategy()
```

---

## 📋 Implementation Plan

### Step 1: State Architecture Foundation (Week 1)

**Tasks:**
1. ✅ Create State Surface file storage interface
2. ✅ Update FileParserService to use State Surface
3. ✅ Remove duplicate copybook retrieval
4. ✅ Update MainframeProcessingAbstraction to use file references
5. ✅ Update adapters to retrieve files from State Surface

**Deliverables:**
- State Surface file storage methods
- Updated FileParserService
- Updated MainframeProcessingAbstraction
- Tests for state coordination

---

### Step 2: Verify & Enhance Custom Implementation (Week 2)

**Tasks:**
1. ✅ Verify OCCURS handling works correctly (code exists, needs testing)
2. ✅ Verify REDEFINES handling works correctly (code exists, needs testing)
3. ✅ Verify FILLER renaming works correctly (code exists, needs testing)
4. ✅ Improve copybook parsing (cleaner, more robust)
5. ✅ Add comprehensive tests for OCCURS, REDEFINES, FILLER
6. ✅ Fix any edge cases discovered during testing

**Deliverables:**
- Verified MainframeProcessingAdapter (OCCURS, REDEFINES, FILLER)
- OCCURS test cases with various scenarios
- REDEFINES test cases with various scenarios
- FILLER renaming tests
- Edge case fixes

---

### Step 3: Fix Cobrix Implementation (Week 2-3)

**Tasks:**
1. ✅ Fix copybook preprocessing (robust identifier stripping)
2. ✅ Implement bytes-to-temp-file handling
3. ✅ Add proper cleanup
4. ✅ Better error handling
5. ✅ Add retry logic

**Deliverables:**
- Fixed CobrixServiceAdapter
- Robust preprocessing
- Temp file management
- Error handling improvements

---

### Step 4: Unified Interface (Week 3)

**Tasks:**
1. ✅ Create strategy pattern
2. ✅ Implement automatic strategy selection
3. ✅ Add user preference options
4. ✅ Create unified adapter
5. ✅ Migration guide

**Deliverables:**
- Unified MainframeProcessingAdapter
- Strategy implementations
- Auto-selection logic
- Migration documentation

---

## 🏗️ New Architecture for `symphainy_source_code`

### Directory Structure

```
symphainy_platform/
  foundations/
    public_works/
      infrastructure_adapters/
        mainframe_parsing/
          __init__.py
          base.py                    # Base strategy protocol
          custom_strategy.py         # Custom implementation
          cobrix_strategy.py         # Cobrix implementation
          unified_adapter.py         # Unified adapter with strategy selection
          copybook_preprocessing.py  # Shared preprocessing utilities
          copybook_parser.py         # Shared copybook parsing
          field_handlers.py          # OCCURS, REDEFINES, FILLER handlers
```

### Key Components

#### 1. Base Strategy Protocol

```python
# base.py
from typing import Protocol
from ..abstraction_contracts.file_parsing_protocol import FileParsingResult

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
        """Check if strategy supports a COBOL feature."""
        # Features: "OCCURS", "REDEFINES", "COMP-3", "large_files", etc.
        ...
```

#### 2. Custom Strategy

```python
# custom_strategy.py
class CustomMainframeStrategy:
    """Custom Python implementation - fast, bytes-based."""
    
    def __init__(self, state_surface: StateSurfaceProtocol):
        self.state_surface = state_surface
        self.copybook_parser = CopybookParser()
        self.field_handlers = FieldHandlers()
    
    async def parse_file(self, file_ref: str, copybook_ref: str, options: Dict) -> FileParsingResult:
        # Retrieve files from State Surface
        file_data = await self.state_surface.get_file(file_ref)
        copybook_data = await self.state_surface.get_file(copybook_ref)
        
        # Parse copybook (with OCCURS, REDEFINES handling)
        field_definitions = await self.copybook_parser.parse(
            copybook_data,
            handle_occurs=True,
            handle_redefines=True,
            rename_fillers=True
        )
        
        # Parse binary records
        records = await self._parse_binary_records(file_data, field_definitions)
        
        return FileParsingResult(...)
    
    def supports_feature(self, feature: str) -> bool:
        return feature in ["OCCURS", "REDEFINES", "COMP-3", "88-level", "VALUE"]
```

#### 3. Cobrix Strategy

```python
# cobrix_strategy.py
class CobrixMainframeStrategy:
    """Cobrix implementation - industry-standard, Spark-based."""
    
    def __init__(self, state_surface: StateSurfaceProtocol, cobrix_service_url: str):
        self.state_surface = state_surface
        self.cobrix_service_url = cobrix_service_url
        self.preprocessor = CopybookPreprocessor()
    
    async def parse_file(self, file_ref: str, copybook_ref: str, options: Dict) -> FileParsingResult:
        # Retrieve files from State Surface
        file_data = await self.state_surface.get_file(file_ref)
        copybook_data = await self.state_surface.get_file(copybook_ref)
        
        # Preprocess copybook for Cobrix
        preprocessed_copybook = self.preprocessor.preprocess_for_cobrix(copybook_data)
        
        # Create temp files (Cobrix requires file paths)
        binary_path, copybook_path = await self._prepare_temp_files(file_data, preprocessed_copybook)
        
        try:
            # Call Cobrix service
            result = await self._call_cobrix_service(binary_path, copybook_path)
            return FileParsingResult(...)
        finally:
            # Cleanup temp files
            await self._cleanup_temp_files(binary_path, copybook_path)
    
    def supports_feature(self, feature: str) -> bool:
        return feature in ["OCCURS", "REDEFINES", "COMP-3", "large_files", "parallel"]
```

#### 4. Unified Adapter

```python
# unified_adapter.py
class MainframeProcessingAdapter:
    """Unified adapter with automatic strategy selection."""
    
    def __init__(
        self,
        state_surface: StateSurfaceProtocol,
        cobrix_service_url: Optional[str] = None
    ):
        self.state_surface = state_surface
        self.custom_strategy = CustomMainframeStrategy(state_surface)
        self.cobrix_strategy = CobrixMainframeStrategy(state_surface, cobrix_service_url) if cobrix_service_url else None
    
    async def parse_file(
        self,
        file_reference: str,
        copybook_reference: str,
        options: Dict[str, Any]
    ) -> FileParsingResult:
        """Parse with automatic strategy selection."""
        
        # Select strategy
        strategy = self._select_strategy(file_reference, copybook_reference, options)
        
        # Parse using selected strategy
        return await strategy.parse_file(file_reference, copybook_reference, options)
    
    def _select_strategy(
        self,
        file_reference: str,
        copybook_reference: str,
        options: Dict[str, Any]
    ) -> MainframeParsingStrategy:
        """Select best parsing strategy."""
        
        # Check user preference
        if options.get("prefer_cobrix") and self.cobrix_strategy:
            return self.cobrix_strategy
        if options.get("prefer_custom"):
            return self.custom_strategy
        
        # Auto-select based on file characteristics
        file_metadata = await self.state_surface.get_file_metadata(file_reference)
        file_size = file_metadata.get("size", 0)
        
        # Large files -> Cobrix
        if file_size > 10 * 1024 * 1024 and self.cobrix_strategy:
            return self.cobrix_strategy
        
        # Default to custom (simpler, faster for most cases)
        return self.custom_strategy
```

---

## 🔧 Migration Steps

### Step 1: Extract to New Structure

1. Create new directory structure in `symphainy_source_code`
2. Copy current implementations
3. Refactor to use State Surface
4. Add missing features (OCCURS, REDEFINES, FILLER)

### Step 2: Test Both Strategies

1. Create test suite for both strategies
2. Test with various copybook formats
3. Test OCCURS, REDEFINES, FILLER handling
4. Performance testing (small vs large files)

### Step 3: Integrate with New Architecture

1. Update MainframeProcessingAbstraction
2. Update FileParserService
3. Update orchestrators
4. Remove duplicate copybook retrieval

### Step 4: Documentation

1. API documentation
2. Usage examples
3. Strategy selection guide
4. Migration guide from old implementation

---

## 📊 Comparison Matrix

| Feature | Custom Strategy | Cobrix Strategy | Recommendation |
|---------|----------------|----------------|----------------|
| **Small Files (<10MB)** | ✅ Fast | ⚠️ Overhead | **Custom** |
| **Large Files (>10MB)** | ⚠️ Sequential | ✅ Parallel | **Cobrix** |
| **OCCURS** | ✅ (after fix) | ✅ Native | **Either** |
| **REDEFINES** | ✅ (after fix) | ✅ Native | **Either** |
| **COMP-3** | ✅ | ✅ | **Either** |
| **88-level fields** | ✅ Extracts | ❌ Must remove | **Custom** |
| **VALUE clauses** | ✅ Handles | ❌ Must remove | **Custom** |
| **Bytes-based** | ✅ Direct | ❌ Needs temp files | **Custom** |
| **Industry Standard** | ❌ Custom | ✅ Cobrix | **Cobrix** |
| **Maintenance** | ⚠️ We own | ✅ Library | **Cobrix** |
| **Dependencies** | ✅ Lightweight | ❌ Heavy (Spark) | **Custom** |

---

## 🎯 Recommendations

### For `symphainy_source_code`:

1. **Primary Strategy: Enhanced Custom Implementation**
   - ✅ OCCURS, REDEFINES, FILLER handling already implemented
   - Verify and test thoroughly
   - Use for most cases (small-medium files)
   - Bytes-based, no temp files
   - Fast, lightweight

2. **Secondary Strategy: Fixed Cobrix Implementation**
   - Use for very large files (>10MB)
   - Use when industry-standard is required
   - Keep as fallback option

3. **Unified Interface:**
   - Automatic strategy selection
   - User preference override
   - Seamless switching

4. **State Architecture:**
   - Use State Surface for file references
   - Single copybook retrieval point
   - Proper state coordination

---

## 📝 Next Steps

1. **Review this plan** - Confirm approach and priorities
2. **Create implementation tasks** - Break down into actionable items
3. **Start with State Architecture** - Foundation for everything else
4. **Enhance Custom Implementation** - Add missing features
5. **Fix Cobrix Implementation** - Make it reliable
6. **Create Unified Interface** - Best of both worlds
7. **Migrate to `symphainy_source_code`** - Clean implementation

---

**Status:** Ready for implementation  
**Estimated Effort:** 3-4 weeks  
**Priority:** High (needed for production mainframe parsing)
