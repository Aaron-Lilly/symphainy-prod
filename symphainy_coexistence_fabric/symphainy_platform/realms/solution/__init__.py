"""
Solution Realm - Outcomes Synthesis and Strategic Deliverables

The Solution Realm is responsible for synthesizing business outcomes from all other realms
(Content, Insights, Journey) into actionable deliverables: roadmaps, POCs, blueprints, and
platform solutions.

WHAT (Realm Role): I synthesize outcomes and create strategic deliverables
HOW (Realm Implementation): I provide intent services that compose pillar outputs into solutions

Key Principles:
- Intent services are pure services (agents handled at orchestrator layer)
- All services use Public Works abstractions (no direct infrastructure)
- Artifacts stored in Artifact Plane (not execution state)
- Services exposed as SOA APIs by orchestrator, wrapped as MCP Tools for agents
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
