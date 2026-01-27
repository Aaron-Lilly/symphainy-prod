# Phase 2: Backend Core Semantic Services (REFINED)

**Date:** January 24, 2026  
**Status:** ✅ **REFINED WITH CTO + CIO FEEDBACK**  
**Goal:** Replace placeholders with *operationally honest* semantic services that support scalable, cost-effective embedding architecture

**Why Now:** These services define semantic truth for all realms. Phase 1 locked frontend to runtime as single source of truth. Phase 2 is the first time backend placeholders will be exercised end-to-end by real UI flows.

**Dependencies:** Phase 0 (foundations must work), Phase 1 (frontend state management complete)

**Estimated Time:** 10-14 hours (increased due to chunking layer and contract documentation)

---

## Executive Summary

Phase 2 combines:
- **CTO's Vision:** Deterministic → Semantic → On-Demand Hydration model
- **CIO's Refinements:** Chunking strategy, structured outputs, failure semantics, contracts
- **Platform Enhancements:** Intent-driven triggers, Public Works governance, dual-layer deterministic

**Key Principle:** Phase 2 defines the **semantic truth layer**. If done correctly, Phase 3 becomes *composition*, not archaeology.

---

## CTO + CIO Alignment

### CTO's 5 Non-Negotiable Principles
1. Deterministic before semantic
2. Semantic meaning is contextual and versioned
3. No semantic computation without explicit trigger
4. All semantics must reference stable deterministic identities
5. Hydration is cheaper than storage

### CIO's "Land the Plane" Expectations
1. Semantic outputs are deterministic and replayable
2. No UX or AGUI concepts in backend code
3. All artifacts are self-describing
4. SemanticMeaningAgent produces structured meaning
5. Orchestrators own truth, agents own reasoning
6. Failures are first-class outcomes
7. One short contract doc exists

### Combined Requirements
- ✅ Chunk-level deterministic identity (CTO + CIO Gap 1)
- ✅ Structured semantic outputs (CTO + CIO Gap 2)
- ✅ Explicit failure semantics (CIO Gap 3)
- ✅ Semantic contracts (CIO requirement)
- ✅ Intent-driven triggers (Platform enhancement)
- ✅ Public Works enforcement (Platform enhancement)

---

## Task 2.0: Implement Deterministic Chunking Layer (CRITICAL - Must be first)

**Status:** ❌ Missing - Blocks everything else

**Priority:** 🔴 **CRITICAL**

**Why First:**
- All semantic work depends on stable chunk identity
- Without this, embeddings will be unstable
- Cannot implement idempotency without chunk IDs
- CIO Gap 1: Embedding granularity & chunking strategy

**Location:** `realms/content/enabling_services/deterministic_chunking_service.py`

**Current State:**
- ❌ No chunk-level deterministic identity
- ✅ Schema-level deterministic exists (`DeterministicEmbeddingService`)
- ⚠️ Need to add chunk-level on top of schema-level

**Action:**
1. Create `DeterministicChunk` data class
2. Implement chunking based on parser structure (not heuristics)
3. Generate stable chunk IDs (content-addressed or path-derived)
4. Store chunk metadata (index, source_path, text_hash, structural_type)
5. Add chunk lineage tracking (file → page → section → paragraph)
6. Link chunks to schema fingerprints (dual-layer deterministic)
7. Add integration test for chunk stability

