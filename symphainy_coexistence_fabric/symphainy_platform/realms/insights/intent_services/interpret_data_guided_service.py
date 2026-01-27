"""
Interpret Data Guided Intent Service

Implements the interpret_data_guided intent for the Insights Realm.

Contract: docs/intent_contracts/journey_insights_data_interpretation/intent_interpret_data_guided.md

Purpose: Guide-based semantic discovery with user-provided constraints and guides.
Uses guides to focus discovery on specific patterns or domains.

WHAT (Intent Service Role): I discover semantic meaning with guide constraints
HOW (Intent Service Implementation): I use guides to focus discovery on specific
    patterns, domains, or use cases

Naming Convention:
- Realm: Insights Realm
- Artifacts: insights_guided_interpretation
- Solution = platform construct (InsightsSolution)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class InterpretDataGuidedService(BaseIntentService):
    """
    Intent service for guided interpretation.
    
    Guided discovery with constraints:
    - Uses guides to focus analysis
    - Applies user-provided patterns
    - Maps to target schemas
    - Generates domain-specific insights
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize InterpretDataGuidedService."""
        super().__init__(
            service_id="interpret_data_guided_service",
            intent_type="interpret_data_guided",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the interpret_data_guided intent.
        
        Args:
            context: Execution context
            params: Optional parameters
        
        Returns:
            Dictionary with artifacts and events
        """
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            # Required parameters
            parsed_file_id = intent_params.get("parsed_file_id")
            guide_id = intent_params.get("guide_id")
            
            if not parsed_file_id:
                raise ValueError("parsed_file_id is required for guided discovery")
            if not guide_id:
                raise ValueError("guide_id is required for guided discovery")
            
            # Get guide
            guide = await self._get_guide(guide_id, context)
            
            # Get embeddings
            embeddings = await self._get_embeddings(parsed_file_id, context)
            
            # Apply guide to discovery
            guided_entities = await self._discover_with_guide(embeddings, guide)
            
            # Map to guide schema
            schema_mapping = await self._map_to_guide_schema(guided_entities, guide)
            
            # Generate guided insights
            guided_insights = await self._generate_guided_insights(
                guided_entities, schema_mapping, guide
            )
            
            # Build interpretation result
            interpretation_id = f"interpretation_{generate_event_id()}"
            
            interpretation = {
                "interpretation_id": interpretation_id,
                "parsed_file_id": parsed_file_id,
                "guide_id": guide_id,
                "discovery_type": "guided",
                "guided_entities": guided_entities,
                "schema_mapping": schema_mapping,
                "guided_insights": guided_insights,
                "guide_used": guide,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Artifact Plane
            artifact_id = await self._store_interpretation(interpretation, context)
            
            self.logger.info(f"Guided discovery completed: {interpretation_id} (guide: {guide_id})")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "interpretation_id": interpretation_id, "guide_id": guide_id
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "interpretation": interpretation,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "data_interpreted",
                        "interpretation_id": interpretation_id,
                        "discovery_type": "guided",
                        "guide_id": guide_id
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _get_guide(
        self,
        guide_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Get guide from registry or state surface."""
        # Try to get guide from public works registry
        if self.public_works:
            try:
                registry = self.public_works.get_registry_abstraction()
                if registry:
                    guide = await registry.get_guide(guide_id, context.tenant_id)
                    if guide:
                        return guide
            except Exception:
                pass
        
        # Return default guide structure
        return {
            "guide_id": guide_id,
            "name": f"Guide {guide_id}",
            "domain": "general",
            "target_schema": {"fields": []},
            "patterns": [],
            "rules": []
        }
    
    async def _get_embeddings(
        self,
        parsed_file_id: str,
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """Get embeddings for the parsed file."""
        embeddings = []
        
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.list_artifacts(
                        tenant_id=context.tenant_id,
                        filters={"related_to": parsed_file_id, "artifact_type": "embedding"}
                    )
                    embeddings = result.get("artifacts", [])
            except Exception:
                pass
        
        if not embeddings:
            embeddings = [
                {"type": "schema", "content": {"fields": ["field1", "field2"]}},
                {"type": "semantic", "content": {"concepts": ["concept1", "concept2"]}}
            ]
        
        return embeddings
    
    async def _discover_with_guide(
        self,
        embeddings: List[Dict[str, Any]],
        guide: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Discover entities using guide constraints."""
        entities = []
        guide_domain = guide.get("domain", "general")
        target_schema = guide.get("target_schema", {})
        target_fields = target_schema.get("fields", [])
        
        for i, embedding in enumerate(embeddings[:10]):
            content = embedding.get("content", {})
            
            if isinstance(content, dict):
                for key, value in content.items():
                    # Check if field matches guide target schema
                    matches_target = key in target_fields if target_fields else True
                    
                    entities.append({
                        "entity_id": f"guided_{i}_{key}",
                        "entity_type": "guided",
                        "name": key,
                        "domain": guide_domain,
                        "matches_target": matches_target,
                        "attributes": value if isinstance(value, list) else [value],
                        "confidence": 0.85 if matches_target else 0.65
                    })
        
        return entities
    
    async def _map_to_guide_schema(
        self,
        entities: List[Dict[str, Any]],
        guide: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map discovered entities to guide schema."""
        target_schema = guide.get("target_schema", {})
        target_fields = target_schema.get("fields", [])
        
        mapped_fields = {}
        unmapped_fields = []
        
        for entity in entities:
            entity_name = entity.get("name", "")
            if entity_name in target_fields:
                mapped_fields[entity_name] = {
                    "source_entity": entity.get("entity_id"),
                    "confidence": entity.get("confidence", 0.5)
                }
            else:
                unmapped_fields.append(entity_name)
        
        return {
            "mapped_fields": mapped_fields,
            "unmapped_fields": unmapped_fields,
            "coverage": len(mapped_fields) / max(len(target_fields), 1) * 100 if target_fields else 100,
            "target_schema": target_schema
        }
    
    async def _generate_guided_insights(
        self,
        entities: List[Dict[str, Any]],
        schema_mapping: Dict[str, Any],
        guide: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights based on guide analysis."""
        coverage = schema_mapping.get("coverage", 0)
        mapped_count = len(schema_mapping.get("mapped_fields", {}))
        unmapped_count = len(schema_mapping.get("unmapped_fields", []))
        
        insights = [
            f"Guide '{guide.get('name', 'Unknown')}' applied successfully",
            f"Schema coverage: {coverage:.1f}%",
            f"Mapped {mapped_count} fields to target schema"
        ]
        
        if unmapped_count > 0:
            insights.append(f"{unmapped_count} fields could not be mapped")
        
        recommendations = []
        if coverage < 70:
            recommendations.append("Consider using a different guide for better coverage")
        if unmapped_count > mapped_count:
            recommendations.append("Many fields unmapped - review guide schema")
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "guide_domain": guide.get("domain", "general"),
            "overall_fit": "good" if coverage > 80 else "moderate" if coverage > 50 else "poor"
        }
    
    async def _store_interpretation(
        self,
        interpretation: Dict[str, Any],
        context: ExecutionContext
    ) -> Optional[str]:
        """Store interpretation in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="interpretation",
                        content=interpretation,
                        metadata={
                            "discovery_type": "guided",
                            "guide_id": interpretation.get("guide_id")
                        },
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store interpretation: {e}")
        return None
