# Infrastructure Gap Analysis for Team A

**Status:** Living Document (January 2026)
**Purpose:** Help Team A understand what infrastructure Team B's services expect
**Audience:** Team A (Infrastructure/Takeoff)

---

## Overview

Team B has built 53 capability services. Of these:
- **16 (30%)** have real implementation logic
- **22 (42%)** are mixed (real logic + infrastructure delegation)
- **15 (28%)** are parlor tricks (agent wrappers with placeholders)

For Team B's services to become REAL, Team A needs to implement specific infrastructure.

---

## Infrastructure Dependency Map

### Layer 1: Public Works Abstractions (Critical)

These are called via `ctx.platform.xxx()`:

| Abstraction | Used By | Current State | Required For |
|-------------|---------|---------------|--------------|
| `ingestion_abstraction` | IngestFileService | Unknown | File upload to work |
| `file_storage_abstraction` | Multiple | Unknown | File persistence |
| `artifact_storage_abstraction` | Multiple | Unknown | Artifact storage |
| `registry_abstraction` | Multiple | Unknown | Artifact discovery |
| `parsing_abstraction` (CSV, PDF, etc.) | ParseContentService | Unknown | File parsing |
| `deterministic_compute_abstraction` | CreateDeterministicEmbeddingsService | Unknown | DuckDB embeddings |
| `semantic_data_abstraction` | Semantic operations | Unknown | Arango semantic storage |
| `visual_generation_abstraction` | Visualization services | Unknown | Chart generation |

**Gap Discovery Approach:**
```python
# Team A can run this to check what's actually wired:
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService

pw = PublicWorksFoundationService(config={})
await pw.initialize()

# Check each abstraction
print(f"Ingestion: {pw.ingestion_abstraction is not None}")
print(f"File Storage: {pw.file_storage_abstraction is not None}")
# ... etc
```

---

### Layer 2: State Surface (Critical)

Called via `ctx.state_surface.xxx()`:

| Method | Used By | Purpose |
|--------|---------|---------|
| `artifact_registry.register_artifact()` | IngestFileService | Register new artifacts |
| `artifact_registry.add_materialization()` | IngestFileService | Add storage locations |
| `get_file_metadata()` | ArchiveFileService, etc. | Retrieve file info |
| `store_file_reference()` | Multiple | Update file state |
| `set_state()` / `get_state()` | Session services | Key-value state |

**Gap Discovery:**
- Does StateSurface actually connect to Redis?
- Does ArtifactRegistry actually connect to ArangoDB?
- What happens when these are called?

---

### Layer 3: Civic Systems / Smart City (Critical)

Called via `ctx.governance.xxx`:

| SDK | Used By | Purpose |
|-----|---------|---------|
| `auth` (SecurityGuardSDK) | All security services | Authentication |
| `data_steward` (DataStewardSDK) | Boundary contracts | Data governance |
| `registry` (CuratorSDK) | Artifact indexing | Discovery |
| `telemetry` (NurseSDK) | All services | Observability |
| `sessions` (TrafficCopSDK) | Session services | Session management |

**Gap Discovery:**
- Are these SDKs actually instantiated?
- Do they connect to real backends (Supabase, Redis, etc.)?

---

### Layer 4: Reasoning / Agents (High Priority)

Called via `ctx.reasoning.xxx`:

| Component | Used By | Purpose |
|-----------|---------|---------|
| `llm.complete()` | AI-enhanced services | LLM completion |
| `llm.embed()` | Embedding services | Text embeddings |
| `agents.invoke()` | 15+ services | Agent execution |
| `agents.get()` | Agent lookup | Get agent instance |

**Current State (from audit):**
- 7/20 agents can instantiate
- 13/20 have `__init__` signature issues
- 7 instantiated agents missing `process/execute/run` methods
- LLM adapter connectivity unknown

**Gap Discovery:**
```python
# Check if OpenAI adapter is actually configured:
from symphainy_platform.civic_systems.platform_sdk.services.reasoning_service import ReasoningService

rs = ReasoningService(public_works=None)
print(f"OpenAI adapter: {rs.llm._openai_adapter is not None}")
```

---

## Suggested Gap Discovery Approach

### Phase 1: Connectivity Probes

Create simple tests that check if infrastructure is reachable:

```python
# infrastructure_probes.py

async def probe_redis():
    """Can we connect to Redis?"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        return {"redis": "connected"}
    except Exception as e:
        return {"redis": f"failed: {e}"}

async def probe_arango():
    """Can we connect to ArangoDB?"""
    try:
        import requests
        resp = requests.get("http://localhost:8529/_api/version", 
                           auth=("root", "password"), timeout=5)
        return {"arango": "connected" if resp.status_code == 200 else "failed"}
    except Exception as e:
        return {"arango": f"failed: {e}"}

async def probe_openai():
    """Is OpenAI configured?"""
    import os
    key = os.environ.get("OPENAI_API_KEY")
    return {"openai": "configured" if key else "missing OPENAI_API_KEY"}
```

### Phase 2: Abstraction Probes

Check if Public Works abstractions are wired:

