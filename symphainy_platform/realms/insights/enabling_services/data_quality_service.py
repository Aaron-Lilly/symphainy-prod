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
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Assess data quality across parsing, data, and source dimensions.
        
        Combines:
        - Parsing results (from Content Realm)
        - Embeddings (from ArangoDB)
        - Source file metadata (from Supabase)
        
        Identifies:
        - Parsing issues (missing fields, format mismatches)
        - Data issues (faded documents, corrupted data)
        - Source issues (copybook mismatches, format problems)
        - Root cause (parsing vs data vs source)
        
        Args:
            parsed_file_id: Parsed file identifier
            source_file_id: Source file identifier
            parser_type: Parser type (e.g., "mainframe", "csv", "json", "pdf")
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with quality assessment results
        """
        self.logger.info(
            f"Assessing data quality: {parsed_file_id} (source: {source_file_id}, "
            f"parser: {parser_type}) for tenant: {tenant_id}"
        )
        
        try:
            # Get parsing results from State Surface
            parsed_data = await self._get_parsed_data(parsed_file_id, context)
            
            # Get embeddings from ArangoDB (if available)
            embeddings = await self._get_embeddings(parsed_file_id, tenant_id, context)
            
            # Get source file metadata from Supabase (if available)
            source_metadata = await self._get_source_metadata(source_file_id, tenant_id, context)
            
            # Assess parsing quality
            parsing_quality = await self._assess_parsing_quality(
                parsed_data, parser_type, source_metadata
            )
            
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
            
            return {
                "quality_assessment": {
                    "overall_quality": overall_quality,
                    "parsing_quality": parsing_quality,
                    "data_quality": data_quality,
                    "source_quality": source_quality,
                    "root_cause_analysis": root_cause
                },
                "parsed_file_id": parsed_file_id,
                "source_file_id": source_file_id,
                "parser_type": parser_type
            }
            
        except Exception as e:
            self.logger.error(f"Failed to assess data quality: {e}", exc_info=True)
            return {
                "quality_assessment": {
                    "overall_quality": "unknown",
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
        # State Surface is accessed via Runtime, not Foundation
        # For now, try to get from context if available
        if hasattr(context, 'state_surface') and context.state_surface:
            try:
                parsed_data = await context.state_surface.retrieve_file(parsed_file_id)
                return parsed_data
            except Exception as e:
                self.logger.debug(f"Could not retrieve parsed data: {e}")
        
        return None
    
    async def _get_embeddings(
        self,
        parsed_file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Optional[List[Dict[str, Any]]]:
        """Get embeddings from ArangoDB."""
        if not self.public_works:
            return None
        
        arango_adapter = self.public_works.get_arango_adapter()
        if not arango_adapter:
            return None
        
        try:
            # Query embeddings collection for this parsed_file_id
            # Note: Embeddings may be stored with different key structure
            # For MVP, we'll check if collection exists and query it
            if await arango_adapter.collection_exists("embeddings"):
                query = """
                FOR e IN embeddings
                FILTER e.parsed_file_id == @parsed_file_id
                RETURN e
                """
                bind_vars = {"parsed_file_id": parsed_file_id}
                
                embeddings = await arango_adapter.execute_aql(query, bind_vars=bind_vars)
                return embeddings if embeddings else None
        except Exception as e:
            self.logger.debug(f"Could not retrieve embeddings: {e}")
        
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
