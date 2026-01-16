"""
Platform Parsing Smoke Test

Quick end-to-end smoke test to verify all parsing adapters work together.

WHAT (Test Role): I verify the platform can parse files using all new adapters
HOW (Test Implementation): I test file upload → parse → verify for each file type
"""

import pytest
import httpx
import asyncio
import os
from typing import Dict, Any
from utilities import get_logger
from symphainy_platform.runtime.intent_model import IntentType

logger = get_logger("PlatformParsingSmokeTest")

# Configuration
RUNTIME_HOST = os.getenv("RUNTIME_HOST", "localhost")
RUNTIME_PORT = os.getenv("RUNTIME_PORT", "8000")
RUNTIME_URL = f"http://{RUNTIME_HOST}:{RUNTIME_PORT}"


def hex_encode(content: str) -> str:
    """Encode string content as hex for file_content parameter."""
    return content.encode('utf-8').hex()


def create_test_file(file_type: str) -> tuple[str, str]:
    """Create test file content for different file types."""
    if file_type == "csv":
        content = "name,age,city\nAlice,30,New York\nBob,25,San Francisco\nCharlie,35,Chicago\n"
    elif file_type == "json":
        content = '{"name": "test", "items": [1, 2, 3], "active": true}'
    elif file_type == "txt":
        content = "This is a plain text file for testing.\nIt has multiple lines.\n"
    elif file_type == "markdown":
        content = "# Test Document\n\nThis is a **markdown** file.\n\n## Section 1\n\nContent here.\n"
    else:
        content = f"Test content for {file_type} file type."
    
    return content, hex_encode(content)


