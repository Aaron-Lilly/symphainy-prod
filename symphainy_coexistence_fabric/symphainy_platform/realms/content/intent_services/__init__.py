"""
Content Realm Intent Services

Intent services for the Content Realm that handle file operations.

Services:
- IngestFileService: Handles file ingestion (upload, EDI, API)
- SaveMaterializationService: Handles materialization registration and lifecycle transitions
- ParseContentService: Parses uploaded files to extract structured content
- ArchiveFileService: Archives (soft deletes) file artifacts
- DeleteFileService: Permanently deletes file artifacts (hard delete)
- ExtractEmbeddingsService: Extracts semantic embeddings from content
- CreateDeterministicEmbeddingsService: Creates deterministic embeddings
- GetParsedFileService: Retrieves parsed file content
- ListArtifactsService: Lists artifacts in session/tenant scope
- RetrieveArtifactMetadataService: Retrieves artifact metadata

These services extend BaseIntentService and follow contract specifications.
"""

from .ingest_file_service import IngestFileService
from .save_materialization_service import SaveMaterializationService
from .parse_content_service import ParseContentService
from .archive_file_service import ArchiveFileService
from .delete_file_service import DeleteFileService
from .extract_embeddings_service import ExtractEmbeddingsService
from .create_deterministic_embeddings_service import CreateDeterministicEmbeddingsService
from .get_parsed_file_service import GetParsedFileService
from .list_artifacts_service import ListArtifactsService
from .retrieve_artifact_metadata_service import RetrieveArtifactMetadataService

__all__ = [
    # Core file operations
    "IngestFileService",
    "SaveMaterializationService",
    "ParseContentService",
    # File management
    "ArchiveFileService",
    "DeleteFileService",
    # Embeddings
    "ExtractEmbeddingsService",
    "CreateDeterministicEmbeddingsService",
    # Retrieval
    "GetParsedFileService",
    "ListArtifactsService",
    "RetrieveArtifactMetadataService",
]
