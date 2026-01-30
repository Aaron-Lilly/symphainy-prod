"""
Experience Surfaces - How Users TOUCH the Platform

This namespace contains platform-native experience compositions built on the Experience SDK.
Experience surfaces are clients of the runtime — they attach via the SDK, they do not
bootstrap the runtime.

Hard invariant: Experience surfaces must not directly access runtime internals,
civic systems, or infrastructure. All access flows through the Experience SDK.

See: docs/architecture/CANONICAL_PLATFORM_ARCHITECTURE.md
"""

__all__ = [
    "content",
    "coexistence",
    "operations",
    "outcomes",
    "control_tower",
    "security",
]
