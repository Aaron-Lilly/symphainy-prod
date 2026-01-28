"""
Workflow Conversion Service - Pure Data Processing for Workflow Operations

Enabling service for workflow conversion operations.

WHAT (Enabling Service Role): I execute workflow conversion
HOW (Enabling Service Implementation): I use Public Works abstractions for workflow operations

Key Principle: Pure data processing - no LLM, no business logic, no orchestration.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
import xml.etree.ElementTree as ET

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.execution_context import ExecutionContext


class WorkflowConversionService:
    """
    Workflow Conversion Service - Pure data processing for workflow conversion.
    
    Uses Public Works abstractions to convert between workflows and SOPs.
    Returns raw data only - no business logic.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Workflow Conversion Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
    
    async def optimize_workflow(
        self,
        workflow_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Optimize workflow for Coexistence (human+AI optimization).
        
        ARCHITECTURAL PRINCIPLE: Analyzes workflow structure to identify optimization opportunities.
        
        Args:
            workflow_id: Workflow identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with optimization results and recommendations
        """
        self.logger.info(f"Optimizing workflow: {workflow_id} for tenant: {tenant_id}")
        
        try:
            # Get workflow data (would come from workflow storage/abstraction)
            workflow_data = context.metadata.get(f"workflow_{workflow_id}", {})
            
            recommendations = []
            
            # Analyze workflow for coexistence opportunities
            tasks = workflow_data.get("tasks", [])
            ai_suitable_tasks = []
            human_required_tasks = []
            
            for task in tasks:
                task_type = task.get("type", "unknown")
                task_name = task.get("name", "")
                
                # Simple heuristics for AI suitability
                if any(keyword in task_name.lower() for keyword in ["data", "extract", "parse", "validate", "transform", "analyze"]):
                    ai_suitable_tasks.append({
                        "task_id": task.get("id"),
                        "task_name": task_name,
                        "reason": "Data processing task suitable for AI automation"
                    })
                elif any(keyword in task_name.lower() for keyword in ["approve", "review", "decide", "judge", "evaluate"]):
                    human_required_tasks.append({
                        "task_id": task.get("id"),
                        "task_name": task_name,
                        "reason": "Requires human judgment and decision-making"
                    })
            
            # Generate optimization recommendations
            if ai_suitable_tasks:
                recommendations.append({
                    "type": "ai_automation",
                    "description": f"Consider automating {len(ai_suitable_tasks)} data processing tasks with AI",
                    "tasks": ai_suitable_tasks,
                    "impact": "high",
                    "effort": "medium"
                })
            
            if human_required_tasks:
                recommendations.append({
                    "type": "human_retention",
                    "description": f"Maintain human oversight for {len(human_required_tasks)} decision-making tasks",
                    "tasks": human_required_tasks,
                    "impact": "high",
                    "effort": "low"
                })
            
            # Calculate optimization potential
            total_tasks = len(tasks)
            automation_potential = len(ai_suitable_tasks) / total_tasks if total_tasks > 0 else 0.0
            
            return {
                "workflow_id": workflow_id,
                "optimization_status": "completed",
                "recommendations": recommendations,
                "automation_potential": automation_potential,
                "ai_suitable_tasks_count": len(ai_suitable_tasks),
                "human_required_tasks_count": len(human_required_tasks),
                "total_tasks": total_tasks
            }
            
        except Exception as e:
            self.logger.error(f"Failed to optimize workflow: {e}", exc_info=True)
            return {
                "workflow_id": workflow_id,
                "optimization_status": "error",
                "recommendations": [],
                "error": str(e)
            }
    
    async def generate_sop(
        self,
        workflow_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Generate SOP from workflow (BPMN to SOP conversion).
        
        ARCHITECTURAL PRINCIPLE: Converts workflow structure to SOP format.
        
        Args:
            workflow_id: Workflow identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with SOP results
        """
        self.logger.info(f"Generating SOP from workflow: {workflow_id} for tenant: {tenant_id}")
        
        try:
            # Get workflow data
            workflow_data = context.metadata.get(f"workflow_{workflow_id}", {})
            workflow_content = workflow_data.get("workflow_content", {})
            bpmn_xml = workflow_data.get("bpmn_xml") or workflow_content.get("bpmn_xml")
            
            sop_id = generate_event_id()
            sop_steps = []
            
            # Parse BPMN XML if available
            if bpmn_xml:
                try:
                    root = ET.fromstring(bpmn_xml)
                    namespace = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}
                    
                    # Find all tasks
                    tasks = root.findall('.//bpmn:task', namespace) or root.findall('.//task')
                    for idx, task in enumerate(tasks, 1):
                        task_name = task.get('name', f'Step {idx}')
                        task_id = task.get('id', f'task_{idx}')
                        
                        sop_steps.append({
                            "step_number": idx,
                            "step_name": task_name,
                            "step_id": task_id,
                            "description": task.get('documentation', ''),
                            "actor": task.get('assignee', 'user'),
                            "type": "task"
                        })
                    
                    # Find gateways (decision points)
                    gateways = root.findall('.//bpmn:exclusiveGateway', namespace) or root.findall('.//exclusiveGateway')
                    for gateway in gateways:
                        gateway_name = gateway.get('name', 'Decision Point')
                        sop_steps.append({
                            "step_number": len(sop_steps) + 1,
                            "step_name": gateway_name,
                            "step_id": gateway.get('id', ''),
                            "description": "Decision point in workflow",
                            "type": "decision"
                        })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse BPMN XML: {e}, using workflow structure")
            
            # Fallback: Use workflow structure if BPMN parsing failed
            if not sop_steps:
                tasks = workflow_data.get("tasks", [])
                for idx, task in enumerate(tasks, 1):
                    sop_steps.append({
                        "step_number": idx,
                        "step_name": task.get("name", f"Step {idx}"),
                        "step_id": task.get("id", f"step_{idx}"),
                        "description": task.get("description", ""),
                        "actor": task.get("actor", "user"),
                        "type": task.get("type", "task")
                    })
            
            # Generate SOP document structure
            sop_content = {
                "sop_id": sop_id,
                "sop_title": workflow_data.get("workflow_name", f"SOP from {workflow_id}"),
                "workflow_source": workflow_id,
                "steps": sop_steps,
                "total_steps": len(sop_steps),
                "created_at": context.metadata.get("timestamp", ""),
                "version": "1.0"
            }
            
            return {
                "workflow_id": workflow_id,
                "sop_id": sop_id,
                "sop_status": "generated",
                "sop_content": sop_content,
                "steps_count": len(sop_steps)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate SOP: {e}", exc_info=True)
            return {
                "workflow_id": workflow_id,
                "sop_id": f"sop_{workflow_id}",
                "sop_status": "error",
                "sop_content": {},
                "error": str(e)
            }
    
    async def create_workflow(
        self,
        sop_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Create workflow (BPMN) from SOP.
        
        ARCHITECTURAL PRINCIPLE: Converts SOP structure to BPMN workflow format.
        
        Args:
            sop_id: SOP identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with workflow results including BPMN XML
        """
        self.logger.info(f"Creating workflow from SOP: {sop_id} for tenant: {tenant_id}")
        
        try:
            # Get SOP data
            sop_data = context.metadata.get(f"sop_{sop_id}", {})
            sop_content = sop_data.get("sop_content", {})
            sop_steps = sop_content.get("steps", [])
            
            workflow_id = generate_event_id()
            
            # Convert SOP steps to BPMN tasks
            bpmn_tasks = []
            bpmn_sequence_flows = []
            
            for idx, step in enumerate(sop_steps):
                step_id = step.get("step_id", f"step_{idx}")
                step_name = step.get("step_name", f"Step {idx}")
                step_type = step.get("type", "task")
                
                if step_type == "task":
                    bpmn_tasks.append({
                        "id": step_id,
                        "name": step_name,
                        "type": "bpmn:task",
                        "documentation": step.get("description", "")
                    })
                elif step_type == "decision":
                    bpmn_tasks.append({
                        "id": step_id,
                        "name": step_name,
                        "type": "bpmn:exclusiveGateway",
                        "documentation": step.get("description", "")
                    })
                
                # Create sequence flow to next step
                if idx < len(sop_steps) - 1:
                    next_step_id = sop_steps[idx + 1].get("step_id", f"step_{idx + 1}")
                    bpmn_sequence_flows.append({
                        "id": f"flow_{step_id}_to_{next_step_id}",
                        "source": step_id,
                        "target": next_step_id
                    })
            
            # Generate BPMN XML structure
            bpmn_xml = self._generate_bpmn_xml(
                process_id=f"process_{workflow_id}",
                process_name=sop_content.get("sop_title", f"Workflow from {sop_id}"),
                tasks=bpmn_tasks,
                sequence_flows=bpmn_sequence_flows
            )
            
            workflow_content = {
                "workflow_id": workflow_id,
                "workflow_name": sop_content.get("sop_title", f"Workflow from {sop_id}"),
                "sop_source": sop_id,
                "bpmn_xml": bpmn_xml,
                "tasks": bpmn_tasks,
                "sequence_flows": bpmn_sequence_flows,
                "total_tasks": len(bpmn_tasks)
            }
            
            return {
                "sop_id": sop_id,
                "workflow_id": workflow_id,
                "workflow_status": "created",
                "workflow_content": workflow_content,
                "bpmn_xml": bpmn_xml
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow: {e}", exc_info=True)
            return {
                "sop_id": sop_id,
                "workflow_id": f"workflow_{sop_id}",
                "workflow_status": "error",
                "workflow_content": {},
                "error": str(e)
            }
    
    def _generate_bpmn_xml(
        self,
        process_id: str,
        process_name: str,
        tasks: List[Dict[str, Any]],
        sequence_flows: List[Dict[str, Any]]
    ) -> str:
        """
        Generate BPMN XML from workflow structure.
        
        Args:
            process_id: Process identifier
            process_name: Process name
            tasks: List of task definitions
            sequence_flows: List of sequence flow definitions
        
        Returns:
            BPMN XML string
        """
        # Generate basic BPMN XML structure
        bpmn_ns = "http://www.omg.org/spec/BPMN/20100524/MODEL"
        bpmndi_ns = "http://www.omg.org/spec/BPMN/20100524/DI"
        
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<bpmn:definitions xmlns:bpmn="{bpmn_ns}" xmlns:bpmndi="{bpmndi_ns}" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">',
            f'  <bpmn:process id="{process_id}" name="{process_name}" isExecutable="true">',
        ]
        
        # Add start event
        xml_lines.append('    <bpmn:startEvent id="StartEvent_1"/>')
        
        # Add tasks
        for task in tasks:
            task_id = task.get("id", "task_1")
            task_name = task.get("name", "Task")
            task_type = task.get("type", "bpmn:task")
            documentation = task.get("documentation", "")
            
            if task_type == "bpmn:exclusiveGateway":
                xml_lines.append(f'    <bpmn:exclusiveGateway id="{task_id}" name="{task_name}"/>')
            else:
                doc_attr = f'<bpmn:documentation>{documentation}</bpmn:documentation>' if documentation else ''
                xml_lines.append(f'    <bpmn:task id="{task_id}" name="{task_name}">{doc_attr}</bpmn:task>')
        
        # Add end event
        xml_lines.append('    <bpmn:endEvent id="EndEvent_1"/>')
        
        # Add sequence flows
        xml_lines.append('    <bpmn:sequenceFlow id="flow_start" sourceRef="StartEvent_1" targetRef="' + (tasks[0].get("id") if tasks else "EndEvent_1") + '"/>')
        
        for flow in sequence_flows:
            flow_id = flow.get("id", "flow_1")
            source = flow.get("source")
            target = flow.get("target")
            xml_lines.append(f'    <bpmn:sequenceFlow id="{flow_id}" sourceRef="{source}" targetRef="{target}"/>')
        
        if tasks:
            last_task_id = tasks[-1].get("id")
            xml_lines.append(f'    <bpmn:sequenceFlow id="flow_end" sourceRef="{last_task_id}" targetRef="EndEvent_1"/>')
        
        xml_lines.append('  </bpmn:process>')
        xml_lines.append('</bpmn:definitions>')
        
        return '\n'.join(xml_lines)
    
    async def parse_bpmn_file(
        self,
        bpmn_xml: str,
        workflow_id: Optional[str] = None,
        tenant_id: str = None,
        context: ExecutionContext = None
    ) -> Dict[str, Any]:
        """
        Parse BPMN XML file and create workflow structure.
        
        ARCHITECTURAL PRINCIPLE: Converts BPMN XML to workflow structure.
        
        Args:
            bpmn_xml: BPMN XML content
            workflow_id: Optional workflow identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with workflow structure
        """
        self.logger.info(f"Parsing BPMN file for workflow: {workflow_id}")
        
        try:
            if not workflow_id:
                workflow_id = generate_event_id()
            
            root = ET.fromstring(bpmn_xml)
            namespace = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}
            
            # Extract process information
            process = root.find('.//bpmn:process', namespace) or root.find('.//process')
            process_id = process.get('id', f'process_{workflow_id}') if process is not None else f'process_{workflow_id}'
            process_name = process.get('name', f'Workflow {workflow_id}') if process is not None else f'Workflow {workflow_id}'
            
            # Extract tasks
            tasks = []
            task_elements = root.findall('.//bpmn:task', namespace) or root.findall('.//task')
            for idx, task in enumerate(task_elements, 1):
                task_id = task.get('id', f'task_{idx}')
                task_name = task.get('name', f'Task {idx}')
                documentation = task.find('bpmn:documentation', namespace)
                doc_text = documentation.text if documentation is not None else ''
                
                tasks.append({
                    "id": task_id,
                    "name": task_name,
                    "type": "task",
                    "description": doc_text,
                    "actor": task.get('assignee', 'user'),
                    "position": idx
                })
            
            # Extract gateways
            gateways = root.findall('.//bpmn:exclusiveGateway', namespace) or root.findall('.//exclusiveGateway')
            for gateway in gateways:
                gateway_id = gateway.get('id', f'gateway_{len(tasks) + 1}')
                gateway_name = gateway.get('name', 'Decision Point')
                tasks.append({
                    "id": gateway_id,
                    "name": gateway_name,
                    "type": "decision",
                    "description": "Decision point in workflow",
                    "actor": "system",
                    "position": len(tasks) + 1
                })
            
            # Extract sequence flows
            sequence_flows = []
            flows = root.findall('.//bpmn:sequenceFlow', namespace) or root.findall('.//sequenceFlow')
            for flow in flows:
                sequence_flows.append({
                    "id": flow.get('id', ''),
                    "source": flow.get('sourceRef', ''),
                    "target": flow.get('targetRef', '')
                })
            
            # Create workflow structure
            workflow_content = {
                "workflow_id": workflow_id,
                "workflow_name": process_name,
                "bpmn_xml": bpmn_xml,
                "tasks": tasks,
                "sequence_flows": sequence_flows,
                "total_tasks": len(tasks),
                "decision_points": len(gateways)
            }
            
            return {
                "workflow_id": workflow_id,
                "workflow_status": "parsed",
                "workflow_content": workflow_content,
                "tasks_count": len(tasks),
                "source": "bpmn_file"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse BPMN file: {e}", exc_info=True)
            return {
                "workflow_id": workflow_id or generate_event_id(),
                "workflow_status": "error",
                "workflow_content": {},
                "error": str(e)
            }
