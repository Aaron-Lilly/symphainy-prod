# Ingestion Extensibility Plan - Unified Multi-Source Ingestion

**Status:** Implementation Plan  
**Date:** January 2026  
**Goal:** Extend `ingest_file` to support EDI, API, and Upload patterns from day 1

---

## Executive Summary

**Great News:** The ingestion infrastructure already exists! We have:
- ✅ `IngestionProtocol` and `IngestionAbstraction` (Layer 1)
- ✅ `UploadAdapter`, `EDIAdapter`, `APIAdapter` (Layer 0)
- ✅ Unified `IngestionRequest`/`IngestionResult` pattern

**The Gap:** `ingest_file` intent doesn't use this infrastructure - it directly calls `FileStorageAbstraction`, bypassing the extensible ingestion pattern.

**Solution:** Refactor `ingest_file` to use `IngestionAbstraction`, enabling unified multi-source ingestion from day 1.

---

## Current State Analysis

### What EXISTS

#### Ingestion Infrastructure (Already Built!)

**Protocol Layer:**
- ✅ `IngestionProtocol` - Defines unified ingestion interface
- ✅ `IngestionType` enum - UPLOAD, EDI, API
- ✅ `IngestionRequest` - Unified request structure
- ✅ `IngestionResult` - Unified result structure

**Abstraction Layer:**
- ✅ `IngestionAbstraction` - Routes to appropriate adapter
- ✅ Supports Upload, EDI, and API adapters

**Adapter Layer:**
- ✅ `UploadAdapter` - Direct file uploads
- ✅ `EDIAdapter` - AS2, SFTP, Email attachments
- ✅ `APIAdapter` - REST, GraphQL, Webhooks

#### Current `ingest_file` Implementation

**Problem:** Directly uses `FileStorageAbstraction`, bypassing ingestion infrastructure:

```python
# Current (bypasses IngestionAbstraction)
upload_result = await self.file_parser_service.file_storage_abstraction.upload_file(
    file_path=temp_file_path,
    file_data=file_content,
    metadata=upload_metadata
)
```

**Should be:**
```python
# Should use IngestionAbstraction
ingestion_result = await self.ingestion_abstraction.ingest_data(
    request=IngestionRequest(
        ingestion_type=IngestionType.UPLOAD,
        tenant_id=context.tenant_id,
        session_id=context.session_id,
        source_metadata={...},
        data=file_content
    )
)
```

---

## Proposed Solution

### Refactor `ingest_file` to Use IngestionAbstraction

**Benefits:**
- ✅ Unified ingestion interface (upload, EDI, API all work the same)
- ✅ Extensibility built in (add new adapters without changing intent)
- ✅ Consistent error handling across all ingestion types
- ✅ Ingestion metadata tracked uniformly
- ✅ Easy to add new ingestion types (webhook, scheduled, streaming)

### Updated `ingest_file` Intent

