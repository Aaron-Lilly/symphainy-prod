"""
Guided Discovery Service - AI-Enhanced Constrained Semantic Interpretation

Enabling service for guided discovery operations using user-provided guides.

WHAT (Enabling Service Role): I interpret data using user-provided guides
HOW (Enabling Service Implementation): I use guide fact patterns to constrain semantic reasoning,
    with OPTIONAL AI enhancement for intelligent suggestions and semantic matching.

Key Principle: Constrained semantic interpretation - user-provided guides constrain discovery.
AI Enhancement: Optional LLM-powered suggestions and semantic understanding.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
import json

from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext
from .schema_matching_service import SchemaMatchingService
from .semantic_matching_service import SemanticMatchingService
from symphainy_platform.foundations.libraries.validation.pattern_validation_service import PatternValidationService


class GuidedDiscoveryService:
    """
    Guided Discovery Service - AI-Enhanced Constrained semantic interpretation.
    
    Interprets data using user-provided guides (fact patterns + output templates).
    
    Returns:
    - Matched entities (found in data, match guide)
    - Unmatched data (found in data, no guide match)
    - Missing expected (expected in guide, not found in data)
    - AI-powered suggestions for unmatched/missing (when enabled)
    - Semantic interpretation explanation (when AI enabled)
    
    AI Enhancement Features:
    - Intelligent suggestion generation using LLM reasoning
    - Semantic entity matching beyond string comparison
    - Interpretation explanations for why data matches or doesn't match
    """
    
    def __init__(self, public_works: Optional[Any] = None, enable_ai: bool = True):
        """
        Initialize Guided Discovery Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
            enable_ai: Whether to enable AI-powered suggestions and interpretation
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        self.enable_ai = enable_ai
        
        # Use guide registry from Public Works (protocol; no adapter access)
        self.guide_registry = public_works.get_guide_registry() if public_works else None
        if not self.guide_registry:
            self.logger.warning("Guide registry not available")
        
        # Initialize three-phase matching services
        # ARCHITECTURAL PRINCIPLE: Use Public Works abstractions for governed access
        self.schema_matching_service = SchemaMatchingService(public_works=public_works)
        self.semantic_matching_service = SemanticMatchingService(public_works=public_works)
        self.pattern_validation_service = PatternValidationService(public_works=public_works)
        
        # LLM adapter for AI-powered features
        self._llm_adapter = None
        if public_works and enable_ai:
            try:
                self._llm_adapter = public_works.get_llm_adapter()
            except Exception:
                self.logger.warning("LLM adapter not available - AI features disabled")
    
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
            
            # Generate AI-powered suggestions
            suggestions = []
            if matching_options.get("show_suggestions", True):
                suggestions = await self._generate_suggestions(
                    unmatched_data, missing_expected, fact_pattern, context
                )
            
            # Calculate confidence and coverage scores
            confidence_score = self._calculate_confidence_score(matched_entities, fact_pattern)
            coverage_score = self._calculate_coverage_score(matched_entities, fact_pattern)
            
            # Format output using guide template
            formatted_output = await self._format_output(
                matched_entities, output_template
            )
            
            # Generate AI-powered interpretation summary if enabled
            interpretation_summary = None
            if self.enable_ai and matching_options.get("include_ai_summary", True):
                interpretation_summary = await self._generate_interpretation_summary(
                    matched_entities, unmatched_data, missing_expected, fact_pattern
                )
            
            return {
                "interpretation": {
                    "matched_entities": matched_entities,
                    "unmatched_data": unmatched_data,
                    "missing_expected": missing_expected,
                    "suggestions": suggestions,
                    "confidence_score": confidence_score,
                    "coverage_score": coverage_score,
                    "formatted_output": formatted_output,
                    "ai_summary": interpretation_summary,
                    "ai_enhanced": self.enable_ai and self._llm_adapter is not None
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
        fact_pattern: Dict[str, Any],
        context: Optional[ExecutionContext] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate AI-powered suggestions for unmatched data and missing expected entities.
        
        When AI is enabled, uses LLM reasoning to provide intelligent suggestions
        explaining WHY data doesn't match and WHAT can be done about it.
        
        Args:
            unmatched_data: Unmatched data
            missing_expected: Missing expected entities
            fact_pattern: Guide fact pattern
            context: Optional execution context
        
        Returns:
            List of suggestion dictionaries with explanations
        """
        # Try AI-powered suggestions first
        if self.enable_ai and self._llm_adapter and (unmatched_data or missing_expected):
            try:
                ai_suggestions = await self._generate_ai_suggestions(
                    unmatched_data, missing_expected, fact_pattern
                )
                if ai_suggestions:
                    return ai_suggestions
            except Exception as e:
                self.logger.warning(f"AI suggestion generation failed: {e}")
        
        # Fallback to rule-based suggestions
        return self._generate_rule_based_suggestions(unmatched_data, missing_expected)
    
    async def _generate_ai_suggestions(
        self,
        unmatched_data: List[Dict[str, Any]],
        missing_expected: List[Dict[str, Any]],
        fact_pattern: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate intelligent suggestions using LLM reasoning.
        
        Provides semantic understanding of WHY matches failed and intelligent
        recommendations for resolution.
        """
        # Build context for LLM
        expected_entities = fact_pattern.get("entities", [])
        
        prompt = f"""You are a data interpretation assistant analyzing why certain data didn't match expected patterns in a guide.

**Expected Entities from Guide:**
{json.dumps(expected_entities, indent=2)}

**Unmatched Data (found in data but doesn't match guide):**
{json.dumps(unmatched_data[:10], indent=2)}  

**Missing Expected (expected in guide but not found in data):**
{json.dumps(missing_expected[:10], indent=2)}

Please provide intelligent suggestions as a JSON array. For each issue, explain:
1. WHY the match likely failed (semantic reasoning)
2. WHAT the user can do to resolve it (actionable recommendation)
3. Whether this is a guide issue or a data issue

Return JSON array with this structure:
[
  {{
    "issue_type": "unmatched_data" or "missing_expected",
    "entity": "entity name",
    "reason": "Explanation of why the match failed",
    "recommendation": "What the user should do",
    "confidence": 0.0-1.0,
    "source": "ai"
  }}
]"""

        system_message = """You are a data interpretation expert. Analyze match failures between data and guides, 
providing intelligent semantic reasoning for why matches failed and actionable recommendations."""

        try:
            response = await self._llm_adapter.create_completion(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=1500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            if isinstance(response, str):
                result = json.loads(response)
            elif isinstance(response, dict):
                result = response.get("suggestions", response.get("choices", [{}])[0].get("message", {}).get("content", "[]"))
                if isinstance(result, str):
                    result = json.loads(result)
            else:
                result = []
            
            # Ensure it's a list
            if isinstance(result, dict):
                result = result.get("suggestions", [result])
            
            self.logger.info(f"✅ Generated {len(result)} AI-powered suggestions")
            return result
            
        except Exception as e:
            self.logger.warning(f"AI suggestion parsing failed: {e}")
            return []
    
    def _generate_rule_based_suggestions(
        self,
        unmatched_data: List[Dict[str, Any]],
        missing_expected: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate rule-based suggestions as fallback.
        
        Returns structured suggestions even without AI.
        """
        suggestions = []
        
        # Suggestions for unmatched data
        for unmatched in unmatched_data:
            entity_type = unmatched.get("entity_type")
            if entity_type:
                suggestions.append({
                    "issue_type": "unmatched_data",
                    "entity": entity_type,
                    "reason": f"Entity type '{entity_type}' found in data but not defined in guide",
                    "recommendation": f"Consider adding '{entity_type}' to your guide's expected entities",
                    "confidence": 0.6,
                    "source": "rule_based"
                })
            else:
                suggestions.append({
                    "issue_type": "unmatched_data",
                    "entity": "unknown",
                    "reason": "Data element found with no entity type classification",
                    "recommendation": "Review the unmatched data and consider adding new entity types to guide",
                    "confidence": 0.4,
                    "source": "rule_based"
                })
        
        # Suggestions for missing expected
        for missing in missing_expected:
            expected_entity = missing.get("expected_entity")
            suggestions.append({
                "issue_type": "missing_expected",
                "entity": expected_entity,
                "reason": f"Expected entity '{expected_entity}' defined in guide but not found in data",
                "recommendation": f"Check if data contains '{expected_entity}' under a different name, or adjust guide expectations",
                "confidence": 0.6,
                "source": "rule_based"
            })
        
        return suggestions
    
    async def _generate_interpretation_summary(
        self,
        matched_entities: List[Dict[str, Any]],
        unmatched_data: List[Dict[str, Any]],
        missing_expected: List[Dict[str, Any]],
        fact_pattern: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an AI-powered interpretation summary explaining the overall results.
        
        This provides a human-readable explanation of what the interpretation found
        and what it means in context.
        """
        if not self._llm_adapter:
            raise RuntimeError(
                "LLM adapter not wired; cannot generate interpretation summary. Platform contract §8A."
            )
        try:
            prompt = f"""You are a data interpretation expert. Summarize the results of matching data against a guide.

**Matched Entities ({len(matched_entities)} found):**
{json.dumps(matched_entities[:5], indent=2)}{"..." if len(matched_entities) > 5 else ""}

**Unmatched Data ({len(unmatched_data)} items):**
{json.dumps(unmatched_data[:5], indent=2)}{"..." if len(unmatched_data) > 5 else ""}

**Missing Expected ({len(missing_expected)} items):**
{json.dumps(missing_expected[:5], indent=2)}{"..." if len(missing_expected) > 5 else ""}

**Guide Expected Entities:**
{json.dumps(fact_pattern.get("entities", [])[:5], indent=2)}

Please provide:
1. A brief summary of what was found (2-3 sentences)
2. The overall quality assessment (excellent/good/fair/poor)
3. Key observations about the data-guide alignment
4. Top 3 priority actions the user should take

Return as JSON:
{{
  "summary": "Brief summary...",
  "quality_assessment": "good",
  "key_observations": ["observation1", "observation2"],
  "priority_actions": ["action1", "action2", "action3"]
}}"""

            system_message = """You are a data interpretation expert providing actionable summaries 
of guide-based data matching results. Be concise and actionable."""

            response = await self._llm_adapter.create_completion(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o-mini",
                max_tokens=800,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            if isinstance(response, str):
                result = json.loads(response)
            elif isinstance(response, dict):
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                result = json.loads(content) if isinstance(content, str) else content
            else:
                result = {}
            
            result["source"] = "ai"
            self.logger.info("✅ Generated AI interpretation summary")
            return result
            
        except Exception as e:
            self.logger.warning(f"AI summary generation failed: {e}")
            return {
                "summary": f"Matched {len(matched_entities)} entities, {len(unmatched_data)} unmatched, {len(missing_expected)} missing",
                "quality_assessment": self._assess_quality(len(matched_entities), len(unmatched_data), len(missing_expected)),
                "key_observations": [],
                "priority_actions": ["Review unmatched data manually"],
                "source": "fallback"
            }
    
    def _assess_quality(self, matched: int, unmatched: int, missing: int) -> str:
        """Assess overall quality based on counts."""
        total = matched + unmatched + missing
        if total == 0:
            return "unknown"
        ratio = matched / total
        if ratio >= 0.8:
            return "excellent"
        elif ratio >= 0.6:
            return "good"
        elif ratio >= 0.4:
            return "fair"
        else:
            return "poor"
    
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
    
    async def match_source_to_target(
        self,
        source_deterministic_embedding_id: str,
        target_deterministic_embedding_id: str,
        source_parsed_file_id: str,
        target_parsed_file_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Match source to target using three-phase matching.
        
        ARCHITECTURAL PRINCIPLE: Integrates all three matching services.
        - Phase 1: Schema alignment (exact match via fingerprints)
        - Phase 2: Semantic matching (fuzzy match via embeddings)
        - Phase 3: Pattern validation (data pattern compatibility)
        
        Args:
            source_deterministic_embedding_id: Source deterministic embedding ID
            target_deterministic_embedding_id: Target deterministic embedding ID
            source_parsed_file_id: Source parsed file ID
            target_parsed_file_id: Target parsed file ID
            context: Execution context
        
        Returns:
            Dict with comprehensive mapping results
        """
        self.logger.info(
            f"Matching source to target: source_emb={source_deterministic_embedding_id}, "
            f"target_emb={target_deterministic_embedding_id}"
        )
        
        try:
            # Phase 1: Schema Alignment
            schema_results = await self.schema_matching_service.match_schemas(
                source_deterministic_embedding_id=source_deterministic_embedding_id,
                target_deterministic_embedding_id=target_deterministic_embedding_id,
                context=context
            )
            
            # Phase 2: Semantic Matching
            semantic_results = await self.semantic_matching_service.match_semantically(
                source_parsed_file_id=source_parsed_file_id,
                target_parsed_file_id=target_parsed_file_id,
                schema_matches=schema_results,
                context=context
            )
            
            # Combine Phase 1 and Phase 2 results
            combined_mappings = {
                "exact_matches": schema_results.get("exact_matches", []),
                "semantic_matches": semantic_results.get("semantic_matches", []),
                "similarity_scores": schema_results.get("similarity_scores", {}),
                "enhanced_confidence": semantic_results.get("enhanced_confidence", {}),
                "unmapped_source": schema_results.get("unmapped_source", []),
                "unmapped_target": schema_results.get("unmapped_target", [])
            }
            
            # Phase 3: Pattern Validation
            validation_results = await self.pattern_validation_service.validate_patterns(
                source_deterministic_embedding_id=source_deterministic_embedding_id,
                target_deterministic_embedding_id=target_deterministic_embedding_id,
                mappings=combined_mappings,
                context=context
            )
            
            # Combine all results
            return {
                "mapping_table": validation_results.get("validated_mappings", []),
                "exact_matches": schema_results.get("exact_matches", []),
                "semantic_matches": semantic_results.get("semantic_matches", []),
                "validated_mappings": validation_results.get("validated_mappings", []),
                "unmapped_source": schema_results.get("unmapped_source", []),
                "unmapped_target": schema_results.get("unmapped_target", []),
                "suggested_mappings": semantic_results.get("suggested_mappings", []),
                "warnings": validation_results.get("warnings", []),
                "errors": validation_results.get("errors", []),
                "confidence_scores": {
                    "schema_confidence": schema_results.get("overall_confidence", 0.0),
                    "semantic_confidence": self._calculate_semantic_confidence(semantic_results),
                    "pattern_validation_confidence": self._calculate_validation_confidence(validation_results)
                },
                "overall_confidence": self._calculate_overall_confidence(
                    schema_results, semantic_results, validation_results
                ),
                "phase_results": {
                    "phase_1_schema": schema_results,
                    "phase_2_semantic": semantic_results,
                    "phase_3_validation": validation_results
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to match source to target: {e}", exc_info=True)
            return {
                "mapping_table": [],
                "exact_matches": [],
                "semantic_matches": [],
                "validated_mappings": [],
                "unmapped_source": [],
                "unmapped_target": [],
                "suggested_mappings": [],
                "warnings": [],
                "errors": [{"message": str(e), "severity": "error"}],
                "confidence_scores": {},
                "overall_confidence": 0.0,
                "error": str(e)
            }
    
    def _calculate_semantic_confidence(self, semantic_results: Dict[str, Any]) -> float:
        """Calculate overall semantic confidence."""
        semantic_matches = semantic_results.get("semantic_matches", [])
        if not semantic_matches:
            return 0.0
        
        confidences = [m.get("confidence", 0.0) for m in semantic_matches]
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def _calculate_validation_confidence(self, validation_results: Dict[str, Any]) -> float:
        """Calculate overall pattern validation confidence."""
        validation_scores = validation_results.get("validation_scores", {})
        if not validation_scores:
            return 0.0
        
        scores = list(validation_scores.values())
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_overall_confidence(
        self,
        schema_results: Dict[str, Any],
        semantic_results: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence from all three phases."""
        schema_conf = schema_results.get("overall_confidence", 0.0)
        semantic_conf = self._calculate_semantic_confidence(semantic_results)
        validation_conf = self._calculate_validation_confidence(validation_results)
        
        # Weighted average (schema: 40%, semantic: 30%, validation: 30%)
        overall = (schema_conf * 0.4) + (semantic_conf * 0.3) + (validation_conf * 0.3)
        return overall