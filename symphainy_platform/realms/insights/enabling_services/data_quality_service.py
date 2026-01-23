"""
Data Quality Service - Combined Parsing + Embedding Analysis

Enabling service for data quality assessment operations.

WHAT (Enabling Service Role): I assess data quality across parsing, data, and source dimensions
HOW (Enabling Service Implementation): I combine parsing results with embeddings to identify root causes

Key Principle: Pure data processing - combines parsing results with embeddings to identify issues.
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


class DataQualityService:
    """
    Data Quality Service - Combined parsing + embedding analysis.
    
    Assesses data quality across:
    - Parsing quality (did parsing work correctly?)
    - Data quality (is the underlying data good?)
    - Source quality (copybook problems, data format issues)
    
    Uses combined parsing + embedding analysis to identify root causes.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Data Quality Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
    
    async def assess_data_quality(
        self,
        parsed_file_id: str,
        source_file_id: str,
        parser_type: str,
        tenant_id: str,
        context: ExecutionContext,
        deterministic_embedding_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assess data quality across parsing, data, and source dimensions.
        
        Combines:
        - Parsing results (from Content Realm)
        - Deterministic embeddings (for schema/pattern validation)
        - Semantic embeddings (from ArangoDB)
        - Source file metadata (from Supabase)
        
        Calculates:
        - Parsing confidence: Based on parsing quality metrics
        - Embedding confidence: Based on deterministic embedding match quality
        - Overall confidence: (parsing_confidence + embedding_confidence) / 2
        
        Identifies:
        - Bad scan (parsing confidence < threshold)
        - Bad schema (embedding confidence < threshold)
        - Missing fields
        - Invalid data
        
        Args:
            parsed_file_id: Parsed file identifier
            source_file_id: Source file identifier
            parser_type: Parser type (e.g., "mainframe", "csv", "json", "pdf")
            tenant_id: Tenant identifier
            context: Execution context
            deterministic_embedding_id: Optional deterministic embedding ID (for embedding confidence)
        
        Returns:
            Dict with quality assessment results including confidence scores
        """
        self.logger.info(
            f"Assessing data quality: {parsed_file_id} (source: {source_file_id}, "
            f"parser: {parser_type}) for tenant: {tenant_id}"
        )
        
        try:
            # Get parsing results from State Surface
            parsed_data = await self._get_parsed_data(parsed_file_id, context)
            
            # Get deterministic embeddings (for embedding confidence calculation)
            deterministic_embedding = None
            if deterministic_embedding_id:
                deterministic_embedding = await self._get_deterministic_embedding(
                    deterministic_embedding_id, context
                )
            
            # Get semantic embeddings from ArangoDB (if available)
            embeddings = await self._get_embeddings(parsed_file_id, tenant_id, context)
            
            # Get source file metadata from Supabase (if available)
            source_metadata = await self._get_source_metadata(source_file_id, tenant_id, context)
            
            # Assess parsing quality and calculate parsing confidence
            parsing_quality = await self._assess_parsing_quality(
                parsed_data, parser_type, source_metadata
            )
            parsing_confidence = self._calculate_parsing_confidence(parsing_quality)
            
            # Assess embedding quality and calculate embedding confidence
            embedding_quality = await self._assess_embedding_quality(
                parsed_data, deterministic_embedding, embeddings
            )
            embedding_confidence = self._calculate_embedding_confidence(embedding_quality)
            
            # Calculate overall confidence
            overall_confidence = (parsing_confidence + embedding_confidence) / 2.0
            
            # Assess data quality
            data_quality = await self._assess_data_quality(
                parsed_data, embeddings, parser_type
            )
            
            # Assess source quality
            source_quality = await self._assess_source_quality(
                parsed_data, parser_type, source_metadata
            )
            
            # Root cause analysis
            root_cause = await self._analyze_root_cause(
                parsing_quality, data_quality, source_quality
            )
            
            # Determine overall quality
            overall_quality = self._determine_overall_quality(
                parsing_quality, data_quality, source_quality
            )
            
            # Identify issues based on confidence thresholds
            issues = self._identify_confidence_issues(
                parsing_confidence, embedding_confidence, overall_confidence
            )
            
            return {
                "quality_assessment": {
                    "overall_quality": overall_quality,
                    "overall_confidence": overall_confidence,
                    "parsing_confidence": parsing_confidence,
                    "embedding_confidence": embedding_confidence,
                    "parsing_quality": parsing_quality,
                    "embedding_quality": embedding_quality,
                    "data_quality": data_quality,
                    "source_quality": source_quality,
                    "root_cause_analysis": root_cause,
                    "issues": issues
                },
                "parsed_file_id": parsed_file_id,
                "source_file_id": source_file_id,
                "parser_type": parser_type,
                "deterministic_embedding_id": deterministic_embedding_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to assess data quality: {e}", exc_info=True)
            return {
                "quality_assessment": {
                    "overall_quality": "unknown",
                    "overall_confidence": 0.0,
                    "parsing_confidence": 0.0,
                    "embedding_confidence": 0.0,
                    "error": str(e)
                },
                "parsed_file_id": parsed_file_id,
                "source_file_id": source_file_id,
                "parser_type": parser_type
            }
    
    async def _get_parsed_data(
        self,
        parsed_file_id: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """Get parsed data from State Surface."""
        # ARCHITECTURAL PRINCIPLE: Use Content Realm service for file retrieval (governed access)
        # Runtime records reality. Smart City governs access. Realms touch data.
        # Never use state_surface.retrieve_file() - that's an anti-pattern.
        try:
            if not self.public_works:
                self.logger.warning("Public Works not available - cannot retrieve parsed file via Content Realm")
                return None
            
            # Use Content Realm service (governed access)
            from symphainy_platform.realms.content.enabling_services.file_parser_service import FileParserService
            file_parser_service = FileParserService(public_works=self.public_works)
            
            parsed_file = await file_parser_service.get_parsed_file(
                parsed_file_id=parsed_file_id,
                tenant_id=tenant_id,
                context=context
            )
            
            # Return parsed content
            return parsed_file.get("parsed_content")
        except Exception as e:
            self.logger.debug(f"Could not retrieve parsed data via Content Realm: {e}")
            return None
    
    async def _get_embeddings(
        self,
        parsed_file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get embeddings via SemanticDataAbstraction (governed access).
        
        ARCHITECTURAL PRINCIPLE: Realms use Public Works abstractions, never direct adapters.
        """
        if not self.public_works:
            return None
        
        # Use SemanticDataAbstraction (governed access)
        semantic_data = self.public_works.get_semantic_data_abstraction()
        if not semantic_data:
            self.logger.warning("SemanticDataAbstraction not available")
            return None
        
        try:
            # Query embeddings via abstraction
            embeddings = await semantic_data.get_semantic_embeddings(
                filter_conditions={"parsed_file_id": parsed_file_id},
                limit=None
            )
            return embeddings if embeddings else None
        except Exception as e:
            self.logger.debug(f"Could not retrieve embeddings via abstraction: {e}")
            return None
    
    async def _get_source_metadata(
        self,
        source_file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """Get source file metadata from Supabase."""
        # For MVP: Return None (Supabase integration will be added)
        # In full implementation, query Supabase files table
        return None
    
    async def _assess_parsing_quality(
        self,
        parsed_data: Optional[Dict[str, Any]],
        parser_type: str,
        source_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess parsing quality.
        
        Checks:
        - Parsing errors
        - Missing fields
        - Unexpected formats
        - Parser configuration issues
        """
        if not parsed_data:
            return {
                "status": "failed",
                "issues": [
                    {
                        "type": "no_parsed_data",
                        "description": "No parsed data available",
                        "severity": "high",
                        "suggestion": "Check if parsing completed successfully"
                    }
                ],
                "suggestions": []
            }
        
        issues = []
        suggestions = []
        
        # Check for parsing errors
        if "error" in parsed_data:
            issues.append({
                "type": "parsing_error",
                "description": parsed_data.get("error", "Unknown parsing error"),
                "severity": "high",
                "suggestion": "Review parser configuration or source file format"
            })
        
        # Check for missing expected fields (parser-specific)
        if parser_type == "mainframe":
            # For mainframe, check for expected COBOL fields
            if "records" in parsed_data:
                records = parsed_data["records"]
                if records and len(records) > 0:
                    # Check first record for expected fields
                    first_record = records[0]
                    # This is a simplified check - full implementation would validate
                    # against copybook structure
                    if not first_record or len(first_record) == 0:
                        issues.append({
                            "type": "empty_records",
                            "description": "Parsed records are empty",
                            "severity": "high",
                            "suggestion": "Check copybook definition or source data format"
                        })
        
        # Determine status
        if issues:
            status = "issues" if any(i.get("severity") == "high" for i in issues) else "warnings"
        else:
            status = "good"
        
        return {
            "status": status,
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def _assess_data_quality(
        self,
        parsed_data: Optional[Dict[str, Any]],
        embeddings: Optional[List[Dict[str, Any]]],
        parser_type: str
    ) -> Dict[str, Any]:
        """
        Assess data quality.
        
        Checks:
        - Data anomalies
        - Completeness
        - Consistency
        - Validity
        - Faded documents (via embeddings)
        - Corrupted data
        """
        issues = []
        suggestions = []
        
        if not parsed_data:
            return {
                "status": "poor",
                "issues": [
                    {
                        "type": "no_data",
                        "description": "No data available for assessment",
                        "severity": "high",
                        "suggestion": "Ensure parsing completed successfully"
                    }
                ],
                "suggestions": []
            }
        
        # Check for data completeness
        if "records" in parsed_data:
            records = parsed_data["records"]
            if not records or len(records) == 0:
                issues.append({
                    "type": "no_records",
                    "description": "No records found in parsed data",
                    "severity": "high",
                    "suggestion": "Check source file or parser configuration"
                })
        
        # Use embeddings to detect semantic anomalies
        if embeddings:
            # Check embedding confidence scores (if available)
            low_confidence_embeddings = [
                e for e in embeddings
                if e.get("confidence", 1.0) < 0.7
            ]
            
            if low_confidence_embeddings:
                issues.append({
                    "type": "low_confidence_embeddings",
                    "description": f"{len(low_confidence_embeddings)} embeddings have low confidence scores",
                    "severity": "medium",
                    "suggestion": "Source data may be faded or hard to read. Consider rescanning or using higher quality source."
                })
        
        # Determine status
        if issues:
            status = "poor" if any(i.get("severity") == "high" for i in issues) else "issues"
        else:
            status = "good"
        
        return {
            "status": status,
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def _assess_source_quality(
        self,
        parsed_data: Optional[Dict[str, Any]],
        parser_type: str,
        source_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess source quality.
        
        Checks:
        - Copybook mismatches (for mainframe)
        - Format issues
        - Structure problems
        """
        issues = []
        suggestions = []
        
        if parser_type == "mainframe":
            # For mainframe, check for copybook-related issues
            if parsed_data and "copybook_issues" in parsed_data:
                copybook_issues = parsed_data["copybook_issues"]
                if copybook_issues:
                    issues.append({
                        "type": "copybook_mismatch",
                        "description": "Copybook definition doesn't match data structure",
                        "severity": "high",
                        "suggestion": "Review copybook or source data format"
                    })
        
        # Determine status
        if issues:
            status = "poor" if any(i.get("severity") == "high" for i in issues) else "issues"
        else:
            status = "good"
        
        return {
            "status": status,
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def _analyze_root_cause(
        self,
        parsing_quality: Dict[str, Any],
        data_quality: Dict[str, Any],
        source_quality: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze root cause of issues.
        
        Determines primary issue type (parsing vs data vs source) and confidence.
        """
        # Count high-severity issues by type
        parsing_high = sum(
            1 for i in parsing_quality.get("issues", [])
            if i.get("severity") == "high"
        )
        data_high = sum(
            1 for i in data_quality.get("issues", [])
            if i.get("severity") == "high"
        )
        source_high = sum(
            1 for i in source_quality.get("issues", [])
            if i.get("severity") == "high"
        )
        
        # Determine primary issue
        if parsing_high > data_high and parsing_high > source_high:
            primary_issue = "parsing"
            confidence = min(0.95, 0.5 + (parsing_high * 0.15))
        elif data_high > source_high:
            primary_issue = "data"
            confidence = min(0.95, 0.5 + (data_high * 0.15))
        elif source_high > 0:
            primary_issue = "source"
            confidence = min(0.95, 0.5 + (source_high * 0.15))
        else:
            primary_issue = "none"
            confidence = 0.9
        
        # Generate recommendations
        recommendations = []
        
        if primary_issue == "parsing":
            recommendations.append("Review parser configuration")
            recommendations.append("Check parser compatibility with source file format")
        elif primary_issue == "data":
            recommendations.append("Check source data quality")
            recommendations.append("Consider rescanning or using higher quality source")
        elif primary_issue == "source":
            recommendations.append("Review source file format")
            recommendations.append("Check copybook definition (for mainframe files)")
        
        return {
            "primary_issue": primary_issue,
            "confidence": confidence,
            "recommendations": recommendations
        }
    
    def _determine_overall_quality(
        self,
        parsing_quality: Dict[str, Any],
        data_quality: Dict[str, Any],
        source_quality: Dict[str, Any]
    ) -> str:
        """Determine overall quality from individual assessments."""
        parsing_status = parsing_quality.get("status", "unknown")
        data_status = data_quality.get("status", "unknown")
        source_status = source_quality.get("status", "unknown")
        
        # If any dimension is "poor" or "failed", overall is "poor"
        if parsing_status in ["poor", "failed"] or \
           data_status in ["poor", "failed"] or \
           source_status in ["poor", "failed"]:
            return "poor"
        
        # If any dimension has "issues", overall is "fair"
        if parsing_status == "issues" or \
           data_status == "issues" or \
           source_status == "issues":
            return "fair"
        
        # If all are "good", overall is "good"
        if parsing_status == "good" and \
           data_status == "good" and \
           source_status == "good":
            return "good"
        
        return "unknown"
    
    async def _get_deterministic_embedding(
        self,
        deterministic_embedding_id: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """Get deterministic embedding from ArangoDB."""
        if not self.public_works:
            return None
        
        # Use DeterministicComputeAbstraction (governed access)
        # ARCHITECTURAL PRINCIPLE: Realms use Public Works abstractions, never direct adapters.
        deterministic_compute = self.public_works.get_deterministic_compute_abstraction()
        if not deterministic_compute:
            self.logger.warning("DeterministicComputeAbstraction not available")
            return None
        
        try:
            # Get deterministic embedding via abstraction
            embedding = await deterministic_compute.get_deterministic_embedding(
                embedding_id=deterministic_embedding_id,
                tenant_id=tenant_id
            )
            
            if embedding:
                # Convert to expected format
                document = {
                    "_key": embedding.get("embedding_id"),
                    "parsed_file_id": embedding.get("parsed_file_id"),
                    "schema_fingerprint": embedding.get("schema_fingerprint"),
                    "pattern_signature": embedding.get("pattern_signature")
                }
                return document
            else:
                return None
        except Exception as e:
            self.logger.debug(f"Could not retrieve deterministic embedding via abstraction: {e}")
            return None
    
    async def _assess_embedding_quality(
        self,
        parsed_data: Optional[Dict[str, Any]],
        deterministic_embedding: Optional[Dict[str, Any]],
        embeddings: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Assess embedding quality using deterministic embeddings.
        
        Checks:
        - Schema fingerprint match quality
        - Pattern signature match quality
        - Missing fields detection
        """
        issues = []
        
        if not deterministic_embedding:
            return {
                "status": "unknown",
                "issues": [
                    {
                        "type": "no_deterministic_embedding",
                        "description": "No deterministic embedding available for validation",
                        "severity": "medium",
                        "suggestion": "Create deterministic embeddings first"
                    }
                ]
            }
        
        if not parsed_data:
            return {
                "status": "unknown",
                "issues": [
                    {
                        "type": "no_parsed_data",
                        "description": "No parsed data available for comparison",
                        "severity": "high"
                    }
                ]
            }
        
        # Extract schema from parsed data
        parsed_schema = self._extract_schema_from_parsed_data(parsed_data)
        deterministic_schema = deterministic_embedding.get("schema", [])
        
        # Check schema match
        schema_match = self._compare_schemas(parsed_schema, deterministic_schema)
        
        if not schema_match["exact_match"]:
            issues.append({
                "type": "schema_mismatch",
                "description": f"Schema mismatch: {schema_match.get('differences', [])}",
                "severity": "high",
                "suggestion": "Review schema definition or source data format"
            })
        
        # Check pattern signature match
        pattern_signature = deterministic_embedding.get("pattern_signature", {})
        if pattern_signature:
            pattern_match = self._validate_pattern_signature(parsed_data, pattern_signature)
            if not pattern_match["valid"]:
                issues.append({
                    "type": "pattern_mismatch",
                    "description": pattern_match.get("description", "Pattern signature validation failed"),
                    "severity": "medium",
                    "suggestion": "Data patterns may have changed or source data format differs"
                })
        
        # Check for missing fields
        missing_fields = self._detect_missing_fields(parsed_schema, deterministic_schema)
        if missing_fields:
            issues.append({
                "type": "missing_fields",
                "description": f"Missing fields: {', '.join(missing_fields)}",
                "severity": "high",
                "suggestion": "Check source data or schema definition"
            })
        
        status = "good" if not issues else ("issues" if not any(i.get("severity") == "high" for i in issues) else "poor")
        
        return {
            "status": status,
            "issues": issues,
            "schema_match": schema_match,
            "pattern_match": pattern_match if pattern_signature else None
        }
    
    def _extract_schema_from_parsed_data(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract schema from parsed data."""
        schema = []
        
        metadata = parsed_data.get("metadata", {})
        columns = metadata.get("columns", [])
        
        if columns:
            for idx, col in enumerate(columns):
                schema.append({
                    "name": col.get("name", f"column_{idx}"),
                    "type": col.get("type", "unknown"),
                    "position": idx
                })
        else:
            # Try to infer from data
            data = parsed_data.get("data", [])
            if isinstance(data, list) and len(data) > 0:
                first_row = data[0]
                if isinstance(first_row, dict):
                    for idx, (key, value) in enumerate(first_row.items()):
                        schema.append({
                            "name": key,
                            "type": type(value).__name__,
                            "position": idx
                        })
        
        return schema
    
    def _compare_schemas(
        self,
        parsed_schema: List[Dict[str, Any]],
        deterministic_schema: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare parsed schema with deterministic schema."""
        parsed_cols = {col["name"].lower(): col for col in parsed_schema}
        det_cols = {col["name"].lower(): col for col in deterministic_schema}
        
        exact_match = parsed_cols == det_cols
        
        differences = []
        if not exact_match:
            missing_in_parsed = set(det_cols.keys()) - set(parsed_cols.keys())
            missing_in_det = set(parsed_cols.keys()) - set(det_cols.keys())
            
            if missing_in_parsed:
                differences.append(f"Missing in parsed: {', '.join(missing_in_parsed)}")
            if missing_in_det:
                differences.append(f"Extra in parsed: {', '.join(missing_in_det)}")
        
        return {
            "exact_match": exact_match,
            "differences": differences
        }
    
    def _validate_pattern_signature(
        self,
        parsed_data: Dict[str, Any],
        pattern_signature: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate parsed data against pattern signature."""
        # Simplified validation - check if data types match
        data = parsed_data.get("data", [])
        if not data:
            return {"valid": False, "description": "No data to validate"}
        
        # Basic validation: check if we have data for expected columns
        first_row = data[0] if isinstance(data, list) else {}
        expected_cols = set(pattern_signature.keys())
        actual_cols = set(first_row.keys()) if isinstance(first_row, dict) else set()
        
        if expected_cols - actual_cols:
            return {
                "valid": False,
                "description": f"Missing columns in data: {', '.join(expected_cols - actual_cols)}"
            }
        
        return {"valid": True}
    
    def _detect_missing_fields(
        self,
        parsed_schema: List[Dict[str, Any]],
        deterministic_schema: List[Dict[str, Any]]
    ) -> List[str]:
        """Detect fields that are in deterministic schema but missing in parsed schema."""
        parsed_cols = {col["name"].lower() for col in parsed_schema}
        det_cols = {col["name"].lower() for col in deterministic_schema}
        
        missing = det_cols - parsed_cols
        return list(missing)
    
    def _calculate_parsing_confidence(self, parsing_quality: Dict[str, Any]) -> float:
        """Calculate parsing confidence score (0.0-1.0)."""
        status = parsing_quality.get("status", "unknown")
        issues = parsing_quality.get("issues", [])
        
        if status == "good":
            return 0.95
        elif status == "issues":
            # Reduce confidence based on number of issues
            high_severity_count = sum(1 for i in issues if i.get("severity") == "high")
            medium_severity_count = sum(1 for i in issues if i.get("severity") == "medium")
            
            confidence = 0.7 - (high_severity_count * 0.2) - (medium_severity_count * 0.1)
            return max(0.0, confidence)
        elif status in ["poor", "failed"]:
            return 0.3
        else:
            return 0.5
    
    def _calculate_embedding_confidence(self, embedding_quality: Dict[str, Any]) -> float:
        """Calculate embedding confidence score (0.0-1.0)."""
        status = embedding_quality.get("status", "unknown")
        issues = embedding_quality.get("issues", [])
        schema_match = embedding_quality.get("schema_match", {})
        
        if status == "good" and schema_match.get("exact_match", False):
            return 0.95
        elif status == "issues":
            # Reduce confidence based on issues
            high_severity_count = sum(1 for i in issues if i.get("severity") == "high")
            medium_severity_count = sum(1 for i in issues if i.get("severity") == "medium")
            
            # Schema match quality
            schema_bonus = 0.3 if schema_match.get("exact_match", False) else 0.0
            
            confidence = 0.6 + schema_bonus - (high_severity_count * 0.2) - (medium_severity_count * 0.1)
            return max(0.0, min(1.0, confidence))
        elif status == "poor":
            return 0.3
        else:
            return 0.5
    
    def _identify_confidence_issues(
        self,
        parsing_confidence: float,
        embedding_confidence: float,
        overall_confidence: float
    ) -> List[Dict[str, Any]]:
        """Identify issues based on confidence thresholds."""
        issues = []
        threshold = 0.7  # Confidence threshold
        
        if parsing_confidence < threshold:
            issues.append({
                "type": "bad_scan",
                "description": f"Parsing confidence is low ({parsing_confidence:.2f})",
                "severity": "high",
                "suggestion": "Review parser configuration or source file format"
            })
        
        if embedding_confidence < threshold:
            issues.append({
                "type": "bad_schema",
                "description": f"Embedding confidence is low ({embedding_confidence:.2f})",
                "severity": "high",
                "suggestion": "Review schema definition or create new deterministic embeddings"
            })
        
        return issues