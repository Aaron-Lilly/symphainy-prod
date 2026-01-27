"""
Content Realm Package

Provides file ingestion, parsing, and deterministic embeddings capabilities.

WHAT (Content Realm Role): I handle file content operations
HOW (Content Realm Implementation): I provide intent services for ingestion, parsing, embeddings

Key Principle: Content Realm owns file operations. All file access is through
Public Works abstractions, never direct infrastructure access.

Intent Services:
- ingest_file: Upload files to the platform
- save_materialization: Authorize and register file materializations
- parse_file: Parse file content (future)
- create_embeddings: Generate embeddings (future)
"""

from .intent_services import IngestFileService, SaveMaterializationService

__all__ = [
    "IngestFileService",
    "SaveMaterializationService"
]
