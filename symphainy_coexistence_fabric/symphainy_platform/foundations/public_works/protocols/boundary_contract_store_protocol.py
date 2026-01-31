"""
Boundary Contract Store Protocol - Abstraction Contract (Layer 2)

Defines the contract for data_boundary_contracts and TTL-related operations.
Enables swappability and keeps adapter use inside Public Works.

WHAT (Infrastructure Role): I define the contract for boundary contract and records_of_fact operations.
HOW (Infrastructure Implementation): Implementations use SupabaseAdapter inside Public Works only.
"""

from typing import Protocol, Optional, List, Dict, Any


class BoundaryContractStoreProtocol(Protocol):
    """
    Protocol for boundary contract store operations.

    Consumers (DataStewardPrimitives, DataStewardSDK, TTLEnforcementJob) depend on this protocol;
    Public Works provides the implementation (over SupabaseAdapter).
    """

    async def create_boundary_contract(self, contract_data: Dict[str, Any]) -> Optional[str]:
        """Create a boundary contract. Returns contract_id or None."""
        ...

    async def get_boundary_contract(
        self,
        tenant_id: str,
        external_source_type: str,
        external_source_identifier: str
    ) -> Optional[Dict[str, Any]]:
        """Get boundary contract by external source. Returns contract dict or None."""
        ...

    async def get_boundary_contract_by_id(
        self, contract_id: str, tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get boundary contract by id and tenant. Returns contract dict or None."""
        ...

    async def update_boundary_contract(
        self,
        contract_id: str,
        tenant_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update boundary contract. Returns True if successful."""
        ...

    async def list_expired_contracts(self, expired_before_iso: str) -> List[Dict[str, Any]]:
        """List active boundary contracts with materialization_expires_at < expired_before_iso."""
        ...

    async def update_contract_status_expired(
        self, contract_id: str, tenant_id: str, expired_at_iso: str
    ) -> bool:
        """Set contract status to expired and set expired_at. Returns True if successful."""
        ...

    async def update_records_of_fact_expired(
        self, source_file_id: str, tenant_id: str, expired_at: str
    ) -> int:
        """Set source_expired_at on records_of_fact for given source_file_id/tenant_id. Returns count updated."""
        ...
