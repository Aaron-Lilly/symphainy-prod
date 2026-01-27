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
from dataclasses import dataclass
import uuid

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
        policy_resolver: Optional[Any] = None,
        data_steward_primitives: Optional[DataStewardPrimitives] = None,
        materialization_policy: Optional[Any] = None
    ):
        self.data_governance = data_governance_abstraction
        self.policy_resolver = policy_resolver
        self.data_steward_primitives = data_steward_primitives
        self.materialization_policy = materialization_policy
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
            # Data Steward primitives are required - no fallback
            raise RuntimeError(
                "Data Steward primitives not available. "
                "All data access must go through Data Steward for boundary contract assignment."
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
        requested_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        materialization_policy: Optional[Any] = None
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
            # Data Steward primitives are required - no fallback
            raise RuntimeError(
                "Data Steward primitives not available. "
                "All materialization must be authorized through Data Steward."
            )
        
        # Use provided materialization_policy or fall back to instance policy
        policy = materialization_policy or self.materialization_policy
        
        return await self.data_steward_primitives.authorize_materialization(
            contract_id=contract_id,
            tenant_id=tenant_id,
            requested_type=requested_type,
            context=context,
            materialization_policy=policy
        )
    
    async def promote_to_record_of_fact(
        self,
        source_file_id: str,
        source_boundary_contract_id: str,
        tenant_id: str,
        record_type: str,  # 'deterministic_embedding', 'semantic_embedding', 'interpretation', 'conclusion'
        record_content: Dict[str, Any],
        embedding_id: Optional[str] = None,
        interpretation_id: Optional[str] = None,
        arango_collection: Optional[str] = None,
        arango_key: Optional[str] = None,
        model_name: Optional[str] = None,
        confidence_score: Optional[float] = None,
        promoted_by: Optional[str] = None,
        promotion_reason: Optional[str] = None,
        supabase_adapter: Optional[Any] = None
    ) -> Optional[str]:
        """
        Promote Working Material to Record of Fact.
        
        This is an explicit workflow that creates a persistent Record of Fact
        from a Working Material. The Record of Fact persists even if the source
        Working Material expires.
        
        Args:
            source_file_id: File ID of source Working Material
            source_boundary_contract_id: Boundary contract ID that authorized materialization
            tenant_id: Tenant identifier
            record_type: Type of record ('deterministic_embedding', 'semantic_embedding', 'interpretation', 'conclusion')
            record_content: The actual record content (meaning, conclusion, etc.)
            embedding_id: Optional embedding ID (if record_type is embedding)
            interpretation_id: Optional interpretation ID (if record_type is interpretation)
            arango_collection: Optional ArangoDB collection name
            arango_key: Optional ArangoDB document key
            model_name: Optional model name (for embeddings)
            confidence_score: Optional confidence score
            promoted_by: Who/what initiated the promotion
            promotion_reason: Reason for promotion
            supabase_adapter: Supabase adapter for database operations
        
        Returns:
            Record ID (UUID string) or None if promotion failed
        """
        try:
            # Validate record_type
            valid_types = ['deterministic_embedding', 'semantic_embedding', 'interpretation', 'conclusion']
            if record_type not in valid_types:
                self.logger.error(f"Invalid record_type: {record_type}. Must be one of: {valid_types}")
                return None
            
            # Validate boundary contract has appropriate materialization type
            if self.data_steward_primitives and self.data_steward_primitives.boundary_contract_store:
                try:
                    contract = await self.data_steward_primitives.boundary_contract_store.get_boundary_contract_by_id(
                        contract_id=source_boundary_contract_id,
                        tenant_id=tenant_id
                    )
                    
                    if not contract:
                        self.logger.error(f"Boundary contract not found: {source_boundary_contract_id}")
                        return None
                    
                    materialization_type = contract.get("materialization_type")
                    if record_type in ['deterministic_embedding', 'semantic_embedding']:
                        if materialization_type not in ['deterministic', 'semantic_embedding']:
                            self.logger.warning(
                                f"Boundary contract materialization_type ({materialization_type}) "
                                f"does not match record_type ({record_type}), but proceeding with promotion"
                            )
                except Exception as e:
                    self.logger.warning(f"Failed to validate boundary contract: {e}, proceeding with promotion")
            
            # Create Record of Fact entry in Supabase
            if not supabase_adapter:
                self.logger.warning("Supabase adapter not available, cannot create Record of Fact")
                return None
            
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID."""
                if not value:
                    return None
                try:
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                    return str(uuid.uuid5(namespace, str(value)))
            
            record_data = {
                "tenant_id": to_uuid(tenant_id),
                "record_type": record_type,
                "source_file_id": to_uuid(source_file_id),
                "source_boundary_contract_id": to_uuid(source_boundary_contract_id),
                "source_expired_at": None,  # Source not expired yet
                "embedding_id": to_uuid(embedding_id) if embedding_id else None,
                "interpretation_id": to_uuid(interpretation_id) if interpretation_id else None,
                "arango_collection": arango_collection,
                "arango_key": arango_key,
                "record_content": record_content,
                "model_name": model_name,
                "confidence_score": confidence_score,
                "promoted_at": self.clock.now_iso(),
                "promoted_by": promoted_by or "system",
                "promotion_reason": promotion_reason,
                "metadata": {}
            }
            
            response = supabase_adapter.service_client.table("records_of_fact").insert(
                record_data
            ).execute()
            
            if response.data and len(response.data) > 0:
                record_id = response.data[0].get("record_id")
                self.logger.info(f"✅ Promoted to Record of Fact: {record_id} (type: {record_type})")
                return str(record_id)
            else:
                self.logger.error("Failed to create Record of Fact: No data returned")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to promote to Record of Fact: {e}", exc_info=True)
            return None