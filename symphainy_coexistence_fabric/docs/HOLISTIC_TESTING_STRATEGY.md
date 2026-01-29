# SymphAIny Holistic Testing Strategy

**Context:** Platform locked (coexistence fabric). Hopefully at the 5-yard line; non-trivial risk that testing reveals we're closer to mid-field. Existing tests have passed; browser testing revealed issues. This strategy reuses and refactors current test assets—no reinventing the wheel—aligned with the discovery-first mindset in [new_testing_mindset.md](new_testing_mindset.md).

**Principle:** Discovery first, alignment second. Use tests as *probes* to learn where the system resists abstraction. When failures occur (in pytest, Docker, or browser), capture them in Stability/Gravity reports. Converge layer by layer; then lock intent (Hop 2).

---

## 1. Strategy at a Glance

| Phase | Goal | Use existing tests as… | Outcome |
|-------|------|------------------------|---------|
| **Hop 1: Discovery** | Map what works, what's fragile, what assumptions must hold | Probes per layer; every failure → report | Coherent map; convergence when patterns stabilize |
| **Hop 2: Commitment** | Enforce boundaries and contracts | Gates and regression guards | CI, contract map, safe velocity |

We are in **Hop 1**. Browser failures are *signal*—they tell us which seam (in-process vs HTTP, or which layer) we haven't yet documented. The strategy turns "tests pass but browser breaks" into structured reports so we know whether we're at the 5-yard line or mid-field.

---

## 2. Get started (first pass)

**Skepticism is valid:** Passing tests alone may not uncover missing insights. The point of this pass is to (a) run the stack in a consistent order so we *see* where things break (including in the browser), and (b) capture every failure in a Stability/Gravity report so we can evolve the approach from what we find.

**Ready to start:**

1. **Run the bottom layer** (platform behavior):
   ```bash
   pytest tests/3d/startup/ -v
   ```
   If anything fails or behaves oddly → copy [docs/testing/stability_gravity_reports/_TEMPLATE.md](testing/stability_gravity_reports/_TEMPLATE.md) to `docs/testing/stability_gravity_reports/YYYYMMDD_platform_<brief>.md` and fill it. Don’t fix yet—record.

2. **Run browser / critical path** (where you’ve seen issues before):
   - Start the app (e.g. `python runtime_main.py` or your usual run), then exercise the flow that broke (e.g. login, guide agent, file upload).
   - When something breaks → same thing: create a Stability/Gravity report. Scope = layer where you think the failure belongs (e.g. `browser_guide_agent` or `civic_auth`). Hypotheses only.

3. **Review after first pass:** Do reports point at the same boundary (e.g. in-process vs HTTP, or a specific service)? Then we’re learning. If not, we iterate: run more probes (other layers, Docker, different env) and keep reporting. Evolve the approach based on what we uncover.

**Evolving:** If passing tests never surface the real issues, the reports from browser failures *are* the discovery. The layered order then helps us map those failures to a layer and decide what to fix or freeze first.

---

## 4. Current Test Asset Map

Existing tests map to the layered convergence stack as follows. **Reuse** these; **refactor** only to add layer tags and a consistent failure→report workflow.

| Layer | Existing tests | Location | Role in strategy |
|-------|----------------|----------|--------------------|
| **Lock platform behavior** | Startup, config, entry point | `tests/3d/startup/`, `runtime_main.py` trace | Probe: process start → first successful response; env, order, deps |
| **Public Works** | Integration (platform services), real infra connectivity | `tests/3d/integration/`, `tests/3d/real_infrastructure/test_real_infrastructure_connectivity.py` | Probe: adapters, Redis, Arango, storage in isolation and together |
| **Curator** | Solution registry, artifact flows | `tests/3d/integration/test_solution_registry.py`, journey/artifact tests | Probe: registry, metadata, lineage assumptions |
| **Civic Systems** | Security, auth, tenant isolation, agents | `tests/3d/security/`, `tests/3d/agents/` | Probe: policy enforcement, auth, agentic boundaries |
| **Contracts vs reality** | (No dedicated suite) | — | Manual + Cursor: compare `docs/solution_contracts`, `docs/journey_contracts`, `docs/intent_contracts` to observed behavior |
| **Solution / Journey / Realm** | Solution, journey, intent tests (3d) | `tests/3d/solution/`, `tests/3d/journey/**/`, `tests/3d/intent/**/` | Probe: does implementation match declared contracts? Happy path vs workaround |
| **Browser / E2E** | E2E demo paths, real_infrastructure critical paths | `tests/e2e/demo_paths/`, `tests/3d/real_infrastructure/test_demo_critical_paths.py` | Verification: does end-to-end match documented reality? |

