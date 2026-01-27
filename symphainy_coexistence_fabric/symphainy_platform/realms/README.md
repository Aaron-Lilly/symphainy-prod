# Domain Services (Realms)

**Status:** Rebuild in Progress  
**Phase:** Phase 4 (Domain Services Rebuild)

---

## Purpose

Domain Services define **meaning, not mechanics**.

These are **SOA services** that contain the vast majority of functional logic.

---

## Canonical Domains

| Domain     | Owns                                          |
| ---------- | --------------------------------------------- |
| Content    | Ingest, parse, embeddings, canonical facts    |
| Insights   | Interpretation, analysis, mapping, querying   |
| Operations | SOPs, workflows, optimization recommendations |
| Outcomes   | Synthesis, roadmaps, POCs, proposals          |

---

## Runtime Participation Contract

Each domain service must:
* declare which **intents** it supports
* accept a **runtime execution context**
* return **artifacts and events**, not side effects
* never bypass Runtime for state, retries, or orchestration

```python
handle_intent(intent, runtime_context) → { artifacts, events }
```

---

## What Domain Services Do

✅ Implement rich internal logic
✅ Can be complex and opinionated
✅ Use Public Works abstractions
✅ Use Civic System SDKs

---

## What Domain Services Don't Do

❌ Own execution or state
❌ Orchestrate workflows
❌ Persist authoritative data
❌ Call infrastructure directly

---

## References

- [Architecture Guide](../../docs/architecture/north_star.md) - Section 2.3 Domain Services
- [Phase 4 Execution Plan](../../docs/execution/phase_4_execution_plan.md)
