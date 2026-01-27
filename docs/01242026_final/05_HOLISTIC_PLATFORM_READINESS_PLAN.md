# Holistic Platform Readiness Plan

**Date:** January 24, 2026  
**Status:** ✅ **COMPREHENSIVE IMPLEMENTATION PLAN**  
**Purpose:** Get platform to 100% readiness with foundation-first approach, minimizing rework

---

## Executive Summary

This plan organizes all known fixes, migrations, and implementations into a **prioritized, dependency-aware sequence** that ensures we build on solid foundations and minimize rework.

**Key Principles:**
1. **Foundation First** - Fix infrastructure before building features
2. **Dependency Aware** - Fix dependencies before dependents
3. **Working Code Only** - No placeholders, mocks, or cheats
4. **Test as We Go** - Validate each phase before proceeding
5. **Minimize Rework** - Do it right the first time

**Total Estimated Time:** 40-60 hours  
**Phases:** 6 phases, 20+ tasks  
**Priority:** HIGH - Blocks production readiness

---

## Phase Overview

| Phase | Focus | Duration | Dependencies | Priority |
|-------|-------|----------|--------------|----------|
| **Phase 0** | Foundation & Infrastructure | 4-6h | None | 🔴 CRITICAL |
| **Phase 1** | Frontend State Management | 8-12h | Phase 0 | 🔴 CRITICAL |
| **Phase 2** | Backend Core Services | 6-8h | Phase 0 | 🔴 CRITICAL |
| **Phase 3** | Realm Integration | 6-8h | Phase 1, 2 | 🟡 HIGH |
| **Phase 4** | Frontend Feature Completion | 8-10h | Phase 1, 3 | 🟡 HIGH |
| **Phase 5** | Data Architecture & Polish | 4-6h | Phase 2, 3 | 🟢 MEDIUM |

---

## Phase 0: Foundation & Infrastructure (4-6 hours)

**Goal:** Ensure all foundational systems are working correctly before building on top

**Why First:** Everything else depends on these foundations. Fixing them first prevents cascading issues.

### Task 0.1: Verify Public Works Abstractions ✅

**Status:** ✅ Already working (from previous fixes)

**Validation:**
- [x] All abstractions accessible as attributes (not methods)
- [x] No `get_X()` method calls on Public Works
- [x] All adapters initialized correctly

**Action:** None needed - already fixed

---

### Task 0.2: Verify Agent 4-Layer Model Compliance ✅

**Status:** ✅ Already working (from previous fixes)

**Validation:**
- [x] All agents implement `_process_with_assembled_prompt()`
- [x] All agents have `get_agent_description()`
- [x] All agents accept `**kwargs` in `__init__`
- [x] Runtime can instantiate all agents

**Action:** None needed - already fixed

---

### Task 0.3: Verify Runtime Startup ✅

**Status:** ✅ Already working (from previous fixes)

**Validation:**
- [x] Runtime container starts without errors
- [x] All realms register successfully
- [x] All services initialize correctly

**Action:** None needed - already fixed

---

### Task 0.5: Verify PlatformStateProvider Sync & Runtime Authority

**Status:** ⚠️ Needs validation

**Location:** `shared/state/PlatformStateProvider.tsx`

**Critical Importance:** This validates "Frontend as Platform Runtime" - frontend must submit to backend authority.

**Sync Mechanism Clarification:**

**Question:** Is sync **pull**, **push**, or **hybrid**?

**Expected Answer:**
- **Primary:** Event-driven push (on critical state transitions)
- **Safety Net:** Pull on 30-second interval (catches missed events)
- **Not:** Polling as primary mechanism

**Validation Checklist:**
- [ ] **Sync Mechanism Clarified:** Team can explain pull vs push vs hybrid
- [ ] **Sync Cadence:** Syncs with Runtime (30-second interval is safety net, not primary)
- [ ] **Event-Driven Updates:** Critical state changes trigger immediate sync
- [ ] **`getRealmState()` Works:** Retrieves state from PlatformStateProvider
- [ ] **`setRealmState()` Persists:** Persists to backend Runtime (not just local state)
- [ ] **State Persists Across Navigation:** State survives pillar navigation
- [ ] **No Context Errors:** All components can access PlatformStateProvider
- [ ] **Runtime Authoritative Overwrite:** If frontend state diverges from Runtime, Runtime wins
- [ ] **Frontend Reconciliation:** Frontend reconciles without user-visible corruption
- [ ] **No Split Brain:** No divergence between frontend and backend state

**Runtime → Frontend Authoritative Overwrite Test (Critical):**

This is the **most important missing check** for "Frontend as Platform Runtime":

**Test Scenario:**
1. Frontend has state: `{ files: [file1, file2] }`
2. Backend Runtime has state: `{ files: [file1, file2, file3] }` (agent added file3)
3. Frontend syncs with Runtime
4. **Expected:** Frontend state becomes `{ files: [file1, file2, file3] }` (Runtime wins)
5. **Not Expected:** Frontend keeps `[file1, file2]` or shows conflict

**Why This Matters:**
- Agents and sagas can modify state concurrently
- Frontend must submit to backend authority
- Without this, "Frontend as Platform Runtime" doesn't work
- This will be exercised once agents and sagas run concurrently

**Action:**
1. **Clarify Sync Mechanism:** Document whether pull, push, or hybrid
2. **Test State Sync:** Verify sync with Runtime works
3. **Test Realm State Get/Set:** Verify `getRealmState()` / `setRealmState()` work
4. **Test State Persistence:** Verify state persists across navigation
5. **Test Context Access:** Verify no context errors
6. **Test Runtime Overwrite:** Create state divergence, verify Runtime wins
7. **Test Reconciliation:** Verify frontend reconciles without corruption
8. **Test No Split Brain:** Verify no divergence between frontend and backend

**Success Criteria:**
- ✅ Sync mechanism explicitly documented (pull/push/hybrid)
- ✅ State syncs correctly with Runtime
- ✅ State persists across navigation
- ✅ No context errors
- ✅ **Runtime authoritative overwrite validated** (critical)
- ✅ Frontend reconciles without corruption
- ✅ No split brain between frontend and backend
- ✅ Team can explain sync mechanism (not "it seems fine")

