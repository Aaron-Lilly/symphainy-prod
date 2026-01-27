"""
Solutions - Solution Layer for Platform

Solutions are the top-level organizational unit that compose journeys,
expose SOA APIs, and wire up with the frontend via Experience SDK.

WHAT (Solution Role): I compose journeys and expose capabilities
HOW (Solution Implementation): I coordinate journey orchestrators, expose SOA APIs and MCP tools

Key Principle: The platform runs Solutions; Solutions run systems.
Solutions bind domain services to external systems.

Available Solutions:
- ContentSolution: File upload, parsing, embedding, management
- InsightsSolution: Business analysis, data quality, semantic discovery
- JourneySolution: Workflow/SOP management, coexistence analysis
- OutcomesSolution: POC creation, roadmap generation, solution synthesis
"""

from .content_solution import ContentSolution
from .insights_solution import InsightsSolution
from .journey_solution import JourneySolution
from .outcomes_solution import OutcomesSolution

__all__ = [
    "ContentSolution",
    "InsightsSolution",
    "JourneySolution",
    "OutcomesSolution"
]
