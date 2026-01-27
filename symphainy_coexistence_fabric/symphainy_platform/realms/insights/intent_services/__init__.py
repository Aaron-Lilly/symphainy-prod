"""
Insights Realm Intent Services

Intent services for the Insights Realm. Each service implements a single intent type
following the BaseIntentService pattern.

Architecture:
- Intent services are pure services (agents handled at orchestrator layer)
- All services use Public Works abstractions (no direct infrastructure)
- Artifacts stored in Artifact Plane (not execution state)
- Services are exposed as SOA APIs by orchestrator, wrapped as MCP Tools for agents

Services:
- AssessDataQualityService: Assess data quality across parsing, data, and source dimensions
- InterpretDataSelfDiscoveryService: Self-discovery interpretation (AI-driven)
- InterpretDataGuidedService: Guided interpretation with guides
- AnalyzeStructuredDataService: Analyze structured data for business insights
- AnalyzeUnstructuredDataService: Analyze unstructured data for business insights
- VisualizeLineageService: Visualize data lineage ("Your Data Mash")
- MapRelationshipsService: Map entity relationships

Naming Convention:
- Realm name: Insights Realm
- Solution: InsightsSolution (platform construct)
- Artifact prefix: insights_*
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
    "MapRelationshipsService"
]