---

**Phase 0 Success Criteria:**

**Foundation Lock Criteria (All Must Pass):**

- ✅ **Session State Machine Explicit:** All 6 states named, all transitions validated
- ✅ **Session Boundary Enforced:** No session mutation outside boundary
- ✅ **Sync Mechanism Clarified:** Team can explain pull/push/hybrid
- ✅ **Runtime Authoritative Overwrite Validated:** Frontend submits to backend authority
- ✅ **No "It Seems Fine" Answers:** All validations have explicit, testable criteria
- ✅ All foundational systems validated
- ✅ Session lifecycle works correctly
- ✅ State management works correctly
- ✅ No infrastructure errors

**Green-Light Criteria for Phase 1:**

Only proceed to Phase 1 if:
- ✅ Session state machine is explicit (all 6 states, all transitions)
- ✅ Runtime overwrite behavior is validated (critical test passes)
- ✅ No "it seems fine" answers remain (all validations explicit)
- ✅ Team can explain sync mechanism (pull/push/hybrid)
- ✅ Team can name all session states and transitions

**Estimated Time:** 3-4 hours (validation with explicit state machine and overwrite tests)

---

## Phase 1: Frontend State Management Migration (8-12 hours)

**Goal:** Complete migration from GlobalSessionProvider to PlatformStateProvider

**Why Now:** This is the foundation for all frontend features. Must be done before fixing components.

**Dependencies:** Phase 0 (SessionBoundaryProvider and PlatformStateProvider must work)

### Task 1.1: Semantic Audit of GlobalSessionProvider Usage

**Status:** ⚠️ Needs completion

**Critical:** This is NOT just a grep exercise. Must capture semantic usage patterns.

**Action:**
1. **Find all files** using `useGlobalSession()` or `GlobalSessionProvider`
2. **For each file, capture semantic usage:**
   - **What role GlobalSession was playing:**
     - Identity? (session ID, user ID, tenant ID)
     - Realm state? (content, insights, journey, outcomes)
     - Orchestration? (workflow coordination)
     - Convenience cache? (derived values)
   - **What replaces it:**
     - SessionBoundary? (session identity)
     - PlatformState? (realm state)
     - Realm slice? (specific realm state)
     - Derived selector? (computed values)
   - **Migration complexity:**
     - Simple (direct replacement)
     - Medium (requires refactoring)
     - Complex (reveals business logic issues)
3. **Categorize by priority:**
   - **Critical:** MainLayout, GuideAgentProvider, Chat components
   - **High:** Pillar components (content, insights, journey, outcomes)
   - **Medium:** Other UI components
4. **Identify hidden issues:**
   - Cross-realm coupling
   - Business logic in state access
   - Synchronous availability assumptions
   - Shadow session state
   - "Sticky" IDs

**Deliverable:** `docs/01242026_final/MIGRATION_CHECKLIST.md` with semantic usage columns

**Success Criteria:**
- Complete list of all files to migrate (52 files)
- Semantic usage documented for each file
- Old responsibility → New source mapping
- Hidden issues identified
- Prioritized by dependency order
- Migration pattern documented

**Key Principle:** This phase isn't just migration — it's archaeological truth-telling. Finding business logic issues now is a win, not a setback.

---

### Task 1.2: Migrate Core Infrastructure Components

**Priority:** 🔴 CRITICAL - Blocks many other components

**Files:**
1. `shared/components/MainLayout.tsx`
2. `shared/agui/GuideAgentProvider.tsx`
3. `shared/components/chatbot/InteractiveChat.tsx`
4. `shared/components/chatbot/InteractiveSecondaryChat.tsx`

**Migration Pattern:**
```typescript
// BEFORE
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
const { guideSessionToken } = useGlobalSession();

// AFTER
import { useSessionBoundary } from '@/shared/state/SessionBoundaryProvider';
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
const { state: sessionState } = useSessionBoundary();
const sessionId = sessionState.sessionId;
```

**Action:**
1. Update each file following Platform Build Guide Pattern 1
2. **Post-Migration Invariant Check (After Each File):**
   - ✅ No derived state stored locally that duplicates PlatformState
   - ✅ No session-derived values cached in refs or component state
   - ✅ No implicit assumption that `sessionId` never changes
   - ✅ All session/realm identity is *read*, not *remembered*
3. Test after each migration
4. Verify no context errors
5. Verify functionality works

**One-Line Rule for Team:**
> **If it depends on session or realm identity, it must be *read*, not *remembered*.**

**What This Prevents:**
- Shadow session state
- "Sticky" IDs
- Subtle desync bugs that only appear on reconnection
- Components quietly re-introducing state management

**Success Criteria:**
- All core components migrated
- Post-migration invariant checks pass for each file
- No context errors
- Chat components work
- MainLayout renders correctly
- No shadow state or cached session values

---

### Task 1.3: Migrate Pillar Components

**Priority:** 🟡 HIGH - Core functionality

**Files:** ~20 files across content, insights, journey, outcomes pillars

**Migration Order:** Content → Insights → Journey → Outcomes (correct dependency order)

**Migration Pattern:**
```typescript
// BEFORE
const { getPillarState, setPillarState } = useGlobalSession();
const pillarState = getPillarState('content');

// AFTER
const { getRealmState, setRealmState } = usePlatformState();
const realmState = getRealmState('content', 'files');
```

**Action:**
1. Migrate Content pillar components first
2. Migrate Insights pillar components
3. Migrate Journey pillar components
4. Migrate Outcomes pillar components
5. Test after each pillar
6. **Cross-Pillar Navigation Test (After All Pillars Migrated):**
   - Navigate Content → Insights → Content
   - Navigate Insights → Journey → Insights
   - Navigate Journey → Outcomes → Journey
   - Navigate Outcomes → Content → Outcomes
   - **Verify:**
     - ✅ Realm state is preserved across navigation
     - ✅ State does not leak across realms
     - ✅ State correctly rehydrates from Runtime on return
     - ✅ No remounted defaults (state restored from PlatformState)

