"""
Map Relationships Service (Platform SDK)

Maps entity relationships from data.

Contract: docs/intent_contracts/journey_insights_relationships/intent_map_relationships.md
"""

from typing import Dict, Any, List
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class MapRelationshipsService(PlatformIntentService):
    """
    Map Relationships Service using Platform SDK.
    
    Maps entity relationships:
    - Entity extraction
    - Relationship detection
    - Graph visualization
    """
    
    intent_type = "map_relationships"
    
    def __init__(self, service_id: str = "map_relationships_service"):
        """Initialize Map Relationships Service."""
        super().__init__(service_id=service_id, intent_type="map_relationships")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute map_relationships intent."""
        self.logger.info(f"Executing map_relationships: {ctx.execution_id}")
        
        parsed_file_id = ctx.intent.parameters.get("parsed_file_id")
        relationship_types = ctx.intent.parameters.get("relationship_types", ["all"])
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required")
        
        # Get parsed content
        parsed_content = await ctx.platform.get_parsed_file(
            parsed_file_id=parsed_file_id,
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id
        )
        
        if not parsed_content:
            raise ValueError(f"Parsed file not found: {parsed_file_id}")
        
        # Try to use SemanticSignalExtractor for relationship mapping
        relationships = await self._map_via_agent(ctx, parsed_content, relationship_types)
        
        relationship_result = {
            "mapping_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "relationship_types": relationship_types,
            "relationships": relationships,
            "mapped_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Relationship mapping complete")
        
        return {
            "artifacts": {
                "relationship_map": relationship_result
            },
            "events": [{
                "type": "relationships_mapped",
                "event_id": generate_event_id(),
                "entity_count": len(relationships.get("entities", [])),
                "relationship_count": len(relationships.get("relationships", []))
            }]
        }
    
    async def _map_via_agent(
        self,
        ctx: PlatformContext,
        parsed_content: Dict[str, Any],
        relationship_types: List[str]
    ) -> Dict[str, Any]:
        """Map relationships using SemanticSignalExtractor."""
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "semantic_signal_extractor",
                    params={
                        "action": "extract_relationships",
                        "content": parsed_content.get("content"),
                        "structure": parsed_content.get("structure"),
                        "relationship_types": relationship_types
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    result = agent_result.get("result", {})
                    result["used_real_llm"] = True
                    return result
                    
            except Exception as e:
                self.logger.warning(f"Agent invocation failed: {e}")
        
        # Fallback to heuristic mapping
        return self._heuristic_mapping(parsed_content)
    
    def _heuristic_mapping(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Heuristic relationship mapping fallback."""
        structure = parsed_content.get("structure", {})
        
        entities = []
        relationships = []
        
        # Extract entities from structure
        if isinstance(structure, dict):
            for field_name in structure.keys():
                entities.append({
                    "id": field_name,
                    "name": field_name,
                    "type": "field"
                })
        
        return {
            "entities": entities,
            "relationships": relationships,
            "graph": {
                "nodes": entities,
                "edges": relationships
            },
            "used_real_llm": False
        }
