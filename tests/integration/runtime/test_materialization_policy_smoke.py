"""
Smoke Tests for Materialization Policy

Lightweight tests to verify Materialization Policy infrastructure works correctly.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from symphainy_platform.runtime.policies.materialization_policy_abstraction import (
    MaterializationPolicyAbstraction,
    DEFAULT_POLICY,
    MVP_POLICY_OVERRIDE
)
from symphainy_platform.runtime.policies.materialization_policy_protocol import (
    MaterializationDecision
)


class TestMaterializationPolicySmoke:
    """Smoke tests for Materialization Policy."""
    
    @pytest.mark.asyncio
    async def test_default_policy_ephemeral(self):
        """Test that default policy makes artifacts ephemeral."""
        policy = MaterializationPolicyAbstraction()
        
        # Mock intent and context
        intent = Mock()
        context = Mock()
        
        # Test workflow (should be DISCARD by default)
        decision = await policy.evaluate_policy(
            result_type="workflow",
            semantic_payload={},
            renderings={},
            intent=intent,
            context=context
        )
        
        assert decision == MaterializationDecision.DISCARD, "Default policy should make workflows ephemeral"
    
    @pytest.mark.asyncio
    async def test_default_policy_platform_native_persist(self):
        """Test that platform-native records are persisted by default."""
        policy = MaterializationPolicyAbstraction()
        
        # Mock intent and context
        intent = Mock()
        context = Mock()
        
        # Test intent (should be PERSIST by default - platform-native)
        decision = await policy.evaluate_policy(
            result_type="intent",
            semantic_payload={},
            renderings={},
            intent=intent,
            context=context
        )
        
        assert decision == MaterializationDecision.PERSIST, "Platform-native records should be persisted"
    
    @pytest.mark.asyncio
    async def test_mvp_override_persist(self):
        """Test that MVP override makes artifacts persist."""
        policy = MaterializationPolicyAbstraction(
            solution_config={"materialization_policy": MVP_POLICY_OVERRIDE}
        )
        
        # Mock intent and context
        intent = Mock()
        context = Mock()
        
        # Test workflow (should be PERSIST with MVP override)
        decision = await policy.evaluate_policy(
            result_type="workflow",
            semantic_payload={},
            renderings={},
            intent=intent,
            context=context
        )
        
        assert decision == MaterializationDecision.PERSIST, "MVP override should make workflows persist"
    
    @pytest.mark.asyncio
    async def test_solution_config_override(self):
        """Test that solution config overrides default policy."""
        custom_policy = {
            "workflow": "persist",
            "sop": "cache",
            "blueprint": "discard"
        }
        
        policy = MaterializationPolicyAbstraction(
            solution_config={"materialization_policy": custom_policy}
        )
        
        # Mock intent and context
        intent = Mock()
        context = Mock()
        
        # Test workflow (should be PERSIST from custom policy)
        decision = await policy.evaluate_policy(
            result_type="workflow",
            semantic_payload={},
            renderings={},
            intent=intent,
            context=context
        )
        assert decision == MaterializationDecision.PERSIST
        
        # Test sop (should be CACHE from custom policy)
        decision = await policy.evaluate_policy(
            result_type="sop",
            semantic_payload={},
            renderings={},
            intent=intent,
            context=context
        )
        assert decision == MaterializationDecision.CACHE
        
        # Test blueprint (should be DISCARD from custom policy)
        decision = await policy.evaluate_policy(
            result_type="blueprint",
            semantic_payload={},
            renderings={},
            intent=intent,
            context=context
        )
        assert decision == MaterializationDecision.DISCARD
    
    @pytest.mark.asyncio
    async def test_unknown_result_type_defaults_to_discard(self):
        """Test that unknown result types default to DISCARD."""
        policy = MaterializationPolicyAbstraction()
        
        # Mock intent and context
        intent = Mock()
        context = Mock()
        
        # Test unknown type
        decision = await policy.evaluate_policy(
            result_type="unknown_artifact_type",
            semantic_payload={},
            renderings={},
            intent=intent,
            context=context
        )
        
        assert decision == MaterializationDecision.DISCARD, "Unknown types should default to DISCARD"
    
    @pytest.mark.asyncio
    async def test_get_default_policy(self):
        """Test that get_default_policy returns correct policy."""
        policy = MaterializationPolicyAbstraction()
        default_policy = policy.get_default_policy()
        
        assert isinstance(default_policy, dict), "Default policy should be a dict"
        assert "workflow" in default_policy, "Default policy should include workflow"
        assert default_policy["workflow"] == "discard", "Default policy should make workflow ephemeral"
        assert default_policy["intent"] == "persist", "Default policy should persist intent"
    
    def test_default_policy_structure(self):
        """Test that DEFAULT_POLICY has correct structure."""
        assert isinstance(DEFAULT_POLICY, dict), "DEFAULT_POLICY should be a dict"
        assert "intent" in DEFAULT_POLICY, "DEFAULT_POLICY should include intent"
        assert "workflow" in DEFAULT_POLICY, "DEFAULT_POLICY should include workflow"
        assert DEFAULT_POLICY["intent"] == "persist", "Intent should be persisted"
        assert DEFAULT_POLICY["workflow"] == "discard", "Workflow should be ephemeral by default"
    
    def test_mvp_policy_override_structure(self):
        """Test that MVP_POLICY_OVERRIDE has correct structure."""
        assert isinstance(MVP_POLICY_OVERRIDE, dict), "MVP_POLICY_OVERRIDE should be a dict"
        assert "workflow" in MVP_POLICY_OVERRIDE, "MVP_POLICY_OVERRIDE should include workflow"
        assert MVP_POLICY_OVERRIDE["workflow"] == "persist", "MVP should persist workflows"
        assert MVP_POLICY_OVERRIDE["sop"] == "persist", "MVP should persist SOPs"
    
    @pytest.mark.asyncio
    async def test_policy_evaluation_with_semantic_payload(self):
        """Test that policy evaluation works with semantic payload."""
        policy = MaterializationPolicyAbstraction(
            solution_config={"materialization_policy": MVP_POLICY_OVERRIDE}
        )
        
        # Mock intent and context
        intent = Mock()
        context = Mock()
        
        # Test with semantic payload
        semantic_payload = {
            "workflow_id": "wf_123",
            "steps": ["step1", "step2"]
        }
        renderings = {
            "workflow": {"name": "Test Workflow"},
            "workflow_visual": {"image_base64": "..."}
        }
        
        decision = await policy.evaluate_policy(
            result_type="workflow",
            semantic_payload=semantic_payload,
            renderings=renderings,
            intent=intent,
            context=context
        )
        
        assert decision == MaterializationDecision.PERSIST, "Should persist with MVP override"
    
    @pytest.mark.asyncio
    async def test_policy_priority_solution_config_overrides_default(self):
        """Test that solution config has higher priority than default policy."""
        # Create policy with solution config that overrides default
        custom_policy = {
            "workflow": "persist"  # Override default (which is discard)
        }
        
        policy = MaterializationPolicyAbstraction(
            solution_config={"materialization_policy": custom_policy}
        )
        
        # Mock intent and context
        intent = Mock()
        context = Mock()
        
        # Should use solution config (persist), not default (discard)
        decision = await policy.evaluate_policy(
            result_type="workflow",
            semantic_payload={},
            renderings={},
            intent=intent,
            context=context
        )
        
        assert decision == MaterializationDecision.PERSIST, "Solution config should override default"
