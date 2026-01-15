# Platform Rules of the Road

**Status:** Canonical (Locked — January 2026)  
**Applies to:** All platform code, tests, and documentation

These rules are **non-negotiable**. They exist to ensure we build a platform that works, not a platform that looks good on paper.

---

## 🚫 Breaking Changes Policy

### No Backwards Compatibility

**Rule:** This is a **new platform**. Breaking changes are expected and required.

**Why:**
- We're rebuilding to follow the new architecture guide
- Backwards compatibility would mask architectural issues
- Backwards compatibility gives teams too much leeway to build with bad habits
- Clean break = clean platform

**What This Means:**
- ✅ Archive old implementations (reference only)
- ✅ Rebuild following new architecture
- ✅ No migration paths from old code
- ✅ No compatibility layers
- ❌ No support for old patterns
- ❌ No dual-mode operation

**Exception:** None. This is a platform rebuild.

---

## ✅ Working Code Only

### No Stubs, Placeholders, or Cheats

**Rule:** All code must **work**. No stubs, placeholders, hard-coded cheats, or "TODO" implementations.

**Why:**
- We're building a platform that works when we're done
- Stubs create false confidence
- Placeholders become permanent technical debt
- Cheats mask real problems

**What This Means:**
- ✅ All functions have real implementations
- ✅ All APIs return real data
- ✅ All integrations work (or fail gracefully with proper errors)
- ✅ All business logic is complete
- ❌ No `pass` statements (unless abstract method)
- ❌ No `raise NotImplementedError` (unless abstract method)
- ❌ No `# TODO: implement this`
- ❌ No hard-coded values that should be configurable
- ❌ No mock data in production code

**Exception:** Deliberate placeholders are allowed **only if**:
1. They are explicitly documented as placeholders
2. They are resolved in the **same sprint/plan**
3. They are tracked in the execution checklist
4. Tests fail if placeholder is used inappropriately

**Example of Allowed Placeholder:**
```python
# PLACEHOLDER: This will be replaced with real implementation in Phase 1.2
# Tracked in: execution/checklists/phase_1_checklist.md
# Resolves: Week 2, Day 3
async def get_data(self):
    # Temporary: Returns empty until Phase 1.2
    return []
```

**Example of Forbidden Placeholder:**
```python
async def get_data(self):
    # TODO: implement this
    pass
```

---

## 🧪 Tests Must Be Real

### No Tests Pass with Cheats

**Rule:** No test can pass if the code has cheats, stubs, or placeholders.

**Why:**
- Tests validate that code works
- If tests pass with cheats, tests are meaningless
- Tests should catch architectural violations

**What This Means:**
- ✅ Tests verify real functionality
- ✅ Tests fail if code has cheats
- ✅ Tests validate architecture compliance
- ✅ Integration tests test real integrations
- ❌ No tests that pass with `pass` statements
- ❌ No tests that pass with hard-coded values
- ❌ No tests that pass with mock data in production code
- ❌ No tests that skip validation

**Test Requirements:**
1. **Unit Tests:** Test individual components in isolation
2. **Integration Tests:** Test component interactions
3. **E2E Tests:** Test full user journeys
4. **Architecture Tests:** Test architectural compliance (no direct DB writes, etc.)

**Test Failure = Code Failure:**
- If a test fails, fix the code, not the test
- If a test passes with cheats, the test is wrong
- If code has cheats, tests must fail

---

## 🏗️ Public Works Pattern

### All Infrastructure via Abstractions

**Rule:** All infrastructure access must go through Public Works abstractions.

**Why:**
- Enables swappability (Redis → ArangoDB, etc.)
- Validates the abstraction pattern
- Keeps business logic separate from infrastructure

**What This Means:**
- ✅ Use `StateManagementAbstraction`, not direct Redis calls
- ✅ Use `FileStorageAbstraction`, not direct GCS calls
- ✅ Use `AuthAbstraction`, not direct Supabase calls
- ✅ Use adapters via abstractions, not directly
- ❌ No direct infrastructure calls in business logic
- ❌ No infrastructure dependencies in domain services
- ❌ No hard-coded infrastructure URLs/credentials

