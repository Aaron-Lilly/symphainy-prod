# Extensible Ingestion Architecture - Upload, EDI, API

**Date:** January 2026  
**Status:** 📋 **DESIGN COMPLETE**  
**Goal:** Add EDI and API ingestion while preserving existing upload flow

---

## 🎯 Executive Summary

**Design an extensible ingestion pattern** that supports multiple ingestion methods (Upload, EDI, API) while maintaining a **single, unified flow** after ingestion. All ingestion methods converge to the same parsing → data mash pipeline.

**Key Principle:** 
> **Ingestion is a boundary crossing mechanism. After ingestion, all data follows the same platform-native flow.**

---

## 📊 Current Flow (Upload)

```
Experience Plane
  ↓ (User uploads file)
POST /api/v1/content/upload
  ↓
Runtime Intent: "content.upload"
  ↓
Content Realm Orchestrator
  ↓
File Storage (GCS + Supabase metadata)
  ↓
State Surface (file_reference)
  ↓
Content Orchestrator.parse_file()
  ↓
Parsing Services (Structured/Unstructured/Hybrid)
  ↓
Parsed artifacts (GCS + Supabase)
  ↓
Data Mash (Phase 5.1)
```

**✅ This flow works and must be preserved.**

---

## 🎯 Extended Flow (Upload + EDI + API)

```
┌─────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                            │
│  (Multiple entry points, single convergence point)          │
└─────────────────────────────────────────────────────────────┘
         │              │              │
         │              │              │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │ Upload  │   │   EDI   │   │   API   │
    │ Adapter │   │ Adapter │   │ Adapter │
    └────┬────┘   └────┬────┘   └────┬────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │  Ingestion Abstraction      │
         │  (Unified Interface)        │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │  Runtime Intent             │
         │  "content.ingest"           │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │  Content Realm              │
         │  Ingestion Service          │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │  File Storage               │
         │  (GCS + Supabase)            │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │  State Surface               │
         │  (file_reference)             │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │  EXISTING FLOW              │
         │  (Parse → Data Mash)        │
         └─────────────────────────────┘
```

**Key Insight:** All ingestion methods converge **before** parsing. The rest of the flow is unchanged.

---

## 🏗️ Architecture Design

### 1. Ingestion Protocol (Layer 2)

**Location:** `symphainy_platform/foundations/public_works/protocols/ingestion_protocol.py`

```python
from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class IngestionType(str, Enum):
    """Ingestion method types."""
    UPLOAD = "upload"      # Direct file upload (existing)
    EDI = "edi"            # EDI protocol (AS2, SFTP, etc.)
    API = "api"            # REST/GraphQL API

@dataclass
class IngestionRequest:
    """Unified ingestion request."""
    ingestion_type: IngestionType
    tenant_id: str
    session_id: str
    source_metadata: Dict[str, Any]  # Source-specific metadata
    data: Optional[bytes] = None      # For upload/EDI
    api_payload: Optional[Dict[str, Any]] = None  # For API
    options: Optional[Dict[str, Any]] = None

@dataclass
class IngestionResult:
    """Unified ingestion result."""
    success: bool
    file_id: str  # Unified file_id after ingestion
    file_reference: str  # State Surface reference
    ingestion_metadata: Dict[str, Any]  # Ingestion-specific metadata
    error: Optional[str] = None

class IngestionAdapter(Protocol):
    """Protocol for ingestion adapters (Layer 0)."""
    
    async def ingest(
        self,
        request: IngestionRequest
    ) -> IngestionResult:
        """Ingest data from source."""
        pass

class IngestionProtocol(Protocol):
    """Protocol for ingestion abstraction (Layer 1)."""
    
    async def ingest_data(
        self,
        request: IngestionRequest
    ) -> IngestionResult:
        """Ingest data using appropriate adapter."""
        pass
```

### 2. Ingestion Adapters (Layer 0)

#### 2.1 Upload Adapter (Existing - Wrapped)

**Location:** `symphainy_platform/foundations/public_works/adapters/upload_adapter.py`

