# Architectural Fixes Analysis

**Status:** Analysis & Recommendations  
**Date:** January 2026  
**Context:** Review of test fixes to align with platform architecture

---

## Executive Summary

After reviewing the platform architecture and FMS/Data Lineage best practices, we've identified four critical architectural issues with the recent test fixes:

1. **`ingest_file` doing too much** - Should only handle new file uploads from users
2. **Inconsistent naming** - Need to standardize on `parsed_file_id` vs `parsed_result_id`
3. **Journey Realm workflow creation** - Should use embeddings from parsed results, not raw files
4. **Supabase adapter availability** - Should be available in test environment

---

## Issue 1: `ingest_file` Intent Scope Violation

### Problem

The `ingest_file` intent was modified to accept both:
- Mode 1: New file uploads (`file_content` hex-encoded)
- Mode 2: Existing file registration (`file_id` + `file_path`)

**This violates the architecture principle:**
- `ingest_file` should **only** handle getting files from users into our ecosystem
- If files already exist in our system, we shouldn't be "ingesting" them again
- This creates circular logic: bringing files that already exist in "our world" into "our world"

### Root Cause

Tests were trying to use `ingest_file` to register files that were already uploaded via `TestDataSeeder`. This is the wrong approach.

### Correct Architecture

According to the platform architecture:

1. **`ingest_file`** - Only for new file uploads from users
   - Accepts `file_content` (hex-encoded bytes)
   - Uploads to GCS via `FileStorageAbstraction`
   - Creates entry in Supabase `files` table
   - Returns `file_id` and `file_reference`

2. **For existing files** - Use different approach:
   - If files come from EDI/API adapters, those adapters should handle ingestion
   - If files are already in GCS, reference them via `file_id` directly
   - Tests should use `file_id` directly in subsequent intents (parse, analyze, etc.)

### Solution

**Revert `ingest_file` to only handle new uploads:**

```python
async def _handle_ingest_file(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle ingest_file intent - upload NEW file from user to GCS and Supabase.
    
    Intent parameters:
    - file_content: bytes (hex-encoded for JSON transport) - REQUIRED
    - ui_name: str (user-friendly filename) - REQUIRED
    - file_type: str (e.g., "pdf", "csv")
    - mime_type: str (e.g., "application/pdf")
    - filename: str (original filename)
    - user_id: str (optional, from context if not provided)
    """
    # Extract file content (hex-encoded) - REQUIRED
    file_content_hex = intent.parameters.get("file_content")
    if not file_content_hex:
        raise ValueError("file_content is required for ingest_file intent")
    
    # ... rest of upload logic
```

**Update tests to use `file_id` directly:**

Tests should:
1. Use `TestDataSeeder` to upload files (this creates `file_id`)
2. Use `file_id` directly in subsequent intents (`parse_content`, `assess_data_quality`, etc.)
3. **Do NOT** call `ingest_file` for files that already exist

---

## Issue 2: Inconsistent Naming - `parsed_file_id` vs `parsed_result_id`

### Problem

The codebase uses both:
- `parsed_file_id` (in some places)
- `parsed_result_id` (in lineage tracking tables)

This creates confusion and potential bugs.

### Root Cause

The lineage tracking architecture uses `parsed_result_id` (as defined in `insights_lineage_tracking.md`), but some orchestrators use `parsed_file_id`.

### Correct Architecture

According to `insights_lineage_tracking.md`:

- **Supabase table:** `parsed_results` has column `parsed_result_id` (TEXT, reference ID)
- **Internal reference:** Should use `parsed_result_id` consistently
- **User-friendly display:** Should track `ui_name` from original file for display

### Solution

**Standardize on `parsed_result_id`:**

1. **Update all orchestrators** to use `parsed_result_id` (not `parsed_file_id`)
2. **Update intent parameters** to accept `parsed_result_id`
3. **Track user-friendly filenames** for UI display:
   - Store `ui_name` from original file in `parsed_results` table
   - Use pattern: `{ui_name}_parsed`, `{ui_name}_embedding`, etc. for display

**Implementation:**

```python
# In Content Orchestrator
parsed_result_id = generate_event_id()  # Use parsed_result_id consistently

# Track in Supabase with ui_name
await supabase_adapter.insert_document("parsed_results", {
    "parsed_result_id": parsed_result_id,
    "file_id": file_id,
    "ui_name": original_file_ui_name,  # Track for UI display
    "parser_type": parser_type,
    # ...
})

# In Insights Orchestrator - accept parsed_result_id
parsed_result_id = intent.parameters.get("parsed_result_id")
if not parsed_result_id:
    raise ValueError("parsed_result_id is required")
```

