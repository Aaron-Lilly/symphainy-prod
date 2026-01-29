# Path to Working Platform (Hybrid: Contract First, Then Discover)

**Problem:** We were starting too deep—tracing boot step-by-step and documenting failure modes (Arango fails → registry_abstraction None → confusing). That produces a lot of confusion with no clear path to resolution. Arango (and other essentials) are **not** optional; the default assumption is **nothing optional at boot**. We need both: understand what we built **and** a roadmap to get to a working platform.

**Source of truth for "what we have vs what we need":** See [PLATFORM_INVENTORY.md](PLATFORM_INVENTORY.md) for containers and config shape. **Canonical contract for required infra and guarantees:** See [PLATFORM_CONTRACT.md](../architecture/PLATFORM_CONTRACT.md). The platform contract defines that **no** infra is optional (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB are all required) and what the pre-boot check must validate. Pre-boot must enforce the contract.

**Hybrid approach:** Define the **platform contract** and **fail at the door** before we build the object graph. Then discovery documents "what we built when the contract holds." The roadmap is: satisfy the contract → boot → first request → critical path → expand.

---

## 1. Why this helps

| Before (deep-first) | After (contract-first) |
|--------------------|------------------------|
| We trace boot, hit Arango failure, then registry_abstraction None. | We **check Arango first**. If it fails, we exit with "Arango required; connection failed: 401." We never enter partial init. |
| Thousands of points of confusion (which adapter, which order, why None). | One clear failure: "Pre-boot check failed: Arango." Fix Arango (or env); retry. |
| "What we built" = mix of intended flow and failure modes. | "What we built" = intended flow **when** infra is ready. Probes document that. |
| No path to resolution. | Roadmap: Step 0 (infra) → Step 1 (boot) → Step 2 (one path) → Step 3 (expand). |

---

## 2. Platform contract (nothing optional at boot)

**Assumption:** Essential infrastructure is **required** at boot. If it's not ready, we do not start the object graph.

**Essential at boot (codified in [PLATFORM_CONTRACT.md](../architecture/PLATFORM_CONTRACT.md)):**

- **Redis** — reachable. Required for state, WAL, events, cache.
- **ArangoDB** — reachable, authorized (no 401). Required for durable state, semantic data, lineage.
- **Consul** — reachable. Required for service discovery.
- **Supabase** — reachable (DB + file). Required for registry, auth, file/artifact metadata.
- **GCS** — reachable, authorized. Required for file/artifact blobs.
- **Meilisearch** — reachable. Required for search/discovery.
- **DuckDB** — path writable/readable. Required for deterministic embeddings.
- **Config (env)** — required keys present and valid per contract; one source drives all adapters.

**Pre-boot validation (fail at the door):**

- **Before** `create_runtime_services()` (or at the very start of it), run a **readiness check**: connect to Arango (and Redis, etc.) with the configured credentials. If any check fails, **exit immediately** with a clear message, e.g.  
  `"Platform requires Arango. Pre-boot check failed: Arango connection refused (401 not authorized). Fix ARANGO_URL / ARANGO_ROOT_PASSWORD and retry."`
- No partial init. No "PublicWorks had issues, continuing anyway." No reaching RuntimeServices with registry_abstraction None.

**Implementation:** Pre-boot and config live in the **bootstrap** layer. See `symphainy_platform/bootstrap/` (Layer 1: `load_platform_config()`, Layer 2: `pre_boot_validate(config)`). `runtime_main.main()` calls Layer 1 → Layer 2 → `create_runtime_services(config)` so we never touch PublicWorks if infra is not ready.

**Wider plan:** The full foundation plan (config acquisition, config contract, pre-boot, init order) aligned with the [Platform Runtime Genesis Protocol](../genesis_protocol.md) and hybrid cloud is in **[FOUNDATION_PLAN.md](../FOUNDATION_PLAN.md)**. That plan defines Gate G2 and G3, discovery-first, and the get-started order. **How we run** (runtime on host vs Docker, recommended local-dev path) is in **[HOW_WE_RUN_THE_PLATFORM.md](../HOW_WE_RUN_THE_PLATFORM.md)**. Use it to avoid past sins (e.g. env files never loaded) and to avoid “mix of both” confusion.

