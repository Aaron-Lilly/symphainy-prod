# Platform Inventory: What We Have vs What We Need

**Purpose:** Single source of truth for "what's actually in our platform" and "what we need" so we can answer that question without digging through multiple containers and codebases.

**Status:** Living document. Update this when adding/removing services, containers, or required env.

---

## 1. Where the truth is today (scattered)

| Question | Where it lives today | Problem |
|----------|----------------------|--------|
| What containers exist? | `docker-compose.yml` (repo root) and `symphainy_coexistence_fabric/docker-compose.yml` | Two compose files; different service sets. |
| What infra does runtime need to boot? | `PublicWorksFoundationService` + `RuntimeServices.__post_init__` | Code-only; no single doc. Arango failure blocks registry_abstraction (see [ARANGO_REGISTRY_ABSTRACTION_SEAM](./ARANGO_REGISTRY_ABSTRACTION_SEAM.md)). |
| What env vars are required? | `env_contract.py` (defaults + validation) | Contract is flat (REDIS_URL, etc.); PublicWorks also expects nested keys (redis, consul) that are never set when config comes from env contract. |
| What services does RuntimeServices require? | `runtime_services.py` (`required` list in `__post_init__`) | Required: public_works, state_surface, execution_lifecycle_manager, registry_abstraction, artifact_storage, file_storage. |
| What adapters/abstractions does PublicWorks create? | `foundation_service.py` (_create_adapters, _create_abstractions) | Long methods; required vs optional is inline (raise RuntimeError vs log warning). |

**Single source of truth (this doc):** Consolidates the above and distinguishes *in platform* vs *needed to run*.

**Canonical contract:** For **required** infra and guarantees that the platform actually works, see [PLATFORM_CONTRACT.md](../architecture/PLATFORM_CONTRACT.md). The contract states that **no** infra is optional (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB are all required) and defines pre-boot validation and config rules. Use the contract as the source of truth for "what must be present and validated at boot."

---

## 2. Containers (what’s in the platform)

### 2.1 Repo root `docker-compose.yml` (full stack)

| Service | Image/Build | Purpose |
|---------|-------------|--------|
| redis | redis:7-alpine | Cache, WAL, sessions |
| arango | arangodb:3.11 | State, graph, semantic data |
| consul | hashicorp/consul | Service discovery |
| meilisearch | getmeili/meilisearch:v1.5 | Search (optional in code) |
| runtime | Dockerfile.runtime | Backend API (single process today) |
| experience | Dockerfile.experience | Experience API (port 8001) |
| realms | Dockerfile.realms | Realms API (port 8002) |
| otel-collector | otel/opentelemetry-collector | Telemetry |
| prometheus | prom/prometheus | Metrics |
| grafana | grafana/grafana | Dashboards |
| tempo | grafana/tempo | Traces |
| traefik | traefik:v2.10 | Reverse proxy |
| frontend | symphainy-frontend Dockerfile | Next.js UI |

### 2.2 Coexistence fabric `symphainy_coexistence_fabric/docker-compose.yml` (reduced stack)

| Service | Same as root? | Note |
|---------|----------------|------|
| redis | ✓ | |
| arango | ✓ | |
| consul | ✓ | |
| runtime | ✓ | |
| experience | ✓ | Uses Dockerfile.runtime (same as runtime) |
| frontend | ✓ | Context ../symphainy-frontend |
| traefik | ✓ | |
| **Not present:** meilisearch, realms, otel-collector, prometheus, grafana, tempo | | |

So: **two stacks** — full (root) vs minimal (coexistence_fabric). No single “canonical” compose; root has more services.

---

## 3. Code: what runtime needs to boot (source of truth: code)

### 3.1 Boot chain (simplified)

1. `runtime_main.py`: `get_env_contract()` → `create_runtime_services(config.__dict__)` → `create_fastapi_app(services)` → uvicorn.
2. `create_runtime_services`:
   - Builds `PublicWorksFoundationService(config)` and runs `await public_works.initialize()`.
   - Then builds StateSurface, WAL, IntentRegistry, solutions, ExecutionLifecycleManager.
   - Then builds `RuntimeServices(..., registry_abstraction=public_works.registry_abstraction, ...)`.

3. **RuntimeServices required fields** (`runtime_services.py`):  
   `public_works`, `state_surface`, `execution_lifecycle_manager`, `registry_abstraction`, `artifact_storage`, `file_storage`.  
   If any is `None`, `ValueError` and process exits (no HTTP server).

### 3.2 How PublicWorks fills those (from `foundation_service.py`)

- **registry_abstraction**  
  Created in `_create_abstractions()` only if `supabase_adapter` exists.  
  **But** `_create_abstractions()` runs after `_ensure_state_collections()` (Arango). If Arango fails there, the method raises and later steps (including `registry_abstraction`) are never run → `registry_abstraction` stays `None` → RuntimeServices raises.  
  So in current code: **Arango must succeed** for runtime to reach a state where `registry_abstraction` is set.

- **file_storage** / **artifact_storage**  
  Require: GCS adapter, Supabase file adapter, GCS bucket name. Otherwise `RuntimeError` in `_create_abstractions()`.

- **state_surface**  
  Uses `public_works.state_abstraction`, which is created with Redis + Arango. If Arango fails after state_abstraction is created but `_ensure_state_collections()` raises, the rest of `_create_abstractions()` (registry, file_storage, artifact_storage) is skipped.

So **effective runtime boot requirements** (from code today):

