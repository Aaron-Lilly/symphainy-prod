# Multi-Component Artifact Storage Strategy

**Date:** January 17, 2026  
**Status:** 🔴 **CRITICAL ARCHITECTURAL CONSIDERATION**  
**Issue:** Complex artifacts with multiple interconnected components need integrated storage

---

## Executive Summary

**Problem:** Some artifacts have multiple interconnected components that must be stored and retrieved as integrated wholes. Simple file storage won't preserve relationships.

**Examples:**
1. **Hybrid Embeddings** - 3 components (structured data, unstructured data, correlation map)
2. **Coexistence Blueprint** - 4 components (current state, coexistence state, roadmap, responsibility matrix)
3. **Roadmaps** - Multiple phases with dependencies
4. **Solution Synthesis** - Multiple pillar summaries with relationships

**Solution:** Composite Artifact Pattern - Store main artifact with component references and relationships.

---

## Multi-Component Artifacts Identified

### 1. Hybrid Embeddings (3 Components) 🔴

**Components:**
1. **Structured Data** (tables/records)
   - Format: JSON structured data
   - Size: Variable (can be large)
   - Storage: Currently in ArangoDB (embeddings)

2. **Unstructured Data** (text chunks)
   - Format: JSON chunks array
   - Size: Variable (can be large)
   - Storage: Currently in ArangoDB (embeddings)

3. **Correlation Map** (relationships)
   - Format: JSON correlation map
   - Size: Small to medium
   - Purpose: Links structured columns to unstructured text sections
   - **Storage:** ⚠️ **MAY NOT BE STORED** (needs verification)

**Relationships:**
- Structured ↔ Correlation Map (which columns map to which text)
- Unstructured ↔ Correlation Map (which text sections reference which columns)
- Structured ↔ Unstructured (via correlation map)

**Current Storage:**
- ✅ Structured embeddings: ArangoDB
- ✅ Unstructured embeddings: ArangoDB
- ❓ Correlation map: Unknown (may not be stored)

**Issue:** Correlation map may not be stored, breaking the integrated whole.

---

### 2. Coexistence Blueprint (4 Components) 🔴

**Components:**
1. **Current State Workflow**
   - Workflow definition (JSON)
   - Workflow chart (PNG image)
   - Description

2. **Coexistence State Workflow**
   - Workflow definition (JSON)
   - Workflow chart (PNG image)
   - Description

3. **Transition Roadmap**
   - Phases
   - Milestones
   - Timeline
   - Dependencies

4. **Responsibility Matrix**
   - Roles
   - Responsibilities
   - Integration points

**Relationships:**
- Current State → Coexistence State (transition)
- Both workflows → Roadmap (implementation plan)
- Roadmap → Responsibility Matrix (who does what)
- All components → Blueprint sections (integrated view)

**Current Storage:**
- ❌ **NOT STORED** (only returned in execution result)

**Issue:** Blueprint is a complex integrated whole - cannot be split.

---

### 3. Roadmaps (Multi-Phase) 🟡

**Components:**
- Phases (array of phase objects)
- Milestones
- Timeline
- Resources
- Risks
- Dependencies (between phases)
- Strategic plan
- Visual (PNG image)

**Relationships:**
- Phases → Dependencies (phase A depends on phase B)
- Phases → Milestones (milestones within phases)
- Phases → Resources (resources per phase)
- Phases → Risks (risks per phase)
- All → Strategic plan (overall strategy)

**Current Storage:**
- ❌ **NOT STORED** (only returned in execution result)

**Issue:** Phases are interconnected - dependencies must be preserved.

---

### 4. Solution Synthesis (Multi-Pillar) 🟡

**Components:**
- Content pillar summary
- Insights pillar summary
- Journey pillar summary
- Synthesis report (integrated view)
- Summary visual (PNG image)

**Relationships:**
- All pillars → Synthesis (how they combine)
- Pillars → Visual (visual representation)

**Current Storage:**
- ❌ **NOT STORED** (only returned in execution result)

