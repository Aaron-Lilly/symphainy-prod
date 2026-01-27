"""
Outcomes Realm - Outcomes Synthesis and Strategic Deliverables

The Outcomes Realm is responsible for synthesizing business outcomes from all other realms
(Content, Insights, Journey) into actionable deliverables: roadmaps, POCs, blueprints, and
platform solutions.

WHAT (Realm Role): I synthesize outcomes and create strategic deliverables
HOW (Realm Implementation): I provide intent services that compose pillar outputs into outcomes

Key Principles:
- Intent services are pure services (agents handled at orchestrator layer)
- All services use Public Works abstractions (no direct infrastructure)
- Artifacts stored in Artifact Plane (not execution state)
- Services exposed as SOA APIs by orchestrator, wrapped as MCP Tools for agents

Naming Convention:
- Realm name: Outcomes Realm
- Artifact prefix: outcome_* (e.g., outcome_synthesis, outcome_roadmap)
- Solution = platform construct that composes journeys (OutcomesSolution)
"""

from .intent_services import (
    SynthesizeOutcomeService,
    GenerateRoadmapService,
    CreatePOCService,
    CreateBlueprintService,
    CreateSolutionService,
    ExportArtifactService
)

__all__ = [
    "SynthesizeOutcomeService",
    "GenerateRoadmapService",
    "CreatePOCService",
    "CreateBlueprintService",
    "CreateSolutionService",
    "ExportArtifactService"
]
