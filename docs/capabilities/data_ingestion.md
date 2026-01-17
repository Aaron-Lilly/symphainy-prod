# Data Ingestion Capability

**Realm:** Content  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

Data Ingestion provides unified file ingestion from multiple sources: direct upload, EDI protocols, and API integrations. This enables the platform to accept data from any source while maintaining consistent processing and governance.

**Business Value:** Enables organizations to ingest data from their existing systems (EDI, APIs, file uploads) without custom integration code.

---

## Available Intents

### 1. Ingest File (Upload)

**Intent:** `ingest_file`

**Purpose:** Upload a file directly to the platform

**Use Case:** User uploads a file via web interface

**Parameters:**
```python
{
    "ingestion_type": "upload",  # Required
    "file_content": "<hex_encoded_file_content>",  # Required for upload
    "ui_name": "<user_friendly_filename>",  # Required
    "file_type": "<file_type>",  # Optional, default: "unstructured"
    "mime_type": "<mime_type>",  # Optional, default: "application/octet-stream"
    "filename": "<filename>",  # Optional, defaults to ui_name
    "user_id": "<user_id>",  # Optional
    "source_metadata": {},  # Optional
    "ingestion_options": {}  # Optional
}
```

**Response:**
```python
{
    "artifacts": {
        "file_id": "<file_uuid>",
        "file_reference": "file:<tenant_id>:<session_id>:<file_id>",
        "file_path": "<gcs_path>",
        "ui_name": "<ui_name>",
        "file_type": "<file_type>",
        "ingestion_type": "upload",
        "status": "ingested"
    },
    "events": [
        {
            "type": "file_ingested",
            "file_id": "<file_uuid>",
            "file_reference": "<file_reference>",
            "ui_name": "<ui_name>",
            "ingestion_type": "upload"
        }
    ]
}
```

**Example:**
```python
# Read file and encode as hex
with open("policy.pdf", "rb") as f:
    file_content_hex = f.read().hex()

intent = IntentFactory.create_intent(
    intent_type="ingest_file",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "ingestion_type": "upload",
        "file_content": file_content_hex,
        "ui_name": "insurance_policy_001.pdf",
        "file_type": "unstructured",
        "mime_type": "application/pdf"
    }
)
result = await execution_manager.execute(intent)
file_id = result.artifacts["file_id"]
```

---

### 2. Ingest File (EDI)

**Intent:** `ingest_file`

**Purpose:** Ingest file via EDI protocol (AS2, SFTP, etc.)

**Use Case:** Partner sends file via EDI protocol

**Parameters:**
```python
{
    "ingestion_type": "edi",  # Required
    "edi_data": "<hex_encoded_edi_data>",  # Required
    "partner_id": "<partner_id>",  # Required
    "ui_name": "<user_friendly_filename>",  # Required
    "edi_protocol": "<protocol>",  # Optional, default: "as2"
    "file_type": "<file_type>",  # Optional
    "mime_type": "<mime_type>",  # Optional
    "source_metadata": {},  # Optional
    "ingestion_options": {}  # Optional
}
```

**Response:** Same as upload, with `ingestion_type: "edi"`

**Example:**
```python
intent = IntentFactory.create_intent(
    intent_type="ingest_file",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "ingestion_type": "edi",
        "edi_data": edi_data_hex,
        "partner_id": "partner_abc",
        "ui_name": "edi_transaction_001.edi",
        "edi_protocol": "as2"
    }
)
result = await execution_manager.execute(intent)
```

---

### 3. Ingest File (API)

**Intent:** `ingest_file`

**Purpose:** Ingest file via API payload (REST, GraphQL, etc.)

**Use Case:** External system sends data via API

**Parameters:**
```python
{
    "ingestion_type": "api",  # Required
    "api_payload": "<api_payload>",  # Required (dict or JSON string)
    "ui_name": "<user_friendly_filename>",  # Required
    "endpoint": "<endpoint>",  # Optional
    "api_type": "<api_type>",  # Optional, default: "rest"
    "file_type": "<file_type>",  # Optional
    "mime_type": "<mime_type>",  # Optional
    "source_metadata": {},  # Optional
    "ingestion_options": {}  # Optional
}
```

**Response:** Same as upload, with `ingestion_type: "api"`

**Example:**
```python
intent = IntentFactory.create_intent(
    intent_type="ingest_file",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "ingestion_type": "api",
        "api_payload": {
            "data": {...},
            "metadata": {...}
        },
        "ui_name": "api_data_001.json",
        "api_type": "rest"
    }
)
result = await execution_manager.execute(intent)
```

---

## Supported File Types

The platform supports ingestion of any file type. Common types include:

- **Documents:** PDF, DOCX, TXT
- **Spreadsheets:** XLSX, CSV
- **Images:** PNG, JPG, TIFF
- **Data:** JSON, XML
- **Workflows:** BPMN
- **Binary:** Mainframe files (with copybooks)

---

## Business Use Cases

### Use Case 1: Web Upload
**Scenario:** User uploads a file via web interface

**Flow:**
1. User selects file in UI
2. Frontend encodes file as hex
3. Frontend calls `ingest_file` with `ingestion_type="upload"`
4. Platform stores file and returns file_id
5. Frontend displays success message

### Use Case 2: EDI Integration
**Scenario:** Partner sends insurance policy via AS2

**Flow:**
1. Partner sends file via AS2 protocol
2. EDI adapter receives file
3. Platform calls `ingest_file` with `ingestion_type="edi"`
4. File is stored and processed
5. Partner receives acknowledgment

### Use Case 3: API Integration
**Scenario:** External system sends data via REST API

**Flow:**
1. External system calls platform API
2. API adapter receives payload
3. Platform calls `ingest_file` with `ingestion_type="api"`
4. Payload is converted to file and stored
5. External system receives confirmation

### Use Case 4: Bulk Upload
**Scenario:** User needs to upload 1000 files

**Flow:**
1. User prepares file list
2. Frontend calls `bulk_ingest_files` (see [Bulk Operations](bulk_operations.md))
3. Platform processes files in batches
4. User tracks progress
5. All files are ingested

---

## Error Handling

All ingestion types return proper error responses:

```python
{
    "success": False,
    "error": "Invalid file content: <error>",
    "artifacts": {},
    "events": []
}
```

**Common Errors:**
- `Invalid file content` - File content is malformed
- `File too large` - File exceeds size limit
- `Unsupported file type` - File type not supported
- `Storage error` - Failed to store file

---

## Idempotency

Ingestion supports idempotency via `idempotency_key`:

```python
intent = IntentFactory.create_intent(
    intent_type="ingest_file",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={...},
    idempotency_key="unique_key_123"  # Prevents duplicate ingestion
)
```

If the same `idempotency_key` is used, the operation returns the existing file_id instead of creating a duplicate.

---

## Related Capabilities

- [File Management](file_management.md) - Retrieve and list files
- [Bulk Operations](bulk_operations.md) - Ingest multiple files
- [File Parsing](file_parsing.md) - Parse ingested files

---

## API Reference

For complete API contracts, see [API Contracts](../execution/api_contracts_frontend_integration.md).

---

**Status:** ✅ Complete and Operational