**Issue:** Synthesis is the integration of pillars - must be stored together.

---

## Storage Strategy: Composite Artifact Pattern

### Pattern Overview

**Principle:** Store main artifact as integrated whole, with component references for large components.

**Structure:**
```
Main Artifact (JSON in GCS)
├── artifact_id
├── artifact_type
├── components (embedded or referenced)
├── relationships (component links)
└── metadata

Large Components (separate files in GCS if needed)
├── component_id
├── component_type
└── reference in main artifact

Metadata (Supabase)
├── artifact_id
├── component_ids[]
├── relationships[]
└── storage_paths[]
```

---

### Strategy 1: Embedded Components (Recommended for Most Cases) ✅

**When to Use:**
- Components are small to medium size (< 10MB total)
- Components are tightly coupled
- Components are always retrieved together

**Storage:**
- Single JSON file in GCS
- All components embedded in main artifact
- Relationships preserved in structure

**Example: Coexistence Blueprint**
```json
{
  "artifact_id": "blueprint_123",
  "artifact_type": "coexistence_blueprint",
  "blueprint_id": "blueprint_123",
  "workflow_id": "workflow_456",
  "current_state": {
    "description": "...",
    "workflow_definition": {...},
    "workflow_chart": {
      "image_base64": "...",
      "storage_path": "artifacts/blueprints/123/current_state_chart.png"
    }
  },
  "coexistence_state": {
    "description": "...",
    "workflow_definition": {...},
    "workflow_chart": {
      "image_base64": "...",
      "storage_path": "artifacts/blueprints/123/coexistence_state_chart.png"
    }
  },
  "roadmap": {...},
  "responsibility_matrix": {...},
  "sections": [...],
  "metadata": {
    "created_date": "...",
    "version": "1.0",
    "tenant_id": "..."
  }
}
```

**Pros:**
- ✅ Simple - single file retrieval
- ✅ Atomic - all components together
- ✅ Relationships preserved in structure
- ✅ No broken references

**Cons:**
- ⚠️ Large files if components are big
- ⚠️ Must retrieve all components even if only one needed

---

### Strategy 2: Referenced Components (For Large Artifacts) 🟡

**When to Use:**
- Components are large (> 10MB total)
- Components may be retrieved independently
- Components are loosely coupled

**Storage:**
- Main artifact JSON in GCS (with component references)
- Large components as separate files in GCS
- Relationships in main artifact structure

**Example: Hybrid Embeddings (if correlation map is large)**
```json
{
  "artifact_id": "hybrid_embeddings_123",
  "artifact_type": "hybrid_embeddings",
  "file_id": "file_456",
  "components": {
    "structured": {
      "component_id": "structured_123",
      "storage_path": "artifacts/hybrid_embeddings/123/structured.json",
      "size": 5242880,
      "format": "json_structured"
    },
    "unstructured": {
      "component_id": "unstructured_123",
      "storage_path": "artifacts/hybrid_embeddings/123/unstructured.json",
      "size": 10485760,
      "format": "json_chunks"
    },
    "correlation_map": {
      "component_id": "correlation_123",
      "storage_path": "artifacts/hybrid_embeddings/123/correlation.json",
      "size": 102400,
      "format": "json"
    }
  },
  "relationships": {
    "structured_to_correlation": {
      "type": "maps_to",
      "mappings": [
        {"column": "customer_id", "text_section": "section_1", "confidence": 0.95}
      ]
    },
    "unstructured_to_correlation": {
      "type": "references",
      "references": [
        {"chunk": "chunk_5", "table": "customers", "confidence": 0.88}
      ]
    }
  },
  "metadata": {
    "created_date": "...",
    "tenant_id": "...",
    "file_id": "file_456"
  }
}
```

**Pros:**
- ✅ Scalable - large components stored separately
- ✅ Efficient - retrieve only needed components
- ✅ Relationships preserved in main artifact

**Cons:**
- ⚠️ More complex - multiple file retrievals
- ⚠️ Risk of broken references
- ⚠️ Must ensure atomic operations

---

