"""
Correlation Map Protocol - Abstraction Contract (Layer 2)

Narrow protocol for correlation map storage and retrieval.
Decomposed from SemanticDataProtocol (mega). Swap unit: correlation store.

WHAT (Infrastructure Role): I define the contract for correlation map operations
HOW (Infrastructure Implementation): I specify the interface for correlation map storage and retrieval

NOTE: This is PURE INFRASTRUCTURE - no business logic.
"""

from typing import Protocol, Dict, Any, Optional


class CorrelationMapProtocol(Protocol):
    """Protocol for correlation map storage and retrieval - pure infrastructure."""

    async def store_correlation_map(
        self,
        correlation_document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store correlation map document - pure infrastructure."""
        ...

    async def get_correlation_map(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get correlation map - pure infrastructure."""
        ...
