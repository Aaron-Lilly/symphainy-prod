"""
Outcomes Enabling Services - DEPRECATED

All outcomes enabling services have been moved or replaced:
- POCGenerationService: Replaced by CreatePOCService intent service
- RoadmapGenerationService: Replaced by GenerateRoadmapService intent service
- SolutionSynthesisService: Replaced by CreateSolutionService intent service
- ReportGeneratorService -> foundations/libraries/reporting/
- ExportService -> foundations/libraries/export/
- VisualGenerationService -> foundations/libraries/visualization/outcome_visual_service.py

Import from foundations.libraries instead:
  from symphainy_platform.foundations.libraries.reporting import ReportGeneratorService
  from symphainy_platform.foundations.libraries.export import ExportService
  from symphainy_platform.foundations.libraries.visualization import VisualGenerationService
"""

# This directory is kept for backward compatibility but should not be used.
# All services have been moved to their canonical locations.

__all__ = []
