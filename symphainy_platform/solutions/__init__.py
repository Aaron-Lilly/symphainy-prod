"""
Solutions - Solution Layer for Platform

Solutions are the top-level organizational unit that compose journeys,
expose SOA APIs, and wire up with the frontend via Experience SDK.

WHAT (Solution Role): I compose journeys and expose capabilities
HOW (Solution Implementation): I coordinate journey orchestrators, expose SOA APIs and MCP tools

Key Principle: The platform runs Solutions; Solutions run systems.
Solutions bind domain services to external systems.

Available Solutions:
- ContentSolution: Content Realm capabilities (file upload, parsing, embedding)
- InsightsSolution: Insights Realm capabilities (quality, analysis, interpretation, lineage)
- OutcomesSolution: Outcomes Realm capabilities (synthesis, roadmaps, POCs, blueprints)
"""

from .content_solution import ContentSolution
from .insights_solution import InsightsSolution
from .outcomes_solution import OutcomesSolution

__all__ = ["ContentSolution", "InsightsSolution", "OutcomesSolution"]
