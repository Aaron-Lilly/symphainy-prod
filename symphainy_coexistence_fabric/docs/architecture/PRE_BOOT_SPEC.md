# Pre-Boot Spec (Gate G3 Entry)

**Purpose:** Define what Gate G3 checks so we never enter Φ3 (Operational Reality) with missing or unreachable backing services. Pre-boot is the enforcement of G3 **before** `create_runtime_services()`.

**Status:** Canonical. Implementation must conform to this spec.

**References:**
- [genesis_protocol.md](../genesis_protocol.md) — Gate G3 (Enter Φ3)
- [FOUNDATION_PLAN.md](../FOUNDATION_PLAN.md) Step 3
- [PLATFORM_CONTRACT.md](PLATFORM_CONTRACT.md) — §3 (required infra), §5 (pre-boot validation)
- [CONFIG_CONTRACT_SPEC.md](CONFIG_CONTRACT_SPEC.md) — canonical config shape (pre-boot input)
- [HYBRID_CLOUD_VISION.md](../HYBRID_CLOUD_VISION.md) — Data → Control → Execution order

---

## 1. Scope

Pre-boot validates **exactly** the seven backing services required by PLATFORM_CONTRACT §3:

| Service | Purpose (per contract) |
|---------|------------------------|
| **Redis** | Hot state, WAL, events, tenant/cache |
| **ArangoDB** | Durable state, semantic data, graph/knowledge |
| **Consul** | Service discovery (control-plane coordination) |
| **Supabase** | Registry, auth, tenant, file metadata |
| **GCS** | Blob storage (file/artifact bytes) |
| **Meilisearch** | Full-text and metadata search |
| **DuckDB** | Deterministic compute, deterministic embeddings |

**Out of scope for G3:** LLM endpoints, OCR/Cobrix containers, EDI config, and other “required when an intent runs” or Φ4/Φ5 capabilities. Blocking Φ3 on those would create an operational nightmare; see STEP0 §6 and PLATFORM_CONTRACT §9.

---

## 2. Input

- Pre-boot uses **only** the **canonical config** (output of the config contract). See [CONFIG_CONTRACT_SPEC.md](CONFIG_CONTRACT_SPEC.md) for shape and keys.
- **No** `os.getenv()` or env file reads inside pre-boot. All values come from the single config dict passed in.
- **Placement:** Pre-boot runs in the process entry path (e.g. `runtime_main.main()`) **after** canonical config is built and **before** `create_runtime_services(config)`.

---

## 3. Check Order

Order follows [HYBRID_CLOUD_VISION.md](../HYBRID_CLOUD_VISION.md): **Data Plane first**, then **Control Plane**.

1. **Data Plane** (persistent state and storage):  
   Redis → ArangoDB → Supabase → GCS → Meilisearch → DuckDB  
2. **Control Plane:**  
   Consul  

This order is the same whether infra is self-hosted or managed (Option C). Option C only changes *where* services run; we still validate them in this order before starting the execution plane.

---

## 4. Per-Service Checks

Each check is minimal: connect and/or one lightweight operation. No Public Works or adapters; use minimal clients (redis, arango, consul, httpx, google.cloud.storage, duckdb) only.

| Service | Check | Config keys used | Success criterion |
|---------|--------|-------------------|--------------------|
| **Redis** | Connect, ping | `config["redis"]` (host, port, db, password) | `ping()` succeeds |
| **ArangoDB** | Connect, authorize | `arango_url`, `arango_username`, `arango_password`, `arango_database` | `db.version()` succeeds (no 401) |
| **Supabase** | Reachable, auth | `supabase_url`, `supabase_service_key` | GET `{url}/rest/v1/` with service key returns non-401/403 |
| **GCS** | Bucket exists, credentials valid | `gcs_project_id`, `gcs_bucket_name`, `gcs_credentials_json` | `bucket.reload()` or equivalent succeeds |
| **Meilisearch** | Reachable | `meilisearch_host`, `meilisearch_port`, `meilisearch_key` | GET `http://{host}:{port}/health` returns non-5xx |
| **DuckDB** | DB path writable/readable | `config["duckdb"]` (database_path, read_only) | Connect and `SELECT 1` succeeds; if read_only, file must exist |
| **Consul** | Reachable | `config["consul"]` (host, port, token) | e.g. `agent.self()` or equivalent API succeeds |

**Timeouts:** Use short timeouts (e.g. 5–10 seconds) per check so boot fails fast.

---

## 5. Failure Semantics

- **On first failure:** Exit the process immediately. Do **not** continue to the next check.
- **Message format:** Single, clear, actionable line, e.g.  
  `"Platform contract violation: [SERVICE] failed: [reason]. [Hint]."`
- **Hint:** Point to the env/config key and remediation (e.g. "Check REDIS_URL and that Redis is reachable.").
- **No partial init:** We do not call `create_runtime_services()` if any check fails. Gate G3 is not satisfied; we do not enter Φ3.

---

## 6. Success

- If **all** seven checks pass, pre-boot returns (or completes without exiting). The caller then proceeds to `create_runtime_services(config)`.
- Gate G3 (Enter Φ3) is satisfied only after pre-boot passes. This is the mechanical definition of “Public Works connects to backing services” for the purpose of the Genesis Protocol.

---

## 7. Contract Summary

| Item | Rule |
|------|------|
| **Scope** | Seven backing services only (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB). |
| **Input** | Canonical config only; no env reads in pre-boot. |
| **Order** | Data plane (Redis, Arango, Supabase, GCS, Meilisearch, DuckDB) then Consul. |
| **Failure** | First failure → exit process with one clear message; no partial init. |
| **Placement** | After config build, before `create_runtime_services()`. |

Implementations (e.g. `symphainy_platform/bootstrap/pre_boot.py`) must conform to this spec. Existing code may need to reorder checks to match §3 (Data Plane then Consul) and to guarantee no env reads (config only).
