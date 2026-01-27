"""
Content Solution - Content Realm Solution

Composes content journeys, exposes SOA APIs, and wires up with Experience SDK.

WHAT (Solution Role): I provide content capabilities for the platform
HOW (Solution Implementation): I compose content journeys and expose SOA APIs

Key Journeys:
- File Upload & Materialization: Upload files, save materializations
- File Parsing: Parse content into structured format
- Deterministic Embedding: Create deterministic embeddings for content
- File Management: Archive, retrieve, list artifacts
"""

from .content_solution import ContentSolution

__all__ = ["ContentSolution"]
