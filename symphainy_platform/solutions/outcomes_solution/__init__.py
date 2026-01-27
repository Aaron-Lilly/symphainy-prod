"""
Outcomes Solution - Outcomes Realm Platform Solution

The platform Solution that composes Outcomes Realm journeys, exposes SOA APIs,
and wires up with the frontend via Experience SDK.

Key Components:
- OutcomesSolution: Main solution class
- Journey Orchestrators: Compose intent services into journeys
- OutcomesSolutionMCPServer: Exposes SOA APIs as MCP tools

Naming Convention:
- Realm: Outcomes Realm
- Solution: Platform construct (OutcomesSolution)
- Artifacts: outcome_* prefix (e.g., outcome_synthesis, outcome_roadmap)
"""

from .outcomes_solution import OutcomesSolution

__all__ = ["OutcomesSolution"]
