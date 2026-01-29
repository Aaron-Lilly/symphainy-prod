# Step 0: Foundation Open Questions (Phase 0 Discovery)

**Purpose:** Make explicit what we don’t know and what we must decide so Gate G2 (config loads) and Gate G3 (enter Φ3) are well-defined. Each question is answered from: (1) Genesis Protocol / north star vision, (2) how the platform actually behaves today, (3) recommended answer. CTO review list and validations are at the end.

**Status:** Phase 0 complete. CTO validated (all items confirmed; clarifications applied). Ready to proceed to Steps 1–2.

**CTO verdict (summary):** Phase separation, single-source-of-truth, deterministic startup, and gated operational reality are correctly internalized. No conceptual misunderstandings. Minor clarifications applied (e.g. .env = defaults/docs only; blank ARANGO_PASS allowed only in dev/CI, forbidden in prod/staging). **Proceed confidently to implement Genesis Protocol enforcement in code.**

**References:** [FOUNDATION_PLAN.md](FOUNDATION_PLAN.md) Step 0, [genesis_protocol.md](genesis_protocol.md), [PLATFORM_CONTRACT.md](architecture/PLATFORM_CONTRACT.md), [HYBRID_CLOUD_VISION.md](HYBRID_CLOUD_VISION.md).

---

## 1. Which env files does this project use, and in which environments?

### 1.1 Open question

Which env files does this project use, in which environments (dev, prod, Docker, CI)? (.env, .env.secrets, config/development.env, others?)

### 1.2 Answer based on Genesis Protocol and north star vision

- **Φ1 (Physical Viability):** “Secrets load” and “Env vars exist” are part of G1. So by the time we enter Φ2, the process must have a defined way to have env vars: either Docker injects them (Φ1) or the process loads them as the first step of Φ2.
- **Gate G2:** “Config loads” means we have a **defined list** of env files, their paths, and load order. No implicit “whatever is in the shell.”
- **North star (Option C):** Same protocol whether running in Docker or against managed services; only the *source* of env (compose env_file vs process-loaded files vs orchestrator-injected) may differ by environment. We should document: per environment (Docker, local dev, CI, prod), which files apply and who loads them.

### 1.3 Answer based on how the platform actually behaves today

- **Docker (runtime service):** `docker-compose.yml` specifies `env_file: .env.secrets` and an `environment:` block with REDIS_URL, ARANGO_*, CONSUL_*, RUNTIME_PORT, LOG_LEVEL. So in Docker, env vars come from (1) `.env.secrets` (injected by Docker at container start) and (2) the `environment:` block (and host env when compose is run). No `.env` or `config/development.env` in compose.
- **Local dev (no Docker):** `runtime_main` does not import `service_config`. It imports `bootstrap` and calls `load_platform_config()`. Inside bootstrap, `_ensure_env_loaded()` runs first and loads (from repo root) `.env.secrets`, `config/development.env`, `.env` if each exists. So **today** local dev relies on bootstrap to load files; without that, only shell-exported vars would be visible. `get_env_contract()` uses only `os.getenv()` and does not load any file itself.
- **Tests (3d real_infrastructure):** `conftest.py` explicitly loads `.env.secrets` via `load_dotenv()` from project root (or `symphainy_platform/.env.secrets`, or cwd) before tests run. So tests that need secrets load them themselves.
- **Other code paths:** `service_config` loads `.env.secrets` at **import time** from one of several paths (project root, symphainy_platform/, parent, cwd). But `runtime_main` does **not** import `service_config`; it only imports bootstrap. So when we run `python runtime_main.py`, service_config is never imported and its `_load_env_secrets()` never runs unless some other imported module imports service_config. `config_helper` does not load at import; it loads `.env.secrets` only when a helper (e.g. `get_supabase_url()`) is called and then only if the env var is missing. Public Works calls `get_env_contract()` and `config_helper` in several places, so if bootstrap didn’t load files first, Public Works would see only what’s in `os.environ` at that moment.
- **Files that exist:** Repo has `.env.secrets` at repo root (per user and .gitignore). There is no `config/` at repo root in the tree; `.env.secrets` comment says “ARANGO_URL, ARANGO_DB, ARANGO_USER are in config/development.env” and “only passwords go here”—so `config/development.env` is a **convention** for non-secret vars (may exist only on some machines or in some setups, not committed).

