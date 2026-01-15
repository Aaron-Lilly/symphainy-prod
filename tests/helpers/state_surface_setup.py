"""
State Surface Setup for Testing

Provides fixtures and utilities for creating in-memory State Surface
for testing without GCS/Supabase dependencies.
"""

import pytest
from typing import Dict, Any, Optional
from symphainy_platform.runtime.state_surface import StateSurface


@pytest.fixture
async def in_memory_state_surface():
    """
    Create in-memory State Surface for testing.
    
    Uses use_memory=True to avoid GCS/Supabase dependencies.
    - State metadata stored in memory
    - File data stored in InMemoryFileStorage (not in State Surface)
    
    Yields:
        StateSurface instance with in-memory storage
    """
    # InMemoryFileStorage will be created automatically by StateSurface when use_memory=True
    state_surface = StateSurface(use_memory=True)
    yield state_surface
    
    # Cleanup (if needed)
    # In-memory storage is automatically cleaned up when fixture goes out of scope


@pytest.fixture
async def test_session_context():
    """
    Create test session context.
    
    Returns:
        Dictionary with session_id and tenant_id
    """
    return {
        "session_id": "test_session_123",
        "tenant_id": "test_tenant_456"
    }


async def store_test_file(
    state_surface: StateSurface,
    file_data: bytes,
    filename: str,
    session_id: str = "test_session",
    tenant_id: str = "test_tenant",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Store a test file in State Surface.
    
    Args:
        state_surface: State Surface instance
        file_data: File data as bytes
        filename: Filename
        session_id: Session ID
        tenant_id: Tenant ID
        metadata: Optional file metadata
        
    Returns:
        File reference string
    """
    file_ref = await state_surface.store_file(
        session_id=session_id,
        tenant_id=tenant_id,
        file_data=file_data,
        filename=filename,
        metadata=metadata
    )
    return file_ref


async def retrieve_test_file(
    state_surface: StateSurface,
    file_reference: str
) -> Optional[bytes]:
    """
    Retrieve a test file from State Surface.
    
    Args:
        state_surface: State Surface instance
        file_reference: File reference string
        
    Returns:
        File data as bytes, or None if not found
    """
    return await state_surface.get_file(file_reference)


async def store_test_files(
    state_surface: StateSurface,
    files: Dict[str, bytes],
    session_id: str = "test_session",
    tenant_id: str = "test_tenant"
) -> Dict[str, str]:
    """
    Store multiple test files in State Surface.
    
    Args:
        state_surface: State Surface instance
        files: Dictionary mapping filenames to file data
        session_id: Session ID
        tenant_id: Tenant ID
        
    Returns:
        Dictionary mapping filenames to file references
    """
    file_refs = {}
    for filename, file_data in files.items():
        file_ref = await store_test_file(
            state_surface=state_surface,
            file_data=file_data,
            filename=filename,
            session_id=session_id,
            tenant_id=tenant_id
        )
        file_refs[filename] = file_ref
    return file_refs
