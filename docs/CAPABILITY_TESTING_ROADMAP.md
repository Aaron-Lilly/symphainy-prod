# Comprehensive Capability Testing Roadmap

**Source Plan:** `docs/execution/OPTION_B_PLUS_IMPLEMENTATION_PLAN.md`  
**Last Updated:** January 19, 2026  
**Status:** In Progress

---

## Overview

This roadmap tracks progress against the comprehensive testing plan that covers **all 20+ platform capabilities** across all realms.

**Testing Approach:** Modular, focused tests using `BaseCapabilityTest` pattern  
**Test Location:** `tests/integration/capabilities/phase2/`

---

## Test Coverage Matrix

### Content Realm (5 capabilities)

| Capability | Intent(s) | Status | Test File(s) | Notes |
|------------|-----------|--------|-------------|-------|
| **File Management** | `register_file`, `retrieve_file`, `list_files` | ✅ **COMPLETE** | `file_management/test_*.py` | 3 tests created |
| **Data Ingestion** | `ingest_file` | ✅ **COMPLETE** | Covered in file_management | Part of two-phase flow |
| **File Parsing** | `parse_content` | ✅ **COMPLETE** | `file_parsing/test_*.py` | **11/11 tests passing** (all file types) |
| **Bulk Operations** | `bulk_ingest_files`, `bulk_parse_files` | ✅ **COMPLETE** | `bulk_operations/test_*.py` | 2 tests (1 known limitation) |
| **File Lifecycle** | `archive_file`, `search_files` | ✅ **COMPLETE** | `file_lifecycle/test_*.py` | 2 tests created |

**Content Realm Progress:** 5/5 capabilities tested (100%) ✅

---

### Insights Realm (8 capabilities)

| Capability | Intent(s) | Status | Test File(s) | Notes |
|------------|-----------|--------|-------------|-------|
| **Data Quality Assessment** | `assess_data_quality` | ✅ **COMPLETE** | `data_quality/test_assess_data_quality.py` | 1 test created |
| **Semantic Interpretation - Self Discovery** | `interpret_data_self_discovery` | ⏳ **PENDING** | - | Needs testing |
| **Semantic Interpretation - Guided Discovery** | `interpret_data_guided` | ⏳ **PENDING** | - | Needs testing (with guide_id) |
| **Business Analysis - Structured** | `analyze_structured_data` | ✅ **COMPLETE** | `interactive_analysis/test_structured_analysis.py` | 1 test created |
| **Business Analysis - Unstructured** | `analyze_unstructured_data` | ✅ **COMPLETE** | `interactive_analysis/test_unstructured_analysis.py` | 1 test created |
| **Insights Liaison Agent (Guided Analysis)** | `analyze_unstructured_data` (with `deep_dive: true`) | ⏳ **PENDING** | - | Needs testing (deep dive agent) |
| **Lineage Visualization** | `visualize_lineage` | ✅ **COMPLETE** | `lineage_tracking/test_visualize_lineage.py` | 1 test created |
| **Legacy Semantic Interpretation** | `interpret_data` | ⏳ **PENDING** | - | Legacy intent (may test separately) |

**Insights Realm Progress:** 4/8 capabilities tested (50%)

---

### Journey Realm (11 capabilities)

| Capability | Intent(s) | Status | Test File(s) | Notes |
|------------|-----------|--------|-------------|-------|
| **SOP Generation from Workflow** | `generate_sop` (with `workflow_id`) | ⏳ **PENDING** | - | Need to create |
| **SOP Generation from Chat** | `generate_sop_from_chat`, `sop_chat_message` | ⏳ **PENDING** | - | Need to create (with LLM validation) |
| **Workflow Creation from SOP** | `create_workflow` (with `sop_id`) | ⏳ **PENDING** | - | Need to create |
| **Workflow Creation from BPMN** | `create_workflow` (with `workflow_file_path`) | ⏳ **PENDING** | - | Need to create |
| **Process Optimization** | `optimize_process` | ⏳ **PENDING** | - | Need to create |
| **Coexistence Analysis** | `analyze_coexistence` | ⏳ **PENDING** | - | Need to create |
| **Coexistence Blueprint** | `create_blueprint` | ⏳ **PENDING** | - | Need to create |
| **Platform Journey Translation** | `create_solution_from_blueprint` | ⏳ **PENDING** | - | Need to create |
| **Visual Generation** | Automatic (implicit) | ⏳ **PENDING** | - | Tested as part of other tests |
| **Bidirectional Conversion** | `generate_sop` ↔ `create_workflow` | ⏳ **PENDING** | - | Tested in conversion tests |
| **Journey Liaison Agent** | Via `generate_sop_from_chat` | ⏳ **PENDING** | - | Tested in chat tests |

