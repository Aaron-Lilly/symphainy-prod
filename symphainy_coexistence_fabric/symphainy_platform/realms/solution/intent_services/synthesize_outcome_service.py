"""
Synthesize Outcome Intent Service

Implements the synthesize_outcome intent for the Solution Realm.

Contract: docs/intent_contracts/journey_solution_synthesis/intent_synthesize_outcome.md

Purpose: Synthesize business outcomes from Content, Insights, and Journey realms into a unified
solution summary. This intent aggregates pillar summaries from session state, generates synthesis
with realm-specific visualizations.

WHAT (Intent Service Role): I synthesize outcomes from all pillars
HOW (Intent Service Implementation): I execute the synthesize_outcome intent, aggregate pillar
    summaries, generate synthesis reports and visualizations, and return structured artifacts
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class SynthesizeOutcomeService(BaseIntentService):
    """
    Intent service for outcome synthesis.
    
    Synthesizes business outcomes from Content, Insights, and Journey realms
    into a unified solution summary with realm-specific visualizations.
    
    Contract Compliance:
    - Parameters: Section 2 of intent contract
    - Returns: Section 3 of intent contract
    - Idempotency: Section 5 of intent contract
    - Error Handling: Section 8 of intent contract
    """
    
    def __init__(self, public_works, state_surface):
        """
        Initialize SynthesizeOutcomeService.
        
        Args:
            public_works: Public Works Foundation Service for infrastructure access
            state_surface: State Surface for state management
        """
        super().__init__(
            service_id="synthesize_outcome_service",
            intent_type="synthesize_outcome",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the synthesize_outcome intent.
        
        Intent Flow (from contract):
        1. Read pillar summaries from session state
        2. Generate synthesis from all pillar data
        3. Generate realm-specific visualizations
        4. Create summary report
        5. Return structured artifact with synthesis and visualizations
        
        Args:
            context: Execution context with intent, tenant, session information
            params: Optional additional parameters (merged with intent.parameters)
        
        Returns:
            Dictionary with artifacts and events per contract Section 3
        
        Raises:
            ValueError: For validation errors
            RuntimeError: For runtime errors
        """
        # Record telemetry (start)
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
            intent_params = context.intent.parameters or {}
            if params:
                intent_params = {**intent_params, **params}
            
            synthesis_options = intent_params.get("synthesis_options", {})
            
            # === READ PILLAR SUMMARIES FROM SESSION STATE ===
            
            session_state = {}
            if context.state_surface:
                try:
                    session_state = await context.state_surface.get_session_state(
                        context.session_id,
                        context.tenant_id
                    ) or {}
                except Exception as e:
                    self.logger.warning(f"Could not read session state: {e}")
            
            # Extract pillar summaries
            content_summary = session_state.get("content_pillar_summary", {})
            insights_summary = session_state.get("insights_pillar_summary", {})
            journey_summary = session_state.get("journey_pillar_summary", {})
            
            self.logger.info(f"Synthesizing outcomes from pillars: content={bool(content_summary)}, "
                           f"insights={bool(insights_summary)}, journey={bool(journey_summary)}")
            
            # === GENERATE SYNTHESIS ===
            
            solution_id = f"synthesis_{generate_event_id()}"
            
            # Generate synthesis from pillar data
            synthesis = await self._generate_synthesis(
                content_summary=content_summary,
                insights_summary=insights_summary,
                journey_summary=journey_summary,
                synthesis_options=synthesis_options,
                context=context
            )
            
            # === GENERATE REALM-SPECIFIC VISUALIZATIONS ===
            
            realm_visuals = await self._generate_realm_visuals(
                content_summary=content_summary,
                insights_summary=insights_summary,
                journey_summary=journey_summary,
                context=context
            )
            
            # === GENERATE SUMMARY REPORT ===
            
            summary_report = await self._generate_summary_report(
                content_summary=content_summary,
                insights_summary=insights_summary,
                journey_summary=journey_summary,
                context=context
            )
            
            # === GENERATE SUMMARY VISUALIZATION (optional) ===
            
            summary_visual = None
            if self.public_works:
                try:
                    visual_abstraction = self.public_works.get_visual_generation_abstraction()
                    if visual_abstraction:
                        pillar_outputs = {
                            "content_pillar": content_summary,
                            "insights_pillar": insights_summary,
                            "journey_pillar": journey_summary
                        }
                        
                        visual_result = await visual_abstraction.create_summary_dashboard(
                            pillar_outputs=pillar_outputs,
                            tenant_id=context.tenant_id
                        )
                        
                        if visual_result and visual_result.success:
                            summary_visual = {
                                "image_base64": visual_result.image_base64,
                                "storage_path": visual_result.metadata.get("storage_path")
                            }
                except Exception as e:
                    self.logger.warning(f"Failed to generate summary visualization: {e}")
            
            # === BUILD RESPONSE (Contract Section 3) ===
            
            semantic_payload = {
                "solution_id": solution_id,
                "session_id": context.session_id,
                "status": "completed"
            }
            
            renderings = {
                "synthesis": synthesis,
                "content_summary": content_summary,
                "insights_summary": insights_summary,
                "journey_summary": journey_summary,
                "realm_visuals": realm_visuals,
                "summary_report": summary_report
            }
            
            if summary_visual:
                renderings["summary_visual"] = summary_visual
            
            structured_artifact = {
                "result_type": "solution",
                "semantic_payload": semantic_payload,
                "renderings": renderings
            }
            
            self.logger.info(f"✅ Outcome synthesized: {solution_id}")
            
            # Record telemetry (success)
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute",
                    "status": "completed",
                    "execution_id": context.execution_id,
                    "intent_type": self.intent_type,
                    "solution_id": solution_id
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "solution": structured_artifact
                },
                "events": [
                    {
                        "type": "outcome_synthesized",
                        "session_id": context.session_id,
                        "solution_id": solution_id
                    }
                ]
            }
            
        except Exception as e:
            # Record telemetry (failure)
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
    
    async def _generate_synthesis(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        synthesis_options: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate synthesis from pillar summaries.
        
        Args:
            content_summary: Content pillar summary
            insights_summary: Insights pillar summary
            journey_summary: Journey pillar summary
            synthesis_options: Synthesis options
            context: Execution context
        
        Returns:
            Dict with synthesis data
        """
        # Extract key findings from each pillar
        key_findings = []
        recommendations = []
        
        # Content findings
        if content_summary:
            files_uploaded = content_summary.get("files_uploaded", 0)
            files_parsed = content_summary.get("files_parsed", 0)
            
            if files_uploaded > 0:
                key_findings.append(f"Processed {files_uploaded} files with {files_parsed} successfully parsed")
            
            embeddings_generated = content_summary.get("embeddings_generated", 0)
            if embeddings_generated > 0:
                key_findings.append(f"Generated {embeddings_generated} embeddings for semantic search")
        
        # Insights findings
        if insights_summary:
            insights_count = insights_summary.get("insights_count", 0)
            quality_score = insights_summary.get("overall_quality", 0.0)
            
            if insights_count > 0:
                key_findings.append(f"Generated {insights_count} business insights")
            
            if quality_score > 0:
                quality_pct = round(quality_score * 100 if quality_score <= 1 else quality_score, 1)
                key_findings.append(f"Data quality score: {quality_pct}%")
                
                if quality_pct < 70:
                    recommendations.append("Address data quality issues before proceeding with migration")
            
            relationships_count = insights_summary.get("relationships_count", 0)
            if relationships_count > 0:
                key_findings.append(f"Mapped {relationships_count} data relationships")
        
        # Journey findings
        if journey_summary:
            workflows_created = journey_summary.get("workflows_created", 0)
            sops_generated = journey_summary.get("sops_generated", 0)
            
            if workflows_created > 0:
                key_findings.append(f"Created {workflows_created} coexistence workflows")
            
            if sops_generated > 0:
                key_findings.append(f"Generated {sops_generated} standard operating procedures")
            
            coexistence_analysis = journey_summary.get("coexistence_analysis", {})
            if coexistence_analysis:
                friction_points = coexistence_analysis.get("friction_points", [])
                if friction_points:
                    key_findings.append(f"Identified {len(friction_points)} friction points for optimization")
                    recommendations.append("Review and address identified friction points")
        
        # Generate overall synthesis
        overall_synthesis = self._generate_overall_synthesis(
            content_summary=content_summary,
            insights_summary=insights_summary,
            journey_summary=journey_summary,
            key_findings=key_findings
        )
        
        return {
            "overall_synthesis": overall_synthesis,
            "key_findings": key_findings,
            "recommendations": recommendations,
            "pillar_status": {
                "content": "completed" if content_summary else "pending",
                "insights": "completed" if insights_summary else "pending",
                "journey": "completed" if journey_summary else "pending"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_overall_synthesis(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        key_findings: list
    ) -> str:
        """Generate overall synthesis text."""
        parts = []
        
        # Introduction
        completed_pillars = sum([
            1 if content_summary else 0,
            1 if insights_summary else 0,
            1 if journey_summary else 0
        ])
        
        if completed_pillars == 3:
            parts.append("All three pillars (Content, Insights, Journey) have been completed.")
        elif completed_pillars > 0:
            parts.append(f"{completed_pillars} of 3 pillars have been completed.")
        else:
            parts.append("No pillars have been completed yet.")
        
        # Summary of findings
        if key_findings:
            parts.append(f"Key findings: {len(key_findings)} significant discoveries across all pillars.")
        
        # Readiness assessment
        if content_summary and insights_summary:
            parts.append("The data foundation is established and insights are available for decision-making.")
        
        if journey_summary:
            parts.append("Coexistence workflows are defined and ready for execution.")
        
        return " ".join(parts)
    
    async def _generate_realm_visuals(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate realm-specific visualizations.
        
        Args:
            content_summary: Content pillar summary
            insights_summary: Insights pillar summary
            journey_summary: Journey pillar summary
            context: Execution context
        
        Returns:
            Dict with realm-specific visual data
        """
        return {
            "content": await self._generate_content_visual(content_summary, context),
            "insights": await self._generate_insights_visual(insights_summary, context),
            "journey": await self._generate_journey_visual(journey_summary, context)
        }
    
    async def _generate_content_visual(
        self,
        content_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate Content pillar visual - Data Mash Tutorial."""
        files_uploaded = content_summary.get("files_uploaded", 0) if content_summary else 0
        files_parsed = content_summary.get("files_parsed", 0) if content_summary else 0
        embeddings_count = content_summary.get("embeddings_generated", 0) if content_summary else 0
        
        stages = [
            {
                "id": "ingestion",
                "name": "File Ingestion",
                "status": "complete" if files_uploaded > 0 else "pending",
                "count": files_uploaded
            },
            {
                "id": "parsing",
                "name": "File Parsing",
                "status": "complete" if files_parsed > 0 else "pending",
                "count": files_parsed
            },
            {
                "id": "embedding",
                "name": "Embedding Generation",
                "status": "complete" if embeddings_count > 0 else "pending",
                "count": embeddings_count
            }
        ]
        
        return {
            "realm": "content",
            "title": "Data Mash: Your Data Journey",
            "visual_type": "data_mash_tutorial",
            "stages": stages,
            "status": "completed" if files_uploaded > 0 else "pending"
        }
    
    async def _generate_insights_visual(
        self,
        insights_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate Insights pillar visual - Insights Ecosystem."""
        quality_score = insights_summary.get("overall_quality", 0.0) if insights_summary else 0.0
        insights_count = insights_summary.get("insights_count", 0) if insights_summary else 0
        relationships_count = insights_summary.get("relationships_count", 0) if insights_summary else 0
        
        return {
            "realm": "insights",
            "title": "Insights Ecosystem",
            "visual_type": "insights_ecosystem",
            "capabilities": {
                "quality_assessment": {
                    "overall_score": round(quality_score * 100, 1) if quality_score <= 1 else round(quality_score, 1),
                    "status": "complete" if quality_score > 0 else "pending"
                },
                "business_analysis": {
                    "insights_count": insights_count,
                    "status": "complete" if insights_count > 0 else "pending"
                },
                "relationship_graph": {
                    "nodes_count": relationships_count,
                    "status": "complete" if relationships_count > 0 else "pending"
                }
            },
            "status": "completed" if insights_summary else "pending"
        }
    
    async def _generate_journey_visual(
        self,
        journey_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate Journey pillar visual - Friction Removal."""
        workflows_created = journey_summary.get("workflows_created", 0) if journey_summary else 0
        sops_generated = journey_summary.get("sops_generated", 0) if journey_summary else 0
        coexistence_analysis = journey_summary.get("coexistence_analysis", {}) if journey_summary else {}
        
        friction_points = coexistence_analysis.get("friction_points", []) if coexistence_analysis else []
        
        return {
            "realm": "journey",
            "title": "Coexistence Analysis",
            "visual_type": "friction_removal",
            "coexistence_analysis": {
                "workflows_created": workflows_created,
                "sops_generated": sops_generated,
                "friction_points_identified": len(friction_points),
                "friction_points_resolved": len([fp for fp in friction_points if fp.get("resolved", False)])
            },
            "status": "completed" if journey_summary else "pending"
        }
    
    async def _generate_summary_report(
        self,
        content_summary: Dict[str, Any],
        insights_summary: Dict[str, Any],
        journey_summary: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate summary report for all pillars.
        
        Args:
            content_summary: Content pillar summary
            insights_summary: Insights pillar summary
            journey_summary: Journey pillar summary
            context: Execution context
        
        Returns:
            Dict with summary report data
        """
        return {
            "content_pillar": {
                "status": "completed" if content_summary else "pending",
                "files_uploaded": content_summary.get("files_uploaded", 0) if content_summary else 0,
                "files_parsed": content_summary.get("files_parsed", 0) if content_summary else 0,
                "embeddings_generated": content_summary.get("embeddings_generated", 0) if content_summary else 0
            },
            "insights_pillar": {
                "status": "completed" if insights_summary else "pending",
                "insights_generated": insights_summary.get("insights_count", 0) if insights_summary else 0,
                "quality_score": insights_summary.get("overall_quality", 0.0) if insights_summary else 0.0,
                "relationships_mapped": insights_summary.get("relationships_count", 0) if insights_summary else 0
            },
            "journey_pillar": {
                "status": "completed" if journey_summary else "pending",
                "workflows_created": journey_summary.get("workflows_created", 0) if journey_summary else 0,
                "sops_generated": journey_summary.get("sops_generated", 0) if journey_summary else 0
            },
            "generated_at": datetime.utcnow().isoformat()
        }
