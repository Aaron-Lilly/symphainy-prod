"""
Generate Report Intent Service

Implements the generate_report intent for the Outcomes Realm.

Contract: docs/intent_contracts/journey_outcomes_synthesis/intent_generate_report.md

Purpose: Generate reports and summaries from platform outputs including pillar summaries,
realm visuals, and comprehensive dashboards.

WHAT (Intent Service Role): I generate reports from platform outputs
HOW (Intent Service Implementation): I use ReportGeneratorService library
    to create various report types

Naming Convention:
- Realm: Outcomes Realm
- Artifacts: outcomes_report
- Solution = platform construct (OutcomesSolution)
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
from symphainy_platform.foundations.libraries.reporting.report_generator_service import ReportGeneratorService
from utilities import generate_event_id


class GenerateReportService(BaseIntentService):
    """
    Intent service for report generation.
    
    Generates reports for:
    - Pillar summaries (Content, Insights, Journey)
    - Realm-specific visuals (tutorial, ecosystem, friction)
    - Comprehensive dashboards
    
    Uses ReportGeneratorService library for report generation capabilities.
    """
    
    # Supported report types
    REPORT_TYPES = {
        "pillar_summary",
        "realm_visuals",
        "comprehensive_dashboard",
        "executive_summary",
        "data_quality_report",
        "coexistence_analysis_report"
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize GenerateReportService."""
        super().__init__(
            service_id="generate_report_service",
            intent_type="generate_report",
            public_works=public_works,
            state_surface=state_surface
        )
        
        # Initialize the report generation library
        self._report_service = ReportGeneratorService(public_works=public_works)
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the generate_report intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            # Validate required parameters
            report_type = intent_params.get("report_type", "pillar_summary")
            
            if report_type not in self.REPORT_TYPES:
                raise ValueError(f"Unknown report_type: {report_type}. Supported: {self.REPORT_TYPES}")
            
            # Get pillar summaries from params or state surface
            content_summary = intent_params.get("content_summary", {})
            insights_summary = intent_params.get("insights_summary", {})
            journey_summary = intent_params.get("journey_summary", {})
            
            # Try to get from state surface if not provided
            if not content_summary or not insights_summary or not journey_summary:
                summaries = await self._get_pillar_summaries(context)
                content_summary = content_summary or summaries.get("content", {})
                insights_summary = insights_summary or summaries.get("insights", {})
                journey_summary = journey_summary or summaries.get("journey", {})
            
            # Route to appropriate report generation method
            report_result = await self._generate_report(
                report_type=report_type,
                content_summary=content_summary,
                insights_summary=insights_summary,
                journey_summary=journey_summary,
                context=context
            )
            
            report_id = f"report_{generate_event_id()}"
            
            # Build result artifact
            report_artifact = {
                "report_id": report_id,
                "report_type": report_type,
                "report_data": report_result,
                "metadata": {
                    "content_pillar_status": "completed" if content_summary else "pending",
                    "insights_pillar_status": "completed" if insights_summary else "pending",
                    "journey_pillar_status": "completed" if journey_summary else "pending"
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Artifact Plane
            artifact_id = await self._store_report(report_artifact, context)
            
            self.logger.info(f"Report generation completed: {report_id}, type={report_type}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "report_id": report_id,
                    "report_type": report_type
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "report": report_artifact,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "report_generated",
                        "report_id": report_id,
                        "report_type": report_type
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _generate_report(
        self,
        report_type: str,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Route to appropriate report generator."""
        
        if report_type == "pillar_summary":
            return await self._report_service.generate_pillar_summary(
                content_summary=content_summary,
                insights_summary=insights_summary,
                journey_summary=journey_summary,
                tenant_id=context.tenant_id,
                context=context
            )
        
        elif report_type == "realm_visuals":
            return await self._report_service.generate_realm_summary_visuals(
                content_summary=content_summary,
                insights_summary=insights_summary,
                journey_summary=journey_summary,
                tenant_id=context.tenant_id,
                context=context
            )
        
        elif report_type == "comprehensive_dashboard":
            # Combine pillar summary and realm visuals
            pillar_summary = await self._report_service.generate_pillar_summary(
                content_summary=content_summary,
                insights_summary=insights_summary,
                journey_summary=journey_summary,
                tenant_id=context.tenant_id,
                context=context
            )
            
            realm_visuals = await self._report_service.generate_realm_summary_visuals(
                content_summary=content_summary,
                insights_summary=insights_summary,
                journey_summary=journey_summary,
                tenant_id=context.tenant_id,
                context=context
            )
            
            return {
                "pillar_summary": pillar_summary,
                "realm_visuals": realm_visuals,
                "overall_status": self._calculate_overall_status(pillar_summary),
                "generated_at": datetime.utcnow().isoformat()
            }
        
        elif report_type == "executive_summary":
            return await self._generate_executive_summary(
                content_summary, insights_summary, journey_summary, context
            )
        
        elif report_type == "data_quality_report":
            return await self._generate_data_quality_report(
                content_summary, insights_summary, context
            )
        
        elif report_type == "coexistence_analysis_report":
            return await self._generate_coexistence_report(
                journey_summary, context
            )
        
        else:
            return {"error": f"Unknown report type: {report_type}"}
    
    async def _generate_executive_summary(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate executive summary report."""
        # Calculate key metrics
        files_processed = content_summary.get("files_parsed", 0) if content_summary else 0
        insights_generated = insights_summary.get("insights_count", 0) if insights_summary else 0
        workflows_created = journey_summary.get("workflows_created", 0) if journey_summary else 0
        
        quality_score = insights_summary.get("overall_quality", 0.0) if insights_summary else 0.0
        if quality_score > 1.0:
            quality_score = quality_score / 100  # Normalize if percentage
        
        return {
            "executive_summary": {
                "title": "Platform Analysis Executive Summary",
                "key_metrics": {
                    "files_processed": files_processed,
                    "insights_generated": insights_generated,
                    "workflows_created": workflows_created,
                    "data_quality_score": f"{quality_score * 100:.1f}%"
                },
                "status": {
                    "content_pillar": "Complete" if files_processed > 0 else "Pending",
                    "insights_pillar": "Complete" if insights_generated > 0 else "Pending",
                    "journey_pillar": "Complete" if workflows_created > 0 else "Pending"
                },
                "recommendations": self._generate_recommendations(
                    content_summary, insights_summary, journey_summary
                )
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_data_quality_report(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate data quality report."""
        return {
            "data_quality_report": {
                "title": "Data Quality Assessment Report",
                "quality_dimensions": {
                    "completeness": insights_summary.get("completeness_score", 0.0) if insights_summary else 0.0,
                    "accuracy": insights_summary.get("accuracy_score", 0.0) if insights_summary else 0.0,
                    "consistency": insights_summary.get("consistency_score", 0.0) if insights_summary else 0.0,
                    "timeliness": insights_summary.get("timeliness_score", 0.0) if insights_summary else 0.0
                },
                "overall_quality": insights_summary.get("overall_quality", 0.0) if insights_summary else 0.0,
                "issues_identified": insights_summary.get("quality_issues", []) if insights_summary else [],
                "files_analyzed": content_summary.get("files_parsed", 0) if content_summary else 0
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_coexistence_report(
        self,
        journey_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate coexistence analysis report."""
        coexistence = journey_summary.get("coexistence_analysis", {}) if journey_summary else {}
        
        return {
            "coexistence_report": {
                "title": "Human-AI Coexistence Analysis Report",
                "coexistence_breakdown": {
                    "human_tasks": coexistence.get("human_tasks_count", 0),
                    "ai_assisted_tasks": coexistence.get("ai_assisted_tasks_count", 0),
                    "hybrid_tasks": coexistence.get("hybrid_tasks_count", 0)
                },
                "friction_analysis": {
                    "points_identified": len(coexistence.get("friction_points", [])),
                    "points_resolved": len([fp for fp in coexistence.get("friction_points", []) if fp.get("resolved", False)])
                },
                "workflows_analyzed": journey_summary.get("workflows_created", 0) if journey_summary else 0,
                "recommendations": coexistence.get("recommendations", [])
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_recommendations(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any]
    ) -> list:
        """Generate recommendations based on pillar summaries."""
        recommendations = []
        
        # Content recommendations
        if not content_summary or content_summary.get("files_parsed", 0) == 0:
            recommendations.append("Upload and process source files to begin data analysis")
        
        # Insights recommendations
        quality_score = insights_summary.get("overall_quality", 0.0) if insights_summary else 0.0
        if quality_score > 0 and quality_score < 0.7:
            recommendations.append("Review data quality issues to improve analysis accuracy")
        
        # Journey recommendations
        if not journey_summary or journey_summary.get("workflows_created", 0) == 0:
            recommendations.append("Create workflows to automate identified processes")
        
        if not recommendations:
            recommendations.append("Continue monitoring and optimizing platform outputs")
        
        return recommendations
    
    def _calculate_overall_status(self, pillar_summary: Dict[str, Any]) -> str:
        """Calculate overall status from pillar summary."""
        completed = 0
        total = 3
        
        if pillar_summary.get("content_pillar", {}).get("status") == "completed":
            completed += 1
        if pillar_summary.get("insights_pillar", {}).get("status") == "completed":
            completed += 1
        if pillar_summary.get("journey_pillar", {}).get("status") == "completed":
            completed += 1
        
        if completed == total:
            return "complete"
        elif completed > 0:
            return "in_progress"
        return "pending"
    
    async def _get_pillar_summaries(self, context: ExecutionContext) -> Dict[str, Any]:
        """Get pillar summaries from state surface."""
        summaries = {"content": {}, "insights": {}, "journey": {}}
        
        if context.state_surface:
            try:
                for pillar in ["content", "insights", "journey"]:
                    data = await context.state_surface.get_execution_state(
                        key=f"{pillar}_summary",
                        tenant_id=context.tenant_id
                    )
                    if data:
                        summaries[pillar] = data
            except Exception:
                pass
        
        return summaries
    
    async def _store_report(
        self,
        report: Dict[str, Any],
        context: ExecutionContext
    ) -> Optional[str]:
        """Store report in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="report",
                        content=report,
                        metadata={
                            "report_id": report.get("report_id"),
                            "report_type": report.get("report_type")
                        },
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store report: {e}")
        return None
