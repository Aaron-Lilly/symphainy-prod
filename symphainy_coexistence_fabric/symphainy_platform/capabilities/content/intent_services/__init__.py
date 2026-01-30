"""
Content Capability Intent Services (New Architecture)

These intent services use the new PlatformIntentService base class
and receive PlatformContext (ctx) for execution.

Architecture:
    - Services extend PlatformIntentService
    - Services receive PlatformContext (ctx) at execute time
    - Services access platform via ctx.platform, ctx.governance, ctx.reasoning

Rebuilt Services (Core Content Flow):
    - IngestFileService: Ingests files using ctx.platform.ingest_file()
    - SaveMaterializationService: Transitions files from Working Material to Records of Fact
    - ParseContentService: Parses uploaded files using ctx.platform.parse()
    - CreateDeterministicEmbeddingsService: Creates schema fingerprints via ctx.platform
    - EchoService: Test service for platform wiring validation

Flow: ingest_file → save_materialization → parse_content → create_deterministic_embeddings
"""

from .create_deterministic_embeddings_service import CreateDeterministicEmbeddingsService
from .echo_service import EchoService
from .ingest_file_service import IngestFileService
from .parse_content_service import ParseContentService
from .save_materialization_service import SaveMaterializationService

__all__ = [
    "CreateDeterministicEmbeddingsService",
    "EchoService",
    "IngestFileService",
    "ParseContentService",
    "SaveMaterializationService",
]
