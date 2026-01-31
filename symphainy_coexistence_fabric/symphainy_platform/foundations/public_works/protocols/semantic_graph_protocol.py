"""
Semantic Graph Protocol - Abstraction Contract (Layer 2)

Narrow protocol for semantic graph (nodes/edges) storage and retrieval.
Decomposed from SemanticDataProtocol (mega). Swap unit: graph backend.

WHAT (Infrastructure Role): I define the contract for semantic graph operations
HOW (Infrastructure Implementation): I specify the interface for graph storage and retrieval

NOTE: This is PURE INFRASTRUCTURE - no business logic.
"""

from typing import Protocol, Dict, Any, List, Optional


class SemanticGraphProtocol(Protocol):
    """Protocol for semantic graph (nodes/edges) storage and retrieval - pure infrastructure."""

    async def store_semantic_graph(
        self,
        node_documents: List[Dict[str, Any]],
        edge_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Store semantic graph documents - pure infrastructure."""
        ...

    async def get_semantic_graph(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get semantic graph - pure infrastructure."""
        ...
