"""
Workflow Processing Abstraction - Layer 1

Lightweight coordination layer for workflow processing operations (BPMN, DrawIO).
Extracts workflow structure (tasks, gateways, flows) for Journey realm.

WHAT (Infrastructure): I coordinate workflow processing operations
HOW (Abstraction): I provide lightweight coordination for workflow parsing
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from datetime import datetime

from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class WorkflowProcessingAbstraction:
    """
    Workflow Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for workflow processing operations.
    Processes BPMN, DrawIO files and extracts workflow structure.
    """
    
    def __init__(
        self,
        workflow_adapter: Optional[Any] = None,  # For future workflow-specific adapter
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Workflow Processing Abstraction.
        
        Args:
            workflow_adapter: Workflow adapter (Layer 0) - optional, uses built-in parsing for now
            state_surface: State Surface instance for file retrieval
        """
        self.workflow_adapter = workflow_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ Workflow Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse workflow file (BPMN, DrawIO) using State Surface reference.
        
        Args:
            request: FileParsingRequest with file_reference
        
        Returns:
            FileParsingResult with workflow structure (tasks, gateways, flows)
        """
        try:
            # Get State Surface from request if not provided in __init__
            state_surface = request.state_surface or self.state_surface
            
            if not state_surface:
                return FileParsingResult(
                    success=False,
                    error="State Surface not available for file retrieval",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Retrieve file from State Surface
            file_data = await state_surface.get_file(request.file_reference)
            
            if not file_data:
                return FileParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Decode file data if bytes
            if isinstance(file_data, bytes):
                bpmn_xml = file_data.decode('utf-8')
            else:
                bpmn_xml = str(file_data)
            
            # Parse BPMN XML structure
            tasks, gateways, flows = self._extract_bpmn_structure(bpmn_xml)
            
            # Build structure metadata for chunking service
            structure = {
                "workflow": {
                    "tasks": [
                        {
                            "task_index": idx,
                            "task_id": task.get("id", f"task_{idx}"),
                            "task_name": task.get("name", ""),
                            "task_type": task.get("type", "task")
                        }
                        for idx, task in enumerate(tasks)
                    ],
                    "gateways": [
                        {
                            "gateway_index": idx,
                            "gateway_id": gw.get("id", f"gateway_{idx}"),
                            "gateway_name": gw.get("name", ""),
                            "gateway_type": gw.get("type", "exclusiveGateway")
                        }
                        for idx, gw in enumerate(gateways)
                    ],
                    "flows": [
                        {
                            "flow_index": idx,
                            "flow_id": flow.get("id", f"flow_{idx}"),
                            "source": flow.get("source"),
                            "target": flow.get("target")
                        }
                        for idx, flow in enumerate(flows)
                    ]
                }
            }
            
            # Build metadata (include structure, parsing_type)
            metadata = {
                "parsing_type": "workflow",
                "structure": structure,
                "file_type": "bpmn",  # or "drawio" if detected
                "task_count": len(tasks),
                "gateway_count": len(gateways),
                "flow_count": len(flows)
            }
            
            # Build structured_data (standardized format, no nested metadata)
            structured_data = {
                "format": "workflow",
                "bpmn_xml": bpmn_xml,  # Keep raw XML for WorkflowConversionService
                "tasks": tasks,
                "gateways": gateways,
                "flows": flows
            }
            
            # Convert to FileParsingResult (standardized format)
            return FileParsingResult(
                success=True,
                text_content=bpmn_xml,  # Keep as text for compatibility with WorkflowConversionService
                structured_data=structured_data,
                metadata=metadata,
                parsing_type="workflow",  # Explicit parsing type
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ Workflow parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"Workflow parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _extract_bpmn_structure(self, bpmn_xml: str) -> tuple:
        """
        Extract BPMN structure (tasks, gateways, flows) from XML.
        
        Args:
            bpmn_xml: BPMN XML content
        
        Returns:
            Tuple of (tasks, gateways, flows) lists
        """
        tasks = []
        gateways = []
        flows = []
        
        try:
            root = ET.fromstring(bpmn_xml)
            
            # BPMN namespace
            namespace = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}
            
            # Find all tasks
            bpmn_tasks = root.findall('.//bpmn:task', namespace) or root.findall('.//task')
            for task in bpmn_tasks:
                tasks.append({
                    "id": task.get('id', ''),
                    "name": task.get('name', ''),
                    "type": "bpmn:task",
                    "documentation": task.findtext('bpmn:documentation', '', namespaces=namespace) or task.findtext('documentation', '')
                })
            
            # Find all gateways
            bpmn_gateways = root.findall('.//bpmn:exclusiveGateway', namespace) or root.findall('.//exclusiveGateway')
            bpmn_gateways.extend(root.findall('.//bpmn:parallelGateway', namespace) or root.findall('.//parallelGateway'))
            bpmn_gateways.extend(root.findall('.//bpmn:inclusiveGateway', namespace) or root.findall('.//inclusiveGateway'))
            
            for gateway in bpmn_gateways:
                gateway_type = gateway.tag.split('}')[-1] if '}' in gateway.tag else gateway.tag
                gateways.append({
                    "id": gateway.get('id', ''),
                    "name": gateway.get('name', ''),
                    "type": gateway_type
                })
            
            # Find all sequence flows
            bpmn_flows = root.findall('.//bpmn:sequenceFlow', namespace) or root.findall('.//sequenceFlow')
            for flow in bpmn_flows:
                flows.append({
                    "id": flow.get('id', ''),
                    "source": flow.get('sourceRef', ''),
                    "target": flow.get('targetRef', '')
                })
            
        except ET.ParseError as e:
            self.logger.warning(f"Failed to parse BPMN XML: {e}, returning empty structure")
        except Exception as e:
            self.logger.warning(f"Error extracting BPMN structure: {e}, returning empty structure")
        
        return tasks, gateways, flows
