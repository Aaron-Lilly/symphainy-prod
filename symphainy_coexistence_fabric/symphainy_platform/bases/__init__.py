"""
Base Classes for SymphAIny Platform

Base classes for solutions, orchestrators, intent services, and other components.

Location: symphainy_platform/bases/

Exports:
- BaseSolution: Base class for platform solutions
- BaseOrchestrator: Base class for journey orchestrators
- BaseIntentService: Base class for intent services
"""

__version__ = "1.0.0"

from .solution_base import BaseSolution
from .orchestrator_base import BaseOrchestrator
from .intent_service_base import BaseIntentService

__all__ = [
    "BaseSolution",
    "BaseOrchestrator",
    "BaseIntentService",
]
