"""
Analyze Structured Data Intent Service

Implements the analyze_structured_data intent for the Insights Realm.

Contract: docs/intent_contracts/journey_insights_data_analysis/intent_analyze_structured_data.md

Purpose: Analyze structured data (CSV, JSON, database tables) for business insights.
Generates statistics, patterns, and actionable recommendations.

WHAT (Intent Service Role): I analyze structured data for business insights
HOW (Intent Service Implementation): I process structured data to generate
    statistics, patterns, and recommendations

Naming Convention:
- Realm: Insights Realm
- Artifacts: insights_structured_analysis
- Solution = platform construct (InsightsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class AnalyzeStructuredDataService(BaseIntentService):
    """
    Intent service for structured data analysis.
    
    Analyzes structured data (CSV, JSON, tables) for:
    - Statistical summaries
    - Pattern detection
    - Anomaly identification
    - Business insights generation
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize AnalyzeStructuredDataService."""
        super().__init__(
            service_id="analyze_structured_data_service",
            intent_type="analyze_structured_data",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the analyze_structured_data intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            parsed_file_id = intent_params.get("parsed_file_id")
            if not parsed_file_id:
                raise ValueError("parsed_file_id is required for structured analysis")
            
            analysis_options = intent_params.get("analysis_options", {})
            
            # Get parsed data
            parsed_data = await self._get_parsed_data(parsed_file_id, context)
            
            # Generate statistics
            statistics = await self._generate_statistics(parsed_data)
            
            # Detect patterns
            patterns = await self._detect_patterns(parsed_data)
            
            # Identify anomalies
            anomalies = await self._identify_anomalies(parsed_data)
            
            # Generate business insights
            business_insights = await self._generate_business_insights(
                statistics, patterns, anomalies
            )
            
            # Build analysis result
            analysis_id = f"analysis_{generate_event_id()}"
            
            analysis = {
                "analysis_id": analysis_id,
                "parsed_file_id": parsed_file_id,
                "analysis_type": "structured",
                "statistics": statistics,
                "patterns": patterns,
                "anomalies": anomalies,
                "business_insights": business_insights,
                "analysis_options": analysis_options,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Artifact Plane
            artifact_id = await self._store_analysis(analysis, context)
            
            self.logger.info(f"Structured analysis completed: {analysis_id}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "analysis_id": analysis_id
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "analysis": analysis,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "structured_data_analyzed",
                        "analysis_id": analysis_id,
                        "analysis_type": "structured"
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _get_parsed_data(self, parsed_file_id: str, context: ExecutionContext) -> Dict[str, Any]:
        """Get parsed data from state surface or artifact plane."""
        if context.state_surface:
            try:
                data = await context.state_surface.get_execution_state(
                    key=f"parsed_file_{parsed_file_id}", tenant_id=context.tenant_id
                )
                if data:
                    return data
            except Exception:
                pass
        
        return {"parsed_file_id": parsed_file_id, "records": [], "schema": {}}
    
    async def _generate_statistics(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate statistical summary of structured data."""
        records = parsed_data.get("records", [])
        schema = parsed_data.get("schema", {})
        
        return {
            "total_records": len(records),
            "total_columns": len(schema),
            "column_statistics": self._calculate_column_stats(records, schema),
            "data_types": {k: v.get("type", "unknown") for k, v in schema.items()} if isinstance(schema, dict) else {},
            "completeness": self._calculate_completeness(records)
        }
    
    def _calculate_column_stats(self, records: list, schema: dict) -> Dict[str, Any]:
        """Calculate per-column statistics."""
        stats = {}
        if not records or not isinstance(schema, dict):
            return stats
        
        for col in list(schema.keys())[:10]:  # Limit columns
            values = [r.get(col) for r in records[:1000] if isinstance(r, dict)]
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            
            stats[col] = {
                "non_null_count": len([v for v in values if v is not None]),
                "null_count": len([v for v in values if v is None]),
                "unique_count": len(set(str(v) for v in values if v is not None))
            }
            
            if numeric_values:
                stats[col]["min"] = min(numeric_values)
                stats[col]["max"] = max(numeric_values)
                stats[col]["avg"] = sum(numeric_values) / len(numeric_values)
        
        return stats
    
    def _calculate_completeness(self, records: list) -> float:
        """Calculate data completeness percentage."""
        if not records:
            return 0.0
        
        total = 0
        non_null = 0
        
        for record in records[:1000]:
            if isinstance(record, dict):
                for value in record.values():
                    total += 1
                    if value is not None and value != "":
                        non_null += 1
        
        return round((non_null / max(total, 1)) * 100, 1)
    
    async def _detect_patterns(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect patterns in structured data."""
        patterns = []
        records = parsed_data.get("records", [])
        
        if len(records) > 100:
            patterns.append({
                "pattern_type": "volume",
                "description": f"Large dataset with {len(records)} records",
                "confidence": 0.9
            })
        
        # Detect schema patterns
        schema = parsed_data.get("schema", {})
        if isinstance(schema, dict):
            id_fields = [k for k in schema.keys() if "id" in k.lower()]
            if id_fields:
                patterns.append({
                    "pattern_type": "identifier",
                    "description": f"Contains identifier fields: {', '.join(id_fields)}",
                    "confidence": 0.85
                })
        
        return patterns
    
    async def _identify_anomalies(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify anomalies in structured data."""
        anomalies = []
        records = parsed_data.get("records", [])
        
        # Check for empty records
        empty_count = sum(1 for r in records if not r or (isinstance(r, dict) and not any(r.values())))
        if empty_count > 0:
            anomalies.append({
                "anomaly_type": "empty_records",
                "count": empty_count,
                "severity": "medium" if empty_count < len(records) * 0.1 else "high"
            })
        
        return anomalies
    
    async def _generate_business_insights(
        self,
        statistics: Dict[str, Any],
        patterns: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate business insights from analysis."""
        insights = []
        recommendations = []
        
        # Generate insights from statistics
        total_records = statistics.get("total_records", 0)
        completeness = statistics.get("completeness", 0)
        
        if total_records > 0:
            insights.append(f"Dataset contains {total_records} records")
        
        if completeness > 90:
            insights.append("Data completeness is excellent (>90%)")
        elif completeness < 70:
            insights.append(f"Data completeness is low ({completeness}%)")
            recommendations.append("Review and address missing data")
        
        # Generate insights from patterns
        for pattern in patterns:
            insights.append(pattern.get("description", ""))
        
        # Generate recommendations from anomalies
        for anomaly in anomalies:
            if anomaly.get("severity") == "high":
                recommendations.append(f"Address {anomaly.get('anomaly_type')} issue")
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "data_quality_score": round(completeness, 1),
            "analysis_confidence": 0.8
        }
    
    async def _store_analysis(self, analysis: Dict[str, Any], context: ExecutionContext) -> Optional[str]:
        """Store analysis in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="analysis_report",
                        content=analysis,
                        metadata={"analysis_type": "structured"},
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store analysis: {e}")
        return None
