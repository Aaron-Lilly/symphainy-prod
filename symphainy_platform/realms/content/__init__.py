"""
Content Realm - Ingest, Parse, Embeddings, Canonical Facts

Content Realm defines meaning for content operations.

WHAT (Content Realm Role): I define meaning for content ingestion, parsing, and semantic interpretation
HOW (Content Realm Implementation): I coordinate orchestrators, enabling services, and agents

Key Principle: Content Realm is the data front door - all client data enters here.
"""

from .content_realm import ContentRealm

__all__ = ["ContentRealm"]
