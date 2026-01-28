"""
Test Solution Registry Integration

Tests that validate SolutionRegistry works correctly with Solution models.
These tests would have caught the solution registration bug we found.

Tests:
- Solution model creation and validation
- Solution registration success/failure
- Solution activation/deactivation
- Solution lifecycle state transitions
- Error handling in registration
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestSolutionModelCreation:
    """Test Solution model creation - validates the bug we found."""
    
    def test_solution_requires_solution_context(self):
        """Solution model should require solution_context (not name/description)."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        # This should work (correct way)
        solution_context = SolutionContext(
            goals=["Test goal"],
            constraints=[],
            risk="Low"
        )
        
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            supported_intents=["test_intent"]
        )
        
        assert solution.solution_id == "test_solution"
        assert solution.solution_context is not None
        assert solution.solution_context.goals == ["Test goal"]
    
    def test_solution_rejects_invalid_parameters(self):
        """Solution model should reject invalid parameters like 'name'."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        solution_context = SolutionContext()
        
        # This should fail - 'name' is not a valid parameter
        with pytest.raises(TypeError):
            Solution(
                solution_id="test_solution",
                solution_context=solution_context,
                name="Test Solution"  # ❌ Invalid parameter
            )
    
    def test_solution_context_can_store_metadata(self):
        """SolutionContext metadata can store name/description/version."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        solution_context = SolutionContext(
            goals=["Provide test capabilities"],
            metadata={
                "name": "Test Solution",
                "description": "A test solution",
                "version": "1.0.0",
                "owner": "platform"
            }
        )
        
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context
        )
        
        assert solution.solution_context.metadata["name"] == "Test Solution"
        assert solution.solution_context.metadata["description"] == "A test solution"
        assert solution.solution_context.metadata["version"] == "1.0.0"


class TestSolutionRegistration:
    """Test solution registration with SolutionRegistry."""
    
    def test_register_valid_solution_succeeds(self, mock_public_works, mock_state_surface):
        """Valid solution should register successfully."""
        from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        registry = SolutionRegistry()
        
        solution_context = SolutionContext(
            goals=["Test goal"],
            constraints=[],
            risk="Low"
        )
        
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            supported_intents=["test_intent"]
        )
        
        result = registry.register_solution(solution)
        assert result is True, "Solution registration should succeed"
        
        # Verify solution is in registry
        registered = registry.get_solution("test_solution")
        assert registered is not None, "Solution should be in registry"
        assert registered.solution_id == "test_solution"
    
    def test_register_invalid_solution_fails(self, mock_public_works, mock_state_surface):
        """Invalid solution should fail registration."""
        from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        registry = SolutionRegistry()
        
        # Create invalid solution (missing solution_id)
        solution_context = SolutionContext()
        
        # This should fail validation
        invalid_solution = Solution(
            solution_id="",  # Empty solution_id - invalid
            solution_context=solution_context
        )
        
        result = registry.register_solution(invalid_solution)
        assert result is False, "Invalid solution should fail registration"
        
        # Verify solution is NOT in registry
        registered = registry.get_solution("")
        assert registered is None, "Invalid solution should not be in registry"


class TestSolutionActivation:
    """Test solution activation and deactivation."""
    
    def test_activate_registered_solution_succeeds(self, mock_public_works, mock_state_surface):
        """Activating a registered solution should succeed."""
        from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        registry = SolutionRegistry()
        
        solution_context = SolutionContext(goals=["Test goal"])
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context
        )
        
        registry.register_solution(solution)
        
        # Initially inactive
        assert registry.is_solution_active("test_solution") is False
        
        # Activate
        result = registry.activate_solution("test_solution")
        assert result is True, "Activation should succeed"
        assert registry.is_solution_active("test_solution") is True
    
    def test_activate_unregistered_solution_fails(self, mock_public_works, mock_state_surface):
        """Activating an unregistered solution should fail."""
        from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
        
        registry = SolutionRegistry()
        
        result = registry.activate_solution("nonexistent_solution")
        assert result is False, "Activating unregistered solution should fail"
        assert registry.is_solution_active("nonexistent_solution") is False


class TestSolutionLifecycle:
    """Test solution lifecycle state transitions."""
    
    def test_solution_lifecycle_states(self, mock_public_works, mock_state_surface):
        """Solution should transition through correct states."""
        from symphainy_platform.civic_systems.platform_sdk.solution_registry import SolutionRegistry
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        registry = SolutionRegistry()
        
        solution_context = SolutionContext(goals=["Test goal"])
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context
        )
        
        # State 1: Not registered
        assert registry.get_solution("test_solution") is None
        assert registry.is_solution_active("test_solution") is False
        
        # State 2: Registered but inactive
        registry.register_solution(solution)
        assert registry.get_solution("test_solution") is not None
        assert registry.is_solution_active("test_solution") is False
        
        # State 3: Active
        registry.activate_solution("test_solution")
        assert registry.is_solution_active("test_solution") is True
        
        # State 4: Deactivated
        registry.deactivate_solution("test_solution")
        assert registry.is_solution_active("test_solution") is False
