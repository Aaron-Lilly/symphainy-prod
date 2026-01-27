"""
Materialization Policy SDK - Policy Configuration Coordination

SDK for Materialization Policy coordination (used by Experience, Solution, Realms).

WHAT (Smart City Role): I coordinate materialization policy configuration
HOW (SDK Implementation): I prepare execution contracts for Runtime validation

⚠️ CRITICAL: NO Runtime dependency.
SDKs prepare execution contracts. Runtime validates and executes them.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, get_clock


class MaterializationPolicySDK:
    """
    Materialization Policy SDK - Coordination Logic
    
    Coordinates materialization policy configuration.
    Prepares execution contracts for Runtime validation.
    
    ⚠️ NO Runtime dependency - SDKs prepare, Runtime executes.
    """
    
    def __init__(
        self,
        config_abstraction: Optional[Any] = None  # Config abstraction (optional for MVP)
    ):
        """
        Initialize Materialization Policy SDK.
        
        Args:
            config_abstraction: Optional config abstraction (from Public Works)
        """
        self.config_abstraction = config_abstraction
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("Materialization Policy SDK initialized (NO Runtime dependency)")
    
    async def configure_materialization_policy(
        self,
        solution_id: str,
        tenant_id: str,
        policy_overrides: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Configure materialization policy for solution (prepare execution contract).
        
        Args:
            solution_id: Solution identifier
            tenant_id: Tenant identifier
            policy_overrides: Policy overrides (result_type -> decision)
        
        Returns:
            Dict with execution contract for Runtime validation
        """
        execution_contract = {
            "action": "configure_materialization_policy",
            "solution_id": solution_id,
            "tenant_id": tenant_id,
            "materialization_policy": policy_overrides,
            "timestamp": self.clock.now_iso()
        }
        
        self.logger.info(f"Prepared materialization policy configuration contract for solution: {solution_id}")
        return execution_contract
    
    async def get_materialization_policy(
        self,
        solution_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get materialization policy for solution (prepare query contract).
        
        Args:
            solution_id: Solution identifier
            tenant_id: Tenant identifier
        
        Returns:
            Dict with execution contract for Runtime query
        """
        execution_contract = {
            "action": "get_materialization_policy",
            "solution_id": solution_id,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return execution_contract
