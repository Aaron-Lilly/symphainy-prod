"""
Smart City Primitives - Policy Decisions

Primitives provide policy decisions (used by Runtime only).

WHAT (Smart City Role): I provide policy validation and governance checks
HOW (Primitive Implementation): I provide pure functions, no side effects, deterministic

⚠️ CRITICAL: Primitives are used by Runtime only.
SDKs prepare execution contracts. Primitives validate them.
"""

from .security_guard_primitives import SecurityGuardPrimitives
from .traffic_cop_primitives import TrafficCopPrimitives
from .post_office_primitives import PostOfficePrimitives

__all__ = [
    "SecurityGuardPrimitives",
    "TrafficCopPrimitives",
    "PostOfficePrimitives",
]
