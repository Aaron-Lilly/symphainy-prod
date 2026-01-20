"""
Unit tests for Curator Primitives - Promotion Validation.

Tests the policy decision logic for promoting Purpose-Bound Outcomes to Platform DNA.
"""

import pytest
from symphainy_platform.civic_systems.smart_city.primitives.curator_primitives import (
    CuratorPrimitives,
    PromotionValidation
)


@pytest.mark.unit
@pytest.mark.civic_systems
class TestCuratorPrimitivesPromotion:
    """Test Curator Primitives promotion validation."""
    
    @pytest.fixture
    def curator_primitives(self):
        """Create CuratorPrimitives instance."""
        return CuratorPrimitives()
    
    @pytest.mark.asyncio
    async def test_validate_promotion_solution_allowed(self, curator_primitives):
        """Test that blueprint can be promoted to solution registry."""
        result = await curator_primitives.validate_promotion(
            artifact_type="blueprint",
            registry_type="solution",
            lifecycle_state="accepted"
        )
        
        assert result.is_allowed is True
        assert result.registry_type == "solution"
        assert result.policy_basis == "mvp_permissive_policy"
    
    @pytest.mark.asyncio
    async def test_validate_promotion_intent_allowed(self, curator_primitives):
        """Test that workflow can be promoted to intent registry."""
        result = await curator_primitives.validate_promotion(
            artifact_type="workflow",
            registry_type="intent",
            lifecycle_state="accepted"
        )
        
        assert result.is_allowed is True
        assert result.registry_type == "intent"
    
    @pytest.mark.asyncio
    async def test_validate_promotion_realm_allowed(self, curator_primitives):
        """Test that journey can be promoted to realm registry."""
        result = await curator_primitives.validate_promotion(
            artifact_type="journey",
            registry_type="realm",
            lifecycle_state="accepted"
        )
        
        assert result.is_allowed is True
        assert result.registry_type == "realm"
    
    @pytest.mark.asyncio
    async def test_validate_promotion_fails_draft_state(self, curator_primitives):
        """Test that promotion fails if artifact is not in 'accepted' state."""
        result = await curator_primitives.validate_promotion(
            artifact_type="blueprint",
            registry_type="solution",
            lifecycle_state="draft"  # Not accepted
        )
        
        assert result.is_allowed is False
        assert "accepted" in result.reason
        assert result.policy_basis == "lifecycle_state_policy"
    
    @pytest.mark.asyncio
    async def test_validate_promotion_fails_wrong_type(self, curator_primitives):
        """Test that promotion fails if artifact type doesn't match registry type."""
        result = await curator_primitives.validate_promotion(
            artifact_type="sop",  # Cannot be promoted to solution
            registry_type="solution",
            lifecycle_state="accepted"
        )
        
        assert result.is_allowed is False
        assert "cannot be promoted" in result.reason
        assert result.policy_basis == "artifact_type_policy"
    
    @pytest.mark.asyncio
    async def test_validate_promotion_fails_invalid_registry_type(self, curator_primitives):
        """Test that promotion fails for invalid registry type."""
        result = await curator_primitives.validate_promotion(
            artifact_type="blueprint",
            registry_type="invalid_type",
            lifecycle_state="accepted"
        )
        
        assert result.is_allowed is False
        assert "Invalid registry_type" in result.reason
        assert result.policy_basis == "invalid_registry_type"
    
    @pytest.mark.asyncio
    async def test_validate_promotion_allows_none_lifecycle_state(self, curator_primitives):
        """Test that promotion allows None lifecycle_state (for backward compatibility)."""
        result = await curator_primitives.validate_promotion(
            artifact_type="blueprint",
            registry_type="solution",
            lifecycle_state=None  # None is allowed (will be checked by service)
        )
        
        assert result.is_allowed is True
    
    @pytest.mark.asyncio
    async def test_validate_promotion_type_mapping(self, curator_primitives):
        """Test that all type mappings work correctly."""
        test_cases = [
            ("blueprint", "solution", True),
            ("solution", "solution", True),
            ("workflow", "intent", True),
            ("intent", "intent", True),
            ("journey", "realm", True),
            ("realm", "realm", True),
            ("blueprint", "intent", False),  # Wrong registry
            ("workflow", "solution", False),  # Wrong registry
        ]
        
        for artifact_type, registry_type, should_allow in test_cases:
            result = await curator_primitives.validate_promotion(
                artifact_type=artifact_type,
                registry_type=registry_type,
                lifecycle_state="accepted"
            )
            
            assert result.is_allowed == should_allow, \
                f"Failed for {artifact_type} -> {registry_type}: expected {should_allow}, got {result.is_allowed}"
