# Init-Order Spec (Φ3 — Runtime Graph Construction)

**Purpose:** Document the deterministic order inside Φ3 (Operational Reality) so there is no hidden coupling. This is the mechanical content of Φ3 — Runtime Graph Construction.

**Status:** Canonical. `service_factory` and Public Works initialization must align with this spec.

**References:**
- [genesis_protocol.md](../genesis_protocol.md) — Φ3, Gate G3
- [FOUNDATION_PLAN.md](../FOUNDATION_PLAN.md) Step 4
- [PLATFORM_CONTRACT.md](PLATFORM_CONTRACT.md) — §5 (pre-boot), §6 (init order, no hidden coupling), §7 (RuntimeServices)
- [PRE_BOOT_SPEC.md](PRE_BOOT_SPEC.md) — G3 runs before this sequence
- [BOOT_PHASES.md](BOOT_PHASES.md) — Φ3 outcome = Experience SDK surface available; Φ4 = attach experience surfaces

---

## 1. Prerequisite

**Gate G3 must have passed.** Pre-boot validation (see [PRE_BOOT_SPEC.md](PRE_BOOT_SPEC.md)) runs **before** any step below. If pre-boot fails, we never call `create_runtime_services()`. Therefore, when we enter this sequence, all seven backing services (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB) are known to be reachable and authorized.

---

## 2. Top-Level Sequence (create_runtime_services)

The runtime object graph is built in this **fixed order**:

| Step | Component | Description |
|------|-----------|-------------|
| 1 | **Public Works** | Infrastructure adapters and abstractions. See §3. |
| 2 | **StateSurface** | State surface with ArtifactRegistry; depends on `state_abstraction`, `file_storage_abstraction` from Public Works. |
| 3 | **WriteAheadLog (WAL)** | Audit trail; depends on `redis_adapter` from Public Works. |
| 4 | **IntentRegistry** | Intent handlers; then register intent services from each realm (Content, Insights, Operations, Outcomes, Security, Control Tower, Coexistence). Each intent service is constructed with `public_works` and `state_surface`. |
| 5 | **ExecutionLifecycleManager** | Orchestrates execution; receives Public Works, StateSurface, WAL, IntentRegistry. |

**Invariant:** No step may be skipped or reordered. Step N may depend only on outputs of steps 1..N-1.

---

## 3. Public Works Init Order (Inside Step 1)

Public Works builds **adapters first**, then **abstractions**.

### 3.1 Adapters (Layer 0)

Create infrastructure and capability adapters in an order that respects dependencies (e.g. Supabase before SupabaseFileAdapter if needed). Typical grouping:

- **Infrastructure:** Redis, Arango, Consul, DuckDB, Meilisearch, Supabase, GCS, Supabase File.
- **Parsing:** CSV, Excel, PDF, Word, HTML, Image, JSON; optional Kreuzberg, Mainframe.
- **Ingestion:** Upload, EDI (if config present), API.
- **Other:** Visual generation, LLM (OpenAI, HuggingFace) if config present.

Each adapter is created from **canonical config only** (see §5). No env reads inside Public Works for platform infra.

### 3.2 Abstractions (Layer 1)

Create abstractions that wrap adapters, e.g.:

- StateManagementAbstraction (Redis + Arango)
- ServiceDiscoveryAbstraction (Consul)
- SemanticSearchAbstraction (Meilisearch)
- RegistryAbstraction (Supabase)
- AuthAbstraction, TenantAbstraction (Supabase)
- FileStorageAbstraction, ArtifactStorageAbstraction (GCS + Supabase file)
- DeterministicComputeAbstraction (DuckDB)
- SemanticDataAbstraction, KnowledgeDiscoveryAbstraction (Arango)
- EventPublisherAbstraction (Redis Streams)
- Parsing abstractions (PDF, Word, Excel, etc.)

Order must ensure that an abstraction only depends on adapters (or abstractions) already created. No circular dependency.

---

## 4. No Hidden Coupling

**Rule:** Failure of one backing service must not prevent creation of an **unrelated** abstraction. Historically, Arango failure during `_ensure_state_collections()` could block creation of `registry_abstraction` (Supabase). That violates the contract: **registry_abstraction does not depend on Arango.**

**Enforcement:**

- **Pre-boot** validates all seven services. If Arango (or any) fails, we exit before building the graph. So we never reach a state where “Arango failed and then registry wasn’t built.”
- **Init order** inside Public Works must not create a dependency of registry (or other Supabase/GCS-backed abstractions) on Arango. If code today has a single init path where Arango runs before registry and Arango failure aborts the path, the fix is either: (A) reorder so registry is built regardless of Arango, or (B) rely on pre-boot so Arango never fails at init time (preferred; see PLATFORM_CONTRACT §6).

**Contract default:** All infra is required; pre-boot fails first. So when we run this init order, every required adapter/abstraction is created and no “continuing anyway” with None for a required field.

---

## 5. Public Works Contract

- **Input:** Public Works receives **only** the **canonical config** (output of config contract). Signature: `PublicWorksFoundationService(config=config)` and `initialize()` uses only `self.config`.
- **No env or config_helper:** Public Works must not read `os.getenv()` or call `get_env_contract()` / `config_helper` for platform infra. All values come from the `config` dict. (Eliminating fallbacks is an implementation task in Step 6.)
- **Output:** Populated adapters and abstractions. After `initialize()`, all required abstractions for RuntimeServices (`state_abstraction`, `file_storage_abstraction`, `registry_abstraction`, `artifact_storage_abstraction`, etc.) are non-None when pre-boot has passed.

---

## 6. RuntimeServices

`create_runtime_services(config)` returns a `RuntimeServices` instance with non-None:

- `public_works`
- `state_surface`
- `execution_lifecycle_manager`
- `registry_abstraction`
- `artifact_storage`
- `file_storage`

This is enforced in code by `RuntimeServices.__post_init__`. The init-order spec guarantees that when G3 has passed and this sequence runs, all of these are successfully created.

---

## 7. Summary

| Item | Rule |
|------|------|
| **Prerequisite** | Gate G3 (pre-boot) passed. |
| **Sequence** | 1. Public Works (adapters → abstractions) 2. StateSurface 3. WAL 4. IntentRegistry + realm intent registration 5. ExecutionLifecycleManager. |
| **No hidden coupling** | Registry and other Supabase/GCS-backed abstractions are not blocked by Arango; pre-boot ensures we do not enter Φ3 with a failed service. |
| **Public Works input** | Canonical config only; no env or config_helper for platform infra. |
| **Φ3 outcome** | Experience SDK surface is available; Φ4 = attach experience surfaces. See [BOOT_PHASES.md](BOOT_PHASES.md). |

Implementations (`service_factory.create_runtime_services`, `PublicWorksFoundationService.initialize`) must conform to this spec. The “continuing anyway” behavior when Public Works init has issues must be removed or made impossible once G2/G3 are fully enforced (Step 6).