---

## 3. Roadmap: Path to Working Platform

**Gate mentality:** Each step has a single, clear gate. If the gate fails, the message tells you what to fix. No digging through layers.

| Step | Gate | What "working" means | If it fails |
|------|------|----------------------|-------------|
| **0. Infra contract** | Pre-boot check passes (Arango, Redis, required env). | Required services are reachable and authorized; config is valid. | Exit with clear error: "Pre-boot check failed: [service]: [reason]." Fix that service or env. |
| **1. Boot to first request** | Process starts; GET /health returns 200 and body `{"status":"healthy",...}`. | Server is up; first request path works. | Logs + error point to missing service or code bug. Fix infra (step 0) or fix object-graph bug. |
| **2. One critical path** | One flow works end-to-end (e.g. file upload → parse → artifact, or auth → session). | You can show one user-facing path that works. | Fix the path (intent, journey, or integration). |
| **3. Expand** | More paths, more probes. | Platform is "working" for a defined set of capabilities. | Document and fix per path or per layer. |

**Order of work:**

1. **Implement Step 0:** Add pre-boot validation (Arango, Redis, required env). Fail fast with clear message. No optional infra at boot.
2. **Re-run Phase 0:** Start runtime. Either pre-boot fails (fix Arango/Redis/env) or boot completes and GET /health succeeds. Document result.
3. **Step 2:** Pick one critical path (e.g. file upload → parse). Make it pass. Gate = that path works.
4. **Step 3:** Expand (more paths, more probes). Probes and reality maps describe "what we built" **when the contract holds**.

---

## 4. How discovery (probes) fits in

- **Probes and reality maps** answer: "When the platform contract is satisfied, how does it actually work?" So we document the **intended** flow: entry point, boot order, first request, Public Works, Curator, Civic, Realms, etc.
- **We do not** use probes to enumerate every failure mode. Failure modes are handled by: (1) pre-boot check (infra), (2) clear errors at each gate. So "registry_abstraction is None" is not a user-facing puzzle—it simply should not happen if pre-boot check passes (Arango up → full init → registry_abstraction set).
- **Stability/Gravity reports** still apply when we see **architectural** tension (e.g. a seam that keeps causing bugs). But the primary path to resolution is: satisfy contract → pass gates → then document behavior.

---

## 5. Concrete next steps