**Implementation Pattern:**
```python
@dataclass
class DeterministicChunk:
    """
    Deterministic chunk identity - stable, reproducible, content-addressed.
    
    CTO Principle: Deterministic = identity + structure + locality signals
    CIO Requirement: Chunk boundaries must be deterministic and replayable
    """
    chunk_id: str  # Stable, content-addressed (SHA256-based)
    chunk_index: int
    source_path: str  # file → page → section → paragraph
    text_hash: str  # Normalized hash for re-embedding detection
    structural_type: str  # page | section | paragraph | table | cell
    byte_offset: Optional[int]
    logical_offset: Optional[int]
    text: str
    # ENHANCEMENT: Link to schema-level deterministic
    schema_fingerprint: Optional[str]  # Links to schema-level
    pattern_hints: Optional[Dict[str, Any]]  # From pattern signature
    metadata: Dict[str, Any]

class DeterministicChunkingService:
    """
    Creates deterministic chunks from parsed content.
    
    CIO Requirement: Chunking must be deterministic and reversible
    CTO Principle: Chunking based on parser structure, not heuristics
    """
    
    def __init__(self, public_works: PublicWorksFoundationService):
        self.parser_registry = public_works.parser_registry
        self.deterministic_embedding_service = DeterministicEmbeddingService(public_works)
    
    async def create_chunks(
        self,
        parsed_content: Dict[str, Any],
        file_id: str,
        tenant_id: str
    ) -> List[DeterministicChunk]:
        """
        Create deterministic chunks from parsed content.
        
        CIO Requirement: Same input → same chunks (deterministic)
        CTO Principle: Use parser structure, not heuristics
        """
        # Get schema-level deterministic (if exists)
        schema_fingerprint = None
        pattern_signature = None
        try:
            deterministic_embedding = await self.deterministic_embedding_service.get_deterministic_embedding(
                parsed_file_id=parsed_content.get("parsed_file_id"),
                context=ExecutionContext(tenant_id=tenant_id)
            )
            if deterministic_embedding:
                schema_fingerprint = deterministic_embedding.get("schema_fingerprint")
                pattern_signature = deterministic_embedding.get("pattern_signature")
        except:
            pass  # Schema-level may not exist yet
        
        # Use parser structure, not heuristics
        parser_type = parsed_content.get("parser_type")
        structure = parsed_content.get("structure", {})
        
        chunks = []
        for idx, element in enumerate(self._extract_structural_elements(structure)):
            # Generate stable chunk ID (content-addressed)
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
                schema_fingerprint=schema_fingerprint,
                pattern_hints=pattern_signature,
                metadata={
                    "file_id": file_id,
                    "tenant_id": tenant_id,
                    "parser_type": parser_type,
                    "created_at": datetime.utcnow().isoformat()
                }
            ))
        
        return chunks
    
    def _generate_chunk_id(
        self,
        file_id: str,
        element_path: str,
        text_hash: str
    ) -> str:
        """
        Generate stable, content-addressed chunk ID.
        
        CIO Requirement: Deterministic and replayable
        CTO Principle: Stable identity
        """
        content = f"{file_id}:{element_path}:{text_hash}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]  # 16-char ID
```

**Success Criteria:**
- ✅ Chunks are stable (same input → same chunks)
- ✅ Chunk IDs are deterministic and content-addressed
- ✅ Lineage is tracked (file → page → section → paragraph)
- ✅ Chunks link to schema fingerprints (dual-layer deterministic)
- ✅ Integration test validates chunk stability (CIO requirement)
- ✅ Re-running on same file produces identical chunk IDs

---

## Task 2.1: Implement EmbeddingService (Chunk-Based, Idempotent, Profile-Aware)

**Status:** ❌ Missing - Critical blocker

**Priority:** 🔴 **CRITICAL**

**Location:** `realms/content/enabling_services/embedding_service.py`

**CTO Feedback:** Chunk-based, idempotent, profile-aware, stores by reference  
**CIO Feedback:** Per-chunk embeddings, stable chunk IDs, explicit failure handling

**Current State:**
- ❌ File doesn't exist
- ❌ Referenced in comments but not implemented
- ❌ `_handle_extract_embeddings()` returns placeholder

**Action:**
1. Create `EmbeddingService` class
2. Implement `create_embeddings()` method (chunk-based)
3. Integrate with embedding model provider (OpenAI, Cohere, etc.)
4. Use `SemanticDataAbstraction` for storage
5. Implement idempotency checks
6. Add semantic profile support
7. Add explicit failure handling (CIO Gap 3)
8. Update `content_orchestrator._handle_extract_embeddings()` to use service
9. Add integration test

