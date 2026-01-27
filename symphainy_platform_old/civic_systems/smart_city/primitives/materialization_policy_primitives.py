"""
Materialization Policy Primitives - Policy Validation for Artifact Materialization

Primitives for Materialization Policy decisions (used by Runtime only).

WHAT (Smart City Role): I validate materialization policies and make persistence decisions
HOW (Primitive Implementation): I provide pure functions, no side effects, deterministic

⚠️ CRITICAL: Primitives are used by Runtime only.
SDKs prepare execution contracts. Primitives validate them.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from enum import Enum
from utilities import get_logger
import yaml
import os


class MaterializationDecision(Enum):
    """Materialization decision types."""
    PERSIST = "persist"      # Store artifact permanently
    CACHE = "cache"         # Store temporarily (e.g., for session)
    DISCARD = "discard"      # Don't store (ephemeral)


# Default Policy: Ephemeral by default (platform-native)
DEFAULT_POLICY = {
    # Platform-native records (always stored in State Surface / WAL)
    "intent": "persist",           # Always stored
    "journey": "persist",          # Always stored
    "state_transition": "persist", # Always stored
    "governance_decision": "persist", # Always stored
    
    # Derived artifacts (ephemeral by default)
    "workflow": "discard",         # Ephemeral by default
    "sop": "discard",              # Ephemeral by default
    "blueprint": "discard",        # Ephemeral by default
    "solution": "discard",         # Ephemeral by default
    "roadmap": "discard",          # Ephemeral by default
    "poc": "discard",              # Ephemeral by default
    "visual": "discard",           # Ephemeral by default
    "file": "discard",             # Ephemeral by default
    "file_list": "discard",        # Ephemeral by default
    "unknown": "discard",          # Unknown types are ephemeral
}


class MaterializationPolicyStore:
    """
    Materialization policy store interface (abstract).
    
    In MVP: Load from config file (YAML)
    In full: ArangoDB graph-based policy store with caching
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Materialization Policy Store.
        
        Args:
            config_path: Optional path to policy config file (YAML)
        """
        self.config_path = config_path
        self.policy_cache: Optional[Dict[str, str]] = None
        self.logger = get_logger(self.__class__.__name__)
    
    async def get_materialization_policy(
        self,
        tenant_id: str,
        solution_id: Optional[str] = None,
        result_type: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get materialization policy for tenant/solution/result_type.
        
        Args:
            tenant_id: Tenant identifier
            solution_id: Optional solution identifier
            result_type: Optional result type filter
        
        Returns:
            Dict mapping result_type to decision ("persist", "cache", "discard")
        """
        # Load policy from config file if not cached
        if self.policy_cache is None:
            self.policy_cache = await self._load_policy_from_config()
        
        # Return full policy or filtered by result_type
        if result_type:
            return {result_type: self.policy_cache.get(result_type, "discard")}
        return self.policy_cache.copy()
    
    async def _load_policy_from_config(self) -> Dict[str, str]:
        """
        Load materialization policy from config file.
        
        Returns:
            Dict mapping result_type to decision
        """
        # Try to load from config file
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    materialization_policy = config.get("materialization_policy", {})
                    self.logger.info(f"Loaded materialization policy from {self.config_path}")
                    return materialization_policy
            except Exception as e:
                self.logger.warning(f"Failed to load policy from {self.config_path}: {e}")
        
        # Fallback to default policy
        self.logger.info("Using default materialization policy (ephemeral by default)")
        return DEFAULT_POLICY.copy()
    
    async def evaluate_policy(
        self,
        policy: Dict[str, str],
        result_type: str
    ) -> str:
        """
        Evaluate a single policy for result_type.
        
        Args:
            policy: Policy dictionary (result_type -> decision)
            result_type: Result type to evaluate
        
        Returns:
            Decision string: "persist", "cache", or "discard"
        """
        # Check if result_type is in policy
        if result_type in policy:
            return policy[result_type]
        
        # Default: DISCARD (ephemeral)
        return "discard"


class MaterializationPolicyPrimitives:
    """
    Materialization Policy Primitives - Policy Validation
    
    Pure functions for materialization policy evaluation.
    Used by Runtime only.
    """
    
    def __init__(self, policy_store: Optional[MaterializationPolicyStore] = None):
        """
        Initialize Materialization Policy Primitives.
        
        Args:
            policy_store: Optional policy store (for MVP, can be None)
        """
        self.policy_store = policy_store or MaterializationPolicyStore()
        self.logger = get_logger(self.__class__.__name__)
    
    @staticmethod
    async def evaluate_policy(
        result_type: str,
        semantic_payload: Dict[str, Any],
        renderings: Dict[str, Any],
        intent: Any,
        context: Any,
        policy_store: MaterializationPolicyStore,
        execution_contract: Dict[str, Any]
    ) -> MaterializationDecision:
        """
        Evaluate materialization policy (Primitive - pure function, no side effects).
        
        This is called by Runtime to validate the execution contract
        prepared by Materialization Policy SDK (or Runtime itself).
        
        Args:
            result_type: Type of result (e.g., 'workflow', 'sop', 'file')
            semantic_payload: Semantic representation of the result
            renderings: Rendered artifacts (documents, charts, etc.)
            intent: Intent object
            context: Execution context
            policy_store: Policy store instance
            execution_contract: Execution contract prepared by SDK (or Runtime)
        
        Returns:
            MaterializationDecision: PERSIST, CACHE, or DISCARD
        """
        try:
            # 1. Get policy from policy store
            tenant_id = execution_contract.get("tenant_id") or (intent.tenant_id if hasattr(intent, 'tenant_id') else None)
            solution_id = execution_contract.get("solution_id") or (intent.solution_id if hasattr(intent, 'solution_id') else None)
            
            # If SDK prepared policy in execution contract, use those
            if execution_contract.get("materialization_policy"):
                policy = execution_contract.get("materialization_policy")
            else:
                # Load policy from store
                policy = await policy_store.get_materialization_policy(
                    tenant_id=tenant_id or "default",
                    solution_id=solution_id,
                    result_type=result_type
                )
            
            # 2. Evaluate policy (deterministic)
            decision_str = await policy_store.evaluate_policy(policy, result_type)
            
            # 3. Convert to MaterializationDecision enum
            if decision_str == "persist":
                return MaterializationDecision.PERSIST
            elif decision_str == "cache":
                return MaterializationDecision.CACHE
            else:
                return MaterializationDecision.DISCARD
            
        except Exception as e:
            # Log error but return DISCARD (fail secure - don't persist if policy evaluation fails)
            logger = get_logger("MaterializationPolicyPrimitives")
            logger.error(f"Materialization policy evaluation failed: {e}", exc_info=True)
            return MaterializationDecision.DISCARD
