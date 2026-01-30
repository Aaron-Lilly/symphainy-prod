"""
Insights Capability Intent Services (Platform SDK Architecture)

These intent services use the PlatformIntentService base class
and receive PlatformContext (ctx) for execution.

Data Quality:
    - AssessDataQualityService: Multi-dimensional quality assessment

Data Interpretation (AI-powered via ctx.reasoning):
    - InterpretDataSelfDiscoveryService: AI-driven discovery via InsightsEDAAgent
    - InterpretDataGuidedService: Guided interpretation with user constraints

Analysis:
    - AnalyzeStructuredDataService: Structured data analysis
    - AnalyzeUnstructuredDataService: Unstructured data analysis

Visualization:
    - VisualizeLineageService: Data lineage visualization
    - MapRelationshipsService: Entity relationship mapping
"""

from .assess_data_quality_service import AssessDataQualityService
from .interpret_data_self_discovery_service import InterpretDataSelfDiscoveryService
from .interpret_data_guided_service import InterpretDataGuidedService
from .analyze_structured_data_service import AnalyzeStructuredDataService
from .analyze_unstructured_data_service import AnalyzeUnstructuredDataService
from .visualize_lineage_service import VisualizeLineageService
from .map_relationships_service import MapRelationshipsService

__all__ = [
    "AssessDataQualityService",
    "InterpretDataSelfDiscoveryService",
    "InterpretDataGuidedService",
    "AnalyzeStructuredDataService",
    "AnalyzeUnstructuredDataService",
    "VisualizeLineageService",
    "MapRelationshipsService",
]
