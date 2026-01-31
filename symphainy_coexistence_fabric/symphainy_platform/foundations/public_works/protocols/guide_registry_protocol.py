"""
Guide Registry Protocol - Abstraction Contract (Layer 2)

Defines the contract for guide CRUD (guides table).
Enables swappability and keeps adapter use inside Public Works.

WHAT (Infrastructure Role): I define the contract for guide storage.
HOW (Infrastructure Implementation): Implementations use SupabaseAdapter inside Public Works only.
"""

from typing import Protocol, Optional, List, Dict, Any


class GuideRegistryProtocol(Protocol):
    """
    Protocol for guide registry operations.

    Consumers (e.g. GuidedDiscoveryService) depend on this protocol;
    Public Works provides the implementation (over SupabaseAdapter).
    """

    async def register_guide(
        self, guide_id: str, guide: Dict[str, Any], tenant_id: str
    ) -> bool:
        """Register a guide. Returns True if successful."""
        ...

    async def get_guide(self, guide_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get guide by id and tenant. Returns guide dict or None."""
        ...

    async def list_guides(
        self, tenant_id: str, guide_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List guides, optionally filtered by type."""
        ...

    async def update_guide(
        self, guide_id: str, updates: Dict[str, Any], tenant_id: str
    ) -> bool:
        """Update a guide. Returns True if successful."""
        ...

    async def delete_guide(self, guide_id: str, tenant_id: str) -> bool:
        """Delete a guide. Returns True if successful."""
        ...
