"""
Full-Text Search Protocol - Abstraction Contract (Layer 2)

Narrow protocol for full-text search index operations.
Decomposed from KnowledgeDiscoveryProtocol (mega). Swap unit: search engine (e.g. Meilisearch to OpenSearch).

WHAT (Infrastructure Role): I define the contract for full-text search operations
HOW (Infrastructure Implementation): I specify the interface for search, facets, analytics, event tracking

NOTE: This is PURE INFRASTRUCTURE - no business logic.
"""

from typing import Protocol, Dict, Any, List, Optional


class FullTextSearchProtocol(Protocol):
    """Protocol for full-text search index - pure infrastructure. Swap unit: search engine."""

    async def search(
        self,
        index: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Search index - pure infrastructure."""
        ...

    async def search_with_facets(
        self,
        index: str,
        query: str,
        facets: List[str],
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Search with facets - pure infrastructure."""
        ...

    async def get_analytics(
        self,
        index: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get search analytics - pure infrastructure."""
        ...

    async def track_event(
        self,
        index: str,
        query: str,
        results_count: int,
        user_id: Optional[str] = None,
    ) -> bool:
        """Track search event - pure infrastructure."""
        ...
