"""
Ingestion Service - Content Realm

Unified ingestion service for all ingestion methods (Upload, EDI, API).
"""

from .ingestion_service import IngestionService

__all__ = ["IngestionService"]
