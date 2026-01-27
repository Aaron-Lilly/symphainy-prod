"""
Security Solution MCP Server

MCP server that exposes Security Solution SOA APIs as MCP tools.

WHAT (MCP Server Role): I expose Security APIs as MCP tools
HOW (MCP Server Implementation): I wrap journey SOA APIs with tool definitions
    and handle MCP protocol communication

Architecture:
- Collects SOA APIs from SecuritySolution
- Registers each API as an MCP tool with prefix "security_"
- Handles tool invocations and routes to appropriate handlers

Tool Naming Convention:
- All tools prefixed with "security_" to avoid namespace collisions
- Example: security_authenticate_user, security_create_user_account
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utilities import get_logger


class SecuritySolutionMCPServer:
    """
    MCP Server for Security Solution.
    
    Exposes SOA APIs as MCP tools:
    - security_authenticate_user: Login with credentials
    - security_create_user_account: Register new user
    - security_validate_token: Validate authentication token
    - security_create_session: Create authenticated session
    - security_validate_authorization: Check user permissions
    - security_terminate_session: Logout user
    - security_check_email_availability: Check if email is available
    """
    
    TOOL_PREFIX = "security_"
    
    def __init__(self, solution, public_works=None):
        """
        Initialize Security Solution MCP Server.
        
        Args:
            solution: SecuritySolution instance
            public_works: Public Works Foundation Service
        """
        self.logger = get_logger(self.__class__.__name__)
        self.solution = solution
        self.public_works = public_works
        
        # Collect SOA APIs from solution
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_tools()
        
        self.logger.info(f"SecuritySolutionMCPServer initialized with {len(self._tools)} tools")
    
    def _register_tools(self):
        """Register SOA APIs as MCP tools."""
        soa_apis = self.solution.get_soa_apis()
        
        # Define tool schemas
        tool_schemas = {
            "authenticate_user": {
                "name": f"{self.TOOL_PREFIX}authenticate_user",
                "description": "Authenticate user with email and password credentials",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "User's email address"
                        },
                        "password": {
                            "type": "string",
                            "description": "User's password"
                        }
                    },
                    "required": ["email", "password"]
                }
            },
            "create_user_account": {
                "name": f"{self.TOOL_PREFIX}create_user_account",
                "description": "Register a new user account",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "User's display name"
                        },
                        "email": {
                            "type": "string",
                            "description": "User's email address"
                        },
                        "password": {
                            "type": "string",
                            "description": "User's password (min 8 characters)"
                        }
                    },
                    "required": ["email", "password"]
                }
            },
            "validate_token": {
                "name": f"{self.TOOL_PREFIX}validate_token",
                "description": "Validate an authentication token",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "token": {
                            "type": "string",
                            "description": "Authentication token to validate"
                        }
                    },
                    "required": ["token"]
                }
            },
            "create_session": {
                "name": f"{self.TOOL_PREFIX}create_session",
                "description": "Create an authenticated session for a user",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to create session for"
                        },
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID for the session"
                        },
                        "access_token": {
                            "type": "string",
                            "description": "Access token for the session"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional session metadata"
                        }
                    }
                }
            },
            "validate_authorization": {
                "name": f"{self.TOOL_PREFIX}validate_authorization",
                "description": "Check if user has permission to perform an action",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to check permissions for"
                        },
                        "tenant_id": {
                            "type": "string",
                            "description": "Tenant ID for permission check"
                        },
                        "action": {
                            "type": "string",
                            "description": "Action to authorize (e.g., read, write, delete)"
                        },
                        "resource": {
                            "type": "string",
                            "description": "Resource to check permission on"
                        }
                    },
                    "required": ["action"]
                }
            },
            "terminate_session": {
                "name": f"{self.TOOL_PREFIX}terminate_session",
                "description": "Logout user and terminate their session",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID to terminate"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID to logout"
                        }
                    }
                }
            },
            "check_email_availability": {
                "name": f"{self.TOOL_PREFIX}check_email_availability",
                "description": "Check if an email address is available for registration",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address to check"
                        }
                    },
                    "required": ["email"]
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
            "server_name": "security_solution_mcp_server",
            "solution_id": self.solution.SOLUTION_ID,
            "version": "1.0",
            "tools_count": len(self._tools),
            "tools": list(self._tools.keys()),
            "foundational": True
        }
