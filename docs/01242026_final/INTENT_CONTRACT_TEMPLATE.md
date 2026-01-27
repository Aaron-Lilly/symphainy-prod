# Intent Contract Template

**Intent:** `[intent_name]`  
**Realm:** `[realm_name]`  
**Status:** ⏳ **IN PROGRESS** | ✅ **COMPLETE** | ❌ **BLOCKED**

---

## 1. Intent Contract

### Required Inputs
- `[parameter_name]`: [description] (required)
- `[parameter_name]`: [description] (required)

### Optional Inputs
- `[parameter_name]`: [description] (optional, default: [value])

### Forbidden Behaviors
- ❌ Direct API calls to `[legacy_endpoint]`
- ❌ Missing parameter validation
- ❌ Missing session validation
- ❌ Missing state updates

### Guaranteed Outputs
- `[output_name]`: [description]
- Realm state update: `[realm].[key]` updated with `[data]`

---

## 2. Runtime Enforcement

### ESLint Rule (if applicable)
- **Rule:** `[rule_name]`
- **Pattern:** `[pattern_to_ban]`
- **Message:** `[error_message]`
- **Status:** ⏳ Not implemented | ✅ Implemented

### Runtime Check
- **Check:** `[what_runtime_checks]`
- **Action if violated:** `[what_happens]`
- **Status:** ⏳ Not implemented | ✅ Implemented

### Proof Test
- **Test:** `[test_name]`
- **Action:** Try to `[intentional_violation]`
- **Expected:** `[must_fail]`
- **Status:** ⏳ Not implemented | ✅ Implemented | ✅ Passing

---

## 3. Journey Evidence

### Journeys Using This Intent
- Journey `[journey_number]`: `[journey_name]` - Step `[step_number]`

### Evidence
- **Journey:** `[journey_name]`
- **Step:** `[step_description]`
- **Verification:** `[how_we_verify_it_works]`
- **Status:** ⏳ Not verified | ✅ Verified

---

## 4. Violations Found

### Direct API Calls
- [ ] `[file_path]`: `[violation_description]`
- [ ] `[file_path]`: `[violation_description]`

### Missing Validation
- [ ] Parameter validation missing: `[parameter_name]`
- [ ] Session validation missing

### Missing State Updates
- [ ] Realm state not updated: `[realm].[key]`

### Other Violations
- [ ] `[violation_description]`

---

## 7. Fixes Applied

### API Migration
- [ ] Migrated to `[APIManager].[method]()` using `submitIntent()`
- [ ] Removed direct API call: `[file_path]`

### Validation Added
- [ ] Parameter validation: `if (![param]) throw new Error(...)`
- [ ] Session validation: `validateSession(platformState, "[operation]")`

### State Updates Added
- [ ] Realm state update: `setRealmState("[realm]", "[key]", ...)`

### Enforcement Implemented
- [ ] ESLint rule: `[rule_name]`
- [ ] Runtime check: `[check_description]`
- [ ] Proof test: `[test_name]`

---

## 8. Verification

### Contract Verification
- [ ] Contract exists and is complete
- [ ] Required inputs documented
- [ ] Forbidden behaviors documented
- [ ] Guaranteed outputs documented

### Enforcement Verification
- [ ] ESLint rule exists (if applicable)
- [ ] Runtime check exists
- [ ] Proof test exists
- [ ] Intentional violation fails ✅

### Journey Evidence Verification
- [ ] At least one journey uses this intent (positive evidence)
- [ ] Intent works in journey context
- [ ] At least one journey proves intent rejects misuse (negative evidence)
- [ ] Journey evidence documented

### Functional Verification
- [ ] Intent works correctly
- [ ] Observable artifacts created
- [ ] State updates correctly

### Idempotency Verification
- [ ] Idempotency key defined
- [ ] Idempotency proof test passes
- [ ] No duplicate side effects on retry

### Observability Verification
- [ ] execution_id in all logs
- [ ] Trace continuity verified
- [ ] Errors include correlation IDs

---

## 9. Gate Status

**Intent is "done" only when:**
- ✅ Contract exists
- ✅ Enforcement implemented
- ✅ Proof test passes (violation fails)
- ✅ Positive journey evidence exists
- ✅ Negative journey evidence exists
- ✅ Idempotency proof test passes
- ✅ Observability guarantees met
- ✅ Intent works correctly

**Current Status:** ⏳ **IN PROGRESS** | ✅ **COMPLETE** | ❌ **BLOCKED**

**Blockers:**
- `[blocker_description]`

---

**Last Updated:** [date]  
**Owner:** [team_member]
