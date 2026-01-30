# Config Contract Spec (Gate G2 — Canonical Config Shape and Provenance)

**Purpose:** Define the **canonical platform config** structure and where each value comes from (env vars, precedence, typical file). This is the single definition of “the” config that Public Works and pre-boot consume. Env must be acquired first per [CONFIG_ACQUISITION_SPEC.md](CONFIG_ACQUISITION_SPEC.md).

**Status:** Canonical. Implementation (platform config builder) must conform to this spec.

**References:**
- [CONFIG_ACQUISITION_SPEC.md](CONFIG_ACQUISITION_SPEC.md) — env files and load order (run before building this config)
- [FOUNDATION_PLAN.md](../FOUNDATION_PLAN.md) Step 2
- [STEP0_FOUNDATION_OPEN_QUESTIONS.md](../STEP0_FOUNDATION_OPEN_QUESTIONS.md) — validated answers, CTO clarifications
- [PLATFORM_CONTRACT.md](PLATFORM_CONTRACT.md) — §3 (required infra), §4 (one config source)

---

## 1. Scope

**Canonical config** is a single structure (e.g. a dict) built **after** env acquisition (Φ2 first step). It is the **only** config source for:

- Pre-boot validation (Gate G3 entry)
- Public Works / `create_runtime_services(config)`
- Any adapter or abstraction that needs platform infra settings

No code that participates in platform boot may read `os.environ` or env files for platform infra after this config is built; they read only this structure.

---

## 2. Canonical Shape

The canonical config is a **dict** with the following keys. Nested blocks are used where Public Works adapters expect `config.get("redis", {})`, etc.

### 2.1 Nested blocks (required for G3)

| Block | Keys | Purpose |
|-------|------|--------|
| **redis** | `host`, `port`, `db`, `password` | Redis adapter (State, WAL, events). Parsed from REDIS_URL or built from REDIS_* if needed. |
| **consul** | `host`, `port`, `token` | Consul adapter (service discovery). |
| **duckdb** | `database_path`, `read_only` | DuckDB adapter (deterministic compute). |

### 2.2 Flat keys — backing services (required for G3)

| Canonical key | Type | Purpose |
|---------------|------|--------|
| **arango_url** | str | ArangoDB URL. |
| **arango_username** | str | ArangoDB username. |
| **arango_password** | str | ArangoDB password (may be empty string in dev/CI only; see §5). |
| **arango_database** | str | ArangoDB database name. |
| **supabase_url** | str \| None | Supabase project URL. |
| **supabase_anon_key** | str \| None | Supabase publishable/anon key (from SUPABASE_PUBLISHABLE_KEY only; see §4). |
| **supabase_service_key** | str \| None | Supabase secret/service key (from SUPABASE_SECRET_KEY only). |
| **supabase_jwks_url** | str \| None | Optional JWKS URL. |
| **supabase_jwt_issuer** | str \| None | Optional JWT issuer. |
| **gcs_project_id** | str \| None | GCP project ID. |
| **gcs_bucket_name** | str \| None | GCS bucket name. |
| **gcs_credentials_json** | str \| None | GCS credentials JSON string. |
| **meilisearch_host** | str | Meilisearch host. |
| **meilisearch_port** | int | Meilisearch port. |
| **meilisearch_key** | str \| None | Meilisearch API key. |

### 2.3 Flat keys — server and telemetry

| Canonical key | Type | Purpose |
|---------------|------|--------|
| **runtime_port** | int | Runtime HTTP server port. |
| **log_level** | str | Log level (e.g. INFO). |
| **otel_exporter_otlp_endpoint** | str | OpenTelemetry OTLP exporter endpoint (required; no default; pre-boot validates presence and reachability). Must be set via `OTEL_EXPORTER_OTLP_ENDPOINT`. |

### 2.4 Optional keys (not required for G3)

These may be present for intent dependencies (EDI, Cobrix, Kreuzberg, LLM, etc.). Omitted from this spec’s mapping table; see PLATFORM_CONTRACT §9 and optional config sources when we add them. Examples: `edi` (nested), `cobrix` (nested), `kreuzberg` (nested), `openai_api_key`, `huggingface_*`.

---

## 3. Env → Canonical Key Mapping

Env must be acquired per CONFIG_ACQUISITION_SPEC before reading. Then the builder reads **only** from `os.environ` (or equivalent). Precedence: first env var that is set (or default) wins, unless otherwise noted.

