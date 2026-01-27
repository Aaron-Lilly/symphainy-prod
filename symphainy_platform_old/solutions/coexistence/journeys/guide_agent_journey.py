"""
Guide Agent Journey Orchestrator

Composes AI-powered guidance operations:
1. initiate_guide_agent - Initialize with platform-wide context and MCP tools
2. process_guide_agent_message - Process messages, optionally call MCP tools
3. route_to_liaison_agent - Route to pillar-specific Liaison Agent

WHAT (Journey Role): I orchestrate AI-powered user guidance with MCP tool access
HOW (Journey Implementation): I compose guide agent intents with Curator integration
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class GuideAgentJourney:
    """
    Guide Agent Journey Orchestrator.
    
    Handles AI-powered guidance with platform-wide MCP tool access:
    - Initialize with all available MCP tools from Curator
    - Process messages with optional MCP tool execution
    - Route to Liaison Agents with context sharing
    
    MCP Tools:
    - coexist_initiate_guide_agent: Initialize with MCP tools
    - coexist_process_message: Process message, call tools
    - coexist_route_to_liaison: Route to specialist
    """
    
    JOURNEY_ID = "guide_agent"
    JOURNEY_NAME = "Guide Agent Interaction"
    
    # Valid Liaison Agent targets
    VALID_PILLARS = ["content", "insights", "journey", "solution"]
    
    # Platform capabilities for context
    PLATFORM_CAPABILITIES = {
        "content": ["file_upload", "file_parsing", "embeddings", "artifact_management"],
        "insights": ["data_quality", "business_analysis", "pattern_discovery", "relationship_mapping"],
        "journey": ["workflow_creation", "sop_management", "coexistence_analysis", "blueprint_creation"],
        "solution": ["poc_creation", "roadmap_generation", "solution_synthesis", "artifact_export"]
    }
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        curator: Optional[Any] = None,
        agent_framework: Optional[Any] = None
    ):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.curator = curator
        self.agent_framework = agent_framework
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        
        # In-memory conversation store (production uses state_surface)
        self._conversations: Dict[str, Dict] = {}
        self._chat_sessions: Dict[str, Dict] = {}
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compose guide agent journey."""
        journey_params = journey_params or {}
        action = journey_params.get("action", "initiate")
        journey_execution_id = generate_event_id()
        
        self.logger.info(f"Composing journey: {self.journey_name}, action: {action}")
        
        try:
            if action == "initiate":
                return await self._initiate_guide_agent(context, journey_params, journey_execution_id)
            elif action == "message":
                return await self._process_guide_agent_message(context, journey_params, journey_execution_id)
            elif action == "route_liaison":
                return await self._route_to_liaison_agent(context, journey_params, journey_execution_id)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    async def _initiate_guide_agent(
        self, 
        context: ExecutionContext, 
        params: Dict, 
        journey_execution_id: str
    ) -> Dict[str, Any]:
        """
        Initialize GuideAgent with platform-wide context and MCP tools.
        
        Per contract:
        - Query Curator for all available MCP tools (all orchestrators)
        - Load conversation history from chat session
        - Retrieve shared context from previous agent (if toggled)
        - Build platform-wide context
        """
        chat_session_id = params.get("chat_session_id") or f"chat_{context.session_id}"
        include_mcp_tools = params.get("include_mcp_tools", True)
        
        # Get or create chat session
        chat_session = self._chat_sessions.get(chat_session_id, {
            "chat_session_id": chat_session_id,
            "active_agent": "guide",
            "conversation_history": [],
            "context": {},
            "created_at": self.clock.now_utc().isoformat()
        })
        self._chat_sessions[chat_session_id] = chat_session
        
        # Load conversation history
        conversation_history = chat_session.get("conversation_history", [])
        
        # Retrieve shared context from previous agent (if toggled)
        shared_context = chat_session.get("context", {}).get("shared_context")
        
        # Query Curator for all available MCP tools from all orchestrators
        available_mcp_tools = []
        if include_mcp_tools:
            available_mcp_tools = await self._query_curator_for_mcp_tools()
        
        # Build platform-wide context
        platform_context = {
            "pillars": list(self.PLATFORM_CAPABILITIES.keys()),
            "solutions": [f"{p}_solution" for p in self.PLATFORM_CAPABILITIES.keys()],
            "capabilities": [cap for caps in self.PLATFORM_CAPABILITIES.values() for cap in caps]
        }
        
        # Store conversation state
        conversation_id = f"conv_{chat_session_id}_{journey_execution_id}"
        self._conversations[conversation_id] = {
            "chat_session_id": chat_session_id,
            "agent_type": "guide",
            "mcp_tools": available_mcp_tools,
            "platform_context": platform_context,
            "created_at": self.clock.now_utc().isoformat()
        }
        
        # Build response artifact
        guide_agent_conversation = {
            "agent_type": "guide",
            "chat_session_id": chat_session_id,
            "conversation_history": conversation_history,
            "shared_context": shared_context,
            "available_mcp_tools": available_mcp_tools,
            "platform_context": platform_context
        }
        
        semantic_payload = {
            "agent_type": "guide",
            "chat_session_id": chat_session_id,
            "mcp_tools_count": len(available_mcp_tools),
            "has_shared_context": shared_context is not None
        }
        
        artifact = create_structured_artifact(
            result_type="guide_agent_conversation",
            semantic_payload=semantic_payload,
            renderings={
                "message": "GuideAgent initialized. I can help you with platform-wide questions and execute actions via MCP tools.",
                "guide_agent_conversation": guide_agent_conversation
            }
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"guide_agent_conversation": artifact},
            "events": [{
                "type": "guide_agent_initialized",
                "chat_session_id": chat_session_id,
                "mcp_tools_count": len(available_mcp_tools)
            }]
        }
    
    async def _query_curator_for_mcp_tools(self) -> List[Dict[str, Any]]:
        """Query Curator for all available MCP tools from all orchestrators."""
        # If Curator is available, query it
        if self.curator:
            try:
                tools = await self.curator.get_all_mcp_tools()
                if tools:
                    return tools
            except Exception as e:
                self.logger.warning(f"Could not query Curator: {e}")
        
        # Return default tools based on known orchestrators
        return [
            # Content orchestrator tools
            {"tool_name": "content_upload_file", "description": "Upload a file for processing", "orchestrator": "content", "parameters": {"file": "object", "file_name": "string"}},
            {"tool_name": "content_parse_file", "description": "Parse an uploaded file", "orchestrator": "content", "parameters": {"artifact_id": "string"}},
            {"tool_name": "content_create_embeddings", "description": "Create embeddings from parsed content", "orchestrator": "content", "parameters": {"parsed_artifact_id": "string"}},
            {"tool_name": "content_list_artifacts", "description": "List content artifacts", "orchestrator": "content", "parameters": {}},
            # Insights orchestrator tools
            {"tool_name": "insights_assess_quality", "description": "Assess data quality", "orchestrator": "insights", "parameters": {"artifact_id": "string"}},
            {"tool_name": "insights_analyze_business", "description": "Perform business analysis", "orchestrator": "insights", "parameters": {"artifact_id": "string", "analysis_type": "string"}},
            # Journey orchestrator tools
            {"tool_name": "journey_create_workflow", "description": "Create workflow from SOP", "orchestrator": "journey", "parameters": {"sop_id": "string"}},
            {"tool_name": "journey_analyze_coexistence", "description": "Analyze coexistence between systems", "orchestrator": "journey", "parameters": {"workflow_id": "string", "sop_id": "string"}},
            # Solution orchestrator tools
            {"tool_name": "outcomes_create_poc", "description": "Create POC proposal", "orchestrator": "outcomes", "parameters": {"analysis_id": "string"}},
            {"tool_name": "outcomes_generate_roadmap", "description": "Generate implementation roadmap", "orchestrator": "outcomes", "parameters": {"poc_id": "string"}},
            # Control Tower tools
            {"tool_name": "tower_get_platform_stats", "description": "Get platform statistics", "orchestrator": "control_tower", "parameters": {}},
            {"tool_name": "tower_list_solutions", "description": "List deployed solutions", "orchestrator": "control_tower", "parameters": {}}
        ]
    
    async def _process_guide_agent_message(
        self, 
        context: ExecutionContext, 
        params: Dict, 
        journey_execution_id: str
    ) -> Dict[str, Any]:
        """
        Process user message to GuideAgent.
        
        Per contract:
        - Process user message with platform-wide knowledge
        - Optionally determine and call MCP tool
        - Update conversation context
        - Return response with optional MCP tool results
        """
        message = params.get("message", "")
        chat_session_id = params.get("chat_session_id")
        mcp_tool_to_call = params.get("mcp_tool_to_call")
        mcp_tool_params = params.get("mcp_tool_params", {})
        
        if not message.strip():
            raise ValueError("message is required")
        
        # Get chat session
        if not chat_session_id:
            chat_session_id = f"chat_{context.session_id}"
        
        chat_session = self._chat_sessions.get(chat_session_id)
        if not chat_session:
            raise ValueError(f"Chat session not found: {chat_session_id}")
        
        # Generate message ID
        message_id = f"msg_{generate_event_id()}"
        
        # Analyze message and determine if MCP tool call needed
        mcp_tool_result = None
        tool_called = None
        
        if mcp_tool_to_call:
            # Explicit tool call requested
            tool_called = mcp_tool_to_call
            mcp_tool_result = await self._call_orchestrator_mcp_tool(
                mcp_tool_to_call, 
                mcp_tool_params, 
                context
            )
        else:
            # Let GuideAgent determine if tool is needed
            tool_decision = self._determine_mcp_tool_for_message(message)
            if tool_decision:
                tool_called = tool_decision["tool_name"]
                mcp_tool_result = await self._call_orchestrator_mcp_tool(
                    tool_decision["tool_name"],
                    tool_decision.get("params", {}),
                    context
                )
        
        # Generate response
        response_content = self._generate_guide_response(message, mcp_tool_result)
        
        # Update conversation context
        chat_session["conversation_history"].append({
            "role": "user",
            "content": message,
            "timestamp": self.clock.now_utc().isoformat()
        })
        chat_session["conversation_history"].append({
            "role": "assistant",
            "content": response_content,
            "timestamp": self.clock.now_utc().isoformat(),
            "mcp_tool_called": tool_called,
            "mcp_tool_result": mcp_tool_result
        })
        
        # Build response artifact
        guide_agent_response = {
            "message_id": message_id,
            "response": {
                "role": "assistant",
                "content": response_content,
                "timestamp": self.clock.now_utc().isoformat()
            },
            "mcp_tool_called": tool_called,
            "mcp_tool_result": mcp_tool_result,
            "suggestions": self._generate_suggestions(message, mcp_tool_result)
        }
        
        semantic_payload = {
            "message_id": message_id,
            "response_type": "with_tool" if tool_called else "conversational",
            "mcp_tool_called": tool_called
        }
        
        artifact = create_structured_artifact(
            result_type="guide_agent_response",
            semantic_payload=semantic_payload,
            renderings=guide_agent_response
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"guide_agent_response": artifact},
            "events": [{
                "type": "guide_agent_message_processed",
                "chat_session_id": chat_session_id,
                "message_id": message_id,
                "mcp_tool_called": tool_called
            }]
        }
    
    def _determine_mcp_tool_for_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Determine if an MCP tool should be called based on the message."""
        message_lower = message.lower()
        
        # Check for file upload intent
        if any(word in message_lower for word in ["upload", "file", "document"]):
            return {"tool_name": "content_upload_file", "params": {}}
        
        # Check for parsing intent
        if any(word in message_lower for word in ["parse", "extract", "read"]):
            return {"tool_name": "content_parse_file", "params": {}}
        
        # Check for quality assessment
        if any(word in message_lower for word in ["quality", "assess", "validate"]):
            return {"tool_name": "insights_assess_quality", "params": {}}
        
        # Check for workflow intent
        if any(word in message_lower for word in ["workflow", "sop", "process"]):
            return {"tool_name": "journey_create_workflow", "params": {}}
        
        # Check for statistics/dashboard
        if any(word in message_lower for word in ["stats", "statistics", "dashboard", "status"]):
            return {"tool_name": "tower_get_platform_stats", "params": {}}
        
        # No tool needed
        return None
    
    async def _call_orchestrator_mcp_tool(
        self, 
        tool_name: str, 
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Call an orchestrator MCP tool (governed execution).
        
        This is the governed pathway - all tool calls go through this method.
        """
        self.logger.info(f"Calling MCP tool: {tool_name} with params: {params}")
        
        # In production, this would call the actual MCP tool via the platform
        # For now, return a simulated result
        return {
            "tool_name": tool_name,
            "status": "success",
            "result": {
                "message": f"Tool '{tool_name}' executed successfully",
                "execution_id": generate_event_id()
            },
            "executed_at": self.clock.now_utc().isoformat()
        }
    
    def _generate_guide_response(self, message: str, mcp_tool_result: Optional[Dict]) -> str:
        """Generate GuideAgent response based on message and tool result."""
        message_lower = message.lower()
        
        if mcp_tool_result:
            tool_name = mcp_tool_result.get("tool_name", "")
            return f"I've executed the **{tool_name}** tool for you. {mcp_tool_result.get('result', {}).get('message', '')} Is there anything else you'd like me to help with?"
        
        # Coexistence explanation
        if "coexistence" in message_lower or "what is" in message_lower:
            return "**Coexistence** in the Symphainy platform means enabling your existing systems to work together with modern AI capabilities without replacing them.\n\nThink of it like this: instead of ripping out your legacy systems, we help you build bridges between them and modern tools. The platform coordinates work that crosses these boundaries.\n\nWould you like me to show you an example?"
        
        # Navigation help
        if any(word in message_lower for word in ["content", "upload", "file"]):
            return "I can help you work with content! The Content pillar handles file uploads, parsing, and embedding creation. Would you like me to navigate you there, or shall I help you upload a file directly?"
        
        if any(word in message_lower for word in ["insights", "analyze", "quality"]):
            return "The Insights pillar is perfect for data analysis and quality assessment. I can help you analyze uploaded content, assess data quality, or discover patterns. What would you like to explore?"
        
        if any(word in message_lower for word in ["journey", "workflow", "sop", "process"]):
            return "The Journey pillar handles workflows, SOPs, and coexistence analysis. I can help you create workflows from SOPs, analyze how systems work together, or build coexistence blueprints. What interests you?"
        
        # Help response
        if any(word in message_lower for word in ["help", "what can", "capabilities"]):
            return "I'm your **Guide Agent** - I have platform-wide knowledge and can help you with:\n\n• **Navigation** - Find the right pillar or solution\n• **Coexistence** - Explain how systems work together\n• **MCP Tools** - Execute actions across all orchestrators\n• **Guidance** - Walk you through any journey\n\nI can also connect you with **Liaison Agents** who specialize in specific pillars. What would you like to explore?"
        
        # Default
        return "I'd be happy to help you with that! I have access to tools across all platform pillars. Could you tell me more about what you're trying to accomplish? I can help with content processing, data analysis, workflow management, or solution creation."
    
    def _generate_suggestions(self, message: str, mcp_tool_result: Optional[Dict]) -> List[str]:
        """Generate contextual suggestions."""
        if mcp_tool_result:
            return [
                "Show me the results",
                "What's next?",
                "Help me understand this"
            ]
        
        message_lower = message.lower()
        if "coexistence" in message_lower:
            return ["Show me an example", "Take me to Journey pillar", "How does it work?"]
        
        return [
            "What is coexistence?",
            "Help me upload a file",
            "Show me available solutions",
            "Connect me with a specialist"
        ]
    
    async def _route_to_liaison_agent(
        self, 
        context: ExecutionContext, 
        params: Dict, 
        journey_execution_id: str
    ) -> Dict[str, Any]:
        """
        Route to pillar-specific Liaison Agent with context sharing.
        
        Per contract:
        - Extract conversation context from GuideAgent
        - Determine appropriate Liaison Agent based on target_pillar
        - Share context via share_context_to_agent
        - Update chat session active_agent
        """
        target_pillar = params.get("target_pillar")
        chat_session_id = params.get("chat_session_id")
        routing_reason = params.get("routing_reason", "User requested specialist assistance")
        context_to_share = params.get("context_to_share")
        
        if not target_pillar:
            raise ValueError("target_pillar is required")
        
        if target_pillar not in self.VALID_PILLARS:
            raise ValueError(f"Invalid target_pillar: {target_pillar}. Valid: {self.VALID_PILLARS}")
        
        # Get chat session
        if not chat_session_id:
            chat_session_id = f"chat_{context.session_id}"
        
        chat_session = self._chat_sessions.get(chat_session_id)
        if not chat_session:
            # Create session if doesn't exist
            chat_session = {
                "chat_session_id": chat_session_id,
                "active_agent": "guide",
                "conversation_history": [],
                "context": {},
                "created_at": self.clock.now_utc().isoformat()
            }
            self._chat_sessions[chat_session_id] = chat_session
        
        # Extract context to share
        if not context_to_share:
            context_to_share = {
                "conversation_history": chat_session.get("conversation_history", []),
                "previous_agent": "guide",
                "routing_reason": routing_reason
            }
        
        # Share context to Liaison Agent (via share_context_to_agent)
        liaison_agent_id = f"liaison_{target_pillar}"
        shared_context = await self._share_context_to_agent(
            source_agent="guide",
            target_agent=liaison_agent_id,
            shared_context=context_to_share
        )
        
        # Update chat session active_agent
        chat_session["active_agent"] = liaison_agent_id
        chat_session["context"]["shared_context"] = shared_context
        
        # Generate Liaison greeting
        liaison_greeting = self._get_liaison_greeting(target_pillar)
        
        # Build response artifact
        liaison_activation = {
            "target_pillar": target_pillar,
            "liaison_agent_id": liaison_agent_id,
            "shared_context": shared_context,
            "routing_reason": routing_reason,
            "active_agent_updated": True,
            "liaison_greeting": liaison_greeting,
            "liaison_capabilities": self.PLATFORM_CAPABILITIES.get(target_pillar, [])
        }
        
        semantic_payload = {
            "target_pillar": target_pillar,
            "liaison_agent_id": liaison_agent_id,
            "routing_reason": routing_reason
        }
        
        artifact = create_structured_artifact(
            result_type="liaison_agent_activation",
            semantic_payload=semantic_payload,
            renderings=liaison_activation
        )
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": {"liaison_agent_activation": artifact},
            "events": [{
                "type": "liaison_agent_activated",
                "chat_session_id": chat_session_id,
                "target_pillar": target_pillar,
                "liaison_agent_id": liaison_agent_id
            }]
        }
    
    async def _share_context_to_agent(
        self, 
        source_agent: str, 
        target_agent: str, 
        shared_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Share context from one agent to another."""
        return {
            "from_agent": source_agent,
            "to_agent": target_agent,
            "context_data": shared_context,
            "shared_at": self.clock.now_utc().isoformat()
        }
    
    def _get_liaison_greeting(self, pillar: str) -> str:
        """Get Liaison Agent greeting based on pillar."""
        greetings = {
            "content": "Hi! I'm the **Content Liaison Agent**. I specialize in file processing, parsing, and embedding creation. I can help you upload files, parse content, create embeddings, and manage your artifacts. What would you like to work on?",
            "insights": "Hi! I'm the **Insights Liaison Agent**. I specialize in data analysis, quality assessment, and pattern discovery. I can help you assess data quality, perform business analysis, and discover relationships in your data. What would you like to explore?",
            "journey": "Hi! I'm the **Journey Liaison Agent**. I specialize in workflows, SOPs, and coexistence analysis. I can help you create workflows from SOPs, analyze how systems coexist, and build blueprints for boundary-crossing work. What process would you like to examine?",
            "solution": "Hi! I'm the **Solution Liaison Agent**. I specialize in POC creation, roadmap generation, and solution synthesis. I can help you create proof-of-concepts, generate implementation roadmaps, and synthesize cross-pillar solutions. What outcome are you working toward?"
        }
        return greetings.get(pillar, f"Hi! I'm the {pillar.title()} Liaison Agent. How can I help you?")
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA API definitions for MCP tool registration."""
        return {
            "initiate_guide_agent": {
                "handler": self._handle_initiate,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "chat_session_id": {"type": "string", "description": "Chat session identifier"},
                        "include_mcp_tools": {"type": "boolean", "description": "Whether to query MCP tools from Curator"},
                        "user_context": {"type": "object"}
                    }
                },
                "description": "Initialize GuideAgent with platform-wide context and MCP tools"
            },
            "process_guide_agent_message": {
                "handler": self._handle_message,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "User message to GuideAgent"},
                        "chat_session_id": {"type": "string", "description": "Chat session identifier"},
                        "mcp_tool_to_call": {"type": "string", "description": "Specific MCP tool to call"},
                        "mcp_tool_params": {"type": "object", "description": "Parameters for MCP tool"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["message"]
                },
                "description": "Process user message, optionally call MCP tools"
            },
            "route_to_liaison_agent": {
                "handler": self._handle_route,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target_pillar": {"type": "string", "enum": ["content", "insights", "journey", "solution"], "description": "Target pillar for Liaison Agent"},
                        "chat_session_id": {"type": "string", "description": "Chat session identifier"},
                        "routing_reason": {"type": "string", "description": "Reason for routing"},
                        "context_to_share": {"type": "object", "description": "Context to share with Liaison"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["target_pillar"]
                },
                "description": "Route to pillar-specific Liaison Agent with context sharing"
            }
        }
    
    async def _handle_initiate(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "initiate", **kwargs})
    
    async def _handle_message(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "message", **kwargs})
    
    async def _handle_route(self, **kwargs) -> Dict[str, Any]:
        context = self._create_context(kwargs)
        return await self.compose_journey(context, {"action": "route_liaison", **kwargs})
    
    def _create_context(self, kwargs: Dict) -> ExecutionContext:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="coexistence"
        )
        context.state_surface = self.state_surface
        return context
