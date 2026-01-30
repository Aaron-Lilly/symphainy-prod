"""
Content Capability Intent Services (New Architecture)

These intent services use the new PlatformIntentService base class
and receive PlatformContext (ctx) for execution.

Architecture:
    - Services extend PlatformIntentService
    - Services receive PlatformContext (ctx) at execute time
    - Services access platform via ctx.platform, ctx.governance, ctx.reasoning

Rebuilt Services:
    - IngestFileService: Ingests files using ctx.platform.ingest_file()
    - ParseContentService: Parses uploaded files using ctx.platform.parse()
    - EchoService: Test service for platform wiring validation
"""

from .echo_service import EchoService
from .ingest_file_service import IngestFileService
from .parse_content_service import ParseContentService

__all__ = [
    "EchoService",
    "IngestFileService",
    "ParseContentService",
]
