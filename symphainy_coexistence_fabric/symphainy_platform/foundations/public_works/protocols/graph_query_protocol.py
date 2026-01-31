"""
Graph Query Protocol - Abstraction Contract (Layer 2)

Narrow protocol for graph query operations (neighbors, paths, stats).
Decomposed from KnowledgeDiscoveryProtocol (mega). Swap unit: graph backend (e.g. Arango to Neo4j).

WHAT (Infrastructure Role): I define the contract for graph query operations
HOW (Infrastructure Implementation): I specify the interface for graph search, neighbors, path, stats

NOTE: This is PURE INFRASTRUCTURE - no business logic.
"""

from typing import Protocol, Dict, Any, List


class GraphQueryProtocol(Protocol):
    """Protocol for graph query - pure infrastructure. Swap unit: graph backend."""

    async def search_graph(
        self,
        graph: str,
        query: str,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Search graph for semantic similarity - pure infrastructure."""
        ...

    async def get_neighbors(
        self,
        graph: str,
        node_id: str,
        collection_name: str,
        max_depth: int = 2,
    ) -> List[Dict[str, Any]]:
        """Get neighbors from graph - pure infrastructure."""
        ...

    async def find_path(
        self,
        graph: str,
        start_id: str,
        start_collection: str,
        end_id: str,
        end_collection: str,
        max_paths: int = 5,
    ) -> List[List[str]]:
        """Find path in graph - pure infrastructure."""
        ...

    async def get_stats(self, graph: str) -> Dict[str, Any]:
        """Get graph statistics - pure infrastructure."""
        ...
