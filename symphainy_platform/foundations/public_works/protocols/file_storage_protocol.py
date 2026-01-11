"""
File Storage Protocol - Abstraction Contract (Layer 2)

Defines the interface for file storage operations.
Enables swappability between GCS, S3, Azure Blob, etc.

WHAT (Infrastructure Role): I define the contract for file storage operations
HOW (Infrastructure Implementation): I specify the interface for file storage
"""

from typing import Protocol, Optional, BinaryIO, Dict, Any, List


class FileStorageProtocol(Protocol):
    """Protocol for file storage operations."""
    
    async def upload_file(
        self,
        file_path: str,
        file_data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Upload a file.
        
        Args:
            file_path: File path in storage
            file_data: File data (binary)
            metadata: Optional metadata
        
        Returns:
            bool: True if successful
        """
        ...
    
    async def download_file(
        self,
        file_path: str
    ) -> Optional[bytes]:
        """
        Download a file.
        
        Args:
            file_path: File path in storage
        
        Returns:
            Optional[bytes]: File data or None if not found
        """
        ...
    
    async def delete_file(
        self,
        file_path: str
    ) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: File path in storage
        
        Returns:
            bool: True if successful
        """
        ...
    
    async def list_files(
        self,
        prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List files.
        
        Args:
            prefix: Optional prefix filter
        
        Returns:
            List of file metadata dictionaries
        """
        ...
    
    async def get_file_metadata(
        self,
        file_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get file metadata.
        
        Args:
            file_path: File path in storage
        
        Returns:
            Optional[Dict]: File metadata or None if not found
        """
        ...
