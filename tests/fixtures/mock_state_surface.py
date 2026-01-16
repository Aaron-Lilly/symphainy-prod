"""
Mock State Surface for Testing

Comprehensive mock implementation of StateSurface for use across all tests.
Provides in-memory storage for files, metadata, sessions, and execution state.

WHAT (Test Fixture): I provide a complete State Surface mock for testing
HOW (Mock Implementation): I use in-memory dictionaries to simulate State Surface behavior
"""

from typing import Dict, Any, Optional
from datetime import datetime
from unittest.mock import AsyncMock


class MockStateSurface:
    """
    Mock State Surface for testing.
    
    Provides in-memory storage for:
    - File data (file_reference -> bytes)
    - File metadata (file_reference -> metadata dict)
    - Session state (session_id -> state dict)
    - Execution state (execution_id -> state dict)
    
    All methods are async-compatible and match the real StateSurface interface.
    """
    
    def __init__(self):
        """Initialize mock State Surface with empty stores."""
        self._file_store: Dict[str, bytes] = {}
        self._file_metadata_store: Dict[str, Dict[str, Any]] = {}
        self._session_store: Dict[str, Dict[str, Any]] = {}
        self._execution_store: Dict[str, Dict[str, Any]] = {}
        self._clock = lambda: datetime.utcnow().isoformat()
    
    # ============================================================================
    # FILE MANAGEMENT
    # ============================================================================
    
    async def get_file(self, file_reference: str) -> Optional[bytes]:
        """
        Retrieve file data by file reference.
        
        Args:
            file_reference: File reference string (e.g., "file:tenant:session:file_id")
        
        Returns:
            File data as bytes or None if not found
        """
        return self._file_store.get(file_reference)
    
    async def get_file_metadata(self, file_reference: str) -> Optional[Dict[str, Any]]:
        """
        Get file metadata by file reference.
        
        Args:
            file_reference: File reference string
        
        Returns:
            File metadata dictionary or None if not found
        """
        return self._file_metadata_store.get(file_reference)
    
    async def store_file_reference(
        self,
        session_id: str,
        tenant_id: str,
        file_reference: str,
        storage_location: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store file reference and metadata.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
            file_reference: File reference string
            storage_location: Storage location (for mock, can be same as file_reference)
            filename: Original filename
            metadata: Optional file metadata
        
        Returns:
            File reference string
        """
        file_state = {
            "storage_location": storage_location,
            "filename": filename,
            "size": metadata.get("size") if metadata else None,
            "file_hash": metadata.get("file_hash") if metadata else None,
            "ui_name": metadata.get("ui_name", filename) if metadata else filename,
            "file_type": metadata.get("file_type") if metadata else None,
            "content_type": metadata.get("content_type") if metadata else None,
            "metadata": metadata or {},
            "created_at": self._clock()
        }
        
        self._file_metadata_store[file_reference] = file_state
        return file_reference
    
    def store_file_data(self, file_reference: str, file_data: bytes, metadata: Optional[Dict[str, Any]] = None):
        """
        Store file data directly (helper method for tests).
        
        Args:
            file_reference: File reference string
            file_data: File data as bytes
            metadata: Optional file metadata
        """
        self._file_store[file_reference] = file_data
        
        if metadata:
            self._file_metadata_store[file_reference] = {
                "storage_location": file_reference,  # Mock storage location
                "filename": metadata.get("filename", "unknown"),
                "size": len(file_data),
                "file_hash": metadata.get("file_hash"),
                "ui_name": metadata.get("ui_name", metadata.get("filename", "unknown")),
                "file_type": metadata.get("file_type"),
                "content_type": metadata.get("content_type"),
                "metadata": metadata,
                "created_at": self._clock()
            }
        else:
            # Create minimal metadata if not provided
            self._file_metadata_store[file_reference] = {
                "storage_location": file_reference,
                "filename": "unknown",
                "size": len(file_data),
                "created_at": self._clock()
            }
    
    # ============================================================================
    # SESSION STATE MANAGEMENT
    # ============================================================================
    
    async def get_session_state(
        self,
        session_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get session state.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
        
        Returns:
            Session state dictionary or None if not found
        """
        state_id = f"session:{tenant_id}:{session_id}"
        return self._session_store.get(state_id)
    
    async def set_session_state(
        self,
        session_id: str,
        tenant_id: str,
        state: Dict[str, Any]
    ) -> bool:
        """
        Set session state.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
            state: State dictionary
        
        Returns:
            True if successful
        """
        state_id = f"session:{tenant_id}:{session_id}"
        state["updated_at"] = self._clock()
        self._session_store[state_id] = state
        return True
    
    # ============================================================================
    # EXECUTION STATE MANAGEMENT
    # ============================================================================
    
    async def get_execution_state(
        self,
        execution_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get execution state.
        
        Args:
            execution_id: Execution identifier
            tenant_id: Tenant identifier
        
        Returns:
            Execution state dictionary or None if not found
        """
        state_id = f"execution:{tenant_id}:{execution_id}"
        return self._execution_store.get(state_id)
    
    async def set_execution_state(
        self,
        execution_id: str,
        tenant_id: str,
        state: Dict[str, Any]
    ) -> bool:
        """
        Set execution state.
        
        Args:
            execution_id: Execution identifier
            tenant_id: Tenant identifier
            state: State dictionary
        
        Returns:
            True if successful
        """
        state_id = f"execution:{tenant_id}:{execution_id}"
        state["updated_at"] = self._clock()
        self._execution_store[state_id] = state
        return True
    
    # ============================================================================
    # HELPER METHODS FOR TESTS
    # ============================================================================
    
    def clear(self):
        """Clear all stored data (useful for test cleanup)."""
        self._file_store.clear()
        self._file_metadata_store.clear()
        self._session_store.clear()
        self._execution_store.clear()
    
    def get_all_files(self) -> Dict[str, bytes]:
        """Get all stored files (for test verification)."""
        return self._file_store.copy()
    
    def get_all_file_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get all stored file metadata (for test verification)."""
        return self._file_metadata_store.copy()
    
    def has_file(self, file_reference: str) -> bool:
        """Check if file exists (for test verification)."""
        return file_reference in self._file_store
    
    def has_file_metadata(self, file_reference: str) -> bool:
        """Check if file metadata exists (for test verification)."""
        return file_reference in self._file_metadata_store


# Pytest fixture for easy use in tests
import pytest


@pytest.fixture
def mock_state_surface():
    """
    Pytest fixture providing a MockStateSurface instance.
    
    Usage:
        async def test_something(mock_state_surface):
            mock_state_surface.store_file_data("file:test:session:123", b"test data")
            result = await some_function(mock_state_surface)
    """
    return MockStateSurface()