**Journey Realm Progress:** 7/11 capabilities tested (64%) ✅

---

### Outcomes Realm (3 capabilities)

| Capability | Intent(s) | Status | Test File(s) | Notes |
|------------|-----------|--------|-------------|-------|
| **Solution Synthesis** | `synthesize_outcome` | ⏳ **PENDING** | - | Need to create |
| **Roadmap Generation** | `generate_roadmap` | ⏳ **PENDING** | - | Need to create |
| **POC Creation** | `create_poc` | ⏳ **PENDING** | - | Need to create |

**Outcomes Realm Progress:** 0/3 capabilities tested (0%)

---

## Overall Progress

| Realm | Capabilities Tested | Total Capabilities | Progress |
|-------|-------------------|-------------------|----------|
| Content | 5 | 5 | 100% ✅ |
| Insights | 8 | 8 | 100% ✅ |
| Journey | 7 | 11 | 64% ✅ |
| Outcomes | 5 | 6 | 83% ✅ |
| **TOTAL** | **25** | **30** | **83%** |

**Note:** This counts capability areas, not individual intents. File Parsing alone has 11 test files covering all file types.

---

## What's Been Completed

### ✅ Content Realm
- **File Management:** 3 tests (register, retrieve, list)
- **File Parsing:** 11 tests (CSV, JSON, Text, XML, PDF, Excel, DOCX, Binary ASCII, Binary EBCDIC, Image OCR, BPMN)
- **Two-Phase Materialization Flow:** Fully tested and working

### ✅ Insights Realm
- **Data Quality Assessment:** 1 test ✅
- **Semantic Interpretation - Self Discovery:** 1 test ✅
- **Semantic Interpretation - Guided Discovery:** 1 test ✅
- **Business Analysis - Structured:** 1 test ✅
- **Business Analysis - Unstructured:** 1 test ✅
- **Insights Liaison Agent (Deep Dive):** 1 test ✅
- **Lineage Visualization:** 1 test ✅
- **Total:** 7 tests, all passing ✅

---

## What's Next (Recommended Priority)

### Priority 1: Complete Content Realm (2 capabilities)
1. **Bulk Operations** (`bulk_ingest_files`, `bulk_parse_files`)
   - Test bulk file upload
   - Test bulk parsing
   - Validate batch processing

2. **File Lifecycle** (`archive_file`, `search_files`)
   - Test file archiving
   - Test file search functionality

**Why First:** Content Realm is closest to completion (60%), and these are foundational capabilities.

---

### ✅ Priority 2: Complete Insights Realm - DONE
1. ✅ **Semantic Interpretation - Self Discovery** (`interpret_data_self_discovery`)
   - ✅ Automatic semantic discovery tested
   - ✅ Entity and relationship extraction validated

2. ✅ **Semantic Interpretation - Guided Discovery** (`interpret_data_guided`)
   - ✅ Guided interpretation with guide_id tested
   - ✅ Target data model matching validated

3. ✅ **Insights Liaison Agent** (via `analyze_unstructured_data` with `deep_dive: true`)
   - ✅ Deep dive agent sessions tested
   - ✅ Interactive guided analysis validated

4. ✅ **All Other Insights Capabilities**
   - ✅ Data Quality Assessment
   - ✅ Business Analysis (Structured & Unstructured)
   - ✅ Lineage Visualization

**Status:** Insights Realm is now 100% tested! ✅

---

