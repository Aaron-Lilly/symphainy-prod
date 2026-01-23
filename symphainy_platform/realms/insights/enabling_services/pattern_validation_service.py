"""
Pattern Validation Service - Phase 3: Pattern Validation

Enabling service for validating data pattern compatibility.

WHAT (Enabling Service Role): I validate data patterns match expected patterns
HOW (Enabling Service Implementation): I use pattern signatures to validate compatibility

ARCHITECTURAL PRINCIPLE: This is Phase 3 of three-phase matching.
- Uses DeterministicComputeAbstraction (governed access)
- Returns validation results and warnings
- No business logic - pure validation algorithm
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger
from symphainy_platform.runtime.execution_context import ExecutionContext


class PatternValidationService:
    """
    Pattern Validation Service - Phase 3: Pattern Validation.
    
    Validates that data patterns match expected patterns.
    Checks value ranges, formats, distributions for compatibility.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Pattern Validation Service.
        
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
    
    async def validate_patterns(
        self,
        source_deterministic_embedding_id: str,
        target_deterministic_embedding_id: str,
        mappings: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Validate data patterns match expected patterns (Phase 3).
        
        ARCHITECTURAL PRINCIPLE: Uses DeterministicComputeAbstraction for governed access.
        
        Args:
            source_deterministic_embedding_id: Source deterministic embedding ID
            target_deterministic_embedding_id: Target deterministic embedding ID
            mappings: Combined results from Phase 1 and Phase 2
            context: Execution context
        
        Returns:
            Dict with:
            - validated_mappings: List of validated mappings
            - warnings: List of warnings (pattern mismatches)
            - errors: List of errors (incompatible patterns)
            - validation_scores: Dict of validation scores per mapping
        """
        self.logger.info(
            f"Validating patterns: source={source_deterministic_embedding_id}, "
            f"target={target_deterministic_embedding_id}"
        )
        
        if not self.deterministic_compute:
            return {
                "validated_mappings": [],
                "warnings": [],
                "errors": [],
                "validation_scores": {},
                "error": "DeterministicComputeAbstraction not available"
            }
        
        try:
            # Get source deterministic embedding
            source_embedding = await self.deterministic_compute.get_deterministic_embedding(
                embedding_id=source_deterministic_embedding_id,
                tenant_id=context.tenant_id
            )
            
            # Get target deterministic embedding
            target_embedding = await self.deterministic_compute.get_deterministic_embedding(
                embedding_id=target_deterministic_embedding_id,
                tenant_id=context.tenant_id
            )
            
            if not source_embedding or not target_embedding:
                return {
                    "validated_mappings": [],
                    "warnings": [],
                    "errors": [],
                    "validation_scores": {},
                    "error": "Deterministic embeddings not found"
                }
            
            # Extract pattern signatures
            source_pattern = source_embedding.get("pattern_signature", {})
            target_pattern = target_embedding.get("pattern_signature", {})
            
            # Get all mappings (exact + semantic)
            all_mappings = []
            exact_matches = mappings.get("exact_matches", [])
            semantic_matches = mappings.get("semantic_matches", [])
            
            all_mappings.extend(exact_matches)
            all_mappings.extend(semantic_matches)
            
            # Validate each mapping
            validated_mappings = []
            warnings = []
            errors = []
            validation_scores = {}
            
            for mapping in all_mappings:
                source_col = mapping.get("source_column")
                target_col = mapping.get("target_column")
                
                # Get pattern signatures for these columns
                source_col_pattern = source_pattern.get(source_col, {})
                target_col_pattern = target_pattern.get(target_col, {})
                
                # Validate pattern compatibility
                validation_result = self._validate_column_patterns(
                    source_col, target_col,
                    source_col_pattern, target_col_pattern
                )
                
                validation_score = validation_result.get("score", 0.0)
                validation_scores[f"{source_col}->{target_col}"] = validation_score
                
                # Add warnings/errors
                if validation_result.get("warnings"):
                    warnings.extend(validation_result["warnings"])
                
                if validation_result.get("errors"):
                    errors.extend(validation_result["errors"])
                
                # Add to validated mappings if score is acceptable
                if validation_score >= 0.5:  # Threshold for acceptable pattern match
                    validated_mapping = mapping.copy()
                    validated_mapping["pattern_validation_score"] = validation_score
                    validated_mapping["pattern_validated"] = True
                    validated_mappings.append(validated_mapping)
                else:
                    # Low score - add warning
                    warnings.append({
                        "mapping": f"{source_col}->{target_col}",
                        "message": f"Pattern validation score too low: {validation_score}",
                        "severity": "warning"
                    })
            
            return {
                "validated_mappings": validated_mappings,
                "warnings": warnings,
                "errors": errors,
                "validation_scores": validation_scores,
                "total_validated": len(validated_mappings),
                "total_warnings": len(warnings),
                "total_errors": len(errors)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate patterns: {e}", exc_info=True)
            return {
                "validated_mappings": [],
                "warnings": [],
                "errors": [],
                "validation_scores": {},
                "error": str(e)
            }
    
    def _validate_column_patterns(
        self,
        source_col: str,
        target_col: str,
        source_pattern: Dict[str, Any],
        target_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate pattern compatibility between source and target columns.
        
        Returns:
            Dict with score, warnings, errors
        """
        if not source_pattern or not target_pattern:
            return {
                "score": 0.5,  # Neutral score if patterns not available
                "warnings": [f"Pattern signatures not available for {source_col} or {target_col}"],
                "errors": []
            }
        
        score = 1.0
        warnings = []
        errors = []
        
        # Check value ranges
        source_min = source_pattern.get("min_value")
        source_max = source_pattern.get("max_value")
        target_min = target_pattern.get("min_value")
        target_max = target_pattern.get("max_value")
        
        if source_min is not None and target_min is not None:
            if source_min < target_min:
                warnings.append({
                    "column": source_col,
                    "message": f"Source min value ({source_min}) < target min value ({target_min})",
                    "severity": "warning"
                })
                score -= 0.1
        
        if source_max is not None and target_max is not None:
            if source_max > target_max:
                errors.append({
                    "column": source_col,
                    "message": f"Source max value ({source_max}) > target max value ({target_max}) - data may overflow",
                    "severity": "error"
                })
                score -= 0.3
        
        # Check data types
        source_type = source_pattern.get("data_type")
        target_type = target_pattern.get("data_type")
        
        if source_type and target_type:
            if not self._are_types_compatible(source_type, target_type):
                errors.append({
                    "column": source_col,
                    "message": f"Incompatible types: source={source_type}, target={target_type}",
                    "severity": "error"
                })
                score -= 0.5
        
        # Check format patterns
        source_format = source_pattern.get("format_pattern")
        target_format = target_pattern.get("format_pattern")
        
        if source_format and target_format:
            if source_format != target_format:
                warnings.append({
                    "column": source_col,
                    "message": f"Format mismatch: source={source_format}, target={target_format}",
                    "severity": "warning"
                })
                score -= 0.1
        
        # Check null ratios
        source_null_ratio = source_pattern.get("null_ratio", 0.0)
        target_null_ratio = target_pattern.get("null_ratio", 0.0)
        
        if source_null_ratio > target_null_ratio + 0.1:  # 10% tolerance
            warnings.append({
                "column": source_col,
                "message": f"Source has higher null ratio ({source_null_ratio}) than target ({target_null_ratio})",
                "severity": "warning"
            })
            score -= 0.05
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        return {
            "score": score,
            "warnings": warnings,
            "errors": errors
        }
    
    def _are_types_compatible(self, source_type: str, target_type: str) -> bool:
        """Check if data types are compatible."""
        # Type compatibility matrix
        compatible_types = {
            "string": ["varchar", "text", "char"],
            "integer": ["int", "bigint", "smallint"],
            "decimal": ["float", "double", "numeric", "money"],
            "date": ["datetime", "timestamp"],
            "boolean": ["bool", "bit"]
        }
        
        source_lower = source_type.lower()
        target_lower = target_type.lower()
        
        # Exact match
        if source_lower == target_lower:
            return True
        
        # Check compatibility groups
        for group in compatible_types.values():
            if source_lower in group and target_lower in group:
                return True
        
        return False
