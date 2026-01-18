"""
Materialization Policy Abstraction

Implements materialization policy evaluation logic.

WHAT (Abstraction Role): I evaluate materialization policy for realm results
HOW (Abstraction Implementation): I use default policy + solution config overrides
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from .materialization_policy_protocol import (
    MaterializationPolicyProtocol,
    MaterializationDecision
)


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
    "unknown": "discard",          # Unknown types are ephemeral
}


# MVP Policy Override: Persist for demo purposes
MVP_POLICY_OVERRIDE = {
    # Platform-native records (always persisted in State Surface / WAL)
    "intent": "persist",
    "journey": "persist",
    "state_transition": "persist",
    "governance_decision": "persist",
    
    # Derived artifacts (MVP persists for demo purposes)
    "workflow": "persist",
    "sop": "persist",
    "blueprint": "persist",
    "solution": "persist",
    "roadmap": "persist",
    "poc": "persist",
    "visual": "persist",
}


class MaterializationPolicyAbstraction(MaterializationPolicyProtocol):
    """
    Materialization policy abstraction.
    
    Evaluates materialization policy based on:
    - Default platform policy (ephemeral by default)
    - Solution configuration overrides (client-specific)
    - Smart City governance rules (future)
    """
    
    def __init__(
        self,
        default_policy: Optional[Dict[str, str]] = None,
        solution_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Materialization Policy abstraction.
        
        Args:
            default_policy: Optional default policy (uses DEFAULT_POLICY if None)
            solution_config: Optional solution-specific configuration
        """
        self.default_policy = default_policy or DEFAULT_POLICY
        self.solution_config = solution_config or {}
        self.logger = get_logger(self.__class__.__name__)
        
        self.logger.info("Materialization Policy Abstraction initialized")
        if solution_config:
            self.logger.info(f"Solution config provided with {len(solution_config)} keys")
    
    async def evaluate_policy(
        self,
        result_type: str,
        semantic_payload: Dict[str, Any],
        renderings: Dict[str, Any],
        intent: Any,
        context: Any,
        solution_config: Optional[Dict[str, Any]] = None
    ) -> MaterializationDecision:
        """
        Evaluate materialization policy.
        
        Priority:
        1. Solution config override (highest priority)
        2. Default platform policy
        3. DISCARD (safest default)
        
        Args:
            result_type: Type of result (e.g., 'workflow', 'sop')
            semantic_payload: Semantic representation
            renderings: Rendered artifacts
            intent: Intent object
            context: Execution context
            solution_config: Optional solution config (overrides instance config)
        
        Returns:
            MaterializationDecision: PERSIST, CACHE, or DISCARD
        """
        # Use provided solution_config or instance solution_config
        active_solution_config = solution_config or self.solution_config
        materialization_policy = active_solution_config.get("materialization_policy", {})
        
        # Check solution config override (highest priority)
        if result_type in materialization_policy:
            decision_str = materialization_policy[result_type]
            if decision_str == "persist":
                self.logger.debug(f"Policy: {result_type} -> PERSIST (solution config override)")
                return MaterializationDecision.PERSIST
            elif decision_str == "cache":
                self.logger.debug(f"Policy: {result_type} -> CACHE (solution config override)")
                return MaterializationDecision.CACHE
            elif decision_str == "discard":
                self.logger.debug(f"Policy: {result_type} -> DISCARD (solution config override)")
                return MaterializationDecision.DISCARD
        
        # Check default policy
        if result_type in self.default_policy:
            decision_str = self.default_policy[result_type]
            if decision_str == "persist":
                self.logger.debug(f"Policy: {result_type} -> PERSIST (default policy)")
                return MaterializationDecision.PERSIST
            elif decision_str == "cache":
                self.logger.debug(f"Policy: {result_type} -> CACHE (default policy)")
                return MaterializationDecision.CACHE
        
        # Default: DISCARD (ephemeral)
        self.logger.debug(f"Policy: {result_type} -> DISCARD (default: ephemeral)")
        return MaterializationDecision.DISCARD
    
    def get_default_policy(self) -> Dict[str, str]:
        """Get default materialization policy."""
        return self.default_policy.copy()