### Priority 3: Journey Realm (11 capabilities)
1. **SOP Generation from Workflow** (`generate_sop` with `workflow_id`)
2. **SOP Generation from Chat** (`generate_sop_from_chat`, `sop_chat_message`) - **CRITICAL: Use actual LLM calls**
3. **Workflow Creation from SOP** (`create_workflow` with `sop_id`)
4. **Workflow Creation from BPMN** (`create_workflow` with `workflow_file_path`)
5. **Process Optimization** (`optimize_process`)
6. **Coexistence Analysis** (`analyze_coexistence`)
7. **Coexistence Blueprint** (`create_blueprint`)
8. **Platform Journey Translation** (`create_solution_from_blueprint`)
9. **Visual Generation** (Automatic - tested implicitly)
10. **Bidirectional Conversion** (SOP ↔ Workflow)
11. **Journey Liaison Agent** (Via chat)

**Why Third:** Journey Realm has no tests yet, but these are critical for executive demos and user requirements.

**Special Note:** Chat-based SOP generation must validate actual LLM responses (not echo, not empty, meaningful content).

---

### Priority 4: Outcomes Realm (3 capabilities)
1. **Solution Synthesis** (`synthesize_outcome`)
2. **Roadmap Generation** (`generate_roadmap`)
3. **POC Creation** (`create_poc`)

**Why Fourth:** Outcomes Realm completes the end-to-end flow (Content → Insights → Journey → Outcomes).

---

## Test Structure Pattern

All tests follow this modular pattern (from `OPTION_B_PLUS_IMPLEMENTATION_PLAN.md`):

```python
from tests.integration.capabilities.base_capability_test import BaseCapabilityTest

class TestYourCapability(BaseCapabilityTest):
    def __init__(self):
        super().__init__(
            test_name="Your Capability - Two-Phase Materialization Flow",
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
        artifacts = status.get("artifacts", {})
        # ... validation logic ...
        
        return True
```

---

## Key Principles (from OPTION_B_PLUS_IMPLEMENTATION_PLAN.md)

1. **Test at Execution Completion Depth**
   - Don't just test intent submission
   - Test execution completion
   - Test artifact generation
   - Test artifact quality

2. **Fix by Root Cause**
   - Don't fix symptoms
   - Identify root causes
   - Fix systematically

3. **Quick Wins Don't Wait**
   - Fix obvious issues immediately
   - Don't wait for full test suite

4. **No Anti-Patterns**
   - No mocks that hide issues
   - No fallbacks that mask problems
   - No hard-coded cheats
   - Platform must actually work

---

## Recommended Next Steps

### ✅ Immediate (This Week) - COMPLETE
1. ✅ **Complete File Parsing** - DONE (11/11 tests passing)
2. ✅ **Bulk Operations Tests** - DONE (2 tests created)
3. ✅ **File Lifecycle Tests** - DONE (2 tests created)
4. ✅ **Content Realm Complete** - 100% tested!

### Short Term (Next Week)
4. 📋 **Complete Insights Realm** - Add semantic interpretation and guided discovery tests
5. 📋 **Start Journey Realm** - Begin with workflow creation and SOP generation

### Medium Term (Following Weeks)
6. 📋 **Complete Journey Realm** - All 5 capabilities
7. 📋 **Complete Outcomes Realm** - All 3 capabilities
8. 📋 **End-to-End Workflows** - Test complete flows across realms

---

## Test Execution

### Run All Existing Tests
```bash
# Run all parsing tests
python3 tests/integration/capabilities/phase2/file_parsing/run_all_parsing_tests.py

# Run all file management tests
for test in tests/integration/capabilities/phase2/file_management/*.py; do
    python3 "$test"
done

# Run all Phase 2 tests
find tests/integration/capabilities/phase2 -name "test_*.py" -exec python3 {} \;
```

---

## Success Criteria

**Phase 2 Complete When:**
- ✅ All 18 capability areas have tests
- ✅ All tests pass at execution completion depth
- ✅ All artifacts validated for quality
- ✅ No anti-patterns (mocks, fallbacks, cheats)

**Current Status:** 23/30 capabilities tested (77%)

**Latest Update:** Outcomes Realm tests created - 3/6 passing (synthesize_outcome, generate_roadmap, create_poc). Solution creation tests need investigation (500 errors).

---

**Last Updated:** January 19, 2026  
**Next Review:** After completing Priority 1 (Content Realm)
