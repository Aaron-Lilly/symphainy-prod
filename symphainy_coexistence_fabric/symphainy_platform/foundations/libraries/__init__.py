"""
Foundations Libraries - Pure Algorithmic Capabilities

These are pure libraries with no business logic, no orchestration, no LLM access.
They provide composable capabilities that can be used by Intent Services.

Organization:
- parsing/       - File parsing capabilities
- chunking/      - Deterministic chunking
- embeddings/    - Embedding generation
- matching/      - Schema and semantic matching
- validation/    - Pattern validation
- metrics/       - Metrics calculation
- quality/       - Data quality assessment
- coexistence/   - Coexistence analysis and blueprints
- export/        - Export and migration capabilities
- extraction/    - Structured data extraction
- visualization/ - Visual generation (diagrams, charts)
- reporting/     - Report generation
- workflow/      - Workflow conversion
- governance/    - Governance enforcement
- registries/    - Profile and config registries

Usage:
    from symphainy_platform.foundations.libraries.parsing import FileParserService
    from symphainy_platform.foundations.libraries.chunking import DeterministicChunkingService
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .parsing import FileParserService
    from .chunking import DeterministicChunkingService
    from .embeddings import DeterministicEmbeddingService
    from .matching import SchemaMatchingService, SemanticMatchingService, GuidedDiscoveryService
    from .validation import PatternValidationService
    from .metrics import MetricsCalculatorService
    from .quality import DataQualityService
    from .coexistence import CoexistenceAnalysisService
    from .export import ExportService
    from .extraction import StructuredExtractionService
    from .visualization import VisualGenerationService
    from .reporting import ReportGeneratorService
    from .workflow import WorkflowConversionService
    from .governance import SemanticTriggerBoundary
    from .registries import SemanticProfileRegistry

__all__ = [
    "FileParserService",
    "DeterministicChunkingService", 
    "DeterministicEmbeddingService",
    "SchemaMatchingService",
    "SemanticMatchingService",
    "GuidedDiscoveryService",
    "PatternValidationService",
    "MetricsCalculatorService",
    "DataQualityService",
    "CoexistenceAnalysisService",
    "ExportService",
    "StructuredExtractionService",
    "VisualGenerationService",
    "ReportGeneratorService",
    "WorkflowConversionService",
    "SemanticTriggerBoundary",
    "SemanticProfileRegistry",
]
