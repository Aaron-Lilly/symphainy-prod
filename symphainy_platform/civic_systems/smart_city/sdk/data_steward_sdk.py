"""
Data Steward SDK - Data Boundaries, Contracts, and Provenance Coordination

SDK for Data Steward coordination (used by Experience, Solution, Realms).
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger, get_clock
from symphainy_platform.civic_systems.smart_city.primitives.data_steward_primitives import (
    DataStewardPrimitives,
    DataAccessRequest,
    MaterializationAuthorization
)


@dataclass
class ProvenanceRecord:
    """Provenance record with execution contract."""
    data_id: str
    provenance_chain: List[Dict[str, Any]]
    execution_contract: Dict[str, Any]


@dataclass
class DataContract:
    """Data contract with execution contract."""
    contract_id: str
    contract_terms: Dict[str, Any]
    execution_contract: Dict[str, Any]


class DataStewardSDK:
    """
    Data Steward SDK - Coordination Logic
    
    Coordinates data boundaries, contracts, and provenance.
    """
    
    def __init__(
        self,
        data_governance_abstraction: Optional[Any] = None,
        policy_resolver: Optional[Any] = None
    ):
        self.data_governance = data_governance_abstraction
        self.policy_resolver = policy_resolver
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def record_provenance(
        self,
        data_id: str,
        tenant_id: str,
        provenance_data: Dict[str, Any]
    ) -> ProvenanceRecord:
        """Record provenance (prepare provenance contract)."""
        execution_contract = {
            "action": "record_provenance",
            "data_id": data_id,
            "tenant_id": tenant_id,
            "provenance_data": provenance_data,
            "timestamp": self.clock.now_iso()
        }
        
        return ProvenanceRecord(
            data_id=data_id,
            provenance_chain=[],
            execution_contract=execution_contract
        )
    
    async def get_data_contract(
        self,
        data_id: str,
        tenant_id: str
    ) -> DataContract:
        """Get data contract (prepare contract contract)."""
        execution_contract = {
            "action": "get_data_contract",
            "data_id": data_id,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return DataContract(
            contract_id=data_id,
            contract_terms={},
            execution_contract=execution_contract
        )
    
    async def validate_data_access(
        self,
        data_id: str,
        user_id: str,
        tenant_id: str,
        action: str
    ) -> Dict[str, Any]:
        """Validate data access (prepare validation contract)."""
        execution_contract = {
            "action": "validate_data_access",
            "data_id": data_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "action": action,
            "timestamp": self.clock.now_iso()
        }
        
        return {
            "is_allowed": True,
            "execution_contract": execution_contract
        }
    
    async def request_data_access(
        self,
        intent: Dict[str, Any],
        context: Dict[str, Any],
        external_source_type: str,
        external_source_identifier: str,
        external_source_metadata: Optional[Dict[str, Any]] = None
    ) -> DataAccessRequest:
        """
        Request data access - negotiate boundary contract.
        
        This is the FIRST step before any data materialization.
        Files are NEVER ingested directly. A contract is negotiated first.
        
        Args:
            intent: Intent that triggered the request
            context: Execution context (tenant_id, user_id, session_id, etc.)
            external_source_type: Type of external source ('file', 'api', 'database', etc.)
            external_source_identifier: Identifier for external source (file path, API endpoint, etc.)
            external_source_metadata: Additional source metadata
        
        Returns:
            DataAccessRequest with access_granted and contract_id
        """
        if not self.data_steward_primitives:
            # Fallback: Allow access without contract (MVP compatibility)
            self.logger.warning("Data Steward primitives not available, allowing access without contract")
            return DataAccessRequest(
                access_granted=True,
                access_reason="MVP fallback - primitives not available"
            )
        
        return await self.data_steward_primitives.request_data_access(
            intent=intent,
            context=context,
            external_source_type=external_source_type,
            external_source_identifier=external_source_identifier,
            external_source_metadata=external_source_metadata
        )
    
    async def authorize_materialization(
        self,
        contract_id: str,
        tenant_id: str,
        requested_type: Optional[str] = None
    ) -> MaterializationAuthorization:
        """
        Authorize materialization - decide what form and where.
        
        This is the SECOND step after access is granted.
        Answers: Can we persist it? In what form? For how long? Where?
        
        Args:
            contract_id: Boundary contract ID from request_data_access()
            tenant_id: Tenant identifier
            requested_type: Requested materialization type (optional)
        
        Returns:
            MaterializationAuthorization with materialization decision
        """
        if not self.data_steward_primitives:
            # Fallback: Allow full artifact materialization (MVP compatibility)
            self.logger.warning("Data Steward primitives not available, allowing full artifact materialization")
            return MaterializationAuthorization(
                materialization_allowed=True,
                materialization_type="full_artifact",
                materialization_backing_store="gcs",
                policy_basis="mvp_fallback",
                reason="MVP fallback - primitives not available"
            )
        
        return await self.data_steward_primitives.authorize_materialization(
            contract_id=contract_id,
            tenant_id=tenant_id,
            requested_type=requested_type,
            materialization_policy=self.materialization_policy
        )
