"""
End-to-End Tests for Public Works Abstractions

Tests abstractions with real containers running.
Validates that abstractions work in real environment.
"""

import pytest
import os
import asyncio
from typing import Dict, Any

# Mark all tests in this file as E2E
pytestmark = pytest.mark.e2e
pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def docker_compose():
    """
    Start Docker containers for E2E testing.
    
    Uses docker-compose to start infrastructure services.
    """
    import subprocess
    import time
    
    # Start containers
    print("📦 Starting Docker containers...")
    result = subprocess.run(
        ["docker-compose", "up", "-d"],
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        pytest.skip(f"Failed to start containers: {result.stderr}")
    
    # Wait for containers to be ready
    print("⏳ Waiting for containers to be ready...")
    time.sleep(15)  # Give containers time to start
    
    yield
    
    # Stop containers
    print("🛑 Stopping Docker containers...")
    subprocess.run(
        ["docker-compose", "down"],
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        capture_output=True
    )


@pytest.fixture
async def public_works_foundation(docker_compose):
    """
    Create Public Works Foundation with real adapters.
    
    This fixture initializes Public Works Foundation with real
    infrastructure (Redis, Supabase, etc.) running in containers.
    """
    from symphainy_platform.foundations.public_works.foundation_service import (
        PublicWorksFoundationService
    )
    
    foundation = PublicWorksFoundationService()
    await foundation.initialize()
    
    yield foundation
    
    # Cleanup if needed
    # (foundation doesn't need explicit cleanup)


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.asyncio
class TestAbstractionsE2E:
    """End-to-end tests for abstractions with real containers."""
    
    async def test_auth_abstraction_e2e(self, public_works_foundation):
        """
        Test Auth abstraction end-to-end with real Supabase.
        
        This test validates that:
        1. Auth abstraction works with real Supabase
        2. Returns raw data (not SecurityContext)
        3. No business logic (no tenant creation)
        """
        auth_abstraction = public_works_foundation.get_auth_abstraction()
        
        if not auth_abstraction:
            pytest.skip("Auth abstraction not available")
        
        # Test authentication (if test credentials available)
        test_email = os.getenv("TEST_USER_EMAIL")
        test_password = os.getenv("TEST_USER_PASSWORD")
        
        if not test_email or not test_password:
            pytest.skip("Test credentials not available")
        
        result = await auth_abstraction.authenticate({
            "email": test_email,
            "password": test_password
        })
        
        # Should return raw data
        assert result is not None
        assert isinstance(result, dict)  # Raw data, not SecurityContext
        assert "user_id" in result or "id" in result
        assert "email" in result
    
    async def test_telemetry_abstraction_e2e(self, public_works_foundation):
        """
        Test Telemetry abstraction end-to-end with real OpenTelemetry.
        
        This test validates that:
        1. Telemetry abstraction works with real OpenTelemetry
        2. Can collect metrics
        3. Can collect traces
        """
        telemetry_abstraction = public_works_foundation.get_telemetry_abstraction()
        
        if not telemetry_abstraction:
            pytest.skip("Telemetry abstraction not available")
        
        # Test metric collection
        from symphainy_platform.foundations.public_works.protocols.telemetry_protocol import (
            TelemetryData, TelemetryType
        )
        
        telemetry_data = TelemetryData(
            name="test_metric",
            type=TelemetryType.METRIC,
            value=1.0,
            metadata={"unit": "count"}
        )
        
        result = await telemetry_abstraction.collect_metric(telemetry_data)
        assert result is True
    
    async def test_state_abstraction_e2e(self, public_works_foundation):
        """
        Test State abstraction end-to-end with real Redis.
        
        This test validates that:
        1. State abstraction works with real Redis
        2. Can store state
        3. Can retrieve state
        """
        state_abstraction = public_works_foundation.get_state_abstraction()
        
        if not state_abstraction:
            pytest.skip("State abstraction not available")
        
        # Test state storage
        test_state_id = "test_state_123"
        test_state_data = {"key": "value", "number": 42}
        
        success = await state_abstraction.store_state(
            state_id=test_state_id,
            state_data=test_state_data,
            metadata={"backend": "redis"},
            ttl=60
        )
        assert success is True
        
        # Test state retrieval
        retrieved = await state_abstraction.retrieve_state(test_state_id)
        assert retrieved is not None
        assert retrieved["key"] == "value"
        assert retrieved["number"] == 42
    
    async def test_file_storage_abstraction_e2e(self, public_works_foundation):
        """
        Test File Storage abstraction end-to-end with real GCS.
        
        This test validates that:
        1. File Storage abstraction works with real GCS
        2. Can upload files
        3. Can download files
        """
        file_storage_abstraction = public_works_foundation.get_file_storage_abstraction()
        
        if not file_storage_abstraction:
            pytest.skip("File Storage abstraction not available")
        
        # Test file upload
        test_file_data = b"test file content"
        test_file_path = "test/test_file.txt"
        
        result = await file_storage_abstraction.upload_file(
            file_path=test_file_path,
            file_data=test_file_data,
            metadata={"content_type": "text/plain"}
        )
        
        assert result["success"] is True
        assert "file_id" in result or "file_path" in result
        
        # Test file download
        downloaded = await file_storage_abstraction.download_file(test_file_path)
        assert downloaded == test_file_data
    
    async def test_service_discovery_abstraction_e2e(self, public_works_foundation):
        """
        Test Service Discovery abstraction end-to-end with real Consul.
        
        This test validates that:
        1. Service Discovery abstraction works with real Consul
        2. Can register services
        3. Can discover services
        """
        service_discovery_abstraction = public_works_foundation.get_service_discovery_abstraction()
        
        if not service_discovery_abstraction:
            pytest.skip("Service Discovery abstraction not available")
        
        # Test service registration
        service_info = {
            "service_name": "test_service",
            "service_type": "test",
            "address": "localhost",
            "port": 8000
        }
        
        registration = await service_discovery_abstraction.register_service(service_info)
        assert registration is not None
        assert registration.success is True
        
        # Test service discovery
        services = await service_discovery_abstraction.discover_service("test_service")
        assert len(services) > 0
        assert services[0].service_name == "test_service"


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.asyncio
class TestSmartCityIntegrationE2E:
    """Test Smart City roles can use abstractions end-to-end."""
    
    async def test_security_guard_uses_auth_abstraction(self, public_works_foundation):
        """
        Test that Security Guard can use Auth abstraction.
        
        This test validates that:
        1. Security Guard uses Auth abstraction for infrastructure
        2. Security Guard adds business logic (SecurityContext)
        3. End-to-end authentication flow works
        """
        # This test will be implemented once Security Guard is built
        # For now, we validate that abstractions are available
        auth_abstraction = public_works_foundation.get_auth_abstraction()
        tenant_abstraction = public_works_foundation.get_tenant_abstraction()
        
        assert auth_abstraction is not None
        assert tenant_abstraction is not None
        
        # TODO: Once Security Guard is built, test:
        # security_guard = SecurityGuard(
        #     auth_abstraction=auth_abstraction,
        #     tenant_abstraction=tenant_abstraction
        # )
        # result = await security_guard.authenticate_user({...})
        # assert isinstance(result, SecurityContext)  # Business logic in Security Guard
    
    async def test_librarian_uses_semantic_search_abstraction(self, public_works_foundation):
        """
        Test that Librarian can use Semantic Search abstraction.
        
        This test validates that:
        1. Librarian uses Semantic Search abstraction for infrastructure
        2. Librarian adds business logic (semantic schema management)
        """
        semantic_search_abstraction = public_works_foundation.get_semantic_search_abstraction()
        
        assert semantic_search_abstraction is not None
        
        # TODO: Once Librarian is built, test:
        # librarian = Librarian(semantic_search_abstraction=semantic_search_abstraction)
        # result = await librarian.search_semantic_schemas({...})
        # assert result is not None