**UI Display Pattern:**
- Original file: `permit_oil_gas.pdf`
- Parsed result: `permit_oil_gas_parsed.jsonl`
- Embedding: `permit_oil_gas_embedding`
- Interpretation: `permit_oil_gas_interpretation.json`

---

## Issue 3: Journey Realm `create_workflow` Should Use Embeddings

### Problem

The `create_workflow` intent was modified to accept `workflow_file_path` (BPMN file), but it should be using **deterministic embeddings from parsed results**, not the raw files themselves.

**This defeats the purpose of the "data mash":**
- The data mash concept means we work with processed data (embeddings, parsed results)
- Workflows should be created from semantic embeddings, not raw files
- This avoids duplicating parsing and leverages the data mash

### Root Cause

The fix was too simplistic - it just accepts a file path without considering the data mash architecture.

### Correct Architecture

According to the data mash concept:

1. **Files are parsed once** → `parsed_result_id`
2. **Parsed results are embedded** → `embedding_id`
3. **Workflows are created from embeddings** → Uses semantic understanding, not raw files

**Workflow creation should:**
- Accept `parsed_result_id` or `embedding_id` (not `workflow_file_path`)
- Use embeddings to understand workflow semantics
- Generate workflow from semantic understanding

### Solution

**Update `create_workflow` to use embeddings:**

```python
async def _handle_create_workflow(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle create_workflow intent.
    
    Uses embeddings from parsed results to create workflows (data mash pattern).
    
    Intent parameters:
    - parsed_result_id: str - Parsed result to create workflow from (REQUIRED)
    - embedding_id: str - Optional, if not provided, will use latest embedding for parsed_result_id
    - workflow_type: str - "bpmn", "flowchart", etc. (optional)
    - generate_visual: bool - Whether to generate visual (optional)
    
    OR (legacy mode for SOP-based workflows):
    - sop_id: str - SOP to create workflow from
    """
    parsed_result_id = intent.parameters.get("parsed_result_id")
    embedding_id = intent.parameters.get("embedding_id")
    sop_id = intent.parameters.get("sop_id")
    
    if not parsed_result_id and not sop_id:
        raise ValueError("Either parsed_result_id or sop_id is required for create_workflow intent")
    
    # Mode 1: Create workflow from embeddings (data mash)
    if parsed_result_id:
        # Get embeddings for parsed result
        if not embedding_id:
            # Get latest embedding for parsed_result_id
            embedding_id = await self._get_latest_embedding_id(parsed_result_id, context.tenant_id)
        
        if not embedding_id:
            raise ValueError(f"No embeddings found for parsed_result_id: {parsed_result_id}")
        
        # Create workflow from embeddings via WorkflowConversionService
        workflow_result = await self.workflow_conversion_service.create_workflow_from_embeddings(
            parsed_result_id=parsed_result_id,
            embedding_id=embedding_id,
            tenant_id=context.tenant_id,
            context=context
        )
    
    # Mode 2: Create workflow from SOP (legacy)
    elif sop_id:
        workflow_result = await self.workflow_conversion_service.create_workflow(
            sop_id=sop_id,
            tenant_id=context.tenant_id,
            context=context
        )
    
    # Generate workflow visualization
    visual_result = None
    if intent.parameters.get("generate_visual", False):
        try:
            visual_result = await self.visual_generation_service.generate_workflow_visual(
                workflow_data=workflow_result,
                tenant_id=context.tenant_id,
                context=context
            )
        except Exception as e:
            self.logger.warning(f"Failed to generate workflow visualization: {e}")
    
    artifacts = {
        "workflow": workflow_result,
        "parsed_result_id": parsed_result_id if parsed_result_id else None,
        "embedding_id": embedding_id if parsed_result_id else None,
        "sop_id": sop_id if sop_id else None
    }
    
    if visual_result and visual_result.get("success"):
        artifacts["workflow_visual"] = {
            "image_base64": visual_result.get("image_base64"),
            "storage_path": visual_result.get("storage_path")
        }
    
    return {
        "artifacts": artifacts,
        "events": [
            {
                "type": "workflow_created",
                "parsed_result_id": parsed_result_id,
                "embedding_id": embedding_id,
                "sop_id": sop_id
            }
        ]
    }
```

