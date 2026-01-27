"""
Map Relationships Intent Service

Implements the map_relationships intent for the Insights Realm.

Contract: docs/intent_contracts/journey_insights_lineage/intent_map_relationships.md

Purpose: Map entity relationships from parsed data and embeddings. Creates
interactive relationship graphs for exploration.

WHAT (Intent Service Role): I map entity relationships
HOW (Intent Service Implementation): I analyze data to identify entities
    and their relationships, creating interactive graphs

Naming Convention:
- Realm: Insights Realm
- Artifacts: insights_relationship_graph
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


class MapRelationshipsService(BaseIntentService):
    """
    Intent service for relationship mapping.
    
    Maps entity relationships:
    - Identifies entities from data
    - Discovers relationships between entities
    - Creates interactive relationship graphs
    - Enables exploration and filtering
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize MapRelationshipsService."""
        super().__init__(
            service_id="map_relationships_service",
            intent_type="map_relationships",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the map_relationships intent."""
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
                raise ValueError("parsed_file_id is required for relationship mapping")
            
            mapping_options = intent_params.get("mapping_options", {})
            
            # Get parsed data
            parsed_data = await self._get_parsed_data(parsed_file_id, context)
            
            # Get embeddings
            embeddings = await self._get_embeddings(parsed_file_id, context)
            
            # Identify entities
            entities = await self._identify_entities(parsed_data, embeddings)
            
            # Discover relationships
            relationships = await self._discover_relationships(entities, parsed_data)
            
            # Build relationship graph
            graph = await self._build_graph(entities, relationships)
            
            # Generate visualization config
            visualization = await self._generate_visualization(graph)
            
            # Build result
            mapping_id = f"mapping_{generate_event_id()}"
            
            relationship_map = {
                "mapping_id": mapping_id,
                "parsed_file_id": parsed_file_id,
                "entities": entities,
                "relationships": relationships,
                "graph": graph,
                "visualization": visualization,
                "statistics": self._calculate_statistics(entities, relationships),
                "mapping_options": mapping_options,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Artifact Plane
            artifact_id = await self._store_mapping(relationship_map, context)
            
            self.logger.info(f"Relationships mapped: {mapping_id} ({len(entities)} entities, {len(relationships)} relationships)")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "mapping_id": mapping_id,
                    "entities_count": len(entities),
                    "relationships_count": len(relationships)
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": {
                    "relationship_map": relationship_map,
                    "artifact_id": artifact_id
                },
                "events": [
                    {
                        "type": "relationships_mapped",
                        "mapping_id": mapping_id,
                        "entities_count": len(entities),
                        "relationships_count": len(relationships)
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
        """Get parsed data from state surface."""
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
    
    async def _get_embeddings(self, parsed_file_id: str, context: ExecutionContext) -> List[Dict[str, Any]]:
        """Get embeddings for the parsed file."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.list_artifacts(
                        tenant_id=context.tenant_id,
                        filters={"related_to": parsed_file_id, "artifact_type": "embedding"}
                    )
                    return result.get("artifacts", [])
            except Exception:
                pass
        return []
    
    async def _identify_entities(
        self,
        parsed_data: Dict[str, Any],
        embeddings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify entities from parsed data and embeddings."""
        entities = []
        
        # Extract entities from schema
        schema = parsed_data.get("schema", {})
        if isinstance(schema, dict):
            for i, (field_name, field_info) in enumerate(list(schema.items())[:20]):
                entities.append({
                    "entity_id": f"entity_{i}",
                    "name": field_name,
                    "entity_type": "field",
                    "attributes": field_info if isinstance(field_info, dict) else {"type": str(field_info)},
                    "source": "schema"
                })
        
        # Extract entities from embeddings
        for i, embedding in enumerate(embeddings[:10]):
            content = embedding.get("content", {})
            if isinstance(content, dict):
                for key in list(content.keys())[:5]:
                    entities.append({
                        "entity_id": f"emb_entity_{i}_{key}",
                        "name": key,
                        "entity_type": "concept",
                        "attributes": {"source_embedding": embedding.get("type", "unknown")},
                        "source": "embedding"
                    })
        
        return entities
    
    async def _discover_relationships(
        self,
        entities: List[Dict[str, Any]],
        parsed_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Discover relationships between entities."""
        relationships = []
        
        # Create relationships based on entity proximity and type
        field_entities = [e for e in entities if e.get("entity_type") == "field"]
        concept_entities = [e for e in entities if e.get("entity_type") == "concept"]
        
        # Relationships between fields (based on naming patterns)
        for i, entity1 in enumerate(field_entities):
            for entity2 in field_entities[i+1:]:
                name1 = entity1.get("name", "").lower()
                name2 = entity2.get("name", "").lower()
                
                # Check for foreign key patterns
                if name1.endswith("_id") and name2.replace("_id", "") in name1:
                    relationships.append({
                        "relationship_id": f"rel_{entity1['entity_id']}_{entity2['entity_id']}",
                        "source": entity1["entity_id"],
                        "target": entity2["entity_id"],
                        "relationship_type": "references",
                        "confidence": 0.8
                    })
                # Check for similar prefixes
                elif name1[:3] == name2[:3] and len(name1) > 3:
                    relationships.append({
                        "relationship_id": f"rel_{entity1['entity_id']}_{entity2['entity_id']}",
                        "source": entity1["entity_id"],
                        "target": entity2["entity_id"],
                        "relationship_type": "related_to",
                        "confidence": 0.5
                    })
        
        # Relationships between fields and concepts
        for field in field_entities[:5]:
            for concept in concept_entities[:5]:
                relationships.append({
                    "relationship_id": f"rel_{field['entity_id']}_{concept['entity_id']}",
                    "source": field["entity_id"],
                    "target": concept["entity_id"],
                    "relationship_type": "describes",
                    "confidence": 0.6
                })
        
        return relationships
    
    async def _build_graph(
        self,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build graph structure from entities and relationships."""
        # Position entities in a layout
        nodes = []
        for i, entity in enumerate(entities):
            x = 100 + (i % 5) * 180
            y = 100 + (i // 5) * 120
            
            nodes.append({
                "id": entity["entity_id"],
                "label": entity["name"],
                "type": entity["entity_type"],
                "x": x,
                "y": y
            })
        
        # Build edges
        edges = []
        for rel in relationships:
            edges.append({
                "id": rel["relationship_id"],
                "source": rel["source"],
                "target": rel["target"],
                "label": rel["relationship_type"],
                "weight": rel.get("confidence", 0.5)
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "layout": "force-directed"
        }
    
    async def _generate_visualization(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization configuration."""
        return {
            "type": "relationship_graph",
            "layout": "force-directed",
            "node_colors": {
                "field": "#3498db",
                "concept": "#9b59b6",
                "default": "#95a5a6"
            },
            "edge_colors": {
                "references": "#e74c3c",
                "related_to": "#2ecc71",
                "describes": "#f39c12"
            },
            "interactive": True,
            "zoomable": True,
            "filterable": True
        }
    
    def _calculate_statistics(
        self,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate relationship statistics."""
        entity_types = {}
        for entity in entities:
            etype = entity.get("entity_type", "unknown")
            entity_types[etype] = entity_types.get(etype, 0) + 1
        
        relationship_types = {}
        for rel in relationships:
            rtype = rel.get("relationship_type", "unknown")
            relationship_types[rtype] = relationship_types.get(rtype, 0) + 1
        
        return {
            "total_entities": len(entities),
            "total_relationships": len(relationships),
            "entity_types": entity_types,
            "relationship_types": relationship_types,
            "avg_relationships_per_entity": round(len(relationships) / max(len(entities), 1), 2)
        }
    
    async def _store_mapping(self, mapping: Dict[str, Any], context: ExecutionContext) -> Optional[str]:
        """Store relationship mapping in Artifact Plane."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    result = await artifact_plane.create_artifact(
                        artifact_type="relationship_graph",
                        content=mapping,
                        metadata={"parsed_file_id": mapping.get("parsed_file_id")},
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
                    return result.get("artifact_id")
            except Exception as e:
                self.logger.warning(f"Could not store mapping: {e}")
        return None
