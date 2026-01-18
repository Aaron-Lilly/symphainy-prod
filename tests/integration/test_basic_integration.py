"""
Basic Integration Tests - Experience → Runtime → Realm Flow

Tests to verify basic intent flow works end-to-end.

WHAT (Test Role): I verify basic integration works
HOW (Test Implementation): I test intent submission from Experience to Runtime to Realm
"""

import pytest
import httpx
import asyncio
import os
from utilities import get_logger
from symphainy_platform.runtime.intent_model import IntentType

logger = get_logger("BasicIntegrationTests")

# Configuration from environment variables
RUNTIME_HOST = os.getenv("RUNTIME_HOST", "localhost")
RUNTIME_PORT = os.getenv("RUNTIME_PORT", "8000")
RUNTIME_URL = f"http://{RUNTIME_HOST}:{RUNTIME_PORT}"

EXPERIENCE_HOST = os.getenv("EXPERIENCE_HOST", "localhost")
EXPERIENCE_PORT = os.getenv("EXPERIENCE_PORT", "8001")
EXPERIENCE_URL = f"http://{EXPERIENCE_HOST}:{EXPERIENCE_PORT}"


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
async def experience_client():
    """Create HTTP client for Experience Plane service."""
    async with httpx.AsyncClient() as client:
        # Wait for Experience Plane to be healthy
        for _ in range(30):
            try:
                response = await client.get(f"{EXPERIENCE_URL}/health")
                if response.status_code == 200 and response.json().get("status") == "healthy":
                    logger.info("✅ Experience Plane is healthy!")
                    break
            except httpx.ConnectError:
                pass
            await asyncio.sleep(1)
        else:
            pytest.fail("Experience Plane did not become healthy in time.")
        yield client


@pytest.mark.asyncio
async def test_runtime_session_creation(runtime_client: httpx.AsyncClient):
    """Test session creation via Runtime API."""
    session_request = {
        "tenant_id": "test_tenant",
        "user_id": "test_user"
    }
    
    response = await runtime_client.post(
        f"{RUNTIME_URL}/api/session/create",
        json=session_request
    )
    
    assert response.status_code == 200
    session_data = response.json()
    
    assert "session_id" in session_data
    assert session_data["tenant_id"] == "test_tenant"
    assert session_data["user_id"] == "test_user"
    
    logger.info(f"✅ Session created via Runtime: {session_data['session_id']}")
    
    return session_data["session_id"]


@pytest.mark.asyncio
async def test_runtime_intent_submission(runtime_client: httpx.AsyncClient):
    """Test intent submission via Runtime API."""
    # First create a session
    session_request = {
        "tenant_id": "test_tenant",
        "user_id": "test_user"
    }
    
    session_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/session/create",
        json=session_request
    )
    assert session_response.status_code == 200
    session_id = session_response.json()["session_id"]
    
    # Submit intent
    intent_request = {
        "intent_type": IntentType.INGEST_FILE.value,
        "tenant_id": "test_tenant",
        "session_id": session_id,
        "solution_id": "default",
        "parameters": {
            "file_id": "test_file_123",
            "ui_name": "test.txt",
            "file_type": "txt",
            "file_content": "74657374"  # hex-encoded "test"
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
    assert "intent_id" in intent_data
    
    logger.info(f"✅ Intent submitted via Runtime: {intent_data['execution_id']}")
    
    return intent_data["execution_id"]


@pytest.mark.asyncio
async def test_runtime_execution_status(runtime_client: httpx.AsyncClient):
    """Test execution status retrieval via Runtime API."""
    # Create session and submit intent
    session_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/session/create",
        json={"tenant_id": "test_tenant", "user_id": "test_user"}
    )
    session_id = session_response.json()["session_id"]
    
    intent_response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": IntentType.INGEST_FILE.value,
            "tenant_id": "test_tenant",
            "session_id": session_id,
            "solution_id": "default",
            "parameters": {
                "file_id": "test_file_456",
                "ui_name": "test.txt",
                "file_type": "txt",
                "file_content": "74657374"  # hex-encoded "test"
            }
        }
    )
    execution_id = intent_response.json()["execution_id"]
    
    # Get execution status
    response = await runtime_client.get(
        f"{RUNTIME_URL}/api/execution/{execution_id}/status",
        params={"tenant_id": "test_tenant"}
    )
    
    assert response.status_code == 200
    status_data = response.json()
    
    assert "execution_id" in status_data
    assert "status" in status_data
    assert status_data["execution_id"] == execution_id
    
    logger.info(f"✅ Execution status retrieved: {status_data['status']}")


@pytest.mark.asyncio
async def test_experience_to_runtime_flow(experience_client: httpx.AsyncClient, runtime_client: httpx.AsyncClient):
    """Test Experience → Runtime flow (if Experience endpoints work)."""
    # This test will verify Experience can submit intents to Runtime
    # For now, we'll test that both services are accessible
    
    # Verify both services are healthy
    runtime_health = await runtime_client.get(f"{RUNTIME_URL}/health")
    experience_health = await experience_client.get(f"{EXPERIENCE_URL}/health")
    
    assert runtime_health.status_code == 200
    assert experience_health.status_code == 200
    
    logger.info("✅ Experience → Runtime connectivity verified (both services healthy)")
    
    # Note: Full intent submission via Experience will be tested once
    # Experience Plane dependencies are properly initialized
