"""
Content Realm Intent Services

Intent services for the Content Realm that handle file ingestion and materialization.

Services:
- IngestFileService: Handles file ingestion (upload, EDI, API)
- SaveMaterializationService: Handles materialization registration and lifecycle transitions

These services extend BaseIntentService and follow contract specifications:
- docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md
- docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md
"""

from .ingest_file_service import IngestFileService
from .save_materialization_service import SaveMaterializationService

__all__ = [
    "IngestFileService",
    "SaveMaterializationService",
]
