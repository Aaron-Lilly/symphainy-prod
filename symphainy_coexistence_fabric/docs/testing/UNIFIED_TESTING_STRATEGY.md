# Unified Testing Strategy

**Status:** Canonical (January 2026)
**Authors:** Team A + Team B with CTO Alignment
**Purpose:** Define a balanced testing approach that validates both boundaries (probes) and correctness (traditional tests)

---

## Core Principle

> **Probes validate contracts at boundaries. Traditional tests validate correctness within boundaries.**

Neither approach alone is sufficient. Together they provide confidence that:
1. The system **wires correctly** (probes)
2. The system **computes correctly** (traditional tests)
3. Failures are **explicit and documented** (§8A enforcement)

---

## 1. Testing Vocabulary

| Term | Definition | Example |
|------|------------|---------|
| **Seam** | A boundary between components where wiring can succeed or fail | Platform SDK → Public Works |
| **Probe** | A test that validates a seam works in BOTH directions (success + failure) | "Service raises §8A when dependency missing" |
| **Contract Test** | A test that validates the interface between components | "Protocol method returns expected shape" |
| **Unit Test** | A test that validates logic within a single component | "Parser correctly extracts fields from CSV" |
| **Integration Test** | A test that validates multiple components working together | "Ingest → Parse → Store flow completes" |
| **E2E Test** | A test that validates a complete user journey | "User uploads file, sees insights" |
| **§8A Violation** | Silent degradation — returning None/empty/default when dependency is missing | ❌ Anti-pattern |

---

## 2. The Testing Pyramid (Revised)

```
                    ┌─────────────┐
                    │   E2E       │  Few, expensive, high confidence
                    │   Tests     │  Full user journeys
                    ├─────────────┤
                    │ Integration │  Cross-component flows
                    │   Tests     │  Real or realistic infrastructure
                ┌───┴─────────────┴───┐
                │   Contract Tests    │  Interface validation
                │   (Probe + Shape)   │  Success AND failure paths
            ┌───┴─────────────────────┴───┐
            │       Unit Tests            │  Business logic, algorithms
            │   (Traditional + Fast)      │  Mocked dependencies OK
        ┌───┴─────────────────────────────┴───┐
        │         Seam Probes                  │  Boundary validation
        │   (Success + Failure + §8A)          │  Foundation of trust
        └─────────────────────────────────────┘
```

---

## 3. When to Use Each Test Type

### Seam Probes (Boundary Validation)

**Use for:**
- Platform SDK ctx services
- Capability service dependency wiring
- Protocol availability after boot
- Cross-domain sovereignty checks
- Agent/LLM availability

**Pattern:**
```python
class TestMyServiceSeam:
    """Probe: MyService seam validation."""
    
    def test_raises_when_dependency_missing(self):
        """FAILURE PATH: Missing dependency → RuntimeError with §8A."""
        service = MyService(dependency=None)
        with pytest.raises(RuntimeError) as exc:
            service.execute()
        assert "Platform contract §8A" in str(exc.value)
    
    @pytest.mark.requires_infra
    def test_succeeds_when_dependency_wired(self, genesis_services):
        """SUCCESS PATH: Wired dependency → operation proceeds."""
        if genesis_services is None:
            pytest.skip("Infrastructure not available")
        # ... test with real dependency
```

**Coverage goal:** Every seam has both success and failure probes.

---

### Contract Tests (Interface Validation)

**Use for:**
- Protocol method signatures
- API response shapes
- Event payload structures
- Inter-service contracts

**Pattern:**
```python
class TestProtocolContract:
    """Contract: StateManagementProtocol interface."""
    
    def test_retrieve_state_returns_expected_shape(self):
        """Protocol method returns documented shape."""
        result = protocol.retrieve_state(session_id, tenant_id)
        assert isinstance(result, dict)
        assert "session_id" in result or result == {}
    
    def test_store_state_accepts_documented_params(self):
        """Protocol method accepts documented parameters."""
        # Should not raise TypeError
        protocol.store_state(
            session_id="test",
            tenant_id="test", 
            state={"key": "value"}
        )
```

**Coverage goal:** Every protocol/interface has contract tests.