**Horizontal (cross-layer) probes:** E2E and real_infrastructure demo paths (guide agent, file-to-insight, auth, control tower, POC-to-roadmap, security) are the primary horizontal journeys. Run these after layer probes to expose coupling.

---

## 5. Layered Probe Order (Hop 1)

Run probes **bottom-up**. At each layer, run the corresponding tests; on **any** failure (or unexpected behavior), produce a **Stability/Gravity report** (see Section 7). Do not fix yet—record. Classify: *architectural signal* vs *operational noise* (e.g. transient Docker order).

### 5.1 Run sequence

1. **Lock platform behavior**
   - Trace: `runtime_main.py` → `get_env_contract()` → `create_runtime_services()` → `create_fastapi_app()` → first HTTP response.
   - Run: `tests/3d/startup/` (e.g. `test_solution_initializer.py`).
   - Probe: Startup with different env (missing vars, wrong order); optional: Docker vs local.
   - Ask: Where do symptoms appear (startup, first request, logs)? Order-dependent?

2. **Public Works**
   - Run: `pytest tests/3d/integration/test_platform_services.py -v`
   - Run: `pytest tests/3d/real_infrastructure/test_real_infrastructure_connectivity.py -v -m sre` (with real Redis/Arango up).
   - Ask: Misconfiguration in foundation vs true architectural instability?

3. **Curator**
   - Run: `pytest tests/3d/integration/test_solution_registry.py -v`
   - Run journey tests that touch artifacts/registry (e.g. file_upload, artifact flows).
   - Ask: Implicit assumptions about artifacts, metadata, lineage?

4. **Civic Systems**
   - Run: `pytest tests/3d/security/ -v`, `pytest tests/3d/agents/ -v`
   - Ask: Policy enforcement gaps, contract mismatches at runtime?

5. **Contracts vs reality**
   - No automated suite. Compare:
     - `docs/solution_contracts/`, `docs/journey_contracts/`, `docs/intent_contracts/`
     - vs actual behavior (from steps 1–4 and 6–7).
   - Decide per contract: foundation fragile vs contract overambitious; list mismatches in reports.

6. **Solution / Journey / Realm**
   - Run: `pytest tests/3d/solution/ -v`, `pytest tests/3d/journey/ -v`, `pytest tests/3d/intent/ -v` (use mocks where intended).
   - Map: Which happy paths exist vs workaround logic; traceability contract → implementation → observed behavior.

7. **Browser / E2E**
   - Run: `pytest tests/e2e/demo_paths/ -v`; `pytest tests/3d/real_infrastructure/ -v -m functional` or `-m critical` (with app and infra up if required).
   - Lens: Does end-to-end match the emergent reality we've documented? Failures here = remaining edge-case misalignments; map to a layer and report.

8. **Horizontal journeys**
   - Run full flows: e.g. Guide Agent, File → Insight, Auth, Control Tower, POC → Roadmap.
   - Use e2e + real_infrastructure critical paths. Feed any new failure into Stability/Gravity and layer mapping.

### 5.2 When to fix

- **During discovery:** Prefer *probe again with variation* or *defer intentionally* over immediate fix. If you must fix to unblock the next probe, still write the report first (hypotheses only; then fix and note "fixed after report").
- **After convergence (per seam):** Fixes become intentional; then freeze and document (Hop 2).

---

## 6. Reuse and Refactor (What to Change)

- **Keep:** All existing test modules, markers (`real_infrastructure`, `sre`, `functional`, `critical`, `llm`, `integration`), fixtures (3d conftest, real_infrastructure conftest), and run commands.
- **Add (minimal):**
  - **Layer markers** (optional but useful): e.g. `@pytest.mark.layer_platform`, `@pytest.mark.layer_public_works`, … so you can run `pytest -m layer_public_works` for that layer. Add to `pyproject.toml` and tag tests as you run probes.
  - **Failure → report workflow:** When a test fails or behavior is wrong (including in browser), create one Stability/Gravity report and link it (e.g. in a `docs/testing/reports/` dir or in the report filename with epoch/layer).
  - **Single place for reports:** [docs/testing/stability_gravity_reports/](testing/stability_gravity_reports/README.md) with naming like `YYYYMMDD_layer_shortname_brief.md` so Cursor and humans know where to append. Copy [\_TEMPLATE.md](testing/stability_gravity_reports/_TEMPLATE.md) to create each report.