### 1.4 Recommended answer

- **Env files we define as part of the contract:**  
  (1) **`.env.secrets`** at repo root — secrets (passwords, API keys).  
  (2) **`config/development.env`** at repo root — non-secret config (URLs, hosts, DB names, user names); optional file (may not exist in all environments).  
  (3) **`.env`** at repo root — optional fallback; optional file.
- **Environments:**  
  - **Docker:** Docker injects `.env.secrets` via `env_file`; compose `environment:` supplies service URLs and ports. We document that in Docker, Φ1 is responsible for “env vars exist” (compose + env_file). No process-side file load required for Docker if we rely on compose.  
  - **Local dev (no Docker):** Process must load env files; designated place is the first step of Φ2 (config acquisition). Load order: `.env.secrets`, `config/development.env`, `.env` (each if present), from repo root.  
  - **CI:** Define explicitly (e.g. CI injects env; or CI places a specific env file and process loads it in Φ2).  
  - **Prod / Option C:** Same as local dev for “process loads files” if not using an orchestrator that injects env; if using GCP/K8s secrets, env may be injected (Φ1 equivalent) and no file load needed.  
- **CTO tightening:** `.env` = **defaults + documentation + non-secret fallback only**. Do not use `.env` for secrets or environment-specific overrides (that would be `.env.secrets` or `config/development.env`). Discourage treating `.env` as “.env.secrets-lite.”

---

## 2. Who loads env files today, and when?

### 2.1 Open question

Who loads env files today? (Docker env_file? Import of service_config? config_helper? Bootstrap? Nothing?)

### 2.2 Answer based on Genesis Protocol and north star vision

- **Single responsibility:** One designated place loads env files, and it runs **before** any code that reads config for platform infra. That is the first mechanical step of Φ2 (Runtime Consciousness). No “maybe some other import already loaded them.”
- **G2:** “Config loads” implies “env files have been loaded (if applicable) then canonical config has been built.” So “who loads” must be explicit and guaranteed to run first.

### 2.3 Answer based on how the platform actually behaves today

- **When entry is `runtime_main.main()`:**  
  - `runtime_main` imports `bootstrap` and calls `load_platform_config()`.  
  - Inside `load_platform_config()`, `_ensure_env_loaded()` runs first and calls `load_dotenv()` for `.env.secrets`, `config/development.env`, `.env` (from repo root, if each exists). So **bootstrap** loads env files, and only when we use the bootstrap path.  
- **When Docker runs the runtime container:** Docker injects `.env.secrets` via `env_file`; the process does not read the file from disk. So **Docker** loads (injects) .env.secrets; the process just sees `os.environ` already populated.  
- **If someone ran code that only used `get_env_contract()` without ever calling bootstrap:** Then no one would load .env.secrets or config/development.env; only shell/compose env would be visible. That was the pre-bootstrap bug.  
- **service_config:** Loads `.env.secrets` at **import** time from one of several paths. But runtime_main does not import service_config, so in the normal runtime_main path, service_config never runs.  
- **config_helper:** Loads `.env.secrets` only when a helper (e.g. get_supabase_url()) is called and the env var is missing. So loading is on-demand and scattered.  
- **Tests (3d):** conftest loads `.env.secrets` explicitly before tests.

### 2.4 Recommended answer

