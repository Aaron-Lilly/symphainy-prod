"""
Data Steward Primitives - Policy Decisions for Data Governance

Primitives for Data Steward policy decisions (used by Runtime only).
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from dataclasses import dataclass

from utilities import get_logger


@dataclass
class DataPermissionCheck:
    """Data permission check result."""
    is_allowed: bool
    data_id: str
    reason: Optional[str] = None


@dataclass
class ProvenanceChainValidation:
    """Provenance chain validation result."""
    is_valid: bool
    chain: List[Dict[str, Any]]
    reason: Optional[str] = None


class DataStewardPrimitives:
    """
    Data Steward Primitives - Policy Decisions
    
    Makes policy decisions for data governance.
    """
    
    def __init__(self, policy_store: Optional[Any] = None):
        self.policy_store = policy_store
        self.logger = get_logger(self.__class__.__name__)
    
    async def check_data_permission(
        self,
        data_id: str,
        user_id: str,
        tenant_id: str,
        action: str
    ) -> DataPermissionCheck:
        """Check data permission (policy decision)."""
        # MVP: Basic validation
        if not data_id:
            return DataPermissionCheck(
                is_allowed=False,
                data_id=data_id,
                reason="Data ID is required"
            )
        
        return DataPermissionCheck(
            is_allowed=True,
            data_id=data_id
        )
    
    async def validate_provenance_chain(
        self,
        provenance_chain: List[Dict[str, Any]],
        tenant_id: str
    ) -> ProvenanceChainValidation:
        """Validate provenance chain (policy decision)."""
        # MVP: Basic validation
        if not provenance_chain:
            return ProvenanceChainValidation(
                is_valid=False,
                chain=provenance_chain,
                reason="Provenance chain is required"
            )
        
        return ProvenanceChainValidation(
            is_valid=True,
            chain=provenance_chain
        )
