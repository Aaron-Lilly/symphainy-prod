"""
Assess Data Quality Intent Service

Implements the assess_data_quality intent for the Insights Realm.

Contract: docs/intent_contracts/journey_insights_data_quality/intent_assess_data_quality.md

Purpose: Assess data quality across parsing, data, and source dimensions. Combines
parsing results with embeddings to identify root causes and calculate confidence scores.

WHAT (Intent Service Role): I assess data quality across multiple dimensions
HOW (Intent Service Implementation): I execute the assess_data_quality intent,
    analyze parsing and embedding quality, and return quality assessment results

Naming Convention:
- Realm: Insights Realm
- Artifacts: insights_quality_report
- Solution = platform construct (InsightsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class AssessDataQualityService(BaseIntentService):
    """
    Intent service for data quality assessment.
    
    Assesses data quality across:
    - Parsing quality (did parsing work correctly?)
    - Data quality (is the underlying data good?)
    - Source quality (copybook problems, data format issues)
    
    Contract Compliance:
    - Parameters: Section 2 of intent contract
    - Returns: Section 3 of intent contract
    - Idempotency: Section 5 of intent contract
    - Error Handling: Section 8 of intent contract
    """
    
    def __init__(self, public_works, state_surface):
        """
        Initialize AssessDataQualityService.
        
        Args:
            public_works: Public Works Foundation Service for infrastructure access
            state_surface: State Surface for state management
        """
        super().__init__(
            service_id="assess_data_quality_service",
            intent_type="assess_data_quality",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the assess_data_quality intent.
        
        Intent Flow (from contract):
        1. Validate required parameters
        2. Get parsed data from state
        3. Get deterministic embeddings (if available)
        4. Assess parsing quality and calculate confidence
        5. Assess embedding quality and calculate confidence
        6. Calculate overall confidence
        7. Identify issues and root causes
        8. Return quality assessment report
        
        Args:
            context: Execution context with intent, tenant, session information
            params: Optional additional parameters (merged with intent.parameters)
        
        Returns:
            Dictionary with artifacts and events per contract Section 3
        """
        await self.record_telemetry(
            telemetry_data={
                "action": "execute",
                "status": "started",
                "execution_id": context.execution_id,
                "intent_type": self.intent_type
            },
            tenant_id=context.tenant_id
        )
        
        try:
            # Get intent parameters
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            # Required parameters
            parsed_file_id = intent_params.get("parsed_file_id")
            if not parsed_file_id:
                raise ValueError("parsed_file_id is required for quality assessment")
            
            source_file_id = intent_params.get("source_file_id", parsed_file_id)
            parser_type = intent_params.get("parser_type", "unknown")
            deterministic_embedding_id = intent_params.get("deterministic_embedding_id")
            
            # === GET PARSED DATA ===
            parsed_data = await self._get_parsed_data(parsed_file_id, context)
            
            # === GET DETERMINISTIC EMBEDDINGS (if available) ===
            embedding_data = None
            if deterministic_embedding_id:
                embedding_data = await self._get_embedding_data(
                    deterministic_embedding_id, context
                )
            
            # === ASSESS PARSING QUALITY ===
            parsing_quality = await self._assess_parsing_quality(
                parsed_data, parser_type
            )
            parsing_confidence = self._calculate_confidence(parsing_quality)
            
            # === ASSESS EMBEDDING QUALITY ===
            embedding_quality = await self._assess_embedding_quality(
                parsed_data, embedding_data
            )
            embedding_confidence = self._calculate_confidence(embedding_quality)
            
            # === CALCULATE OVERALL CONFIDENCE ===
            overall_confidence = (parsing_confidence + embedding_confidence) / 2.0
            
            # === ASSESS DATA QUALITY ===
            data_quality = await self._assess_data_quality(parsed_data, parser_type)
            
            # === IDENTIFY ISSUES ===
            issues = self._identify_issues(
                parsing_confidence, embedding_confidence, overall_confidence
            )
            
            # === ROOT CAUSE ANALYSIS ===
            root_cause = self._analyze_root_cause(parsing_quality, data_quality, issues)
            
            # === GENERATE RECOMMENDATIONS ===
            recommendations = self._generate_recommendations(issues, root_cause)
            
            # === BUILD QUALITY REPORT ===
            report_id = f"quality_report_{generate_event_id()}"
            
            quality_report = {
                "report_id": report_id,
                "parsed_file_id": parsed_file_id,
                "source_file_id": source_file_id,
                "parser_type": parser_type,
                "confidence_scores": {
                    "parsing_confidence": round(parsing_confidence, 3),
                    "embedding_confidence": round(embedding_confidence, 3),
                    "overall_confidence": round(overall_confidence, 3)
                },
                "quality_assessment": {
                    "parsing_quality": parsing_quality,
                    "embedding_quality": embedding_quality,
                    "data_quality": data_quality
                },
                "issues": issues,
                "root_cause": root_cause,
                "recommendations": recommendations,
                "assessed_at": datetime.utcnow().isoformat()
            }
            
            # === STORE IN ARTIFACT PLANE (if available) ===
            artifact_id = None
            if self.public_works:
                try:
                    artifact_plane = self.public_works.get_artifact_plane()
                    if artifact_plane:
                        artifact_result = await artifact_plane.create_artifact(
                            artifact_type="quality_report",
                            content=quality_report,
                            metadata={
                                "parsed_file_id": parsed_file_id,
                                "overall_confidence": overall_confidence,
                                "issues_count": len(issues)
                            },
                            tenant_id=context.tenant_id,
                            include_payload=True
                        )
                        artifact_id = artifact_result.get("artifact_id")
                except Exception as e:
                    self.logger.warning(f"Could not store in Artifact Plane: {e}")
            
            self.logger.info(f"Quality assessed: {report_id} (confidence: {overall_confidence:.2f})")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "report_id": report_id,
                    "overall_confidence": overall_confidence
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "quality_report": quality_report,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "data_quality_assessed",
                        "report_id": report_id,
                        "parsed_file_id": parsed_file_id,
                        "overall_confidence": overall_confidence
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "failed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "error": str(e)
                },
                tenant_id=context.tenant_id
            )
            raise
    
    async def _get_parsed_data(
        self,
        parsed_file_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Get parsed data from state surface or artifact plane."""
        # Try state surface first
        if context.state_surface:
            try:
                parsed_data = await context.state_surface.get_execution_state(
                    key=f"parsed_file_{parsed_file_id}",
                    tenant_id=context.tenant_id
                )
                if parsed_data:
                    return parsed_data
            except Exception:
                pass
        
        # Try artifact plane
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    artifact = await artifact_plane.get_artifact(
                        artifact_id=parsed_file_id,
                        tenant_id=context.tenant_id
                    )
                    if artifact:
                        return artifact.get("content", {})
            except Exception:
                pass
        
        # Return placeholder if not found
        return {
            "parsed_file_id": parsed_file_id,
            "status": "not_found",
            "records": [],
            "schema": {}
        }
    
    async def _get_embedding_data(
        self,
        embedding_id: str,
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """Get embedding data from artifact plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    embedding = await artifact_plane.get_artifact(
                        artifact_id=embedding_id,
                        tenant_id=context.tenant_id
                    )
                    return embedding
            except Exception:
                pass
        return None
    
    async def _assess_parsing_quality(
        self,
        parsed_data: Dict[str, Any],
        parser_type: str
    ) -> Dict[str, Any]:
        """Assess parsing quality."""
        records = parsed_data.get("records", [])
        schema = parsed_data.get("schema", {})
        errors = parsed_data.get("parsing_errors", [])
        
        total_records = len(records)
        error_count = len(errors)
        
        # Calculate metrics
        success_rate = ((total_records - error_count) / max(total_records, 1)) * 100
        schema_completeness = len(schema) / max(10, len(schema)) * 100  # Assume 10 expected fields
        
        return {
            "total_records": total_records,
            "error_count": error_count,
            "success_rate": round(success_rate, 1),
            "schema_completeness": round(schema_completeness, 1),
            "parser_type": parser_type,
            "status": "good" if success_rate > 90 else "poor" if success_rate < 70 else "moderate"
        }
    
    async def _assess_embedding_quality(
        self,
        parsed_data: Dict[str, Any],
        embedding_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess embedding quality."""
        if not embedding_data:
            return {
                "has_embedding": False,
                "match_quality": 0.0,
                "coverage": 0.0,
                "status": "no_embedding"
            }
        
        # Assess match quality between parsed data and embedding
        embedding_fields = embedding_data.get("schema", {}).keys() if isinstance(embedding_data.get("schema"), dict) else []
        parsed_fields = parsed_data.get("schema", {}).keys() if isinstance(parsed_data.get("schema"), dict) else []
        
        common_fields = set(embedding_fields) & set(parsed_fields)
        coverage = len(common_fields) / max(len(embedding_fields), 1) * 100
        
        return {
            "has_embedding": True,
            "match_quality": round(coverage, 1),
            "coverage": round(coverage, 1),
            "common_fields": len(common_fields),
            "status": "good" if coverage > 80 else "poor" if coverage < 50 else "moderate"
        }
    
    async def _assess_data_quality(
        self,
        parsed_data: Dict[str, Any],
        parser_type: str
    ) -> Dict[str, Any]:
        """Assess overall data quality."""
        records = parsed_data.get("records", [])
        
        # Calculate data quality metrics
        null_count = 0
        total_fields = 0
        
        for record in records[:100]:  # Sample first 100 records
            if isinstance(record, dict):
                for value in record.values():
                    total_fields += 1
                    if value is None or value == "" or value == "NULL":
                        null_count += 1
        
        completeness = ((total_fields - null_count) / max(total_fields, 1)) * 100
        
        return {
            "completeness": round(completeness, 1),
            "sample_size": min(len(records), 100),
            "null_count": null_count,
            "total_fields": total_fields,
            "status": "good" if completeness > 90 else "poor" if completeness < 70 else "moderate"
        }
    
    def _calculate_confidence(self, quality: Dict[str, Any]) -> float:
        """Calculate confidence score from quality assessment."""
        status = quality.get("status", "unknown")
        
        if status == "good":
            return 0.9
        elif status == "moderate":
            return 0.7
        elif status == "poor":
            return 0.4
        elif status == "no_embedding":
            return 0.5  # Neutral when no embedding
        else:
            return 0.5
    
    def _identify_issues(
        self,
        parsing_confidence: float,
        embedding_confidence: float,
        overall_confidence: float
    ) -> list:
        """Identify quality issues based on confidence scores."""
        issues = []
        
        if parsing_confidence < 0.7:
            issues.append({
                "type": "parsing_issue",
                "severity": "high" if parsing_confidence < 0.5 else "medium",
                "description": "Parsing quality below acceptable threshold"
            })
        
        if embedding_confidence < 0.7:
            issues.append({
                "type": "embedding_issue",
                "severity": "high" if embedding_confidence < 0.5 else "medium",
                "description": "Embedding match quality below acceptable threshold"
            })
        
        if overall_confidence < 0.6:
            issues.append({
                "type": "overall_quality",
                "severity": "high",
                "description": "Overall data quality requires attention"
            })
        
        return issues
    
    def _analyze_root_cause(
        self,
        parsing_quality: Dict[str, Any],
        data_quality: Dict[str, Any],
        issues: list
    ) -> Dict[str, Any]:
        """Analyze root cause of quality issues."""
        if not issues:
            return {"status": "no_issues", "causes": []}
        
        causes = []
        
        if parsing_quality.get("error_count", 0) > 0:
            causes.append("Parsing errors detected - check file format and parser configuration")
        
        if data_quality.get("completeness", 100) < 80:
            causes.append("High null/empty field rate - check source data quality")
        
        if parsing_quality.get("status") == "poor":
            causes.append("Poor parsing success rate - may need different parser or file format correction")
        
        return {
            "status": "issues_found",
            "causes": causes,
            "primary_cause": causes[0] if causes else "Unknown"
        }
    
    def _generate_recommendations(
        self,
        issues: list,
        root_cause: Dict[str, Any]
    ) -> list:
        """Generate recommendations based on issues and root cause."""
        recommendations = []
        
        for issue in issues:
            if issue["type"] == "parsing_issue":
                recommendations.append({
                    "priority": "high",
                    "action": "Review parsing configuration and file format",
                    "expected_improvement": "Improved parsing success rate"
                })
            elif issue["type"] == "embedding_issue":
                recommendations.append({
                    "priority": "medium",
                    "action": "Review embedding configuration and schema mapping",
                    "expected_improvement": "Better schema alignment"
                })
            elif issue["type"] == "overall_quality":
                recommendations.append({
                    "priority": "high",
                    "action": "Review source data quality and extraction process",
                    "expected_improvement": "Higher overall data quality"
                })
        
        if not recommendations:
            recommendations.append({
                "priority": "low",
                "action": "Continue monitoring data quality",
                "expected_improvement": "Maintain current quality levels"
            })
        
        return recommendations