```python
async def _handle_ingest_file(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle ingest_file intent - unified ingestion from multiple sources.
    
    Supports:
    - UPLOAD: Direct file upload (hex-encoded bytes)
    - EDI: EDI protocol (AS2, SFTP, etc.)
    - API: REST/GraphQL API payloads
    
    Intent parameters:
    - ingestion_type: str (REQUIRED) - "upload", "edi", or "api"
    - file_content: bytes (hex-encoded) - For UPLOAD type
    - api_payload: Dict - For API type
    - edi_data: bytes - For EDI type
    - ui_name: str (REQUIRED) - User-friendly filename
    - file_type: str - File type (e.g., "pdf", "csv")
    - mime_type: str - MIME type (e.g., "application/pdf")
    - source_metadata: Dict - Source-specific metadata (partner_id for EDI, endpoint for API, etc.)
    - ingestion_options: Dict - Ingestion-specific options
    """
    # Get ingestion abstraction from Public Works
    if not self.public_works:
        raise RuntimeError("Public Works not initialized - cannot access IngestionAbstraction")
    
    ingestion_abstraction = self.public_works.get_ingestion_abstraction()
    if not ingestion_abstraction:
        raise RuntimeError("IngestionAbstraction not available - Public Works not configured")
    
    # Determine ingestion type
    ingestion_type_str = intent.parameters.get("ingestion_type", "upload").lower()
    try:
        ingestion_type = IngestionType(ingestion_type_str)
    except ValueError:
        raise ValueError(f"Invalid ingestion_type: {ingestion_type_str}. Must be 'upload', 'edi', or 'api'")
    
    # Extract common metadata
    ui_name = intent.parameters.get("ui_name")
    if not ui_name:
        raise ValueError("ui_name is required for ingest_file intent")
    
    file_type = intent.parameters.get("file_type", "unstructured")
    mime_type = intent.parameters.get("mime_type", "application/octet-stream")
    user_id = intent.parameters.get("user_id") or context.metadata.get("user_id", "system")
    source_metadata = intent.parameters.get("source_metadata", {})
    ingestion_options = intent.parameters.get("ingestion_options", {})
    
    # Prepare source metadata
    source_metadata.update({
        "ui_name": ui_name,
        "file_type": file_type,
        "content_type": mime_type,
        "user_id": user_id,
        "filename": intent.parameters.get("filename", ui_name)
    })
    
    # Prepare ingestion request based on type
    if ingestion_type == IngestionType.UPLOAD:
        # Extract file content (hex-encoded)
        file_content_hex = intent.parameters.get("file_content")
        if not file_content_hex:
            raise ValueError("file_content is required for upload ingestion_type")
        
        try:
            file_data = bytes.fromhex(file_content_hex)
        except ValueError as e:
            raise ValueError(f"Invalid file_content (must be hex-encoded): {e}")
        
        ingestion_request = IngestionRequest(
            ingestion_type=IngestionType.UPLOAD,
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            source_metadata=source_metadata,
            data=file_data,
            options=ingestion_options
        )
    
    elif ingestion_type == IngestionType.EDI:
        # Extract EDI data
        edi_data_hex = intent.parameters.get("edi_data")
        if not edi_data_hex:
            raise ValueError("edi_data is required for edi ingestion_type")
        
        try:
            edi_data = bytes.fromhex(edi_data_hex)
        except ValueError as e:
            raise ValueError(f"Invalid edi_data (must be hex-encoded): {e}")
        
        # EDI-specific metadata
        partner_id = intent.parameters.get("partner_id")
        if not partner_id:
            raise ValueError("partner_id is required for edi ingestion_type")
        
        source_metadata["partner_id"] = partner_id
        source_metadata["edi_protocol"] = intent.parameters.get("edi_protocol", "as2")
        
        ingestion_request = IngestionRequest(
            ingestion_type=IngestionType.EDI,
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            source_metadata=source_metadata,
            data=edi_data,
            options=ingestion_options
        )
    
    elif ingestion_type == IngestionType.API:
        # Extract API payload
        api_payload = intent.parameters.get("api_payload")
        if not api_payload:
            raise ValueError("api_payload is required for api ingestion_type")
        
        # API-specific metadata
        endpoint = intent.parameters.get("endpoint")
        api_type = intent.parameters.get("api_type", "rest")  # rest, graphql, webhook
        
        source_metadata["endpoint"] = endpoint
        source_metadata["api_type"] = api_type
        
        ingestion_request = IngestionRequest(
            ingestion_type=IngestionType.API,
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            source_metadata=source_metadata,
            api_payload=api_payload,
            options=ingestion_options
        )
    
    # Execute ingestion via IngestionAbstraction
    ingestion_result = await ingestion_abstraction.ingest_data(ingestion_request)
    
    if not ingestion_result.success:
        raise RuntimeError(f"Ingestion failed: {ingestion_result.error}")
    
    # Register file reference in State Surface (for governed file access)
    file_reference = ingestion_result.file_reference
    
    # Get file metadata from ingestion result
    file_metadata = ingestion_result.ingestion_metadata
    
    await context.state_surface.store_file_reference(
        session_id=context.session_id,
        tenant_id=context.tenant_id,
        file_reference=file_reference,
        storage_location=ingestion_result.storage_location,
        filename=file_metadata.get("filename", ui_name),
        metadata={
            "ui_name": ui_name,
            "file_type": file_type,
            "content_type": mime_type,
            "size": file_metadata.get("size"),
            "file_hash": file_metadata.get("file_hash"),
            "file_id": ingestion_result.file_id,
            "ingestion_type": ingestion_type.value,
            "ingestion_metadata": ingestion_result.ingestion_metadata
        }
    )
    
    self.logger.info(f"File ingested via {ingestion_type.value}: {ingestion_result.file_id} ({ui_name}) -> {file_reference}")
    
    return {
        "artifacts": {
            "file_id": ingestion_result.file_id,
            "file_reference": file_reference,
            "file_path": ingestion_result.storage_location,
            "ui_name": ui_name,
            "file_type": file_type,
            "ingestion_type": ingestion_type.value,
            "status": "ingested"
        },
        "events": [
            {
                "type": "file_ingested",
                "file_id": ingestion_result.file_id,
                "file_reference": file_reference,
                "ui_name": ui_name,
                "ingestion_type": ingestion_type.value
            }
        ]
    }
```