- **Designated loader:** The **first step of Φ2** (config acquisition) is the single place that loads env files when the process is responsible for loading (i.e. when not relying on Docker/orchestrator to inject env). In code, that is the same as “first thing inside `load_platform_config()`” (or a dedicated “acquire env” function called by main/runtime_main before building config).  
- **Docker:** We treat Docker’s `env_file` as Φ1 (Physical Viability); the process does not load .env.secrets from disk in that case. So “who loads” is: **Docker** in Docker mode; **process (Φ2 config acquisition)** in local dev / any mode where env is not pre-injected.  
- **Eliminate scattered loading:** We should not rely on service_config import or config_helper on-demand loading for platform boot. Contract: “By the time we build canonical config, env has been loaded by the designated Φ2 step (or by Φ1 in Docker).”

---

## 3. Where do env files live?

### 3.1 Open question

Where do env files live? (repo root, config/, elsewhere?)

### 3.2 Answer based on Genesis Protocol and north star vision

- **Fixed, documented paths:** So that “config loads” (G2) is deterministic, paths must be defined relative to a known root (e.g. repo root or process cwd). No guessing.

### 3.3 Answer based on how the platform actually behaves today

- **Bootstrap `_ensure_env_loaded()`:** Resolves repo root as `Path(__file__).resolve().parents[2]` (from `symphainy_platform/bootstrap/platform_config.py`), then looks for `.env.secrets`, `config/development.env`, `.env` under that root. So “repo root” = directory containing `symphainy_platform/`.  
- **service_config:** Uses `Path(__file__).resolve().parents[3]` as project root (one level up from bootstrap’s), then looks for `.env.secrets` in several places including that root and `symphainy_platform/.env.secrets`. So there is a slight inconsistency (parents[2] vs parents[3]) depending on where __file__ is.  
- **config_helper _find_env_secrets():** Looks for `.env.secrets` in: `symphainy_platform/.env.secrets`, `symphainy_platform/.env.secrets` (cwd-relative), `.env.secrets` (cwd), and several other paths.  
- **.env.secrets:** User and docs refer to “project root” or “symphainy_coexistence_fabric/”; docker-compose uses `env_file: .env.secrets` (compose file is at repo root, so .env.secrets is at repo root).  
- **config/development.env:** Not present in repo; convention is “config/development.env” under repo root for non-secret vars.

### 3.4 Recommended answer

- **Repo root:** The single definition of “repo root” for env file paths is: the directory that contains the `symphainy_platform` package (i.e. the workspace root of the coexistence fabric repo). All env file paths are relative to that directory.  
- **Paths:**  
  - `.env.secrets` at repo root (required for secrets when not using Docker env_file).  
  - `config/development.env` at repo root (optional; non-secret config).  
  - `.env` at repo root (optional).  
- **Resolve repo root in one place:** Use a single helper (e.g. “get repo root”) so that bootstrap and any future code use the same definition (e.g. from runtime_main’s __file__ or from a known marker). Document that when running in Docker, “repo root” may still be the app directory inside the container if we ever read files there; for Docker today we don’t read .env.secrets from disk.

---

## 4. For each required backing service, which env keys (and which file) are the source of truth?

### 4.1 Open question

For each required backing service (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB), which env keys—and which file—are the source of truth? Include naming variants (e.g. ARANGO_USER vs ARANGO_USERNAME).

### 4.2 Answer based on Genesis Protocol and north star vision

- **Config contract:** One canonical shape; each key has a defined provenance (env var name(s), which file(s) if any). So we can document “Arango password comes from ARANGO_PASS or ARANGO_ROOT_PASSWORD, typically in .env.secrets (or injected).”

### 4.3 Answer based on how the platform actually behaves today

