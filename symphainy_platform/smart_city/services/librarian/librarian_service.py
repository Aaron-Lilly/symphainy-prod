"""
Librarian Service - Phase 4

WHAT: I govern knowledge and manage semantic search
HOW: I observe Runtime execution and manage knowledge
"""

from typing import Dict, Any, Optional
from symphainy_platform.smart_city.protocols.smart_city_service_protocol import SmartCityServiceProtocol
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService
from symphainy_platform.runtime.runtime_service import RuntimeService
from symphainy_platform.agentic.foundation_service import AgentFoundationService
from utilities import get_logger, get_clock, LogLevel, LogCategory


class LibrarianService(SmartCityServiceProtocol):
    """Librarian Service - Knowledge governance."""
    
    def __init__(
        self,
        public_works_foundation: PublicWorksFoundationService,
        curator_foundation: CuratorFoundationService,
        runtime_service: RuntimeService,
        agent_foundation: Optional[AgentFoundationService] = None
    ):
        self.public_works = public_works_foundation
        self.curator = curator_foundation
        self.runtime_service = runtime_service
        self.agent_foundation = agent_foundation
        self.logger = get_logger("librarian", LogLevel.INFO, LogCategory.PLATFORM)
        self.clock = get_clock()
        
        # Get semantic search abstraction from Public Works
        self.semantic_search = public_works_foundation.get_semantic_search_abstraction()
        if not self.semantic_search:
            self.logger.warning("Semantic search abstraction not available")
        
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        await self.curator.register_service(
            service_instance=self,
            service_metadata={
                "service_name": "LibrarianService",
                "service_type": "smart_city",
                "realm": "smart_city",
                "capabilities": ["knowledge_governance", "semantic_search", "metadata_management"]
            }
        )
        await self.runtime_service.register_observer("librarian", self)
        self.is_initialized = True
        return True
    
    async def observe_execution(self, execution_id: str, event: dict) -> None:
        """Observe Runtime execution events."""
        # Future: Index execution artifacts for semantic search
        pass
    
    async def enforce_policy(self, execution_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"allowed": True}
    
    async def semantic_search(
        self,
        query: str,
        index: str = "knowledge",
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Perform semantic search (public method).
        
        Args:
            query: Search query
            index: Index name
            filters: Optional filters
            limit: Result limit
        
        Returns:
            Dict containing search results
        """
        if not self.semantic_search:
            self.logger.error("Semantic search abstraction not available")
            return {"hits": [], "estimatedTotalHits": 0}
        
        try:
            results = await self.semantic_search.search(
                query=query,
                index=index,
                filters=filters,
                limit=limit
            )
            return results
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}", exc_info=True)
            return {"hits": [], "estimatedTotalHits": 0}
    
    async def govern_knowledge(
        self,
        knowledge_artifact: Dict[str, Any],
        index: str = "knowledge"
    ) -> bool:
        """
        Index knowledge artifact for semantic search.
        
        Args:
            knowledge_artifact: Knowledge artifact to index
            index: Index name
        
        Returns:
            bool: True if successful
        """
        if not self.semantic_search:
            self.logger.error("Semantic search abstraction not available")
            return False
        
        try:
            success = await self.semantic_search.index_document(
                index=index,
                document=knowledge_artifact
            )
            return success
        except Exception as e:
            self.logger.error(f"Failed to index knowledge artifact: {e}", exc_info=True)
            return False
    
    async def shutdown(self) -> None:
        self.is_initialized = False
