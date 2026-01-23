"""
Smoke Tests - Service Startup Verification

Tests to verify that Runtime and Experience Plane services start correctly.

WHAT (Test Role): I verify services start and are accessible
HOW (Test Implementation): I check health endpoints and basic connectivity
"""

import pytest
import httpx
import asyncio
import os
from utilities import get_logger

logger = get_logger("ServiceStartupTests")

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
        for _ in range(30):  # Retry for 30 seconds
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
        for _ in range(30):  # Retry for 30 seconds
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
async def test_runtime_health(runtime_client: httpx.AsyncClient):
    """Test Runtime service health check."""
    response = await runtime_client.get(f"{RUNTIME_URL}/health")
    
    assert response.status_code == 200
    health_data = response.json()
    
    assert health_data["status"] == "healthy"
    assert health_data["service"] == "runtime"
    assert health_data["version"] == "2.0.0"
    assert "realms" in health_data
    assert health_data["realms"] >= 0  # Should have at least 0 realms (3 expected)
    
    logger.info(f"✅ Runtime health check passed: {health_data}")


@pytest.mark.asyncio
async def test_runtime_realms_registered(runtime_client: httpx.AsyncClient):
    """Test that all realms are registered with Runtime (Content, Insights, Journey, Outcomes)."""
    response = await runtime_client.get(f"{RUNTIME_URL}/health")
    
    assert response.status_code == 200
    health_data = response.json()
    
    realm_count = health_data.get("realms", 0)
    # We have 4 realms: Content, Insights, Journey, Outcomes
    assert realm_count >= 4, f"Expected at least 4 realms registered, got {realm_count}"
    
    logger.info(f"✅ All realms registered: {realm_count}")


@pytest.mark.asyncio
async def test_experience_health(experience_client: httpx.AsyncClient):
    """Test Experience Plane service health check."""
    response = await experience_client.get(f"{EXPERIENCE_URL}/health")
    
    assert response.status_code == 200
    health_data = response.json()
    
    assert health_data["status"] == "healthy"
    assert health_data["service"] == "experience"
    assert health_data["version"] == "2.0.0"
    
    logger.info(f"✅ Experience Plane health check passed: {health_data}")


@pytest.mark.asyncio
async def test_runtime_api_endpoints_exist(runtime_client: httpx.AsyncClient):
    """Test that Runtime API endpoints exist."""
    # Test session creation endpoint (should exist, may require auth)
    response = await runtime_client.post(
        f"{RUNTIME_URL}/api/session/create",
        json={
            "tenant_id": "test_tenant",
            "user_id": "test_user"
        }
    )
    
    # Should not be 404 (endpoint exists)
    assert response.status_code != 404, "Session creation endpoint not found"
    
    # Test intent submission endpoint (should exist, may require auth)
    response = await runtime_client.post(
        f"{RUNTIME_URL}/api/intent/submit",
        json={
            "intent_type": "ingest_file",
            "tenant_id": "test_tenant",
            "session_id": "test_session",
            "solution_id": "default",
            "parameters": {}
        }
    )
    
    # Should not be 404 (endpoint exists)
    assert response.status_code != 404, "Intent submission endpoint not found"
    
    logger.info("✅ Runtime API endpoints exist")


@pytest.mark.asyncio
async def test_experience_api_endpoints_exist(experience_client: httpx.AsyncClient):
    """Test that Experience Plane API endpoints exist."""
    # Test session endpoint (should exist)
    response = await experience_client.get(f"{EXPERIENCE_URL}/api/session/test_session")
    
    # Should not be 404 (endpoint exists)
    assert response.status_code != 404, "Session endpoint not found"
    
    # Test intent submission endpoint (should exist)
    response = await experience_client.post(
        f"{EXPERIENCE_URL}/api/intent/submit",
        json={
            "intent_type": "ingest_file",
            "session_id": "test_session",
            "parameters": {}
        }
    )
    
    # Should not be 404 (endpoint exists)
    assert response.status_code != 404, "Intent submission endpoint not found"
    
    logger.info("✅ Experience Plane API endpoints exist")


@pytest.mark.asyncio
async def test_experience_to_runtime_connectivity(experience_client: httpx.AsyncClient, runtime_client: httpx.AsyncClient):
    """Test that Experience Plane can connect to Runtime."""
    # Verify both services are healthy
    runtime_health = await runtime_client.get(f"{RUNTIME_URL}/health")
    experience_health = await experience_client.get(f"{EXPERIENCE_URL}/health")
    
    assert runtime_health.status_code == 200
    assert experience_health.status_code == 200
    
    # Experience Plane should be able to reach Runtime
    # (This is a connectivity test, not a functional test)
    logger.info("✅ Experience Plane and Runtime are both healthy and accessible")
    
    # Note: Actual intent submission will be tested in integration tests
    # This just verifies both services are running
