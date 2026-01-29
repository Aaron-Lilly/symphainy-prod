# Arango + registry_abstraction: The Hidden Seam

**Path to resolution:** Arango is **required** at boot (nothing optional). For a clear roadmap to a working platform (pre-boot check, gates, no optional infra), see [PATH_TO_WORKING_PLATFORM.md](PATH_TO_WORKING_PLATFORM.md). This doc explains *why* boot fails when Arango fails; that doc defines *how* to get to working.

**Why the Arango issue "sometimes goes away":** Boot doesn’t fail because of Arango itself. It fails because **we never create `registry_abstraction`** when Arango fails. `registry_abstraction` is **Supabase-based**, but we only run the code that creates it **after** an Arango-dependent step that raises.

---

## What the code actually does

1. **PublicWorks._create_adapters()**  
   - Creates `ArangoAdapter`, calls `await self.arango_adapter.connect()`.  
   - If `connect()` returns **False** (e.g. 401), we only log "ArangoDB adapter connection failed".  
   - We **do not** set `self.arango_adapter = None`. So the adapter instance still exists.

2. **PublicWorks._create_abstractions()** (called from `initialize()`)  
   - Creates `state_abstraction` (uses `arango_adapter`).  
   - **If `self.arango_adapter`:** calls `await self._ensure_state_collections()`.  
   - **`_ensure_state_collections()`** uses the adapter (e.g. `collection_exists`, `create_collection`). With a failed connection it throws → we **re-raise** `RuntimeError("Infrastructure initialization failed: could not create collection state_data")`.  
   - So we **never reach** the rest of `_create_abstractions()`, including:
     - `registry_abstraction = RegistryAbstraction(supabase_adapter)` (Supabase, **not** Arango).

3. **Service factory**  
   - Catches the exception from `public_works.initialize()`, logs "had issues, continuing anyway", and continues.  
   - Later it does `registry_abstraction = public_works.registry_abstraction` → **None**.  
   - **RuntimeServices** then raises: `ValueError: Required service registry_abstraction is None`.

So:

- **When Arango works:** We pass `_ensure_state_collections()`, finish `_create_abstractions()`, set `registry_abstraction` (Supabase), and boot can complete. The Arango issue "goes away."
- **When Arango fails:** We raise **before** creating `registry_abstraction`. Boot fails on `registry_abstraction is None`, not on Arango directly. That’s the hidden cheat: the failure looks like "missing registry" but the root cause is **order of operations** after an Arango failure.

---

## Dependency summary

| Abstraction            | Backing store   | Created when                          |
|------------------------|-----------------|----------------------------------------|
| registry_abstraction  | **Supabase**    | After _ensure_state_collections()      |
| state_abstraction     | Redis + Arango  | Before _ensure_state_collections()     |

So **registry_abstraction does not depend on Arango**; we just never run the code that creates it when Arango fails, because _ensure_state_collections() raises first.

---

## Where to go next (recommendations)

**Option A – Make Arango optional for boot (recommended)**  
Goal: Boot can complete and reach first request even when Arango is down or misconfigured.

1. **When Arango connect fails:** set `self.arango_adapter = None` (and `arango_graph_adapter = None`) so we don’t call _ensure_state_collections() and don’t assume Arango later.
2. **Semantic data abstraction:** Today we `raise RuntimeError("ArangoDB adapter is required for semantic data abstraction")` when `not self.arango_adapter`. Change to: when Arango is missing, set `self.semantic_data_abstraction = None` and log a warning (same pattern as knowledge_discovery_abstraction). Ensure any caller that needs it checks for None.
3. **Leave _ensure_state_collections() as-is:** It already returns when `not self.arango_adapter`. With (1), we won’t call it when Arango failed.
4. **Result:** We always run the rest of _create_abstractions(), including `registry_abstraction = RegistryAbstraction(supabase_adapter)`. Boot completes; RuntimeServices gets a non-None registry_abstraction; you can reach first request. State/lineage that need Arango will be degraded until Arango is fixed.

**Option B – Keep Arango required, fix it everywhere**  
- Treat Arango as mandatory for boot.  
- Fix credentials and connectivity in every environment so connect() succeeds.  
- No code change to order of operations; the "cheat" stays implicit.

**Option C – Only document (no code change)**  
- Add this doc (and a short note in Platform Operation Map / Phase 0) so the seam is explicit.  
- Accept that in envs where Arango fails, boot will fail with `registry_abstraction is None`.

---

## Recommendation

**Option A** is the most aligned with "we know how it really works":

- Makes the dependency explicit: Arango is optional for **boot**; Supabase-backed registry_abstraction is what unblocks the server.
- Stops the Arango issue from hiding behind "registry_abstraction is None."
- Keeps fail-fast for things that truly require Arango (e.g. semantic_data) by having callers handle None and document degraded behavior.

Next concrete steps:

1. Implement Option A (arango_adapter = None on connect failure; semantic_data_abstraction optional when arango_adapter is None).
2. Re-run Phase 0: start runtime, send GET /health, and confirm first request path with evidence.
3. Add a one-line note to [PHASE0_WHAT_WE_ACTUALLY_BUILT.md](PHASE0_WHAT_WE_ACTUALLY_BUILT.md) and [PLATFORM_OPERATION_MAP.md](PLATFORM_OPERATION_MAP.md): "registry_abstraction is Supabase-based; boot only reaches it when Arango does not raise in _ensure_state_collections(); Option A makes Arango optional for boot."
