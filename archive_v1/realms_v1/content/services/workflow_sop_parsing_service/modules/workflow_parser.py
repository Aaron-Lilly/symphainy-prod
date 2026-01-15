"""
Workflow Parser Module

Parses workflow files (BPMN, Draw.io, JSON workflows).
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult
)

logger = logging.getLogger(__name__)


class WorkflowParser:
    """
    Workflow Parser Module.
    
    Parses workflow files:
    - BPMN (XML-based)
    - Draw.io (XML-based)
    - JSON workflows
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize Workflow Parser.
        
        Args:
            state_surface: State Surface instance
            platform_gateway: Platform Gateway (not used for workflows)
        """
        self.state_surface = state_surface
        self.logger = logger
    
    async def parse(self, request: ParsingRequest, file_type: str) -> ParsingResult:
        """
        Parse workflow file.
        
        Args:
            request: ParsingRequest with file_reference
            file_type: File type (bpmn, drawio, json)
        
        Returns:
            ParsingResult with workflow structure (nodes, edges)
        """
        try:
            # Retrieve file from State Surface
            file_data = await self.state_surface.get_file(request.file_reference)
            
            if not file_data:
                return ParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Route to specific parser
            if file_type == "bpmn":
                return await self._parse_bpmn(file_data)
            elif file_type == "drawio":
                return await self._parse_drawio(file_data)
            elif file_type == "json":
                return await self._parse_json_workflow(file_data)
            else:
                return ParsingResult(
                    success=False,
                    error=f"Unsupported workflow file type: {file_type}",
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except Exception as e:
            self.logger.error(f"❌ Workflow parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"Workflow parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _parse_bpmn(self, file_data: bytes) -> ParsingResult:
        """Parse BPMN file (XML-based)."""
        try:
            import xml.etree.ElementTree as ET
            
            # Parse XML
            root = ET.fromstring(file_data.decode('utf-8'))
            
            # Extract nodes and edges (simplified - full BPMN parsing would be more complex)
            nodes = []
            edges = []
            
            # Find all process elements
            for process in root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}process'):
                # Extract tasks, gateways, events
                for task in process.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}task'):
                    nodes.append({
                        "id": task.get("id"),
                        "name": task.get("name"),
                        "type": "task"
                    })
                
                for gateway in process.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}gateway'):
                    nodes.append({
                        "id": gateway.get("id"),
                        "name": gateway.get("name"),
                        "type": "gateway"
                    })
                
                # Extract sequence flows (edges)
                for flow in process.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow'):
                    edges.append({
                        "id": flow.get("id"),
                        "source": flow.get("sourceRef"),
                        "target": flow.get("targetRef")
                    })
            
            return ParsingResult(
                success=True,
                data={
                    "nodes": nodes,
                    "edges": edges,
                    "type": "bpmn"
                },
                metadata={
                    "node_count": len(nodes),
                    "edge_count": len(edges)
                },
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"BPMN parsing failed: {e}")
            return ParsingResult(
                success=False,
                error=f"BPMN parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _parse_drawio(self, file_data: bytes) -> ParsingResult:
        """Parse Draw.io file (XML-based)."""
        try:
            import xml.etree.ElementTree as ET
            
            # Parse XML
            root = ET.fromstring(file_data.decode('utf-8'))
            
            # Extract nodes and edges (simplified)
            nodes = []
            edges = []
            
            # Find all mxCell elements (Draw.io uses mxGraph format)
            for cell in root.findall('.//mxCell'):
                cell_id = cell.get("id")
                value = cell.get("value", "")
                edge = cell.get("edge")
                source = cell.get("source")
                target = cell.get("target")
                
                if edge == "1":
                    # This is an edge
                    edges.append({
                        "id": cell_id,
                        "source": source,
                        "target": target
                    })
                elif value:
                    # This is a node
                    nodes.append({
                        "id": cell_id,
                        "name": value,
                        "type": "node"
                    })
            
            return ParsingResult(
                success=True,
                data={
                    "nodes": nodes,
                    "edges": edges,
                    "type": "drawio"
                },
                metadata={
                    "node_count": len(nodes),
                    "edge_count": len(edges)
                },
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"Draw.io parsing failed: {e}")
            return ParsingResult(
                success=False,
                error=f"Draw.io parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _parse_json_workflow(self, file_data: bytes) -> ParsingResult:
        """Parse JSON workflow file."""
        try:
            # Parse JSON
            workflow_data = json.loads(file_data.decode('utf-8'))
            
            # Extract nodes and edges (assuming standard workflow JSON format)
            nodes = workflow_data.get("nodes", [])
            edges = workflow_data.get("edges", [])
            
            return ParsingResult(
                success=True,
                data={
                    "nodes": nodes,
                    "edges": edges,
                    "type": "json"
                },
                metadata={
                    "node_count": len(nodes),
                    "edge_count": len(edges)
                },
                timestamp=datetime.utcnow().isoformat()
            )
        
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON workflow parsing failed: {e}")
            return ParsingResult(
                success=False,
                error=f"Invalid JSON workflow: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
