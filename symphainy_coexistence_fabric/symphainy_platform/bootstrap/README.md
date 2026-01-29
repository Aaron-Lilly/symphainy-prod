# Bootstrap: Contract-First Config and Pre-Boot Validation

The bootstrap is the **single deliberate foundation** for platform startup. It runs before the object graph is built. No env reads for platform infra happen outside this layer.

**Reference:** [PLATFORM_CONTRACT.md](../../../docs/architecture/PLATFORM_CONTRACT.md) §4 (config), §5 (pre-boot validation).

---

## Layer 1: Platform Config

- **Module:** `platform_config.py`
- **Entry:** `load_platform_config() -> Dict[str, Any]`

**Responsibility:** One source of truth for configuration. Reads from the environment (via `EnvContract` for validation and defaults), then builds **one canonical dict** that the rest of the platform consumes. Keys include:

- **Nested:** `redis`, `consul`, `duckdb` (host/port/password, etc.) for adapters that expect `config.get("redis", {})`.
- **Flat:** `arango_url`, `supabase_url`, `gcs_project_id`, `meilisearch_host`, `meilisearch_port`, `meilisearch_key`, and other adapter keys.
- **Server:** `runtime_port`, `log_level`.

**Rule:** Downstream (e.g. Public Works) must not call `get_env_contract()` or read `os.environ` for platform infra. They receive only the config produced by Layer 1.

**Env files:** Before reading env, Layer 1 loads `.env.secrets`, `config/development.env`, and `.env` (if present) from the repo root, so non-secret Arango vars (e.g. in `config/development.env`) and secrets (in `.env.secrets`) are both visible. **Arango:** Supports both naming conventions: `ARANGO_USER` / `ARANGO_USERNAME`, `ARANGO_DB` / `ARANGO_DATABASE`, `ARANGO_PASS` / `ARANGO_ROOT_PASSWORD`. Blank `ARANGO_PASS` is valid (no password).

---

## Layer 2: Pre-Boot Validation

- **Module:** `pre_boot.py`
- **Entry:** `pre_boot_validate(config: Dict[str, Any]) -> None`

**Responsibility:** Consumes only the canonical config. For each required backing service (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB), runs a minimal connectivity/readiness check. Does **not** use Public Works or any adapters. On first failure: **exits the process** with a clear, actionable message (e.g. "Platform contract violation: Redis failed: ... Check REDIS_URL and retry.").

**Rule:** Pre-boot runs in `runtime_main.main()` **before** `create_runtime_services(config)`. If it returns, all required services are reachable; the object graph can be built.

---

## Runtime Entry Point Flow

1. `load_platform_config()` — Layer 1.
2. `pre_boot_validate(config)` — Layer 2 (exits on failure).
3. `create_runtime_services(config)` — Object graph built with the same config.
4. `create_fastapi_app(services)` then `uvicorn.run(...)`.

Config is loaded once; validation runs once; then the graph is built. No partial init, no "continuing anyway" when infra is missing.

---

## Layer 3 (Future)

Refactor Public Works (and any other consumers) to **consume only** the canonical config. Remove internal `get_env_contract()` and config_helper fallbacks so that the only path from env to config is Layer 1.
