"""
Materialization Policy Protocol

Defines the contract for materialization policy evaluation.

WHAT (Protocol Role): I define the contract for materialization policy evaluation
HOW (Protocol Implementation): I use Protocol typing to define the interface
"""

from typing import Protocol, Dict, Any, Optional
from enum import Enum


class MaterializationDecision(Enum):
    """Materialization decision types."""
    PERSIST = "persist"      # Store artifact permanently
    CACHE = "cache"         # Store temporarily (e.g., for session)
    DISCARD = "discard"      # Don't store (ephemeral)


class MaterializationPolicyProtocol(Protocol):
    """Protocol for materialization policy evaluation."""
    
    async def evaluate_policy(
        self,
        result_type: str,  # 'workflow', 'sop', 'solution', etc.
        semantic_payload: Dict[str, Any],
        renderings: Dict[str, Any],
        intent: Any,  # Intent object
        context: Any,  # ExecutionContext
        solution_config: Optional[Dict[str, Any]] = None
    ) -> MaterializationDecision:
        """
        Evaluate materialization policy for a realm result.
        
        Args:
            result_type: Type of result (e.g., 'workflow', 'sop', 'blueprint')
            semantic_payload: Semantic representation of the result
            renderings: Rendered artifacts (documents, charts, etc.)
            intent: The intent that produced this result
            context: Execution context
            solution_config: Optional solution-specific configuration
        
        Returns:
            MaterializationDecision: PERSIST, CACHE, or DISCARD
        """
        ...
    
    def get_default_policy(self) -> Dict[str, str]:
        """
        Get default materialization policy.
        
        Returns:
            Dict mapping result_type to decision (default: all ephemeral)
        """
        ...
