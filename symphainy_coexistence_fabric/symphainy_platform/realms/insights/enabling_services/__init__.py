"""
Insights Enabling Services - Pure Data Processing

Services that remain in realm (have unique orchestrator functionality):
- DataAnalyzerService: Aggregator service for insights orchestrator
- SemanticSelfDiscoveryService: Self-discovery interpretation
- StructuredAnalysisService: Structured data analysis
- UnstructuredAnalysisService: Unstructured data analysis
- LineageVisualizationService: Data lineage visualization

Services moved to foundations/libraries:
- DataQualityService -> foundations/libraries/quality/
- MetricsCalculatorService -> foundations/libraries/metrics/
- GuidedDiscoveryService -> foundations/libraries/matching/
- PatternValidationService -> foundations/libraries/validation/
- SchemaMatchingService -> foundations/libraries/matching/
- SemanticMatchingService -> foundations/libraries/matching/
- StructuredExtractionService -> foundations/libraries/extraction/
"""

from .data_analyzer_service import DataAnalyzerService
from .semantic_self_discovery_service import SemanticSelfDiscoveryService
from .structured_analysis_service import StructuredAnalysisService
from .unstructured_analysis_service import UnstructuredAnalysisService
from .lineage_visualization_service import LineageVisualizationService

__all__ = [
    "DataAnalyzerService",
    "SemanticSelfDiscoveryService",
    "StructuredAnalysisService",
    "UnstructuredAnalysisService",
    "LineageVisualizationService"
]
