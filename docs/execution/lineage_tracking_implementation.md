# Complete Lineage Tracking: Implementation Guide

**Status:** Implementation Guide  
**Created:** January 2026  
**Goal:** Implement complete lineage tracking for embeddings and analysis results

---

## Overview

Complete lineage tracking ensures:
- **Embeddings** are traceable to original user file
- **Analysis results** are traceable to guides used
- **Full provenance chain** queryable via Supabase and Data Brain

---

## Implementation Steps

### Step 1: Create Supabase Tables

**File:** `migrations/create_insights_lineage_tables.sql`

**Tables to create:**
1. `parsed_results` - Track parsed results, link to files
2. `embeddings` - Track embeddings, link to files + parsed results
3. `interpretations` - Track interpretations, link to files + embeddings + guides
4. `analyses` - Track analyses, link to files + interpretations + guides
5. `guides` - Store guides (fact patterns + output templates)

**See:** [Insights Lineage Tracking Architecture](../architecture/insights_lineage_tracking.md) for full schema

### Step 2: Content Realm - Track Parsed Results

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**After parsing completes:**
```python
# Store parsed results in GCS
gcs_path = f"tenant/{tenant_id}/parsed/{parsed_result_id}.jsonl"
await file_storage.upload_file(gcs_path, parsed_data)

# Track in Supabase
if supabase_adapter:
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

### Step 3: Content Realm - Track Embeddings

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**After embedding generation:**
```python
# Store embeddings in ArangoDB
arango_collection = "embeddings"
arango_key = embedding_id
await arango_adapter.insert_document(arango_collection, {
    "_key": arango_key,
    "embeddings": embeddings_data,
    "metadata": {...}
})

# Track in Supabase
if supabase_adapter:
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

# Register in Data Brain
if data_brain:
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

### Step 4: Insights Realm - Track Interpretations

**File:** `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`

**After interpretation completes:**
```python
# Store interpretation results in GCS
gcs_path = f"tenant/{tenant_id}/interpretations/{interpretation_id}.json"
await file_storage.upload_file(gcs_path, interpretation_data)

# Track in Supabase
if supabase_adapter:
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

# Register in Data Brain
if data_brain:
    source_refs = [original_file_id, parsed_result_id]
    if embedding_id:
        source_refs.append(embedding_id)
    if guide_id:
        source_refs.append(guide_id)
    
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

### Step 5: Insights Realm - Track Analyses

**File:** `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`

**After analysis completes:**
```python
# Store analysis results in GCS
gcs_path = f"tenant/{tenant_id}/analyses/{analysis_id}.json"
await file_storage.upload_file(gcs_path, analysis_data)

# Track in Supabase
if supabase_adapter:
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

# Register in Data Brain
if data_brain:
    source_refs = [original_file_id, parsed_result_id]
    if interpretation_id:
        source_refs.append(interpretation_id)
    if guide_id:
        source_refs.append(guide_id)
    
    await data_brain.register_reference(
        reference_id=analysis_id,
        reference_type="analysis",
        storage_location=f"gcs://{gcs_path}",
        metadata={
            "file_id": original_file_id,
            "parsed_result_id": parsed_result_id,
            "interpretation_id": interpretation_id,
            "guide_id": guide_id,
            "analysis_type": analysis_type
        },
        execution_id=context.execution_id
    )
    
    # Track provenance
    await data_brain.track_provenance(
        reference_id=analysis_id,
        execution_id=context.execution_id,
        operation="created",
        source_reference_ids=source_refs,
        metadata={
            "operation": "analysis",
            "type": analysis_type,
            "guide_id": guide_id
        }
    )