```python
# abstraction_probes.py

async def probe_abstractions(public_works):
    """Check which abstractions are actually available."""
    probes = {
        "ingestion": public_works.ingestion_abstraction,
        "file_storage": public_works.file_storage_abstraction,
        "artifact_storage": public_works.artifact_storage_abstraction,
        "registry": public_works.registry_abstraction,
        "deterministic_compute": public_works.deterministic_compute_abstraction,
        "semantic_data": public_works.semantic_data_abstraction,
    }
    
    results = {}
    for name, abstraction in probes.items():
        results[name] = "wired" if abstraction is not None else "NOT WIRED"
    
    return results
```

### Phase 3: End-to-End Probes

Test actual functionality (requires infrastructure running):

```python
# e2e_probes.py

async def probe_file_upload(runtime_services):
    """Can we actually upload a file end-to-end?"""
    try:
        # Submit ingest_file intent
        intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="probe_tenant",
            session_id="probe_session",
            solution_id="probe_solution",
            parameters={
                "ui_name": "probe_test.txt",
                "file_content": "48656c6c6f".encode().hex(),  # "Hello"
                "file_type": "text",
                "ingestion_type": "upload"
            }
        )
        
        result = await runtime_services.execution_lifecycle_manager.execute(intent)
        
        if result.get("artifacts", {}).get("artifact"):
            return {"file_upload": "WORKS"}
        else:
            return {"file_upload": f"failed: no artifact returned"}
            
    except Exception as e:
        return {"file_upload": f"failed: {e}"}
```

---

## Infrastructure Dependency Matrix

| Team B Service | Requires Working | Priority |
|----------------|------------------|----------|
| `IngestFileService` | ingestion_abstraction, file_storage, artifact_registry | CRITICAL |
| `ParseContentService` | parsing_abstractions, file_storage | CRITICAL |
| `AuthenticateUserService` | auth_abstraction (Supabase) | CRITICAL |
| `AssessDataQualityService` | parsed file retrieval | HIGH |
| `GenerateSOPService` | LLM adapter, SOP agent | MEDIUM |
| `GenerateRoadmapService` | LLM adapter, Roadmap agent | MEDIUM |

---

## What "Done" Looks Like

### For Team A

Infrastructure is "done" when these probes pass:

```
✅ Redis connectivity probe: connected
✅ ArangoDB connectivity probe: connected
✅ Supabase connectivity probe: connected
✅ GCS/Storage connectivity probe: connected
✅ OpenAI API probe: configured

✅ Public Works Abstractions:
   - ingestion_abstraction: wired
   - file_storage_abstraction: wired
   - artifact_storage_abstraction: wired
   - registry_abstraction: wired
   - auth_abstraction: wired

✅ State Surface:
   - artifact_registry.register_artifact(): works
   - state.set_state() / get_state(): works

✅ Reasoning:
   - llm.complete(): works
   - agents.invoke("guide_agent"): works
```

### For Team B

Capability services are "done" when:

1. **No parlor tricks** - All 15 parlor trick services either:
   - Have real implementation, OR
   - Are clearly marked as "requires infrastructure" and don't claim to work

2. **Honest code** - Comments say what actually happens:
   ```python
   # ❌ BAD: "Uses REAL AI"
   # ✅ GOOD: "Attempts AI, falls back to template if unavailable"
   ```

3. **Clean architecture** - All services have:
   - `intent_type` class attribute
   - Consistent `__init__` signatures
   - Clear dependency declarations

---

## Collaboration Model

### Team A Provides → Team B Consumes

```
Team A (Infrastructure)          Team B (Capabilities)
─────────────────────           ─────────────────────
Public Works Abstractions   →   ctx.platform.xxx()
State Surface               →   ctx.state_surface.xxx()
Civic Systems SDKs          →   ctx.governance.xxx()
LLM Adapters                →   ctx.reasoning.llm.xxx()
Agent Framework             →   ctx.reasoning.agents.xxx()
```

### Feedback Loop

When Team B finds a gap:
1. Document it in this file
2. Create a minimal repro / probe test
3. Team A implements the infrastructure
4. Team B verifies via probe test
5. Mark as resolved

---

## Current Known Gaps

| Gap ID | Description | Blocking | Status |
|--------|-------------|----------|--------|
| GAP-001 | 13 agents have `__init__` signature mismatch | Agent invocation | OPEN |
| GAP-002 | 7 agents missing process/execute/run method | Agent invocation | OPEN |
| GAP-003 | 47 services missing intent_type class attr | Clean architecture | OPEN |
| GAP-004 | LLM adapter connectivity unknown | AI features | NEEDS PROBE |
| GAP-005 | Storage abstraction connectivity unknown | File upload | NEEDS PROBE |
| GAP-006 | Auth abstraction connectivity unknown | Security features | NEEDS PROBE |

---

## Next Steps

1. **Team A:** Run connectivity probes, report results
2. **Team B:** Fix GAP-001, GAP-002, GAP-003 (architecture cleanup)
3. **Both:** Run abstraction probes, identify what's not wired
4. **Both:** Run E2E probes, identify what doesn't work end-to-end
