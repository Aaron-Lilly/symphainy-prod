"""
Insights Enabling Services - DEPRECATED

All Insights enabling services have been replaced by Intent Services:

- DataAnalyzerService: Use AnalyzeStructuredDataService or AnalyzeUnstructuredDataService
- SemanticSelfDiscoveryService: Use InterpretDataSelfDiscoveryService  
- StructuredAnalysisService: Use AnalyzeStructuredDataService
- UnstructuredAnalysisService: Use AnalyzeUnstructuredDataService
- LineageVisualizationService: Use VisualizeLineageService

Services moved to foundations/libraries:
- DataQualityService -> foundations/libraries/quality/
- MetricsCalculatorService -> foundations/libraries/metrics/
- GuidedDiscoveryService -> foundations/libraries/matching/
- PatternValidationService -> foundations/libraries/validation/
- SchemaMatchingService -> foundations/libraries/matching/
- SemanticMatchingService -> foundations/libraries/matching/
- StructuredExtractionService -> foundations/libraries/extraction/

Use Intent Services from ..intent_services/ for all operations.
"""

# This directory is deprecated. All functionality moved to intent_services/.

__all__ = []
