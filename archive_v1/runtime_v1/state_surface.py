"""
Runtime State Surface - Centralized Execution State

Runtime-owned, not realm-owned.
Uses Public Works StateManagementAbstraction for swappable backends.
In-memory fallback for tests.
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger, get_clock
import uuid
import hashlib

from symphainy_platform.foundations.public_works.protocols.state_protocol import StateManagementProtocol
from symphainy_platform.foundations.public_works.protocols.file_storage_protocol import FileStorageProtocol


class StateSurface:
    """
    Centralized recording of execution state.
    
    Runtime-owned state surface that coordinates all state operations.
    Uses Public Works StateManagementAbstraction for swappable backends.
    In-memory fallback for tests.
    
    **Architectural Principles:**
    - Stores execution state, facts, references, and lineage
    - Does NOT store file data, blobs, or large payloads
    - File data is stored in FileStorageAbstraction (GCS/ArangoDB)
    - State Surface stores only metadata and storage_location references
    
    **File Storage Pattern:**
    - store_file(): Accepts file_data, stores in FileStorageAbstraction,
                    stores only metadata/reference in State Surface
    - store_file_reference(): Stores only metadata/reference (file already in FileStorageAbstraction)
    - get_file(): Gets storage_location from State Surface,
                  retrieves file_data from FileStorageAbstraction
    """
    
    def __init__(
        self,
        state_abstraction: Optional[StateManagementProtocol] = None,
        file_storage: Optional[FileStorageProtocol] = None,
        use_memory: bool = False
    ):
        """
        Initialize state surface.
        
        Architecture:
        - State Surface stores file METADATA/REFERENCES only
        - FileStorageAbstraction stores actual FILE DATA (GCS/ArangoDB/Redis)
        
        Args:
            state_abstraction: Optional state management abstraction (from Public Works)
            file_storage: Optional file storage abstraction (for actual file data storage)
            use_memory: If True, use in-memory storage (for tests)
        """
        self.use_memory = use_memory
        self.state_abstraction = state_abstraction
        self.file_storage = file_storage
        
        # For tests: create in-memory file storage if not provided
        if not file_storage and use_memory:
            from .in_memory_file_storage import InMemoryFileStorage
            self.file_storage = InMemoryFileStorage()
            self.logger = get_logger(self.__class__.__name__)
            self.logger.info("Using in-memory file storage for tests")
        
        self._memory_store: Dict[str, Any] = {}
        if not hasattr(self, 'logger'):
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
        Store file and return reference.
        
        Architecture:
        - File DATA is stored in FileStorageAbstraction (GCS/ArangoDB/Redis)
        - File METADATA/REFERENCE is stored in State Surface
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier (for isolation)
            file_data: File data as bytes
            filename: Original filename
            metadata: Optional file metadata (e.g., {"content_type": "application/pdf", "size": 12345})
        
        Returns:
            File reference string (e.g., "file:tenant_123:session_456:file_789")
        """
        if not self.file_storage:
            raise RuntimeError(
                "FileStorageAbstraction not available. "
                "Files must be stored via FileStorageAbstraction (GCS/ArangoDB), not in State Surface."
            )
        
        # Generate unique file ID and storage path
        file_id = str(uuid.uuid4())
        file_ref = f"file:{tenant_id}:{session_id}:{file_id}"
        
        # Storage path in GCS/ArangoDB (tenant/session/file_id format)
        storage_path = f"{tenant_id}/{session_id}/{file_id}/{filename}"
        
        # Calculate file hash for deduplication
        file_hash = hashlib.sha256(file_data).hexdigest()
        
        # Store actual file data in FileStorageAbstraction (GCS/ArangoDB)
        storage_metadata = {
            "tenant_id": tenant_id,
            "session_id": session_id,
            "file_id": file_id,
            "content_type": metadata.get("content_type") if metadata else None
        }
        if metadata:
            storage_metadata.update(metadata)
        
        upload_success = await self.file_storage.upload_file(
            file_path=storage_path,
            file_data=file_data,
            metadata=storage_metadata
        )
        
        if not upload_success:
            raise RuntimeError(f"Failed to store file in FileStorageAbstraction: {storage_path}")
        
        # Store only metadata/reference in State Surface (NOT file data)
        file_state = {
            "storage_location": storage_path,  # Where the file is stored (GCS path, ArangoDB doc ID, etc.)
            "filename": filename,
            "file_hash": file_hash,
            "size": len(file_data),
            "metadata": metadata or {},
            "created_at": self.clock.now_iso()
        }
        
        # Store metadata in State Surface
        state_id = file_ref
        success = await self.state_abstraction.store_state(
            state_id=state_id,
            state_data=file_state,
            metadata={
                "backend": "redis",
                "strategy": "hot",
                "type": "file_metadata",
                "tenant_id": tenant_id,
                "session_id": session_id
            },
            ttl=86400  # 24 hour TTL for file metadata
        ) if self.state_abstraction else False
        
        if not success and not self.use_memory:
            # Fallback to memory if state abstraction fails
            self._memory_store[state_id] = file_state
            self.logger.warning(f"State abstraction failed, using in-memory storage for file metadata: {file_ref}")
        elif self.use_memory:
            self._memory_store[state_id] = file_state
        
        self.logger.debug(f"File stored: {file_ref} -> {storage_path} ({len(file_data)} bytes)")
        return file_ref
    
    async def get_file(
        self,
        file_reference: str
    ) -> Optional[bytes]:
        """
        Retrieve file data from FileStorageAbstraction.
        
        Architecture:
        - Gets storage location from State Surface (metadata)
        - Retrieves actual file data from FileStorageAbstraction (GCS/ArangoDB)
        
        Args:
            file_reference: File reference string (e.g., "file:tenant:session:file_id")
        
        Returns:
            File data as bytes or None if not found
        """
        if not self.file_storage:
            self.logger.error(
                f"FileStorageAbstraction not available. "
                f"StateSurface.use_memory={self.use_memory}, "
                f"file_storage={self.file_storage}"
            )
            raise RuntimeError("FileStorageAbstraction not available. Cannot retrieve file data.")
        
        # Get file metadata from State Surface (contains storage_location)
        file_metadata = await self.get_file_metadata(file_reference)
        if not file_metadata:
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
            file_reference: File reference string
        
        Returns:
            File metadata dictionary or None if not found
            {
                "storage_location": str,  # Where file is stored (GCS path, ArangoDB doc ID, etc.)
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
                    "storage_location": file_state.get("storage_location"),
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
                    "storage_location": file_state.get("storage_location"),
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
                    "storage_location": file_state.get("storage_location"),
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
        Delete file from FileStorageAbstraction and State Surface.
        
        Architecture:
        - Deletes file data from FileStorageAbstraction (GCS/ArangoDB)
        - Deletes file metadata from State Surface
        
        Args:
            file_reference: File reference string
        
        Returns:
            True if successful
        """
        if not self.file_storage:
            raise RuntimeError("FileStorageAbstraction not available. Cannot delete file.")
        
        # Get storage location from metadata
        file_metadata = await self.get_file_metadata(file_reference)
        if file_metadata:
            storage_location = file_metadata.get("storage_location")
            if storage_location:
                # Delete from FileStorageAbstraction
                try:
                    await self.file_storage.delete_file(storage_location)
                except Exception as e:
                    self.logger.warning(f"Failed to delete file from storage {storage_location}: {e}")
        
        # Delete metadata from State Surface
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
                self.logger.debug(f"File metadata deleted from State Surface: {file_reference}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete file metadata {file_reference}: {e}", exc_info=True)
            return False
    
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
        
        Use this when the file has already been stored via FileStorageAbstraction
        and you just need to register the reference in State Surface.
        
        This method is used by ingestion services where adapters have already
        stored files via FileStorageAbstraction.upload_file().
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier (for isolation)
            file_reference: File reference string (e.g., "file:tenant:session:id")
            storage_location: Where file is stored (GCS path, ArangoDB doc ID, etc.)
            filename: Original filename
            metadata: Optional file metadata (e.g., {"content_type": "application/pdf", "size": 12345})
        
        Returns:
            File reference string (same as input)
        """
        # Store only metadata/reference in State Surface (NOT file data)
        file_state = {
            "storage_location": storage_location,
            "filename": filename,
            "size": metadata.get("size") if metadata else None,
            "file_hash": metadata.get("file_hash") if metadata else None,
            "metadata": metadata or {},
            "created_at": self.clock.now_iso()
        }
        
        # Store metadata in State Surface
        state_id = file_reference
        success = await self.state_abstraction.store_state(
            state_id=state_id,
            state_data=file_state,
            metadata={
                "backend": "redis",
                "strategy": "hot",
                "type": "file_metadata",
                "tenant_id": tenant_id,
                "session_id": session_id
            },
            ttl=86400  # 24 hour TTL for file metadata
        ) if self.state_abstraction else False
        
        if not success and not self.use_memory:
            # Fallback to memory if state abstraction fails
            self._memory_store[state_id] = file_state
            self.logger.warning(f"State abstraction failed, using in-memory storage for file metadata: {file_reference}")
        elif self.use_memory:
            self._memory_store[state_id] = file_state
        
        self.logger.debug(f"File reference stored: {file_reference} -> {storage_location}")
        return file_reference
    
    # ============================================================================
    # FILE LINEAGE TRACKING
    # ============================================================================
    
    async def store_file_lineage(
        self,
        file_id: str,
        file_type: str,
        ui_name: str,
        tenant_id: str,
        parent_file_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store file lineage fact in State Surface.
        
        Architecture:
        - Stores lineage facts (references, not data)
        - Links files: uploaded → parsed → embedded
        - Enables fast lineage lookups during execution
        
        Args:
            file_id: File UUID
            file_type: File type ("uploaded" | "parsed" | "embedded")
            ui_name: User-friendly display name
            tenant_id: Tenant identifier
            parent_file_id: Parent file UUID (None for original files)
            metadata: Optional additional metadata
        
        Returns:
            True if successful
        """
        lineage_id = f"lineage:{tenant_id}:{file_id}"
        
        lineage_fact = {
            "file_id": file_id,
            "file_type": file_type,
            "ui_name": ui_name,
            "parent_file_id": parent_file_id,
            "child_file_ids": [],
            "relationships": {},
            "metadata": metadata or {},
            "created_at": self.clock.now_iso(),
            "updated_at": self.clock.now_iso()
        }
        
        if self.use_memory:
            self._memory_store[lineage_id] = lineage_fact
            return True
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            self._memory_store[lineage_id] = lineage_fact
            return True
        
        try:
            success = await self.state_abstraction.store_state(
                state_id=lineage_id,
                state_data=lineage_fact,
                metadata={
                    "backend": "redis",
                    "strategy": "hot",
                    "type": "file_lineage",
                    "tenant_id": tenant_id,
                    "file_id": file_id
                },
                ttl=86400  # 24 hour TTL for lineage facts
            )
            return success
        except Exception as e:
            self.logger.error(f"Failed to store file lineage: {e}", exc_info=True)
            # Fallback to memory
            self._memory_store[lineage_id] = lineage_fact
            return False
    
    async def link_file_versions(
        self,
        parent_file_id: str,
        child_file_id: str,
        relationship_type: str,
        tenant_id: str
    ) -> bool:
        """
        Link file versions (parent → child) in State Surface.
        
        Updates lineage facts to establish parent-child relationships.
        
        Args:
            parent_file_id: Parent file UUID
            child_file_id: Child file UUID
            relationship_type: Relationship type ("parsed_from" | "embedded_from")
            tenant_id: Tenant identifier
        
        Returns:
            True if successful
        """
        # Update parent's lineage fact (add child)
        parent_lineage_id = f"lineage:{tenant_id}:{parent_file_id}"
        parent_lineage = await self._get_lineage_fact(parent_lineage_id)
        
        if parent_lineage:
            if child_file_id not in parent_lineage.get("child_file_ids", []):
                parent_lineage.setdefault("child_file_ids", []).append(child_file_id)
                parent_lineage.setdefault("relationships", {})[child_file_id] = relationship_type
                parent_lineage["updated_at"] = self.clock.now_iso()
                
                # Store updated lineage
                if self.use_memory:
                    self._memory_store[parent_lineage_id] = parent_lineage
                elif self.state_abstraction:
                    await self.state_abstraction.store_state(
                        state_id=parent_lineage_id,
                        state_data=parent_lineage,
                        metadata={
                            "backend": "redis",
                            "strategy": "hot",
                            "type": "file_lineage",
                            "tenant_id": tenant_id,
                            "file_id": parent_file_id
                        },
                        ttl=86400
                    )
        
        # Update child's lineage fact (set parent)
        child_lineage_id = f"lineage:{tenant_id}:{child_file_id}"
        child_lineage = await self._get_lineage_fact(child_lineage_id)
        
        if child_lineage:
            child_lineage["parent_file_id"] = parent_file_id
            child_lineage["updated_at"] = self.clock.now_iso()
            
            # Store updated lineage
            if self.use_memory:
                self._memory_store[child_lineage_id] = child_lineage
            elif self.state_abstraction:
                await self.state_abstraction.store_state(
                    state_id=child_lineage_id,
                    state_data=child_lineage,
                    metadata={
                        "backend": "redis",
                        "strategy": "hot",
                        "type": "file_lineage",
                        "tenant_id": tenant_id,
                        "file_id": child_file_id
                    },
                    ttl=86400
                )
        
        self.logger.debug(f"Linked file versions: {parent_file_id} → {child_file_id} ({relationship_type})")
        return True
    
    async def get_file_lineage_from_state(
        self,
        file_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get file lineage chain from State Surface (fast lookup).
        
        Returns lineage chain: original → parsed → embedded
        
        Args:
            file_id: File UUID
            tenant_id: Tenant identifier
        
        Returns:
            Dict with lineage chain or None if not found
        """
        lineage_id = f"lineage:{tenant_id}:{file_id}"
        lineage_fact = await self._get_lineage_fact(lineage_id)
        
        if not lineage_fact:
            return None
        
        # Build lineage chain
        lineage_chain = {
            "file_id": file_id,
            "ui_name": lineage_fact.get("ui_name"),
            "file_type": lineage_fact.get("file_type"),
            "parent_file_id": lineage_fact.get("parent_file_id"),
            "child_file_ids": lineage_fact.get("child_file_ids", []),
            "relationships": lineage_fact.get("relationships", {})
        }
        
        return lineage_chain
    
    async def _get_lineage_fact(self, lineage_id: str) -> Optional[Dict[str, Any]]:
        """Internal helper to get lineage fact from State Surface or memory."""
        if self.use_memory:
            return self._memory_store.get(lineage_id)
        
        if not self.state_abstraction:
            return self._memory_store.get(lineage_id)
        
        try:
            state_data = await self.state_abstraction.retrieve_state(lineage_id)
            if state_data:
                return state_data.get("state_data")
        except Exception as e:
            self.logger.error(f"Failed to get lineage fact {lineage_id}: {e}", exc_info=True)
        
        return None