| Canonical key(s) | Env var(s) (precedence order) | Default / notes | Typical file |
|------------------|-------------------------------|-----------------|--------------|
| **redis** (nested) | REDIS_URL (parsed to host, port, db, password) | host=localhost, port=6379, db=0 | .env or compose |
| **consul** (nested) | CONSUL_HOST, CONSUL_PORT, CONSUL_TOKEN | host=localhost, port=8500 | .env or compose |
| **duckdb** (nested) | DUCKDB_DATABASE_PATH, DUCKDB_READ_ONLY | database_path=/app/data/duckdb/main.duckdb, read_only=False | .env or config |
| **arango_url** | ARANGO_URL | http://localhost:8529 | config/development.env or compose |
| **arango_username** | ARANGO_USERNAME, then ARANGO_USER | root | config/development.env or compose |
| **arango_password** | ARANGO_PASS, then ARANGO_ROOT_PASSWORD | "" (see §5) | .env.secrets |
| **arango_database** | ARANGO_DATABASE, then ARANGO_DB | symphainy_platform | config/development.env or compose |
| **supabase_url** | SUPABASE_URL | None | .env.secrets or compose |
| **supabase_anon_key** | SUPABASE_PUBLISHABLE_KEY only (Supabase-supported name) | None | .env.secrets or compose |
| **supabase_service_key** | SUPABASE_SECRET_KEY only (Supabase-supported name) | None | .env.secrets or compose |
| **supabase_jwks_url** | SUPABASE_JWKS_URL | None | .env.secrets or .env |
| **supabase_jwt_issuer** | SUPABASE_JWT_ISSUER | None | .env.secrets or .env |
| **gcs_project_id** | GCS_PROJECT_ID | None | .env.secrets |
| **gcs_bucket_name** | GCS_BUCKET_NAME | None | .env.secrets |
| **gcs_credentials_json** | GCS_CREDENTIALS_JSON | None | .env.secrets |
| **meilisearch_host** | MEILISEARCH_HOST | meilisearch | .env or compose |
| **meilisearch_port** | MEILISEARCH_PORT | 7700 | .env or compose |
| **meilisearch_key** | MEILI_MASTER_KEY | None | .env.secrets or .env |
| **runtime_port** | RUNTIME_PORT | 8000 | .env or compose |
| **log_level** | LOG_LEVEL | INFO | .env or compose |
| **otel_exporter_otlp_endpoint** | OTEL_EXPORTER_OTLP_ENDPOINT | **Required; no default.** Boot fails if unset or unreachable. | .env.secrets or compose |

---

## 4. Naming Variants and Supabase

- **Arango:** Accept **ARANGO_USER** or ARANGO_USERNAME; **ARANGO_DB** or ARANGO_DATABASE; **ARANGO_PASS** or ARANGO_ROOT_PASSWORD. Document both so config/development.env and compose can use either convention.
- **Supabase:** Use **only** **SUPABASE_PUBLISHABLE_KEY** and **SUPABASE_SECRET_KEY** (Supabase-supported names). Do **not** document or support SUPABASE_ANON_KEY or SUPABASE_SERVICE_KEY as env var names; those were deprecated by Supabase. Internal canonical keys remain `supabase_anon_key` and `supabase_service_key` (populated from the two env vars above).

---

## 5. Rules

- **Blank arango_password:** Allowed **only in dev and CI**. **Forbidden in prod and staging.** Implementations may enforce this (e.g. fail build or pre-boot in prod if password is empty).
- **Optional keys:** Keys that are `None` or absent may be valid; Public Works or pre-boot will fail later if a required backing service is missing (e.g. pre-boot exits on missing Supabase URL). The contract does not require every key to be non-None at build time; it requires that the **shape** and **provenance** are defined so that when env is populated, the builder produces a consistent structure.
- **No env reads after build:** Once canonical config is built, no code in the platform boot path (pre-boot, Public Works, service_factory) may read `os.getenv()` or env files for platform infra. They receive only the canonical config dict.

---

## 6. Alignment with PLATFORM_CONTRACT

- **§3 Required Infrastructure:** The eight backing services (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB, Telemetry OTLP) each have a defined canonical key or nested block and env mapping above. Pre-boot (G3) and Public Works use these keys to connect.
- **§4 One Source of Truth:** This spec **is** that source. Env is acquired per CONFIG_ACQUISITION_SPEC; then this contract defines the single structure built from that env. All adapters are created from this config.

---

## 7. References to This Spec

- **CONFIG_ACQUISITION_SPEC.md** — env acquisition runs first; then the builder that implements this contract runs.
- **PLATFORM_CONTRACT.md** §4 — “single canonical config is built from that env per the Config Contract” links here.
- **FOUNDATION_PLAN.md** Step 2 — output is this spec.
- **Pre-Boot spec (Step 3)** — pre-boot consumes only this canonical config; no env reads inside pre-boot.