### Strategy 3: Graph Storage (For Complex Relationships) 🟢

**When to Use:**
- Very complex relationships
- Relationships need to be queried
- Components are highly interconnected

**Storage:**
- Components in GCS
- Relationships in ArangoDB (graph database)
- Main artifact as manifest

**Example: Complex Blueprint with Many Relationships**
```json
// Main artifact (manifest)
{
  "artifact_id": "blueprint_123",
  "artifact_type": "coexistence_blueprint",
  "components": [
    {"id": "current_state", "type": "workflow", "storage_path": "..."},
    {"id": "coexistence_state", "type": "workflow", "storage_path": "..."},
    {"id": "roadmap", "type": "roadmap", "storage_path": "..."},
    {"id": "responsibility_matrix", "type": "matrix", "storage_path": "..."}
  ],
  "graph_id": "blueprint_123_graph"  // Reference to ArangoDB graph
}
```

**ArangoDB Graph:**
```
Vertices:
- blueprint_123 (artifact)
- current_state (component)
- coexistence_state (component)
- roadmap (component)
- responsibility_matrix (component)

Edges:
- blueprint_123 -> current_state (has_component)
- blueprint_123 -> coexistence_state (has_component)
- current_state -> coexistence_state (transitions_to)
- coexistence_state -> roadmap (implemented_by)
- roadmap -> responsibility_matrix (assigns_responsibilities)
```

**Pros:**
- ✅ Powerful - complex relationship queries
- ✅ Scalable - handles many relationships
- ✅ Flexible - relationships can evolve

**Cons:**
- ⚠️ Complex - requires graph database
- ⚠️ Overkill for simple artifacts
- ⚠️ Additional infrastructure

**Not Recommended for MVP:** Too complex for current needs.

---

## Recommended Implementation

### For Most Artifacts: Strategy 1 (Embedded Components) ✅

**Apply to:**
- Coexistence Blueprints
- Roadmaps
- Solution Synthesis
- POCs

**Implementation:**
```python
async def store_composite_artifact(
    artifact_type: str,
    artifact_data: Dict[str, Any],
    tenant_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store composite artifact with embedded components.
    
    Components are embedded in main artifact JSON.
    Large binary components (visuals) stored separately with references.
    """
    artifact_id = generate_artifact_id()
    
    # Extract large binary components (visuals)
    visuals = {}
    for key, value in artifact_data.items():
        if key.endswith("_visual") and isinstance(value, dict):
            if "image_base64" in value:
                # Store visual separately
                visual_path = f"artifacts/{artifact_type}/{artifact_id}/{key}.png"
                image_bytes = base64.b64decode(value["image_base64"])
                await file_storage.upload_file(visual_path, image_bytes, {...})
                
                # Replace with reference
                visuals[key] = {
                    "storage_path": visual_path,
                    "format": "png"
                }
                artifact_data[key] = visuals[key]
    
    # Store main artifact with embedded components
    artifact_path = f"artifacts/{artifact_type}/{tenant_id}/{artifact_id}.json"
    artifact_json = json.dumps(artifact_data, indent=2)
    await file_storage.upload_file(artifact_path, artifact_json.encode(), {...})
    
    # Store metadata in Supabase
    await supabase.store_artifact_metadata({
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "tenant_id": tenant_id,
        "storage_path": artifact_path,
        "component_count": len(artifact_data.get("components", {})),
        "has_visuals": len(visuals) > 0,
        "visual_paths": list(visuals.keys()),
        **metadata
    })
    
    return {
        "artifact_id": artifact_id,
        "storage_path": artifact_path,
        "visual_paths": visuals
    }
```

---

### For Hybrid Embeddings: Strategy 2 (Referenced Components) 🟡

**Why:** Components are already in ArangoDB, correlation map needs to link them.

