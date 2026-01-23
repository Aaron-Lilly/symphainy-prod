"""
Semantic Matching Service - Phase 2: Semantic Matching

Enabling service for semantic matching using semantic embeddings.

WHAT (Enabling Service Role): I match columns by semantic meaning
HOW (Enabling Service Implementation): I use semantic embeddings to find similar columns

ARCHITECTURAL PRINCIPLE: This is Phase 2 of three-phase matching.
- Uses SemanticDataAbstraction (governed access)
- Returns semantic similarity scores
- No business logic - pure matching algorithm
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext


class SemanticMatchingService:
    """
    Semantic Matching Service - Phase 2: Semantic Matching.
    
    Matches columns by semantic meaning using semantic embeddings.
    Returns similarity scores based on semantic similarity.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Semantic Matching Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Get SemanticDataAbstraction (governed access)
        # ARCHITECTURAL PRINCIPLE: Realms use Public Works abstractions, never direct adapters.
        self.semantic_data = None
        if public_works:
            self.semantic_data = public_works.get_semantic_data_abstraction()
            if not self.semantic_data:
                self.logger.warning("SemanticDataAbstraction not available")
    
    async def match_semantically(
        self,
        source_parsed_file_id: str,
        target_parsed_file_id: str,
        schema_matches: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Match columns semantically using semantic embeddings (Phase 2).
        
        ARCHITECTURAL PRINCIPLE: Uses SemanticDataAbstraction for governed access.
        
        Args:
            source_parsed_file_id: Source parsed file ID
            target_parsed_file_id: Target parsed file ID
            schema_matches: Results from Phase 1 (schema matching)
            context: Execution context
        
        Returns:
            Dict with:
            - semantic_matches: List of semantic matches with similarity scores
            - enhanced_confidence: Enhanced confidence scores for existing matches
            - suggested_mappings: Suggested mappings for unmapped columns
        """
        self.logger.info(
            f"Matching semantically: source={source_parsed_file_id}, "
            f"target={target_parsed_file_id}"
        )
        
        if not self.semantic_data:
            return {
                "semantic_matches": [],
                "enhanced_confidence": {},
                "suggested_mappings": [],
                "error": "SemanticDataAbstraction not available"
            }
        
        try:
            # Get source semantic embeddings
            source_embeddings = await self.semantic_data.get_semantic_embeddings(
                filter_conditions={"parsed_file_id": source_parsed_file_id},
                limit=None
            )
            
            # Get target semantic embeddings
            target_embeddings = await self.semantic_data.get_semantic_embeddings(
                filter_conditions={"parsed_file_id": target_parsed_file_id},
                limit=None
            )
            
            if not source_embeddings or not target_embeddings:
                return {
                    "semantic_matches": [],
                    "enhanced_confidence": {},
                    "suggested_mappings": [],
                    "error": "Semantic embeddings not found"
                }
            
            # Build column-to-embedding maps
            source_col_map = self._build_column_map(source_embeddings)
            target_col_map = self._build_column_map(target_embeddings)
            
            # Get unmapped columns from Phase 1
            unmapped_source = schema_matches.get("unmapped_source", [])
            unmapped_target = schema_matches.get("unmapped_target", [])
            
            # Phase 2: Semantic matching for unmapped columns
            semantic_matches = []
            suggested_mappings = []
            enhanced_confidence = {}
            
            # For each unmapped source column, find best semantic match
            for source_col in unmapped_source:
                source_emb = source_col_map.get(source_col)
                if not source_emb:
                    continue
                
                best_match = None
                best_score = 0.0
                
                # Try to match against unmapped target columns
                for target_col in unmapped_target:
                    target_emb = target_col_map.get(target_col)
                    if not target_emb:
                        continue
                    
                    # Calculate semantic similarity
                    similarity = self._calculate_semantic_similarity(source_emb, target_emb)
                    
                    if similarity > best_score:
                        best_score = similarity
                        best_match = target_col
                
                # If good match found, add to semantic matches
                if best_match and best_score > 0.6:  # Threshold for semantic match
                    semantic_matches.append({
                        "source_column": source_col,
                        "target_column": best_match,
                        "match_type": "semantic",
                        "confidence": best_score,
                        "semantic_meaning": source_emb.get("semantic_meaning", "")
                    })
                    suggested_mappings.append({
                        "source_column": source_col,
                        "target_column": best_match,
                        "confidence": best_score,
                        "reason": "Semantic similarity"
                    })
            
            # Enhance confidence for existing schema matches using semantic similarity
            exact_matches = schema_matches.get("exact_matches", [])
            for match in exact_matches:
                source_col = match.get("source_column")
                target_col = match.get("target_column")
                
                source_emb = source_col_map.get(source_col)
                target_emb = target_col_map.get(target_col)
                
                if source_emb and target_emb:
                    semantic_sim = self._calculate_semantic_similarity(source_emb, target_emb)
                    # Enhance confidence if semantic similarity confirms match
                    if semantic_sim > 0.7:
                        enhanced_confidence[f"{source_col}->{target_col}"] = min(1.0, match.get("confidence", 0.0) + 0.1)
            
            return {
                "semantic_matches": semantic_matches,
                "enhanced_confidence": enhanced_confidence,
                "suggested_mappings": suggested_mappings
            }
            
        except Exception as e:
            self.logger.error(f"Failed to match semantically: {e}", exc_info=True)
            return {
                "semantic_matches": [],
                "enhanced_confidence": {},
                "suggested_mappings": [],
                "error": str(e)
            }
    
    def _build_column_map(
        self,
        embeddings: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Build map of column name to embedding."""
        col_map = {}
        
        for emb in embeddings:
            column_name = emb.get("column_name")
            if column_name:
                col_map[column_name] = emb
        
        return col_map
    
    def _calculate_semantic_similarity(
        self,
        source_emb: Dict[str, Any],
        target_emb: Dict[str, Any]
    ) -> float:
        """
        Calculate semantic similarity between two embeddings.
        
        Uses cosine similarity on meaning_embedding vectors.
        """
        try:
            # Get meaning embeddings
            source_meaning_emb = source_emb.get("meaning_embedding")
            target_meaning_emb = target_emb.get("meaning_embedding")
            
            if not source_meaning_emb or not target_meaning_emb:
                # Fallback: Use semantic_meaning text similarity
                source_meaning = source_emb.get("semantic_meaning", "")
                target_meaning = target_emb.get("semantic_meaning", "")
                return self._text_similarity(source_meaning, target_meaning)
            
            # Calculate cosine similarity
            import numpy as np
            
            source_vec = np.array(source_meaning_emb)
            target_vec = np.array(target_meaning_emb)
            
            # Cosine similarity
            dot_product = np.dot(source_vec, target_vec)
            norm_source = np.linalg.norm(source_vec)
            norm_target = np.linalg.norm(target_vec)
            
            if norm_source == 0 or norm_target == 0:
                return 0.0
            
            similarity = dot_product / (norm_source * norm_target)
            return float(similarity)
            
        except Exception as e:
            self.logger.debug(f"Failed to calculate semantic similarity: {e}")
            # Fallback to text similarity
            source_meaning = source_emb.get("semantic_meaning", "")
            target_meaning = target_emb.get("semantic_meaning", "")
            return self._text_similarity(source_meaning, target_meaning)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity (Jaccard similarity on words)."""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
