# Phase 2b: Supabase Artifact Index Implementation Guide

**Date:** January 26, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Prerequisites:** Phase 1 (Artifact Registry) and Phase 2 (Runtime API) complete

---

## Summary

This guide implements the Supabase artifact index table and integrates it with our artifact registration flow. This enables the `/api/artifact/list` endpoint for UI dropdowns.

---

## Step 1: Create `artifact_index` Table

**File:** `docs/supabase_tablesandschemas/artifact_index_migration.sql`

**Action:**
1. Copy the migration script into Supabase SQL Editor
2. Execute the script
3. Verify table and indexes are created

**Verification:**
```sql
-- Check table exists
SELECT * FROM information_schema.tables 
WHERE table_name = 'artifact_index';

-- Check indexes
SELECT indexname FROM pg_indexes 
WHERE tablename = 'artifact_index';
```

---

## Step 2: Update Artifact Registration (Dual-Write Pattern)

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**Changes Needed:**

After each artifact registration in State Surface, also write to `artifact_index`:

```python
# After registering artifact in State Surface
artifact_registered = await context.state_surface.register_artifact(...)

if artifact_registered:
    # Also write to artifact_index (discovery layer)
    if self.public_works and hasattr(self.public_works, 'registry_abstraction'):
        registry = self.public_works.registry_abstraction
        if registry:
            try:
                await registry.create_record("artifact_index", {
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type,
                    "tenant_id": tenant_id,
                    "lifecycle_state": lifecycle_state,
                    "semantic_descriptor": semantic_descriptor.to_dict(),
                    "produced_by": {
                        "intent": produced_by.intent,
                        "execution_id": produced_by.execution_id
                    },
                    "parent_artifacts": parent_artifacts
                })
                self.logger.debug(f"Artifact indexed: {artifact_id}")
            except Exception as e:
                # Don't fail if indexing fails (State Surface is authoritative)
                self.logger.warning(f"Failed to index artifact {artifact_id}: {e}")
```

**Locations to Update:**
1. `_handle_ingest_file()` - After file artifact registration
2. `_handle_parse_content()` - After parsed_content artifact registration
3. `_handle_extract_embeddings()` - After embeddings artifact registration

---

## Step 3: Implement RegistryAbstraction.list_artifacts()

**File:** `symphainy_platform/foundations/public_works/abstractions/registry_abstraction.py`

**Add Method:**
```python
async def list_artifacts(
    self,
    tenant_id: str,
    artifact_type: Optional[str] = None,
    lifecycle_state: Optional[str] = None,
    eligible_for: Optional[str] = None,  # Next intent
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List artifacts from artifact_index (discovery/exploration).
    
    Args:
        tenant_id: Tenant identifier
        artifact_type: Filter by artifact type
        lifecycle_state: Filter by lifecycle state (default: READY)
        eligible_for: Filter artifacts eligible for next intent
        limit: Pagination limit
        offset: Pagination offset
    
    Returns:
        Dict with 'artifacts' list and 'total' count
    """
    try:
        # Build query
        query = self._client.table("artifact_index").select("*")
        query = query.eq("tenant_id", tenant_id)
        
        # Default to READY if lifecycle_state not specified
        if lifecycle_state:
            query = query.eq("lifecycle_state", lifecycle_state)
        else:
            query = query.in_("lifecycle_state", ["READY", "ARCHIVED"])
        
        if artifact_type:
            query = query.eq("artifact_type", artifact_type)
        
        # TODO: Implement eligible_for filtering
        # This requires intent eligibility rules (future enhancement)
        if eligible_for:
            # For MVP, we can filter by artifact_type based on intent requirements
            # Example: "extract_embeddings" requires "parsed_content" artifacts
            eligible_types = self._get_eligible_artifact_types(eligible_for)
            if eligible_types:
                query = query.in_("artifact_type", eligible_types)
        
        # Get total count
        count_query = query
        count_result = count_query.execute()
        total = len(count_result.data) if count_result.data else 0
        
        # Apply pagination
        query = query.order("created_at", desc=True).limit(limit).offset(offset)
        
        # Execute query
        result = query.execute()
        
        return {
            "artifacts": result.data or [],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        self.logger.error(f"Failed to list artifacts: {e}", exc_info=True)
        return {
            "artifacts": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }

def _get_eligible_artifact_types(self, intent_type: str) -> List[str]:
    """
    Get artifact types eligible for a given intent.
    
    MVP: Hard-coded mapping
    Future: Dynamic eligibility rules
    """
    eligibility_map = {
        "parse_content": ["file"],
        "extract_embeddings": ["parsed_content"],
        "create_deterministic_embeddings": ["parsed_content"],
        "hydrate_semantic_profile": ["parsed_content"],
        "save_materialization": ["file", "parsed_content", "embeddings"]
    }
    return eligibility_map.get(intent_type, [])
```

