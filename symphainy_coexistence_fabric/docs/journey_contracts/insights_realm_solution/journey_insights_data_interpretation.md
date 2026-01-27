# Journey Contract: Data Interpretation & Discovery

**Journey:** Data Interpretation & Discovery  
**Journey ID:** `journey_insights_data_interpretation`  
**Solution:** Insights Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey

---

## 1. Journey Overview

### Intents in Journey
1. **`interpret_data_self_discovery`** - Unguided semantic discovery
   - Discovers entities, relationships, and patterns
   - Uses chunk-based embedding queries
   - Promotes to Record of Fact

2. **`interpret_data_guided`** - Guided interpretation with guide
   - Matches data against pre-defined guide
   - Higher precision than self-discovery
   - Promotes to Record of Fact

### Journey Flow
```
[User requests data interpretation]
    ↓
[Choose interpretation mode]
    ├── Self-discovery (no guide)
    │   ↓
    │   [interpret_data_self_discovery intent]
    │   ↓
    │   [SemanticSelfDiscoveryService.discover_semantics()]
    │
    └── Guided (with guide)
        ↓
        [interpret_data_guided intent]
        ↓
        [GuidedDiscoveryService.interpret_with_guide()]
    ↓
[Track interpretation in Supabase]
    ↓
[Promote to Record of Fact via Data Steward SDK]
    ↓
[Return interpretation artifact]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts

#### Self-Discovery

| Artifact | Type | Description |
|----------|------|-------------|
| `discovery` | object | Self-discovery interpretation |
| `discovery.interpretation_type` | string | "self_discovery" |
| `discovery.entities` | array | Discovered entities |
| `discovery.relationships` | array | Discovered relationships |
| `discovery.patterns` | array | Identified patterns |
| `discovery.confidence_score` | float | Discovery confidence |
| `discovery.coverage_score` | float | Data coverage |

#### Guided Interpretation

| Artifact | Type | Description |
|----------|------|-------------|
| `interpretation` | object | Guided interpretation |
| `interpretation.interpretation_type` | string | "guided" |
| `interpretation.guide_id` | string | Guide used |
| `interpretation.entities` | array | Matched entities |
| `interpretation.relationships` | array | Matched relationships |
| `interpretation.confidence_score` | float | Match confidence |
| `interpretation.coverage_score` | float | Guide coverage |

### Artifact Lifecycle State Transitions

| State | Transition | Description |
|-------|------------|-------------|
| CREATED | → | Interpretation created |
| PROMOTED | → | Promoted to Record of Fact |

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `interpret_data_self_discovery` | `hash(parsed_file_id + tenant_id)` | Same file = same discovery |
| `interpret_data_guided` | `hash(parsed_file_id + guide_id + tenant_id)` | Same file + guide = same interpretation |

### Journey Completion Definition

**Journey is considered complete when:**

* Interpretation artifact returned
* Interpretation tracked in Supabase
* Interpretation promoted to Record of Fact

---

## 2. Scenario 1: Self-Discovery Happy Path

### Test Description
Self-discovery interpretation completes successfully.

### Steps
1. [x] User has a parsed file with embeddings
2. [x] User triggers `interpret_data_self_discovery`
3. [x] SemanticSelfDiscoveryService discovers semantics
4. [x] Interpretation tracked in Supabase
5. [x] Interpretation promoted to Record of Fact
6. [x] Discovery artifact returned

### Verification
- [x] `discovery` artifact returned
- [x] `discovery.entities` non-empty
- [x] `discovery.confidence_score` > 0
- [x] Interpretation tracked in `interpretations` table
- [x] Record of Fact created

---

## 3. Scenario 2: Guided Interpretation Happy Path

### Test Description
Guided interpretation with guide completes successfully.

### Steps
1. [x] User has a parsed file and a guide_id
2. [x] User triggers `interpret_data_guided`
3. [x] GuidedDiscoveryService matches against guide
4. [x] Interpretation tracked in Supabase
5. [x] Interpretation promoted to Record of Fact
6. [x] Interpretation artifact returned

### Verification
- [x] `interpretation` artifact returned
- [x] `interpretation.guide_id` matches input
- [x] `interpretation.entities` show matched fields
- [x] Record of Fact created

---

## 4. Scenario 3: Missing Guide Error

### Test Description
Guided interpretation fails gracefully when guide_id missing.

### Steps
1. [x] User triggers `interpret_data_guided` without guide_id
2. [x] Validation error raised
3. [x] Error message: "guide_id is required for interpret_data_guided intent"

### Verification
- [x] ValueError raised
- [x] Clear error message
- [x] No partial state created

---

## 5. Integration Points

### Platform Services
- **Insights Realm:** SemanticSelfDiscoveryService, GuidedDiscoveryService
- **Content Realm:** DeterministicChunkingService, FileParserService
- **Public Works:** SemanticDataAbstraction, RegistryAbstraction
- **Data Steward SDK:** Record of Fact promotion

### Backend Handler
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_self_discovery`
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_guided_discovery`

### Frontend API
`symphainy-frontend/shared/managers/InsightsAPIManager.ts::interpretDataSelfDiscovery()`
`symphainy-frontend/shared/managers/InsightsAPIManager.ts::interpretDataGuided()`

---

## 6. Chunk-Based Embedding Pattern

The interpretation handlers use chunk-based embedding queries (Phase 3):

```python
# 1. Get parsed file
parsed_file = await file_parser_service.get_parsed_file(...)

# 2. Create deterministic chunks
chunks = await deterministic_chunking_service.create_chunks(...)

# 3. Query embeddings by chunk_id (not parsed_file_id)
chunk_ids = [chunk.chunk_id for chunk in chunks]
embeddings = await semantic_data.get_semantic_embeddings(
    filter_conditions={"chunk_id": {"$in": chunk_ids}}
)
```

---

## 7. Gate Status

**Journey is "done" only when:**
- [x] ✅ Self-discovery happy path works
- [x] ✅ Guided interpretation happy path works
- [x] ✅ Missing guide error handled
- [x] ✅ Lineage tracking works
- [x] ✅ Record of Fact promotion works

**Current Status:** ✅ **IMPLEMENTED**

---

## 8. Related Documents

- **Intent Contract (Self-Discovery):** `docs/intent_contracts/insights_data_interpretation/intent_interpret_data_self_discovery.md`
- **Intent Contract (Guided):** `docs/intent_contracts/insights_data_interpretation/intent_interpret_data_guided.md`
- **Analysis:** `docs/intent_contracts/INSIGHTS_REALM_ANALYSIS.md`

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team