- **Do not:** Rewrite tests to "fit" the philosophy; run them as-is and use their failures as input to reports. Do not add CI gates that block on "all green" until after Hop 1 convergence.

---

## 7. Stability/Gravity Report (Short Form)

Use this for every failure or instability. Full template and Cursor prompt are in [new_testing_mindset.md](new_testing_mindset.md).

```markdown
## Stability & Gravity Report
**Scope:** <layer or service>  
**Epoch:** <date or iteration>

**A. What was probed**  
- Change/trigger:  
- Expected impact:  

**B. Observed behavior**  
- What broke; where (browser / logs / startup / runtime / network); time to failure:  

**C. Stability (yes/no + short)**  
- Unrelated components broke? Restart "fixed" it? Order change moved failure? Config had outsized effect?  

**D. Gravity (yes/no + short)**  
- Logic migrated to one place? Agents needed extra context? Responsibilities blurred? Fix touched many files?  

**E. Hypotheses (do not resolve here)**  
- Unstable boundary:  
- Missing contract:  
- Premature abstraction:  

**F. Classification**  
[ ] Collapsing abstraction  [ ] Leaky boundary  [ ] Stable seam  [ ] Unknown / need more probes  

**G. Recommendation**  
Probe again with variation | Isolate behind temporary adapter | Freeze and document | Defer intentionally  
```

Save under [docs/testing/stability_gravity_reports/](testing/stability_gravity_reports/README.md) with naming `YYYYMMDD_<layer>_<short_description>.md`.

---

## 8. Convergence and Hop 2

**You've converged (Hop 1 done) when:**

- Failures repeat in recognizable patterns.
- You can predict what will break before running.
- Certain files/services are obvious "centers of gravity."
- Stability reports stop producing new hypotheses for the seams you care about for deployment.

**Then (Hop 2):**

- Freeze: service boundaries, ownership, runtime lifecycle, config surfaces.
- Formalize: update solution/journey/intent contracts to match observed reality; produce Architectural Intent doc and System Contract Map.
- Enforce: add minimal CI gates, promotion rules, golden-path tenant config. Use Cursor in "Architectural Commitment Mode" (see new_testing_mindset.md).

**5-yard line vs mid-field:** If after one full bottom-up pass plus horizontal journeys you have few reports and most are "superficial config" or "noise," you're likely near the 5-yard line. If the same boundaries keep appearing (e.g. "in-process vs HTTP" or "PublicWorks/Curator contract"), you're closer to mid-field—converge on those seams first, then reassess.

---

## 7. Quick Reference

| Task | Command / action |
|------|------------------|
| Run by layer (examples) | `pytest tests/3d/startup/ -v`; `pytest tests/3d/integration/ -v`; `pytest tests/3d/journey/ -v`; `pytest tests/3d/solution/ -v`; `pytest tests/3d/intent/ -v` |
| Run by layer marker (optional) | After tagging tests with `@pytest.mark.layer_platform` etc., use `pytest -m layer_public_works -v`. Markers defined in `pyproject.toml`. |
| Real infra (SRE) | `pytest tests/3d/real_infrastructure/ -v -m sre` (Redis/Arango up) |
| Critical demo paths | `pytest tests/3d/real_infrastructure/ -v -m critical`; `pytest tests/e2e/demo_paths/ -v` |
| Full 3d (no real infra) | `pytest tests/3d/ -v` (exclude `real_infrastructure` or use `-m "not real_infrastructure"` if desired) |
| On failure | Create Stability/Gravity report; link to layer; do not fix yet (or fix only after report and note it). |
| Cursor mode | Discovery: "Architectural Discovery Mode" (new_testing_mindset.md). After convergence: "Architectural Commitment Mode." |

---

## 10. Summary

- **Reuse** all current tests; treat them as **probes** in a bottom-up, layer-by-layer order.
- **Refactor** minimally: optional layer markers, a failure→report workflow, and a dedicated directory for Stability/Gravity reports.
- **Browser** is verification; when it breaks, that's signal—map to a layer and report.
- **Converge** when patterns stabilize and hypotheses stop changing; then **lock** (Hop 2) and add CI/gates.
- This strategy is aligned with [new_testing_mindset.md](new_testing_mindset.md) and is designed to get you from "tests pass, browser doesn't" to a clear picture of where you stand (5-yard line vs mid-field) and what to freeze for deployment.
