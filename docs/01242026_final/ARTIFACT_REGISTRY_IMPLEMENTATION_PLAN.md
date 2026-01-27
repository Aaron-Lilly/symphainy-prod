# Artifact Registry Implementation Plan

**Date:** January 26, 2026  
**Status:** 🔴 **READY FOR IMPLEMENTATION**  
**Based on:** CTO-validated strategic analysis with refined schema

---

## Executive Summary

This document provides the concrete implementation plan for Phase 1: State Surface Artifact Registry. This is the foundation that enables all subsequent artifact-centric changes.

**CTO Validation:** ✅ Analysis confirmed, schema refined, ready to proceed

---

## 1. Artifact Registry Schema (CTO-Recommended)

### 1.1 Core Artifact Record

```python
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Materialization:
    """Single materialization of an artifact."""
    materialization_id: str
    storage_type: str  # "gcs" | "arango" | "duckdb" | "vector_store"
    uri: str
    format: str  # "json" | "parquet" | "csv" | "faiss"
    compression: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class SemanticDescriptor:
    """What the artifact means (independent of storage)."""
    schema: str  # logical schema / version
    record_count: Optional[int] = None
    parser_type: Optional[str] = None
    embedding_model: Optional[str] = None
    # Add other semantic fields as needed
    # NO storage info here

@dataclass
class ProducedBy:
    """Provenance: which intent execution produced this artifact."""
    intent: str  # "ingest_file", "parse_content", "extract_embeddings"
    execution_id: str

@dataclass
class ArtifactRecord:
    """Authoritative artifact registry entry."""
    # Identity
    artifact_id: str
    artifact_type: str  # "file" | "parsed_content" | "embeddings" | "summary" | etc.
    tenant_id: str
    
    # Provenance
    produced_by: ProducedBy
    parent_artifacts: List[str] = field(default_factory=list)  # lineage
    
    # Lifecycle
    lifecycle_state: str  # "PENDING" | "READY" | "FAILED" | "ARCHIVED" | "DELETED"
    
    # Semantics (what it means)
    semantic_descriptor: SemanticDescriptor
    
    # Materialization (how it's stored)
    materializations: List[Materialization] = field(default_factory=list)
    
    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
```

### 1.2 Schema Rationale

**Why separate identity, semantics, and materialization?**

1. **Identity independence**: Artifact ID stays stable even if storage changes
2. **Multiple materializations**: One artifact can exist in GCS (JSON), ArangoDB (graph), DuckDB (deterministic)
3. **Semantic stability**: What it means doesn't change when re-materialized
4. **Future-proof**: Supports new storage backends, formats, compression without schema changes

**Why richer lifecycle?**

- `PENDING`: Intent submitted, artifact registered, but materialization not complete
- `READY`: Valid and accessible
- `FAILED`: Intent executed but artifact invalid (enables retries)
- `ARCHIVED`: Retained but not active
- `DELETED`: Marked for deletion

---

## 2. State Surface Artifact Registry API

### 2.1 Core Methods