- **EnvContract / get_env_contract():** Uses: REDIS_URL, ARANGO_URL, ARANGO_ROOT_PASSWORD, CONSUL_HOST, CONSUL_PORT, CONSUL_TOKEN, SUPABASE_URL, SUPABASE_ANON_KEY (from os.getenv("SUPABASE_PUBLISHABLE_KEY")), SUPABASE_SERVICE_KEY (from os.getenv("SUPABASE_SECRET_KEY")), GCS_*, MEILISEARCH_PORT, MEILI_MASTER_KEY, RUNTIME_PORT, LOG_LEVEL, etc. No ARANGO_USER, ARANGO_DB, ARANGO_PASS in EnvContract; no MEILISEARCH_HOST; no DUCKDB_* in EnvContract.  
- **Bootstrap platform_config:** After loading env files, builds canonical config. Uses: env.ARANGO_URL, os.getenv("ARANGO_USERNAME") or os.getenv("ARANGO_USER"), os.getenv("ARANGO_DATABASE") or os.getenv("ARANGO_DB"), os.getenv("ARANGO_PASS") or os.getenv("ARANGO_ROOT_PASSWORD") or env.ARANGO_ROOT_PASSWORD; MEILISEARCH_HOST from os.getenv("MEILISEARCH_HOST"); DUCKDB_* from os.getenv; redis/consul/duckdb nested from REDIS_URL, CONSUL_*, duckdb path.  
- **docker-compose:** Supplies ARANGO_USERNAME, ARANGO_DATABASE, ARANGO_ROOT_PASSWORD, REDIS_URL, ARANGO_URL, CONSUL_HOST, CONSUL_PORT, RUNTIME_PORT, LOG_LEVEL; secrets (Supabase, GCS, etc.) come from .env.secrets via env_file.  
- **.env.secrets comment:** Says ARANGO_URL, ARANGO_DB, ARANGO_USER are in config/development.env and only passwords go in .env.secrets; ARANGO_PASS can be blank.

### 4.4 Recommended answer

- **Single table (source of truth for canonical config):**  

| Backing service | Canonical key(s) | Env var(s) (precedence) | Typical file |
|-----------------|------------------|---------------------------|--------------|
| Redis | redis (nested) | REDIS_URL | .env or compose |
| Arango | arango_url, arango_username, arango_password, arango_database | ARANGO_URL; ARANGO_USERNAME or ARANGO_USER; ARANGO_ROOT_PASSWORD or ARANGO_PASS; ARANGO_DATABASE or ARANGO_DB | URL/user/db: config/development.env or compose; password: .env.secrets. **CTO:** Blank ARANGO_PASS allowed in dev + CI only; blank forbidden in prod/staging. |
| Consul | consul (nested) | CONSUL_HOST, CONSUL_PORT, CONSUL_TOKEN | .env or compose |
| Supabase | supabase_url, supabase_anon_key, supabase_service_key, ... | SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY or SUPABASE_ANON_KEY, SUPABASE_SECRET_KEY or SUPABASE_SERVICE_KEY, ... | .env.secrets / compose |
| GCS | gcs_project_id, gcs_bucket_name, gcs_credentials_json | GCS_PROJECT_ID, GCS_BUCKET_NAME, GCS_CREDENTIALS_JSON | .env.secrets |
| Meilisearch | meilisearch_host, meilisearch_port, meilisearch_key | MEILISEARCH_HOST, MEILISEARCH_PORT, MEILI_MASTER_KEY | .env or compose |
| DuckDB | duckdb (nested) | DUCKDB_DATABASE_PATH, DUCKDB_READ_ONLY | .env or config |

- **Naming variants:** Support both: ARANGO_USER / ARANGO_USERNAME, ARANGO_DB / ARANGO_DATABASE, ARANGO_PASS / ARANGO_ROOT_PASSWORD; SUPABASE_PUBLISHABLE_KEY → anon, SUPABASE_SECRET_KEY → service_key. Document in config contract.

---

## 5. Φ1 vs Φ2: Who is responsible for “env vars exist”?

### 5.1 Open question

If Docker injects env via `env_file`, is that sufficient for G1 (Physical Viability)? If the process runs without Docker (e.g. local dev), must Φ2 load env files before building config?

### 5.2 Answer based on Genesis Protocol and north star vision