---

## Step 4: Update Runtime API list_artifacts()

**File:** `symphainy_platform/runtime/runtime_api.py`

**Update Method:**
```python
async def list_artifacts(
    self,
    request: ArtifactListRequest
) -> ArtifactListResponse:
    """
    List artifacts for UI dropdowns (discovery/indexing via Supabase).
    """
    try:
        if not self.registry_abstraction:
            self.logger.warning("Registry abstraction not available")
            return ArtifactListResponse(
                artifacts=[],
                total=0,
                limit=request.limit or 100,
                offset=request.offset or 0
            )
        
        # Query artifact_index via RegistryAbstraction
        result = await self.registry_abstraction.list_artifacts(
            tenant_id=request.tenant_id,
            artifact_type=request.artifact_type,
            lifecycle_state=request.lifecycle_state or "READY",
            eligible_for=request.eligible_for,
            limit=request.limit or 100,
            offset=request.offset or 0
        )
        
        # Convert to response format
        artifacts = [
            ArtifactListItem(
                artifact_id=item["artifact_id"],
                artifact_type=item["artifact_type"],
                lifecycle_state=item["lifecycle_state"],
                semantic_descriptor=item["semantic_descriptor"],
                created_at=item["created_at"],
                updated_at=item["updated_at"]
            )
            for item in result.get("artifacts", [])
        ]
        
        return ArtifactListResponse(
            artifacts=artifacts,
            total=result.get("total", 0),
            limit=result.get("limit", request.limit or 100),
            offset=result.get("offset", request.offset or 0)
        )
        
    except Exception as e:
        self.logger.error(f"Failed to list artifacts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
```

---

## Step 5: Test End-to-End

### Test 1: Artifact Registration → Indexing

```python
# Submit ingest_file intent
result = await submit_intent({
    "intent_type": "ingest_file",
    "tenant_id": "test_tenant",
    "session_id": "test_session",
    "parameters": {...}
})

# Verify artifact in State Surface
artifact = await state_surface.resolve_artifact(
    artifact_id=file_id,
    artifact_type="file",
    tenant_id="test_tenant"
)
assert artifact is not None

# Verify artifact in artifact_index
indexed = await registry_abstraction.query_records(
    table="artifact_index",
    filters={"artifact_id": file_id}
)
assert len(indexed) == 1
```

### Test 2: Artifact Listing

```python
# List artifacts
response = await runtime_api.list_artifacts(ArtifactListRequest(
    tenant_id="test_tenant",
    artifact_type="file",
    lifecycle_state="READY"
))

assert len(response.artifacts) > 0
assert response.artifacts[0].artifact_type == "file"
```

### Test 3: Eligibility Filtering

```python
# List artifacts eligible for parse_content
response = await runtime_api.list_artifacts(ArtifactListRequest(
    tenant_id="test_tenant",
    eligible_for="parse_content"
))

# Should return only "file" artifacts
assert all(a.artifact_type == "file" for a in response.artifacts)
```

---

## Step 6: Update Lifecycle State in Index

**When updating artifact lifecycle in State Surface, also update artifact_index:**

```python
# After updating lifecycle in State Surface
await context.state_surface.update_artifact_lifecycle(
    artifact_id=artifact_id,
    tenant_id=tenant_id,
    new_state=LifecycleState.READY.value
)

# Also update artifact_index
if self.public_works and hasattr(self.public_works, 'registry_abstraction'):
    registry = self.public_works.registry_abstraction
    if registry:
        try:
            await registry.update_record(
                table="artifact_index",
                record_id=artifact_id,
                updates={
                    "lifecycle_state": LifecycleState.READY.value,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            self.logger.warning(f"Failed to update artifact_index lifecycle: {e}")
```

---

## Success Criteria

### ✅ Phase 2b Complete When:

1. ✅ `artifact_index` table created in Supabase
2. ✅ Artifact registration writes to both State Surface and artifact_index
3. ✅ `RegistryAbstraction.list_artifacts()` implemented
4. ✅ `RuntimeAPI.list_artifacts()` uses RegistryAbstraction
5. ✅ `/api/artifact/list` endpoint functional
6. ✅ End-to-end tests pass

---

## Next Steps (Phase 3: Frontend Integration)

1. Add `listArtifacts()` to `ContentAPIManager`
2. Migrate UI dropdowns to use `listArtifacts()`
3. Test UI dropdowns with real data

---

## Notes

- **State Surface is authoritative** - artifact_index is for discovery only
- **Dual-write pattern** - write to both during migration
- **Eligibility filtering** - MVP uses hard-coded mapping, future: dynamic rules
- **Backward compatibility** - keep `project_files` during migration
