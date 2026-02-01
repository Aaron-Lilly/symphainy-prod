# Foundation Contract Pass Strategy

**Status:** Canonical (January 2026)  
**Purpose:** How to approach the "mess under the covers" we found for Curator (and the risk of similar gaps under Genesis/Public Works) without relying only on "fix in context as we work up the stack."

**Related:** [MEET_IN_THE_MIDDLE_PLAN.md](MEET_IN_THE_MIDDLE_PLAN.md), [CURATOR_INFRASTRUCTURE_ALIGNMENT.md](CURATOR_INFRASTRUCTURE_ALIGNMENT.md), [CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN.md](CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN.md).

---

## 1. What We Learned

Even after "successful" refactoring of Genesis and Public Works, we found a **mess under the covers** for Curator:

- CuratorSDK stubs (register_capability, discover_agents, get_domain_registry) with no backing
- Two unconnected Curator worlds (CuratorSDK vs CuratorFoundationService)
- RegistryAbstraction missing methods that callers expect (list_files, get_registry_entry, register_entry, list_registry_entries)
- list_files called on registry_abstraction in several places → AttributeError (we fixed these to use file_storage)
- semantic_profile_registry broken (expects RegistryAbstraction methods that don't exist)
- CuratorService return-value bug (registry_id vs id_field) — fixed

Similar gaps may exist elsewhere: adapter leaks, wrong getters, missing protocols. So **"fix in context as we work up the stack"** is workable only if we (a) remember we're doing it and (b) retest everything as we move up—which is easy to forget and expensive.

---

## 2. Recommended Approach: Foundation Contract Pass

Don't rely on fix-in-context alone. Treat **foundations** as a **contract boundary**.

### 2.1 Foundation Contract Pass (Step 2, deliberate)

Before depending on foundations from Runtime and Civic, complete a **single, explicit** pass:

1. **Define** the foundation contract in one place (checklist or doc):
   - Boundary getters from INTERCEPT_ALIGNMENT_CONTRACT (protocol getters only; no adapter leak)
   - Curator contract from PLATFORM_SDK_REQUIREMENT_SPEC (register_capability, discover_agents, get_domain_registry, promote_to_platform_dna)
   - RegistryAbstraction vs file_storage responsibilities (list_files on file_storage; registry for artifact_index, intent_executions, generic RLS)
   - Curator backing unified per CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN (adapter → abstraction → protocol)

2. **Audit** foundations against that contract (Public Works + Curator):
   - Use existing audits: CURATOR_INFRASTRUCTURE_ALIGNMENT, CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN
   - Extend to: every boundary getter exists and returns protocol type; no caller uses registry.list_files; no adapter passed to Team B surface; Curator has one backing (Supabase or CuratorFoundationService)

3. **Fix all contract violations** in that pass:
   - Curator unification (wire CuratorSDK to one implementation)
   - semantic_profile_registry path (add get_registry_entry/register_entry/list_registry_entries to RegistryAbstraction or give it a dedicated store)
   - Any getter returning adapter → fix or remove from boundary
   - Any caller using wrong abstraction → fix (list_files already fixed to file_storage)
   - Don't defer "we'll fix it when we touch it"—fix it so the foundation **conforms**.

4. **Probe** foundations in isolation:
   - Boot succeeds with expected config
   - Call boundary getters; Curator/registry surface behaves per contract
   - Failure modes: missing optional adapter → predictable (no crash, clear log)
   - Optionally add **contract assertion** tests (e.g. "GovernanceService uses only getters," "no registry.list_files callers") that we re-run whenever we touch foundations

5. **Document** "Foundation contract satisfied as of &lt;date&gt;" and "how foundations fail and when."

### 2.2 Then Work Up the Stack

Runtime (Step 3) and Civic (Step 4) then **depend on** "foundation is contract-complete." If we find a foundation bug while working on Runtime or Civic, we **fix it and re-run the foundation contract probes** (and any contract assertion tests). So we're not "remembering to retest everything"—we're **"foundation has a contract and probes; we re-run them when we touch foundation."**

### 2.3 Why This Is More Strategic

- **Single place of truth:** The foundation contract is written down; we audit and fix against it once, in one pass, instead of discovering messes layer by layer.
- **Clear "done" criterion:** Step 2 is "done" when the foundation contract pass is complete and probes pass—not "we moved on and hope nothing breaks."
- **Cheaper retesting:** When we touch foundation code later, we re-run foundation probes (and contract assertions), not "everything."
- **Same idea for other layers (optional):** We can define a "Runtime contract pass" and "Civic contract pass" with the same idea: audit against contract, fix all violations, probe, document—then the next layer depends on "layer N is contract-complete."

---

## 3. Summary

**Fix-in-context as we work up** is fine **as long as** we first do a **Foundation Contract Pass** so that:

- "Foundation conforms to the contract" is a **stated invariant**
- We have **probes** (and optionally contract assertion tests) to re-run when we touch foundations

That way we're not relying on memory or full-stack retests every time we move up. Step 2 (Foundations) in MEET_IN_THE_MIDDLE_PLAN is executed as this Foundation Contract Pass; only when it is complete do we proceed to Runtime and Civic.

---

## 4. Foundation Contract Pass Completed (January 2026)

- **Define:** Foundation contract is defined in this doc and in CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN.
- **Audit:** Curator gaps were audited (CURATOR_INFRASTRUCTURE_ALIGNMENT, CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN).
- **Fix:** (1) RegistryAbstraction: added get_registry_entry, register_entry, list_registry_entries (table registry_entries). (2) CuratorProtocol: added in foundations/public_works/protocols/curator_protocol.py. (3) CuratorSDK: wired to CuratorFoundationService for register_capability/discover_agents/get_domain_registry; implements sovereignty stubs (classify_artifact, approve_promotion, approve_cross_domain, approve_message_routing). (4) GovernanceService: creates CuratorFoundationService and passes to CuratorSDK.
- **Probe:** Re-run foundation probes (boot, boundary getters, Curator/registry surface) to confirm. Optional: add contract assertion tests.
- **Document:** “Foundation contract satisfied as of January 2026.” How foundations fail: missing optional adapter → no crash, clear log; missing registry_entries table → semantic_profile_registry falls back to defaults; CuratorService not wired → promote_to_platform_dna no-op.
