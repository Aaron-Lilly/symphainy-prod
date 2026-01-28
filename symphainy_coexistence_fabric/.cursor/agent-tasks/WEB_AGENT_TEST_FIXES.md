# Web Agent Task: Fix Test Parameters and Assertions

**Priority:** High  
**Estimated Time:** 30-60 minutes  
**Status:** Ready for execution  
**Goal:** Fix parameter and assertion issues to get tests from 76% to 86%+ passing

---

## 📋 Task Overview

You need to fix two types of issues in the test suite:

1. **Parameter Issues** (~30 tests) - Tests use empty `{}` parameters when services require specific fields
2. **Assertion Issues** (~20 tests) - Tests check for `"success"` but results use different structure

---

## 🎯 Part 1: Fix Parameter Issues

### Problem
Many tests call services with empty parameters `{}`, but the services require specific fields like:
- `create_workflow` needs `sop_id`, `bpmn_file_id`, or `workflow_spec`
- `authenticate_user` needs `email` and `password`
- `analyze_coexistence` needs `workflow_id` or `sop_id`
- `generate_sop` needs `workflow_id` or `sop_id`

### Solution
1. Find the contract for each intent service
2. Extract example parameters from the contract
3. Update test files with real test data

### How to Find Parameters

**Step 1:** Locate the intent contract
- Contracts are in: `docs/intent_contracts/journey_<journey_name>/intent_<intent_name>.md`
- Example: `docs/intent_contracts/journey_workflow_management/intent_create_workflow.md`

**Step 2:** Read the contract's "Input Parameters" or "Example" section
- Look for `parameters:`, `input:`, or example JSON
- Copy the example parameters

**Step 3:** Update the test file
- Replace empty `{}` with the example parameters
- Use realistic test values (e.g., `"test_workflow_123"`, `"test@example.com"`)

### Example Fix

**Before:**
```python
async def test_executes_successfully(self, operations_solution, execution_context):
    intent = IntentFactory.create_intent(
        intent_type="create_workflow",
        parameters={}  # ❌ Empty - will fail
    )
```

**After:**
```python
async def test_executes_successfully(self, operations_solution, execution_context):
    intent = IntentFactory.create_intent(
        intent_type="create_workflow",
        parameters={
            "sop_id": "test_sop_123",  # ✅ From contract
            "workflow_name": "Test Workflow"
        }
    )
```

### Files to Fix - Intent Service Tests

**Operations Realm:**
- `tests/3d/intent/operations/test_create_workflow_service.py`
- `tests/3d/intent/operations/test_analyze_coexistence_service.py`
- `tests/3d/intent/operations/test_generate_sop_service.py`
- `tests/3d/intent/operations/test_optimize_process_service.py`

**Security Realm:**
- `tests/3d/intent/security/test_authenticate_user_service.py`
- `tests/3d/intent/security/test_create_user_account_service.py`
- `tests/3d/intent/security/test_create_session_service.py`
- `tests/3d/intent/security/test_validate_authorization_service.py`

**Content Realm:**
- `tests/3d/intent/content/test_upload_file_service.py`
- `tests/3d/intent/content/test_parse_file_service.py`
- `tests/3d/intent/content/test_create_embeddings_service.py`
- `tests/3d/intent/content/test_delete_file_service.py`
- `tests/3d/intent/content/test_retrieve_file_service.py`
- `tests/3d/intent/content/test_list_files_service.py`

**Outcomes Realm:**
- `tests/3d/intent/outcomes/test_create_solution_service.py`
- `tests/3d/intent/outcomes/test_create_blueprint_service.py`
- `tests/3d/intent/outcomes/test_synthesize_outcome_service.py`
- `tests/3d/intent/outcomes/test_generate_roadmap_service.py`
- `tests/3d/intent/outcomes/test_export_artifact_service.py`
- `tests/3d/intent/outcomes/test_create_poc_service.py`

### Files to Fix - Journey Tests

**Operations Solution:**
- `tests/3d/journey/operations_solution/test_workflow_management_journey.py`
  - Needs: `sop_id`, `bpmn_file_id`, or `workflow_spec` in `journey_params`
- `tests/3d/journey/operations_solution/test_sop_management_journey.py`
  - Needs: `workflow_id` in `journey_params` (already has it, but check assertion)
- `tests/3d/journey/operations_solution/test_coexistence_analysis_journey.py`
  - Needs: `workflow_id` or `sop_id` in `journey_params`
- `tests/3d/journey/operations_solution/test_process_optimization_journey.py`
  - Needs: `workflow_id` in `journey_params` (already has it, but check assertion)

**Security Solution:**
- `tests/3d/journey/security_solution/test_authentication_journey.py`
  - Needs: `email` and `password` in `journey_params`
- `tests/3d/journey/security_solution/test_registration_journey.py`
  - Needs: `email` and `password` in `journey_params`
- `tests/3d/journey/security_solution/test_session_management_journey.py`
  - Check if needs parameters (may just need assertion fix)

---

## 🎯 Part 2: Fix Assertion Issues

### Problem
Tests check for `"success" in result` but actual results use different structure:
- Results have: `journey_id`, `journey_execution_id`, `artifacts`, `events`
- Results don't have: `"success"` key

### Solution
Update assertions to check for actual result structure:
- Check for `artifacts` in result
- Check for `journey_execution_id` in result
- Check for `events` in result
- Remove `"success"` checks where not applicable

### Example Fix

