# File Parsing Capability

**Realm:** Content  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

File Parsing extracts structured data from diverse file types including PDFs, Excel spreadsheets, binary mainframe files, images, BPMN workflows, and DOCX documents. The platform automatically detects file types and routes to appropriate parsers.

**Business Value:** Enables organizations to extract structured data from any file format without custom parsing code, supporting legacy system migration and data extraction.

---

## Supported File Types

### Structured Files
- **PDF (Structured)** - Forms, permits, structured documents
- **Excel** - XLSX, CSV spreadsheets
- **JSON** - Structured data files
- **XML** - Structured data files

### Unstructured Files
- **PDF (Unstructured)** - Text documents, reports
- **DOCX** - Word documents
- **TXT** - Plain text files

### Binary Files
- **Mainframe Binary (ASCII)** - With copybook definitions
- **Mainframe Binary (EBCDIC)** - With copybook definitions
- **Images** - PNG, JPG, TIFF (for OCR)

### Workflow Files
- **BPMN** - Business process models

---

## Available Intents

### 1. Parse Content

**Intent:** `parse_content`

**Purpose:** Parse a file to extract structured data

**Use Case:** Extract data from uploaded file

**Parameters:**
```python
{
    "file_id": "<file_uuid>",  # Required
    "file_reference": "<file_reference>",  # Optional
    "parse_options": {  # Optional
        "extract_tables": True,
        "extract_text": True,
        "ocr": False  # For images
    }
}
```

**Response:**
```python
{
    "artifacts": {
        "parsed_result_id": "<parsed_id>",
        "file_id": "<file_uuid>",
        "file_type": "<file_type>",
        "parsed_data": {
            # Extracted structured data
        },
        "metadata": {
            "parser_used": "<parser_name>",
            "parsing_time": <seconds>,
            "extracted_fields": [...]
        }
    },
    "events": [
        {
            "type": "file_parsed",
            "file_id": "<file_uuid>",
            "parsed_result_id": "<parsed_id>"
        }
    ]
}
```

**Example:**
```python
intent = IntentFactory.create_intent(
    intent_type="parse_content",
    tenant_id="tenant_123",
    session_id="session_456",
    solution_id="solution_789",
    parameters={
        "file_id": "abc-123-def-456",
        "parse_options": {
            "extract_tables": True,
            "extract_text": True
        }
    }
)
result = await execution_manager.execute(intent)
parsed_data = result.artifacts["parsed_data"]
```

---

### 2. Extract Embeddings

**Intent:** `extract_embeddings`

**Purpose:** Generate semantic embeddings from parsed content

**Use Case:** Create embeddings for semantic search and analysis

**Parameters:**
```python
{
    "parsed_result_id": "<parsed_id>",  # Required
    "embedding_options": {  # Optional
        "model": "default",
        "chunk_size": 512
    }
}
```

**Response:**
```python
{
    "artifacts": {
        "embedding_id": "<embedding_id>",
        "parsed_result_id": "<parsed_id>",
        "embeddings": [
            {
                "chunk_id": "<chunk_id>",
                "text": "<text_chunk>",
                "embedding": [<vector>],
                "metadata": {...}
            }
        ],
        "metadata": {
            "model_used": "<model_name>",
            "chunk_count": <count>
        }
    },
    "events": []
}
```

---

### 3. Get Parsed File

**Intent:** `get_parsed_file`

**Purpose:** Retrieve parsed results for a file

**Use Case:** Display parsed data, use for analysis

**Parameters:**
```python
{
    "parsed_result_id": "<parsed_id>"  # Required
}
```

**Response:**
```python
{
    "artifacts": {
        "parsed_result_id": "<parsed_id>",
        "file_id": "<file_uuid>",
        "parsed_data": {
            # Extracted structured data
        },
        "metadata": {...}
    },
    "events": []
}
```

---

## Parser Details

### PDF Parser
- **Structured PDFs:** Extracts form fields, tables, structured data
- **Unstructured PDFs:** Extracts text, performs OCR if needed
- **Use Cases:** Permit extraction, form processing, document analysis

### Excel Parser
- **XLSX:** Extracts sheets, cells, formulas
- **CSV:** Parses delimited data
- **Use Cases:** Data migration, spreadsheet analysis

### Binary Parser (Mainframe)
- **ASCII:** Parses ASCII-encoded binary files with copybooks
- **EBCDIC:** Parses EBCDIC-encoded binary files with copybooks
- **Use Cases:** Legacy system migration, insurance policy processing

### Image Parser
- **OCR:** Extracts text from images
- **Metadata:** Extracts image metadata
- **Use Cases:** Document digitization, image analysis

### BPMN Parser
- **Workflow Extraction:** Extracts process definitions
- **Use Cases:** Workflow creation, process analysis

---

## Business Use Cases

### Use Case 1: Permit Data Extraction
**Scenario:** Extract structured data from PDF permits

**Flow:**
1. Upload PDF permit file
2. Call `parse_content` with file_id
3. Parser extracts permit number, date, location, etc.
4. Use parsed data for analysis

### Use Case 2: Insurance Policy Migration
**Scenario:** Extract data from 350k mainframe binary files

**Flow:**
1. Upload binary files with copybooks
2. Call `bulk_parse_files` (see [Bulk Operations](bulk_operations.md))
3. Parser extracts policy data using copybook definitions
4. Data is ready for migration

### Use Case 3: Spreadsheet Analysis
**Scenario:** Analyze Excel spreadsheet data

**Flow:**
1. Upload Excel file
2. Call `parse_content`
3. Parser extracts all sheets and cells
4. Use parsed data for analysis

---

## Error Handling

Parsing errors are handled gracefully:

```python
{
    "success": False,
    "error": "Parser error: <error_message>",
    "artifacts": {
        "file_id": "<file_uuid>",
        "parser_attempted": "<parser_name>",
        "error_details": {...}
    },
    "events": []
}
```

**Common Errors:**
- `Unsupported file type` - No parser available for file type
- `Parser error` - Parser failed to extract data
- `File corrupted` - File cannot be parsed

---

## Related Capabilities

- [Data Ingestion](data_ingestion.md) - Upload files to parse
- [Bulk Operations](bulk_operations.md) - Parse multiple files
- [Semantic Interpretation](../insights/semantic_interpretation.md) - Interpret parsed data

---

## API Reference

For complete API contracts, see [API Contracts](../execution/api_contracts_frontend_integration.md).

---

**Status:** ✅ Complete and Operational
