"""
Insights Realm - Data Quality, Analysis, and Interpretation

The Insights Realm is responsible for assessing data quality, creating semantic
interpretations, discovering relationships, and generating business insights.

WHAT (Realm Role): I analyze, interpret, and generate insights from data
HOW (Realm Implementation): I provide intent services for quality, interpretation, and analysis

Key Principles:
- Intent services are pure services (agents handled at orchestrator layer)
- All services use Public Works abstractions (no direct infrastructure)
- Artifacts stored in Artifact Plane (not execution state)
- Services exposed as SOA APIs by orchestrator, wrapped as MCP Tools for agents

Naming Convention:
- Realm name: Insights Realm
- Solution: InsightsSolution (platform construct that composes journeys)
- Artifact prefix: insights_* (e.g., insights_quality_report, insights_analysis)
"""

from .intent_services import (
    AssessDataQualityService,
    InterpretDataSelfDiscoveryService,
    InterpretDataGuidedService,
    AnalyzeStructuredDataService,
    AnalyzeUnstructuredDataService,
    VisualizeLineageService,
    MapRelationshipsService
)

__all__ = [
    "AssessDataQualityService",
    "InterpretDataSelfDiscoveryService",
    "InterpretDataGuidedService",
    "AnalyzeStructuredDataService",
    "AnalyzeUnstructuredDataService",
    "VisualizeLineageService",
    "MapRelationshipsService"
]
