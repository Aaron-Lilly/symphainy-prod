"""
Solutions - Solution Layer for Platform

Solutions are the top-level organizational unit that compose journeys,
expose SOA APIs, and wire up with the frontend via Experience SDK.

WHAT (Solution Role): I compose journeys and expose capabilities
HOW (Solution Implementation): I coordinate journey orchestrators, expose SOA APIs and MCP tools

Key Principle: The platform runs Solutions; Solutions run systems.
Solutions bind domain services to external systems.

Available Solutions:
- CoexistenceSolution: Platform entry point (introduction, navigation, guide agent)
- ContentSolution: File upload, parsing, embedding, management
- InsightsSolution: Business analysis, data quality, semantic discovery
- JourneySolution: Workflow/SOP management, coexistence analysis
- OutcomesSolution: POC creation, roadmap generation, solution synthesis
- ControlTower: Platform command center (monitoring, management, composition)
"""

from .coexistence import CoexistenceSolution
from .content_solution import ContentSolution
from .insights_solution import InsightsSolution
from .journey_solution import JourneySolution
from .outcomes_solution import OutcomesSolution
from .control_tower import ControlTower

__all__ = [
    "CoexistenceSolution",
    "ContentSolution",
    "InsightsSolution",
    "JourneySolution",
    "OutcomesSolution",
    "ControlTower"
]
