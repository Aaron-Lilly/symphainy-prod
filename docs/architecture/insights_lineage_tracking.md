# Insights Realm: Complete Lineage Tracking

**Status:** Architectural Design  
**Created:** January 2026  
**Goal:** Ensure semantic embeddings and analysis results are fully traceable back to source files and guides

---

## Executive Summary

Complete lineage tracking ensures:
- **Embeddings** are traceable to original user file
- **Analysis results** are traceable to guides used
- **Full provenance chain** from file → parse → embed → interpret → analyze
- **Reproducibility** - can recreate any analysis
- **Explainability** - can explain why we got these results

---

## Lineage Chain

### Complete Chain

```
User File (GCS)
  ↓
File Metadata (Supabase: files table)
  ↓
Parsed Results (GCS)
  ↓
Parsed Results Metadata (Supabase: parsed_results table, links to file)
  ↓
Embeddings (ArangoDB)
  ↓
Embedding References (Supabase: embeddings table, links to parsed_result + file)
  ↓
Interpretation Results (GCS)
  ↓
Interpretation Metadata (Supabase: interpretations table, links to embeddings + guide)
  ↓
Analysis Results (GCS)
  ↓
Analysis Metadata (Supabase: analyses table, links to interpretation + guide)
```

---

## Data Model

### Supabase Tables

#### 1. `parsed_results` Table

**Purpose:** Track parsed results and link to source file

**Schema:**
```sql
CREATE TABLE parsed_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    file_id UUID NOT NULL REFERENCES files(id),
    parsed_result_id TEXT NOT NULL,  -- Reference ID
    gcs_path TEXT NOT NULL,  -- Where parsed results stored in GCS
    parser_type TEXT NOT NULL,  -- "mainframe", "csv", "json", "pdf", etc.
    parser_config JSONB,  -- Parser configuration used
    record_count INTEGER,
    status TEXT,  -- "success", "partial", "failed"
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, parsed_result_id)
);

CREATE INDEX idx_parsed_results_file_id ON parsed_results(file_id);
CREATE INDEX idx_parsed_results_tenant_id ON parsed_results(tenant_id);
```

**Lineage:**
- `file_id` → links to original file
- `parsed_result_id` → reference to parsed results in GCS

#### 2. `embeddings` Table

**Purpose:** Track embeddings and link to parsed results + source file

**Schema:**
```sql
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    file_id UUID NOT NULL REFERENCES files(id),
    parsed_result_id UUID NOT NULL REFERENCES parsed_results(id),
    embedding_id TEXT NOT NULL,  -- Reference ID for embedding in ArangoDB
    arango_collection TEXT NOT NULL,  -- ArangoDB collection name
    arango_key TEXT NOT NULL,  -- ArangoDB document key
    embedding_count INTEGER,  -- Number of embeddings generated
    model_name TEXT,  -- Embedding model used
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, embedding_id)
);

CREATE INDEX idx_embeddings_file_id ON embeddings(file_id);
CREATE INDEX idx_embeddings_parsed_result_id ON embeddings(parsed_result_id);
CREATE INDEX idx_embeddings_tenant_id ON embeddings(tenant_id);
```

**Lineage:**
- `file_id` → links to original file
- `parsed_result_id` → links to parsed results
- `embedding_id` → reference to embeddings in ArangoDB
- **Many:1 relationship** - Multiple embeddings from one file

#### 3. `interpretations` Table

**Purpose:** Track interpretation results and link to embeddings + guide

**Schema:**
```sql
CREATE TABLE interpretations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    file_id UUID NOT NULL REFERENCES files(id),
    parsed_result_id UUID NOT NULL REFERENCES parsed_results(id),
    embedding_id UUID REFERENCES embeddings(id),  -- Optional (for guided discovery)
    guide_id UUID,  -- NULL for self-discovery, guide_id for guided discovery
    interpretation_id TEXT NOT NULL,
    gcs_path TEXT NOT NULL,  -- Where interpretation results stored in GCS
    interpretation_type TEXT NOT NULL,  -- "self_discovery" | "guided"
    matched_entities_count INTEGER,
    unmatched_data_count INTEGER,
    missing_expected_count INTEGER,
    confidence_score FLOAT,
    coverage_score FLOAT,  -- How much of guide was matched
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, interpretation_id)
);

CREATE INDEX idx_interpretations_file_id ON interpretations(file_id);
CREATE INDEX idx_interpretations_parsed_result_id ON interpretations(parsed_result_id);
CREATE INDEX idx_interpretations_embedding_id ON interpretations(embedding_id);
CREATE INDEX idx_interpretations_guide_id ON interpretations(guide_id);
CREATE INDEX idx_interpretations_tenant_id ON interpretations(tenant_id);
```

