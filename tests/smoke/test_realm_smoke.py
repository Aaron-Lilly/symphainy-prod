"""
Realm Smoke Tests - Basic Intent Handling Verification

Tests to verify each realm can handle basic intents.

WHAT (Test Role): I verify realms can process basic intents
HOW (Test Implementation): I submit minimal intents to each realm via Runtime
"""

import pytest
import httpx
import asyncio
import os
from utilities import get_logger
from symphainy_platform.runtime.intent_model import IntentType

logger = get_logger("RealmSmokeTests")

# Configuration from environment variables
RUNTIME_HOST = os.getenv("RUNTIME_HOST", "localhost")
RUNTIME_PORT = os.getenv("RUNTIME_PORT", "8000")
RUNTIME_URL = f"http://{RUNTIME_HOST}:{RUNTIME_PORT}"


@pytest.fixture(scope="module")
async def runtime_client():
    """Create HTTP client for Runtime service."""
    async with httpx.AsyncClient() as client:
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
    assert response.status_code == 200
    session_data = response.json()
    return session_data["session_id"]


@pytest.mark.asyncio
async def test_content_realm_ingest_file(runtime_client: httpx.AsyncClient, test_session: str):
    """Test Content Realm can handle ingest_file intent."""
    intent_request = {
        "intent_type": IntentType.INGEST_FILE.value,
        "tenant_id": "test_tenant",
        "session_id": test_session,
        "solution_id": "default",
        "parameters": {
            "file_id": "test_file_smoke_1",
            "ui_name": "smoke_test.txt",
            "file_type": "txt",
            "file_content": "54686973206973206120736d6f6b6520746573742066696c652e",  # hex-encoded "This is a smoke test file."
            "mime_type": "text/plain"
        }
    }
    
    response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json=intent_request
    )
    
    assert response.status_code == 200
    intent_data = response.json()
    
    assert intent_data["status"] == "accepted"
    assert "execution_id" in intent_data
    
    logger.info(f"✅ Content Realm ingest_file intent accepted: {intent_data['execution_id']}")


@pytest.mark.asyncio
async def test_insights_realm_analyze_content(runtime_client: httpx.AsyncClient, test_session: str):
    """Test Insights Realm can handle analyze_content intent."""
    intent_request = {
        "intent_type": IntentType.ANALYZE_CONTENT.value,
        "tenant_id": "test_tenant",
        "session_id": test_session,
        "solution_id": "default",
        "parameters": {
            "parsed_file_id": "test_parsed_file_smoke_1"
        }
    }
    
    response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json=intent_request
    )
    
    assert response.status_code == 200
    intent_data = response.json()
    
    assert intent_data["status"] == "accepted"
    assert "execution_id" in intent_data
    
    logger.info(f"✅ Insights Realm analyze_content intent accepted: {intent_data['execution_id']}")


@pytest.mark.asyncio
async def test_operations_realm_optimize_process(runtime_client: httpx.AsyncClient, test_session: str):
    """Test Operations Realm can handle optimize_process intent."""
    intent_request = {
        "intent_type": IntentType.OPTIMIZE_PROCESS.value,
        "tenant_id": "test_tenant",
        "session_id": test_session,
        "solution_id": "default",
        "parameters": {
            "workflow_id": "test_workflow_smoke_1"
        }
    }
    
    response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json=intent_request
    )
    
    assert response.status_code == 200
    intent_data = response.json()
    
    assert intent_data["status"] == "accepted"
    assert "execution_id" in intent_data
    
    logger.info(f"✅ Operations Realm optimize_process intent accepted: {intent_data['execution_id']}")


@pytest.mark.asyncio
async def test_outcomes_realm_synthesize_outcome(runtime_client: httpx.AsyncClient, test_session: str):
    """Test Outcomes Realm can handle synthesize_outcome intent."""
    intent_request = {
        "intent_type": IntentType.SYNTHESIZE_OUTCOME.value,
        "tenant_id": "test_tenant",
        "session_id": test_session,
        "solution_id": "default",
        "parameters": {}
    }
    
    response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json=intent_request
    )
    
    assert response.status_code == 200
    intent_data = response.json()
    
    assert intent_data["status"] == "accepted"
    assert "execution_id" in intent_data
    
    logger.info(f"✅ Outcomes Realm synthesize_outcome intent accepted: {intent_data['execution_id']}")