**CTO + CIO-Aligned Implementation Pattern:**
```python
class EmbeddingService:
    """
    Embedding Service - Creates semantic embeddings from deterministic chunks.
    
    CTO Principle: Chunk-based, idempotent, profile-aware, stores by reference
    CIO Requirement: Per-chunk embeddings, stable chunk IDs, explicit failures
    """
    
    def __init__(self, public_works: PublicWorksFoundationService):
        self.semantic_data = public_works.semantic_data_abstraction
        self.llm_adapter = public_works.openai_adapter
    
    async def create_embeddings(
        self,
        chunks: List[DeterministicChunk],
        semantic_profile: str,
        model_name: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Create semantic embeddings for chunks (idempotent, profile-aware).
        
        Returns:
            {
                "status": "success" | "partial" | "failed",
                "embedded_chunk_ids": List[str],
                "failed_chunks": List[Dict[str, Any]],
                "semantic_profile": str,
                "model_name": str
            }
        """
        results = {
            "status": "success",
            "embedded_chunk_ids": [],
            "failed_chunks": [],
            "semantic_profile": semantic_profile,
            "model_name": model_name
        }
        
        for chunk in chunks:
            try:
                # Idempotency check (CTO principle)
                if self.semantic_data.embedding_exists(
                    chunk_id=chunk.chunk_id,
                    semantic_profile=semantic_profile,
                    model=model_name
                ):
                    results["embedded_chunk_ids"].append(chunk.chunk_id)
                    continue  # Skip if already embedded
                
                # Create embedding
                embedding = await self.llm_adapter.create_embeddings(
                    text=chunk.text,
                    model=model_name
                )
                
                # Store by reference (chunk_id), not blob (CTO principle)
                await self.semantic_data.store_embedding(
                    chunk_id=chunk.chunk_id,
                    embedding=embedding,
                    semantic_profile=semantic_profile,
                    model=model_name,
                    semantic_version="1.0.0",  # Platform-controlled (CTO principle)
                    metadata={
                        "chunk_index": chunk.chunk_index,
                        "source_path": chunk.source_path,
                        "text_hash": chunk.text_hash,
                        "structural_type": chunk.structural_type,
                        "schema_fingerprint": chunk.schema_fingerprint,
                        "tenant_id": tenant_id,
                        "created_at": datetime.utcnow().isoformat()
                    }
                )
                
                results["embedded_chunk_ids"].append(chunk.chunk_id)
                
            except Exception as e:
                # Explicit failure handling (CIO Gap 3)
                results["failed_chunks"].append({
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
                results["status"] = "partial" if results["embedded_chunk_ids"] else "failed"
        
        return results
```

