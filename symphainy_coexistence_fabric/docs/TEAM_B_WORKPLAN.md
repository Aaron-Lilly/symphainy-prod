# Team B (Landing) Workplan

**Status:** Active (January 2026)  
**Owner:** Team B  
**Dependencies:** Team A intercept wiring, Team C frontend

---

## Current State

| Component | Status | Notes |
|-----------|--------|-------|
| Platform SDK (ctx) | ✅ Complete | PlatformContext, factory, 4 services |
| PlatformIntentService | ✅ Complete | Base class for all new services |
| Capability Services (52) | ✅ Complete | Content, Security, Coexistence, Insights, Operations, Outcomes, Control Tower |
| AI Agents (15+) | ✅ Complete | Real LLM, not keyword matching |
| Architecture Docs | ✅ Complete | All canonical docs pushed |
| Disposable Wrapper Compliance | ⚠️ Needs Audit | Per Team A request |

---

## Workplan

### Phase 1: Team A Support (Priority: Immediate)

**Goal:** Unblock Team A's intercept wiring by ensuring our code is compliant and well-documented.

#### Task 1.1: Disposable Wrapper Audit ✅ DONE
- [x] Document the Disposable Wrapper Pattern
- [x] Audit PlatformService methods
- [x] Audit GovernanceService properties
- [x] Audit ReasoningService methods
- [x] Document method signatures for Team A reference

**Deliverable:** `docs/architecture/DISPOSABLE_WRAPPER_PATTERN.md`

#### Task 1.2: Review Flagged Items
- [ ] Review `create_deterministic_embeddings()` in PlatformService
  - Issue: Creates internal ExecutionContext
  - Decision: Is this "light shaping" or should context come from caller?
  - Action: If problematic, refactor to receive context as parameter
  
- [ ] Review `AgentService._lazy_instantiate_agent()` in ReasoningService
  - Issue: Dynamic import and instantiation logic
  - Decision: Is initialization logic acceptable in wrapper?
  - Action: If problematic, move to factory pattern owned by Team A

- [ ] Review `AgentService.collaborate()` in ReasoningService
  - Issue: Orchestration logic (sequential agent calls)
  - Decision: Should this be in wrapper or higher layer?
  - Action: If problematic, move to a collaboration orchestrator

**Estimated Time:** 2-4 hours

#### Task 1.3: Integration Test Preparation
- [ ] Create a minimal integration test that Team A can use to verify wiring:

```python
# tests/integration/test_intercept_path.py

async def test_ingest_file_intercept():
    """
    Verify: Runtime → PlatformContextFactory → ctx → IngestFileService
    
    Team A runs this to confirm wiring is complete.
    """
    # 1. Create mock intent
    intent = Intent(
        intent_type="ingest_file",
        tenant_id="test_tenant",
        session_id="test_session",
        solution_id="test_solution",
        parameters={
            "file_data": b"test content",
            "source_metadata": {"ui_name": "test.txt", "file_type": "text"}
        }
    )
    
    # 2. Submit through Runtime (Team A's code)
    # execution_id = await runtime.execute(intent)
    
    # 3. Verify our service executed
    # assert result.status == "success"
    # assert result.artifacts.get("file_id") is not None
```

- [ ] Create verification points Team A can check:
  1. Handler lookup succeeds for `ingest_file`
  2. `uses_platform_context` flag is True
  3. `PlatformContextFactory.create_context()` is called
  4. `ctx.platform` is not None
  5. Service returns expected structure

**Estimated Time:** 2-3 hours

---

### Phase 2: Service Validation (Priority: High)

**Goal:** Ensure all 52 services are correctly registered and callable.

#### Task 2.1: Service Registration Audit
- [ ] Verify all services in `service_factory.py` are registered
- [ ] Verify intent_type → service mapping is correct
- [ ] Verify `uses_platform_context: True` is set for all new services

**Checklist:**

| Capability | Services | Registered? |
|------------|----------|-------------|
| Content | 10 | ⬜ Verify |
| Security | 7 | ⬜ Verify |
| Coexistence | 7 | ⬜ Verify |
| Insights | 7 | ⬜ Verify |
| Operations | 6 | ⬜ Verify |
| Outcomes | 6 | ⬜ Verify |
| Control Tower | 9 | ⬜ Verify |

**Estimated Time:** 1-2 hours

#### Task 2.2: Service Contract Validation
- [ ] For each service, verify:
  - `execute(ctx)` method exists and is async
  - Required parameters are validated
  - Return structure matches `{artifacts, events, status}`
  - Error handling returns `{status: "failed", error: "..."}`

**Estimated Time:** 2-3 hours

---

### Phase 3: AI Agent Validation (Priority: High)

**Goal:** Ensure all AI agents work correctly when invoked via `ctx.reasoning.agents.invoke()`.

#### Task 3.1: Agent Registry Audit
- [ ] Verify all agents in `AgentService._AGENT_CLASSES` mapping
- [ ] Verify agent class paths are correct
- [ ] Verify agents can be lazily instantiated

**Agent Checklist:**