**Update tests:**

Tests should:
1. Upload and parse file → get `parsed_result_id`
2. Generate embeddings → get `embedding_id`
3. Create workflow from `parsed_result_id` or `embedding_id` (not from BPMN file path)

---

## Issue 4: Supabase Adapter Not Available in Test Environment

### Problem

The lineage visualization test is skipped because "Supabase adapter not available", but the user has run all the same migration scripts on both test and production projects, so they should be identical.

### Root Cause

Looking at `test_fixtures.py`, the Supabase adapter is created, but it may not be properly initialized in `test_public_works` fixture, or the test is checking for it incorrectly.

### Solution

**Check `test_public_works` fixture:**

```python
@pytest.fixture
async def test_public_works(
    test_redis,
    test_arango,
    test_supabase,  # Ensure this is included
    test_gcs,
    test_meilisearch
):
    """Create Public Works Foundation Service with test adapters."""
    public_works = PublicWorksFoundationService()
    
    # Initialize with all adapters
    await public_works.initialize(
        redis_adapter=test_redis,
        arango_adapter=test_arango,
        supabase_adapter=test_supabase,  # Ensure this is set
        gcs_adapter=test_gcs,
        meilisearch_adapter=test_meilisearch
    )
    
    yield public_works
```

**Verify Supabase adapter is available:**

```python
# In lineage visualization service
supabase_adapter = self.public_works.get_supabase_adapter()
if not supabase_adapter:
    # Log error with details
    self.logger.error(
        f"Supabase adapter not available. "
        f"Public Works initialized: {self.public_works is not None}, "
        f"Adapters: {self.public_works.get_available_adapters() if self.public_works else 'N/A'}"
    )
    raise RuntimeError("Supabase adapter not available - required for lineage visualization")
```

**Check test environment:**

1. Verify `.env.secrets` has Supabase credentials
2. Verify `test_supabase` fixture is working
3. Verify `test_public_works` includes Supabase adapter

---

## Implementation Plan

### Phase 1: Fix `ingest_file` Scope (Priority: High)

1. Revert `ingest_file` to only handle new uploads
2. Update tests to use `file_id` directly (not call `ingest_file` for existing files)
3. Document that EDI/API adapters handle their own ingestion

### Phase 2: Standardize Naming (Priority: High)

1. Update all orchestrators to use `parsed_result_id` (not `parsed_file_id`)
2. Update intent parameters to accept `parsed_result_id`
3. Add `ui_name` tracking to `parsed_results` table for UI display
4. Update UI display pattern to use `{ui_name}_parsed`, `{ui_name}_embedding`, etc.

### Phase 3: Fix Journey Realm Workflow Creation (Priority: High)

1. Update `create_workflow` to accept `parsed_result_id` or `embedding_id`
2. Implement `create_workflow_from_embeddings` in `WorkflowConversionService`
3. Update tests to create workflows from embeddings (not from BPMN file paths)
4. Remove `workflow_file_path` parameter (or deprecate it)

### Phase 4: Fix Supabase Adapter Availability (Priority: Medium)

1. Verify `test_public_works` includes Supabase adapter
2. Add better error logging for missing adapters
3. Verify test environment has Supabase credentials
4. Re-enable lineage visualization test

---

## Success Criteria

✅ **`ingest_file` only handles new uploads:**
- No circular logic
- Tests use `file_id` directly for existing files
- EDI/API adapters handle their own ingestion

✅ **Consistent naming:**
- All code uses `parsed_result_id` (not `parsed_file_id`)
- UI displays user-friendly filenames: `{ui_name}_parsed`, `{ui_name}_embedding`

✅ **Workflows use embeddings:**
- `create_workflow` accepts `parsed_result_id` or `embedding_id`
- Workflows created from semantic understanding (data mash)
- No duplicate parsing

✅ **Supabase adapter available:**
- Test environment has Supabase adapter
- Lineage visualization test passes
- All lineage tracking works in tests

---

## References

- [Platform Rules](../PLATFORM_RULES.md)
- [Insights Lineage Tracking Architecture](../architecture/insights_lineage_tracking.md)
- [Lineage Tracking Implementation](../execution/lineage_tracking_implementation.md)
- [Data Mash Implementation Plan](../../symphainy_source/docs/DATA_MASH_IMPLEMENTATION_PLAN.md)
