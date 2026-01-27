"""
Solutions - Solution Layer for Platform

Solutions are the top-level organizational unit that compose journeys,
expose SOA APIs, and wire up with the frontend via Experience SDK.

WHAT (Solution Role): I compose journeys and expose capabilities
HOW (Solution Implementation): I coordinate journey orchestrators, expose SOA APIs and MCP tools

Key Principle: The platform runs Solutions; Solutions run systems.
Solutions bind domain services to external systems.

Naming Convention:
- Realm = user-facing domain (Content, Insights, Operations, Outcomes, Security)
- Solution = platform construct (composes journeys)
- Journey = platform capability (invisible to users)

Available Solutions:
- CoexistenceSolution: Platform entry point (introduction, navigation, guide agent)
- ContentSolution: Content Realm capabilities (file upload, parsing, embedding)
- InsightsSolution: Insights Realm capabilities (quality, analysis, interpretation, lineage)
- OperationsSolution: Operations Realm capabilities (workflows, SOPs, coexistence)
- OutcomesSolution: Outcomes Realm capabilities (synthesis, roadmaps, POCs, blueprints)
- SecuritySolution: Security Realm capabilities (auth, sessions, authorization) - FOUNDATIONAL
- ControlTower: Platform command center (monitoring, management, composition)
"""

from .coexistence import CoexistenceSolution
from .content_solution import ContentSolution
from .insights_solution import InsightsSolution
from .operations_solution import OperationsSolution
from .outcomes_solution import OutcomesSolution
from .security_solution import SecuritySolution
from .control_tower import ControlTower

__all__ = [
    "CoexistenceSolution",
    "ContentSolution",
    "InsightsSolution",
    "OperationsSolution",
    "OutcomesSolution",
    "SecuritySolution",
    "ControlTower"
]