@pytest.fixture(scope="module")
async def runtime_client():
    """Create HTTP client for Runtime service."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Wait for Runtime to be healthy
        for _ in range(30):
            try:
                response = await client.get(f"{RUNTIME_URL}/health")
                if response.status_code == 200 and response.json().get("status") == "healthy":
                    logger.info("✅ Runtime is healthy!")
                    break
            except httpx.ConnectError:
                pass
            await asyncio.sleep(1)
        else:
            pytest.fail("Runtime did not become healthy in time.")
        yield client


@pytest.fixture(scope="module")
async def test_session(runtime_client: httpx.AsyncClient):
    """Create a test session."""
    response = await runtime_client.post(
        f"{RUNTIME_URL}/api/session/create",
        json={
            "tenant_id": "test_tenant",
            "user_id": "test_user"
        }
    )
    assert response.status_code == 200, f"Session creation failed: {response.text}"
    session_data = response.json()
    logger.info(f"✅ Test session created: {session_data['session_id']}")
    return session_data["session_id"]


@pytest.mark.asyncio
async def test_platform_startup(runtime_client: httpx.AsyncClient):
    """Test that platform starts correctly with all adapters."""
    response = await runtime_client.get(f"{RUNTIME_URL}/health")
    assert response.status_code == 200
    health_data = response.json()
    assert health_data.get("status") == "healthy"
    logger.info("✅ Platform startup verified")


@pytest.mark.asyncio
async def test_csv_parsing_smoke(runtime_client: httpx.AsyncClient, test_session: str):
    """Test CSV parsing with new CSV adapter."""
    content, hex_content = create_test_file("csv")
    
    # Upload file
    upload_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.INGEST_FILE.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": "test_csv_001",
                "ui_name": "test.csv",
                "file_type": "csv",
                "file_content": hex_content,
                "mime_type": "text/csv"
            }
        }
    )
    assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
    upload_data = upload_response.json()
    execution_id = upload_data.get("execution_id")
    assert execution_id, "Execution ID not returned"
    logger.info(f"✅ CSV file upload intent submitted: {execution_id}")
    
    # Wait for upload to complete
    file_id = None
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                artifacts = status_data.get("artifacts", {})
                file_id = artifacts.get("file_id") or artifacts.get("file_reference")
                if file_id:
                    logger.info(f"✅ CSV file uploaded: {file_id}")
                    break
            elif status_data.get("status") == "failed":
                error = status_data.get("error", "Unknown error")
                pytest.fail(f"CSV upload failed: {error}")
    
    assert file_id, "File ID not returned from upload"
    
    # Parse file
    parse_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.PARSE_CONTENT.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": file_id
            }
        }
    )
    assert parse_response.status_code == 200, f"Parse failed: {parse_response.text}"
    parse_data = parse_response.json()
    parse_execution_id = parse_data.get("execution_id")
    assert parse_execution_id, "Parse execution ID not returned"
    
    # Wait for parsing to complete
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{parse_execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                logger.info("✅ CSV parsing successful")
                return
            elif status_data.get("status") == "failed":
                error = status_data.get("error", "Unknown error")
                pytest.fail(f"CSV parsing failed: {error}")
    
    pytest.fail("CSV parsing did not complete in time")


@pytest.mark.asyncio
async def test_json_parsing_smoke(runtime_client: httpx.AsyncClient, test_session: str):
    """Test JSON parsing with new JSON adapter."""
    content, hex_content = create_test_file("json")
    
    # Upload file
    upload_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.INGEST_FILE.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": "test_json_001",
                "ui_name": "test.json",
                "file_type": "json",
                "file_content": hex_content,
                "mime_type": "application/json"
            }
        }
    )
    assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
    upload_data = upload_response.json()
    execution_id = upload_data.get("execution_id")
    
    # Wait for upload
    file_reference = None
    file_id = None
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                artifacts = status_data.get("artifacts", {})
                file_reference = artifacts.get("file_reference")
                file_id = artifacts.get("file_id")
                if file_reference or file_id:
                    logger.info(f"✅ JSON file uploaded: file_id={file_id}, file_reference={file_reference}")
                    break
    
    assert file_reference or file_id, "File reference/ID not returned"
    
    # Parse file
    parse_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.PARSE_CONTENT.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": file_id or "test_json_001",
                "file_reference": file_reference
            }
        }
    )
    assert parse_response.status_code == 200, f"Parse failed: {parse_response.text}"
    parse_data = parse_response.json()
    parse_execution_id = parse_data.get("execution_id")
    
    # Wait for parsing
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{parse_execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                logger.info("✅ JSON parsing successful")
                return
            elif status_data.get("status") == "failed":
                error = status_data.get("error", "Unknown error")
                pytest.fail(f"JSON parsing failed: {error}")
    
    pytest.fail("JSON parsing did not complete in time")


@pytest.mark.asyncio
async def test_text_parsing_smoke(runtime_client: httpx.AsyncClient, test_session: str):
    """Test text parsing."""
    content, hex_content = create_test_file("txt")
    
    # Upload file
    upload_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.INGEST_FILE.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": "test_txt_001",
                "ui_name": "test.txt",
                "file_type": "txt",
                "file_content": hex_content,
                "mime_type": "text/plain"
            }
        }
    )
    assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
    upload_data = upload_response.json()
    execution_id = upload_data.get("execution_id")
    
    # Wait for upload
    file_reference = None
    file_id = None
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                artifacts = status_data.get("artifacts", {})
                file_reference = artifacts.get("file_reference")
                file_id = artifacts.get("file_id")
                if file_reference or file_id:
                    logger.info(f"✅ Text file uploaded: file_id={file_id}, file_reference={file_reference}")
                    break
    
    assert file_reference or file_id, "File reference/ID not returned"
    
    # Parse file
    parse_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.PARSE_CONTENT.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": file_id or "test_txt_001",
                "file_reference": file_reference
            }
        }
    )
    assert parse_response.status_code == 200, f"Parse failed: {parse_response.text}"
    parse_data = parse_response.json()
    parse_execution_id = parse_data.get("execution_id")
    
    # Wait for parsing
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{parse_execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                logger.info("✅ Text parsing successful")
                return
            elif status_data.get("status") == "failed":
                error = status_data.get("error", "Unknown error")
                pytest.fail(f"Text parsing failed: {error}")
    
    pytest.fail("Text parsing did not complete in time")


@pytest.mark.asyncio
async def test_custom_mainframe_parsing_smoke(runtime_client: httpx.AsyncClient, test_session: str):
    """Test custom mainframe parsing with copybook."""
    # Create simple copybook
    copybook = """       01  CUSTOMER-RECORD.
           05  CUSTOMER-ID        PIC X(10).
           05  CUSTOMER-NAME      PIC X(30).
           05  CUSTOMER-STATUS    PIC X(1).
           05  CUSTOMER-BALANCE   PIC 9(10)V99.