```python
class ArtifactRegistry:
    """
    Artifact registry within State Surface.
    
    Provides authoritative artifact resolution and lifecycle management.
    """
    
    async def register_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        tenant_id: str,
        produced_by: ProducedBy,
        semantic_descriptor: SemanticDescriptor,
        parent_artifacts: Optional[List[str]] = None,
        lifecycle_state: str = "PENDING"
    ) -> bool:
        """
        Register a new artifact.
        
        Args:
            artifact_id: Stable, global artifact identifier
            artifact_type: Type of artifact
            tenant_id: Tenant identifier
            produced_by: Intent execution that produced this artifact
            semantic_descriptor: What the artifact means
            parent_artifacts: Lineage (optional)
            lifecycle_state: Initial lifecycle state (default: PENDING)
        
        Returns:
            True if registration successful
        """
        pass
    
    async def resolve_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        tenant_id: str
    ) -> Optional[ArtifactRecord]:
        """
        Resolve artifact by ID with validation.
        
        Validates:
        - Artifact exists
        - Artifact type matches
        - Tenant access
        - Lifecycle state is accessible (READY or ARCHIVED)
        
        Args:
            artifact_id: Artifact identifier
            artifact_type: Expected artifact type
            tenant_id: Tenant identifier (for access control)
        
        Returns:
            ArtifactRecord if found and accessible, None otherwise
        
        Raises:
            ValueError: If artifact not found or not accessible
        """
        pass
    
    async def add_materialization(
        self,
        artifact_id: str,
        tenant_id: str,
        materialization: Materialization
    ) -> bool:
        """
        Add a materialization to an existing artifact.
        
        Allows one artifact to have multiple storage forms.
        
        Args:
            artifact_id: Artifact identifier
            tenant_id: Tenant identifier
            materialization: Materialization to add
        
        Returns:
            True if successful
        """
        pass
    
    async def update_artifact_lifecycle(
        self,
        artifact_id: str,
        tenant_id: str,
        new_state: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Update artifact lifecycle state.
        
        Valid state transitions:
        - PENDING → READY (materialization complete)
        - PENDING → FAILED (materialization failed)
        - READY → ARCHIVED (retention policy)
        - ARCHIVED → DELETED (deletion policy)
        - Any → FAILED (validation failure)
        
        Args:
            artifact_id: Artifact identifier
            tenant_id: Tenant identifier
            new_state: New lifecycle state
            reason: Optional reason for state change
        
        Returns:
            True if successful
        """
        pass
    
    # ⚠️ NO list_artifacts() method in State Surface
    # Supabase is for exploration/discovery (dropdowns)
    # State Surface is for resolution (actions)
    # See ARTIFACT_LISTING_UI_PATTERN.md for listing pattern
```

### 2.2 Integration with State Surface

```python
# In state_surface.py
class StateSurface:
    def __init__(self, ...):
        # ... existing initialization ...
        self.artifact_registry = ArtifactRegistry(
            state_abstraction=self.state_abstraction,
            use_memory=self.use_memory
        )
    
    # Delegate artifact operations
    async def register_artifact(self, ...):
        return await self.artifact_registry.register_artifact(...)
    
    async def resolve_artifact(self, ...):
        return await self.artifact_registry.resolve_artifact(...)
```

---

## 3. Implementation Steps

### Step 1: Create Artifact Registry Module

**File:** `symphainy_platform/runtime/artifact_registry.py`

**Tasks:**
1. Define dataclasses (ArtifactRecord, Materialization, SemanticDescriptor, ProducedBy)
2. Implement ArtifactRegistry class
3. Use StateManagementAbstraction for storage (ArangoDB for durability)
4. Add validation logic (lifecycle transitions, access control)

**Estimated Time:** 1-2 days

---

### Step 2: Integrate with State Surface

**File:** `symphainy_platform/runtime/state_surface.py`

**Tasks:**
1. Add ArtifactRegistry instance to StateSurface
2. Add delegate methods (register_artifact, resolve_artifact, etc.)
3. Ensure artifact registry uses same state abstraction as State Surface

**Estimated Time:** 0.5 days

---

### Step 3: Update ContentOrchestrator to Register Artifacts

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Tasks:**
1. After `ingest_file` intent execution:
   - Register `file` artifact with lifecycle_state=PENDING
   - Add GCS materialization
   - Update lifecycle_state=READY when materialization complete
   
2. After `parse_content` intent execution:
   - Register `parsed_content` artifact
   - Set parent_artifacts=[file_id]
   - Add GCS materialization
   - Update lifecycle_state=READY
   
3. After `extract_embeddings` intent execution:
   - Register `embeddings` artifact
   - Set parent_artifacts=[parsed_file_id]
   - Add ArangoDB materialization
   - Update lifecycle_state=READY

**Estimated Time:** 2-3 days

---

### Step 4: Add Runtime Artifact Resolution API

**File:** `symphainy_platform/runtime/runtime_api.py`

