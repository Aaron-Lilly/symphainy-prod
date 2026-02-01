"""
Control Tower Capability Intent Services (Platform SDK Architecture)

These intent services use the PlatformIntentService base class
and receive PlatformContext (ctx) for execution.

Platform Monitoring:
    - GetPlatformStatisticsService: Platform statistics
    - GetSystemHealthService: System health check
    - GetRealmHealthService: Realm health check
    - GetExecutionMetricsService: Execution metrics

Solution Management:
    - ListSolutionsService: List available solutions
    - GetSolutionStatusService: Get solution status
    - ValidateSolutionService: Validate solution configuration
    - ComposeSolutionService: Create solution from template/config
    - GetSolutionTemplatesService: Get available solution templates

Developer Documentation:
    - GetPatternsService: Get platform patterns
    - GetCodeExamplesService: Get code examples
    - GetDocumentationService: Get documentation
"""

from .get_platform_statistics_service import GetPlatformStatisticsService
from .get_system_health_service import GetSystemHealthService
from .get_realm_health_service import GetRealmHealthService
from .get_execution_metrics_service import GetExecutionMetricsService
from .list_solutions_service import ListSolutionsService
from .get_solution_status_service import GetSolutionStatusService
from .validate_solution_service import ValidateSolutionService
from .compose_solution_service import ComposeSolutionService
from .get_solution_templates_service import GetSolutionTemplatesService
from .get_patterns_service import GetPatternsService
from .get_code_examples_service import GetCodeExamplesService
from .get_documentation_service import GetDocumentationService

__all__ = [
    "GetPlatformStatisticsService",
    "GetSystemHealthService",
    "GetRealmHealthService",
    "GetExecutionMetricsService",
    "ListSolutionsService",
    "GetSolutionStatusService",
    "ValidateSolutionService",
    "ComposeSolutionService",
    "GetSolutionTemplatesService",
    "GetPatternsService",
    "GetCodeExamplesService",
    "GetDocumentationService",
]