**Exception:** Adapters can call infrastructure directly (that's their job).

---

## 📐 Architecture Guide Wins

### Code Must Match Architecture

**Rule:** If code conflicts with the architecture guide, the architecture guide is correct.

**Why:**
- Architecture guide is the source of truth
- Code can be wrong, architecture guide is canonical
- Prevents architectural drift

**What This Means:**
- ✅ Code must follow architecture guide
- ✅ If code doesn't match, fix the code
- ✅ Architecture guide is updated only through ADRs
- ❌ No "pragmatic" deviations from architecture
- ❌ No "temporary" architectural violations

**Process:**
1. If code conflicts with architecture, fix code
2. If architecture needs to change, create ADR
3. If unsure, ask (don't guess)

---

## 🎯 Code Quality Standards

### Type Safety

- ✅ All functions have type hints
- ✅ All classes have type hints
- ✅ Use `typing.Protocol` for contracts
- ✅ Use `@dataclass` for structured data
- ✅ Validate with mypy (no errors)

### Async First

- ✅ All I/O operations are async
- ✅ Use `async/await` consistently
- ✅ No blocking I/O in async functions

### Error Handling

- ✅ All errors are handled explicitly
- ✅ All errors are logged
- ✅ All errors return proper error responses
- ❌ No silent failures
- ❌ No bare `except:` clauses

### Documentation

- ✅ All public functions have docstrings
- ✅ All classes have docstrings
- ✅ Docstrings explain WHAT and HOW
- ✅ Complex logic has inline comments

---

## 🚦 Development Process

### Before Starting Work

1. Read architecture guide
2. Read platform rules (this document)
3. Check current state documentation
4. Review execution plan
5. Understand dependencies

### During Development

1. Follow architecture guide strictly
2. Write working code (no stubs)
3. Write tests (tests must fail if code has cheats)
4. Use Public Works abstractions
5. Document decisions (ADRs if architectural)

### After Completing Work

1. Update checklists
2. Update current state documentation
3. Run all tests (must pass)
4. Verify no cheats/stubs remain
5. Document any new patterns

---

## ❌ Anti-Patterns (Forbidden)

### Code Anti-Patterns

- ❌ **Stubs:** `pass`, `raise NotImplementedError`, `# TODO`
- ❌ **Cheats:** Hard-coded values, mock data in production code
- ❌ **Placeholders:** Unresolved placeholders that persist
- ❌ **Direct Infrastructure:** Direct Redis/DB calls in business logic
- ❌ **Architectural Violations:** Code that doesn't match architecture guide

### Test Anti-Patterns

- ❌ **Tests That Pass with Cheats:** Tests that pass when code has stubs
- ❌ **Mock Everything:** Tests that mock all dependencies (no real integration)
- ❌ **Skipped Tests:** Tests marked as skipped without good reason
- ❌ **False Positives:** Tests that pass when they should fail

### Process Anti-Patterns

- ❌ **Pragmatic Deviations:** "Just this once" architectural violations
- ❌ **Temporary Solutions:** Solutions that become permanent
- ❌ **Backwards Compatibility:** Supporting old patterns "just in case"
- ❌ **Undocumented Decisions:** Changes without ADRs or documentation

---

## ✅ What Good Looks Like

### Good Code

```python
async def get_data(self, tenant_id: str) -> List[Dict[str, Any]]:
    """
    Get data for tenant.
    
    Uses StateManagementAbstraction to retrieve data from durable storage.
    Returns empty list if no data exists.
    
    Args:
        tenant_id: Tenant identifier
        
    Returns:
        List of data dictionaries
    """
    if not tenant_id:
        raise ValueError("tenant_id is required")
    
    state = await self.state_abstraction.get_state(
        tenant_id=tenant_id,
        key="data"
    )
    
    return state.get("items", [])
```

### Good Test

```python
async def test_get_data_returns_data(test_state_abstraction):
    """Test that get_data returns data from state abstraction."""
    service = DataService(state_abstraction=test_state_abstraction)
    
    # Setup: Store data
    await test_state_abstraction.set_state(
        tenant_id="test_tenant",
        key="data",
        state={"items": [{"id": "1", "value": "test"}]}
    )
    
    # Execute
    result = await service.get_data("test_tenant")
    
    # Verify
    assert len(result) == 1
    assert result[0]["id"] == "1"
    assert result[0]["value"] == "test"
```

### Good Architecture Compliance

- ✅ Domain service uses Runtime Participation Contract
- ✅ All infrastructure via Public Works abstractions
- ✅ No direct DB writes (uses Runtime artifacts)
- ✅ No orchestration in domain services (uses Runtime sagas)
- ✅ All execution via Runtime

---

## 📝 Checklist for Every Change

Before submitting code, verify:

- [ ] Code works (no stubs/cheats)
- [ ] Tests pass (and would fail if code had cheats)
- [ ] Uses Public Works abstractions (no direct infrastructure)
- [ ] Matches architecture guide
- [ ] Has type hints
- [ ] Has docstrings
- [ ] Handles errors properly
- [ ] No backwards compatibility code
- [ ] Documented in execution checklist
- [ ] Current state documentation updated

---

## 🎯 Remember

> **We're building a platform that works.**
> 
> No shortcuts.  
> No cheats.  
> No backwards compatibility baggage.  
> No tests that pass with stubs.
>
> **Working code only.**

---

**If you're unsure about a rule, ask. Don't guess. Don't "just this once".**
