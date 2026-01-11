"""
Runtime State Surface - Centralized Execution State

Runtime-owned, not realm-owned.
Uses Public Works StateManagementAbstraction for swappable backends.
In-memory fallback for tests.
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger, get_clock

from symphainy_platform.foundations.public_works.protocols.state_protocol import StateManagementProtocol


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
        use_memory: bool = False
    ):
        """
        Initialize state surface.
        
        Args:
            state_abstraction: Optional state management abstraction (from Public Works)
            use_memory: If True, use in-memory storage (for tests)
        """
        self.use_memory = use_memory
        self.state_abstraction = state_abstraction
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
            if state_data:
                return state_data.get("state_data")
        except Exception as e:
            self.logger.error(f"Failed to get execution state: {e}", exc_info=True)
        
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
                state_id=state_id,
                state_data=state,
                metadata={"backend": "redis", "strategy": "hot", "type": "execution"},
                ttl=3600  # 1 hour TTL
            )
            return success
        except Exception as e:
            self.logger.error(f"Failed to set execution state: {e}", exc_info=True)
            # Fallback to memory
            self._memory_store[state_id] = state
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
            self.logger.warning("State abstraction not available, using in-memory fallback")
            return self._memory_store.get(state_id)
        
        try:
            state_data = await self.state_abstraction.retrieve_state(state_id)
            if state_data:
                return state_data.get("state_data")
        except Exception as e:
            self.logger.error(f"Failed to get session state: {e}", exc_info=True)
        
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
            self.logger.warning("State abstraction not available, using in-memory fallback")
            self._memory_store[state_id] = state
            return True
        
        try:
            success = await self.state_abstraction.store_state(
                state_id=state_id,
                state_data=state,
                metadata={"backend": "redis", "strategy": "hot", "type": "session"},
                ttl=86400  # 24 hour TTL
            )
            return success
        except Exception as e:
            self.logger.error(f"Failed to set session state: {e}", exc_info=True)
            # Fallback to memory
            self._memory_store[state_id] = state
            return False
    
    async def delete_state(
        self,
        key_prefix: str,
        tenant_id: str,
        resource_id: str
    ) -> bool:
        """
        Delete state.
        
        Args:
            key_prefix: Key prefix (e.g., "execution", "session")
            tenant_id: Tenant identifier
            resource_id: Resource identifier
        
        Returns:
            True if successful
        """
        state_id = f"{key_prefix}:{tenant_id}:{resource_id}"
        
        if self.use_memory:
            if state_id in self._memory_store:
                del self._memory_store[state_id]
                return True
            return False
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            if state_id in self._memory_store:
                del self._memory_store[state_id]
                return True
            return False
        
        try:
            success = await self.state_abstraction.delete_state(state_id)
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete state: {e}", exc_info=True)
            return False
    
    async def list_executions(
        self,
        tenant_id: str,
        limit: int = 100
    ) -> List[str]:
        """
        List execution IDs for tenant.
        
        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of executions to return
        
        Returns:
            List of execution IDs
        """
        if self.use_memory:
            return [
                key.split(":")[-1]
                for key in self._memory_store.keys()
                if key.startswith(f"execution:{tenant_id}:")
            ][:limit]
        
        if not self.state_abstraction:
            return []
        
        try:
            states = await self.state_abstraction.list_states(
                filters={"tenant_id": tenant_id, "type": "execution"},
                limit=limit
            )
            # Extract execution IDs from state IDs
            execution_ids = []
            for state in states:
                state_id = state.get("state_id", "")
                if state_id.startswith(f"execution:{tenant_id}:"):
                    execution_ids.append(state_id.split(":")[-1])
            return execution_ids[:limit]
        except Exception as e:
            self.logger.error(f"Failed to list executions: {e}", exc_info=True)
            return []
    
    async def store_file(
        self,
        session_id: str,
        tenant_id: str,
        file_data: bytes,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store file in State Surface and return reference.
        
        Files are stored in State Surface using StateManagementProtocol.
        For large files, consider using blob storage (S3, GCS) and storing references.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier (for isolation)
            file_data: File data as bytes
            filename: Original filename
            metadata: Optional file metadata (e.g., {"content_type": "application/pdf", "size": 12345})
        
        Returns:
            File reference string (e.g., "file:tenant_123:session_456:file_789")
        """
        import hashlib
        import uuid
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_ref = f"file:{tenant_id}:{session_id}:{file_id}"
        
        # Calculate file hash for deduplication (optional)
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # Prepare file state data
        file_state = {
            "file_data": file_data,  # Store file data in state
            "filename": filename,
            "file_hash": file_hash,
            "size": len(file_data),
            "metadata": metadata or {},
            "created_at": self.clock.now_iso()
        }
        
        # Store in State Surface
        state_id = file_ref
        success = await self.state_abstraction.store_state(
            state_id=state_id,
            state_data=file_state,
            metadata={
                "backend": "redis",
                "strategy": "hot",
                "type": "file",
                "tenant_id": tenant_id,
                "session_id": session_id
            },
            ttl=86400  # 24 hour TTL for files
        ) if self.state_abstraction else False
        
        if not success and not self.use_memory:
            # Fallback to memory if state abstraction fails
            self._memory_store[state_id] = file_state
            self.logger.warning(f"State abstraction failed, using in-memory storage for file: {file_ref}")
        elif self.use_memory:
            self._memory_store[state_id] = file_state
        
        self.logger.debug(f"File stored in State Surface: {file_ref} ({len(file_data)} bytes)")
        return file_ref
    
    async def get_file(
        self,
        file_reference: str
    ) -> Optional[bytes]:
        """
        Retrieve file data from State Surface.
        
        Args:
            file_reference: File reference string (e.g., "file:tenant:session:file_id")
        
        Returns:
            File data as bytes or None if not found
        """
        if self.use_memory:
            file_state = self._memory_store.get(file_reference)
            if file_state:
                return file_state.get("file_data")
            return None
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            file_state = self._memory_store.get(file_reference)
            if file_state:
                return file_state.get("file_data")
            return None
        
        try:
            state_data = await self.state_abstraction.retrieve_state(file_reference)
            if state_data:
                file_state = state_data.get("state_data", {})
                return file_state.get("file_data")
        except Exception as e:
            self.logger.error(f"Failed to get file {file_reference}: {e}", exc_info=True)
        
        return None
    
    async def get_file_metadata(
        self,
        file_reference: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from State Surface.
        
        Args:
            file_reference: File reference string
        
        Returns:
            File metadata dictionary or None if not found
            {
                "filename": str,
                "size": int,
                "file_hash": str,
                "metadata": Dict,
                "created_at": str
            }
        """
        if self.use_memory:
            file_state = self._memory_store.get(file_reference)
            if file_state:
                return {
                    "filename": file_state.get("filename"),
                    "size": file_state.get("size"),
                    "file_hash": file_state.get("file_hash"),
                    "metadata": file_state.get("metadata", {}),
                    "created_at": file_state.get("created_at")
                }
            return None
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            file_state = self._memory_store.get(file_reference)
            if file_state:
                return {
                    "filename": file_state.get("filename"),
                    "size": file_state.get("size"),
                    "file_hash": file_state.get("file_hash"),
                    "metadata": file_state.get("metadata", {}),
                    "created_at": file_state.get("created_at")
                }
            return None
        
        try:
            state_data = await self.state_abstraction.retrieve_state(file_reference)
            if state_data:
                file_state = state_data.get("state_data", {})
                return {
                    "filename": file_state.get("filename"),
                    "size": file_state.get("size"),
                    "file_hash": file_state.get("file_hash"),
                    "metadata": file_state.get("metadata", {}),
                    "created_at": file_state.get("created_at")
                }
        except Exception as e:
            self.logger.error(f"Failed to get file metadata {file_reference}: {e}", exc_info=True)
        
        return None
    
    async def delete_file(
        self,
        file_reference: str
    ) -> bool:
        """
        Delete file from State Surface.
        
        Args:
            file_reference: File reference string
        
        Returns:
            True if successful
        """
        if self.use_memory:
            if file_reference in self._memory_store:
                del self._memory_store[file_reference]
                return True
            return False
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            if file_reference in self._memory_store:
                del self._memory_store[file_reference]
                return True
            return False
        
        try:
            success = await self.state_abstraction.delete_state(file_reference)
            if success:
                self.logger.debug(f"File deleted from State Surface: {file_reference}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_reference}: {e}", exc_info=True)
            return False