- **Φ1:** “Secrets load, Env vars exist” — in Docker, that means compose has started the container with env_file and environment block; the process sees env. So Φ1 (Docker) is responsible.  
- **Φ2:** “Config loads” — if the process is started without pre-injected env (e.g. `python runtime_main.py` on a dev machine), then the first step of Φ2 must be “load env files then build config.” So responsibility is split by deployment: Φ1 when Docker/orchestrator injects; Φ2 when the process loads files.

### 5.3 Answer based on how the platform actually behaves today

- **Docker:** Compose sets env_file and environment; process never reads .env.secrets from disk. So “env vars exist” is satisfied by Docker.  
- **Local dev:** If we run `python runtime_main.py` without exporting vars, bootstrap’s `_ensure_env_loaded()` loads .env.secrets, config/development.env, .env. So today we rely on Φ2 (bootstrap) to load when not in Docker.

### 5.4 Recommended answer

- **Docker (or any env-injected run):** Φ1 is responsible for “env vars exist.” G1 passes when containers are up and env is injected. Process does not load env files.  
- **Local / non-Docker (process started without pre-injected env):** Φ2’s first step is “load env files (in defined order) then build canonical config.” G2 passes when that step has run and config is built.  
- **Document both paths** in the Config Acquisition spec so that “who loads” is unambiguous per deployment mode.

---

## 6. Capability vs foundation: What is “required at boot” (G3) vs “required when an intent runs”?

### 6.1 Open question

Which dependencies are “required at boot” (Gate G3) vs “required when an intent runs” (e.g. Cobrix, LLM)? Clarify “backing service vs library vs Civic” for §9.

### 6.2 Answer based on Genesis Protocol and north star vision

- **G3:** “Public Works connects to backing services” — so at boot we validate **only** the backing services that Public Works must have to build the full runtime graph (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB per PLATFORM_CONTRACT §3).  
- **North star:** Option C and “single source of truth” require that the **data plane** and **control plane** are reachable at boot. LLM/Cobrix/Kreuzberg are **capabilities** used by specific intents; they can be “required for the platform to deliver” but “validated at first use” or “validated in Φ4/Φ5” rather than blocking Φ3.  
- **Backing service vs library vs Civic:** Backing service = external process/store we connect to (Redis, Arango, Cobrix service). Library = in-process dependency (pandas, openpyxl). Civic = surface provided by Civic Systems (Artifact Plane, Telemetry). G3 should require only the backing services that are needed to construct the runtime graph and pass RuntimeServices; libraries can be “importable by G2 or first use”; Civic can be “injected by Φ3.”

### 6.3 Answer based on how the platform actually behaves today

- **Pre-boot (bootstrap):** Currently validates Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB. Does not validate LLM, HuggingFace, Cobrix, Kreuzberg, or pandas.  
- **Public Works:** Creates adapters for Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB when config is present. Also creates OpenAI/HuggingFace adapters when keys are present; Kreuzberg when config; Cobrix when config. If Redis/Consul/DuckDB config is missing (e.g. flat config without nested blocks), those adapters are not created and we get “continuing anyway.”  
- **PLATFORM_CONTRACT §9:** Says EDI, parsing (including Cobrix “likely required soon”), pandas/openpyxl, LLM/HF, visualization are required for the platform to deliver; but §3 and §5 only list the seven backing services for pre-boot. So “required for delivery” is not the same as “required for G3.”

### 6.4 Recommended answer

- **Required at boot (G3):** Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB. Pre-boot validates these only. No Cobrix, LLM, or Kreuzberg at G3.  
- **Required for platform to deliver (by Φ3 or first use):**  
  - **Libraries:** pandas, openpyxl (and plotly, numpy, PyYAML) — required in environment; we can add a G2 or first-use check that they are importable.  
  - **Backing services used by intents:** LLM (OpenAI), HuggingFace, Cobrix, Kreuzberg, EDI config — required for specific intents; we do **not** block Φ3 on them. Option: “validate at first use” or a separate “capability check” in Φ4/Φ5.  
  - **Civic:** Artifact Plane, Telemetry — must be provided (injected or on Public Works) by the end of Φ3 or when an intent that needs them runs; not a connectivity check in pre-boot.  
