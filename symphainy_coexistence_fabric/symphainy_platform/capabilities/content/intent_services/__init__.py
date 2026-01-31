"""
Content Capability Intent Services (Platform SDK Architecture)

These intent services use the PlatformIntentService base class
and receive PlatformContext (ctx) for execution.

Architecture:
    - Services extend PlatformIntentService
    - Services receive PlatformContext (ctx) at execute time
    - Services access platform via ctx.platform, ctx.governance, ctx.reasoning

Core Content Flow:
    - IngestFileService: Ingests files using ctx.platform.ingest_file()
    - SaveMaterializationService: Transitions files from Working Material to Records of Fact
    - ParseContentService: Parses uploaded files using ctx.platform.parse()
    - CreateDeterministicEmbeddingsService: Creates schema fingerprints via ctx.platform

File Management:
    - GetParsedFileService: Retrieves parsed file content
    - RetrieveArtifactMetadataService: Retrieves artifact metadata
    - ListArtifactsService: Lists artifacts for tenant/session
    - ArchiveFileService: Soft delete (archive) files
    - DeleteFileService: Hard delete files

Test Service:
    - EchoService: Platform wiring validation

Flow: ingest_file → save_materialization → parse_content → create_deterministic_embeddings
"""

from .archive_file_service import ArchiveFileService
from .create_deterministic_embeddings_service import CreateDeterministicEmbeddingsService
from .delete_file_service import DeleteFileService
from .echo_service import EchoService
from .get_parsed_file_service import GetParsedFileService
from .ingest_file_service import IngestFileService
from .list_artifacts_service import ListArtifactsService
from .parse_content_service import ParseContentService
from .retrieve_artifact_metadata_service import RetrieveArtifactMetadataService
from .save_materialization_service import SaveMaterializationService

__all__ = [
    "ArchiveFileService",
    "CreateDeterministicEmbeddingsService",
    "DeleteFileService",
    "EchoService",
    "GetParsedFileService",
    "IngestFileService",
    "ListArtifactsService",
    "ParseContentService",
    "RetrieveArtifactMetadataService",
    "SaveMaterializationService",
]