**Implementation:**
```python
async def store_hybrid_embeddings(
    file_id: str,
    structured_embeddings: List[Dict],
    unstructured_embeddings: List[Dict],
    correlation_map: Dict[str, Any],
    tenant_id: str
) -> Dict[str, Any]:
    """
    Store hybrid embeddings with correlation map.
    
    Structured and unstructured embeddings already in ArangoDB.
    Correlation map stored separately and links to ArangoDB embeddings.
    """
    artifact_id = f"hybrid_{file_id}"
    
    # Store correlation map
    correlation_path = f"artifacts/hybrid_embeddings/{tenant_id}/{artifact_id}/correlation.json"
    correlation_json = json.dumps(correlation_map, indent=2)
    await file_storage.upload_file(correlation_path, correlation_json.encode(), {...})
    
    # Store manifest linking components
    manifest = {
        "artifact_id": artifact_id,
        "artifact_type": "hybrid_embeddings",
        "file_id": file_id,
        "components": {
            "structured": {
                "storage": "arango",
                "collection": "embeddings",
                "query": {"hybrid_file_id": artifact_id, "hybrid_part_type": "structured"}
            },
            "unstructured": {
                "storage": "arango",
                "collection": "embeddings",
                "query": {"hybrid_file_id": artifact_id, "hybrid_part_type": "unstructured"}
            },
            "correlation_map": {
                "storage": "gcs",
                "storage_path": correlation_path
            }
        },
        "relationships": {
            "structured_to_correlation": "via correlation_map.structured_mappings",
            "unstructured_to_correlation": "via correlation_map.unstructured_mappings"
        }
    }
    
    manifest_path = f"artifacts/hybrid_embeddings/{tenant_id}/{artifact_id}/manifest.json"
    manifest_json = json.dumps(manifest, indent=2)
    await file_storage.upload_file(manifest_path, manifest_json.encode(), {...})
    
    # Store metadata in Supabase
    await supabase.store_artifact_metadata({
        "artifact_id": artifact_id,
        "artifact_type": "hybrid_embeddings",
        "tenant_id": tenant_id,
        "file_id": file_id,
        "storage_path": manifest_path,
        "component_storage": {
            "structured": "arango",
            "unstructured": "arango",
            "correlation_map": "gcs"
        }
    })
    
    return {
        "artifact_id": artifact_id,
        "storage_path": manifest_path
    }
```

---

## Storage Structure

### GCS Bucket Organization

```
GCS Bucket:
├── artifacts/
│   ├── blueprints/
│   │   └── {tenant_id}/
│   │       └── {blueprint_id}.json  (all components embedded)
│   ├── roadmaps/
│   │   └── {tenant_id}/
│   │       └── {roadmap_id}.json  (all components embedded)
│   ├── solutions/
│   │   └── {tenant_id}/
│   │       └── {solution_id}.json  (all components embedded)
│   ├── hybrid_embeddings/
│   │   └── {tenant_id}/
│   │       └── {artifact_id}/
│   │           ├── manifest.json  (component references)
│   │           └── correlation.json  (correlation map)
│   └── visuals/
│       ├── blueprints/
│       │   └── {tenant_id}/
│       │       └── {blueprint_id}/
│       │           ├── current_state_chart.png
│       │           └── coexistence_state_chart.png
│       └── roadmaps/
│           └── {tenant_id}/
│               └── {roadmap_id}_visual.png
```

---

## Retrieval Strategy

### Retrieve Composite Artifact

```python
async def get_composite_artifact(
    artifact_id: str,
    tenant_id: str
) -> Dict[str, Any]:
    """
    Retrieve composite artifact with all components.
    
    For embedded components: Single file retrieval
    For referenced components: Retrieve main + components
    """
    # Get metadata from Supabase
    metadata = await supabase.get_artifact_metadata(artifact_id, tenant_id)
    storage_path = metadata["storage_path"]
    
    # Retrieve main artifact
    artifact_json = await file_storage.download_file(storage_path)
    artifact = json.loads(artifact_json)
    
    # If components are referenced, retrieve them
    if "components" in artifact and isinstance(artifact["components"], dict):
        for component_key, component_ref in artifact["components"].items():
            if component_ref.get("storage") == "gcs":
                component_path = component_ref["storage_path"]
                component_data = await file_storage.download_file(component_path)
                artifact["components"][component_key] = json.loads(component_data)
            elif component_ref.get("storage") == "arango":
                # Query ArangoDB for embeddings
                query = component_ref["query"]
                embeddings = await arango.query_embeddings(query)
                artifact["components"][component_key] = embeddings
    
    # Retrieve visuals if referenced
    for key, value in artifact.items():
        if key.endswith("_visual") and isinstance(value, dict):
            if "storage_path" in value and value.get("format") == "png":
                visual_path = value["storage_path"]
                visual_bytes = await file_storage.download_file(visual_path)
                visual_base64 = base64.b64encode(visual_bytes).decode()
                artifact[key]["image_base64"] = visual_base64
    
    return artifact
```