---

## Additional Extensibility Patterns to Build In

### 1. Webhook Ingestion (Future)

**Use Case:** Real-time file ingestion via webhooks

**Implementation:**
- Add `IngestionType.WEBHOOK`
- Create `WebhookAdapter` that validates webhook signatures
- Supports GitHub, Stripe, custom webhooks

**Intent Parameters:**
```python
{
    "ingestion_type": "webhook",
    "webhook_payload": {...},
    "webhook_source": "github",  # github, stripe, custom
    "webhook_signature": "...",  # For validation
    "ui_name": "webhook_file.json"
}
```

### 2. Scheduled Ingestion (Future)

**Use Case:** Poll external systems for new files

**Implementation:**
- Add `IngestionType.SCHEDULED`
- Create `ScheduledIngestionAdapter` that polls on schedule
- Supports cron-based scheduling

**Intent Parameters:**
```python
{
    "ingestion_type": "scheduled",
    "schedule": "0 */6 * * *",  # Every 6 hours
    "source_type": "sftp",  # sftp, api, etc.
    "source_config": {...}
}
```

### 3. Streaming Ingestion (Future)

**Use Case:** Large files that need to be streamed (not loaded into memory)

**Implementation:**
- Add `IngestionType.STREAMING`
- Create `StreamingIngestionAdapter` that streams to GCS
- Supports chunked uploads

**Intent Parameters:**
```python
{
    "ingestion_type": "streaming",
    "stream_url": "https://...",
    "chunk_size": 10485760,  # 10MB chunks
    "ui_name": "large_file.zip"
}
```

### 4. Multi-Part Upload (Future)

**Use Case:** Large files uploaded in parts (S3-style)

**Implementation:**
- Add `initiate_multipart_upload` intent
- Add `upload_part` intent
- Add `complete_multipart_upload` intent

**Flow:**
```
1. initiate_multipart_upload → Returns upload_id
2. upload_part (multiple times) → Uploads parts
3. complete_multipart_upload → Combines parts
```

### 5. Ingestion Validation (Built In)

**Use Case:** Validate files before processing

**Implementation:**
- Add validation hooks to `IngestionAbstraction`
- Validate file size, type, format before storing
- Return validation errors early

**Intent Parameters:**
```python
{
    "ingestion_type": "upload",
    "file_content": "...",
    "validation_rules": {
        "max_size": 104857600,  # 100MB
        "allowed_types": ["pdf", "csv", "json"],
        "required_metadata": ["policy_number"]
    }
}
```

### 6. Ingestion Monitoring (Built In)

**Use Case:** Track ingestion metrics and alert on failures

**Implementation:**
- Track ingestion metrics (count, size, duration, failures)
- Alert on high failure rates
- Dashboard for ingestion health