- **Refine §9** to separate “required at G3” vs “required for intents” vs “libraries” vs “Civic,” so Cobrix (container) and pandas (library) are clearly different layers.
- **CTO:** Blocking startup on LLMs or OCR containers would be a guaranteed operational nightmare; G3 scope is correct.

---

## 7. Is config/development.env required or optional?

### 7.1 Open question

Is `config/development.env` a required file or optional? It does not exist in the repo; the convention (from .env.secrets comment) is that non-secret Arango vars live there.

### 7.2 Answer based on Genesis Protocol and north star vision

- **Determinism:** If we require it, G2 must fail clearly when it’s missing. If it’s optional, we must define what happens when it’s absent (e.g. all values from .env.secrets and .env only).

### 7.3 Answer based on how the platform actually behaves today

- **Repo:** No `config/` at repo root; no committed config/development.env. So today it’s an optional/local file.  
- **Bootstrap:** Loads it “if present”; does not require it.  
- **Docker:** Compose does not reference config/development.env; all non-secret vars come from the `environment:` block. So in Docker we don’t use that file.

### 7.4 Recommended answer

- **Optional.** config/development.env is an optional file for local dev (non-secret config). If absent, we rely on .env.secrets, .env, and/or shell/compose env. G2 does not fail when it’s missing. We document that when using “ARANGO_USER, ARANGO_DB in config/development.env,” the file must exist and be loaded in Φ2 for those vars to apply.

---

## 8. Supabase env key names: Publishable and Secret (supported); Anon/Service deprecated

### 8.1 Open question

EnvContract uses field names SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY but get_env_contract() reads os.getenv("SUPABASE_PUBLISHABLE_KEY") and os.getenv("SUPABASE_SECRET_KEY"). Which names are canonical for the config contract?

### 8.2 Answer based on Genesis Protocol and north star vision

- **One canonical mapping:** Config contract should list the env var names we read. Those should align with what the backing service (Supabase) supports.

### 8.3 Answer based on how the platform actually behaves today

- **get_env_contract():** Reads SUPABASE_PUBLISHABLE_KEY and SUPABASE_SECRET_KEY (and maps them into EnvContract fields). So the code already uses the names Supabase supports.
- **Supabase:** Publishable and Secret are the supported names. Anon/Service were deprecated by Supabase and are no longer supported.

### 8.4 Recommended answer (CTO-validated)

- **Canonical env var names (Supabase-supported):** **SUPABASE_PUBLISHABLE_KEY** and **SUPABASE_SECRET_KEY**. Everything else (SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY) was deprecated by Supabase and is no longer supported.
- **Config contract:** We read only SUPABASE_PUBLISHABLE_KEY → canonical key for anon/publishable key; SUPABASE_SECRET_KEY → canonical key for service/secret key. Internal config keys (e.g. supabase_anon_key, supabase_service_key) are populated from these two env vars only. Do not document or support the deprecated anon/service env var names as alternatives.

---

## 9. What exactly must be true before Φ3 is allowed to start? (Meta: Φ3 preconditions)

*Added per CTO meta-improvement: force operational rigor by answering this explicitly.*

### 9.1 Open question

What exactly must be true before Φ3 (Operational Reality / Runtime Graph Construction) is allowed to start? Require: concrete health checks, specific connection tests, explicit failure semantics.

### 9.2 Answer based on Genesis Protocol and north star vision

- **Gate G3:** “Public Works connects to backing services” means we have **passed** a defined set of checks before we call `create_runtime_services()`. No “try to build the graph and see what fails.”
- **Operational rigor:** Each required backing service has: (1) a concrete health/connection check (e.g. connect + ping, or minimal API call), (2) explicit failure semantics (e.g. exit process with one clear message, no partial init). So “what must be true before Φ3” = “pre-boot validation has passed for all seven backing services.”