```python
class UploadAdapter:
    """
    Upload adapter - wraps existing file upload flow.
    
    This adapter preserves the existing upload pathway.
    """
    
    def __init__(self, file_storage_abstraction: Any):
        self.file_storage = file_storage_abstraction
        self.logger = get_logger(self.__class__.__name__)
    
    async def ingest(self, request: IngestionRequest) -> IngestionResult:
        """Ingest via file upload (existing flow)."""
        if request.ingestion_type != IngestionType.UPLOAD:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                ingestion_metadata={},
                error=f"Upload adapter only handles UPLOAD, got {request.ingestion_type}"
            )
        
        # Use existing file storage abstraction
        filename = request.source_metadata.get("filename", "uploaded_file")
        result = await self.file_storage.upload_file(
            file_path=filename,
            file_data=request.data,
            metadata={
                **request.source_metadata,
                "ingestion_type": "upload",
                "ingestion_timestamp": get_clock().now_iso()
            },
            tenant_id=request.tenant_id
        )
        
        if result.get("success"):
            return IngestionResult(
                success=True,
                file_id=result["file_id"],
                file_reference=result.get("file_reference", result["file_id"]),
                ingestion_metadata={
                    "ingestion_type": "upload",
                    "original_filename": filename
                }
            )
        else:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                ingestion_metadata={},
                error=result.get("error", "Upload failed")
            )
```

#### 2.2 EDI Adapter

**Location:** `symphainy_platform/foundations/public_works/adapters/edi_adapter.py`

```python
class EDIAdapter:
    """
    EDI adapter - handles EDI protocol ingestion.
    
    Supports:
    - AS2 (Applicability Statement 2)
    - SFTP (Secure File Transfer Protocol)
    - Email attachments (future)
    """
    
    def __init__(
        self,
        file_storage_abstraction: Any,
        edi_config: Optional[Dict[str, Any]] = None
    ):
        self.file_storage = file_storage_abstraction
        self.config = edi_config or {}
        self.logger = get_logger(self.__class__.__name__)
    
    async def ingest(self, request: IngestionRequest) -> IngestionResult:
        """Ingest via EDI protocol."""
        if request.ingestion_type != IngestionType.EDI:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                ingestion_metadata={},
                error=f"EDI adapter only handles EDI, got {request.ingestion_type}"
            )
        
        # Extract EDI-specific metadata
        edi_protocol = request.source_metadata.get("protocol", "as2")  # as2, sftp, email
        partner_id = request.source_metadata.get("partner_id")
        transaction_type = request.source_metadata.get("transaction_type")
        
        # Process EDI data (decrypt, validate, etc.)
        processed_data = await self._process_edi_data(
            request.data,
            edi_protocol,
            partner_id
        )
        
        # Store as file (same as upload)
        filename = request.source_metadata.get("filename", f"edi_{transaction_type}_{get_clock().now_iso()}")
        result = await self.file_storage.upload_file(
            file_path=filename,
            file_data=processed_data,
            metadata={
                **request.source_metadata,
                "ingestion_type": "edi",
                "edi_protocol": edi_protocol,
                "partner_id": partner_id,
                "transaction_type": transaction_type,
                "ingestion_timestamp": get_clock().now_iso()
            },
            tenant_id=request.tenant_id
        )
        
        if result.get("success"):
            return IngestionResult(
                success=True,
                file_id=result["file_id"],
                file_reference=result.get("file_reference", result["file_id"]),
                ingestion_metadata={
                    "ingestion_type": "edi",
                    "edi_protocol": edi_protocol,
                    "partner_id": partner_id,
                    "transaction_type": transaction_type
                }
            )
        else:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                ingestion_metadata={},
                error=result.get("error", "EDI ingestion failed")
            )
    
    async def _process_edi_data(
        self,
        data: bytes,
        protocol: str,
        partner_id: Optional[str]
    ) -> bytes:
        """Process EDI data (decrypt, validate, etc.)."""
        # Protocol-specific processing
        if protocol == "as2":
            # AS2 decryption/validation
            return await self._process_as2(data, partner_id)
        elif protocol == "sftp":
            # SFTP file processing
            return data  # SFTP files are already decrypted
        else:
            return data
    
    async def _process_as2(self, data: bytes, partner_id: Optional[str]) -> bytes:
        """Process AS2 protocol data."""
        # TODO: Implement AS2 decryption/validation
        # For now, return as-is
        return data
```

#### 2.3 API Adapter

**Location:** `symphainy_platform/foundations/public_works/adapters/api_adapter.py`