**Success Criteria:**
- All pillar components migrated
- State persists across pillar navigation
- Cross-pillar navigation test passes
- No state leakage between realms
- State rehydrates correctly from Runtime
- No context errors

**Why This Matters:**
This is where previous refactors likely "felt fine" but weren't actually correct. Navigation between pillars must preserve realm state without leaking or losing state.

---

### Task 1.4: Migrate Remaining Components

**Priority:** 🟢 MEDIUM - Other UI components

**Files:** ~20+ remaining files

**Action:**
1. Migrate remaining components
2. Test after each migration
3. Verify no context errors

**Success Criteria:**
- All components migrated
- No references to GlobalSessionProvider
- All tests pass

---

### Task 1.5: Remove GlobalSessionProvider

**Priority:** 🟢 MEDIUM - Cleanup

**Action:**
1. **CI Guardrail:** Add CI check that fails if `GlobalSessionProvider` is imported anywhere
   - Prevents regression
   - Turns "discipline" into automation
   - Catches accidental re-introduction
2. Delete `shared/agui/GlobalSessionProvider.tsx`
3. Delete old `shared/agui/AppProviders.tsx` (if exists)
4. Remove unused imports
5. Update documentation
6. **Verify CI check passes:** No imports of GlobalSessionProvider found

**CI Check Pattern:**
```bash
# In CI pipeline
if grep -r "GlobalSessionProvider\|useGlobalSession" --include="*.ts" --include="*.tsx" symphainy-frontend/; then
  echo "❌ ERROR: GlobalSessionProvider still imported"
  exit 1
fi
```

**Success Criteria:**
- Old system completely removed
- CI check added and passing
- No broken imports
- Documentation updated
- Zero references to GlobalSessionProvider

**Why This Matters:**
Migration fatigue at ~80% is a historical pattern. CI automation prevents backsliding and turns discipline into automation.

---

**Phase 1 Success Criteria:**

**Foundation Lock Criteria (All Must Pass):**
- ✅ All 52 files migrated (semantic usage documented)
- ✅ No references to GlobalSessionProvider (CI check passes)
- ✅ Post-migration invariant checks pass (no shadow state)
- ✅ Cross-pillar navigation test passes (state preserved, no leakage)
- ✅ All tests pass
- ✅ Session state syncs correctly
- ✅ No context errors
- ✅ No business logic issues hidden (archaeological truth-telling complete)

**Green-Light Criteria for Phase 2:**
Only proceed to Phase 2 if:
- ✅ All 52 files migrated
- ✅ CI check passes (no GlobalSessionProvider imports)
- ✅ Cross-pillar navigation test passes
- ✅ No shadow state or cached session values
- ✅ All business logic issues surfaced and documented

**Estimated Time:** 10-14 hours (includes semantic audit and invariant checks)

**Key Principle:**
> **This phase isn't just migration — it's archaeological truth-telling.**
> Finding business logic issues now is a win, not a setback.

---

## Phase 2: Backend Core Semantic Services (REFINED)

**Goal:** Replace placeholders with *operationally honest* semantic services that support scalable, cost-effective embedding architecture

**Why Now:** These services define semantic truth for all realms. Phase 1 locked frontend to runtime as single source of truth. Phase 2 is the first time backend placeholders will be exercised end-to-end by real UI flows.

**Dependencies:** Phase 0 (foundations must work), Phase 1 (frontend state management complete)

**CTO + CIO Feedback Incorporated:** 
- See `CTO_EMBEDDING_VISION_ANALYSIS.md` for CTO's embedding vision
- See `PLATFORM_ENHANCEMENTS_TO_CTO_VISION.md` for platform enhancements
- See `PHASE_2_REFINED_PLAN.md` for complete refined plan

**Key Principles:**
- **CTO's 5 Principles:** Deterministic before semantic, versioned, trigger-based, chunk-referenced, hydration cheaper than storage
- **CIO's "Land the Plane" Expectations:** Deterministic outputs, no UX concepts, self-describing artifacts, structured meaning, orchestrator truth, first-class failures, contract doc
- **Platform Enhancements:** Intent-driven triggers, Public Works governance, dual-layer deterministic

**Estimated Time:** 10-14 hours (increased due to chunking layer, failure handling, and contract documentation)

### Task 2.0: Implement Deterministic Chunking Layer (NEW - CRITICAL)

**Status:** ❌ Missing - Blocks everything else

**Why First:**
- All semantic work depends on stable chunk identity
- Without this, embeddings will be unstable
- Cannot implement idempotency without chunk IDs

**Location:** `realms/content/enabling_services/deterministic_chunking_service.py`

**Action:**
1. Create `DeterministicChunk` data class
2. Implement chunking based on parser structure (not heuristics)
3. Generate stable chunk IDs (content-addressed or path-derived)
4. Store chunk metadata (index, source_path, text_hash, structural_type)
5. Add chunk lineage tracking (file → page → section → paragraph)
6. Add integration test for chunk stability

**Implementation Pattern:**
```python
@dataclass
class DeterministicChunk:
    chunk_id: str  # Stable, content-addressed
    chunk_index: int
    source_path: str  # file → page → section → paragraph
    text_hash: str  # Normalized hash
    structural_type: str  # page | section | paragraph | table | cell
    byte_offset: Optional[int]
    logical_offset: Optional[int]
    text: str
    metadata: Dict[str, Any]

class DeterministicChunkingService:
    def __init__(self, public_works: PublicWorksFoundationService):
        self.parser_registry = public_works.parser_registry
    
    async def create_chunks(
        self,
        parsed_content: Dict[str, Any],
        file_id: str,
        tenant_id: str
    ) -> List[DeterministicChunk]:
        # Use parser structure, not heuristics
        parser_type = parsed_content.get("parser_type")
        structure = parsed_content.get("structure", {})
        
        chunks = []
        for idx, element in enumerate(self._extract_structural_elements(structure)):
            chunk_id = self._generate_chunk_id(
                file_id=file_id,
                element_path=element["path"],
                text_hash=self._normalize_and_hash(element["text"])
            )
            
            chunks.append(DeterministicChunk(
                chunk_id=chunk_id,
                chunk_index=idx,
                source_path=f"{file_id}:{element['path']}",
                text_hash=self._normalize_and_hash(element["text"]),
                structural_type=element["type"],
                byte_offset=element.get("byte_offset"),
                logical_offset=element.get("logical_offset"),
                text=element["text"],
                metadata={
                    "file_id": file_id,
                    "tenant_id": tenant_id,
                    "parser_type": parser_type
                }
            ))
        
        return chunks
```

