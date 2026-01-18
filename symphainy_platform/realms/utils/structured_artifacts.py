"""
Structured Artifact Utilities

Helper functions for creating structured artifacts with semantic_payload and renderings.

WHAT (Utility Role): I help realms create structured artifacts
HOW (Utility Implementation): I separate semantic data from renderings
"""

from typing import Dict, Any, Optional


def create_structured_artifact(
    result_type: str,
    semantic_payload: Dict[str, Any],
    renderings: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a structured artifact with semantic_payload and renderings.
    
    This is the canonical format for realm results:
    - semantic_payload: The meaning/structure (always available, can be re-rendered)
    - renderings: The rendered views (documents, charts, visuals - ephemeral by default)
    
    Args:
        result_type: Type of result (e.g., 'workflow', 'sop', 'blueprint')
        semantic_payload: Semantic representation (IDs, structure, metadata)
        renderings: Rendered artifacts (documents, visuals, etc.)
        metadata: Optional additional metadata
    
    Returns:
        Dict with result_type, semantic_payload, and renderings
    """
    artifact = {
        "result_type": result_type,
        "semantic_payload": semantic_payload,
        "renderings": renderings
    }
    
    if metadata:
        artifact["metadata"] = metadata
    
    return artifact


def extract_semantic_fields(data: Dict[str, Any], semantic_fields: list) -> Dict[str, Any]:
    """
    Extract semantic fields from data dictionary.
    
    Helper to identify which fields are semantic (meaning) vs renderings (views).
    
    Args:
        data: Source data dictionary
        semantic_fields: List of field names that are semantic
    
    Returns:
        Dict with only semantic fields
    """
    semantic = {}
    for field in semantic_fields:
        if field in data:
            semantic[field] = data[field]
    return semantic


def separate_semantic_and_renderings(
    data: Dict[str, Any],
    semantic_fields: list,
    rendering_keys: Optional[list] = None
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Separate semantic payload from renderings in a data dictionary.
    
    Args:
        data: Source data dictionary
        semantic_fields: List of field names that are semantic (e.g., ['workflow_id', 'steps'])
        rendering_keys: Optional list of keys that are renderings (e.g., ['workflow', 'workflow_visual'])
                        If None, all keys not in semantic_fields are renderings
    
    Returns:
        Tuple of (semantic_payload, renderings)
    """
    semantic_payload = extract_semantic_fields(data, semantic_fields)
    
    if rendering_keys:
        renderings = {k: v for k, v in data.items() if k in rendering_keys}
    else:
        # All keys not in semantic_fields are renderings
        renderings = {k: v for k, v in data.items() if k not in semantic_fields}
    
    return semantic_payload, renderings
