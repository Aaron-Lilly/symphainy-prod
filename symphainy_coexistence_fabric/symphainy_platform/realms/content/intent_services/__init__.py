"""
Content Realm Intent Services

Atomic platform capabilities for the Content Realm.

Intent services are SOA APIs in realms. They align to intent contracts.
Intent services return artifacts and events.
Intent services never bypass Runtime.

Available Intent Services:
- IngestFileService: Implements ingest_file intent
- SaveMaterializationService: Implements save_materialization intent

Contract Locations:
- ingest_file: docs/intent_contracts/journey_content_file_upload_materialization/intent_ingest_file.md
- save_materialization: docs/intent_contracts/journey_content_file_upload_materialization/intent_save_materialization.md

Usage:
    from symphainy_platform.realms.content.intent_services import (
        IngestFileService,
        SaveMaterializationService
    )
    
    # Initialize services with Public Works and State Surface
    ingest_service = IngestFileService(public_works, state_surface)
    save_service = SaveMaterializationService(public_works, state_surface)
    
    # Execute intents via Runtime
    result = await ingest_service.execute(context, params)
"""

from .ingest_file_service import IngestFileService
from .save_materialization_service import SaveMaterializationService

__all__ = [
    "IngestFileService",
    "SaveMaterializationService"
]
