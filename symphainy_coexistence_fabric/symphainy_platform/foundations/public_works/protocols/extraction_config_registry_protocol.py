"""
Extraction Config Registry Protocol - Abstraction Contract (Layer 2)

Defines the contract for extraction config CRUD (extraction_configs table).
Enables swappability and keeps adapter use inside Public Works.

WHAT (Infrastructure Role): I define the contract for extraction config storage.
HOW (Infrastructure Implementation): Implementations use SupabaseAdapter inside Public Works only.
"""

from typing import Protocol, Optional, List, Any


class ExtractionConfigRegistryProtocol(Protocol):
    """
    Protocol for extraction config registry operations.

    Consumers (e.g. StructuredExtractionService) depend on this protocol;
    Public Works provides the implementation (over SupabaseAdapter).
    """

    async def register_config(self, config: Any, tenant_id: str) -> bool:
        """Register an extraction config. Returns True if successful."""
        ...

    async def get_config(self, config_id: str, tenant_id: str) -> Optional[Any]:
        """Get extraction config by id and tenant. Returns config or None."""
        ...

    async def list_configs(
        self, tenant_id: str, domain: Optional[str] = None
    ) -> List[Any]:
        """List extraction configs, optionally filtered by domain."""
        ...

    async def update_config(self, config: Any, tenant_id: str) -> bool:
        """Update an extraction config. Returns True if successful."""
        ...

    async def delete_config(self, config_id: str, tenant_id: str) -> bool:
        """Delete an extraction config. Returns True if successful."""
        ...
