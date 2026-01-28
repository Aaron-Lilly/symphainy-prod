"""
Test Solution Model Validation

Comprehensive validation tests for Solution model and related components.
These tests ensure Solution model is used correctly and catches misuse.

Tests:
- Solution model validation
- SolutionContext validation
- DomainServiceBinding validation
- SyncStrategy validation
- Edge cases and error scenarios
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestSolutionContextValidation:
    """Test SolutionContext validation."""
    
    def test_solution_context_creation_with_defaults(self):
        """SolutionContext should have sensible defaults."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import SolutionContext
        
        context = SolutionContext()
        
        assert context.goals == []
        assert context.constraints == []
        assert context.risk == "Low"
        assert context.metadata == {}
    
    def test_solution_context_creation_with_values(self):
        """SolutionContext should accept custom values."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import SolutionContext
        
        context = SolutionContext(
            goals=["Goal 1", "Goal 2"],
            constraints=["Constraint 1"],
            risk="Medium",
            metadata={"key": "value"}
        )
        
        assert context.goals == ["Goal 1", "Goal 2"]
        assert context.constraints == ["Constraint 1"]
        assert context.risk == "Medium"
        assert context.metadata == {"key": "value"}
    
    def test_solution_context_to_dict(self):
        """SolutionContext.to_dict() should return correct structure."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import SolutionContext
        
        context = SolutionContext(
            goals=["Goal 1"],
            constraints=["Constraint 1"],
            risk="High",
            metadata={"key": "value"}
        )
        
        result = context.to_dict()
        
        assert result["goals"] == ["Goal 1"]
        assert result["constraints"] == ["Constraint 1"]
        assert result["risk"] == "High"
        assert result["metadata"] == {"key": "value"}
    
    def test_solution_context_from_dict(self):
        """SolutionContext.from_dict() should create correct instance."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import SolutionContext
        
        data = {
            "goals": ["Goal 1"],
            "constraints": ["Constraint 1"],
            "risk": "Medium",
            "metadata": {"key": "value"}
        }
        
        context = SolutionContext.from_dict(data)
        
        assert context.goals == ["Goal 1"]
        assert context.constraints == ["Constraint 1"]
        assert context.risk == "Medium"
        assert context.metadata == {"key": "value"}


class TestSolutionValidation:
    """Test Solution model validation."""
    
    def test_solution_validate_requires_solution_id(self):
        """Solution.validate() should require solution_id."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        solution_context = SolutionContext()
        
        # Empty solution_id should fail
        solution = Solution(
            solution_id="",
            solution_context=solution_context
        )
        
        is_valid, error = solution.validate()
        assert is_valid is False
        assert "solution_id" in error.lower()
    
    def test_solution_validate_requires_solution_context(self):
        """Solution.validate() should require solution_context."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import Solution
        
        # This should fail at creation (required field)
        with pytest.raises(TypeError):
            Solution(solution_id="test")  # Missing solution_context
    
    def test_solution_validate_returns_tuple(self):
        """Solution.validate() should return (bool, Optional[str])."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        solution_context = SolutionContext()
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context
        )
        
        result = solution.validate()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert result[1] is None or isinstance(result[1], str)
    
    def test_solution_validate_valid_solution(self):
        """Valid solution should pass validation."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        solution_context = SolutionContext(goals=["Test goal"])
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            supported_intents=["test_intent"]
        )
        
        is_valid, error = solution.validate()
        assert is_valid is True
        assert error is None


class TestDomainServiceBindingValidation:
    """Test DomainServiceBinding validation."""
    
    def test_domain_service_binding_requires_domain(self):
        """DomainServiceBinding should require domain."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext, DomainServiceBinding
        )
        
        solution_context = SolutionContext()
        
        # Create solution with invalid binding (empty domain)
        invalid_binding = DomainServiceBinding(
            domain="",  # Empty - invalid
            system_name="test_system",
            adapter_type="rest"
        )
        
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            domain_service_bindings=[invalid_binding]
        )
        
        is_valid, error = solution.validate()
        assert is_valid is False
        assert "domain" in error.lower()
    
    def test_domain_service_binding_requires_system_name(self):
        """DomainServiceBinding should require system_name."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext, DomainServiceBinding
        )
        
        solution_context = SolutionContext()
        
        invalid_binding = DomainServiceBinding(
            domain="content",
            system_name="",  # Empty - invalid
            adapter_type="rest"
        )
        
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            domain_service_bindings=[invalid_binding]
        )
        
        is_valid, error = solution.validate()
        assert is_valid is False
        assert "system_name" in error.lower()
    
    def test_domain_service_binding_requires_adapter_type(self):
        """DomainServiceBinding should require adapter_type."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext, DomainServiceBinding
        )
        
        solution_context = SolutionContext()
        
        invalid_binding = DomainServiceBinding(
            domain="content",
            system_name="test_system",
            adapter_type=""  # Empty - invalid
        )
        
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            domain_service_bindings=[invalid_binding]
        )
        
        is_valid, error = solution.validate()
        assert is_valid is False
        assert "adapter_type" in error.lower()
    
    def test_domain_service_binding_valid(self):
        """Valid DomainServiceBinding should pass validation."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext, DomainServiceBinding
        )
        
        solution_context = SolutionContext()
        
        valid_binding = DomainServiceBinding(
            domain="content",
            system_name="test_system",
            adapter_type="rest"
        )
        
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            domain_service_bindings=[valid_binding]
        )
        
        is_valid, error = solution.validate()
        assert is_valid is True


class TestSyncStrategyValidation:
    """Test SyncStrategy validation."""
    
    def test_sync_strategy_requires_strategy_type(self):
        """SyncStrategy should require strategy_type."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext, SyncStrategy
        )
        
        solution_context = SolutionContext()
        
        invalid_strategy = SyncStrategy(
            strategy_type="",  # Empty - invalid
            conflict_resolution="last_write_wins"
        )
        
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            sync_strategies=[invalid_strategy]
        )
        
        is_valid, error = solution.validate()
        assert is_valid is False
        assert "strategy_type" in error.lower()
    
    def test_sync_strategy_requires_conflict_resolution(self):
        """SyncStrategy should require conflict_resolution."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext, SyncStrategy
        )
        
        solution_context = SolutionContext()
        
        invalid_strategy = SyncStrategy(
            strategy_type="bi_directional",
            conflict_resolution=""  # Empty - invalid
        )
        
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            sync_strategies=[invalid_strategy]
        )
        
        is_valid, error = solution.validate()
        assert is_valid is False
        assert "conflict_resolution" in error.lower()


class TestSolutionEdgeCases:
    """Test Solution model edge cases."""
    
    def test_solution_with_empty_supported_intents(self):
        """Solution should handle empty supported_intents."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        solution_context = SolutionContext()
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            supported_intents=[]  # Empty list
        )
        
        is_valid, error = solution.validate()
        assert is_valid is True  # Empty intents are valid
    
    def test_solution_with_empty_metadata(self):
        """Solution should handle empty metadata."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        solution_context = SolutionContext(metadata={})
        solution = Solution(
            solution_id="test_solution",
            solution_context=solution_context
        )
        
        is_valid, error = solution.validate()
        assert is_valid is True
    
    def test_solution_to_dict_and_from_dict(self):
        """Solution should serialize and deserialize correctly."""
        from symphainy_platform.civic_systems.platform_sdk.solution_model import (
            Solution, SolutionContext
        )
        
        solution_context = SolutionContext(
            goals=["Goal 1"],
            metadata={"name": "Test Solution"}
        )
        
        original = Solution(
            solution_id="test_solution",
            solution_context=solution_context,
            supported_intents=["intent1", "intent2"]
        )
        
        # Serialize
        data = original.to_dict()
        
        # Deserialize
        restored = Solution.from_dict(data)
        
        assert restored.solution_id == original.solution_id
        assert restored.solution_context.goals == original.solution_context.goals
        assert restored.supported_intents == original.supported_intents
