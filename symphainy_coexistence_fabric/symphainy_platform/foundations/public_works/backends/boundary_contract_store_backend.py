"""
Boundary Contract Store Backend - BoundaryContractStoreProtocol implementation

Implements BoundaryContractStoreProtocol using SupabaseAdapter.
Used by DataStewardPrimitives, DataStewardSDK, and TTLEnforcementJob.
Lives inside Public Works; callers receive only BoundaryContractStoreProtocol.
"""

from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

from utilities import get_logger, get_clock
from ..adapters.supabase_adapter import SupabaseAdapter


def _to_uuid(value: Optional[str]) -> Optional[str]:
    """Convert string to UUID; deterministic uuid5 for non-UUID strings."""
    if not value:
        return None
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError):
        namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
        return str(uuid.uuid5(namespace, str(value)))


class BoundaryContractStoreBackend:
    """
    BoundaryContractStoreProtocol implementation using Supabase.

    Wraps SupabaseAdapter for data_boundary_contracts and records_of_fact.
    Created by foundation_service when Supabase is available; exposed via get_boundary_contract_store().
    """

    def __init__(self, supabase_adapter: SupabaseAdapter):
        self._supabase = supabase_adapter
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()

    async def create_boundary_contract(self, contract_data: Dict[str, Any]) -> Optional[str]:
        if not self._supabase:
            raise RuntimeError(
                "Supabase adapter not wired; cannot create boundary contract. Platform contract §8A."
            )
        try:
            if "contract_id" not in contract_data:
                contract_data["contract_id"] = str(uuid.uuid4())
            response = self._supabase.service_client.table("data_boundary_contracts").insert(
                contract_data
            ).execute()
            if response.data and len(response.data) > 0:
                return response.data[0].get("contract_id")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create boundary contract: {e}", exc_info=True)
            return None

    async def get_boundary_contract(
        self,
        tenant_id: str,
        external_source_type: str,
        external_source_identifier: str
    ) -> Optional[Dict[str, Any]]:
        if not self._supabase:
            raise RuntimeError(
                "Supabase adapter not wired; cannot get boundary contract. Platform contract §8A."
            )
        try:
            response = self._supabase.service_client.table("data_boundary_contracts").select(
                "*"
            ).eq("tenant_id", _to_uuid(tenant_id)).eq(
                "external_source_type", external_source_type
            ).eq(
                "external_source_identifier", external_source_identifier
            ).eq("contract_status", "active").order("created_at", desc=True).limit(1).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            self.logger.error(f"Failed to get boundary contract: {e}", exc_info=True)
            return None

    async def get_boundary_contract_by_id(
        self, contract_id: str, tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        if not self._supabase:
            raise RuntimeError(
                "Supabase adapter not wired; cannot get boundary contract by ID. Platform contract §8A."
            )
        try:
            response = self._supabase.service_client.table("data_boundary_contracts").select(
                "*"
            ).eq("contract_id", _to_uuid(contract_id)).eq("tenant_id", _to_uuid(tenant_id)).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            self.logger.error(f"Failed to get boundary contract by ID: {e}", exc_info=True)
            return None

    async def update_boundary_contract(
        self,
        contract_id: str,
        tenant_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        if not self._supabase:
            raise RuntimeError(
                "Supabase adapter not wired; cannot update boundary contract. Platform contract §8A."
            )
        try:
            updates["updated_at"] = datetime.utcnow().isoformat() + "Z"
            response = self._supabase.service_client.table("data_boundary_contracts").update(
                updates
            ).eq("contract_id", _to_uuid(contract_id)).eq("tenant_id", _to_uuid(tenant_id)).execute()
            return bool(response.data)
        except Exception as e:
            self.logger.error(f"Failed to update boundary contract: {e}", exc_info=True)
            return False

    async def list_expired_contracts(self, expired_before_iso: str) -> List[Dict[str, Any]]:
        if not self._supabase:
            raise RuntimeError(
                "Supabase adapter not wired; cannot list expired contracts. Platform contract §8A."
            )
        try:
            response = self._supabase.service_client.table("data_boundary_contracts").select(
                "*"
            ).eq("contract_status", "active").lt(
                "materialization_expires_at", expired_before_iso
            ).execute()
            return response.data if response.data else []
        except Exception as e:
            self.logger.error(f"Failed to list expired contracts: {e}", exc_info=True)
            return []

    async def update_contract_status_expired(
        self, contract_id: str, tenant_id: str, expired_at_iso: str
    ) -> bool:
        if not self._supabase:
            raise RuntimeError(
                "Supabase adapter not wired; cannot update contract status. Platform contract §8A."
            )
        try:
            response = self._supabase.service_client.table("data_boundary_contracts").update({
                "contract_status": "expired",
                "expired_at": expired_at_iso
            }).eq("contract_id", _to_uuid(contract_id)).eq(
                "tenant_id", _to_uuid(tenant_id)
            ).execute()
            return bool(response.data)
        except Exception as e:
            self.logger.error(f"Failed to update contract status: {e}", exc_info=True)
            return False

    async def update_records_of_fact_expired(
        self, source_file_id: str, tenant_id: str, expired_at: str
    ) -> int:
        if not self._supabase:
            raise RuntimeError(
                "Supabase adapter not wired; cannot update records of fact. Platform contract §8A."
            )
        try:
            response = self._supabase.service_client.table("records_of_fact").update({
                "source_expired_at": expired_at
            }).eq("source_file_id", _to_uuid(source_file_id)).eq(
                "tenant_id", _to_uuid(tenant_id)
            ).is_("source_expired_at", None).execute()
            return len(response.data) if response.data else 0
        except Exception as e:
            self.logger.error(f"Failed to update records_of_fact: {e}", exc_info=True)
            return 0