---

### Unit Tests (Logic Validation)

**Use for:**
- Business logic within services
- Data transformation algorithms
- Parsing logic
- Calculation correctness
- Edge cases within a component

**Pattern:**
```python
class TestParsingLogic:
    """Unit: CSV parsing logic."""
    
    def test_parses_standard_csv(self):
        """Standard CSV parsed correctly."""
        result = parse_csv(SAMPLE_CSV)
        assert result["rows"] == 3
        assert result["columns"] == ["a", "b", "c"]
    
    def test_handles_empty_csv(self):
        """Empty CSV returns empty result."""
        result = parse_csv("")
        assert result["rows"] == 0
    
    def test_handles_malformed_csv(self):
        """Malformed CSV raises ParseError with details."""
        with pytest.raises(ParseError) as exc:
            parse_csv(MALFORMED_CSV)
        assert "line 3" in str(exc.value)
```

**Coverage goal:** Business logic has thorough unit tests including edge cases.

---

### Integration Tests (Flow Validation)

**Use for:**
- Multi-service flows
- Journey execution
- Cross-capability operations
- Real infrastructure validation

**Pattern:**
```python
class TestIngestToInsightFlow:
    """Integration: Content → Insights flow."""
    
    @pytest.mark.requires_infra
    def test_uploaded_file_produces_insights(self, genesis_services):
        """File upload → parse → analyze produces insights."""
        # Upload
        file_id = await content_service.ingest(file_data)
        
        # Parse
        parsed = await content_service.parse(file_id)
        assert parsed["status"] == "success"
        
        # Analyze
        insights = await insights_service.analyze(parsed["artifact_id"])
        assert insights["quality_score"] is not None
```

**Coverage goal:** Critical flows have integration tests with real infrastructure.

---

### E2E Tests (Journey Validation)

**Use for:**
- Complete user journeys
- Demo critical paths
- Regression prevention

**Pattern:**
```python
class TestContentPillarJourney:
    """E2E: Content pillar user journey."""
    
    @pytest.mark.e2e
    def test_user_uploads_and_sees_insights(self, browser):
        """User can upload file and view generated insights."""
        # Navigate
        browser.goto("/content")
        
        # Upload
        browser.upload_file("#file-input", TEST_FILE)
        browser.click("#upload-button")
        
        # Wait for processing
        browser.wait_for("#insights-panel")
        
        # Verify
        assert browser.text("#quality-score") != "N/A"
```

**Coverage goal:** Each pillar/solution has E2E tests for critical paths.

---

## 4. Test Organization

```
tests/
├── probes/                      # Seam probes (boundary validation)
│   ├── platform_sdk/
│   │   ├── test_governance_service_seam.py
│   │   ├── test_reasoning_service_seam.py
│   │   └── test_platform_service_seam.py
│   ├── capabilities/
│   │   ├── test_content_services_seam.py
│   │   ├── test_insights_services_seam.py
│   │   └── ...
│   └── sovereignty/
│       ├── test_curator_seam.py
│       └── test_cross_domain_seam.py
│
├── contracts/                   # Contract tests (interface validation)
│   ├── protocols/
│   │   ├── test_state_protocol_contract.py
│   │   └── ...
│   └── api/
│       └── test_experience_sdk_contract.py
│
├── unit/                        # Unit tests (logic validation)
│   ├── parsing/
│   ├── analysis/
│   └── transformation/
│
├── integration/                 # Integration tests (flow validation)
│   ├── content_to_insights/
│   ├── journey_execution/
│   └── sovereignty_enforcement/
│
├── e2e/                         # E2E tests (journey validation)
│   ├── content_pillar/
│   ├── insights_pillar/
│   └── demo_paths/
│
└── 3d/                          # Team A's existing structure
    ├── compliance/              # Platform contract probes
    ├── real_infrastructure/     # Real infra integration
    └── startup/                 # Genesis/boot tests
```

---

## 5. Test Markers

