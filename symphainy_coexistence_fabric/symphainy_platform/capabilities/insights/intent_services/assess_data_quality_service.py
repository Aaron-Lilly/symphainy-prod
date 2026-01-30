"""
Assess Data Quality Service (Platform SDK)

Assesses data quality across parsing, data, and source dimensions.

Contract: docs/intent_contracts/journey_insights_data_quality/intent_assess_data_quality.md
"""

from typing import Dict, Any, List
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class AssessDataQualityService(PlatformIntentService):
    """
    Assess Data Quality Service using Platform SDK.
    
    Assesses data quality across:
    - Parsing quality (did parsing work correctly?)
    - Data quality (is the underlying data good?)
    - Source quality (copybook problems, data format issues)
    """
    
    def __init__(self, service_id: str = "assess_data_quality_service"):
        """Initialize Assess Data Quality Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute assess_data_quality intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with quality assessment results
        """
        self.logger.info(f"Executing assess_data_quality: {ctx.execution_id}")
        
        # Get parameters
        parsed_file_id = ctx.intent.parameters.get("parsed_file_id")
        embedding_id = ctx.intent.parameters.get("embedding_id")
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for quality assessment")
        
        # Get parsed content
        parsed_content = await ctx.platform.get_parsed_file(
            parsed_file_id=parsed_file_id,
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id
        )
        
        if not parsed_content:
            raise ValueError(f"Parsed file not found: {parsed_file_id}")
        
        # Assess parsing quality
        parsing_quality = self._assess_parsing_quality(parsed_content)
        
        # Assess data quality
        data_quality = self._assess_data_quality(parsed_content)
        
        # Assess source quality
        source_quality = self._assess_source_quality(parsed_content)
        
        # Calculate overall confidence
        overall_confidence = (
            parsing_quality["confidence"] * 0.4 +
            data_quality["confidence"] * 0.4 +
            source_quality["confidence"] * 0.2
        )
        
        # Build quality report
        quality_report = {
            "report_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "embedding_id": embedding_id,
            "overall_confidence": overall_confidence,
            "quality_grade": self._calculate_grade(overall_confidence),
            "dimensions": {
                "parsing": parsing_quality,
                "data": data_quality,
                "source": source_quality
            },
            "issues": self._identify_issues(parsing_quality, data_quality, source_quality),
            "recommendations": self._generate_recommendations(overall_confidence),
            "assessed_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Quality assessment complete: {quality_report['quality_grade']}")
        
        return {
            "artifacts": {
                "quality_report": quality_report
            },
            "events": [{
                "type": "data_quality_assessed",
                "event_id": generate_event_id(),
                "quality_grade": quality_report["quality_grade"],
                "overall_confidence": overall_confidence
            }]
        }
    
    def _assess_parsing_quality(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of parsing."""
        # Check for parsing errors
        errors = parsed_content.get("errors", [])
        warnings = parsed_content.get("warnings", [])
        
        # Check completeness
        has_content = bool(parsed_content.get("content"))
        has_structure = bool(parsed_content.get("structure") or parsed_content.get("schema"))
        
        # Calculate confidence
        confidence = 1.0
        if errors:
            confidence -= 0.3 * min(len(errors), 3) / 3
        if warnings:
            confidence -= 0.1 * min(len(warnings), 5) / 5
        if not has_content:
            confidence -= 0.3
        if not has_structure:
            confidence -= 0.2
        
        return {
            "confidence": max(0.0, confidence),
            "errors": len(errors),
            "warnings": len(warnings),
            "has_content": has_content,
            "has_structure": has_structure
        }
    
    def _assess_data_quality(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of underlying data."""
        content = parsed_content.get("content", {})
        
        # Check for null/empty values
        total_fields = 0
        empty_fields = 0
        
        if isinstance(content, dict):
            for key, value in content.items():
                total_fields += 1
                if value is None or value == "" or value == []:
                    empty_fields += 1
        elif isinstance(content, list) and content:
            sample = content[0] if isinstance(content[0], dict) else {}
            total_fields = len(sample)
        
        completeness = 1.0 - (empty_fields / max(total_fields, 1))
        
        return {
            "confidence": completeness,
            "total_fields": total_fields,
            "empty_fields": empty_fields,
            "completeness": completeness
        }
    
    def _assess_source_quality(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Assess quality of source data format."""
        metadata = parsed_content.get("metadata", {})
        
        # Check for format issues
        has_valid_encoding = metadata.get("encoding", "utf-8").lower() in ["utf-8", "ascii", "latin-1"]
        has_valid_format = metadata.get("file_type") in ["csv", "json", "xml", "pdf", "xlsx", "txt"]
        
        confidence = 0.7  # Base confidence
        if has_valid_encoding:
            confidence += 0.15
        if has_valid_format:
            confidence += 0.15
        
        return {
            "confidence": min(1.0, confidence),
            "encoding_valid": has_valid_encoding,
            "format_recognized": has_valid_format
        }
    
    def _calculate_grade(self, confidence: float) -> str:
        """Calculate quality grade from confidence."""
        if confidence >= 0.9:
            return "A"
        elif confidence >= 0.8:
            return "B"
        elif confidence >= 0.7:
            return "C"
        elif confidence >= 0.6:
            return "D"
        else:
            return "F"
    
    def _identify_issues(self, parsing: Dict, data: Dict, source: Dict) -> List[Dict[str, Any]]:
        """Identify issues from quality assessments."""
        issues = []
        
        if parsing["errors"] > 0:
            issues.append({
                "type": "parsing_errors",
                "severity": "high",
                "description": f"Found {parsing['errors']} parsing errors"
            })
        
        if data["completeness"] < 0.8:
            issues.append({
                "type": "incomplete_data",
                "severity": "medium",
                "description": f"Data completeness is {data['completeness']:.0%}"
            })
        
        if not source["encoding_valid"]:
            issues.append({
                "type": "encoding_issue",
                "severity": "low",
                "description": "Non-standard character encoding detected"
            })
        
        return issues
    
    def _generate_recommendations(self, confidence: float) -> List[str]:
        """Generate recommendations based on quality."""
        recommendations = []
        
        if confidence < 0.7:
            recommendations.append("Consider re-parsing the file with different settings")
            recommendations.append("Review source data for formatting issues")
        elif confidence < 0.9:
            recommendations.append("Data is usable but may benefit from cleanup")
        else:
            recommendations.append("Data quality is excellent - ready for analysis")
        
        return recommendations