```python
class APIAdapter:
    """
    API adapter - handles API-based ingestion.
    
    Supports:
    - REST API (JSON payloads)
    - GraphQL API (queries/mutations)
    - Webhook callbacks
    """
    
    def __init__(self, file_storage_abstraction: Any):
        self.file_storage = file_storage_abstraction
        self.logger = get_logger(self.__class__.__name__)
    
    async def ingest(self, request: IngestionRequest) -> IngestionResult:
        """Ingest via API."""
        if request.ingestion_type != IngestionType.API:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                ingestion_metadata={},
                error=f"API adapter only handles API, got {request.ingestion_type}"
            )
        
        # Extract API-specific metadata
        api_type = request.source_metadata.get("api_type", "rest")  # rest, graphql, webhook
        endpoint = request.source_metadata.get("endpoint")
        
        # Convert API payload to file format
        file_data = await self._convert_api_payload_to_file(
            request.api_payload,
            api_type
        )
        
        # Store as file (same as upload)
        filename = request.source_metadata.get("filename", f"api_{get_clock().now_iso()}.json")
        result = await self.file_storage.upload_file(
            file_path=filename,
            file_data=file_data,
            metadata={
                **request.source_metadata,
                "ingestion_type": "api",
                "api_type": api_type,
                "endpoint": endpoint,
                "ingestion_timestamp": get_clock().now_iso()
            },
            tenant_id=request.tenant_id
        )
        
        if result.get("success"):
            return IngestionResult(
                success=True,
                file_id=result["file_id"],
                file_reference=result.get("file_reference", result["file_id"]),
                ingestion_metadata={
                    "ingestion_type": "api",
                    "api_type": api_type,
                    "endpoint": endpoint
                }
            )
        else:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                ingestion_metadata={},
                error=result.get("error", "API ingestion failed")
            )
    
    async def _convert_api_payload_to_file(
        self,
        payload: Dict[str, Any],
        api_type: str
    ) -> bytes:
        """Convert API payload to file bytes."""
        import json
        
        if api_type == "rest" or api_type == "graphql":
            # Convert JSON payload to JSON file
            return json.dumps(payload, indent=2).encode('utf-8')
        else:
            # Webhook or other - convert to JSON
            return json.dumps(payload).encode('utf-8')
```

### 3. Ingestion Abstraction (Layer 1)

**Location:** `symphainy_platform/foundations/public_works/abstractions/ingestion_abstraction.py`

```python
class IngestionAbstraction:
    """
    Ingestion abstraction - unified interface for all ingestion methods.
    
    Routes to appropriate adapter based on ingestion type.
    """
    
    def __init__(
        self,
        upload_adapter: Optional[IngestionAdapter] = None,
        edi_adapter: Optional[IngestionAdapter] = None,
        api_adapter: Optional[IngestionAdapter] = None
    ):
        self.upload_adapter = upload_adapter
        self.edi_adapter = edi_adapter
        self.api_adapter = api_adapter
        self.logger = get_logger(self.__class__.__name__)
    
    async def ingest_data(self, request: IngestionRequest) -> IngestionResult:
        """Ingest data using appropriate adapter."""
        # Route to appropriate adapter
        if request.ingestion_type == IngestionType.UPLOAD:
            if not self.upload_adapter:
                return IngestionResult(
                    success=False,
                    file_id="",
                    file_reference="",
                    ingestion_metadata={},
                    error="Upload adapter not configured"
                )
            return await self.upload_adapter.ingest(request)
        
        elif request.ingestion_type == IngestionType.EDI:
            if not self.edi_adapter:
                return IngestionResult(
                    success=False,
                    file_id="",
                    file_reference="",
                    ingestion_metadata={},
                    error="EDI adapter not configured"
                )
            return await self.edi_adapter.ingest(request)
        
        elif request.ingestion_type == IngestionType.API:
            if not self.api_adapter:
                return IngestionResult(
                    success=False,
                    file_id="",
                    file_reference="",
                    ingestion_metadata={},
                    error="API adapter not configured"
                )
            return await self.api_adapter.ingest(request)
        
        else:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                ingestion_metadata={},
                error=f"Unknown ingestion type: {request.ingestion_type}"
            )
```

### 4. Content Realm Ingestion Service

**Location:** `symphainy_platform/realms/content/services/ingestion_service/ingestion_service.py`

