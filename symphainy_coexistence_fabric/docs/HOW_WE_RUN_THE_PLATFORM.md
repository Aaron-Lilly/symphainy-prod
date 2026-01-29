# How We Run the Platform (Genesis-Aligned)

**Purpose:** One place that explains how we run the platform (local dev vs Docker), how that fits the Genesis Protocol, and what we recommend so there’s no “mix of both” confusion.

**References:** [genesis_protocol.md](genesis_protocol.md), [FOUNDATION_PLAN.md](FOUNDATION_PLAN.md), [CONFIG_ACQUISITION_SPEC.md](architecture/CONFIG_ACQUISITION_SPEC.md), [PATH_TO_WORKING_PLATFORM.md](testing/PATH_TO_WORKING_PLATFORM.md).

---

## 1. Genesis principles (unchanged by how you run)

The **same protocol** runs every time:

1. **Φ1 (Physical Viability)** — Containers/process start; env is available (injected or about to be loaded).
2. **G2 (Config loads)** — Env is populated (by Φ1 or by Φ2), then **canonical config** is built. One config source; no scattered env reads.
3. **G3 (Pre-boot)** — We **do not** enter Φ3 until pre-boot passes: all seven backing services (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB) are reachable and authorized.
4. **Φ3 (Operational Reality)** — `create_runtime_services(config)` runs; runtime graph is built in fixed order; no partial init.

So: **same gates, same order.** The only thing that changes by “how you run” is **who supplies env** (Φ1 vs Φ2) and **what hostnames/URLs** go into config (localhost vs service names vs cloud URLs).

---

## 2. Two run modes (and why it felt like a mix)

We effectively have **two** ways to run the runtime process; both use the same code path (G2 → G3 → Φ3) but differ in where env comes from and what hosts/ports mean.

| | **Mode A: Runtime on host** | **Mode B: Runtime in Docker** |
|---|-----------------------------|-------------------------------|
| **How you start** | `python runtime_main.py` (from repo root) | `docker-compose up runtime` (or `up` for full stack) |
| **Who supplies env** | **Φ2:** Process loads `.env.secrets`, `config/development.env`, `.env` (in that order). | **Φ1:** Compose injects `env_file: .env.secrets` + `environment:` block. Process does **not** read files. |
| **Hostnames/URLs** | `config/development.env` uses **localhost** (e.g. `ARANGO_URL=http://localhost:8529`) because services are on the same machine (Docker with port exposure, or local installs). | Compose `environment:` uses **service names** (e.g. `ARANGO_URL=http://arango:8529`, `MEILISEARCH_HOST=meilisearch`). |
| **What must be running** | Redis, Arango, Consul, Meilisearch (and optionally Supabase/GCS/DuckDB per contract) must be **reachable from the host** (e.g. `docker-compose up -d redis arango consul meilisearch`). Supabase/GCS/DuckDB from `.env.secrets` / config (cloud or paths). | Same seven services; when runtime is in Docker, they’re reached by service name (redis, arango, consul, meilisearch). Supabase/GCS/DuckDB still from `.env.secrets` (or compose env) — usually cloud. |

The **“mix”** was: we had **config/development.env** set up for **Mode A** (localhost), and **docker-compose** set up for **Mode B** (service names). So depending on whether you ran `python runtime_main.py` or `docker-compose up runtime`, the same code saw different env and different hosts — which is correct, but we hadn’t spelled out the two modes and which one we’re optimizing for.

---

## 3. Which path to use: containers-only vs optional local dev

**If your workflow is “start containers, run tests, rebuild on fix”** — you do **not** need a local Python env or pip on the host. Use **Mode B (containers-only)** as your primary path. The runtime image installs `requirements.txt` (including duckdb and all G3 deps); compose injects env (Φ1). Same Genesis: G2 → G3 → Φ3 inside the container.

**If you want faster iteration without image rebuilds**, you can use **Mode A (runtime on host)** as an optional path: run backing services in Docker, run `python runtime_main.py` on the host with a venv that has `pip install -r requirements.txt`. Not required.

---

### Recommended for this project: **Mode B — Containers-only**

**Why this fits your workflow:**

- **No local pip/venv:** You start containers and run tests; you don’t run Python on the host. The runtime container has all deps (Dockerfile.runtime does `pip install -r requirements.txt`).
- **Same protocol:** G2 (config from env) → G3 (pre-boot) → Φ3 inside the container. Compose supplies env (Φ1) and service names (arango, redis, meilisearch, etc.).
- **Rebuild when you change code:** `docker-compose build runtime` (or `build --no-cache` when needed). Then `docker-compose up -d` or `up runtime` and run your tests.

**Concrete steps:**

1. **Env:** `.env.secrets` at repo root (Supabase, GCS, Arango password, etc.). Compose uses `env_file: .env.secrets` and `environment:` for service URLs (arango, redis, consul, meilisearch, DuckDB path).
2. **Start stack:**  
   ```bash
   docker-compose up -d redis arango consul meilisearch
   docker-compose up -d runtime
   ```
   Or `docker-compose up -d` for the full stack. Pre-boot runs inside the runtime container; if it fails, fix the service or env and restart the runtime container.
3. **Tests:** Run your test suite against the running containers (e.g. health, intents). No need for a host Python env.
4. **After code changes:** `docker-compose build runtime` then `docker-compose up -d runtime` (or `build --no-cache` when you want a clean build).

**Summary:** Containers-only = no local dev env. Genesis unchanged; everything runs in containers; env from Φ1 (compose + .env.secrets).