```

### Step 6: Guide Registry Integration

**File:** `symphainy_platform/civic_systems/platform_sdk/guide_registry.py`

**When guide registered:**
```python
# Store guide in Supabase
await supabase_adapter.insert_document("guides", {
    "id": generate_uuid(),
    "tenant_id": tenant_id,
    "guide_id": guide_id,
    "name": name,
    "description": description,
    "type": "default" | "user_uploaded" | "user_created",
    "fact_pattern": fact_pattern,
    "output_template": output_template,
    "version": "1.0",
    "created_by": user_id  # If user_created
})
```

---

## E2E Test Implementation

### Test: Complete Lineage Chain Verification

**File:** `tests/integration/realms/insights/test_insights_lineage_tracking.py`

```python
@pytest.mark.asyncio
async def test_complete_lineage_chain(
    self,
    insights_realm_setup
):
    """Test complete lineage chain from file → parse → embed → interpret → analyze."""
    
    # 1. Upload file
    file_result = await content_realm.handle_intent(upload_intent, context)
    file_id = file_result["artifacts"]["file_id"]
    
    # 2. Parse file
    parse_result = await content_realm.handle_intent(parse_intent, context)
    parsed_result_id = parse_result["artifacts"]["parsed_result_id"]
    
    # Verify parsed_results table entry
    parsed_result_record = await supabase_adapter.get_document(
        "parsed_results",
        {"parsed_result_id": parsed_result_id}
    )
    assert parsed_result_record is not None
    assert parsed_result_record["file_id"] == file_id
    
    # 3. Generate embeddings
    embed_result = await content_realm.handle_intent(embed_intent, context)
    embedding_id = embed_result["artifacts"]["embedding_id"]
    
    # Verify embeddings table entry
    embedding_record = await supabase_adapter.get_document(
        "embeddings",
        {"embedding_id": embedding_id}
    )
    assert embedding_record is not None
    assert embedding_record["file_id"] == file_id
    assert embedding_record["parsed_result_id"] == parsed_result_id
    
    # 4. Interpret with guide
    guide_id = "pso_default_guide"
    interpret_result = await insights_realm.handle_intent(interpret_intent, context)
    interpretation_id = interpret_result["artifacts"]["interpretation_id"]
    
    # Verify interpretations table entry
    interpretation_record = await supabase_adapter.get_document(
        "interpretations",
        {"interpretation_id": interpretation_id}
    )
    assert interpretation_record is not None
    assert interpretation_record["file_id"] == file_id
    assert interpretation_record["parsed_result_id"] == parsed_result_id
    assert interpretation_record["embedding_id"] == embedding_id
    assert interpretation_record["guide_id"] == guide_id
    
    # 5. Analyze data
    analyze_result = await insights_realm.handle_intent(analyze_intent, context)
    analysis_id = analyze_result["artifacts"]["analysis_id"]
    
    # Verify analyses table entry
    analysis_record = await supabase_adapter.get_document(
        "analyses",
        {"analysis_id": analysis_id}
    )
    assert analysis_record is not None
    assert analysis_record["file_id"] == file_id
    assert analysis_record["parsed_result_id"] == parsed_result_id
    assert analysis_record["interpretation_id"] == interpretation_id
    assert analysis_record["guide_id"] == guide_id
    
    # 6. Query complete lineage chain via Supabase
    lineage_query = """
    SELECT 
        f.id as file_id,
        f.ui_name as file_name,
        pr.parsed_result_id,
        e.embedding_id,
        i.interpretation_id,
        g.name as guide_name,
        a.analysis_id
    FROM files f
    LEFT JOIN parsed_results pr ON pr.file_id = f.id
    LEFT JOIN embeddings e ON e.file_id = f.id
    LEFT JOIN interpretations i ON i.file_id = f.id
    LEFT JOIN guides g ON g.id = i.guide_id
    LEFT JOIN analyses a ON a.file_id = f.id
    WHERE f.id = :file_id
    """
    lineage_result = await supabase_adapter.execute_query(lineage_query, {"file_id": file_id})
    assert len(lineage_result) > 0
    assert lineage_result[0]["file_id"] == file_id
    assert lineage_result[0]["parsed_result_id"] == parsed_result_id
    assert lineage_result[0]["embedding_id"] == embedding_id
    assert lineage_result[0]["interpretation_id"] == interpretation_id
    assert lineage_result[0]["guide_name"] == "PSO Permit Guide"
    assert lineage_result[0]["analysis_id"] == analysis_id
    
    # 7. Query complete lineage chain via Data Brain
    embedding_ref = await data_brain.get_reference(embedding_id)
    assert embedding_ref is not None
    assert embedding_ref.reference_type == "embedding"
    
    interpretation_ref = await data_brain.get_reference(interpretation_id)
    assert interpretation_ref is not None
    assert interpretation_ref.reference_type == "interpretation"
    
    # 8. Verify provenance chain
    embedding_provenance = await data_brain.get_provenance(embedding_id)
    assert len(embedding_provenance) > 0
    assert file_id in embedding_provenance[0].source_reference_ids
    
    interpretation_provenance = await data_brain.get_provenance(interpretation_id)
    assert len(interpretation_provenance) > 0
    assert embedding_id in interpretation_provenance[0].source_reference_ids
    assert guide_id in interpretation_provenance[0].metadata.get("guide_id")
```

---

## Success Criteria

✅ **Complete Lineage:**
- Every embedding links to file + parsed results in Supabase
- Every interpretation links to embeddings + guide in Supabase
- Every analysis links to interpretation + guide in Supabase
- Full chain queryable via Supabase

✅ **Data Brain Integration:**
- All references registered in Data Brain
- All provenance tracked in Data Brain
- Full lineage queryable via Data Brain

✅ **Traceability:**
- Can trace embedding back to original file
- Can trace interpretation back to guide used
- Can trace analysis back to guide used
- Full provenance chain complete

✅ **Reproducibility:**
- Can recreate any analysis
- Know exactly what guide was used
- Know exactly what embeddings were used
