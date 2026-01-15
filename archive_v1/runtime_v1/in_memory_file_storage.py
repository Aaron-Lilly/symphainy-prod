"""
In-Memory File Storage for Testing

Provides in-memory file storage implementation for tests.
No GCS/Supabase dependencies.

WHAT (Infrastructure Role): I provide file storage for testing
HOW (Infrastructure Implementation): I store files in memory
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger


class InMemoryFileStorage:
    """
    In-memory file storage for testing.
    
    Stores files in memory dictionary (no GCS/Supabase needed).
    Implements FileStorageProtocol for testing.
    """
    
    def __init__(self):
        """Initialize in-memory file storage."""
        self._files: Dict[str, bytes] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger(self.__class__.__name__)
    
    async def upload_file(
        self,
        file_path: str,
        file_data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Upload a file to in-memory storage.
        
        Args:
            file_path: File path (used as storage key)
            file_data: File data (binary)
            metadata: Optional metadata
        
        Returns:
            bool: True if successful
        """
        try:
            self._files[file_path] = file_data
            self._metadata[file_path] = metadata or {}
            self.logger.debug(f"File stored in memory: {file_path} ({len(file_data)} bytes)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store file {file_path}: {e}")
            return False
    
    async def download_file(
        self,
        file_path: str
    ) -> Optional[bytes]:
        """
        Download a file from in-memory storage.
        
        Args:
            file_path: File path (storage key)
        
        Returns:
            Optional[bytes]: File data or None if not found
        """
        return self._files.get(file_path)
    
    async def delete_file(
        self,
        file_path: str
    ) -> bool:
        """
        Delete a file from in-memory storage.
        
        Args:
            file_path: File path (storage key)
        
        Returns:
            bool: True if successful
        """
        if file_path in self._files:
            del self._files[file_path]
            if file_path in self._metadata:
                del self._metadata[file_path]
            return True
        return False
    
    async def list_files(
        self,
        prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in in-memory storage.
        
        Args:
            prefix: Optional prefix filter
        
        Returns:
            List of file metadata dictionaries
        """
        files = []
        for file_path, file_data in self._files.items():
            if prefix and not file_path.startswith(prefix):
                continue
            
            files.append({
                "file_path": file_path,
                "size": len(file_data),
                "metadata": self._metadata.get(file_path, {})
            })
        
        return files
    
    async def get_file_metadata(
        self,
        file_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from in-memory storage.
        
        Args:
            file_path: File path (storage key)
        
        Returns:
            Optional[Dict]: File metadata or None if not found
        """
        if file_path not in self._files:
            return None
        
        return {
            "file_path": file_path,
            "size": len(self._files[file_path]),
            "metadata": self._metadata.get(file_path, {})
        }
