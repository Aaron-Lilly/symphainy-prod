# Hybrid Cloud Vision: Option C and Three Planes

**Purpose:** Single, clean reference for the platform’s hybrid cloud north star and how it evolves. Aligns with the [Platform Contract](architecture/PLATFORM_CONTRACT.md) and the three-plane mental model.

**Status:** Canonical vision. Use this doc for “where we’re going” and “how deployment evolves.”

**Principle:** Option C (Fully Hosted) is the target. We get there by: (1) stable VM with contract and bootstrap, then (2) swap each backing service to its managed equivalent. Bootstrap respects the three planes regardless of where those services run.

---

## 1. North Star: Option C (Fully Hosted “Everything as a Service”)

**Target:** Push all infrastructure to managed SaaS (or managed-equivalent) so we get almost zero DevOps and fast go-to-market. Trade-off: less ideal if we later need to host regulated or proprietary data entirely on our own infra.

**What we’ve built is compatible with Option C.** The platform contract defines *what* the platform requires (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB, etc.). Option C defines *where* those run: managed services. Same code; we swap URLs and credentials.

---

## 2. Option C: Extended Mapping (Aligned with Platform Contract)

The original Option C table did not mention Consul, GCS, or DuckDB. Our contract requires them. This is the **extended** Option C mapping so the vision matches what we actually need.

| Required by contract | Option C (managed) target | Notes |
|----------------------|---------------------------|--------|
| **Redis** | Upstash / GCP MemoryStore | Hot state, WAL, events, cache. |
| **ArangoDB** | ArangoDB Oasis | Durable state, graph, semantic data. |
| **Consul** | Managed service discovery or self-hosted Consul | Contract requires service discovery. Option C: use managed discovery (e.g. GCP/Cloud Run discovery) or run Consul in a small control plane (e.g. GKE). |
| **Supabase** | Supabase Cloud | Registry, auth, tenant, file metadata. |
| **GCS** | GCP Cloud Storage (or S3) | Blob storage for files and artifacts. Option C doc didn’t list it; we need it. Supabase has storage; for scale/durability we use GCS. |
| **Meilisearch** | **Default:** containerized (docker-compose `meilisearch`). **Option C:** Meilisearch Cloud. | Full-text and metadata search. |
| **DuckDB** | Persistent volume (e.g. GKE PVC) or managed analytical store | Deterministic embeddings. No mainstream “DuckDB as a Service”; Option C = DuckDB on a volume, or later migrate to BigQuery/Snowflake etc. for that workload. |
| **Telemetry** | Grafana Cloud (OTel/Tempo) or GCP Operations | Observability. |
| **LLM / Embeddings** | Hugging Face Inference API / OpenAI / Anthropic / Replicate | Agents and semantic embeddings. |

**Summary:** Option C remains the north star. We explicitly add **Consul** (or managed equivalent), **GCS**, and **DuckDB** (volume or managed analytical) so the vision matches the platform contract.

---

## 3. Three Planes and Bootstrap

**Mental model:** The platform is split into three planes. Bootstrap that “respects” them means we validate in order: **Data Plane first**, then **Control Plane** (if any), then start **Execution Plane**. We do not start execution until the data plane is reachable and authorized.

| Plane | What it is | Option C (where it lives) |
|-------|------------|----------------------------|
| **Data Plane** | Redis, Arango, Supabase, GCS, Meilisearch, DuckDB — persistent state and storage. | Managed services (Oasis, MemoryStore, Supabase Cloud, GCS, Meilisearch Cloud) + DuckDB on volume or managed analytical. |
| **Control Plane** | Service discovery (Consul), governance, configuration, Curator, DI. | Managed discovery or Consul in GKE; telemetry in Grafana Cloud or GCP. |
| **Execution Plane** | Runtime, Realms, APIs, agents, frontend. | Today: single runtime process (VM or container). Later: can split to Cloud Run / GKE Deployments. |

**Bootstrap order:** Before we build the object graph or start the server:

1. **Validate Data Plane:** Connect to Redis, Arango, Supabase, GCS, Meilisearch, DuckDB (per contract). If any check fails, exit with a clear error. No partial init.
2. **Validate Control Plane:** If we use Consul (or equivalent), validate it is reachable. Same: fail fast.
3. **Start Execution:** Only then call `create_runtime_services()` and start uvicorn.

This order is the same whether the data plane is self-hosted on a VM or fully managed (Option C). Option C only changes *where* the services run; we still validate them before starting.

---

## 4. Phased Evolution (Recommended)

| Phase | Goal | What we do |
|-------|------|------------|
| **Phase 0: Stable VM** | One canonical stack that boots and serves the first request. | Implement platform contract: pre-boot validation, one config source, all required infra (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB) present and validated. Bootstrap respects three planes (Data → Control → Execution). Single runtime process on VM. |
| **Phase 1: Option C data plane** | Swap backing services to managed. | Keep the same runtime and code. Point Redis → MemoryStore, Arango → Oasis, Supabase → Cloud, GCS → Cloud Storage, Meilisearch → Cloud. Consul: managed discovery or small Consul in GKE. DuckDB: keep on volume or migrate to managed analytical. No change to execution shape yet. |
| **Phase 2 (optional): Split execution** | Scale execution independently. | Split runtime/realms/APIs to Cloud Run or GKE Deployments. Data and control remain as in Phase 1. |

**CTO sequence:** “We could do Option C as soon as we were able to deploy a stable version in our VM.” So: **Phase 0 first** (stable VM with contract and bootstrap), **then Phase 1** (Option C data plane). Phase 2 is a later optimization.

---

## 5. What “Option C” Does and Doesn’t Mean

- **Does mean:** Data plane (and where appropriate, control plane) use managed services. We don’t run our own Redis/Arango/Meilisearch; we use Oasis, MemoryStore, Supabase Cloud, Meilisearch Cloud, GCS. Consul or equivalent is explicit; DuckDB on volume or managed analytical is explicit.
- **Does mean:** Bootstrap still validates Data Plane (and Control) before starting Execution. Same contract, same pre-boot, whether infra is self-hosted or managed.
- **Does not mean:** We must split the runtime into many services before we can say “Option C.” Option C can be “single runtime process talking to managed Redis, Arango, etc.” Splitting execution (Phase 2) is an optional next step.

---

## 6. References

- [Platform Contract](architecture/PLATFORM_CONTRACT.md) — required infra, config, pre-boot, and solution/journey/intent requirements. Option C is the *deployment target* for that contract.
- [Path to Working Platform](testing/PATH_TO_WORKING_PLATFORM.md) — roadmap (pre-boot → boot → first request → critical path). Phase 0 of this vision.
- [Platform Inventory](testing/PLATFORM_INVENTORY.md) — what’s in the platform; contract is source of truth for “required.”
- Original strategy (for context): `symphainy_source/docs/hybridcloudstrategy.md` — Option C and three planes; this doc is the **updated, canonical** vision for the coexistence fabric.