```python
class IngestionService:
    """
    Content Realm Ingestion Service.
    
    Handles all ingestion methods and routes to parsing.
    """
    
    def __init__(
        self,
        ingestion_abstraction: Any,
        content_orchestrator: Any,
        state_surface: Any
    ):
        self.ingestion = ingestion_abstraction
        self.orchestrator = content_orchestrator
        self.state_surface = state_surface
        self.logger = get_logger(self.__class__.__name__)
    
    async def ingest_and_parse(
        self,
        request: IngestionRequest,
        parse_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest data and immediately parse it.
        
        This is the unified entry point for all ingestion methods.
        """
        # Step 1: Ingest (converges all methods to file storage)
        ingestion_result = await self.ingestion.ingest_data(request)
        
        if not ingestion_result.success:
            return {
                "success": False,
                "error": ingestion_result.error,
                "ingestion_metadata": ingestion_result.ingestion_metadata
            }
        
        # Step 2: Store file reference in State Surface (if not already there)
        await self.state_surface.store_file(
            file_id=ingestion_result.file_id,
            file_reference=ingestion_result.file_reference,
            tenant_id=request.tenant_id,
            metadata=ingestion_result.ingestion_metadata
        )
        
        # Step 3: Parse (existing flow - unchanged)
        parse_result = await self.orchestrator.parse_file(
            file_reference=ingestion_result.file_reference,
            filename=ingestion_result.ingestion_metadata.get("original_filename", ingestion_result.file_id),
            parsing_type=None,  # Auto-detect
            options=parse_options
        )
        
        return {
            "success": True,
            "file_id": ingestion_result.file_id,
            "file_reference": ingestion_result.file_reference,
            "ingestion_metadata": ingestion_result.ingestion_metadata,
            "parse_result": parse_result
        }
```

### 5. Runtime Intent Update

**Location:** `symphainy_platform/runtime/runtime_service.py`

```python
# Add new intent type (preserves existing "content.upload")
INTENT_TYPES = {
    "content.upload",      # Existing - preserved
    "content.ingest",     # New - unified ingestion
    "content.ingest.edi", # New - EDI-specific
    "content.ingest.api"  # New - API-specific
}
```

**Experience Plane can use either:**
- `content.upload` - Direct upload (existing flow, unchanged)
- `content.ingest` - Unified ingestion (supports all methods)

---

## 🔄 Flow Comparison

### Existing Upload Flow (Preserved)

```
POST /api/v1/content/upload
  ↓
Runtime Intent: "content.upload"
  ↓
Content Realm (existing handler)
  ↓
File Storage → Parse → Data Mash
```

### New Unified Ingestion Flow

```
POST /api/v1/content/ingest
  ↓
Runtime Intent: "content.ingest"
  ↓
Content Realm Ingestion Service
  ↓
Ingestion Abstraction (routes to adapter)
  ↓
File Storage (convergence point)
  ↓
Parse → Data Mash (unchanged)
```

**Key:** Both flows converge at File Storage. Everything after is identical.

---

## ✅ Benefits

1. **Preserves Existing Flow** - Upload pathway unchanged
2. **Extensible** - Easy to add new ingestion methods
3. **Unified** - Single abstraction for all methods
4. **Platform-Native** - Uses Runtime, State Surface, WAL
5. **Testable** - Each adapter can be tested independently

---

## 🚀 Implementation Plan

### Phase 1: Foundation (1-2 days)
1. Create Ingestion Protocol (Layer 2)
2. Create Upload Adapter (wraps existing)
3. Create Ingestion Abstraction (Layer 1)
4. Register in Public Works Foundation

### Phase 2: EDI Support (2-3 days)
1. Create EDI Adapter
2. Add EDI configuration
3. Test EDI ingestion flow

### Phase 3: API Support (2-3 days)
1. Create API Adapter
2. Add API endpoint handlers
3. Test API ingestion flow

### Phase 4: Integration (1 day)
1. Create Ingestion Service in Content Realm
2. Update Runtime intents
3. Update Experience Plane handlers
4. End-to-end testing

---

## ⚠️ Migration Strategy

**Existing upload flow continues to work unchanged.**

New ingestion methods are **additive**, not replacements:

- ✅ `content.upload` - Still works (preserved)
- ✅ `content.ingest` - New unified method
- ✅ `content.ingest.edi` - EDI-specific
- ✅ `content.ingest.api` - API-specific

**No breaking changes.**

---

## 📝 Next Steps

1. **Review this design** - Confirm approach
2. **Implement Phase 1** - Foundation (protocols, adapters, abstraction)
3. **Test with existing upload** - Verify no regressions
4. **Add EDI/API** - Implement new adapters
5. **Integrate** - Wire into Content Realm

---

**Status:** ✅ **READY FOR IMPLEMENTATION**
