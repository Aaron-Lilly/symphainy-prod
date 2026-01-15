"""
Experience Plane - User Interaction Layer

Experience translates external interaction into intent.

WHAT (Experience Role): I translate user actions into intents
HOW (Experience Implementation): I expose REST, WebSockets, and coordinate with Runtime

Key Principle: Experience never:
- Calls domain services directly
- Manages workflows
- Owns state

Experience only:
- Authenticates callers
- Establishes sessions via Runtime
- Translates user actions into intents
- Streams execution updates back
"""

from .experience_service import ExperienceService

__all__ = ["ExperienceService"]
