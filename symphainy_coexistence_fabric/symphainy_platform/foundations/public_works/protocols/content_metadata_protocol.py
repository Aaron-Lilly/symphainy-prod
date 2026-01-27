"""
Content Metadata Protocol - Abstraction Contract (Layer 2)

Defines the contract for content metadata operations.
Enables swappability between ArangoDB, MongoDB, etc.

WHAT (Infrastructure Role): I define the contract for content metadata operations
HOW (Infrastructure Implementation): I specify the interface for content metadata

NOTE: Only includes governance-related methods.
Domain logic methods (analyze, extract, generate) are flagged for future phases.
"""

from typing import Protocol, Dict, Any, List, Optional


class ContentMetadataProtocol(Protocol):
    """Protocol for content metadata operations (governance methods only)."""
    
    # ============================================================================
    # CORE CONTENT METADATA OPERATIONS (Governance)
    # ============================================================================
    
    async def create_content_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create content metadata document.
        
        Args:
            content_data: Content metadata and information (must include content_id, file_uuid, content_type)
            
        Returns:
            Dict containing created content metadata information
        """
        ...
    
    async def get_content_metadata(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Get content metadata by ID.
        
        Args:
            content_id: Unique identifier for the content metadata
            
        Returns:
            Dict containing content metadata information or None if not found
        """
        ...
    
    async def update_content_metadata(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update content metadata document.
        
        Args:
            content_id: Unique identifier for the content metadata
            updates: Dictionary of fields to update
            
        Returns:
            Dict containing updated content metadata information
        """
        ...
    
    async def delete_content_metadata(self, content_id: str) -> bool:
        """
        Delete content metadata document.
        
        Args:
            content_id: Unique identifier for the content metadata
            
        Returns:
            bool indicating success
        """
        ...
    
    async def search_content_metadata(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search content metadata by various criteria.
        
        Args:
            query: Dictionary of search criteria (filter conditions)
            
        Returns:
            List of matching content metadata records
        """
        ...
    
    async def get_content_relationships(self, content_id: str, direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get content relationships.
        
        Args:
            content_id: Unique identifier for the content
            direction: "both", "out", or "in"
            
        Returns:
            List of relationship records
        """
        ...
