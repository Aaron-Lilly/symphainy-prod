"""
Outcomes Realm Intent Services

Intent services for the Outcomes Realm. Each service implements a single intent type
following the BaseIntentService pattern.

Architecture:
- Intent services are pure services (agents handled at orchestrator layer)
- All services use Public Works abstractions (no direct infrastructure)
- Artifacts stored in Artifact Plane (not execution state)
- Services are exposed as SOA APIs by orchestrator, wrapped as MCP Tools for agents

Services:
- SynthesizeOutcomeService: Synthesize outcomes from all pillars
- GenerateRoadmapService: Generate strategic roadmap from goals
- CreatePOCService: Create POC proposal from description
- CreateBlueprintService: Create coexistence blueprint from workflow
- CreateSolutionService: Create platform solution from artifact
- ExportArtifactService: Export artifact in various formats

Naming Convention:
- Realm name: Outcomes Realm
- Artifact prefix: outcome_* (e.g., outcome_synthesis, outcome_roadmap)
- Solution = platform construct that composes journeys (OutcomesSolution)
"""

from .synthesize_outcome_service import SynthesizeOutcomeService
from .generate_roadmap_service import GenerateRoadmapService
from .create_poc_service import CreatePOCService
from .create_blueprint_service import CreateBlueprintService
from .create_solution_service import CreateSolutionService
from .export_artifact_service import ExportArtifactService

__all__ = [
    "SynthesizeOutcomeService",
    "GenerateRoadmapService",
    "CreatePOCService",
    "CreateBlueprintService",
    "CreateSolutionService",
    "ExportArtifactService"
]