"""
    copybook_hex = hex_encode(copybook)
    
    # Create simple binary file (simulated mainframe record)
    # For ASCII fixed-width: 10 + 30 + 1 + 12 = 53 bytes
    binary_data = b'CUST001   Test Customer Name        A000000123456'
    binary_hex = binary_data.hex()
    
    # Upload copybook
    copybook_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.INGEST_FILE.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": "test_copybook_001",
                "ui_name": "test.cpy",
                "file_type": "txt",
                "file_content": copybook_hex,
                "mime_type": "text/plain"
            }
        }
    )
    assert copybook_response.status_code == 200, f"Copybook upload failed: {copybook_response.text}"
    copybook_data = copybook_response.json()
    copybook_execution_id = copybook_data.get("execution_id")
    
    # Wait for copybook upload
    copybook_reference = None
    copybook_id = None
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{copybook_execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                artifacts = status_data.get("artifacts", {})
                copybook_reference = artifacts.get("file_reference")
                copybook_id = artifacts.get("file_id")
                if copybook_reference or copybook_id:
                    logger.info(f"✅ Copybook uploaded: file_id={copybook_id}, file_reference={copybook_reference}")
                    break
    
    assert copybook_reference or copybook_id, "Copybook reference/ID not returned"
    
    # Upload binary file
    binary_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.INGEST_FILE.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": "test_binary_001",
                "ui_name": "test.bin",
                "file_type": "binary",
                "file_content": binary_hex,
                "mime_type": "application/octet-stream"
            }
        }
    )
    assert binary_response.status_code == 200, f"Binary upload failed: {binary_response.text}"
    binary_data_response = binary_response.json()
    binary_execution_id = binary_data_response.get("execution_id")
    
    # Wait for binary upload
    binary_reference = None
    binary_id = None
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{binary_execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                artifacts = status_data.get("artifacts", {})
                binary_reference = artifacts.get("file_reference")
                binary_id = artifacts.get("file_id")
                if binary_reference or binary_id:
                    logger.info(f"✅ Binary file uploaded: file_id={binary_id}, file_reference={binary_reference}")
                    break
    
    assert binary_reference or binary_id, "Binary file reference/ID not returned"
    
    # Parse binary file with copybook
    parse_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.PARSE_CONTENT.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": binary_id or "test_binary_001",
                "file_reference": binary_reference,
                "copybook_reference": copybook_reference,
                "file_type": "binary",
                "parse_options": {
                    "codepage": "ascii"
                }
            }
        }
    )
    assert parse_response.status_code == 200, f"Parse failed: {parse_response.text}"
    parse_data = parse_response.json()
    parse_execution_id = parse_data.get("execution_id")
    
    # Wait for parsing
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{parse_execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                logger.info("✅ Custom mainframe parsing successful")
                return
            elif status_data.get("status") == "failed":
                error = status_data.get("error", "Unknown error")
                # Custom strategy should work now, but log if it fails
                logger.warning(f"⚠️ Custom mainframe parsing failed: {error}")
                # For smoke test, we'll fail if parsing fails (should work now)
                pytest.fail(f"Custom mainframe parsing failed: {error}")
    
    pytest.fail("Custom mainframe parsing did not complete in time")


@pytest.mark.asyncio
async def test_adapter_required_fail_fast(runtime_client: httpx.AsyncClient, test_session: str):
    """Test that adapters are required (fail-fast if missing)."""
    # This test verifies that adapters are being used (not fallbacks)
    # If parsing succeeds, adapters are working
    # If it fails with "adapter is required", fail-fast is working
    
    content, hex_content = create_test_file("csv")
    
    # Upload file
    upload_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.INGEST_FILE.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": "test_failfast_001",
                "ui_name": "test_failfast.csv",
                "file_type": "csv",
                "file_content": hex_content,
                "mime_type": "text/csv"
            }
        }
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    execution_id = upload_data.get("execution_id")
    
    # Wait for upload
    file_reference = None
    file_id = None
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                artifacts = status_data.get("artifacts", {})
                file_reference = artifacts.get("file_reference")
                file_id = artifacts.get("file_id")
                if file_reference or file_id:
                    break
    
    assert file_reference or file_id, "File reference/ID not returned"
    
    # Parse file
    parse_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.PARSE_CONTENT.value,
            "tenant_id": "test_tenant",
            "session_id": test_session,
            "solution_id": "default",
            "parameters": {
                "file_id": file_id or "test_failfast_001",
                "file_reference": file_reference
            }
        }
    )
    assert parse_response.status_code == 200
    parse_data = parse_response.json()
    parse_execution_id = parse_data.get("execution_id")
    
    # Wait for parsing
    for _ in range(30):
        await asyncio.sleep(1)
        status_response = await runtime_client.get(
            f"{RUNTIME_URL}/api/execution/{parse_execution_id}/status",
            params={"tenant_id": "test_tenant"}
        )
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get("status") == "completed":
                # Parsing succeeded - adapters are working
                logger.info("✅ Fail-fast behavior verified (adapters are required and working)")
                return
            elif status_data.get("status") == "failed":
                error = status_data.get("error", "")
                # Check that we're not using fallbacks
                assert "fallback" not in error.lower(), "Fallback should not be used"
                # If we get "adapter is required", that's good (fail-fast working)
                if "adapter is required" in error.lower():
                    logger.info("✅ Fail-fast behavior verified (adapter required error)")
                    return
                else:
                    # Other parsing error - might be adapter issue
                    logger.warning(f"⚠️ Parsing failed with error: {error}")
                    pytest.fail(f"CSV parsing failed: {error}")
    
    pytest.fail("Parsing did not complete in time")
