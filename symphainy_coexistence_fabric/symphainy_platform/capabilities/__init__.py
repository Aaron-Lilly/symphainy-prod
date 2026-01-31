"""
Capabilities - What the Platform CAN DO

This namespace contains the Execution Plane implementations of platform capabilities.
Capabilities are governed primitives that implement platform functionality.

Capabilities may access Public Works, State Surface, and foundations directly
(they are below the SDK boundary).

Experience surfaces (Solutions Plane) consume capabilities via the Experience SDK;
they do not access capabilities directly.

See: docs/architecture/CANONICAL_PLATFORM_ARCHITECTURE.md
"""

__all__ = [
    "content",
    "coexistence",
    "insights",
    "journey_engine",
    "solution_synthesis",
    "security",
    "control_tower",
]