### 9.3 Answer based on how the platform actually behaves today

- **Bootstrap pre_boot.py:** Already implements checks for Redis (ping), Arango (connect + db.version()), Consul (agent.self()), Supabase (GET rest/v1/ with service key), GCS (bucket.reload()), Meilisearch (GET /health), DuckDB (connect + SELECT 1). On first failure: `_fail(service, reason, hint)` → log + sys.exit(1). So we have concrete checks and failure semantics; they are not yet documented as the formal “Φ3 preconditions” contract.

### 9.4 Recommended answer

- **Φ3 is allowed to start only when:** Pre-boot validation has completed successfully for all seven backing services (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB), using **only** the canonical config (no env reads inside pre-boot).
- **Concrete health checks (per service):** Document in the **Pre-Boot spec** (Step 3): exact check (e.g. “Redis: connect, ping”), timeout, and what “success” means.
- **Explicit failure semantics:** Any single failure → process exits immediately with one clear message: “Platform contract violation: [SERVICE] failed: [reason]. [Hint].” No partial init; no “continuing anyway.”
- **Order:** Pre-boot runs in the process entry path (e.g. runtime_main) **after** canonical config is built and **before** `create_runtime_services(config)`. So “what must be true before Φ3” = “G2 passed (config loaded) and pre-boot (G3 entry) passed.”

---

## Phase 0: CTO Review — Validated and Clarifications Applied

**CTO assessment (summary):** Phase separation, single-source-of-truth, deterministic startup contracts, and gated operational reality are correctly internalized. No conceptual misunderstandings. Minor clarifications and tightening applied below. **Verdict: Confidently proceed to implement Genesis Protocol enforcement in code.**

| # | Item | Status | CTO clarification / tightening |
|---|------|--------|-------------------------------|
| 1 | Env files and environments (1.4) | ✅ Confirmed | **.env** = defaults + documentation + non-secret fallback only. Do not use .env for secrets or env-specific overrides (avoid “.env.secrets-lite”). Confirmed for dev, CI, prod/Option C. |
| 2 | Single designated loader (2.4) | ✅ Strong yes | Exactly one env acquisition point. Hard architectural invariant. No reliance on service_config or config_helper for boot. |
| 3 | Repo root definition (3.4) | ✅ Lock in | Repo root = directory containing `symphainy_platform`. Single helper, no ambiguity. |
| 4 | Source-of-truth table (4.4) | ✅ Confirmed | **Blank ARANGO_PASS:** acceptable only in dev + CI; **forbidden in prod/staging.** Table and naming variants = canonical config contract. |
| 5 | Φ1 vs Φ2 responsibility (5.4) | ✅ Perfect | Docker: Φ1 supplies env; process only consumes. Non-Docker: Φ2 loads files then builds config. |
| 6 | G3 scope: seven backing services (6.4) | ✅ Fully confirmed | G3 = existence, not full operational capability. Blocking startup on LLMs or OCR containers = guaranteed operational nightmare. |
| 7 | config/development.env optional (7.4) | ✅ Correct | Optional; document “if you use ARANGO_USER/ARANGO_DB in that file, create it and ensure Φ2 loads it.” |
| 8 | Supabase env var names (8.4) | ✅ Confirmed | Publishable and secret only (SUPABASE_PUBLISHABLE_KEY, SUPABASE_SECRET_KEY). |

**Meta-improvement (CTO):** Answer explicitly: *“What exactly must be true before Φ3 is allowed to start?”* — **Section 9** above and the **Pre-Boot spec (Step 3)** will define: concrete health checks, specific connection tests, explicit failure semantics. Φ3 starts only when G2 (config loaded) and pre-boot (G3 entry) have passed.

---

**Next:** Proceed to **Step 1 (Config Acquisition spec)** and **Step 2 (Config Contract spec)** using the recommended answers and CTO clarifications as the basis. **Step 3 (Pre-Boot spec)** will formalize “what must be true before Φ3” with concrete checks and failure semantics.