```python
# pytest markers for test categorization

# Infrastructure requirements
@pytest.mark.requires_infra      # Needs real infrastructure
@pytest.mark.requires_llm        # Needs LLM access
@pytest.mark.requires_db         # Needs database

# Test type
@pytest.mark.probe              # Seam probe test
@pytest.mark.contract           # Contract test
@pytest.mark.unit               # Unit test
@pytest.mark.integration        # Integration test
@pytest.mark.e2e                # End-to-end test

# Speed
@pytest.mark.fast               # < 100ms
@pytest.mark.slow               # > 1s

# Criticality
@pytest.mark.critical           # Must pass for deploy
@pytest.mark.demo               # Demo critical path
```

---

## 6. CI Pipeline Strategy

### Fast Feedback (Every Commit)

```yaml
fast-tests:
  runs:
    - probes (failure paths only - no infra needed)
    - contracts
    - unit tests
  time: < 2 minutes
  blocks: merge
```

### Full Validation (PR Merge)

```yaml
full-tests:
  runs:
    - all fast tests
    - probes (success paths - with infra)
    - integration tests
  time: < 10 minutes
  blocks: merge to main
```

### Nightly/Release

```yaml
comprehensive-tests:
  runs:
    - all tests
    - e2e tests
    - performance benchmarks
  time: < 30 minutes
  blocks: release
```

---

## 7. Coverage Requirements

| Test Type | Coverage Target | Enforcement |
|-----------|----------------|-------------|
| **Seam Probes** | Every public seam | PR review checklist |
| **Contract Tests** | Every protocol/API | PR review checklist |
| **Unit Tests** | 80% of business logic | Coverage tool |
| **Integration Tests** | Critical flows | Demo checklist |
| **E2E Tests** | Each pillar happy path | Release checklist |

---

## 8. Writing Tests: Decision Tree

```
Is this testing a BOUNDARY between components?
├── YES → Write a SEAM PROBE
│         - Test success path (dependency wired)
│         - Test failure path (dependency missing → §8A)
│
└── NO → Is this testing an INTERFACE contract?
         ├── YES → Write a CONTRACT TEST
         │         - Test method signatures
         │         - Test return shapes
         │
         └── NO → Is this testing BUSINESS LOGIC?
                  ├── YES → Write a UNIT TEST
                  │         - Test algorithm correctness
                  │         - Test edge cases
                  │         - Mock dependencies OK
                  │
                  └── NO → Is this testing a FLOW?
                           ├── YES (multi-component) → INTEGRATION TEST
                           └── YES (user journey) → E2E TEST
```

---

## 9. §8A Enforcement Checklist

When writing a new service, verify:

- [ ] Service constructor accepts dependencies (not fetches them)
- [ ] Missing required dependency → `RuntimeError` with "Platform contract §8A"
- [ ] No silent return of `None`, `[]`, `{}`, `False` when dependency missing
- [ ] Seam probe exists for failure path
- [ ] Seam probe exists for success path

---

## 10. Test Documentation Template

Each test file should have a header explaining its purpose:

```python
"""
[Test Type]: [Component] [aspect being tested]

Layer: Probe | Contract | Unit | Integration | E2E
Seam: [If probe, which boundary]
Dependencies: [What infrastructure/fixtures needed]

Tests:
- test_X: [What it validates]
- test_Y: [What it validates]

Related:
- [Link to architecture doc]
- [Link to related tests]
"""
```

---

## 11. Summary

| Question | Answer |
|----------|--------|
| When do I write a probe? | When testing a boundary between components |
| When do I write a unit test? | When testing logic within a component |
| When do I write an integration test? | When testing a flow across components |
| What's the §8A rule? | Never silently degrade - raise explicit errors |
| What runs on every commit? | Probes (failure), contracts, units |
| What runs on PR merge? | All above + probes (success), integration |

---

## References

- [PLATFORM_PROBE_APPROACH.md](PLATFORM_PROBE_APPROACH.md) — Team A's probe strategy
- [PLATFORM_SEAMS.md](PLATFORM_SEAMS.md) — Platform boundary definitions
- [PLATFORM_CONTRACT.md](../architecture/PLATFORM_CONTRACT.md) — §8A and contract rules
- [PROTOCOL_REGISTRY.md](../architecture/PROTOCOL_REGISTRY.md) — Protocol stability rules
