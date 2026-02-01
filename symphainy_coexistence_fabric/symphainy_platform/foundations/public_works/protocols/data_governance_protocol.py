"""
Data Governance Protocol - Abstraction Contract (Layer 2)

Defines the interface for Data Steward policy operations: access requests,
materialization authorization, permission checks, and provenance validation.
Implementations are built inside Public Works (e.g. DataStewardPrimitives over
BoundaryContractStore); no supabase_adapter at boundary.

Consumed by GovernanceService / DataStewardSDK via get_data_governance_abstraction() only.

WHAT (Infrastructure Role): I define the contract for data governance operations
HOW (Infrastructure Implementation): Implementations use boundary_contract_store (protocol) inside PW only
"""

from typing import Protocol, Dict, Any, Optional, List


class DataGovernanceProtocol(Protocol):
    """
    Protocol for Data Steward primitives (data governance at boundary).

    Implementations provide request_data_access, authorize_materialization,
    check_data_permission, validate_provenance_chain, and optional boundary_contract_store.
    DataStewardSDK uses this via get_data_governance_abstraction(); never raw adapters.
    """

    @property
    def boundary_contract_store(self) -> Optional[Any]:
        """
        Optional boundary contract store (BoundaryContractStoreProtocol) for contract lookup.
        Used by DataStewardSDK for get_boundary_contract_by_id when promoting to record of fact.
        """
        ...

    async def request_data_access(
        self,
        intent: Dict[str, Any],
        context: Dict[str, Any],
        external_source_type: str,
        external_source_identifier: str,
        external_source_metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Request data access and negotiate boundary contract (first step before materialization).

        Returns:
            DataAccessRequest (access_granted, contract_id, access_reason, access_conditions)
        """
        ...

    async def authorize_materialization(
        self,
        contract_id: str,
        tenant_id: str,
        requested_type: Optional[str] = None,
        materialization_policy: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Authorize materialization: decide form, TTL, and backing store (second step after access).

        Returns:
            MaterializationAuthorization (materialization_allowed, materialization_type, scope, ttl, etc.)
        """
        ...

    async def check_data_permission(
        self,
        data_id: str,
        user_id: str,
        tenant_id: str,
        action: str,
    ) -> Any:
        """
        Check data permission (policy decision).

        Returns:
            DataPermissionCheck (is_allowed, data_id, reason)
        """
        ...

    async def validate_provenance_chain(
        self,
        provenance_chain: List[Dict[str, Any]],
        tenant_id: str,
    ) -> Any:
        """
        Validate provenance chain (policy decision).

        Returns:
            ProvenanceChainValidation (is_valid, chain, reason)
        """
        ...