**Metrics:**
- Ingestion rate (files/hour)
- Success rate (%)
- Average file size
- Ingestion latency
- Failure rate by type (upload, EDI, API)

---

## Updated 4-Phase Implementation Plan

### Phase 1: Core File Management & Unified Ingestion (Week 1)

**Priority: CRITICAL**

**File Management Intents:**
1. `register_file` - Register existing file in State Surface
2. `retrieve_file_metadata` - Get Supabase record
3. `retrieve_file` - Get file contents
4. `list_files` - List files with filters
5. `get_file_by_id` - Get file by file_id

**Unified Ingestion (NEW):**
6. **Refactor `ingest_file` to use `IngestionAbstraction`**
   - Support `ingestion_type` parameter (upload, edi, api)
   - Route to appropriate adapter via abstraction
   - Unified error handling and metadata tracking
7. **Wire up IngestionAbstraction in Public Works**
   - Ensure `get_ingestion_abstraction()` is available
   - Initialize adapters (Upload, EDI, API)
8. **Update tests to use unified ingestion**
   - Test upload ingestion
   - Test EDI ingestion (if configured)
   - Test API ingestion

**Why This Phase:**
- File management intents are foundational
- Unified ingestion enables extensibility from day 1
- EDI/API clients can use same intent as uploads
- Sets pattern for future ingestion types

### Phase 2: Bulk Operations (Week 2)

**Priority: CRITICAL**

1. `bulk_ingest_files` - Bulk upload with batching
   - **Supports all ingestion types** (upload, EDI, API)
   - Batch size configuration
   - Parallel processing
   - Progress tracking
2. `bulk_parse_files` - Bulk parse with parallel processing
3. `bulk_extract_embeddings` - Bulk embedding creation
4. `bulk_interpret_data` - Bulk interpretation

**Why This Phase:**
- Essential for 350k policy processing
- Bulk operations work with all ingestion types
- Enables high-throughput processing

### Phase 3: Error Handling & Resilience (Week 3)

**Priority: HIGH**

1. Idempotency keys for all operations
   - **Include ingestion_type in idempotency key**
   - Prevents duplicate ingestion across types
2. Retry logic with exponential backoff
   - **Ingestion-specific retry strategies** (EDI may need different retry than API)
3. Progress tracking and status queries
4. Resume capability
   - **Resume bulk ingestion from last successful batch**

**Why This Phase:**
- Critical for reliability at scale
- Different ingestion types may need different retry strategies
- Need to track progress across all ingestion types

### Phase 4: File Lifecycle & Advanced Features (Week 4)

**Priority: MEDIUM**

1. `archive_file`, `purge_file`, `restore_file`
2. `validate_file`, `preprocess_file`
3. `search_files`, `query_files`
4. `update_file_metadata`
5. **Future ingestion types** (webhook, scheduled, streaming) - if needed

**Why This Phase:**
- Important for production operations
- Advanced features can be added incrementally
- Future ingestion types can be added without changing core

---

## Implementation Details

### Step 1: Wire Up IngestionAbstraction in Public Works

**File:** `symphainy_platform/foundations/public_works/foundation_service.py`

```python
def __init__(self, ...):
    # ... existing initialization ...
    
    # Initialize ingestion adapters
    upload_adapter = UploadAdapter(file_storage_abstraction=self.file_storage_abstraction)
    edi_adapter = EDIAdapter(
        file_storage_abstraction=self.file_storage_abstraction,
        edi_config=edi_config  # From config
    )
    api_adapter = APIAdapter(file_storage_abstraction=self.file_storage_abstraction)
    
    # Create ingestion abstraction
    self.ingestion_abstraction = IngestionAbstraction(
        upload_adapter=upload_adapter,
        edi_adapter=edi_adapter,
        api_adapter=api_adapter
    )

def get_ingestion_abstraction(self) -> Optional[IngestionAbstraction]:
    """Get ingestion abstraction."""
    return self.ingestion_abstraction
```

### Step 2: Update Content Orchestrator

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

