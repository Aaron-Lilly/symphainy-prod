"""
Runtime Policies Module

NOTE: Materialization policy has been moved to Smart City Primitives.
This module is kept for backward compatibility but is deprecated.
"""

# Materialization policy moved to Smart City Primitives
# Import from new location for backward compatibility
from symphainy_platform.civic_systems.smart_city.primitives.materialization_policy_primitives import (
    MaterializationDecision,
    MaterializationPolicyStore,
    MaterializationPolicyPrimitives,
    DEFAULT_POLICY
)

__all__ = [
    "MaterializationDecision",
    "MaterializationPolicyStore",
    "MaterializationPolicyPrimitives",
    "DEFAULT_POLICY",
]