**Success Criteria:**
- ✅ EmbeddingService works with chunks (not blobs)
- ✅ Idempotent (won't re-embed existing chunks)
- ✅ Supports multiple semantic profiles
- ✅ Stores chunk references, not text blobs
- ✅ Explicit failure handling (partial success, failed chunks)
- ✅ Integration test validates embeddings exist and are idempotent

---

## Task 2.2: SemanticMeaningAgent → SemanticSignalExtractor (Structured Output)

**Status:** ❌ Placeholder implementation

**Priority:** 🔴 **CRITICAL**

**Location:** `realms/content/enabling_services/semantic_signal_extractor.py` (Rename from SemanticMeaningAgent)

**CTO Feedback:** Rename to `SemanticSignalExtractor`. It's a semantic normalizer, not a philosopher.  
**CIO Feedback:** Must produce structured signals, not prose-only. Defines what other agents rely on.

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
6. Map to 4-layer agent model (Platform enhancement)
7. Test with real data

**CTO + CIO-Aligned Implementation Pattern:**
```python
class SemanticSignalExtractor(AgentBase):
    """
    Semantic Signal Extractor - Semantic normalizer, not a philosopher.
    
    CTO Principle: Extracts structured semantic signals, normalizes language
    CIO Requirement: Produces structured meaning other agents can depend on
    Platform Enhancement: Uses 4-layer agent model for structure
    """
    
    async def _process_with_assembled_prompt(
        self,
        system_message: str,  # Layer 1 (AgentDefinition)
        user_message: str,
        runtime_context: AgentRuntimeContext,  # Layer 3
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Extract structured semantic signals from chunks.
        
        CIO Requirement: Structured output, not prose-only
        CTO Principle: Reference chunk IDs, not raw text
        """
        # Extract chunks from runtime_context (not raw text)
        chunks = runtime_context.get("chunks", [])
        
        if not chunks:
            return {
                "artifact_type": "semantic_signals",
                "artifact": {
                    "error": "No chunks provided"
                },
                "confidence": 0.0,
                "source_artifact_id": None,
                "producing_agent": self.get_agent_description().get("name"),
                "timestamp": datetime.utcnow().isoformat(),
                "tenant_id": context.tenant_id
            }
        
        # Extract structured signals (not prose)
        signals = await self._extract_structured_signals(
            chunks=chunks,
            system_message=system_message,
            context=context
        )
        
        # CIO Requirement: Self-describing artifact
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
            # CIO Requirement: Self-describing metadata
            "source_artifact_id": chunks[0].chunk_id if chunks else None,
            "producing_agent": self.get_agent_description().get("name"),
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": context.tenant_id,
            # CTO Principle: Reference deterministic IDs
            "derived_from": [chunk.chunk_id for chunk in chunks]
        }
    
    async def _extract_structured_signals(
        self,
        chunks: List[DeterministicChunk],
        system_message: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Extract structured signals using LLM with JSON response format.
        
        CIO Requirement: Deterministic and replayable (modulo model variance)
        """
        # Build structured extraction prompt
        prompt = self._build_structured_extraction_prompt(chunks)
        
        # Use JSON response format for structured output
        response = await self._call_llm(
            prompt=prompt,
            system_message=system_message,
            model="gpt-4o-mini",
            max_tokens=1000,
            temperature=0.3,
            response_format={"type": "json_object"},  # Force structured output
            context=context
        )
        
        return json.loads(response)
```

**Trigger Boundary (CRITICAL - CTO Principle):**
- ❌ **DO NOT** auto-fire on parse/ingest/upload
- ✅ **DO** fire on:
  - Explicit user intent (via intent system - Platform enhancement)
  - Downstream agent request (via intent system)
  - Missing semantic signal required for task (detected by Runtime)

**Success Criteria:**
- ✅ Returns structured signals (not prose-first)
- ✅ References chunk IDs
- ✅ Only fires on explicit triggers
- ✅ Self-describing artifacts (CIO requirement)
- ✅ Test validates structured output
- ✅ Re-running produces structurally identical output (CIO requirement)

---

## Task 2.3: Content Orchestrator - Split Intents & Honest Outcomes

**Status:** ❌ Placeholder implementation

**Priority:** 🔴 **CRITICAL**

**Location:** `realms/content/orchestrators/content_orchestrator.py`

**CTO Feedback:** Split into two intents: `extract_deterministic_structure` and `hydrate_semantic_profile`  
**CIO Feedback:** Explicit failure handling, honest outcomes, no silent success on partial failure

**Current State:**
- Single `extract_embeddings` intent
- No separation of deterministic vs semantic
- Returns fake `embedding_id`
- No explicit failure handling

**Action:**
1. Create `_handle_extract_deterministic_structure()` intent handler
2. Create `_handle_hydrate_semantic_profile()` intent handler
3. Remove old `_handle_extract_embeddings()` placeholder
4. Add explicit failure handling
5. Update intent routing
6. Add integration tests

**CTO + CIO-Aligned Implementation Pattern:**
```python
async def _handle_extract_deterministic_structure(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Extract deterministic chunks (no LLM, no embeddings).
    
    CTO Principle: Deterministic before semantic
    CIO Requirement: Deterministic and replayable
    """
    file_id = intent.parameters.get("file_id")
    parsed_file_id = intent.parameters.get("parsed_file_id")
    
    if not parsed_file_id:
        return {
            "artifact_type": "error",
            "artifact": {
                "error": "parsed_file_id is required",
                "error_type": "ValidationError"
            },
            "confidence": 0.0,
            "source_artifact_id": None,
            "producing_agent": "ContentOrchestrator",
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": context.tenant_id
        }
    
    try:
        # Get parsed content
        parsed_content = await self._get_parsed_content(parsed_file_id, context)
        
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
            "confidence": 1.0,  # Deterministic = 100% confidence
            "source_artifact_id": parsed_file_id,
            "producing_agent": "ContentOrchestrator",
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": context.tenant_id
        }
        
    except Exception as e:
        # Explicit failure handling (CIO Gap 3)
        return {
            "artifact_type": "error",
            "artifact": {
                "error": str(e),
                "error_type": type(e).__name__,
                "retryable": self._is_retryable_error(e)
            },
            "confidence": 0.0,
            "source_artifact_id": parsed_file_id,
            "producing_agent": "ContentOrchestrator",
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": context.tenant_id
        }

async def _handle_hydrate_semantic_profile(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Hydrate semantic embeddings for a specific profile.
    
    CTO Principle: Only fires on explicit trigger (pull-based)
    CIO Requirement: Explicit failure handling, honest outcomes
    Platform Enhancement: Intent-driven trigger
    """
    file_id = intent.parameters.get("file_id")
    semantic_profile = intent.parameters.get("semantic_profile", "default")
    model_name = intent.parameters.get("model_name", "text-embedding-ada-002")
    
    # Check trigger boundary (CTO principle)
    if not self.semantic_trigger_boundary.should_compute_semantics(
        trigger_type="explicit_user_intent",
        intent=intent,
        context=context
    ):
        return {
            "artifact_type": "error",
            "artifact": {
                "error": "Semantic computation not authorized - no explicit trigger",
                "error_type": "TriggerBoundaryViolation"
            },
            "confidence": 0.0,
            "source_artifact_id": file_id,
            "producing_agent": "ContentOrchestrator",
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": context.tenant_id
        }
    
    try:
        # Get deterministic chunks (must exist first - CTO principle)
        chunks = await self._get_deterministic_chunks(file_id, context)
        
        if not chunks:
            return {
                "artifact_type": "error",
                "artifact": {
                    "error": "Deterministic chunks not found. Run extract_deterministic_structure first.",
                    "error_type": "MissingDependency",
                    "retryable": False
                },
                "confidence": 0.0,
                "source_artifact_id": file_id,
                "producing_agent": "ContentOrchestrator",
                "timestamp": datetime.utcnow().isoformat(),
                "tenant_id": context.tenant_id
            }
        
        # Create embeddings (idempotent, profile-aware)
        embedding_result = await self.embedding_service.create_embeddings(
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
            chunk_ids=embedding_result["embedded_chunk_ids"],
            failed_chunks=embedding_result["failed_chunks"],
            tenant_id=context.tenant_id
        )
        
        # CIO Requirement: Honest outcomes (no silent success on partial failure)
        return {
            "artifact_type": "semantic_hydration",
            "artifact": {
                "status": embedding_result["status"],  # success | partial | failed
                "semantic_profile": semantic_profile,
                "model_name": model_name,
                "chunk_count": len(embedding_result["embedded_chunk_ids"]),
                "chunk_ids": embedding_result["embedded_chunk_ids"],
                "failed_chunks": embedding_result["failed_chunks"]  # Explicit failures
            },
            "confidence": 0.9 if embedding_result["status"] == "success" else 0.5,
            "source_artifact_id": file_id,
            "producing_agent": "ContentOrchestrator",
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": context.tenant_id
        }
        
    except Exception as e:
        # Explicit failure handling (CIO Gap 3)
        return {
            "artifact_type": "error",
            "artifact": {
                "error": str(e),
                "error_type": type(e).__name__,
                "retryable": self._is_retryable_error(e)
            },
            "confidence": 0.0,
            "source_artifact_id": file_id,
            "producing_agent": "ContentOrchestrator",
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": context.tenant_id
        }
```

**Success Criteria:**
- ✅ Two separate intents implemented
- ✅ Deterministic step is LLM-free
- ✅ Semantic step is trigger-based
- ✅ Explicit failure handling (partial success, failed chunks)
- ✅ Honest outcomes (no silent success on partial failure)
- ✅ Integration test validates flow

---

## Task 2.4: Semantic Profile System

**Status:** ❌ Missing

**Priority:** 🟡 **HIGH**

**Location:** `realms/content/enabling_services/semantic_profile_registry.py`

**CTO Feedback:** Semantic profiles are versioned, scoped, contextual  
**Platform Enhancement:** Map semantic profiles to AgentPosture

**Action:**
1. Create `SemanticProfile` data class
2. Implement `SemanticProfileRegistry`
3. Store profiles in Supabase
4. Reference profiles in all semantic artifacts
5. Link to AgentPosture (Platform enhancement)
6. Add profile management endpoints

**Implementation Pattern:**
```python
@dataclass
class SemanticProfile:
    """
    Semantic Profile - Versioned, scoped semantic interpretation.
    
    CTO Principle: Semantic meaning is contextual and versioned
    Platform Enhancement: Links to AgentPosture for behavioral tuning
    """
    profile_name: str
    model_name: str
    prompt_template: str
    semantic_version: str  # Platform-controlled
    agent_posture_config: Dict[str, Any]  # Platform enhancement
    compliance_mode: str
    created_at: datetime
    is_active: bool
    metadata: Dict[str, Any]

class SemanticProfileRegistry:
    """
    Registry for semantic profiles.
    
    CTO Principle: Profiles are versioned and scoped
    """
    
    def __init__(self, public_works: PublicWorksFoundationService):
        self.registry = public_works.registry_abstraction
    
    async def get_profile(self, profile_name: str, version: Optional[str] = None) -> SemanticProfile:
        """Get semantic profile (latest version if version not specified)."""
        pass
    
    async def register_profile(self, profile: SemanticProfile):
        """Register new semantic profile."""
        pass
    
    async def list_profiles(self, tenant_id: str) -> List[SemanticProfile]:
        """List all active profiles for tenant."""
        pass
```

**Success Criteria:**
- ✅ Profiles can be registered and retrieved
- ✅ Profiles are versioned
- ✅ All semantic artifacts reference profiles
- ✅ Profiles link to AgentPosture (Platform enhancement)

---

## Task 2.5: Semantic Trigger Boundary

**Status:** ❌ Missing

**Priority:** 🟡 **HIGH**

**Location:** `realms/content/enabling_services/semantic_trigger_boundary.py`

**CTO Principle:** No semantic computation without explicit trigger  
**Platform Enhancement:** Use intent system for triggers

**Action:**
1. Create `SemanticTriggerBoundary` class
2. Define trigger types (explicit_user_intent, downstream_agent_request, missing_semantic_signal)
3. Integrate with Content Orchestrator
4. Use intent system for trigger detection (Platform enhancement)
5. Add logging for cost tracking

**Implementation Pattern:**
```python
class SemanticTriggerBoundary:
    """
    Enforces pull-based semantic computation.
    
    CTO Principle: No semantic computation without explicit trigger
    Platform Enhancement: Uses intent system for trigger detection
    """
    
    TRIGGER_TYPES = [
        "explicit_user_intent",
        "downstream_agent_request",
        "missing_semantic_signal"
    ]
    
    def should_compute_semantics(
        self,
        trigger_type: str,
        intent: Optional[Intent] = None,
        context: ExecutionContext
    ) -> bool:
        """
        Determine if semantic computation should proceed.
        
        Platform Enhancement: Uses intent system for trigger detection
        """
        if trigger_type not in self.TRIGGER_TYPES:
            return False
        
        # Platform Enhancement: Intent-driven trigger detection
        if trigger_type == "explicit_user_intent":
            return intent is not None and intent.type == "hydrate_semantic_profile"
        
        if trigger_type == "downstream_agent_request":
            # Check if agent requested semantic signal via intent
            return context.get("requested_semantic_signal") is not None
        
        if trigger_type == "missing_semantic_signal":
            # Check if semantic signal is required but missing
            return context.get("required_semantic_signal") is not None
        
        return False
    
    async def log_semantic_computation(
        self,
        chunk_ids: List[str],
        semantic_profile: str,
        model_name: str,
        trigger_type: str,
        context: ExecutionContext
    ):
        """
        Log semantic computation for cost tracking.
        
        Platform Enhancement: Uses Runtime WAL for cost tracking
        """
        # Log to Runtime WAL (Platform enhancement)
        await self.runtime_wal.log_semantic_computation(
            chunk_ids=chunk_ids,
            semantic_profile=semantic_profile,
            model_name=model_name,
            trigger_type=trigger_type,
            tenant_id=context.tenant_id
        )
```

**Success Criteria:**
- ✅ SemanticSignalExtractor only fires on explicit triggers
- ✅ All semantic computations are logged
- ✅ Integration test validates trigger enforcement
- ✅ Cost tracking shows selective hydration

---

## Task 2.6: Semantic Contracts & Invariants (CIO Requirement)

**Status:** ❌ Missing

**Priority:** 🟡 **HIGH**

**Location:** `docs/01242026_final/SEMANTIC_TRUTH_CONTRACT_V1.md`

**CIO Requirement:** One short contract doc that defines what embeddings and semantic meaning guarantee

**Action:**
1. Create `SEMANTIC_TRUTH_CONTRACT_V1.md`
2. Document what embeddings guarantee
3. Document what semantic meaning guarantees
4. Document what is explicitly NOT guaranteed yet
5. Define handshake between Backend, Experience SDK, AGUI, Frontend runtime

**Contract Template:**
```markdown
# Semantic Truth Contract V1

## What Embeddings Guarantee

1. **Chunk Identity:** Each embedding references a stable `chunk_id`
2. **Idempotency:** Re-embedding same chunk with same profile/model produces same result
3. **Profile Isolation:** Different semantic profiles produce different embeddings
4. **Versioning:** All embeddings have `semantic_version` for selective re-embedding

## What Semantic Meaning Guarantees

1. **Structured Output:** Semantic signals are structured, not prose-only
2. **Chunk References:** All semantic artifacts reference `chunk_id`
3. **Deterministic Structure:** Same chunks → same semantic structure (modulo model variance)
4. **Trigger-Based:** Only computed on explicit triggers

## What Is Explicitly NOT Guaranteed Yet

1. **Cross-Chunk Reasoning:** Not yet supported
2. **Multi-Vector Per Chunk:** Not yet supported
3. **Re-Ranking:** Not yet supported
4. **Learned Chunking:** Not yet supported

## Handshake Between Systems

- **Backend:** Produces deterministic chunks and semantic embeddings
- **Experience SDK:** Consumes semantic artifacts for user experiences
- **AGUI:** Compiles semantic meaning, not text
- **Frontend Runtime:** Renders semantic state
```

**Success Criteria:**
- ✅ Contract document exists
- ✅ Defines guarantees and non-guarantees
- ✅ Handshake between systems documented
- ✅ Team validated contract

---

## Phase 2 Success Criteria (Combined CTO + CIO)

### Foundation Lock Criteria (All Must Pass):

**CTO Principles:**
- ✅ Deterministic chunking implemented and stable
- ✅ EmbeddingService works with chunks (idempotent, profile-aware)
- ✅ SemanticSignalExtractor returns structured signals
- ✅ Content Orchestrator has separate deterministic/semantic intents
- ✅ Semantic profile system implemented
- ✅ Semantic trigger boundary enforced

**CIO "Land the Plane" Expectations:**
- ✅ Semantic outputs are deterministic and replayable
- ✅ No UX or AGUI concepts in backend code
- ✅ All artifacts are self-describing
- ✅ SemanticSignalExtractor produces structured meaning
- ✅ Orchestrators own truth, agents own reasoning
- ✅ Failures are first-class outcomes
- ✅ Semantic contract document exists

**Operational:**
- ✅ All integration tests pass
- ✅ Cost tracking shows selective hydration
- ✅ Explicit failure handling works
- ✅ Re-running produces identical outputs (deterministic)

---

## Implementation Order

1. **Task 2.0:** Deterministic Chunking Layer (CRITICAL - Blocks everything)
2. **Task 2.1:** EmbeddingService (Chunk-Based)
3. **Task 2.2:** SemanticSignalExtractor (Structured)
4. **Task 2.3:** Content Orchestrator (Split Intents)
5. **Task 2.4:** Semantic Profile System
6. **Task 2.5:** Semantic Trigger Boundary
7. **Task 2.6:** Semantic Contracts & Invariants

---

## Key Architectural Decisions

### 1. Dual-Layer Deterministic (Platform Enhancement)

**Decision:** Keep schema-level + add chunk-level

**Rationale:**
- Schema-level enables schema matching, data type inference
- Chunk-level enables semantic search, text queries
- Both serve different purposes and complement each other

**Implementation:**
- Chunks reference `schema_fingerprint`
- Pattern signatures guide semantic profile selection

---

### 2. Intent-Driven Semantic Triggers (Platform Enhancement)

**Decision:** Use intent system for semantic trigger mechanism

**Rationale:**
- Intents are already explicit and auditable
- Runtime can enforce trigger boundaries
- Intent history provides cost tracking

**Implementation:**
- Runtime automatically detects "missing semantic signal" triggers
- Agents request semantic signals via intents

---

### 3. Public Works Enforcement (Platform Enhancement)

**Decision:** Enforce CTO's principles in Public Works abstractions

**Rationale:**
- Abstractions can enforce chunk_id references
- Abstractions can require semantic_version
- Abstractions can log all semantic computations

**Implementation:**
- `SemanticDataAbstraction.store_embedding()` requires chunk_id
- `SemanticDataAbstraction.store_embedding()` requires semantic_version
- All semantic computations logged automatically

---

## Testing Strategy

### Deterministic Tests (CIO Requirement)

**Test:** Re-run embedding + semantic meaning on same file twice  
**Expected:** Outputs should be structurally identical (modulo model variance)

### Trigger Boundary Tests (CTO Principle)

**Test:** Attempt semantic computation without explicit trigger  
**Expected:** Should be rejected by SemanticTriggerBoundary

### Failure Handling Tests (CIO Requirement)

**Test:** Simulate partial embedding failure  
**Expected:** Artifact should have `status: "partial"` and `failed_chunks` list

### Self-Describing Artifact Tests (CIO Requirement)

**Test:** Check all artifacts have required metadata  
**Expected:** All artifacts have `artifact_type`, `source_artifact_id`, `producing_agent`, `timestamp`, `tenant_id`

---

## Estimated Time

**Original Estimate:** 6-8 hours  
**Refined Estimate:** 10-14 hours

**Breakdown:**
- Task 2.0: 2-3 hours (chunking layer)
- Task 2.1: 2-3 hours (embedding service)
- Task 2.2: 2-3 hours (semantic signal extractor)
- Task 2.3: 2-3 hours (orchestrator split)
- Task 2.4: 1-2 hours (profile system)
- Task 2.5: 1 hour (trigger boundary)
- Task 2.6: 1 hour (contract doc)

---

## Next Steps After Phase 2

1. ✅ **Phase 3: Realm Integration** - Can now compose on semantic truth layer
2. ✅ **AGUI Alignment** - Semantic signals ready for AGUI compilation
3. ✅ **Experience SDK** - Can consume semantic artifacts

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **REFINED - READY FOR IMPLEMENTATION**
