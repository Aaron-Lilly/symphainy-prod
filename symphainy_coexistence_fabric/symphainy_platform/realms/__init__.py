"""
Realms Package - Domain Services for SymphAIny Platform

Realms contain domain-specific services organized by business capability.

CORRECT PATTERN (Security Realm model):
- Realms contain ONLY intent_services/
- No orchestrators/ (Runtime handles orchestration via Sagas)
- No mcp_server/ (MCP Servers belong to Solutions)
- No agents/ (Agents belong in civic_systems/agentic/agents/)

User-Facing Domains (Realms):
- Content Realm: File ingestion, parsing, and content management
- Insights Realm: Analysis, extraction, and intelligence generation
- Operations Realm: Workflow/SOP management, coexistence analysis
- Outcomes Realm: Outcomes synthesis, roadmaps, POCs, blueprints
- Security Realm: Authentication, authorization, session management (foundational)
- Control Tower Realm: Platform administration, monitoring, developer docs
- Coexistence Realm: Platform entry, navigation, agent interactions

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

from .security import (
    AuthenticateUserService,
    CreateUserAccountService,
    CreateSessionService,
    ValidateAuthorizationService,
    TerminateSessionService,
    CheckEmailAvailabilityService,
    ValidateTokenService
)

from .control_tower import (
    GetPlatformStatisticsService,
    GetSystemHealthService,
    GetRealmHealthService,
    ListSolutionsService,
    GetSolutionStatusService,
    GetPatternsService,
    GetCodeExamplesService,
    GetDocumentationService,
    ValidateSolutionService
)

from .coexistence import (
    IntroducePlatformService,
    ShowSolutionCatalogService,
    NavigateToSolutionService,
    InitiateGuideAgentService,
    ProcessGuideAgentMessageService,
    RouteToLiaisonAgentService,
    ListAvailableMCPToolsService,
    CallOrchestratorMCPToolService
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
    "SOPChatMessageService",
    # Security Realm
    "AuthenticateUserService",
    "CreateUserAccountService",
    "CreateSessionService",
    "ValidateAuthorizationService",
    "TerminateSessionService",
    "CheckEmailAvailabilityService",
    "ValidateTokenService",
    # Control Tower Realm
    "GetPlatformStatisticsService",
    "GetSystemHealthService",
    "GetRealmHealthService",
    "ListSolutionsService",
    "GetSolutionStatusService",
    "GetPatternsService",
    "GetCodeExamplesService",
    "GetDocumentationService",
    "ValidateSolutionService",
    # Coexistence Realm
    "IntroducePlatformService",
    "ShowSolutionCatalogService",
    "NavigateToSolutionService",
    "InitiateGuideAgentService",
    "ProcessGuideAgentMessageService",
    "RouteToLiaisonAgentService",
    "ListAvailableMCPToolsService",
    "CallOrchestratorMCPToolService"
]