**Lineage:**
- `file_id` → links to original file
- `parsed_result_id` → links to parsed results
- `embedding_id` → links to embeddings (if used)
- `guide_id` → links to guide used (if guided discovery)

#### 4. `analyses` Table

**Purpose:** Track analysis results and link to interpretation + guide

**Schema:**
```sql
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    file_id UUID NOT NULL REFERENCES files(id),
    parsed_result_id UUID NOT NULL REFERENCES parsed_results(id),
    interpretation_id UUID REFERENCES interpretations(id),  -- Optional
    guide_id UUID,  -- Guide used for analysis (if applicable)
    analysis_id TEXT NOT NULL,
    gcs_path TEXT NOT NULL,  -- Where analysis results stored in GCS
    analysis_type TEXT NOT NULL,  -- "structured" | "unstructured" | "quality"
    analysis_subtype TEXT,  -- "statistical", "pattern", "semantic", "sentiment", etc.
    deep_dive BOOLEAN DEFAULT FALSE,  -- Whether Insights Liaison Agent was used
    agent_session_id TEXT,  -- If deep_dive=true, link to agent session
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, analysis_id)
);

CREATE INDEX idx_analyses_file_id ON analyses(file_id);
CREATE INDEX idx_analyses_parsed_result_id ON analyses(parsed_result_id);
CREATE INDEX idx_analyses_interpretation_id ON analyses(interpretation_id);
CREATE INDEX idx_analyses_guide_id ON analyses(guide_id);
CREATE INDEX idx_analyses_tenant_id ON analyses(tenant_id);
```

**Lineage:**
- `file_id` → links to original file
- `parsed_result_id` → links to parsed results
- `interpretation_id` → links to interpretation (if used)
- `guide_id` → links to guide used (if applicable)

#### 5. `guides` Table

**Purpose:** Store guides (fact patterns + output templates)

**Schema:**
```sql
CREATE TABLE guides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    guide_id TEXT NOT NULL,  -- Reference ID
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,  -- "default" | "user_uploaded" | "user_created"
    fact_pattern JSONB NOT NULL,  -- Entities, relationships, attributes
    output_template JSONB NOT NULL,  -- Output structure template
    version TEXT DEFAULT "1.0",
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID,  -- User who created (if user_created)
    
    UNIQUE(tenant_id, guide_id)
);

CREATE INDEX idx_guides_tenant_id ON guides(tenant_id);
CREATE INDEX idx_guides_type ON guides(type);
```

---

## Implementation

### Content Realm: Track Parsed Results

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**When parsing completes:**
```python
# After parsing
parsed_result_id = generate_event_id()
gcs_path = f"tenant/{tenant_id}/parsed/{parsed_result_id}.jsonl"

# Store parsed results in GCS
await file_storage.upload_file(gcs_path, parsed_data)

# Track in Supabase
await supabase_adapter.insert_document("parsed_results", {
    "id": generate_uuid(),
    "tenant_id": tenant_id,
    "file_id": original_file_id,  # Link to original file
    "parsed_result_id": parsed_result_id,
    "gcs_path": gcs_path,
    "parser_type": parser_type,
    "parser_config": parser_config,
    "record_count": len(parsed_records),
    "status": "success"
})
```

### Content Realm: Track Embeddings

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**When embeddings generated:**
```python
# After embedding generation
embedding_id = generate_event_id()

# Store embeddings in ArangoDB
arango_collection = "embeddings"
arango_key = embedding_id
await arango_adapter.insert_document(arango_collection, {
    "_key": arango_key,
    "embeddings": embeddings_data,
    "metadata": {...}
})

# Track in Supabase
await supabase_adapter.insert_document("embeddings", {
    "id": generate_uuid(),
    "tenant_id": tenant_id,
    "file_id": original_file_id,  # Link to original file
    "parsed_result_id": parsed_result_id,  # Link to parsed results
    "embedding_id": embedding_id,
    "arango_collection": arango_collection,
    "arango_key": arango_key,
    "embedding_count": len(embeddings_data),
    "model_name": model_name
})
```

