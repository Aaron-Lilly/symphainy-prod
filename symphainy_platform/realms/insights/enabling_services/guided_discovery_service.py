"""
Guided Discovery Service - Constrained Semantic Interpretation

Enabling service for guided discovery operations using user-provided guides.

WHAT (Enabling Service Role): I interpret data using user-provided guides
HOW (Enabling Service Implementation): I use guide fact patterns to constrain semantic reasoning

Key Principle: Constrained semantic interpretation - user-provided guides constrain discovery.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.platform_sdk.guide_registry import GuideRegistry


class GuidedDiscoveryService:
    """
    Guided Discovery Service - Constrained semantic interpretation.
    
    Interprets data using user-provided guides (fact patterns + output templates).
    Returns:
    - Matched entities (found in data, match guide)
    - Unmatched data (found in data, no guide match)
    - Missing expected (expected in guide, not found in data)
    - Suggestions for unmatched/missing
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Guided Discovery Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Initialize Guide Registry
        supabase_adapter = None
        if public_works:
            supabase_adapter = public_works.get_supabase_adapter()
        
        if GuideRegistry:
            self.guide_registry = GuideRegistry(supabase_adapter=supabase_adapter)
        else:
            self.guide_registry = None
            self.logger.warning("GuideRegistry not available")
    
    async def interpret_with_guide(
        self,
        parsed_file_id: str,
        guide_id: str,
        embeddings: List[Dict[str, Any]],
        matching_options: Dict[str, Any],
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Interpret data using user-provided guide.
        
        Args:
            parsed_file_id: Parsed file identifier
            guide_id: Guide identifier
            embeddings: List of embeddings from ArangoDB
            matching_options: Matching options (show_unmatched, show_suggestions)
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with matched entities, unmatched data, missing expected, suggestions
        """
        self.logger.info(
            f"Interpreting data with guide: {parsed_file_id} (guide: {guide_id}) "
            f"for tenant: {tenant_id}"
        )
        
        try:
            # Get guide from registry
            if not self.guide_registry:
                raise ValueError("Guide Registry not available")
            
            guide = await self.guide_registry.get_guide(guide_id, tenant_id)
            if not guide:
                raise ValueError(f"Guide not found: {guide_id}")
            
            fact_pattern = guide.get("fact_pattern", {})
            output_template = guide.get("output_template", {})
            
            # Match data against guide entities/relationships
            matched_entities = await self._match_entities(
                embeddings, fact_pattern, matching_options
            )
            
            # Identify unmatched data
            unmatched_data = []
            if matching_options.get("show_unmatched", True):
                unmatched_data = await self._identify_unmatched_data(
                    embeddings, fact_pattern, matched_entities
                )
            
            # Identify missing expected entities
            missing_expected = await self._identify_missing_expected(
                fact_pattern, matched_entities
            )
            
            # Generate suggestions
            suggestions = []
            if matching_options.get("show_suggestions", True):
                suggestions = await self._generate_suggestions(
                    unmatched_data, missing_expected, fact_pattern
                )
            
            # Calculate confidence and coverage scores
            confidence_score = self._calculate_confidence_score(matched_entities, fact_pattern)
            coverage_score = self._calculate_coverage_score(matched_entities, fact_pattern)
            
            # Format output using guide template
            formatted_output = await self._format_output(
                matched_entities, output_template
            )
            
            return {
                "interpretation": {
                    "matched_entities": matched_entities,
                    "unmatched_data": unmatched_data,
                    "missing_expected": missing_expected,
                    "suggestions": suggestions,
                    "confidence_score": confidence_score,
                    "coverage_score": coverage_score,
                    "formatted_output": formatted_output
                },
                "guide_id": guide_id,
                "parsed_file_id": parsed_file_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to interpret with guide: {e}", exc_info=True)
            return {
                "interpretation": {
                    "matched_entities": [],
                    "unmatched_data": [],
                    "missing_expected": [],
                    "suggestions": [],
                    "confidence_score": 0.0,
                    "coverage_score": 0.0,
                    "error": str(e)
                },
                "guide_id": guide_id,
                "parsed_file_id": parsed_file_id
            }
    
    async def _match_entities(
        self,
        embeddings: List[Dict[str, Any]],
        fact_pattern: Dict[str, Any],
        matching_options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Match embeddings against guide entities.
        
        Args:
            embeddings: List of embeddings
            fact_pattern: Guide fact pattern (entities, relationships, attributes)
            matching_options: Matching options
        
        Returns:
            List of matched entities
        """
        expected_entities = fact_pattern.get("entities", [])
        matched_entities = []
        
        # For each expected entity in guide
        for expected_entity in expected_entities:
            entity_type = expected_entity.get("entity_type")
            expected_attributes = expected_entity.get("attributes", {})
            
            # Try to find matching embeddings
            for emb in embeddings:
                emb_entity_type = emb.get("entity_type")
                emb_attributes = emb.get("attributes", {})
                
                # Check if entity type matches
                if emb_entity_type == entity_type or self._fuzzy_match_entity_type(emb_entity_type, entity_type):
                    # Check if attributes match
                    attribute_matches = self._match_attributes(emb_attributes, expected_attributes)
                    
                    if attribute_matches.get("match_score", 0) > 0.5:
                        matched_entities.append({
                            "entity": entity_type,
                            "confidence": attribute_matches.get("match_score", 0.8),
                            "attributes": emb_attributes,
                            "source_embedding": emb.get("embedding_id")
                        })
        
        return matched_entities
    
    async def _identify_unmatched_data(
        self,
        embeddings: List[Dict[str, Any]],
        fact_pattern: Dict[str, Any],
        matched_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify data that doesn't match guide entities.
        
        Args:
            embeddings: List of embeddings
            fact_pattern: Guide fact pattern
            matched_entities: Already matched entities
        
        Returns:
            List of unmatched data
        """
        matched_embedding_ids = {e.get("source_embedding") for e in matched_entities}
        expected_entity_types = {e.get("entity_type") for e in fact_pattern.get("entities", [])}
        
        unmatched_data = []
        
        for emb in embeddings:
            emb_id = emb.get("embedding_id")
            if emb_id not in matched_embedding_ids:
                emb_entity_type = emb.get("entity_type")
                
                # Check if entity type is not in expected entities
                if not emb_entity_type or emb_entity_type not in expected_entity_types:
                    unmatched_data.append({
                        "data_snippet": emb.get("semantic_meaning", str(emb)),
                        "reason": "No matching entity in guide",
                        "entity_type": emb_entity_type,
                        "source_embedding": emb_id
                    })
        
        return unmatched_data
    
    async def _identify_missing_expected(
        self,
        fact_pattern: Dict[str, Any],
        matched_entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify expected entities that weren't found in data.
        
        Args:
            fact_pattern: Guide fact pattern
            matched_entities: Already matched entities
        
        Returns:
            List of missing expected entities
        """
        expected_entities = fact_pattern.get("entities", [])
        matched_entity_types = {e.get("entity") for e in matched_entities}
        
        missing_expected = []
        
        for expected_entity in expected_entities:
            entity_type = expected_entity.get("entity_type")
            if entity_type not in matched_entity_types:
                missing_expected.append({
                    "expected_entity": entity_type,
                    "reason": "Not found in data",
                    "expected_attributes": expected_entity.get("attributes", {})
                })
        
        return missing_expected
    
    async def _generate_suggestions(
        self,
        unmatched_data: List[Dict[str, Any]],
        missing_expected: List[Dict[str, Any]],
        fact_pattern: Dict[str, Any]
    ) -> List[str]:
        """
        Generate suggestions for unmatched data and missing expected entities.
        
        Args:
            unmatched_data: Unmatched data
            missing_expected: Missing expected entities
            fact_pattern: Guide fact pattern
        
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Suggestions for unmatched data
        for unmatched in unmatched_data:
            entity_type = unmatched.get("entity_type")
            if entity_type:
                suggestions.append(f"Could be '{entity_type}' entity - consider adding to guide")
            else:
                suggestions.append("Could be a new entity type - consider adding to guide")
        
        # Suggestions for missing expected
        for missing in missing_expected:
            expected_entity = missing.get("expected_entity")
            suggestions.append(
                f"Expected '{expected_entity}' entity not found - check if data contains this entity "
                "or if guide needs adjustment"
            )
        
        return suggestions
    
    async def _format_output(
        self,
        matched_entities: List[Dict[str, Any]],
        output_template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format output using guide template.
        
        Args:
            matched_entities: Matched entities
            output_template: Guide output template
        
        Returns:
            Formatted output
        """
        # For MVP: Simple template application
        # In full implementation: Use template engine to format output
        
        formatted = {
            "entities": matched_entities,
            "template_version": output_template.get("version", "1.0")
        }
        
        # Apply template structure if provided
        if output_template.get("structure"):
            structure = output_template.get("structure")
            formatted.update(structure)
        
        return formatted
    
    def _fuzzy_match_entity_type(
        self,
        emb_entity_type: Optional[str],
        expected_entity_type: str
    ) -> bool:
        """Fuzzy match entity types (simple heuristic)."""
        if not emb_entity_type:
            return False
        
        # Simple case-insensitive matching
        return emb_entity_type.lower() == expected_entity_type.lower()
    
    def _match_attributes(
        self,
        emb_attributes: Dict[str, Any],
        expected_attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Match attributes between embedding and expected entity.
        
        Returns:
            Dict with match_score and matched_attributes
        """
        if not expected_attributes:
            return {"match_score": 0.8, "matched_attributes": {}}
        
        matched_count = 0
        total_count = len(expected_attributes)
        matched_attributes = {}
        
        for key, expected_value in expected_attributes.items():
            if key in emb_attributes:
                emb_value = emb_attributes[key]
                # Simple value matching (can be enhanced)
                if emb_value == expected_value or str(emb_value).lower() == str(expected_value).lower():
                    matched_count += 1
                    matched_attributes[key] = emb_value
        
        match_score = matched_count / total_count if total_count > 0 else 0.0
        
        return {
            "match_score": match_score,
            "matched_attributes": matched_attributes
        }
    
    def _calculate_confidence_score(
        self,
        matched_entities: List[Dict[str, Any]],
        fact_pattern: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for matched entities."""
        if not matched_entities:
            return 0.0
        
        # Average confidence of matched entities
        confidences = [e.get("confidence", 0.0) for e in matched_entities]
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def _calculate_coverage_score(
        self,
        matched_entities: List[Dict[str, Any]],
        fact_pattern: Dict[str, Any]
    ) -> float:
        """Calculate coverage score (how much of guide was matched)."""
        expected_entities = fact_pattern.get("entities", [])
        if not expected_entities:
            return 0.0
        
        matched_entity_types = {e.get("entity") for e in matched_entities}
        expected_entity_types = {e.get("entity_type") for e in expected_entities}
        
        if not expected_entity_types:
            return 0.0
        
        matched_count = len(matched_entity_types.intersection(expected_entity_types))
        return matched_count / len(expected_entity_types)