**Tasks:**
1. Add `/api/artifact/resolve` endpoint
2. Endpoint validates access, resolves via State Surface
3. Retrieves content via materialization URI (opaque)
4. Returns artifact content

**Estimated Time:** 1 day

---

### Step 4a: Add Supabase Artifact Index API (For UI Dropdowns)

**File:** `symphainy_platform/runtime/runtime_api.py` or separate index service

**Tasks:**
1. Add `/api/artifact/list` endpoint (or use Supabase directly)
2. Endpoint queries Supabase artifact index
3. Supports filters: `artifact_type`, `lifecycle_state`, `eligible_for`
4. Returns artifact metadata (not content) for dropdowns
5. See `ARTIFACT_LISTING_UI_PATTERN.md` for pattern

**Key Distinction:**
- `/api/artifact/list` → Supabase (discovery/index)
- `/api/artifact/resolve` → State Surface (resolution)

**Estimated Time:** 1 day

---

### Step 5: Test End-to-End

**Tasks:**
1. Test artifact registration after intent execution
2. Test artifact resolution via Runtime API
3. Test lifecycle state transitions
4. Test multiple materializations
5. Test access control (tenant isolation)

**Estimated Time:** 1-2 days

---

## 4. Migration Strategy

### 4.1 Backward Compatibility

**Critical:** Existing code must continue working during migration.

**Approach:**
1. Add artifact registration **alongside** existing file reference storage
2. New intents register artifacts, old code still works
3. Gradually migrate retrieval to artifact resolution
4. Deprecate old patterns once migration complete

### 4.2 Phased Rollout

**Week 1: Foundation**
- ✅ Implement ArtifactRegistry
- ✅ Integrate with State Surface
- ✅ Test artifact registration/resolution

**Week 2: Backend Integration**
- ✅ Update `ingest_file` to register artifacts
- ✅ Update `parse_content` to register artifacts
- ✅ Update `extract_embeddings` to register artifacts

**Week 3: Runtime API**
- ✅ Add artifact resolution endpoint
- ✅ Test end-to-end resolution

**Week 4: Frontend Integration**
- ✅ Add `resolveArtifact()` to PlatformState
- ✅ Add `listArtifacts()` to ContentAPIManager (replaces listFiles, etc.)
- ✅ Migrate one dropdown to artifact listing pattern
- ✅ Migrate one component to artifact resolution
- ✅ Test frontend artifact resolution and listing

---

## 5. Success Criteria

### 5.1 Functional

- ✅ Artifacts registered after intent execution
- ✅ Artifacts resolvable by ID via Runtime API
- ✅ Lifecycle states transition correctly
- ✅ Multiple materializations supported
- ✅ Access control enforced (tenant isolation)

### 5.2 Architectural

- ✅ No direct storage queries from application code
- ✅ State Surface is authoritative for artifacts
- ✅ Storage is opaque (content_ref, not storage_location)
- ✅ Artifact identity independent of storage

### 5.3 Litmus Test

> "If I changed the storage backend tomorrow, would this code change?"

**Target:** ✅ **PASSES** - Artifact resolution uses opaque materialization URIs

---

## 6. Risk Mitigation

### 6.1 Risks

1. **Schema evolution**: Artifact schema may need changes
   - **Mitigation**: Schema is extensible, semantic_descriptor is flexible

2. **Performance**: Artifact resolution adds latency
   - **Mitigation**: State Surface uses ArangoDB (fast), materialization retrieval is async

3. **Migration complexity**: Dual system during transition
   - **Mitigation**: Backward compatible, gradual migration

### 6.2 Rollback Plan

If issues arise:
1. Artifact registration is additive (doesn't break existing code)
2. Can disable artifact registration without breaking existing flows
3. Old file reference storage continues working

---

## 7. Next Steps

1. **Review this plan with team**
2. **Start Step 1: Create Artifact Registry Module**
3. **Implement and test incrementally**
4. **Document as we go**

**Status:** Ready to begin implementation
