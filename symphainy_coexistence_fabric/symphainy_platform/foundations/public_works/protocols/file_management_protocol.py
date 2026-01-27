"""
File Management Protocol - Abstraction Contract (Layer 2)

Defines the contract for file management operations.
Enables swappability between GCS, S3, Azure Blob, etc.

WHAT (Infrastructure Role): I define the contract for file management operations
HOW (Infrastructure Implementation): I specify the interface for file management
"""

from typing import Protocol, Dict, Any, List, Optional


class FileManagementProtocol(Protocol):
    """Protocol for file management operations."""
    
    # ============================================================================
    # CORE FILE OPERATIONS
    # ============================================================================
    
    async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new file record.
        
        Args:
            file_data: File metadata and information (must include file_content, user_id, ui_name, file_type)
            
        Returns:
            Dict containing created file information (includes uuid, ui_name, file_type, etc.)
        """
        ...
    
    async def get_file(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get file record by UUID.
        
        Args:
            file_uuid: Unique identifier for the file
            
        Returns:
            Dict containing file information (includes file_content if available) or None if not found
        """
        ...
    
    async def update_file(self, file_uuid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update file record.
        
        Args:
            file_uuid: Unique identifier for the file
            updates: Dictionary of fields to update
            
        Returns:
            Dict containing updated file information
        """
        ...
    
    async def delete_file(self, file_uuid: str) -> bool:
        """
        Delete file record.
        
        Args:
            file_uuid: Unique identifier for the file
            
        Returns:
            bool indicating success
        """
        ...
    
    async def list_files(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List files with optional filtering.
        
        Args:
            user_id: User identifier
            tenant_id: Optional tenant identifier
            filters: Optional filters to apply
            limit: Optional limit on number of results
            offset: Optional offset for pagination
            
        Returns:
            List of file records
        """
        ...
