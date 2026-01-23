"""
Schema Matching Service - Phase 1: Schema Alignment

Enabling service for schema matching using deterministic embeddings.

WHAT (Enabling Service Role): I match schemas using deterministic embeddings
HOW (Enabling Service Implementation): I use schema fingerprints for exact matching

ARCHITECTURAL PRINCIPLE: This is Phase 1 of three-phase matching.
- Uses DeterministicComputeAbstraction (governed access)
- Returns exact matches via schema fingerprints
- No business logic - pure matching algorithm
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext


class SchemaMatchingService:
    """
    Schema Matching Service - Phase 1: Schema Alignment.
    
    Matches source and target schemas using deterministic embeddings (schema fingerprints).
    Returns exact matches and similarity scores.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Schema Matching Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Get DeterministicComputeAbstraction (governed access)
        # ARCHITECTURAL PRINCIPLE: Realms use Public Works abstractions, never direct adapters.
        self.deterministic_compute = None
        if public_works:
            self.deterministic_compute = public_works.get_deterministic_compute_abstraction()
            if not self.deterministic_compute:
                self.logger.warning("DeterministicComputeAbstraction not available")
    
    async def match_schemas(
        self,
        source_deterministic_embedding_id: str,
        target_deterministic_embedding_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Match source and target schemas using deterministic embeddings (Phase 1).
        
        ARCHITECTURAL PRINCIPLE: Uses DeterministicComputeAbstraction for governed access.
        
        Args:
            source_deterministic_embedding_id: Source deterministic embedding ID
            target_deterministic_embedding_id: Target deterministic embedding ID
            context: Execution context
        
        Returns:
            Dict with:
            - exact_matches: List of exact column matches
            - similarity_scores: Dict of column similarity scores
            - unmapped_source: List of unmapped source columns
            - unmapped_target: List of unmapped target columns
            - overall_confidence: Overall confidence score (0-1)
        """
        self.logger.info(
            f"Matching schemas: source={source_deterministic_embedding_id}, "
            f"target={target_deterministic_embedding_id}"
        )
        
        if not self.deterministic_compute:
            return {
                "exact_matches": [],
                "similarity_scores": {},
                "unmapped_source": [],
                "unmapped_target": [],
                "overall_confidence": 0.0,
                "error": "DeterministicComputeAbstraction not available"
            }
        
        try:
            # Get source deterministic embedding
            source_embedding = await self.deterministic_compute.get_deterministic_embedding(
                embedding_id=source_deterministic_embedding_id,
                tenant_id=context.tenant_id
            )
            
            if not source_embedding:
                return {
                    "exact_matches": [],
                    "similarity_scores": {},
                    "unmapped_source": [],
                    "unmapped_target": [],
                    "overall_confidence": 0.0,
                    "error": f"Source embedding not found: {source_deterministic_embedding_id}"
                }
            
            # Get target deterministic embedding
            target_embedding = await self.deterministic_compute.get_deterministic_embedding(
                embedding_id=target_deterministic_embedding_id,
                tenant_id=context.tenant_id
            )
            
            if not target_embedding:
                return {
                    "exact_matches": [],
                    "similarity_scores": {},
                    "unmapped_source": [],
                    "unmapped_target": [],
                    "overall_confidence": 0.0,
                    "error": f"Target embedding not found: {target_deterministic_embedding_id}"
                }
            
            # Extract schema fingerprints
            source_fingerprint = source_embedding.get("schema_fingerprint", {})
            target_fingerprint = target_embedding.get("schema_fingerprint", {})
            
            # Extract column information
            source_columns = self._extract_columns(source_fingerprint)
            target_columns = self._extract_columns(target_fingerprint)
            
            # Phase 1: Exact match via fingerprints
            exact_matches = []
            similarity_scores = {}
            mapped_source_cols = set()
            mapped_target_cols = set()
            
            for source_col in source_columns:
                source_col_name = source_col.get("name")
                source_col_type = source_col.get("type")
                source_col_hash = self._hash_column(source_col)
                
                best_match = None
                best_score = 0.0
                
                for target_col in target_columns:
                    target_col_name = target_col.get("name")
                    target_col_type = target_col.get("type")
                    target_col_hash = self._hash_column(target_col)
                    
                    # Exact match (same name, type, position)
                    if source_col_hash == target_col_hash:
                        exact_matches.append({
                            "source_column": source_col_name,
                            "target_column": target_col_name,
                            "match_type": "exact",
                            "confidence": 1.0,
                            "source_type": source_col_type,
                            "target_type": target_col_type
                        })
                        mapped_source_cols.add(source_col_name)
                        mapped_target_cols.add(target_col_name)
                        best_match = target_col_name
                        best_score = 1.0
                        break
                    
                    # Name match (exact column name)
                    elif source_col_name.lower() == target_col_name.lower():
                        score = 0.8 if source_col_type == target_col_type else 0.6
                        if score > best_score:
                            best_match = target_col_name
                            best_score = score
                    
                    # Type match (same type, different name)
                    elif source_col_type == target_col_type:
                        score = 0.5
                        if score > best_score:
                            best_match = target_col_name
                            best_score = score
                
                # Store similarity score if not exact match
                if best_match and best_score < 1.0:
                    similarity_scores[source_col_name] = {
                        "target_column": best_match,
                        "score": best_score,
                        "match_type": "similarity"
                    }
                    mapped_source_cols.add(source_col_name)
                    mapped_target_cols.add(best_match)
            
            # Identify unmapped columns
            unmapped_source = [
                col.get("name") for col in source_columns
                if col.get("name") not in mapped_source_cols
            ]
            unmapped_target = [
                col.get("name") for col in target_columns
                if col.get("name") not in mapped_target_cols
            ]
            
            # Calculate overall confidence
            total_source_cols = len(source_columns)
            total_target_cols = len(target_columns)
            total_mapped = len(exact_matches) + len(similarity_scores)
            max_cols = max(total_source_cols, total_target_cols)
            
            overall_confidence = total_mapped / max_cols if max_cols > 0 else 0.0
            
            return {
                "exact_matches": exact_matches,
                "similarity_scores": similarity_scores,
                "unmapped_source": unmapped_source,
                "unmapped_target": unmapped_target,
                "overall_confidence": overall_confidence,
                "source_columns_count": total_source_cols,
                "target_columns_count": total_target_cols,
                "mapped_count": total_mapped
            }
            
        except Exception as e:
            self.logger.error(f"Failed to match schemas: {e}", exc_info=True)
            return {
                "exact_matches": [],
                "similarity_scores": {},
                "unmapped_source": [],
                "unmapped_target": [],
                "overall_confidence": 0.0,
                "error": str(e)
            }
    
    def _extract_columns(self, schema_fingerprint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract column information from schema fingerprint."""
        if not schema_fingerprint:
            return []
        
        # Schema fingerprint structure: {"columns": [{"name": "...", "type": "...", ...}, ...]}
        columns = schema_fingerprint.get("columns", [])
        
        # If columns is a dict, convert to list
        if isinstance(columns, dict):
            columns = [
                {"name": name, "type": info.get("type", "unknown"), **info}
                for name, info in columns.items()
            ]
        
        return columns
    
    def _hash_column(self, column: Dict[str, Any]) -> str:
        """Generate hash for column (name + type + position)."""
        import hashlib
        
        name = column.get("name", "")
        col_type = column.get("type", "")
        position = column.get("position", "")
        
        hash_input = f"{name}:{col_type}:{position}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
