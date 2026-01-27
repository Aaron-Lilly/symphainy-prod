"""
Realms Package - Domain Services for SymphAIny Platform

Realms contain domain-specific services organized by business capability:
- Content Realm: File ingestion, parsing, and content management
- Insights Realm: Analysis, extraction, and intelligence generation
- Operations Realm: Workflow/SOP management, coexistence analysis
- Outcomes Realm: Outcomes synthesis, roadmaps, POCs, blueprints, and strategic deliverables

Naming Conventions:
- "Realm" = domain area (user-facing business capability)
- "Solution" = platform construct (composes journeys, exposes SOA APIs)
- "Journey" = platform capability (invisible to users, orchestration mechanism)
"""

from .outcomes import (
    SynthesizeOutcomeService,
    GenerateRoadmapService,
    CreatePOCService,
    CreateBlueprintService,
    CreateSolutionService,
    ExportArtifactService
)

from .insights import (
    AssessDataQualityService,
    InterpretDataSelfDiscoveryService,
    InterpretDataGuidedService,
    AnalyzeStructuredDataService,
    AnalyzeUnstructuredDataService,
    VisualizeLineageService,
    MapRelationshipsService
)

from .operations import (
    OptimizeProcessService,
    GenerateSOPService,
    CreateWorkflowService,
    AnalyzeCoexistenceService,
    GenerateSOPFromChatService,
    SOPChatMessageService
)

__all__ = [
    # Outcomes Realm
    "SynthesizeOutcomeService",
    "GenerateRoadmapService",
    "CreatePOCService",
    "CreateBlueprintService",
    "CreateSolutionService",
    "ExportArtifactService",
    # Insights Realm
    "AssessDataQualityService",
    "InterpretDataSelfDiscoveryService",
    "InterpretDataGuidedService",
    "AnalyzeStructuredDataService",
    "AnalyzeUnstructuredDataService",
    "VisualizeLineageService",
    "MapRelationshipsService",
    # Operations Realm
    "OptimizeProcessService",
    "GenerateSOPService",
    "CreateWorkflowService",
    "AnalyzeCoexistenceService",
    "GenerateSOPFromChatService",
    "SOPChatMessageService"
]
