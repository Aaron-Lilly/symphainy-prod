# Cursor Agent Prompt: Option B+ Implementation

**Copy this prompt to start your next Cursor session:**

---

## Context

I'm continuing work on comprehensive test suite expansion for the Symphainy Platform. We've just discovered that our previous tests were surface-level only (testing intent submission, not execution completion). We've created a new deep validation test suite that tests execution completion, artifact generation, and visual validation.

**Key Discoveries:**
1. Visual generation is not working (workflows/solutions complete but no visuals generated)
2. **CRITICAL:** Artifacts are created but NOT stored anywhere - they only exist in memory during execution and are lost after execution completes. This is an architectural gap that needs to be addressed.

**Strategy:** Option B+ - Phased Test Expansion with Quick Wins
- Expand test suite comprehensively to get full visibility
- Fix quick wins immediately in parallel
- Create holistic remediation plan
- Fix systematically by root cause

---

## Current State

### What's Done ✅
1. Created `test_execution_completion.py` - Deep validation tests (working)
2. Found critical issue: Visual generation not working
3. Created comprehensive analysis documents
4. Created implementation plan: `OPTION_B_PLUS_IMPLEMENTATION_PLAN.md`

### What's Next 🔴
**Phase 1: Critical Path Tests (Days 1-2)**
- Expand visual generation tests (SOP, Blueprint)
- Create agent validation tests
- Create E2E workflow tests

**Phase 2: Comprehensive Capability Tests (Days 3-4)**
- Create realm-specific test files
- Test all intents at execution completion depth
- Capture all issues

**Phase 3: Issue Analysis (Day 5)**
- Create issue inventory
- Create prioritization matrix
- Create remediation plan

---

## Your Task

**Begin Phase 1: Critical Path Tests**

1. **Review the implementation plan:**
   - Read: `docs/execution/OPTION_B_PLUS_IMPLEMENTATION_PLAN.md`
   - Read: `docs/execution/SESSION_HANDOFF_OPTION_B_PLUS.md`

2. **Expand visual generation tests:**
   - Edit: `tests/integration/execution/test_execution_completion.py`
   - Add tests for: SOP visual generation, Blueprint visual generation
   - Follow existing test patterns

3. **Create agent validation tests:**
   - Create: `tests/integration/agents/test_agent_validation.py`
   - Test: Intent analysis, Domain expertise, Context preservation, LLM integration
   - Reuse helper functions from `test_execution_completion.py`

4. **Create E2E workflow tests:**
   - Create: `tests/integration/workflows/test_end_to_end_workflows.py`
   - Test: Content→Insights→Outcomes workflow, Workflow→Visual workflow, Solution→Visual workflow

5. **Run tests and capture issues:**
   - Run all new tests
   - Document all issues found in `docs/execution/ISSUE_INVENTORY.md` (create if needed)
   - Fix quick wins immediately if found

---

## Key Files

- **Implementation Plan:** `docs/execution/OPTION_B_PLUS_IMPLEMENTATION_PLAN.md`
- **Handoff Document:** `docs/execution/SESSION_HANDOFF_OPTION_B_PLUS.md`
- **Current Test:** `tests/integration/execution/test_execution_completion.py`
- **Analysis:** `docs/execution/CAPABILITIES_VALIDATION_ASSESSMENT.md`
- **Architecture Gap:** `docs/execution/ARTIFACT_STORAGE_ARCHITECTURE_GAP.md` ⚠️ **CRITICAL**

---

## Key Principles

1. **Test at Execution Completion Depth** - Don't just test intent submission
2. **Fix by Root Cause** - Don't fix symptoms
3. **Quick Wins Don't Wait** - Fix obvious issues immediately
4. **No Anti-Patterns** - No mocks, fallbacks, or hard-coded cheats

---

## Test Pattern to Follow

```python
async def test_[intent_type]_completion():
    """Test that [intent_type] completes successfully."""
    # 1. Get valid token
    token = await get_valid_token()
    
    # 2. Submit intent
    result = await submit_intent(token, "[intent_type]", {...})
    execution_id = result["execution_id"]
    
    # 3. Poll execution status until completion
    status = await poll_execution_status(execution_id, timeout=30)
    
    # 4. Validate execution succeeded
    assert status["status"] == "completed"
    
    # 5. Validate artifacts exist
    artifacts = status["artifacts"]
    assert "[expected_artifact]" in artifacts
    
    # 6. Validate artifact quality (if applicable)
    # 7. Validate visual (if applicable)
```

---

## Helper Functions Available

From `test_execution_completion.py`:
- `get_valid_token()` - Get authentication token
- `submit_intent()` - Submit intent via Runtime API
- `get_execution_status()` - Get execution status
- `poll_execution_status()` - Poll until completion
- `validate_image_base64()` - Validate image format

**Reuse these in new test files!**

---

## Environment

- Services: Experience (8001), Runtime (8000)
- Test mode: Use `TEST_HEADERS = {"X-Test-Mode": "true"}`
- Run from project root: `python3 tests/integration/execution/test_execution_completion.py`

---

## Success Criteria

**Phase 1 Complete When:**
- ✅ Critical path tests implemented
- ✅ All tests run
- ✅ Issues captured
- ✅ Quick wins identified

---

**Please begin with Phase 1: Critical Path Tests. Start by reviewing the implementation plan, then expand the visual generation tests, create agent validation tests, and create E2E workflow tests. Run all tests and capture any issues found.**