| Dependency | Used for | Required by code? |
|------------|----------|-------------------|
| ArangoDB | state_abstraction, _ensure_state_collections(); gate before registry/file/artifact | **Yes** (failure prevents registry_abstraction and thus boot) |
| Redis | state_abstraction, WAL | Adapter optional in config; state_abstraction still created with redis_adapter=None possible |
| Supabase (auth + DB) | registry_abstraction, auth, tenant | **Yes** for registry_abstraction |
| Supabase (file) | file_storage, artifact_storage | **Yes** (RuntimeError if missing) |
| GCS | file_storage, artifact_storage | **Yes** (RuntimeError if missing) |
| Consul | service_discovery_abstraction | No (warning only) |
| Meilisearch | semantic_search_abstraction | No (warning only) |
| DuckDB | deterministic_compute_abstraction | No (warning only) |

### 3.3 Config shape vs env contract

- **runtime_main** passes `config = get_env_contract()` then `config.__dict__` into `create_runtime_services`. So PublicWorks receives a **flat** dict (e.g. REDIS_URL, ARANGO_URL, CONSUL_HOST, SUPABASE_*, GCS_*, ...).
- **PublicWorks** in `_create_adapters()` uses:
  - `self.config.get("redis", {})`, `self.config.get("consul", {})`, `self.config.get("duckdb", {})`, etc.  
  With flat env dict, these are always `{}`, so **Redis, Consul, DuckDB adapters are never created** when booting from env contract only.
  - For Arango, Supabase, GCS, Meilisearch, etc. it uses `self.config.get("arango_url")` or similar **plus** fallback to `get_env_contract()` (env). EnvContract uses uppercase names (ARANGO_URL); `config.__dict__` keys are the same. So those adapters can be created from env.

So: **single source of “what we need” for boot** is currently the code (RuntimeServices + PublicWorks), but **config shape** is inconsistent: env contract is flat, PublicWorks expects some nested keys for Redis/Consul/DuckDB. Result: Redis/Consul/DuckDB are not created when using only env contract.

---

## 4. Env vars (env_contract.py)

- **With defaults (assumed available locally):** REDIS_URL, ARANGO_URL, ARANGO_ROOT_PASSWORD, RUNTIME_PORT, SMART_CITY_PORT, REALMS_PORT, REDIS_PORT, ARANGO_PORT, CONSUL_HOST, CONSUL_PORT, TRAEFIK_*, TEMPO_PORT, GRAFANA_PORT, OTEL_EXPORTER_OTLP_ENDPOINT, LOG_LEVEL, MEILISEARCH_PORT.
- **Optional (feature flags / integrations):** CONSUL_TOKEN, SUPABASE_*, GCS_*, MEILI_MASTER_KEY.

In practice, for **current** boot to succeed we need Arango, Supabase (DB + file), and GCS configured; Redis/Consul are optional in code but WAL and state benefit from Redis. Env contract does not mark “required for boot” explicitly; that’s only in code and this doc.

---

## 5. What we have vs what we need (summary)

| Layer | Have (in platform) | Need (to boot / run) | Gap / note |
|-------|--------------------|----------------------|------------|
| Containers | Two compose files (full vs minimal) | One canonical stack for “working platform” | Align on one compose or document which is canonical. |
| Infra | Arango, Redis, Consul, Meilisearch, Supabase, GCS (in compose or env) | Arango + Supabase (DB+file) + GCS required by code; Redis recommended | Arango must succeed; otherwise registry_abstraction never set. |
| Config | EnvContract (flat) | PublicWorks expects nested redis/consul/duckdb for those adapters | Redis/Consul/DuckDB not created when config is only env contract. |
| Required services | RuntimeServices required list | registry_abstraction, artifact_storage, file_storage + rest | Satisfied only if PublicWorks completes _create_abstractions (Arango must not fail). |

---

## 6. Recommended next steps

1. **Treat [PLATFORM_CONTRACT.md](../architecture/PLATFORM_CONTRACT.md) as the canonical contract** for “what’s in the platform” and “what we need”; the contract defines what **must** be present and validated at boot (no optional infra).
2. **Pre-boot check** (see [PATH_TO_WORKING_PLATFORM](./PATH_TO_WORKING_PLATFORM.md)): validate **all** required services per the platform contract (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB) *before* calling `create_runtime_services()`.
3. **Config bridge:** Per the contract, either (a) build a platform config builder that fills nested `redis`/`consul`/`duckdb` from env, or (b) change PublicWorks to read flat env keys for Redis/Consul/DuckDB so one source (env) drives all adapters.
4. **Compose:** Decide which compose is "platform" and ensure it includes all contract-required services (Redis, Arango, Consul, Meilisearch, Supabase/GCS via env; DuckDB via volume or path).

---

## 7. References

- **[PLATFORM_CONTRACT.md](../architecture/PLATFORM_CONTRACT.md)** — canonical contract: required infra (no optional), pre-boot validation, config, guarantees.
- [ARANGO_REGISTRY_ABSTRACTION_SEAM](./ARANGO_REGISTRY_ABSTRACTION_SEAM.md) — why Arango failure leaves registry_abstraction None.
- [PHASE0_WHAT_WE_ACTUALLY_BUILT](./PHASE0_WHAT_WE_ACTUALLY_BUILT.md) — boot probe evidence.
- [PATH_TO_WORKING_PLATFORM](./PATH_TO_WORKING_PLATFORM.md) — pre-boot validation and path to working platform.
- [PLATFORM_OPERATION_MAP](./PLATFORM_OPERATION_MAP.md) — entry point and boot order (code trace).
- Code: `runtime_services.py` (required list), `foundation_service.py` (_create_adapters, _create_abstractions), `env_contract.py`, `runtime_main.py` (config flow).