**Success Criteria:**
- Chunks are stable (same input → same chunks)
- Chunk IDs are deterministic
- Lineage is tracked
- Integration test validates chunk stability

---

### Task 2.1: Implement EmbeddingService (REFACTORED - Chunk-Based)

**Status:** ❌ Missing - Critical blocker

**Location:** `realms/content/enabling_services/embedding_service.py`

**Current State:**
- ❌ File doesn't exist
- ❌ Referenced in comments but not implemented
- ❌ `_handle_extract_embeddings()` returns placeholder

**Action:**
1. Create `EmbeddingService` class
2. Implement `create_embeddings()` method
3. Integrate with embedding model provider (OpenAI, Cohere, etc.)
4. Use `SemanticDataAbstraction` for storage
5. Update `content_orchestrator._handle_extract_embeddings()` to use service
6. Add integration test

**Implementation Pattern:**
```python
class EmbeddingService:
    def __init__(self, public_works: PublicWorksFoundationService):
        self.semantic_data = public_works.semantic_data_abstraction
        self.llm_adapter = public_works.openai_adapter  # or configured model
    
    async def create_embeddings(
        self,
        parsed_content: Dict[str, Any],
        model_name: str = "text-embedding-ada-002",
        tenant_id: str
    ) -> Dict[str, Any]:
        # Extract text from parsed content
        text = self._extract_text(parsed_content)
        
        # Create embeddings via LLM adapter
        embeddings = await self.llm_adapter.create_embeddings(
            text=text,
            model=model_name
        )
        
        # Store in ArangoDB via SemanticDataAbstraction
        embedding_id = await self.semantic_data.store_embeddings(
            embeddings=embeddings,
            metadata={
                "model": model_name,
                "tenant_id": tenant_id,
                "source": parsed_content.get("file_id")
            }
        )
        
        return {
            "embedding_id": embedding_id,
            "embedding_count": len(embeddings),
            "model_name": model_name
        }
```

