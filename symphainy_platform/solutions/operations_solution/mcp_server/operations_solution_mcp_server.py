"""
Operations Solution MCP Server

MCP server that exposes Operations Solution SOA APIs as MCP tools.

WHAT (MCP Server Role): I expose Operations APIs as MCP tools
HOW (MCP Server Implementation): I wrap journey SOA APIs with tool definitions
    and handle MCP protocol communication

Architecture:
- Collects SOA APIs from OperationsSolution
- Registers each API as an MCP tool with prefix "operations_"
- Handles tool invocations and routes to appropriate handlers

Tool Naming Convention:
- All tools prefixed with "operations_" to avoid namespace collisions
- Example: operations_create_workflow, operations_generate_sop
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utilities import get_logger


class OperationsSolutionMCPServer:
    """
    MCP Server for Operations Solution.
    
    Exposes SOA APIs as MCP tools:
    - operations_create_workflow: Create workflow from SOP or BPMN
    - operations_generate_sop: Generate SOP from workflow
    - operations_start_sop_chat: Start interactive SOP session
    - operations_sop_chat_message: Process chat message in SOP session
    - operations_analyze_coexistence: Analyze coexistence opportunities
    - operations_optimize_process: Optimize workflow process
    """
    
    TOOL_PREFIX = "operations_"
    
    def __init__(self, solution, public_works=None):
        """
        Initialize Operations Solution MCP Server.
        
        Args:
            solution: OperationsSolution instance
            public_works: Public Works Foundation Service
        """
        self.logger = get_logger(self.__class__.__name__)
        self.solution = solution
        self.public_works = public_works
        
        # Collect SOA APIs from solution
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_tools()
        
        self.logger.info(f"OperationsSolutionMCPServer initialized with {len(self._tools)} tools")
    
    def _register_tools(self):
        """Register SOA APIs as MCP tools."""
        soa_apis = self.solution.get_soa_apis()
        
        # Define tool schemas
        tool_schemas = {
            "create_workflow": {
                "name": f"{self.TOOL_PREFIX}create_workflow",
                "description": "Create a workflow from SOP document or BPMN file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sop_id": {
                            "type": "string",
                            "description": "ID of SOP document to create workflow from"
                        },
                        "bpmn_file_id": {
                            "type": "string",
                            "description": "ID of BPMN file to create workflow from"
                        },
                        "workflow_spec": {
                            "type": "object",
                            "description": "Manual workflow specification"
                        }
                    },
                    "anyOf": [
                        {"required": ["sop_id"]},
                        {"required": ["bpmn_file_id"]},
                        {"required": ["workflow_spec"]}
                    ]
                }
            },
            "generate_sop": {
                "name": f"{self.TOOL_PREFIX}generate_sop",
                "description": "Generate SOP document from workflow",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of workflow to generate SOP from"
                        },
                        "sop_options": {
                            "type": "object",
                            "description": "Options for SOP generation"
                        }
                    },
                    "required": ["workflow_id"]
                }
            },
            "start_sop_chat": {
                "name": f"{self.TOOL_PREFIX}start_sop_chat",
                "description": "Start interactive SOP creation chat session",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sop_topic": {
                            "type": "string",
                            "description": "Topic/title for the SOP to create"
                        },
                        "initial_context": {
                            "type": "object",
                            "description": "Initial context for the chat session"
                        }
                    }
                }
            },
            "sop_chat_message": {
                "name": f"{self.TOOL_PREFIX}sop_chat_message",
                "description": "Process a message in an SOP creation chat session",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "chat_session_id": {
                            "type": "string",
                            "description": "ID of the chat session"
                        },
                        "message": {
                            "type": "string",
                            "description": "User message to process"
                        }
                    },
                    "required": ["chat_session_id", "message"]
                }
            },
            "analyze_coexistence": {
                "name": f"{self.TOOL_PREFIX}analyze_coexistence",
                "description": "Analyze workflow and SOP for coexistence opportunities",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of workflow to analyze"
                        },
                        "sop_id": {
                            "type": "string",
                            "description": "ID of SOP to analyze"
                        }
                    },
                    "anyOf": [
                        {"required": ["workflow_id"]},
                        {"required": ["sop_id"]}
                    ]
                }
            },
            "optimize_process": {
                "name": f"{self.TOOL_PREFIX}optimize_process",
                "description": "Optimize workflow process by identifying friction points and generating recommendations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "ID of workflow to optimize"
                        },
                        "optimization_focus": {
                            "type": "string",
                            "description": "Focus area for optimization (general, efficiency, cost, time)"
                        }
                    },
                    "required": ["workflow_id"]
                }
            }
        }
        
        # Register tools and handlers
        for api_name, handler in soa_apis.items():
            if api_name in tool_schemas:
                schema = tool_schemas[api_name]
                tool_name = schema["name"]
                self._tools[tool_name] = schema
                self._handlers[tool_name] = handler
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available MCP tools.
        
        Returns:
            List of tool definitions
        """
        return list(self._tools.values())
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            context: Execution context
            
        Returns:
            Tool execution result
        """
        if tool_name not in self._handlers:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        handler = self._handlers[tool_name]
        
        # Create execution context if not provided
        if context is None:
            from symphainy_platform.runtime.execution_context import ExecutionContext
            context = ExecutionContext(
                tenant_id="default",
                session_id="mcp_session"
            )
        
        self.logger.info(f"Calling tool: {tool_name}")
        
        result = await handler(context, arguments)
        
        return {
            "tool_name": tool_name,
            "result": result,
            "status": "success"
        }
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        return self._tools.get(tool_name)
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information."""
        return {
            "server_name": "operations_solution_mcp_server",
            "solution_id": self.solution.SOLUTION_ID,
            "version": "1.0",
            "tools_count": len(self._tools),
            "tools": list(self._tools.keys())
        }