```python
def __init__(self, public_works: Optional[Any] = None):
    # ... existing initialization ...
    
    # Get ingestion abstraction from Public Works
    self.ingestion_abstraction = None
    if public_works:
        self.ingestion_abstraction = public_works.get_ingestion_abstraction()
```

### Step 3: Refactor `_handle_ingest_file`

Replace direct `FileStorageAbstraction` calls with `IngestionAbstraction` calls (see code above).

### Step 4: Update Tests

**File:** `tests/integration/realms/test_content_realm.py`

```python
# Test upload ingestion
intent = IntentFactory.create_intent(
    intent_type="ingest_file",
    parameters={
        "ingestion_type": "upload",
        "file_content": file_content_hex,
        "ui_name": "test_file.pdf",
        "file_type": "application/pdf"
    }
)

# Test EDI ingestion (if configured)
intent = IntentFactory.create_intent(
    intent_type="ingest_file",
    parameters={
        "ingestion_type": "edi",
        "edi_data": edi_data_hex,
        "partner_id": "partner_001",
        "ui_name": "edi_file.edi",
        "file_type": "application/edi"
    }
)

# Test API ingestion
intent = IntentFactory.create_intent(
    intent_type="ingest_file",
    parameters={
        "ingestion_type": "api",
        "api_payload": {"data": "..."},
        "endpoint": "https://api.example.com/files",
        "ui_name": "api_file.json",
        "file_type": "application/json"
    }
)
```

---

## Benefits of Unified Ingestion

### ✅ Extensibility Built In

- Add new ingestion types without changing `ingest_file` intent
- All ingestion types use same interface
- Easy to add webhook, scheduled, streaming later

### ✅ Consistent Error Handling

- All ingestion types have same error format
- Unified retry logic
- Consistent logging and monitoring

### ✅ Unified Metadata Tracking

- All ingestion types track same metadata
- Ingestion source tracked in lineage
- Easy to query by ingestion type

### ✅ EDI/API Clients Use Same Intent

- No special handling needed
- Same intent for all sources
- Consistent behavior across sources

### ✅ Future-Proof

- Easy to add new adapters
- Pattern established for all ingestion types
- No architectural changes needed for new types

---

## Success Criteria

✅ **Unified Ingestion:**
- `ingest_file` supports upload, EDI, and API
- All ingestion types use `IngestionAbstraction`
- Consistent error handling and metadata

✅ **Extensibility:**
- Can add new ingestion types without changing intent
- Pattern established for future types
- Easy to add webhook, scheduled, streaming

✅ **EDI/API Support:**
- EDI clients can ingest via `ingest_file`
- API clients can ingest via `ingest_file`
- Same intent, different `ingestion_type` parameter

✅ **Bulk Operations:**
- `bulk_ingest_files` supports all ingestion types
- Can bulk ingest from multiple sources
- Unified progress tracking

---

## Additional Considerations

### Configuration

**EDI Configuration:**
- Partner configurations (AS2 names, keys, certificates)
- Protocol settings (AS2, SFTP, etc.)
- Stored in config, passed to `EDIAdapter`

**API Configuration:**
- API endpoints and authentication
- Rate limiting and retry policies
- Stored in config, passed to `APIAdapter`

### Security

**EDI:**
- AS2 encryption/decryption
- Signature verification
- Partner authentication

**API:**
- API key authentication
- Webhook signature validation
- Rate limiting

### Monitoring

**Ingestion Metrics:**
- Count by ingestion type (upload, EDI, API)
- Success rate by type
- Latency by type
- Failure reasons by type

**Alerts:**
- High failure rate for any ingestion type
- Slow ingestion (latency threshold)
- Missing adapters (EDI/API not configured)

---

## References

- [E2E Data Flow Audit](./e2e_data_flow_audit.md)
- [Ingest File Analysis](./ingest_file_analysis.md)
- [Platform Rules](../PLATFORM_RULES.md)
- [Ingestion Protocol](../../symphainy_platform/foundations/public_works/protocols/ingestion_protocol.py)
- [Ingestion Abstraction](../../symphainy_platform/foundations/public_works/abstractions/ingestion_abstraction.py)
