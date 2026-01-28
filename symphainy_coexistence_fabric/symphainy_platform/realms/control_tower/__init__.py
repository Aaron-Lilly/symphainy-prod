"""
Control Tower Realm - Platform Administration Domain

Provides intent services for:
- Platform monitoring and health
- Solution management
- Developer documentation
- System metrics

User-Facing Domain: Control Tower (Admin Dashboard)
Pattern: Only intent_services/ - no orchestrators, agents, or MCP servers

Intent Services handle individual intents.
Journey Orchestrators (in Solutions) compose intents.
Runtime handles orchestration via Sagas.
"""

from .intent_services import (
    # Platform Monitoring
    GetPlatformStatisticsService,
    GetSystemHealthService,
    GetRealmHealthService,
    GetExecutionMetricsService,
    GetSolutionRegistryStatusService,
    # Solution Management
    ListSolutionsService,
    GetSolutionStatusService,
    ManageSolutionService,
    GetSolutionMetricsService,
    # Developer Docs
    GetPatternsService,
    GetCodeExamplesService,
    GetDocumentationService,
    # Solution Composition
    GetSolutionTemplatesService,
    ComposeSolutionService,
    ValidateSolutionService,
    GetCompositionGuideService,
)

__all__ = [
    # Platform Monitoring
    "GetPlatformStatisticsService",
    "GetSystemHealthService",
    "GetRealmHealthService",
    "GetExecutionMetricsService",
    "GetSolutionRegistryStatusService",
    # Solution Management
    "ListSolutionsService",
    "GetSolutionStatusService",
    "ManageSolutionService",
    "GetSolutionMetricsService",
    # Developer Docs
    "GetPatternsService",
    "GetCodeExamplesService",
    "GetDocumentationService",
    # Solution Composition
    "GetSolutionTemplatesService",
    "ComposeSolutionService",
    "ValidateSolutionService",
    "GetCompositionGuideService",
]