**Success Criteria:**
- EmbeddingService works with chunks (not blobs)
- Idempotent (won't re-embed existing chunks)
- Supports multiple semantic profiles
- Stores chunk references, not text blobs
- Integration test validates embeddings exist and are idempotent

---

### Task 2.2: SemanticMeaningAgent → SemanticSignalExtractor (REFACTORED)

**Status:** ❌ Placeholder implementation

**Location:** `realms/content/enabling_services/semantic_signal_extractor.py` (Rename from SemanticMeaningAgent)

**CTO Feedback:** Rename to `SemanticSignalExtractor`. It's a semantic normalizer, not a philosopher.

**Current State:**
```python
async def _process_with_assembled_prompt(...):
    return {
        "artifact_type": "semantic_meaning",
        "artifact": {},
        "confidence": 0.0
    }
```

**Action:**
1. Rename to `SemanticSignalExtractor`
2. Accept chunks (not raw text)
3. Extract structured signals (not prose-first)
4. Reference chunk IDs in output
5. Only fire on explicit triggers (not auto-fire)
6. Test with real data

**CTO-Recommended Pattern:**
```python
class SemanticSignalExtractor(AgentBase):
    """
    Semantic normalizer, not a philosopher.
    Extracts structured semantic signals, normalizes language into shared primitives.
    """
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,
        user_message: str,
        runtime_context: AgentRuntimeContext,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        # Extract chunks from runtime_context (not raw text)
        chunks = runtime_context.get("chunks", [])
        
        if not chunks:
            return {
                "artifact_type": "semantic_signals",
                "artifact": {"error": "No chunks provided"},
                "confidence": 0.0
            }
        
        # Extract structured signals (not prose)
        signals = await self._extract_structured_signals(
            chunks=chunks,
            system_message=system_message,
            context=context
        )
        
        return {
            "artifact_type": "semantic_signals",
            "artifact": {
                "key_concepts": signals.get("concepts", []),
                "inferred_intents": signals.get("intents", []),
                "domain_hints": signals.get("domains", []),
                "entities": {
                    "dates": signals.get("dates", []),
                    "documents": signals.get("documents", []),
                    "people": signals.get("people", []),
                    "organizations": signals.get("organizations", [])
                },
                "ambiguities": signals.get("ambiguities", []),
                "interpretation": signals.get("interpretation", "")  # Optional prose
            },
            "confidence": signals.get("confidence", 0.7),
            "derived_from": [chunk.chunk_id for chunk in chunks]  # Reference deterministic IDs
        }
```

**Trigger Boundary (CRITICAL):**
- ❌ **DO NOT** auto-fire on parse/ingest/upload
- ✅ **DO** fire on:
  - Explicit user intent
  - Downstream agent request
  - Missing semantic signal required for task

**Success Criteria:**
- Returns structured signals (not prose-first)
- References chunk IDs
- Only fires on explicit triggers
- Test validates structured output

---

### Task 2.3: Content Orchestrator - Split Intents (REFACTORED)

**Status:** ❌ Placeholder implementation

**Location:** `realms/content/orchestrators/content_orchestrator.py`

**CTO Feedback:** Split into two intents: `extract_deterministic_structure` and `hydrate_semantic_profile`

**Current State:**
- Single `extract_embeddings` intent
- No separation of deterministic vs semantic
- Returns fake `embedding_id`

**Action:**
1. Create `_handle_extract_deterministic_structure()` intent handler
2. Create `_handle_hydrate_semantic_profile()` intent handler
3. Remove old `_handle_extract_embeddings()` placeholder
4. Update intent routing
5. Add integration tests

**CTO-Recommended Pattern:**
```python
async def _handle_extract_deterministic_structure(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Extract deterministic chunks (no LLM, no embeddings).
    This is the foundation for all semantic work.
    """
    file_id = intent.parameters.get("file_id")
    
    # Get parsed content
    parsed_content = await self._get_parsed_content(file_id, context)
    
    # Create deterministic chunks
    chunks = await self.deterministic_chunking_service.create_chunks(
        parsed_content=parsed_content,
        file_id=file_id,
        tenant_id=context.tenant_id
    )
    
    # Store chunks (idempotent)
    chunk_ids = await self._store_chunks(chunks, context)
    
    return {
        "artifact_type": "deterministic_chunks",
        "artifact": {
            "chunk_count": len(chunks),
            "chunk_ids": chunk_ids,
            "structure": [{
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "source_path": chunk.source_path,
                "structural_type": chunk.structural_type
            } for chunk in chunks]
        },
        "confidence": 1.0  # Deterministic = 100% confidence
    }

async def _handle_hydrate_semantic_profile(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Hydrate semantic embeddings for a specific profile.
    Only fires on explicit trigger (user intent, agent request, missing signal).
    """
    file_id = intent.parameters.get("file_id")
    semantic_profile = intent.parameters.get("semantic_profile", "default")
    model_name = intent.parameters.get("model_name", "text-embedding-ada-002")
    
    # Get deterministic chunks (must exist first)
    chunks = await self._get_deterministic_chunks(file_id, context)
    
    if not chunks:
        return {
            "artifact_type": "error",
            "artifact": {
                "error": "Deterministic chunks not found. Run extract_deterministic_structure first."
            },
            "confidence": 0.0
        }
    
    # Create embeddings (idempotent)
    embedded_chunk_ids = await self.embedding_service.create_embeddings(
        chunks=chunks,
        semantic_profile=semantic_profile,
        model_name=model_name,
        tenant_id=context.tenant_id
    )
    
    # Track in Supabase for lineage
    await self._track_semantic_hydration(
        file_id=file_id,
        semantic_profile=semantic_profile,
        model_name=model_name,
        chunk_ids=embedded_chunk_ids,
        tenant_id=context.tenant_id
    )
    
    return {
        "artifact_type": "semantic_hydration",
        "artifact": {
            "semantic_profile": semantic_profile,
            "model_name": model_name,
            "chunk_count": len(embedded_chunk_ids),
            "chunk_ids": embedded_chunk_ids
        },
        "confidence": 0.9
    }
```

**Success Criteria:**
- Two separate intents implemented
- Deterministic step is LLM-free
- Semantic step is trigger-based
- Integration test validates flow

---

### Task 2.4: Semantic Profile System (NEW)

**Status:** ❌ Missing

**Location:** `realms/content/enabling_services/semantic_profile_registry.py`

**Purpose:** Manage semantic profiles (versioned, scoped semantic interpretations)

**Action:**
1. Create `SemanticProfile` data class
2. Implement `SemanticProfileRegistry`
3. Store profiles in Supabase
4. Reference profiles in all semantic artifacts
5. Add profile management endpoints

**Success Criteria:**
- Profiles can be registered and retrieved
- Profiles are versioned
- All semantic artifacts reference profiles

---

### Task 2.5: Semantic Trigger Boundary (NEW)

**Status:** ❌ Missing

**Location:** `realms/content/enabling_services/semantic_trigger_boundary.py`

**Purpose:** Enforce pull-based semantic computation (prevent over-eager interpretation)

**Action:**
1. Create `SemanticTriggerBoundary` class
2. Define trigger types (explicit_user_intent, downstream_agent_request, missing_semantic_signal)
3. Integrate with Content Orchestrator
4. Add logging for cost tracking

**Success Criteria:**
- SemanticSignalExtractor only fires on explicit triggers
- All semantic computations are logged
- Integration test validates trigger enforcement

---

**Phase 2 Success Criteria:**
- ✅ Deterministic chunking implemented and stable
- ✅ EmbeddingService works with chunks (idempotent, profile-aware)
- ✅ SemanticSignalExtractor returns structured signals
- ✅ Content Orchestrator has separate deterministic/semantic intents
- ✅ Semantic profile system implemented
- ✅ Semantic trigger boundary enforced
- ✅ All integration tests pass
- ✅ Cost tracking shows selective hydration

**Estimated Time:** 8-12 hours (increased due to deterministic chunking layer and refactoring)

---

## Phase 3: Realm Integration (6-8 hours)

**Goal:** Integrate Journey and Insights realms with Artifact Plane

**Why Now:** These are dependencies for Outcomes realm and frontend features.

**Dependencies:** Phase 1 (frontend state), Phase 2 (backend services)

### Task 3.1: Integrate Journey Realm with Artifact Plane

**Status:** ❌ Not integrated

**Location:** `realms/journey/orchestrators/journey_orchestrator.py`

**Current State:**
- ❌ Blueprints stored via `ArtifactStorageProtocol` directly
- ❌ SOPs stored in execution state
- ❌ Workflows stored in execution state
- ❌ No `ArtifactPlane` initialization

**Action:**
1. Initialize `ArtifactPlane` in `JourneyOrchestrator.__init__`
2. Update `_handle_create_blueprint()` to use Artifact Plane
3. Update `_handle_generate_sop()` to use Artifact Plane
4. Update `_handle_create_workflow()` to use Artifact Plane
5. Test blueprint → solution flow

**Implementation Pattern:**
```python
class JourneyOrchestrator:
    def __init__(self, public_works: PublicWorksFoundationService):
        # ... existing initialization
        self.artifact_plane = ArtifactPlane(public_works)
    
    async def _handle_create_blueprint(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        # ... create blueprint logic
        
        # Store in Artifact Plane
        artifact_id = await self.artifact_plane.create_artifact(
            artifact_type="blueprint",
            artifact=blueprint_data,
            owner="client",
            purpose="decision_support",
            lifecycle_state="draft",
            tenant_id=context.tenant_id,
            session_id=context.session_id
        )
        
        return {
            "artifact_type": "blueprint",
            "artifact": {
                "artifact_id": artifact_id,
                "blueprint": blueprint_data
            },
            "confidence": 0.9
        }
```

**Success Criteria:**
- Artifact Plane initialized
- Blueprints stored in Artifact Plane
- SOPs stored in Artifact Plane
- Workflows stored in Artifact Plane
- Blueprint → solution flow works

---

### Task 3.2: Insights Realm Migration (4-6 hours)

**Status:** ❌ **CRITICAL** - All services bypass chunks

**Location:** `realms/insights/orchestrators/insights_orchestrator.py` and all enabling services

**Issues Found:**
- ❌ **All services directly query embeddings by `parsed_file_id`** (bypasses chunks)
- ❌ No semantic signals used
- ❌ Old embedding format (`semantic_meaning` field)
- ❌ No trigger boundaries

**Action:**
1. Update all services to use chunk-based embeddings (query by `chunk_id`, not `parsed_file_id`)
2. Add semantic signal extraction
3. Migrate from old embedding format to chunk-based format
4. Add trigger boundary checks
5. Update: SemanticMatchingService, DataQualityService, DataAnalyzerService, InsightsLiaisonAgent, StructuredExtractionService

**Success Criteria:**
- Artifact Plane initialized
- All insights artifacts in Artifact Plane
- Test files retrieve from Artifact Plane

---

**Phase 3 Success Criteria (Refined):**
- ✅ Content Realm: Legacy intents deprecated, all services use chunk-based pattern
- ✅ Journey Realm: Workflow/SOP files chunked, semantic signals used for analysis
- ✅ Insights Realm: All services use chunk-based embeddings, semantic signals extracted
- ✅ Outcomes Realm: Services verified for chunk usage
- ✅ Artifact Plane: Integrated after realm alignment (Task 3.5)

**Estimated Time:** 12-18 hours (increased due to alignment work)

**See:** `PHASE_2_REALM_AUDIT.md` for detailed audit findings  
**See:** `PHASE_3_REFINED_PLAN.md` for complete implementation plan

---

## Phase 4: Frontend Feature Completion (8-10 hours)

**Goal:** Fix all frontend placeholders and complete incomplete features

**Why Now:** Backend is ready, frontend state is migrated. Can now complete features.

**Dependencies:** Phase 1 (state migration), Phase 3 (realm integration)

### Task 4.1: Fix State Management Placeholders

**Status:** ❌ Placeholders in multiple files

**Files:**
- `components/content/FileUploader.tsx`
- `components/operations/CoexistenceBluprint.tsx`
- `components/insights/VARKInsightsPanel.tsx`

**Current State:**
```typescript
const getPillarState = (pillar: string) => null;
const setPillarState = async (pillar: string, state: any) => {};
```

**Action:**
1. Replace with `usePlatformState()` following Platform Build Guide
2. Test state persistence across pillar navigation

**Success Criteria:**
- All placeholders replaced
- State persists correctly
- No null returns

---

### Task 4.2: Fix Mock User ID

**Status:** ❌ Hardcoded `user_id: "mock-user"`

**Location:** `components/content/FileUploader.tsx`

**Action:**
1. Use `useSessionBoundary()` to get actual user ID
2. Replace all `"mock-user"` with actual user ID
3. Test with authenticated and anonymous sessions

**Success Criteria:**
- No hardcoded user IDs
- Works with authenticated sessions
- Works with anonymous sessions

---

### Task 4.3: Fix File Upload Mock Fallback

**Status:** ❌ Creates mock file when sessionId === null

**Location:** `components/content/FileUploader.tsx`

**Action:**
1. Remove mock file creation code
2. Add proper error handling
3. Show user-friendly error message
4. Test with invalid session

**Success Criteria:**
- No mock file creation
- Proper error handling
- User-friendly error messages

---

### Task 4.4: Implement Business Outcomes Handlers

**Status:** ❌ TODOs in handlers

**Location:** `app/(protected)/pillars/business-outcomes/page.tsx`

**Current State:**
```typescript
const handleCreateBlueprint = async () => { // TODO: Implement ... };
const handleCreatePOC = async () => { // TODO: Implement ... };
const handleGenerateRoadmap = async () => { // TODO: Implement ... };
```

**Action:**
1. Create `useOutcomesAPI` hook (if doesn't exist)
2. Implement `createBlueprint()` handler
3. Implement `createPOC()` handler
4. Implement `generateRoadmap()` handler
5. Implement `exportArtifact()` handler
6. Connect to Outcomes realm endpoints
7. Test end-to-end flow

**Implementation Pattern:**
```typescript
// Create hook
export function useOutcomesAPI() {
  const { state: sessionState } = useSessionBoundary();
  const { submitIntent } = useServiceLayerAPI();
  
  const createPOC = async (params: CreatePOCParams) => {
    return await submitIntent({
      intent_type: "create_poc",
      parameters: params,
      session_id: sessionState.sessionId
    });
  };
  
  return { createPOC, createBlueprint, generateRoadmap, exportArtifact };
}

// Use in component
const { createPOC } = useOutcomesAPI();
const handleCreatePOC = async () => {
  const { data, error } = await createPOC({
    description: "...",
    synthesis: businessOutcomesOutputs?.synthesis
  });
  
  if (error) {
    setError(error.message);
    return;
  }
  
  setArtifacts(prev => ({ ...prev, poc: data }));
};
```

**Backend Endpoints Needed:**
- `POST /api/v1/outcomes/create-blueprint`
- `POST /api/v1/outcomes/create-poc`
- `POST /api/v1/outcomes/generate-roadmap`
- `POST /api/v1/outcomes/export-artifact`

**Success Criteria:**
- All handlers implemented
- Connected to backend
- End-to-end flow works
- No TODOs remaining

---

### Task 4.5: Remove All Direct API Calls

**Status:** ⚠️ Some components may still call APIs directly

**Action:**
1. Find all direct `fetch()` calls to `/api/*`
2. Replace with service layer hooks
3. Test after each replacement

**Success Criteria:**
- No direct API calls
- All calls go through service layer hooks
- All tests pass

---

### Task 4.6: Fix Legacy Endpoint Patterns - Migrate to Intent-Based API

**Status:** ❌ Legacy endpoints found in frontend (endpoints don't exist in backend)

**Issue:** Frontend is calling non-existent legacy endpoints that bypass Runtime/ExecutionLifecycleManager

**Legacy Endpoints Found:**
- `/api/v1/business_enablement/content/upload-file` (Content pillar)
- `/api/v1/content-pillar/upload-file` (Content pillar)
- `/api/v1/insights-solution/*` (Insights pillar)
- `/api/v1/journey/guide-agent/*` (Journey pillar)
- `/api/v1/business-outcomes-solution/*` (Business Outcomes pillar)
- `/api/v1/business-outcomes-pillar/*` (Business Outcomes pillar)

**Files Affected:**
- `symphainy-frontend/app/(protected)/pillars/content/components/ContentPillarUpload.tsx`
- `symphainy-frontend/shared/services/content/file-processing.ts`
- `symphainy-frontend/shared/managers/ContentAPIManager.ts`
- `symphainy-frontend/shared/services/insights/core.ts`
- `symphainy-frontend/shared/managers/GuideAgentAPIManager.ts`
- `symphainy-frontend/shared/managers/BusinessOutcomesAPIManager.ts`
- `symphainy-frontend/shared/services/business-outcomes/solution-service.ts`

**Action:**
1. Replace all legacy endpoint calls with `/api/intent/submit` pattern
2. Use proper intent types (`ingest_file`, `parse_content`, `analyze_data`, etc.)
3. Ensure all operations go through Runtime/ExecutionLifecycleManager
4. Verify boundary contracts are created automatically
5. Test each pillar after migration

**Proper Pattern:**
```typescript
// Instead of:
fetch("/api/v1/business_enablement/content/upload-file", { ... })

// Use:
fetch("/api/intent/submit", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify({
    intent_type: "ingest_file",
    tenant_id: tenantId,
    session_id: sessionId,
    solution_id: solutionId,
    parameters: {
      ingestion_type: "upload",
      file_content: fileContentHex,
      ui_name: fileName,
      file_type: fileType,
      mime_type: mimeType
    }
  })
});
```

**Success Criteria:**
- All legacy endpoints replaced with intent-based API
- All operations go through Runtime/ExecutionLifecycleManager
- Boundary contracts created automatically
- All pillars tested and working

**Reference:** See `LEGACY_ENDPOINT_AUDIT.md` for detailed analysis

---

### Task 4.7: Audit All Pillars for Intent-Based API Alignment

**Status:** ⚠️ Need comprehensive audit

**Goal:** Ensure all pillars (Content, Insights, Journey, Business Outcomes) use intent-based API pattern consistently

**Action:**
1. **Content Pillar Audit:**
   - Verify file upload uses `ingest_file` intent
   - Verify file parsing uses `parse_content` intent
   - Verify chunking uses `extract_deterministic_structure` intent
   - Verify embeddings use `hydrate_semantic_profile` intent

2. **Insights Pillar Audit:**
   - Verify analysis requests use appropriate intents (`analyze_data`, `get_business_summary`, etc.)
   - Check for legacy `/api/v1/insights-solution/*` patterns
   - Ensure all operations go through Runtime

3. **Journey Pillar Audit:**
   - Verify workflow/SOP operations use appropriate intents
   - Check for legacy `/api/v1/journey/*` patterns
   - Ensure coexistence analysis uses proper intent flow

4. **Business Outcomes Pillar Audit:**
   - Verify roadmap generation uses appropriate intents
   - Verify POC proposal uses appropriate intents
   - Check for legacy `/api/v1/business-outcomes-*` patterns
   - Ensure all synthesis operations use proper intent flow

5. **Create Intent Mapping Document:**
   - Document all intent types used by each pillar
   - Map legacy endpoints to new intent types
   - Provide migration guide for each pillar

**Success Criteria:**
- All pillars use intent-based API consistently
- No legacy endpoint patterns remain
- Intent mapping document created
- All operations verified to go through Runtime

**Reference:** See `BOUNDARY_CONTRACT_UI_AUDIT.md` for architecture details

---

**Phase 4 Success Criteria:**
- ✅ All placeholders fixed
- ✅ All mocks removed
- ✅ All TODOs implemented
- ✅ All features work end-to-end
- ✅ No direct API calls
- ✅ All legacy endpoints migrated to intent-based API
- ✅ All pillars use consistent intent-based pattern

**Estimated Time:** 10-12 hours (increased due to legacy endpoint migration and pillar audit)

---

## Phase 5: Data Architecture & Polish (4-6 hours)

**Goal:** Complete four-class data architecture and polish

**Why Last:** These are refinements, not blockers. Can be done after core functionality works.

**Dependencies:** Phase 2 (backend services), Phase 3 (realm integration)

### Task 5.1: Implement TTL Enforcement for Working Materials

**Status:** ⚠️ TTL tracked but not enforced

**Action:**
1. Create automated purge job
2. Enforce TTL based on boundary contracts
3. Test purge automation

**Success Criteria:**
- TTL enforced automatically
- Working Materials purged when expired
- Tests validate purge behavior

---

### Task 5.2: Complete Records of Fact Promotion

**Status:** ⚠️ Partially implemented

**Action:**
1. Ensure all embeddings stored as Records of Fact
2. Ensure all interpretations stored as Records of Fact
3. Test promotion workflow

**Success Criteria:**
- All Records of Fact properly stored
- Promotion workflow works
- Tests validate persistence

---

### Task 5.3: Complete Purpose-Bound Outcomes Lifecycle

**Status:** ⚠️ Partially implemented

**Action:**
1. Ensure all artifacts have lifecycle states
2. Implement lifecycle state transitions
3. Test lifecycle management

**Success Criteria:**
- All artifacts have lifecycle states
- State transitions work
- Tests validate lifecycle

---

### Task 5.4: Code Quality & Documentation

**Status:** ⚠️ Needs polish

**Action:**
1. Remove all remaining TODOs (if any)
2. Add docstrings to all new code
3. Update architecture documentation
4. Create migration completion summary

**Success Criteria:**
- No TODOs in production code
- All code documented
- Documentation updated

---

**Phase 5 Success Criteria:**
- ✅ Four-class data architecture complete
- ✅ TTL enforcement working
- ✅ All code documented
- ✅ Documentation updated

**Estimated Time:** 4-6 hours

---

## Implementation Checklist

### Phase 0: Foundation & Infrastructure
- [ ] Task 0.4: Verify Session Boundary Pattern
- [ ] Task 0.5: Verify PlatformStateProvider Sync & Runtime Authority

### Phase 1: Frontend State Management Migration
- [ ] Task 1.1: Audit All GlobalSessionProvider Usage
- [ ] Task 1.2: Migrate Core Infrastructure Components
- [ ] Task 1.3: Migrate Pillar Components
- [ ] Task 1.4: Migrate Remaining Components
- [ ] Task 1.5: Remove GlobalSessionProvider

### Phase 2: Backend Core Services
- [ ] Task 2.1: Implement EmbeddingService
- [ ] Task 2.2: Fix SemanticMeaningAgent Placeholder
- [ ] Task 2.3: Fix Embedding Extraction Placeholder

### Phase 3: Realm Integration
- [ ] Task 3.1: Integrate Journey Realm with Artifact Plane
- [ ] Task 3.2: Integrate Insights Realm with Artifact Plane

### Phase 4: Frontend Feature Completion
- [ ] Task 4.1: Fix State Management Placeholders
- [ ] Task 4.2: Fix Mock User ID
- [ ] Task 4.3: Fix File Upload Mock Fallback
- [ ] Task 4.4: Implement Business Outcomes Handlers
- [ ] Task 4.5: Remove All Direct API Calls

### Phase 5: Data Architecture & Polish
- [ ] Task 5.1: Implement TTL Enforcement for Working Materials
- [ ] Task 5.2: Complete Records of Fact Promotion
- [ ] Task 5.3: Complete Purpose-Bound Outcomes Lifecycle
- [ ] Task 5.4: Code Quality & Documentation

---

## Risk Assessment

### High Risk Areas

1. **Frontend State Migration (Phase 1)**
   - **Risk:** Breaking existing functionality
   - **Mitigation:** Incremental migration, test after each file
   - **Rollback:** Keep GlobalSessionProvider until migration complete

2. **EmbeddingService Implementation (Phase 2)**
   - **Risk:** Integration with LLM providers
   - **Mitigation:** Start with OpenAI (well-documented), add others later
   - **Rollback:** Keep placeholder until service works

3. **Artifact Plane Integration (Phase 3)**
   - **Risk:** Breaking existing artifact retrieval
   - **Mitigation:** Test thoroughly, keep old storage until new works
   - **Rollback:** Keep old storage pattern until integration complete

### Medium Risk Areas

1. **Business Outcomes Handlers (Phase 4)**
   - **Risk:** Backend endpoints may not exist
   - **Mitigation:** Create backend endpoints first, then frontend
   - **Rollback:** Keep TODOs until backend ready

2. **TTL Enforcement (Phase 5)**
   - **Risk:** Accidentally purging active data
   - **Mitigation:** Test thoroughly, add safeguards
   - **Rollback:** Disable automation until tested

---

## Success Metrics

### Technical Metrics

- ✅ Zero context errors
- ✅ Zero references to GlobalSessionProvider
- ✅ Zero placeholders/mocks in production code
- ✅ Zero TODOs in production code
- ✅ All tests passing
- ✅ All integrations working

### Functional Metrics

- ✅ Login flow works
- ✅ File upload works
- ✅ File parsing works
- ✅ Embedding creation works
- ✅ Semantic interpretation works
- ✅ Business analysis works
- ✅ SOP generation works
- ✅ POC creation works
- ✅ Roadmap generation works
- ✅ Artifact export works

### Architecture Metrics

- ✅ All execution through Runtime
- ✅ All data access through Realms
- ✅ All infrastructure through Public Works
- ✅ Session-first pattern working
- ✅ Intent-based execution working
- ✅ Policy-governed sagas working

---

## Timeline

### Week 1: Foundation & Core
- **Days 1-2:** Phase 0 (Foundation validation)
- **Days 3-5:** Phase 1 (Frontend state migration)

### Week 2: Backend & Integration
- **Days 1-3:** Phase 2 (Backend core services)
- **Days 4-5:** Phase 3 (Realm integration)

### Week 3: Features & Polish
- **Days 1-3:** Phase 4 (Frontend feature completion)
- **Days 4-5:** Phase 5 (Data architecture & polish)

**Total Estimated Time:** 3 weeks (40-60 hours)

---

## Next Steps

1. **Review this plan** with team
2. **Approve priorities** and timeline
3. **Start Phase 0** (Foundation validation)
4. **Execute phases sequentially** (don't skip ahead)
5. **Test after each phase** (don't proceed if tests fail)
6. **Update checklist** as tasks complete

---

## References

- **Platform Build Guide:** `docs/01242026_final/04_PLATFORM_BUILD_GUIDE.md`
- **Architectural Principles:** `docs/01242026_final/00_ARCHITECTURAL_PRINCIPLES_CTO_VALIDATED.md`
- **Backend Architecture:** `docs/01242026_final/01_BACKEND_ARCHITECTURE_SUMMARY.md`
- **Frontend Architecture:** `docs/01242026_final/02_FRONTEND_ARCHITECTURE_SUMMARY.md`
- **Platform North Star:** `docs/01242026_final/03_OVERALL_PLATFORM_ARCHITECTURE_NORTH_STAR.md`
- **Frontend/Backend Integration Audit:** `docs/FRONTEND_BACKEND_INTEGRATION_AUDIT.md`
- **Platform Audit:** `docs/PLATFORM_AUDIT_AND_REFACTORING_PLAN.md`

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **READY FOR IMPLEMENTATION**
