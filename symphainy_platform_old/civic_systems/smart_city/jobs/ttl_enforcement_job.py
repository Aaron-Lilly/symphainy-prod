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

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utilities import get_logger, get_clock
import uuid


class TTLEnforcementJob:
    """
    TTL Enforcement Job - Automated purge of expired Working Materials.
    
    This job enforces TTL policies for Working Materials by:
    - Finding expired materials (based on boundary contract materialization_expires_at)
    - Validating lifecycle state (only purge if appropriate)
    - Purging expired materials from GCS
    - Updating boundary contract status
    - Updating Records of Fact with source_expired_at
    """
    
    def __init__(
        self,
        supabase_adapter: Optional[Any] = None,
        gcs_adapter: Optional[Any] = None
    ):
        """
        Initialize TTL Enforcement Job.
        
        Args:
            supabase_adapter: Supabase adapter for database operations
            gcs_adapter: GCS adapter for purging expired materials
        """
        self.supabase_adapter = supabase_adapter
        self.gcs_adapter = gcs_adapter
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
        try:
            # Query boundary contracts where materialization_expires_at < NOW()
            # and contract_status is 'active'
            response = self.supabase_adapter.service_client.table("data_boundary_contracts").select(
                "*"
            ).eq(
                "contract_status", "active"
            ).lt(
                "materialization_expires_at", self.clock.now_iso()
            ).execute()
            
            if response.data:
                return response.data
            return []
            
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
        
        # 2. Purge expired material from GCS (if applicable)
        if materialization_type in ["full_artifact", "partial_extraction"]:
            if self.gcs_adapter and external_source_identifier:
                try:
                    # Extract file path from external_source_identifier or contract metadata
                    file_path = self._extract_file_path(contract)
                    if file_path:
                        await self._purge_from_gcs(file_path, tenant_id)
                        results["materials_purged"] += 1
                        self.logger.info(f"Purged expired material from GCS: {file_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to purge from GCS: {e}")
        
        # 3. Update boundary contract status to "expired"
        try:
            await self._update_contract_status(contract_id, tenant_id)
            results["contracts_updated"] += 1
        except Exception as e:
            self.logger.error(f"Failed to update contract status: {e}")
            raise
        
        # 4. Update Records of Fact with source_expired_at if applicable
        source_file_id = contract.get("external_source_metadata", {}).get("file_id")
        if source_file_id:
            try:
                updated_count = await self._update_records_of_fact(
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
    
    async def _purge_from_gcs(self, file_path: str, tenant_id: str) -> None:
        """
        Purge expired material from GCS.
        
        Args:
            file_path: GCS file path
            tenant_id: Tenant ID
        """
        if not self.gcs_adapter:
            self.logger.warning("GCS adapter not available, cannot purge from GCS")
            return
        
        try:
            # Extract bucket and blob name from path
            if file_path.startswith("gs://"):
                # Format: gs://bucket/path/to/file
                parts = file_path.replace("gs://", "").split("/", 1)
                if len(parts) == 2:
                    bucket_name = parts[0]
                    blob_name = parts[1]
                    await self.gcs_adapter.delete_blob(bucket_name, blob_name)
                    self.logger.info(f"Deleted blob from GCS: {bucket_name}/{blob_name}")
            else:
                # Assume it's a relative path, construct full path
                # This would need tenant_id to construct proper path
                self.logger.warning(f"Cannot purge from GCS: Invalid path format: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to purge from GCS: {e}", exc_info=True)
            raise
    
    async def _update_contract_status(self, contract_id: str, tenant_id: str) -> None:
        """
        Update boundary contract status to "expired".
        
        Args:
            contract_id: Contract ID
            tenant_id: Tenant ID
        """
        try:
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID."""
                if not value:
                    return None
                try:
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                    return str(uuid.uuid5(namespace, str(value)))
            
            self.supabase_adapter.service_client.table("data_boundary_contracts").update({
                "contract_status": "expired",
                "expired_at": self.clock.now_iso()
            }).eq("contract_id", to_uuid(contract_id)).eq(
                "tenant_id", to_uuid(tenant_id)
            ).execute()
            
        except Exception as e:
            self.logger.error(f"Failed to update contract status: {e}", exc_info=True)
            raise
    
    async def _update_records_of_fact(
        self,
        source_file_id: str,
        tenant_id: str,
        expired_at: str
    ) -> int:
        """
        Update Records of Fact with source_expired_at.
        
        Args:
            source_file_id: Source file ID
            tenant_id: Tenant ID
            expired_at: Expiration timestamp
        
        Returns:
            Number of Records of Fact updated
        """
        try:
            def to_uuid(value: Optional[str]) -> Optional[str]:
                """Convert string to UUID."""
                if not value:
                    return None
                try:
                    return str(uuid.UUID(value))
                except (ValueError, AttributeError):
                    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                    return str(uuid.uuid5(namespace, str(value)))
            
            # Update Records of Fact where source_file_id matches and source_expired_at is NULL
            response = self.supabase_adapter.service_client.table("records_of_fact").update({
                "source_expired_at": expired_at
            }).eq("source_file_id", to_uuid(source_file_id)).eq(
                "tenant_id", to_uuid(tenant_id)
            ).is_(
                "source_expired_at", "null"
            ).execute()
            
            if response.data:
                return len(response.data)
            return 0
            
        except Exception as e:
            self.logger.error(f"Failed to update Records of Fact: {e}", exc_info=True)
            return 0
