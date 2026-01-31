"""
Outcomes Capability Intent Services (Platform SDK Architecture)

These intent services use the PlatformIntentService base class
and receive PlatformContext (ctx) for execution.

Synthesis (AI-powered via ctx.reasoning):
    - SynthesizeOutcomeService: Outcome synthesis via OutcomesSynthesisAgent
    - GenerateRoadmapService: Roadmap generation via RoadmapGenerationAgent
    - CreatePOCService: POC creation via POCGenerationAgent
    - CreateBlueprintService: Blueprint creation via BlueprintCreationAgent

Export:
    - ExportArtifactService: Artifact export
    - CreateSolutionService: Solution creation
"""

from .synthesize_outcome_service import SynthesizeOutcomeService
from .generate_roadmap_service import GenerateRoadmapService
from .create_poc_service import CreatePOCService
from .create_blueprint_service import CreateBlueprintService
from .export_artifact_service import ExportArtifactService
from .create_solution_service import CreateSolutionService

__all__ = [
    "SynthesizeOutcomeService",
    "GenerateRoadmapService",
    "CreatePOCService",
    "CreateBlueprintService",
    "ExportArtifactService",
    "CreateSolutionService",
]
