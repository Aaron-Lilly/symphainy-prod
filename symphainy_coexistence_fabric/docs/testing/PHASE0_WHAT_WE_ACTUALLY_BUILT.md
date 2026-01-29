# Phase 0: What We've Actually Built (Evidence from Probes)

**Date:** 2026-01-29  
**Method:** Ran runtime_main.py with timeout; captured full boot log. No assumptions—only observed behavior.

---

## 1. Entry point and boot order (confirmed)

- **Process:** `python3 runtime_main.py`
- **Sequence observed in log:** Starting Symphainy Runtime → Building runtime object graph → Initializing PublicWorksFoundationService → Initializing adapters and abstractions → … → Creating ExecutionLifecycleManager → **then process exited with error** (see below).
- **Probe 01 code trace is correct:** get_env_contract() → create_runtime_services() → PublicWorks → StateSurface → WAL → IntentRegistry → register intents → initialize_solutions → ELM → RuntimeServices. We did **not** reach create_fastapi_app() or uvicorn.run() in this run.

---

## 2. What actually happened during boot (from log)

### 2.1 PublicWorks – adapters created vs not

| Adapter | Created? | Evidence |
|---------|----------|----------|
| Redis | **No** | "Redis configuration not provided, Redis adapter not created" |
| Consul | **No** | "Consul configuration not provided, Consul adapter not created" |
| Kreuzberg | **No** | "Kreuzberg configuration not provided" |
| CSV, Excel, PDF, Word, HTML, Image, JSON | **Yes** | "X adapter created" |
| Meilisearch | **Yes** | "Meilisearch adapter connected: meilisearch:7700" |
| Supabase | **Yes** | SUPABASE_URL/ANON_KEY/SERVICE_KEY set; adapter initialized |
| GCS | **Yes** | GCS_PROJECT_ID, BUCKET_NAME, CREDENTIALS set; adapter initialized |
| Supabase File | **Yes** | "Supabase File Management adapter connected" |
| Visual Generation | **Yes** | "VisualGenerationAdapter initialized" |
| OpenAI, HuggingFace | **Yes** | "OpenAI adapter created", "HuggingFace adapter created" |
| ArangoDB | **No (failed)** | "Failed to connect to ArangoDB: [HTTP 401][ERR 11] not authorized" |
| DuckDB | **No** | "DuckDB configuration not provided, DuckDB adapter not created" |

**Implication:** PublicWorks expects config keys like `redis`, `consul` (nested dicts). get_env_contract() returns flat env (REDIS_URL, etc.). So either config is transformed before being passed, or Redis/Consul are never created in this environment—**config-as-behavior**: which keys actually drive adapter creation?

### 2.2 PublicWorks – abstractions and state collections

- "Creating infrastructure abstractions..." → StateManagementAbstraction initialized.
- ArangoDB failed again when ensuring collection `state_data` → "Failed to create ArangoDB collection: state_data" → **RuntimeError: Infrastructure initialization failed: could not create collection state_data**.
- **Service factory caught the exception:** "PublicWorksFoundationService initialization had issues, continuing anyway..." → boot continued. So we have **partial** PublicWorks: adapters that were created exist; state_abstraction may be in a bad state (Arango-backed state_data missing).

### 2.3 StateSurface, WAL, IntentRegistry

- StateSurface created.
- WriteAheadLog created (uses redis_adapter—which was **not** created; may be None).
- IntentRegistry created; intent handlers registered in order (Content → Insights → …).

### 2.4 Intent registration failures

- **extract_embeddings:** "Failed to register extract_embeddings: cannot import name 'EmbeddingAgent' from '...embedding_agent'". One intent not registered.
- Other Content/Insights/Operations/Outcomes/Security/Control Tower/Coexistence intents registered as per log.

### 2.5 Solutions and MCP servers

- **8 solutions** initialized.
- **6 MCP servers** reported initialized (not 8): Coexistence, Content, Insights, Journey (operations?), Outcomes, Control Tower.
- **Operations MCP:** "Failed to initialize MCP Server for operations_solution: object OperationsSolutionMCPServer can't be used in 'await' expression".
- **Security MCP:** "Failed to initialize MCP Server for security_solution: object SecuritySolutionMCPServer can't be used in 'await' expression".
- So **async/sync mismatch**: two solution MCP servers are not async but are awaited.

### 2.6 Fatal error – server never started

- **ExecutionLifecycleManager** created.
- **RuntimeServices** constructor: **ValueError: Required service registry_abstraction is None**.
- **Process exited.** We never reached create_fastapi_app() or uvicorn.run(). So in this run:
  - **No first request** (server never listened).
  - **First request path (GET /health)** was not exercised—only code trace from Probe 01.

**Why is registry_abstraction None?** PublicWorks creates registry_abstraction (and other abstractions) in _create_abstractions(). Arango failed before that completed (state_data collection). So either registry_abstraction is created only when Arango succeeds, or it is created but not assigned when there is an exception. Need to trace: registry_abstraction is set where in PublicWorks, and is it conditional on Arango?

---

## 3. Summary: what we've actually built (Phase 0 evidence)

| Claim / assumption | Reality (from this run) |
|--------------------|-------------------------|
| Boot order matches Probe 01 | **Yes**—sequence in log matches. |
| All adapters created from config | **No**—Redis, Consul, Kreuzberg, DuckDB not created; Arango failed. Config keys (redis, consul, etc.) may not match env contract. |
| PublicWorks init failure is fatal | **No**—service_factory catches and continues. |
| We reach uvicorn and first request | **No**—RuntimeServices validation fails (registry_abstraction is None); process exits before FastAPI/uvicorn. |
| All intents registered | **No**—extract_embeddings failed (EmbeddingAgent import). |
| All solution MCP servers initialized | **No**—Operations and Security MCP fail (await on non-async). |
| First request path (GET /health) | **Not observed**—server never started. Code path from Probe 01 is correct; runtime path was not reached. |

---

## 4. Next steps (probe / fix—do not assume)

1. **registry_abstraction None:** Explained in [ARANGO_REGISTRY_ABSTRACTION_SEAM.md](ARANGO_REGISTRY_ABSTRACTION_SEAM.md). registry_abstraction is **Supabase-based**; we never create it when Arango fails because _ensure_state_collections() raises **before** the code that creates registry_abstraction runs. That’s the "hidden cheat" that makes the Arango issue "go away" when Arango works.
2. **Recommended next:** Use [PATH_TO_WORKING_PLATFORM.md](PATH_TO_WORKING_PLATFORM.md): add **pre-boot check** (Arango, Redis, required env); fail at the door with clear message; **nothing optional at boot**. Then re-run Phase 0 and confirm first request. (Do *not* make Arango optional—see PATH_TO_WORKING_PLATFORM.)
3. **Config contract vs PublicWorks:** Trace where config dict comes from (Probe 02 + code trace) if Redis/Consul "not provided" needs clarification.
4. **Probe 03 (order/restart):** Run config variation and restart; record in Stability/Gravity.

---

*This document is evidence-only. Fix recommendation is in ARANGO_REGISTRY_ABSTRACTION_SEAM.md.*