### Insights Realm: Track Interpretations

**File:** `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`

**When interpretation completes:**
```python
# After interpretation
interpretation_id = generate_event_id()
gcs_path = f"tenant/{tenant_id}/interpretations/{interpretation_id}.json"

# Store interpretation results in GCS
await file_storage.upload_file(gcs_path, interpretation_data)

# Track in Supabase
await supabase_adapter.insert_document("interpretations", {
    "id": generate_uuid(),
    "tenant_id": tenant_id,
    "file_id": original_file_id,  # Link to original file
    "parsed_result_id": parsed_result_id,  # Link to parsed results
    "embedding_id": embedding_id,  # Link to embeddings (if used)
    "guide_id": guide_id,  # Link to guide (if guided discovery)
    "interpretation_id": interpretation_id,
    "gcs_path": gcs_path,
    "interpretation_type": "self_discovery" | "guided",
    "matched_entities_count": len(matched_entities),
    "unmatched_data_count": len(unmatched_data),
    "missing_expected_count": len(missing_expected),
    "confidence_score": confidence_score,
    "coverage_score": coverage_score
})
```

### Insights Realm: Track Analyses

**File:** `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`

**When analysis completes:**
```python
# After analysis
analysis_id = generate_event_id()
gcs_path = f"tenant/{tenant_id}/analyses/{analysis_id}.json"

# Store analysis results in GCS
await file_storage.upload_file(gcs_path, analysis_data)

# Track in Supabase
await supabase_adapter.insert_document("analyses", {
    "id": generate_uuid(),
    "tenant_id": tenant_id,
    "file_id": original_file_id,  # Link to original file
    "parsed_result_id": parsed_result_id,  # Link to parsed results
    "interpretation_id": interpretation_id,  # Link to interpretation (if used)
    "guide_id": guide_id,  # Link to guide (if used)
    "analysis_id": analysis_id,
    "gcs_path": gcs_path,
    "analysis_type": "structured" | "unstructured" | "quality",
    "analysis_subtype": "statistical" | "pattern" | "semantic" | etc.,
    "deep_dive": deep_dive,
    "agent_session_id": agent_session_id  # If deep_dive=true
})
```

---

## Querying Lineage

### Get Full Lineage for File

**Query:**
```sql
-- Get complete lineage for a file
SELECT 
    f.id as file_id,
    f.ui_name as file_name,
    pr.id as parsed_result_id,
    pr.parser_type,
    e.id as embedding_id,
    e.embedding_count,
    i.id as interpretation_id,
    i.interpretation_type,
    g.name as guide_name,
    a.id as analysis_id,
    a.analysis_type
FROM files f
LEFT JOIN parsed_results pr ON pr.file_id = f.id
LEFT JOIN embeddings e ON e.file_id = f.id
LEFT JOIN interpretations i ON i.file_id = f.id
LEFT JOIN guides g ON g.id = i.guide_id
LEFT JOIN analyses a ON a.file_id = f.id
WHERE f.id = :file_id
ORDER BY f.created_at, pr.created_at, e.created_at, i.created_at, a.created_at;
```

### Get All Embeddings for File

**Query:**
```sql
-- Get all embeddings for a file
SELECT 
    e.embedding_id,
    e.arango_collection,
    e.arango_key,
    e.embedding_count,
    pr.parsed_result_id,
    pr.parser_type
FROM embeddings e
JOIN parsed_results pr ON pr.id = e.parsed_result_id
WHERE e.file_id = :file_id;
```

### Get All Interpretations Using Guide

**Query:**
```sql
-- Get all interpretations that used a specific guide
SELECT 
    i.interpretation_id,
    i.interpretation_type,
    i.confidence_score,
    i.coverage_score,
    f.ui_name as file_name,
    pr.parsed_result_id
FROM interpretations i
JOIN files f ON f.id = i.file_id
JOIN parsed_results pr ON pr.id = i.parsed_result_id
WHERE i.guide_id = :guide_id;
```

### Get Analysis Lineage

