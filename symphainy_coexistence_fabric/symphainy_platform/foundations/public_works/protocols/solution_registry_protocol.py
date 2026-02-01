"""
Solution Registry Protocol - Abstraction Contract (Layer 2)

Defines the interface for solution registration, listing, and lifecycle.
Used by Control Tower (list_solutions, compose_solution) and Runtime/solution initializer.
Implementations may be in-memory (MVP) or backed by Curator/durable storage later.

WHAT (Infrastructure Role): I define the contract for solution registry operations
HOW (Infrastructure Implementation): Implementations wrap in-memory or durable store; no adapter at boundary
"""

from typing import Protocol, Dict, Any, Optional, List


class SolutionRegistryProtocol(Protocol):
    """
    Protocol for solution registry (list, get, register, activate, deactivate).

    Control Tower intent services use this via get_solution_registry() (ctx.platform).
    Implementations live in Public Works; may be in-memory or Curator-backed later.
    """

    def list_solutions(
        self,
        active_only: bool = False,
        domain: Optional[str] = None,
    ) -> List[Any]:
        """
        List solutions, optionally filtered by active status and domain.

        Returns:
            List of Solution (or dict) instances
        """
        ...

    def get_solution(self, solution_id: str) -> Optional[Any]:
        """Get solution by ID. Returns Solution or None."""
        ...

    def register_solution(self, solution: Any) -> bool:
        """Register a solution. Returns True if successful."""
        ...

    def activate_solution(self, solution_id: str) -> bool:
        """Activate a solution. Returns True if successful."""
        ...

    def deactivate_solution(self, solution_id: str) -> bool:
        """Deactivate a solution. Returns True if successful."""
        ...

    def is_solution_active(self, solution_id: str) -> bool:
        """Check if solution is active."""
        ...