---

### Optional: **Mode A — Runtime on host** (only if you want it)

Use only if you want to iterate without rebuilding the image (e.g. run `python runtime_main.py` on the host with a venv). Then you need: `pip install -r requirements.txt` in that venv, backing services via `docker-compose up -d redis arango consul meilisearch`, and `config/development.env` with localhost URLs. Not required for the containers-only workflow.

---

## 4. Mode B details (containers-only)

When the runtime runs in Docker:

- **Env:** Compose injects `.env.secrets` and the `environment:` block (service names: `arango`, `redis`, `meilisearch`, etc.). The runtime process does **not** read `config/development.env` from disk; it uses whatever compose put in `os.environ` (Φ1).
- **Deps:** The runtime image (Dockerfile.runtime) runs `pip install -r requirements.txt`, so duckdb and all other deps are in the image. No pip on the host needed.
- **Same protocol:** G2 (config from env) → G3 (pre-boot) → Φ3 inside the container.

To add or change env for the runtime container, edit `docker-compose.yml` (e.g. `MEILISEARCH_HOST=meilisearch`) or `.env.secrets` (for secrets).

---

## 5. The seven backing services (G3) — where they come from

Pre-boot always checks the same seven; only *where* they run and *how* the runtime gets their URLs/hosts differs by mode.

| Service    | Mode A (runtime on host)        | Mode B (runtime in Docker)     |
|-----------|----------------------------------|---------------------------------|
| Redis     | Docker: `localhost:6379`; URL in `config/development.env` | Compose: `redis:6379` via `REDIS_URL` in runtime env |
| Arango    | Docker: `localhost:8529`; URL in `config/development.env`; password in `.env.secrets` | Compose: `arango:8529` + `ARANGO_ROOT_PASSWORD` in runtime env |
| Consul    | Docker: `localhost:8500`; in `config/development.env` | Compose: `consul:8500` in runtime env |
| Meilisearch | Docker: `localhost:7700`; in `config/development.env` | Compose: `meilisearch:7700` in runtime env |
| Supabase  | `.env.secrets` (URL + keys) — **hosted** | Same (from `env_file` or compose) |
| GCS       | `.env.secrets` (project, bucket, credentials) — **hosted** | Same |
| DuckDB    | **Local:** `config/development.env` → `DUCKDB_DATABASE_PATH=./data/duckdb/main.duckdb` (host path; dir created on first run) | **Local:** runtime container has volume `duckdb_data:/app/data/duckdb`; `DUCKDB_DATABASE_PATH=/app/data/duckdb/main.duckdb` |

**Local (in Docker or on host):** Redis, Arango, Consul, Meilisearch, DuckDB. **Hosted (external):** Supabase, GCS. DuckDB is embedded (file-based); there is no “DuckDB server” container — the runtime uses a file path. For Mode A we use `DUCKDB_DATABASE_PATH=./data/duckdb/main.duckdb` in `config/development.env` (host path); for Mode B the runtime container has volume `duckdb_data:/app/data/duckdb`. Meilisearch and a DuckDB volume are in `docker-compose.yml`; `docker-compose up -d redis arango consul meilisearch` gives the four local *services*; DuckDB is just a volume mount for the runtime when it runs in Docker, or a host path when runtime runs on host.

---

## 6. What we changed to reduce the “mix”

- **Meilisearch in docker-compose** — So “infra only” (redis, arango, consul, meilisearch) is one command; runtime on host uses `config/development.env` with `MEILISEARCH_HOST=localhost`, `MEILISEARCH_PORT=7700`.
- **DuckDB (local, not a server)** — Embedded DB: no separate container. Runtime-on-host uses `DUCKDB_DATABASE_PATH=./data/duckdb/main.duckdb` in `config/development.env` (dir created on first run). Runtime-in-Docker uses volume `duckdb_data:/app/data/duckdb` and `DUCKDB_DATABASE_PATH=/app/data/duckdb/main.duckdb`. So all local backing stores are either in Docker (Redis, Arango, Consul, Meilisearch) or a local path/volume (DuckDB); only Supabase and GCS are hosted.
- **This doc** — One place that defines Mode A vs Mode B, aligns them with Genesis (Φ1 vs Φ2, same G2/G3/Φ3), and recommends Mode A for local dev.
- **config/development.env** — Non-secret localhost URLs and DuckDB path for Mode A; secrets stay in `.env.secrets`.

No change to Genesis or to the bootstrap/pre-boot code — only clarity on *how* we run and *which* mode we optimize for (runtime on host, backing services from Docker).

---

## 7. Quick reference

- **Containers-only (recommended for this project):**  
  `docker-compose up -d redis arango consul meilisearch` then `docker-compose up -d runtime` (or `up -d` for full stack).  
  Env: Φ1 (compose + `.env.secrets`). No local pip/venv. Rebuild runtime after code changes: `docker-compose build runtime` (or `build --no-cache` when needed).

- **Optional local dev (runtime on host):**  
  `docker-compose up -d redis arango consul meilisearch` → create venv, `pip install -r requirements.txt` → `python runtime_main.py`.  
  Env: `.env.secrets` + `config/development.env` (localhost). Use only if you want faster iteration without image rebuilds.

- **Pre-boot fails?**  
  Fix the service or the config key the message names (e.g. Arango 401 → password in `.env.secrets`; Meilisearch connection refused → start meilisearch or fix host/port). Then restart the runtime container (or rerun if on host).