**Query:**
```sql
-- Get complete lineage for an analysis
SELECT 
    a.analysis_id,
    a.analysis_type,
    a.analysis_subtype,
    i.interpretation_id,
    i.interpretation_type,
    g.name as guide_name,
    e.embedding_id,
    pr.parsed_result_id,
    f.ui_name as file_name
FROM analyses a
JOIN files f ON f.id = a.file_id
LEFT JOIN parsed_results pr ON pr.id = a.parsed_result_id
LEFT JOIN embeddings e ON e.id = a.interpretation_id
LEFT JOIN interpretations i ON i.id = a.interpretation_id
LEFT JOIN guides g ON g.id = a.guide_id
WHERE a.analysis_id = :analysis_id;
```

---

## Data Brain Integration

### Register Embedding Reference

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**After embedding generation:**
```python
# Register embedding reference in Data Brain
await data_brain.register_reference(
    reference_id=embedding_id,
    reference_type="embedding",
    storage_location=f"arangodb://{arango_collection}/{arango_key}",
    metadata={
        "file_id": original_file_id,
        "parsed_result_id": parsed_result_id,
        "embedding_count": len(embeddings_data),
        "model_name": model_name
    },
    execution_id=context.execution_id
)

# Track provenance
await data_brain.track_provenance(
    reference_id=embedding_id,
    execution_id=context.execution_id,
    operation="created",
    source_reference_ids=[original_file_id, parsed_result_id],
    metadata={
        "operation": "embedding_generation",
        "model": model_name
    }
)
```

### Register Interpretation Reference

**File:** `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`

**After interpretation:**
```python
# Register interpretation reference in Data Brain
await data_brain.register_reference(
    reference_id=interpretation_id,
    reference_type="interpretation",
    storage_location=f"gcs://{gcs_path}",
    metadata={
        "file_id": original_file_id,
        "parsed_result_id": parsed_result_id,
        "embedding_id": embedding_id,
        "guide_id": guide_id,
        "interpretation_type": interpretation_type
    },
    execution_id=context.execution_id
)

# Track provenance
source_refs = [original_file_id, parsed_result_id]
if embedding_id:
    source_refs.append(embedding_id)
if guide_id:
    source_refs.append(guide_id)

await data_brain.track_provenance(
    reference_id=interpretation_id,
    execution_id=context.execution_id,
    operation="created",
    source_reference_ids=source_refs,
    metadata={
        "operation": "interpretation",
        "type": interpretation_type,
        "guide_id": guide_id
    }
)
```

---

## E2E Test: Complete Lineage Verification

### Test: `test_complete_lineage_chain`

**What it validates:**
- File → Parsed Results → Embeddings → Interpretation → Analysis
- All links present in Supabase
- All references registered in Data Brain
- Full provenance chain queryable

**Test Steps:**
1. Upload file
2. Parse file
3. Generate embeddings
4. Interpret with guide
5. Analyze data
6. Query complete lineage chain
7. Verify all links present
8. Verify can trace back to original file
9. Verify can trace back to guide used

---

## Benefits

✅ **Complete Traceability:**
- Every embedding traceable to original file
- Every analysis traceable to guide used
- Full provenance chain queryable

✅ **Reproducibility:**
- Can recreate any analysis
- Know exactly what guide was used
- Know exactly what embeddings were used

✅ **Explainability:**
- Can explain why we got these results
- Can show what guide was used
- Can show what data was matched/unmatched

✅ **Auditability:**
- Full audit trail of all operations
- Know who created guides
- Know when analyses were run

---

## Implementation Priority

### Phase 1: Supabase Tables (Week 1)
1. Create `parsed_results` table
2. Create `embeddings` table
3. Create `interpretations` table
4. Create `analyses` table
5. Create `guides` table

### Phase 2: Content Realm Integration (Week 1-2)
6. Track parsed results in Supabase
7. Track embeddings in Supabase
8. Register references in Data Brain
9. Track provenance in Data Brain

### Phase 3: Insights Realm Integration (Week 2-3)
10. Track interpretations in Supabase
11. Track analyses in Supabase
12. Link to guides used
13. Register references in Data Brain
14. Track provenance in Data Brain

### Phase 4: Query & Verification (Week 3)
15. Implement lineage query functions
16. E2E test for complete lineage chain
17. Verify all links present

---

## Success Criteria

✅ **Complete Lineage:**
- Every embedding links to file + parsed results
- Every interpretation links to embeddings + guide
- Every analysis links to interpretation + guide
- Full chain queryable

✅ **Data Brain Integration:**
- All references registered
- All provenance tracked
- Full lineage queryable via Data Brain

✅ **Reproducibility:**
- Can recreate any analysis
- Know exactly what was used