| Agent | Mapped? | Instantiates? |
|-------|---------|---------------|
| GuideAgent | ⬜ | ⬜ |
| ContentLiaisonAgent | ⬜ | ⬜ |
| InsightsLiaisonAgent | ⬜ | ⬜ |
| OperationsLiaisonAgent | ⬜ | ⬜ |
| OutcomesLiaisonAgent | ⬜ | ⬜ |
| SOPGenerationAgent | ⬜ | ⬜ |
| CoexistenceAnalysisAgent | ⬜ | ⬜ |
| BlueprintCreationAgent | ⬜ | ⬜ |
| RoadmapGenerationAgent | ⬜ | ⬜ |
| POCGenerationAgent | ⬜ | ⬜ |
| OutcomesSynthesisAgent | ⬜ | ⬜ |
| InsightsEDAAgent | ⬜ | ⬜ |
| BusinessAnalysisAgent | ⬜ | ⬜ |
| WorkflowOptimizationAgent | ⬜ | ⬜ |

**Estimated Time:** 2-3 hours

#### Task 3.2: LLM Integration Test
- [ ] Verify OpenAI adapter is accessible via `ctx.reasoning.llm`
- [ ] Test a simple completion call
- [ ] Verify error handling when LLM unavailable

**Estimated Time:** 1-2 hours

---

### Phase 4: Integration Readiness (Priority: Medium)

**Goal:** Be ready for end-to-end testing when Team A completes wiring.

#### Task 4.1: Create Integration Test Suite
- [ ] Test each capability area with one representative intent:
  - `ingest_file` (Content)
  - `authenticate_user` (Security)
  - `initiate_guide_agent` (Coexistence)
  - `assess_data_quality` (Insights)
  - `generate_sop` (Operations)
  - `create_blueprint` (Outcomes)
  - `get_system_health` (Control Tower)

**Estimated Time:** 4-6 hours

#### Task 4.2: Error Scenario Testing
- [ ] Test §8A compliance (missing dependencies raise RuntimeError)
- [ ] Test invalid parameter handling
- [ ] Test tenant isolation (if Team A has implemented baseline)

**Estimated Time:** 2-3 hours

---

### Phase 5: Documentation Finalization (Priority: Low)

**Goal:** Ensure all documentation is complete and accurate.

#### Task 5.1: Update Service Documentation
- [ ] Document all 52 service intent types
- [ ] Document expected parameters for each
- [ ] Document return structures

#### Task 5.2: Update Architecture Documentation
- [ ] Verify all docs reference correct file paths
- [ ] Ensure diagrams match implementation
- [ ] Add any missing cross-references

**Estimated Time:** 3-4 hours

---

## Timeline

| Phase | Est. Time | Dependencies | Status |
|-------|-----------|--------------|--------|
| Phase 1: Team A Support | 4-7 hours | None | 🟡 In Progress |
| Phase 2: Service Validation | 3-5 hours | None | ⬜ Not Started |
| Phase 3: Agent Validation | 3-5 hours | None | ⬜ Not Started |
| Phase 4: Integration Readiness | 6-9 hours | Team A wiring | ⬜ Blocked |
| Phase 5: Documentation | 3-4 hours | None | ⬜ Not Started |

**Total Estimated Time:** 19-30 hours (3-4 days)

---

## Daily Standup Questions

1. **Wiring Status:** Has Team A completed the intercept path?
2. **Service Status:** Are our services being called correctly?
3. **Blocker Status:** What's preventing integration testing?

---

## Success Criteria

### For Team A Integration

- [ ] Team A can call `IngestFileService.execute(ctx)` and get a result
- [ ] Team A confirms all 52 services are reachable via intent submission
- [ ] Team A confirms `ctx` is properly constructed with all 4 services

### For MVP Demo

- [ ] All Content intents work
- [ ] All Security intents work (login flow)
- [ ] All Coexistence intents work (chat with agents)
- [ ] All Insights intents work (data analysis)
- [ ] All Operations intents work (SOP generation)
- [ ] All Outcomes intents work (roadmap generation)
- [ ] Control Tower shows real platform data

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Team A wiring delayed | Focus on Phase 2-3 (internal validation) while waiting |
| Service registration errors | Audit against service_factory.py |
| Agent instantiation failures | Test lazy loading independently |
| LLM integration issues | Verify OpenAI adapter availability early |

---

## Appendix: Quick Reference

### Service Factory Location
```
symphainy_platform/runtime/service_factory.py
```

### Platform SDK Location
```
symphainy_platform/civic_systems/platform_sdk/
├── context.py              # PlatformContext, PlatformContextFactory
├── intent_service_base.py  # PlatformIntentService
└── services/
    ├── platform_service.py    # ctx.platform
    ├── governance_service.py  # ctx.governance
    └── reasoning_service.py   # ctx.reasoning
```

### Capability Services Location
```
symphainy_platform/capabilities/
├── content/          # 10 services
├── security/         # 7 services
├── coexistence/      # 7 services
├── insights/         # 7 services
├── operations/       # 6 services
├── outcomes/         # 6 services
└── control_tower/    # 9 services
```

### AI Agents Location
```
symphainy_platform/civic_systems/agentic/agents/
```