1. **Add pre-boot check** (see below). Require Arango (and Redis if required) at entry. Fail with one clear message if not ready.
2. **Remove or tighten "continuing anyway"** in service_factory when PublicWorks.initialize() fails—either fail the boot or make pre-boot the only way infra can be wrong. Prefer: pre-boot is the single place we check infra; if we get to PublicWorks, we assume infra is ready (and PublicWorks can still fail if something is misconfigured we didn't check).
3. **Re-run Phase 0** with Arango fixed (or with pre-boot in place). Confirm gate: boot → GET /health 200.
4. **Document "what we built"** (Platform Operation Map, Phase 0 evidence) **assuming** step 0 and 1 pass. Probes continue for deeper layers (Public Works, Curator, etc.) under that assumption.

---

## 6. Pre-boot check (minimal design)

**Where:** `runtime_main.main()` at the very top, right after `get_env_contract()`, **before** `create_runtime_services(config)`.

**What:**

- **Arango:** Using config (ARANGO_URL, ARANGO_ROOT_PASSWORD, database name), create a minimal connection (e.g. connect and call `db.properties()` or equivalent). If it raises or returns auth error, exit with:  
  `"Platform requires Arango. Pre-boot check failed: [exception or 401]. Check ARANGO_URL, ARANGO_ROOT_PASSWORD."`
- **Redis (if required):** Same idea: connect, ping. If failed, exit with clear message.
- **Required env keys:** Validate that required keys are present and valid (e.g. ports in range, LOG_LEVEL in allowed set). If not, exit with:  
  `"Pre-boot check failed: [key] invalid or missing."`

**Result:** Either all checks pass and we proceed to `create_runtime_services()`, or we exit with one clear reason. No partial init, no "registry_abstraction is None" deep in the stack.

---

## 7. Summary

- **Wrong layer:** Starting from deep inside boot (adapters, order, registry_abstraction) led to documenting confusion with no path to resolution.
- **Right layer:** Start from **platform contract** (nothing optional at boot) and **pre-boot check** (fail at the door). Then roadmap: Step 0 (infra) → Step 1 (boot to first request) → Step 2 (one critical path) → Step 3 (expand).
- **Probes:** Document "what we built" when the contract holds. Failure modes are handled by pre-boot and gates, not by documenting every branch.
- **Next:** Implement pre-boot check; require Arango (and Redis if required); re-run Phase 0; then continue discovery and one critical path.

---

## 8. Container health checks and Step 2 order (critical paths)

**Outstanding to-do (closed):** Fix container health checks so "healthy" means *actually usable*, not just "port open" or "TCP up."

**What was wrong:**

- **Arango:** Healthcheck used `nc -z 127.0.0.1 8529` → container could be "healthy" while runtime got 401 (auth not verified).
- **Experience:** Healthcheck used TCP-only `</dev/tcp/127.0.0.1/8001` → container could be "healthy" while the app wasn’t serving HTTP.

**What we did:** In `docker-compose.yml`:

- **Arango:** Healthcheck now calls `/_api/version` with `root:$ARANGO_ROOT_PASSWORD` (wget) so "healthy" implies HTTP + auth OK.
- **Experience:** Healthcheck now uses `curl -f http://localhost:8001/health` (same idea as runtime `/health`).

**Recommended order when fixing the three broken critical paths:**

1. **Container health checks (this)** — So we trust `docker-compose ps` and "healthy" before debugging auth or upload.
2. **Auth → session** — Easiest path to get one end-to-end flow working and validate the stack.
3. **File upload → parse → artifact** — Most complex; tackle after health checks and auth are solid.
4. **Control Tower** — Can be fixed in parallel or after auth (e.g. journey/action naming: `get_stats` vs `stats`).

**Probing health checks (don’t just wait for “healthy”):** After bringing the stack up, run the health-check probe from the host so we verify the same contract the container healthchecks enforce (HTTP + auth for Arango, GET /health for runtime and experience, etc.):

```bash
# From repo root; ensure .env.secrets (and config/development.env) are loaded for ARANGO_ROOT_PASSWORD, ports
python scripts/probe_health_checks.py
```

The script exits 0 only if all probes pass (Redis ping, Arango `/_api/version` with auth, Consul leader, Meilisearch /health, Runtime /health, Experience /health). Run it after `docker-compose up -d` and once all services show healthy; if the probe fails, the health checks or env are wrong, not just slow.

**Experience service and auth → session (unblocked):** The Experience container was previously running `runtime_main.py` (no separate entrypoint) and never set `app.state.security_guard_sdk` / `traffic_cop_sdk`, so `/api/auth/login` and `/api/session/*` would fail with "SDK not initialized." We added:

1. **`experience_main.py`** — Entry point that loads config, runs pre-boot, builds the runtime object graph, creates SecurityGuardSDK and TrafficCopSDK from Public Works abstractions, attaches them to the Experience app, and runs uvicorn on EXPERIENCE_PORT (8001).
2. **docker-compose** — Experience service uses `command: ["python3", "experience_main.py"]` and fixed container-network env (REDIS_URL=redis://redis:6379, etc.) so pre-boot passes inside the container.
3. **Bootstrap** — `acquire_env()` now uses `load_dotenv(..., override=False)` so process env (Docker Compose) wins over `.env.secrets` in the image; Experience no longer connects to localhost when run in compose.

After rebuilding and restarting Experience, all health-check probes pass. Next: exercise **auth → session** (e.g. `POST /api/auth/login` or `POST /api/session/create-anonymous`) with valid Supabase config to confirm the full path.