**Before:**
```python
result = await journey.compose_journey(...)
assert "success" in result or "error" in result  # ❌ Wrong structure
```

**After:**
```python
result = await journey.compose_journey(...)
assert "artifacts" in result  # ✅ Correct structure
assert "journey_execution_id" in result  # ✅ Also check this
```

### Pattern to Follow

**For Journey Execution Tests:**
```python
result = await journey.compose_journey(...)

# ✅ Good assertions:
assert "artifacts" in result
assert "journey_execution_id" in result
assert "events" in result

# ❌ Bad assertions:
assert "success" in result or "error" in result
```

**For Intent Service Execution Tests:**
```python
result = await solution.handle_intent(intent, execution_context)

# ✅ Good assertions:
assert "artifacts" in result or "artifact_id" in result
# OR if it's a journey result:
assert "journey_execution_id" in result

# ❌ Bad assertions:
assert "success" in result
```

### Files to Fix

**Journey Execution Tests:**
- All files in `tests/3d/journey/*/test_*_journey.py`
- Look for `test_execute_journey` and `test_returns_artifacts` methods
- Fix assertions in execution test classes

**Intent Service Execution Tests:**
- All files in `tests/3d/intent/*/test_*_service.py`
- Look for `test_executes_successfully` and `test_registers_artifact` methods
- Fix assertions in execution test classes

---

## 📝 Step-by-Step Instructions

### Step 1: Fix Parameters (30 tests)

1. **Pick a test file** from the list above
2. **Find the contract:**
   - Intent service: `docs/intent_contracts/journey_<journey>/intent_<intent>.md`
   - Journey: Check the journey contract or solution contract
3. **Read the contract** for example parameters
4. **Update the test file:**
   - Find all `parameters={}` or `journey_params={}`
   - Replace with example parameters from contract
   - Use realistic test values
5. **Save and move to next file**

### Step 2: Fix Assertions (20 tests)

1. **Pick a test file** with execution tests
2. **Find assertion issues:**
   - Search for `assert "success" in result`
   - Search for `assert "error" in result`
3. **Update assertions:**
   - Replace with `assert "artifacts" in result`
   - Add `assert "journey_execution_id" in result` for journey tests
   - Keep error checks if they're testing error scenarios
4. **Save and move to next file**

### Step 3: Verify

After fixing, you can verify by running:
```bash
cd /home/founders/demoversion/symphainy_source_code/symphainy_coexistence_fabric
python3 -m pytest tests/3d/intent/ tests/3d/journey/ -v --tb=line | grep -E "PASSED|FAILED"
```

---

## 🔍 Quick Reference: Common Parameters

### Operations Realm
```python
# create_workflow
parameters={
    "sop_id": "test_sop_123",  # OR
    "bpmn_file_id": "test_bpmn_123",  # OR
    "workflow_spec": {"name": "Test Workflow", "steps": [...]}
}

# generate_sop
parameters={
    "workflow_id": "test_workflow_123",
    "generation_mode": "from_workflow"
}

# analyze_coexistence
parameters={
    "workflow_id": "test_workflow_123"  # OR
    "sop_id": "test_sop_123"
}

# optimize_process
parameters={
    "workflow_id": "test_workflow_123"
}
```

### Security Realm
```python
# authenticate_user
parameters={
    "email": "test@example.com",
    "password": "Password123!"
}

# create_user_account
parameters={
    "email": "test@example.com",
    "password": "Password123!",
    "name": "Test User"
}

# create_session
parameters={
    "user_id": "test_user_123"
}
```

### Content Realm
```python
# upload_file
parameters={
    "file_content": "<base64>",
    "file_name": "test.pdf",
    "file_type": "application/pdf"
}

# parse_file
parameters={
    "file_id": "test_file_123"
}

# create_embeddings
parameters={
    "parsed_artifact_id": "test_parsed_123"
}
```

### Outcomes Realm
```python
# create_solution
parameters={
    "solution_name": "Test Solution",
    "description": "Test description"
}

# create_blueprint
parameters={
    "solution_id": "test_solution_123"
}
```

---

## ✅ Success Criteria

After completing this task:

1. **Parameter fixes:** All tests should have proper parameters from contracts
2. **Assertion fixes:** All tests should check for actual result structure
3. **Test results:** Should see ~50 more tests passing (from 379 to ~429)
4. **No regressions:** Existing passing tests should still pass

---

## 🚨 Important Notes

1. **Don't break existing tests:** Only fix the failing ones
2. **Use contract examples:** Always get parameters from contracts, not guess
3. **Keep test values realistic:** Use `test_*` prefixes for test IDs
4. **Check both places:** Some tests have parameters in `parameters={}` and `journey_params={}`
5. **Verify after fixes:** Run tests to confirm they pass

---

## 📚 Resources

- **Test Results:** `.cursor/agent-tasks/TEST_EXECUTION_RESULTS.md`
- **Test Status:** `.cursor/agent-tasks/TEST_SUITE_STATUS.md`
- **Contracts:** `docs/intent_contracts/` and `docs/journey_contracts/`
- **Solution Contracts:** `docs/solution_contracts/`

---

## 🎯 Expected Outcome

After completing this task:
- ✅ ~50 more tests passing (429/498 = 86%)
- ✅ Parameter issues resolved
- ✅ Assertion issues resolved
- ✅ Tests ready for further enhancement

**Status:** Ready to start! Begin with Part 1 (parameters), then Part 2 (assertions).
