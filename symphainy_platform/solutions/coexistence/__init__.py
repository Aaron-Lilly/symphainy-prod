"""
Coexistence Solution - Platform Entry Point & Navigation

The Coexistence Solution is the front door to the Symphainy Platform.
Previously known as "Landing Page", this solution handles:
- Platform Introduction: Welcome and onboarding
- Solution Navigation: Routing to appropriate solutions
- Guide Agent: AI-powered assistance and guidance

WHAT (Coexistence Role): I am the platform's front door and navigator
HOW (Coexistence Implementation): I compose introduction, navigation, and guide agent journeys

Key Concept: Coexistence means enabling existing systems to work together
with modern AI capabilities without requiring replacement.
"""

from .coexistence import CoexistenceSolution

__all__ = ["CoexistenceSolution"]
