"""
Runtime State Surface - Centralized Execution State

Runtime-owned state surface that coordinates all state operations.
Uses Public Works StateManagementAbstraction for swappable backends.

WHAT (Runtime Role): I provide centralized execution state management
HOW (Runtime Implementation): I use Public Works StateManagementAbstraction
"""

from typing import Dict, Any, Optional, List

from utilities import get_logger, get_clock
from symphainy_platform.foundations.public_works.protocols.state_protocol import StateManagementProtocol
from symphainy_platform.foundations.public_works.protocols.file_storage_protocol import FileStorageProtocol


class StateSurface:
    """
    Centralized recording of execution state.
    
    Runtime-owned state surface that coordinates all state operations.
    Uses Public Works StateManagementAbstraction for swappable backends.
    In-memory fallback for tests.
    """
    
    def __init__(
        self,
        state_abstraction: Optional[StateManagementProtocol] = None,
        file_storage: Optional[FileStorageProtocol] = None,
        use_memory: bool = False
    ):
        """
        Initialize state surface.
        
        Args:
            state_abstraction: Optional state management abstraction (from Public Works)
            file_storage: Optional file storage abstraction (for file retrieval)
            use_memory: If True, use in-memory storage (for tests)
        """
        self.use_memory = use_memory
        self.state_abstraction = state_abstraction
        self.file_storage = file_storage
        self._memory_store: Dict[str, Any] = {}
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def get_execution_state(
        self,
        execution_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get execution state.
        
        Args:
            execution_id: Execution identifier
            tenant_id: Tenant identifier (for isolation)
        
        Returns:
            Execution state dictionary or None if not found
        """
        state_id = f"execution:{tenant_id}:{execution_id}"
        
        if self.use_memory:
            return self._memory_store.get(state_id)
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            return self._memory_store.get(state_id)
        
        try:
            state_data = await self.state_abstraction.retrieve_state(state_id)
            return state_data
        except Exception as e:
            self.logger.error(f"Failed to retrieve execution state: {e}", exc_info=True)
            return None
    
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
            tenant_id: Tenant identifier (for isolation)
            state: State dictionary
        
        Returns:
            True if successful
        """
        state_id = f"execution:{tenant_id}:{execution_id}"
        state["updated_at"] = self.clock.now_iso()
        
        if self.use_memory:
            self._memory_store[state_id] = state
            return True
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            self._memory_store[state_id] = state
            return True
        
        try:
            success = await self.state_abstraction.store_state(
                state_id,
                state,
                metadata={"type": "execution_state", "tenant_id": tenant_id},
                ttl=3600  # 1 hour TTL for hot state
            )
            return success
        except Exception as e:
            self.logger.error(f"Failed to store execution state: {e}", exc_info=True)
            return False
    
    async def get_session_state(
        self,
        session_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get session state.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier (for isolation)
        
        Returns:
            Session state dictionary or None if not found
        """
        state_id = f"session:{tenant_id}:{session_id}"
        
        if self.use_memory:
            return self._memory_store.get(state_id)
        
        if not self.state_abstraction:
            return self._memory_store.get(state_id)
        
        try:
            state_data = await self.state_abstraction.retrieve_state(state_id)
            return state_data
        except Exception as e:
            self.logger.error(f"Failed to retrieve session state: {e}", exc_info=True)
            return None
    
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
            tenant_id: Tenant identifier (for isolation)
            state: State dictionary
        
        Returns:
            True if successful
        """
        state_id = f"session:{tenant_id}:{session_id}"
        state["updated_at"] = self.clock.now_iso()
        
        if self.use_memory:
            self._memory_store[state_id] = state
            return True
        
        if not self.state_abstraction:
            self._memory_store[state_id] = state
            return True
        
        try:
            success = await self.state_abstraction.store_state(
                state_id,
                state,
                metadata={"type": "session_state", "tenant_id": tenant_id},
                ttl=86400  # 24 hour TTL
            )
            return success
        except Exception as e:
            self.logger.error(f"Failed to store session state: {e}", exc_info=True)
            return False
    
    # ============================================================================
    # FILE REFERENCE MANAGEMENT
    # ============================================================================
    
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
        Store file reference in State Surface (file already stored in FileStorageAbstraction).
        
        Architecture:
        - State Surface stores file references and metadata, NOT file data
        - File data is stored in FileStorageAbstraction (GCS, etc.)
        - This method registers the file reference for execution context
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier (for isolation)
            file_reference: File reference string (e.g., "file:tenant:session:file_id")
            storage_location: Where file is stored (GCS path, etc.)
            filename: Original filename
            metadata: Optional file metadata (e.g., {"content_type": "application/pdf", "size": 12345, "ui_name": "..."})
        
        Returns:
            File reference string (same as input)
        """
        # Store only metadata/reference in State Surface (NOT file data)
        file_state = {
            "storage_location": storage_location,
            "filename": filename,
            "size": metadata.get("size") if metadata else None,
            "file_hash": metadata.get("file_hash") if metadata else None,
            "ui_name": metadata.get("ui_name", filename) if metadata else filename,
            "file_type": metadata.get("file_type") if metadata else None,
            "content_type": metadata.get("content_type") if metadata else None,
            "metadata": metadata or {},
            "created_at": self.clock.now_iso()
        }
        
        # Store metadata in State Surface
        state_id = file_reference
        
        if self.use_memory:
            self._memory_store[state_id] = file_state
            self.logger.debug(f"File reference stored (memory): {file_reference} -> {storage_location}")
            return file_reference
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            self._memory_store[state_id] = file_state
            return file_reference
        
        try:
            success = await self.state_abstraction.store_state(
                state_id=state_id,
                state_data=file_state,
                metadata={
                    "type": "file_metadata",
                    "tenant_id": tenant_id,
                    "session_id": session_id
                },
                ttl=86400  # 24 hour TTL for file metadata
            )
            
            if success:
                self.logger.debug(f"File reference stored: {file_reference} -> {storage_location}")
            else:
                self.logger.warning(f"Failed to store file reference, using in-memory fallback: {file_reference}")
                self._memory_store[state_id] = file_state
            
            return file_reference
        except Exception as e:
            self.logger.error(f"Failed to store file reference: {e}", exc_info=True)
            # Fallback to memory
            self._memory_store[state_id] = file_state
            return file_reference
    
    async def get_file(
        self,
        file_reference: str
    ) -> Optional[bytes]:
        """
        Retrieve file data from FileStorageAbstraction via State Surface reference.
        
        Architecture:
        - Gets storage_location from State Surface (metadata)
        - Retrieves actual file data from FileStorageAbstraction (GCS, etc.)
        - All file access goes through Runtime (governed, observable, replayable)
        
        Args:
            file_reference: File reference string (e.g., "file:tenant:session:file_id")
        
        Returns:
            File data as bytes or None if not found
        """
        if not self.file_storage:
            self.logger.error(
                f"FileStorageAbstraction not available. "
                f"Cannot retrieve file: {file_reference}"
            )
            raise RuntimeError("FileStorageAbstraction not available. Cannot retrieve file data.")
        
        # Get file metadata from State Surface (contains storage_location)
        file_metadata = await self.get_file_metadata(file_reference)
        if not file_metadata:
            self.logger.warning(f"File metadata not found: {file_reference}")
            return None
        
        # Get storage location from metadata
        storage_location = file_metadata.get("storage_location")
        if not storage_location:
            self.logger.error(f"File metadata missing storage_location: {file_reference}")
            return None
        
        # Retrieve actual file data from FileStorageAbstraction
        try:
            file_data = await self.file_storage.download_file(storage_location)
            if file_data:
                self.logger.debug(f"File retrieved from storage: {storage_location} ({len(file_data)} bytes)")
            return file_data
        except Exception as e:
            self.logger.error(f"Failed to retrieve file from storage {storage_location}: {e}", exc_info=True)
            return None
    
    async def get_file_metadata(
        self,
        file_reference: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from State Surface.
        
        Args:
            file_reference: File reference string (e.g., "file:tenant:session:file_id")
        
        Returns:
            File metadata dictionary or None if not found
        """
        if self.use_memory:
            return self._memory_store.get(file_reference)
        
        if not self.state_abstraction:
            return self._memory_store.get(file_reference)
        
        try:
            file_metadata = await self.state_abstraction.retrieve_state(file_reference)
            return file_metadata
        except Exception as e:
            self.logger.error(f"Failed to retrieve file metadata: {e}", exc_info=True)
            return None
