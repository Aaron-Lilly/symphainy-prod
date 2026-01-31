"""
TTL Enforcement Job - Automated purge of expired Working Materials.

This job runs periodically to:
1. Find expired Working Materials (based on boundary contract TTL)
2. Purge expired materials from GCS
3. Update boundary contract status to "expired"
4. Update Records of Fact with source_expired_at if applicable
5. Log all purges for audit

Implements "capability by design, implementation by policy" - real enforcement job
with policy-driven TTL (MVP: 30 days, production can tighten).
"""

import sys
from pathlib import Path

# TTL Enforcement Job is at: symphainy_platform/civic_systems/smart_city/jobs/ttl_enforcement_job.py
# Project root is 5 levels up
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
from utilities import get_logger, get_clock

if TYPE_CHECKING:
    from symphainy_platform.foundations.public_works.protocols.boundary_contract_store_protocol import BoundaryContractStoreProtocol
    from symphainy_platform.foundations.public_works.protocols.file_storage_protocol import FileStorageProtocol


class TTLEnforcementJob:
    """
    TTL Enforcement Job - Automated purge of expired Working Materials.

    Uses BoundaryContractStoreProtocol and FileStorageProtocol (from Public Works);
    adapters must not escape Public Works.
    """
    
    def __init__(
        self,
        boundary_contract_store: Optional["BoundaryContractStoreProtocol"] = None,
        file_storage: Optional["FileStorageProtocol"] = None,
    ):
        """
        Initialize TTL Enforcement Job.

        Args:
            boundary_contract_store: Boundary contract store (from Public Works get_boundary_contract_store())
            file_storage: File storage (from Public Works get_file_storage_abstraction()) for purging blobs
        """
        self.boundary_contract_store = boundary_contract_store
        self.file_storage = file_storage
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def run(self) -> Dict[str, Any]:
        """
        Run TTL enforcement job.
        
        Returns:
            Dict with execution results:
            {
                "expired_contracts_found": int,
                "materials_purged": int,
                "contracts_updated": int,
                "records_of_fact_updated": int,
                "errors": List[str]
            }
        """
        self.logger.info("Starting TTL enforcement job")
        
        results = {
            "expired_contracts_found": 0,
            "materials_purged": 0,
            "contracts_updated": 0,
            "records_of_fact_updated": 0,
            "errors": []
        }
        
        if not self.supabase_adapter:
            self.logger.warning("Supabase adapter not available, cannot run TTL enforcement job")
            results["errors"].append("Supabase adapter not available")
            return results
        
        try:
            # 1. Query boundary contracts for expired materials
            expired_contracts = await self._find_expired_contracts()
            results["expired_contracts_found"] = len(expired_contracts)
            
            self.logger.info(f"Found {len(expired_contracts)} expired boundary contracts")
            
            # 2. Process each expired contract
            for contract in expired_contracts:
                try:
                    await self._process_expired_contract(contract, results)
                except Exception as e:
                    error_msg = f"Failed to process expired contract {contract.get('contract_id')}: {e}"
                    self.logger.error(error_msg, exc_info=True)
                    results["errors"].append(error_msg)
            
            self.logger.info(
                f"TTL enforcement job completed: "
                f"{results['materials_purged']} materials purged, "
                f"{results['contracts_updated']} contracts updated, "
                f"{results['records_of_fact_updated']} records of fact updated"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"TTL enforcement job failed: {e}", exc_info=True)
            results["errors"].append(f"Job execution failed: {e}")
            return results
    
    async def _find_expired_contracts(self) -> List[Dict[str, Any]]:
        """
        Find boundary contracts with expired materials.
        
        Returns:
            List of expired boundary contracts
        """
        if not self.boundary_contract_store:
            raise RuntimeError(
                "Boundary contract store not wired; cannot list expired contracts. Platform contract §8A."
            )
        try:
            return await self.boundary_contract_store.list_expired_contracts(
                expired_before_iso=self.clock.now_iso()
            )
        except Exception as e:
            self.logger.error(f"Failed to find expired contracts: {e}", exc_info=True)
            return []
    
    async def _process_expired_contract(
        self,
        contract: Dict[str, Any],
        results: Dict[str, Any]
    ) -> None:
        """
        Process a single expired contract.
        
        Args:
            contract: Expired boundary contract
            results: Results dictionary to update
        """
        contract_id = contract.get("contract_id")
        tenant_id = contract.get("tenant_id")
        materialization_type = contract.get("materialization_type")
        external_source_identifier = contract.get("external_source_identifier")
        
        self.logger.info(f"Processing expired contract: {contract_id}")
        
        # 1. Validate lifecycle state (only purge if appropriate)
        # For MVP: Purge all expired materials
        # Production: Can add lifecycle state validation here
        
        # 2. Purge expired material from file storage (if applicable)
        if materialization_type in ["full_artifact", "partial_extraction"]:
            if self.file_storage and external_source_identifier:
                try:
                    file_path = self._extract_file_path(contract)
                    if file_path:
                        await self._purge_from_storage(file_path, tenant_id)
                        results["materials_purged"] += 1
                        self.logger.info(f"Purged expired material: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to purge from storage: {e}")
        
        # 3. Update boundary contract status to "expired"
        try:
            await self._update_contract_status(contract_id, tenant_id)
            results["contracts_updated"] += 1
        except Exception as e:
            self.logger.error(f"Failed to update contract status: {e}")
            raise
        
        # 4. Update Records of Fact with source_expired_at if applicable
        source_file_id = contract.get("external_source_metadata", {}).get("file_id")
        if source_file_id and self.boundary_contract_store:
            try:
                updated_count = await self.boundary_contract_store.update_records_of_fact_expired(
                    source_file_id=source_file_id,
                    tenant_id=tenant_id,
                    expired_at=self.clock.now_iso()
                )
                results["records_of_fact_updated"] += updated_count
                if updated_count > 0:
                    self.logger.info(f"Updated {updated_count} Records of Fact with source_expired_at")
            except Exception as e:
                self.logger.warning(f"Failed to update Records of Fact: {e}")
    
    def _extract_file_path(self, contract: Dict[str, Any]) -> Optional[str]:
        """
        Extract file path from contract for GCS purging.
        
        Args:
            contract: Boundary contract
        
        Returns:
            File path or None
        """
        # Try to get file path from contract metadata
        metadata = contract.get("external_source_metadata", {})
        file_path = metadata.get("file_path") or metadata.get("storage_path")
        
        if not file_path:
            # Try external_source_identifier
            external_source_identifier = contract.get("external_source_identifier")
            if external_source_identifier and external_source_identifier.startswith("gs://"):
                return external_source_identifier
        
        return file_path
    
    async def _purge_from_storage(self, file_path: str, tenant_id: str) -> None:
        """
        Purge expired material via FileStorageProtocol.

        Args:
            file_path: Path (gs://bucket/path or blob path within default bucket)
            tenant_id: Tenant ID (for logging)
        """
        if not self.file_storage:
            self.logger.warning("File storage not available, cannot purge")
            return
        try:
            # FileStorageProtocol.delete_file(file_path): blob path within bucket
            if file_path.startswith("gs://"):
                # Use path after gs://bucket/ as blob path (assumes single default bucket)
                parts = file_path.replace("gs://", "").split("/", 1)
                blob_path = parts[1] if len(parts) == 2 else file_path
            else:
                blob_path = file_path
            await self.file_storage.delete_file(blob_path)
            self.logger.info(f"Deleted from storage: {blob_path}")
        except Exception as e:
            self.logger.error(f"Failed to purge from storage: {e}", exc_info=True)
            raise

    async def _update_contract_status(self, contract_id: str, tenant_id: str) -> None:
        """Update boundary contract status to expired via protocol."""
        if not self.boundary_contract_store:
            return
        try:
            await self.boundary_contract_store.update_contract_status_expired(
                contract_id=contract_id,
                tenant_id=tenant_id,
                expired_at_iso=self.clock.now_iso()
            )
        except Exception as e:
            self.logger.error(f"Failed to update contract status: {e}", exc_info=True)
            raise
