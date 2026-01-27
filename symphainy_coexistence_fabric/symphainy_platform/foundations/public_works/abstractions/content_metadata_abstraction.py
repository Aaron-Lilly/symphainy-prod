"""
Content Metadata Abstraction - Pure Infrastructure (Layer 1)

Implements content metadata operations using ArangoDB adapter.
Returns raw data only - no business logic.

WHAT (Infrastructure Role): I provide content metadata storage services
HOW (Infrastructure Implementation): I use ArangoDB adapter for content metadata

NOTE: This is PURE INFRASTRUCTURE - no business logic.
Business logic (content ID generation, validation, metadata enhancement) belongs in Platform SDK.
Domain logic (analyze, extract, generate) belongs in Realm services (flagged for future phases).
"""

from typing import Dict, Any, Optional, List

from typing import Any  # For adapter type hint
from utilities import get_logger
from ..protocols.content_metadata_protocol import ContentMetadataProtocol


class ContentMetadataAbstraction(ContentMetadataProtocol):
    """
    Content metadata abstraction - pure infrastructure.
    
    Returns raw data only (Dict[str, Any]), not business objects.
    Business logic (content ID generation, validation, metadata enhancement) belongs in Platform SDK.
    Domain logic (analyze, extract, generate) belongs in Realm services.
    """
    
    def __init__(self, arango_adapter: Any):
        """
        Initialize Content Metadata abstraction.
        
        Args:
            arango_adapter: ArangoDB adapter for content metadata (Layer 0)
        """
        self.arango = arango_adapter
        self.logger = get_logger(self.__class__.__name__)
        
        # Collection names for ArangoDB
        self.content_metadata_collection = "content_metadata"
        self.content_relationships_collection = "content_relationships"
        
        self.logger.info("Content Metadata Abstraction initialized (pure infrastructure)")
    
    async def create_content_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create content metadata - pure infrastructure only.
        
        Stores content metadata in ArangoDB.
        Returns raw data from adapter.
        
        Args:
            content_data: Content metadata dict (must include content_id as _key, file_uuid, content_type)
        
        Returns:
            Raw content metadata dict from ArangoDB adapter
        """
        try:
            # Extract content_id for document key
            content_id = content_data.get("content_id")
            if not content_id:
                # Platform SDK should provide content_id, but if not, use a fallback
                # This is infrastructure fallback, not business logic
                content_id = content_data.get("_key") or content_data.get("file_uuid")
            
            # Create document with _key
            document = {**content_data, "_key": content_id}
            
            # Store in ArangoDB (pure infrastructure)
            result = await self.arango.create_document(
                self.content_metadata_collection,
                document
            )
            
            self.logger.info(f"Content metadata created: {content_id}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create content metadata: {e}", exc_info=True)
            raise
    
    async def get_content_metadata(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Get content metadata - pure infrastructure only.
        
        Retrieves content metadata from ArangoDB.
        Returns raw data from adapter.
        
        Args:
            content_id: Content ID
        
        Returns:
            Raw content metadata dict from ArangoDB or None if not found
        """
        try:
            result = await self.arango.get_document(
                self.content_metadata_collection,
                content_id
            )
            
            if result:
                self.logger.debug(f"Content metadata retrieved: {content_id}")
            else:
                self.logger.warning(f"Content metadata not found: {content_id}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get content metadata {content_id}: {e}", exc_info=True)
            raise
    
    async def update_content_metadata(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update content metadata - pure infrastructure only.
        
        Updates content metadata in ArangoDB.
        Returns raw data from adapter.
        
        Args:
            content_id: Content ID
            updates: Dictionary of fields to update
        
        Returns:
            Raw updated content metadata dict from ArangoDB
        """
        try:
            # Update in ArangoDB (pure infrastructure)
            result = await self.arango.update_document(
                self.content_metadata_collection,
                content_id,
                updates
            )
            
            self.logger.info(f"Content metadata updated: {content_id}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update content metadata {content_id}: {e}", exc_info=True)
            raise
    
    async def delete_content_metadata(self, content_id: str) -> bool:
        """
        Delete content metadata - pure infrastructure only.
        
        Deletes content metadata from ArangoDB.
        Returns raw success status.
        
        NOTE: Relationship checking is business logic and should be done in Platform SDK
        before calling this method.
        
        Args:
            content_id: Content ID
        
        Returns:
            bool: True if successful
        """
        try:
            # Delete from ArangoDB (pure infrastructure)
            result = await self.arango.delete_document(
                self.content_metadata_collection,
                content_id
            )
            
            if result:
                self.logger.info(f"Content metadata deleted: {content_id}")
            else:
                self.logger.error(f"Failed to delete content metadata: {content_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to delete content metadata {content_id}: {e}", exc_info=True)
            raise
    
    async def search_content_metadata(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search content metadata - pure infrastructure only.
        
        Searches content metadata in ArangoDB.
        Returns raw data from adapter.
        
        Args:
            query: Search query dict (filter conditions)
        
        Returns:
            List of raw content metadata dicts from ArangoDB
        """
        try:
            # Search in ArangoDB (pure infrastructure)
            result = await self.arango.find_documents(
                self.content_metadata_collection,
                filter_conditions=query
            )
            
            self.logger.debug(f"Content metadata search returned {len(result)} results")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to search content metadata: {e}", exc_info=True)
            raise
    
    async def get_content_relationships(self, content_id: str, direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get content relationships - pure infrastructure only.
        
        Retrieves content relationships from ArangoDB.
        Returns raw data from adapter.
        
        Args:
            content_id: Content ID
            direction: "both", "out", or "in"
        
        Returns:
            List of raw relationship dicts from ArangoDB
        """
        try:
            # Build AQL query based on direction
            if direction == "both":
                aql_query = """
                    FOR edge IN @@collection
                        FILTER edge._from == @content_id OR edge._to == @content_id
                        RETURN edge
                """
            elif direction == "out":
                aql_query = """
                    FOR edge IN @@collection
                        FILTER edge._from == @content_id
                        RETURN edge
                """
            else:  # direction == "in"
                aql_query = """
                    FOR edge IN @@collection
                        FILTER edge._to == @content_id
                        RETURN edge
                """
            
            # Execute AQL query (pure infrastructure)
            result = await self.arango.execute_aql(
                aql_query,
                bind_vars={
                    "@collection": self.content_relationships_collection,
                    "content_id": f"{self.content_metadata_collection}/{content_id}"
                }
            )
            
            self.logger.debug(f"Content relationships retrieved: {len(result)} relationships")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get content relationships {content_id}: {e}", exc_info=True)
            raise
    
    # ============================================================================
    # DOMAIN LOGIC METHODS (Flagged for Future Phases)
    # ============================================================================
    # NOTE: These methods contain domain logic (Content/Insights Pillar) and should
    # be moved to Realm services in future phases. They are kept here for backward
    # compatibility but should not be used by Smart City roles.
    # ============================================================================
    
    # ⏸️ FLAGGED FOR FUTURE PHASES:
    # - analyze_content_structure() - Domain logic (Content Pillar)
    # - extract_content_schema() - Domain logic (Content Pillar)
    # - generate_content_insights() - Domain logic (Content Pillar)
    # - get_semantic_embeddings() - Domain logic (Insights Pillar)
    # - get_semantic_graph() - Domain logic (Insights Pillar)
