"""
Pre-configured Agent Postures

Agent postures for common scenarios (Layer 2: Tenant/Solution Scoped).
"""

from .default_postures import (
    DEFAULT_POSTURE,
    CONSERVATIVE_POSTURE,
    EXPLORATORY_POSTURE,
    PRODUCTION_POSTURE
)

__all__ = [
    "DEFAULT_POSTURE",
    "CONSERVATIVE_POSTURE",
    "EXPLORATORY_POSTURE",
    "PRODUCTION_POSTURE"
]
