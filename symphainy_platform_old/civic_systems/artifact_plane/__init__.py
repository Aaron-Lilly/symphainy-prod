"""
Artifact Plane - Derived Artifact Management

The Artifact Plane provides first-class management of derived artifacts (roadmaps, POCs, blueprints, etc.)
as governed representations separate from execution state.

WHAT (Civic System Role): I manage the lifecycle of derived artifacts
HOW (Civic System Implementation): I coordinate artifact storage, registry, and lineage
"""

from .artifact_plane import ArtifactPlane

__all__ = ["ArtifactPlane"]
