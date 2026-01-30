"""
Control Tower Capability Intent Services (Platform SDK Architecture)

These intent services use the PlatformIntentService base class
and receive PlatformContext (ctx) for execution.

Platform Monitoring:
    - GetPlatformStatisticsService: Platform statistics
    - GetSystemHealthService: System health check
    - GetRealmHealthService: Realm health check

Solution Management:
    - ListSolutionsService: List available solutions
    - GetSolutionStatusService: Get solution status
    - ValidateSolutionService: Validate solution configuration

Developer Documentation:
    - GetPatternsService: Get platform patterns
    - GetCodeExamplesService: Get code examples
    - GetDocumentationService: Get documentation
"""

from .get_platform_statistics_service import GetPlatformStatisticsService
from .get_system_health_service import GetSystemHealthService
from .get_realm_health_service import GetRealmHealthService
from .list_solutions_service import ListSolutionsService
from .get_solution_status_service import GetSolutionStatusService
from .validate_solution_service import ValidateSolutionService
from .get_patterns_service import GetPatternsService
from .get_code_examples_service import GetCodeExamplesService
from .get_documentation_service import GetDocumentationService

__all__ = [
    "GetPlatformStatisticsService",
    "GetSystemHealthService",
    "GetRealmHealthService",
    "ListSolutionsService",
    "GetSolutionStatusService",
    "ValidateSolutionService",
    "GetPatternsService",
    "GetCodeExamplesService",
    "GetDocumentationService",
]
