"""
Solution Registry - Registry for Managing Solutions

Manages solution registration, resolution, and lifecycle.

WHAT (Platform SDK Role): I manage Solutions in the platform
HOW (Platform SDK Implementation): I provide registry for Solutions with validation
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger

from .solution_model import Solution


class SolutionRegistry:
    """
    Registry for managing Solutions.
    
    Provides:
    - Solution registration
    - Solution resolution by ID
    - Solution listing
    - Solution activation/deactivation
    """
    
    def __init__(self):
        """Initialize solution registry."""
        self.solutions: Dict[str, Solution] = {}
        self.active_solutions: Dict[str, bool] = {}  # solution_id -> is_active
        self.logger = get_logger(self.__class__.__name__)
    
    def register_solution(self, solution: Solution) -> bool:
        """
        Register a solution.
        
        Args:
            solution: Solution to register
        
        Returns:
            True if registration successful
        """
        try:
            # Validate solution
            is_valid, error = solution.validate()
            if not is_valid:
                self.logger.error(f"Invalid solution: {error}")
                return False
            
            # Register solution
            self.solutions[solution.solution_id] = solution
            self.active_solutions[solution.solution_id] = False  # Inactive by default
            self.logger.info(f"Solution registered: {solution.solution_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register solution: {e}", exc_info=True)
            return False
    
    def get_solution(self, solution_id: str) -> Optional[Solution]:
        """
        Get solution by ID.
        
        Args:
            solution_id: Solution identifier
        
        Returns:
            Solution if found, None otherwise
        """
        return self.solutions.get(solution_id)
    
    def list_solutions(
        self,
        active_only: bool = False,
        domain: Optional[str] = None
    ) -> List[Solution]:
        """
        List solutions.
        
        Args:
            active_only: If True, only return active solutions
            domain: Optional domain filter
        
        Returns:
            List of solutions
        """
        solutions = list(self.solutions.values())
        
        # Filter by active status
        if active_only:
            solutions = [
                s for s in solutions
                if self.active_solutions.get(s.solution_id, False)
            ]
        
        # Filter by domain
        if domain:
            solutions = [
                s for s in solutions
                if any(binding.domain == domain for binding in s.domain_service_bindings)
            ]
        
        return solutions
    
    def activate_solution(self, solution_id: str) -> bool:
        """
        Activate a solution.
        
        Args:
            solution_id: Solution identifier
        
        Returns:
            True if activation successful
        """
        if solution_id not in self.solutions:
            self.logger.error(f"Solution not found: {solution_id}")
            return False
        
        # Validate solution before activation
        solution = self.solutions[solution_id]
        is_valid, error = solution.validate()
        if not is_valid:
            self.logger.error(f"Cannot activate invalid solution: {error}")
            return False
        
        self.active_solutions[solution_id] = True
        self.logger.info(f"Solution activated: {solution_id}")
        return True
    
    def deactivate_solution(self, solution_id: str) -> bool:
        """
        Deactivate a solution.
        
        Args:
            solution_id: Solution identifier
        
        Returns:
            True if deactivation successful
        """
        if solution_id not in self.solutions:
            self.logger.error(f"Solution not found: {solution_id}")
            return False
        
        self.active_solutions[solution_id] = False
        self.logger.info(f"Solution deactivated: {solution_id}")
        return True
    
    def is_solution_active(self, solution_id: str) -> bool:
        """
        Check if solution is active.
        
        Args:
            solution_id: Solution identifier
        
        Returns:
            True if solution is active
        """
        return self.active_solutions.get(solution_id, False)
    
    def unregister_solution(self, solution_id: str) -> bool:
        """
        Unregister a solution.
        
        Args:
            solution_id: Solution identifier
        
        Returns:
            True if unregistration successful
        """
        if solution_id not in self.solutions:
            self.logger.error(f"Solution not found: {solution_id}")
            return False
        
        # Deactivate before unregistering
        if self.active_solutions.get(solution_id, False):
            self.deactivate_solution(solution_id)
        
        del self.solutions[solution_id]
        del self.active_solutions[solution_id]
        self.logger.info(f"Solution unregistered: {solution_id}")
        return True