---

## Implementation Plan

### Phase 1: Composite Artifact Storage Abstraction (2-3 days)

**Create:** `ArtifactStorageAbstraction` with composite support

**Methods:**
- `store_composite_artifact()` - Store with embedded components
- `store_referenced_artifact()` - Store with component references
- `get_composite_artifact()` - Retrieve with all components
- `get_artifact_component()` - Retrieve single component

---

### Phase 2: Blueprint Storage (1 day)

**Update:** `CoexistenceAnalysisService.create_blueprint()`

**Changes:**
- Store blueprint after creation
- All components embedded in single JSON
- Visuals stored separately with references

---

### Phase 3: Roadmap Storage (1 day)

**Update:** `RoadmapGenerationService.generate_roadmap()`

**Changes:**
- Store roadmap after generation
- All phases embedded in single JSON
- Visual stored separately with reference

---

### Phase 4: Solution Synthesis Storage (1 day)

**Update:** `OutcomesOrchestrator._handle_synthesize_outcome()`

**Changes:**
- Store synthesis after creation
- All pillar summaries embedded
- Visual stored separately with reference

---

### Phase 5: Hybrid Embeddings Correlation Map (1-2 days)

**Update:** Hybrid embedding storage

**Changes:**
- Verify correlation map is stored
- Store correlation map if missing
- Link to ArangoDB embeddings via manifest

---

## Other Multi-Component Cases to Consider

### 1. SOP with Visuals 🟡
- SOP document (JSON)
- SOP visual (PNG)
- **Storage:** Embedded (SOP + visual reference)

### 2. Workflow with Visuals 🟡
- Workflow definition (JSON)
- Workflow visual (PNG)
- **Storage:** Embedded (workflow + visual reference)

### 3. POC with Multiple Sections 🟡
- Proposal document
- Financials
- Technical specs
- Visual
- **Storage:** Embedded (all in one JSON)

### 4. Multi-Step Analysis Results 🟢
- Analysis results from multiple steps
- Intermediate results
- Final synthesis
- **Storage:** Embedded (all results together)

---

## Success Criteria

### Phase 1 Complete When:
- ✅ Composite artifact storage abstraction created
- ✅ Can store artifacts with embedded components
- ✅ Can retrieve artifacts with all components

### Phase 2 Complete When:
- ✅ Blueprints stored as integrated wholes
- ✅ Roadmaps stored as integrated wholes
- ✅ Solutions stored as integrated wholes

### Phase 3 Complete When:
- ✅ Hybrid embeddings correlation map stored
- ✅ All multi-component artifacts stored correctly
- ✅ Relationships preserved

---

## Summary

**Problem:** Multi-component artifacts need integrated storage to preserve relationships.

**Solution:** Composite Artifact Pattern
- **Most artifacts:** Embedded components (single JSON file)
- **Large artifacts:** Referenced components (main + separate files)
- **Complex relationships:** Graph storage (if needed, not recommended for MVP)

**Implementation:** 5-7 days to complete.

**Impact:** 🔴 **CRITICAL** - Without this, multi-component artifacts lose their integrated nature.

---

**Last Updated:** January 17, 2026  
**Status:** 🔴 **ARCHITECTURAL GAP - IMPLEMENTATION REQUIRED**
